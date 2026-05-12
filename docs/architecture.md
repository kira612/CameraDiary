# Architecture

## 1. システムの狙い

本研究の最終出力は、**定点カメラの長尺動画から、各園児に対応する根拠付き自然文を 1 本ずつ生成すること**です。

ここで重要なのは、設計の主語を `event` や `tracking` に固定しないことです。

- 出力単位は `child-wise`
- 中間表現の中心は `evidence`
- `tracking` は有力な手段の一つ
- 最後に evidence を園児ごとに束ねて自然文を生成する

したがって、本システムは「イベント抽出システム」でも「人物追跡システム」でもなく、**evidence-first な園児別連絡帳生成システム**として整理する。

## 2. 層構造

### 2.1 Ingest Layer

役割:

- RTSP 受信
- フレーム抽出
- タイムスタンプ付与
- 長尺動画の分割や保存

入力:

- Raspberry Pi から送られる RTSP ストリーム
- または録画済み長尺動画

出力:

- timestamp 付き frames
- clips

### 2.2 Evidence Extraction Layer

役割:

- diary-worthy な証拠候補の抽出
- 人物、移動、静止、近接、エリア滞在、姿勢、相互作用などの候補化

ここでは `tracking` も使うが、それ自体を最終目的にしない。

候補:

- person detection
- person tracking
- area occupancy
- motion change
- stillness
- pairwise proximity
- pose / interaction cues

出力:

- evidence candidates

### 2.3 Child-wise Evidence Organization Layer

役割:

- evidence を園児単位へ束ねる
- `track_id` をそのまま最終 `child_id` にしない
- `temp_id` や手動補助を含めて束ねる

ここで大切なのは、tracking 結果を一段抽象化して扱うこと。

出力:

- child-wise evidence bundles

### 2.4 Multimodal Interpretation Layer

役割:

- clip
- low-level observations
- grouped evidence
- 必要なら過去文脈

をまとめて局所要約や意味解釈を生成する。

ここでは VLM / LLM を使ってもよいが、入力は動画全体ではなく evidence に絞る。

出力:

- local multimodal summaries

### 2.5 Diary Composition / Review Layer

役割:

- 園児 1 名につき 1 本の自然文を生成する
- 文ごとに根拠区間を提示する
- 保育士が修正し、確定する

出力:

- child-wise daily diary drafts
- supporting evidence references
- review status

## 3. 全体フロー

```text
Frames
  -> Evidence Candidates
  -> Child-wise Evidence Bundles
  -> Local Multimodal Summaries
  -> Child-wise Daily Diary Drafts
  -> Review UI
```

補足:

- `Person Detection / Tracking` は `Evidence Candidates` の内部手段として位置づける
- tracking が不安定でも、evidence bundle を中心にすれば設計全体は崩れにくい

## 4. 論理アーキテクチャ

```text
[Camera / Raspberry Pi]
  role:
    - 映像入力
    - RTSP 送信

[Streaming Gateway / MediaMTX]
  role:
    - RTSP 受信
    - downstream への配信起点

[Ingest Worker]
  role:
    - frame extraction
    - timestamping
    - clip segmentation

[Evidence Extractor]
  role:
    - detection / tracking / area / motion / proximity
    - evidence candidate creation

[Child-wise Grouper]
  role:
    - evidence to child_temp_id assignment
    - track bundle organization

[Multimodal Summarizer]
  role:
    - clip-level interpretation
    - evidence-level summary generation

[Diary Composer]
  role:
    - child-wise daily text generation
    - evidence-linked draft creation

[Review UI]
  role:
    - child-wise draft review
    - evidence inspection
    - text correction / finalize
```

## 5. データの考え方

イベントは重要だが、唯一の中間表現ではない。中心は `evidence` と `child-wise grouping` に置く。

### 5.1 observations

低レベル観測を扱う。

例:

- timestamp
- bbox
- area
- motion score
- stillness
- near_people_count
- pose_state

### 5.2 evidence_segments

文章生成に使う候補区間。

例:

- segment_id
- start_at / end_at
- theme
- score
- clip_ref
- supporting observations

### 5.3 child_groups

園児ごとの束ね。

例:

- child_temp_id
- related_track_ids
- related_segments
- confidence

### 5.4 diary_drafts

最終出力。

例:

- child_temp_id
- date
- summary
- generated_from_segments
- review_status

## 6. 非機能要件

### 精度

- 完全自動識別を前提にしない
- 根拠区間を提示して、人が確認しやすいことを優先する

### 可観測性

- stream ingest status
- extracted evidence count
- grouped child bundle count
- local summary count
- diary draft count

をログとして残す

### プライバシー

- 生映像全量の長期保存は避ける
- 必要最小限の clip / thumbnail / metadata を優先する
- child-wise 出力でも個人識別の扱いは慎重に設計する

## 7. 既存検証との接続

既に完了している内容:

- Raspberry Pi からの RTSP 配信基盤
- Windows + WSL2 + MediaMTX での受信
- WSL 側で Python / OpenCV による RTSP 読み込み

次に必要な内容:

- evidence candidate 抽出
- child-wise grouping
- local multimodal summarization
- child-wise diary generation
- root evidence を見られる review UI
