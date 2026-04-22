# Pi 側 RTSP 送信の適用手順

このディレクトリには、USB 接続された実カメラを自動検出して RTSP 配信するためのスクリプトと `systemd` ユニット例を置いている。

## 使うファイル

- `start_rtsp_stream.sh`
- `rtsp-stream.service.example`

## 方針

- `/dev/video0` 固定ではなく、USB の `Video Capture` デバイスを自動検出する
- `MJPEG` が使えれば優先する
- `systemd` は `ffmpeg` を直接呼ばず、検出スクリプトを呼ぶ

## Pi 側への配置例

Pi 上で以下を実行する。

```bash
sudo install -m 755 scripts/pi/start_rtsp_stream.sh /usr/local/bin/start_rtsp_stream.sh
sudo install -m 644 scripts/pi/rtsp-stream.service.example /etc/systemd/system/rtsp-stream.service
```

## 設定確認

特に確認するのは `RTSP_URL`。

```ini
Environment=RTSP_URL=rtsp://10.34.44.247:8554/cam1
```

Windows 側の IP が変わる場合はここを直す。

## 起動

```bash
sudo systemctl daemon-reload
sudo systemctl enable rtsp-stream.service
sudo systemctl restart rtsp-stream.service
```

## 確認

```bash
sudo systemctl status rtsp-stream.service
journalctl -u rtsp-stream.service -n 50 --no-pager
```

## 停止

```bash
sudo systemctl stop rtsp-stream.service
```

## 期待するログ

正常時は journal に次のような内容が出る。

- USB カメラのデバイスパス
- RTSP URL
- 入力フォーマット

例:

```text
[INFO] Selected camera: /dev/video0
[INFO] RTSP URL: rtsp://10.34.44.247:8554/cam1
[INFO] Input format: mjpeg
```
