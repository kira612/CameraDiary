# 保育園におけるカメラ映像を使った連絡帳記入支援システム

定点カメラで撮影された長尺保育動画から、映像中の各園児に対応する証拠区間を抽出・整理し、園児ごとに根拠付きの自然な連絡帳文を 1 本ずつ生成することを目指すプロジェクトです。

現時点では、Raspberry Pi と USB カメラから RTSP 配信を行い、Windows + WSL 上で受信する基盤検証まで完了しています。次の段階では、evidence 抽出、園児別束ね、局所要約、園児別連絡帳文生成を接続して、保育現場で使える最小構成を組み立てます。

## 背景

保育園の連絡帳には、食事、睡眠、遊び、排泄、機嫌、特記事項など、1日の様子を短時間で正確に記録することが求められます。一方で、保育士は現場対応が優先されるため、後から記憶を頼りに記入する負担が大きくなりがちです。

本システムは、カメラ映像から diary-worthy な evidence を抽出・整理し、保育士が確認・修正しやすい園児別文章下書きを提示することで、記録負担を減らすことを狙います。

## 目標

- 長尺動画から園児ごとの evidence を抽出・整理する
- 園児 1 名につき 1 本の自然な連絡帳文を生成する
- 各文に対応する根拠区間を提示する
- 保育士が最終確認しやすい UI を用意する
- 生映像そのものではなく、必要最小限の要約情報を扱える構成にする

## 設計方針

- 出力単位は `child-wise`
- 設計思想は `evidence-first`
- `tracking` は有力な手段だが唯一の中心ではない
- repo の主語は `event extraction` ではなく `diary generation`
- `event`、`tracking`、`VLM` はすべて最終出力のための手段として扱う

## 想定ユースケース

保育現場の連絡帳で頻出するテーマを優先し、動画 1 本から複数園児分の文を出すユースケースを対象にします。

- 食事・おやつ:
  - 食べ始めた時刻、完食の有無、おかわり、苦手な食材への挑戦を記録候補にする
- お昼寝・排泄:
  - 入眠時刻、起床時刻、睡眠時間、トイレ誘導や排泄の有無を記録候補にする
- 遊び:
  - どの遊びに興味を示したか、繰り返し取り組んだ行動、集中していた場面を下書き化する
- 友だちとの関わり:
  - 一緒に遊んだ様子、貸し借り、簡単なトラブルとその後の関わり直しを記録候補にする
- 体調・怪我:
  - 咳、鼻水、疲れた様子、転倒など、保護者への共有が必要な出来事を事実ベースで残す
- 園児別文生成:
  - 1 日の長尺動画から、園児ごとに evidence を束ねて自然文を 1 本ずつ生成する
- 日報仕上げ:
  - 保育士が園児別の根拠区間と候補文を確認し、保護者向けの丁寧な文章に整える

## 全体構成

```text
USB Camera
  -> Raspberry Pi
  -> FFmpeg RTSP Publisher
  -> MediaMTX (WSL)
  -> Video Ingest Worker
  -> Evidence Extraction
  -> Child-wise Evidence Organization
  -> Local Multimodal Summaries
  -> Child-wise Diary Draft Generator
  -> Review UI / Export
```

### 構成要素

- 映像取得: Raspberry Pi + USB カメラで保育室映像を取得
- 映像転送: FFmpeg で RTSP 配信し、MediaMTX で受信
- 解析処理: OpenCV などでフレームを読み、evidence 候補を抽出する
- 束ね処理: evidence を園児ごとに整理し、child-wise bundle を作る
- 要約生成: clip と evidence をもとに局所要約と連絡帳文を生成する
- 確認画面: 保育士が園児別の文と根拠区間を確認、修正、確定する

## MVP の範囲

最初の実装では、以下に絞る想定です。

- 1 台の固定カメラ映像を受信できる
- 長尺動画をフレーム列として読み出せる
- 動画中の複数園児について evidence 候補を抽出できる
- 少なくとも一部の園児について evidence を束ねられる
- 園児ごとに自然文を 1 本ずつ生成できる
- 各文に対して対応する根拠区間を提示できる
- 保育士が最終的に手修正して保存できる

## 現状

- RTSP 配信経路の疎通確認は完了
- Windows + WSL2 で `MediaMTX` を受信サーバとして動作確認済み
- `portproxy + firewall` の設定が必要であることを確認済み

## 補助スクリプト

- [scripts/start_mediamtx_wsl.bat](./scripts/start_mediamtx_wsl.bat)
  - Windows から WSL 上の `MediaMTX` を起動するためのバッチファイル
  - 既定の起動先は `/home/kirataiki/apps/mediamtx`
  - 使い方:
    - `scripts\start_mediamtx_wsl.bat`
    - `scripts\start_mediamtx_wsl.bat Ubuntu`
    - `scripts\start_mediamtx_wsl.bat Ubuntu /home/kirataiki/apps/mediamtx`
- [scripts/read_rtsp_opencv.py](./scripts/read_rtsp_opencv.py)
  - WSL 側で `rtsp://localhost:8554/cam1` を OpenCV で読む最小受信スクリプト
  - 使い方:
    - `python3 scripts/read_rtsp_opencv.py`
    - `python3 scripts/read_rtsp_opencv.py --max-frames 300`
    - `python3 scripts/read_rtsp_opencv.py --save-dir tmp/frames --save-every 60`
- [scripts/pi/INSTALL.md](./scripts/pi/INSTALL.md)
  - Raspberry Pi 側で USB カメラ自動検出 + `systemd` 常駐化を適用する手順

### WSL 側セットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-wsl.txt
python3 scripts/read_rtsp_opencv.py --max-frames 300
```

詳細な配信メモは [日報/2026-04-17.txt](./日報/2026-04-17.txt) を参照してください。

## ドキュメント

- [docs/architecture.md](./docs/architecture.md): システム構成と処理フロー
- [docs/implementation-plan.md](./docs/implementation-plan.md): 実装方針、フェーズ、直近タスク
- [docs/research-scope.md](./docs/research-scope.md): 研究スコープと設計原則

## 重要な注意点

- 本システムは保育士の記録を置き換えるものではなく、記入支援を目的とする
- 顔画像や生映像の長期保存は避け、必要最小限のメタデータ保存を優先する
- 園児識別や行動推定には誤りがあり得るため、必ず人の確認工程を挟む
- 導入時には保護者説明、同意、保存期間、閲覧権限の設計が必要

## 参考

- 保育のひきだし「もう悩まない！保育士が知りたい『連絡帳を書くコツ』と『使える例文』」
  - https://www.hoikunohikidashi.jp/?p=16774691

## 次の一歩

1. RTSP 映像を Python で安定して読み込む受信ワーカーを作る
2. evidence candidate を保存するデータモデルを定義する
3. child-wise evidence bundle を作る
4. 園児ごとの連絡帳文と根拠区間を確認できる流れを作る
