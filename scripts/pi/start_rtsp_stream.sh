#!/usr/bin/env bash
set -euo pipefail

RTSP_URL="${RTSP_URL:-rtsp://10.34.44.247:8554/cam1}"
FRAMERATE="${FRAMERATE:-15}"
VIDEO_SIZE="${VIDEO_SIZE:-1280x720}"
LOGLEVEL="${LOGLEVEL:-warning}"

find_usb_camera() {
  local dev
  for dev in /dev/video*; do
    [ -e "$dev" ] || continue

    if ! udevadm info --query=property --name="$dev" 2>/dev/null | grep -q '^ID_BUS=usb$'; then
      continue
    fi

    if ! v4l2-ctl -d "$dev" --all 2>/dev/null | grep -Eq 'Video Capture|Video Capture Multiplanar'; then
      continue
    fi

    echo "$dev"
    return 0
  done

  return 1
}

pick_input_format() {
  local dev="$1"
  local formats
  formats="$(v4l2-ctl -d "$dev" --list-formats-ext 2>/dev/null || true)"

  if grep -Eq "MJPG|MJPEG" <<<"$formats"; then
    echo "mjpeg"
    return 0
  fi

  if grep -Eq "YUYV|YUY2" <<<"$formats"; then
    echo "yuyv422"
    return 0
  fi

  echo ""
}

main() {
  local camera_dev
  local input_format
  local -a ffmpeg_args

  if ! camera_dev="$(find_usb_camera)"; then
    echo "[ERROR] No USB video capture device found." >&2
    exit 1
  fi

  input_format="$(pick_input_format "$camera_dev")"

  echo "[INFO] Selected camera: $camera_dev"
  echo "[INFO] RTSP URL: $RTSP_URL"
  if [ -n "$input_format" ]; then
    echo "[INFO] Input format: $input_format"
  else
    echo "[INFO] Input format: auto"
  fi

  ffmpeg_args=(
    /usr/bin/ffmpeg
    -loglevel "$LOGLEVEL"
    -f v4l2
    -framerate "$FRAMERATE"
    -video_size "$VIDEO_SIZE"
  )

  if [ -n "$input_format" ]; then
    ffmpeg_args+=(-input_format "$input_format")
  fi

  ffmpeg_args+=(
    -i "$camera_dev"
    -an
    -vf format=yuv420p
    -c:v libx264
    -preset veryfast
    -tune zerolatency
    -g 30
    -f rtsp
    -rtsp_transport tcp
    -muxdelay 0.1
    "$RTSP_URL"
  )

  exec "${ffmpeg_args[@]}"
}

main "$@"
