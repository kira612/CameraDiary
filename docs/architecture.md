# Architecture

## 1. システムの狙い

カメラ映像をそのまま保育記録にするのではなく、映像から抽出したイベントを連絡帳記入の補助情報に変換することを目的とします。

そのため、システムは次の 3 層に分けて考えるのが扱いやすいです。

- 映像取得・配信層
- 映像解析・イベント化層
- 連絡帳下書き生成・確認層

## 2. 論理アーキテクチャ

```text
[Camera / Raspberry Pi]
  role:
    - 映像入力
    - RTSP 送信

[Streaming Gateway]
  role:
    - MediaMTX で RTSP 受信
    - 解析系ワーカーへの配信起点

[Ingest Worker]
  role:
    - ストリーム読込
    - フレーム間引き
    - タイムスタンプ付与

[CV / Event Worker]
  role:
    - 動作・領域ベースのイベント検出
    - 園児単位またはエリア単位のイベント化

[Event Store]
  role:
    - event_type
    - started_at / ended_at
    - target_child
    - confidence
    - note

[Draft Generator]
  role:
    - イベント列の整形
    - 連絡帳向け文章の下書き生成

[Review UI]
  role:
    - タイムライン確認
    - 文面修正
    - 保存確定
```

## 3. 映像処理パイプライン

### 3.1 入力

- Raspberry Pi 上の USB カメラから映像取得
- FFmpeg で H.264 に変換して RTSP 配信
- MediaMTX が受信し、ローカル解析系に再配信

### 3.2 受信

- Python ワーカーが `rtsp://localhost:8554/cam1` を読む
- すべてのフレームを処理せず、用途に応じて 1 fps から 5 fps 程度に間引く
- 各フレームに `captured_at` を付与する

### 3.3 前処理

- 画像リサイズ
- 解析対象エリアの切り出し
- 明るさ補正や軽いノイズ低減

### 3.4 イベント抽出

最初は高精度モデルよりも、再現しやすいルールベースから始める方が妥当です。

候補:

- 特定領域への入室 / 退出
- 机や食事エリアへの滞在開始 / 終了
- 午睡エリアでの長時間静止
- 遊びエリアごとの滞在時間集計

将来的には次を検討します。

- 物体検出モデル
- 姿勢推定
- 園児トラッキング
- マルチカメラ統合

## 4. 連絡帳生成フロー

```text
Frames
  -> Event Candidates
  -> Normalized Events
  -> Child / Time Slot Aggregation
  -> Prompt / Template Input
  -> Diary Draft
  -> Human Review
```

### 4.1 正規化イベント

イベントは文章化しやすい形に揃えます。

例:

- `play_started`
- `play_ended`
- `meal_started`
- `meal_finished`
- `nap_started`
- `nap_ended`
- `entered_area`
- `left_area`

連絡帳の頻出テーマに合わせて、MVP では次のカテゴリを優先します。

- 食事:
  - `meal_started`
  - `meal_finished`
  - `meal_area_seated`
- お昼寝 / 排泄:
  - `nap_started`
  - `nap_ended`
  - `toilet_prompted`
- 遊び:
  - `play_started`
  - `play_focus_detected`
  - `left_play_area`
- 友だちとの関わり:
  - `peer_interaction_detected`
- 体調 / 注意事項:
  - `health_attention_needed`

### 4.2 下書き生成の考え方

いきなり LLM に生の時系列を渡すのではなく、まずは機械的に整形します。

例:

```json
{
  "child_id": "child-a",
  "date": "2026-04-17",
  "events": [
    {
      "type": "play_started",
      "label": "積み木遊びを開始",
      "time": "09:20"
    },
    {
      "type": "meal_started",
      "label": "昼食を開始",
      "time": "11:48"
    }
  ]
}
```

この整形済みデータに対して、テンプレートまたは LLM を使って自然文へ変換します。

## 5. データ保存方針

MVP では、以下の 2 系統に分けて保存するのが安全です。

- メタデータ
  - イベント時刻
  - エリア名
  - 園児 ID
  - 信頼度
  - 手修正の履歴
- 必要最小限の参照データ
  - イベント前後数秒のクリップ
  - 静止画サムネイル

生映像全量の長期保存は、運用負担とプライバシー負荷が大きいため、初期段階では避けます。

## 6. 非機能要件

### 精度

- 自動生成文は参考情報として扱う
- 誤検出時に保育士がすぐ修正できることを優先する

### レイテンシ

- リアルタイム性は厳密でなくてよい
- 数十秒から数分単位で更新されれば実運用上は十分な可能性が高い

### 可観測性

- ストリーム受信の成否
- フレーム処理速度
- イベント抽出数
- 下書き生成数

は最低限ログとして残す

### セキュリティ / プライバシー

- 閲覧権限の分離
- 保存期間の明示
- 園児識別情報の最小化
- 下書き確定前の自動生成文への注意表示

## 7. 既存検証との接続

既に完了している内容:

- Raspberry Pi から RTSP 配信
- Windows + WSL2 上の MediaMTX 受信
- `portproxy` と Windows Firewall の設定確認

次に必要な内容:

- Python による RTSP 受信ワーカー
- イベントスキーマ定義
- ダミーの連絡帳ドラフト生成器
- 確認用の簡易 UI
