# Raspberry Pi RTSP Publisher Setup

このディレクトリは、Raspberry Pi から USB カメラ映像を RTSP 配信するための手順と補助ファイルを置く場所です。

現時点の最小検証では、Pi 側で FFmpeg を使って WSL 側の MediaMTX に送信します。

```bash
ffmpeg -f v4l2 -i /dev/video0 -f rtsp rtsp://<WSL_HOST_IP>:8554/cam1
```

今後ここに置くもの:

- USB カメラ自動検出スクリプト
- `systemd` service unit
- Pi 側のネットワーク確認手順
