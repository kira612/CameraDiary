# Implementation Plan

## 1. 前提

本 repo の中心は、**定点カメラ長尺動画から園児ごとの根拠付き自然文を生成すること**です。

したがって、実装順序も以下を守る。

- 出力は `child-wise`
- 設計思想は `evidence-first`
- `tracking` は重要だが唯一の中心ではない
- MVP でも「根拠付きの園児別文生成」まで入れる

## 2. まず固定すること

- 対象は 1 台の定点カメラ長尺動画
- 複数園児が写る前提
- 完全自動個人識別は最初から要求しない
- `track_id` と `child_id` は分けて扱う
- 最終出力は `園児 1 名につき 1 本の自然文`

## 3. 推奨フェーズ

### Phase 1: Ingest 固定

目的:

- 長尺動画または RTSP を安定して読み込める状態を作る

実施内容:

- MediaMTX からの RTSP 受信
- 長尺動画取り込み
- frame extraction
- timestamp 付与

成果物:

- ingest worker
- clip export
- ingest log

### Phase 2: Evidence Candidate Extraction

目的:

- diary-worthy な証拠候補を動画全体から抽出する

実施内容:

- person detection
- tracking
- area occupancy
- motion / stillness
- proximity / interaction candidate
- theme score 付与

成果物:

- evidence candidates
- low-level observations

### Phase 3: Child-wise Grouping

目的:

- 候補区間を園児ごとに束ねる

実施内容:

- `track_id` を bundle 化
- `child_temp_id` の導入
- evidence_segment と child_group の関連付け
- 必要なら手動補助の導線を残す

成果物:

- child_groups
- related evidence bundles

### Phase 4: Local Summarization

目的:

- evidence ごとの局所要約を作る

実施内容:

- clip + observation の入力整形
- multimodal summary 生成
- theme / confidence 付与

成果物:

- local multimodal summaries
- segment interpretation logs

### Phase 5: Child-wise Diary Generation

目的:

- 園児 1 名につき 1 本の連絡帳文を生成する

実施内容:

- child-wise evidence bundle の整形
- prompt / template 設計
- root evidence を紐づけた draft 生成

成果物:

- child-wise daily diary drafts
- generated_from_segments

### Phase 6: Review / Evaluation

目的:

- 根拠区間付きで確認・修正できる状態を作る

実施内容:

- child-wise draft review UI
- evidence inspection UI
- 修正量 / 有用性 / 欠落の計測

成果物:

- reviewed drafts
- evaluation memo

## 4. MVP の定義

MVP では、以下が満たされれば成立とする。

- 1 台の定点カメラ長尺動画を読み込める
- 動画中の複数園児について evidence 候補を抽出できる
- 少なくとも一部の園児について evidence を束ねられる
- 園児ごとに自然文を 1 本ずつ生成できる
- 各文に対して対応する根拠区間を提示できる
- 保育士が修正できる

ここでは、全園児の完全自動識別までは要求しない。

## 5. 技術選定のたたき台

### Ingest / Streaming

- Raspberry Pi
- FFmpeg
- MediaMTX

### Vision / Evidence

- Python 3.11+
- OpenCV
- NumPy
- 必要に応じて PyAV
- 追跡や検出モデルは後段で追加

### Summarization / Composition

- template-based generation
- 必要に応じて VLM / LLM

### UI / API

- FastAPI
- 軽量 UI

### Storage

- SQLite から開始

## 6. データモデル案

### observations

```json
{
  "id": "obs_001",
  "timestamp": "2026-04-22T09:20:10+09:00",
  "bbox": [120, 80, 260, 420],
  "area": "play_zone_a",
  "motion_score": 0.73,
  "near_people_count": 2,
  "pose_state": "standing"
}
```

### evidence_segments

```json
{
  "segment_id": "seg_001",
  "start_at": "2026-04-22T09:20:10+09:00",
  "end_at": "2026-04-22T09:22:40+09:00",
  "theme": "play",
  "score": 0.84,
  "clip_ref": "clips/seg_001.mp4",
  "supporting_observations": ["obs_001", "obs_002"]
}
```

### child_groups

```json
{
  "child_temp_id": "child_tmp_01",
  "related_track_ids": ["track_12", "track_17"],
  "related_segments": ["seg_001", "seg_008"],
  "confidence": 0.79
}
```

### diary_drafts

```json
{
  "id": "draft_001",
  "child_temp_id": "child_tmp_01",
  "date": "2026-04-22",
  "summary": "午前中は積み木遊びに繰り返し取り組み、周囲の友だちと近い距離で遊ぶ様子が見られました。",
  "generated_from_segments": ["seg_001", "seg_008"],
  "review_status": "draft"
}
```

## 7. 直近タスク

1. ingest worker を安定化する
2. evidence candidate を保存する最小データモデルを作る
3. child_temp_id 単位で evidence を束ねる
4. segment ごとの局所要約を作る
5. child-wise draft を 1 本ずつ生成する
6. 根拠区間付きで確認できる画面を作る

## 8. 成功条件

- 複数園児が写る長尺動画を ingest できる
- 複数の evidence candidate を抽出できる
- 少なくとも一部の園児について child-wise bundle を作れる
- 園児ごとに 1 本ずつ自然文を生成できる
- 生成文に対応する evidence を確認できる

## 9. 避けるべき設計

### event-first に戻りすぎる設計

- 「イベント抽出して文章化するシステム」

これは狙いより狭い。

### tracking-first に固定しすぎる設計

- 「人物追跡して個人動画を作って要約するシステム」

これは手法を固定しすぎる。

本 repo は、**child-wise output / evidence-first design** を基本にする。
