# 保育園におけるカメラ映像を使った連絡帳記入支援システム

保育園内のカメラ映像をもとに、園児ごとの行動や生活記録の下書きを生成し、保育士の連絡帳記入を支援するためのプロジェクトです。

現時点では、Raspberry Pi と USB カメラから RTSP 配信を行い、Windows + WSL 上で受信する基盤検証まで完了しています。次の段階では、映像解析、イベント抽出、連絡帳ドラフト生成を接続して、保育現場で使える最小構成を組み立てます。

## 背景

保育園の連絡帳には、食事、睡眠、遊び、排泄、機嫌、特記事項など、1日の様子を短時間で正確に記録することが求められます。一方で、保育士は現場対応が優先されるため、後から記憶を頼りに記入する負担が大きくなりがちです。

本システムは、カメラ映像から行動の手掛かりを抽出し、保育士が確認・修正しやすい文章下書きを提示することで、記録負担を減らすことを狙います。

## 目標

- 園児の活動記録を時系列イベントとして整理する
- 連絡帳に転記しやすい自然文の下書きを生成する
- 保育士が最終確認しやすい UI を用意する
- 生映像そのものではなく、必要最小限の要約情報を扱える構成にする

## 想定ユースケース

保育現場の連絡帳で頻出するテーマを優先し、次のユースケースを対象にします。

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
- 日報仕上げ:
  - 1日の終わりに、保育士がイベント一覧と候補文を確認し、保護者向けの丁寧な文章に整える

## 全体構成

```text
USB Camera
  -> Raspberry Pi
  -> FFmpeg RTSP Publisher
  -> MediaMTX (WSL)
  -> Video Ingest Worker
  -> Event Extraction / CV Pipeline
  -> Diary Draft Generator
  -> Review UI / Export
```

### 構成要素

- 映像取得: Raspberry Pi + USB カメラで保育室映像を取得
- 映像転送: FFmpeg で RTSP 配信し、MediaMTX で受信
- 解析処理: OpenCV などでフレームを読み、行動イベント候補を抽出
- 要約生成: イベント列をもとに連絡帳向けの下書きを生成
- 確認画面: 保育士が下書きを確認、修正、確定する

## MVP の範囲

最初の実装では、以下に絞る想定です。

- 1 台の固定カメラ映像を受信できる
- 特定時間帯の映像をフレーム列として読み出せる
- 単純なイベント候補を記録できる
  - 食事エリアへの着席
  - 午睡エリアでの滞在開始 / 終了
  - 遊びエリアへの出入り
  - 一定時間以上の滞在
- イベント一覧から、食事・午睡・遊びを中心とした連絡帳用の短い文面テンプレートを生成できる
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

詳細な配信メモは [設計メモ/2026-04-17.txt](./設計メモ/2026-04-17.txt) を参照してください。

## ドキュメント

- [docs/architecture.md](./docs/architecture.md): システム構成と処理フロー
- [docs/implementation-plan.md](./docs/implementation-plan.md): 実装方針、フェーズ、直近タスク

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
2. 時刻付きイベントを保存するデータモデルを定義する
3. 単純なルールベースで連絡帳下書きを生成する
4. 確認画面を作り、保育士が修正できる流れを作る
