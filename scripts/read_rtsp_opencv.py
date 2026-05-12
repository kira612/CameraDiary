#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import cv2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read and display an RTSP stream with OpenCV."
    )
    parser.add_argument(
        "--source",
        default="rtsp://localhost:8554/cam1",
        help="RTSP URL to read.",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=0,
        help="Stop after N frames. 0 means unlimited.",
    )
    parser.add_argument(
        "--sample-every",
        type=int,
        default=30,
        help="Print one progress line every N frames.",
    )
    parser.add_argument(
        "--save-dir",
        type=Path,
        default=None,
        help="Optional directory to save sampled JPEG frames.",
    )
    parser.add_argument(
        "--save-every",
        type=int,
        default=150,
        help="Save one JPEG every N frames when --save-dir is set.",
    )
    parser.add_argument(
        "--warmup-seconds",
        type=float,
        default=10.0,
        help="Fail if the first frame is not received within this time.",
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Disable the OpenCV preview window.",
    )
    return parser.parse_args()


def open_capture(source: str) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
    return cap


def check_display_available() -> bool:
    build_info = cv2.getBuildInformation()
    gui_line = next(
        (line.strip() for line in build_info.splitlines() if line.strip().startswith("GUI:")),
        "",
    )
    if gui_line.endswith("NONE"):
        print(
            "[ERROR] この OpenCV は GUI バックエンドなしでビルドされているため、cv2.imshow() を使用できません。",
            file=sys.stderr,
        )
        print(
            "[ERROR] GUI 対応版の OpenCV をインストールするか、--no-display を付けて実行してください。",
            file=sys.stderr,
        )
        return False

    if sys.platform.startswith("linux") and not (
        os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
    ):
        print(
            "[ERROR] Linux の表示サーバーが検出できません。DISPLAY/WAYLAND_DISPLAY を設定するか、--no-display を付けて実行してください。",
            file=sys.stderr,
        )
        return False

    return True


def main() -> int:
    args = parse_args()

    if args.sample_every <= 0:
        print("[ERROR] --sample-every は 1 以上を指定してください。", file=sys.stderr)
        return 2

    if args.save_dir is not None:
        args.save_dir.mkdir(parents=True, exist_ok=True)
        if args.save_every <= 0:
            print("[ERROR] --save-every は 1 以上を指定してください。", file=sys.stderr)
            return 2

    display_enabled = not args.no_display
    if display_enabled and not check_display_available():
        return 2

    print(f"[INFO] ストリームを開いています: {args.source}")
    cap = open_capture(args.source)
    if not cap.isOpened():
        print("[ERROR] RTSP ストリームを開けませんでした。", file=sys.stderr)
        return 1

    started = time.time()
    frames = 0
    first_frame_at: float | None = None
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps_hint = cap.get(cv2.CAP_PROP_FPS)
    print(f"[INFO] キャプチャを開始しました: 幅={width}, 高さ={height}, 推定FPS={fps_hint:.2f}")

    window_name = "RTSP OpenCV Preview"
    if display_enabled:
        print("[INFO] 表示を有効にしました。終了するにはプレビューウィンドウで 'q' または Esc を押してください。")

    try:
        while True:
            ok, frame = cap.read()
            now = time.time()

            if not ok:
                if first_frame_at is None and now - started > args.warmup_seconds:
                    print(
                        f"[ERROR] {args.warmup_seconds:.1f} 秒以内にフレームを受信できませんでした。",
                        file=sys.stderr,
                    )
                    return 1
                time.sleep(0.1)
                continue

            if first_frame_at is None:
                first_frame_at = now
                print("[INFO] 最初のフレームを受信しました。")

            frames += 1

            if frames % args.sample_every == 0:
                elapsed = now - first_frame_at
                fps = frames / elapsed if elapsed > 0 else 0.0
                h, w = frame.shape[:2]
                print(
                    f"[INFO] フレーム={frames} サイズ={w}x{h} 平均FPS={fps:.2f}"
                )

            if args.save_dir is not None and frames % args.save_every == 0:
                output = args.save_dir / f"frame_{frames:06d}.jpg"
                cv2.imwrite(str(output), frame)
                print(f"[INFO] 保存しました: {output}")

            if display_enabled:
                cv2.imshow(window_name, frame)
                key = cv2.waitKey(1) & 0xFF
                if key in (ord("q"), 27):
                    print("[INFO] プレビューウィンドウで終了が要求されました。")
                    return 0

            if args.max_frames > 0 and frames >= args.max_frames:
                print(f"[INFO] 最大フレーム数に到達しました: {frames}")
                return 0

    except KeyboardInterrupt:
        print("\n[INFO] ユーザー操作により中断されました。")
        return 0
    finally:
        cap.release()
        if display_enabled:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    raise SystemExit(main())

