#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import cv2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read an RTSP stream with OpenCV and print basic frame stats."
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
    return parser.parse_args()


def open_capture(source: str) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
    return cap


def main() -> int:
    args = parse_args()

    if args.sample_every <= 0:
        print("[ERROR] --sample-every must be >= 1", file=sys.stderr)
        return 2

    if args.save_dir is not None:
        args.save_dir.mkdir(parents=True, exist_ok=True)
        if args.save_every <= 0:
            print("[ERROR] --save-every must be >= 1", file=sys.stderr)
            return 2

    print(f"[INFO] Opening stream: {args.source}")
    cap = open_capture(args.source)
    if not cap.isOpened():
        print("[ERROR] Failed to open RTSP stream.", file=sys.stderr)
        return 1

    started = time.time()
    frames = 0
    first_frame_at: float | None = None
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps_hint = cap.get(cv2.CAP_PROP_FPS)
    print(f"[INFO] Capture opened: width={width}, height={height}, fps_hint={fps_hint:.2f}")

    try:
        while True:
            ok, frame = cap.read()
            now = time.time()

            if not ok:
                if first_frame_at is None and now - started > args.warmup_seconds:
                    print(
                        f"[ERROR] No frame received within {args.warmup_seconds:.1f}s.",
                        file=sys.stderr,
                    )
                    return 1
                time.sleep(0.1)
                continue

            if first_frame_at is None:
                first_frame_at = now
                print("[INFO] First frame received.")

            frames += 1

            if frames % args.sample_every == 0:
                elapsed = now - first_frame_at
                fps = frames / elapsed if elapsed > 0 else 0.0
                h, w = frame.shape[:2]
                print(
                    f"[INFO] frame={frames} size={w}x{h} avg_fps={fps:.2f}"
                )

            if args.save_dir is not None and frames % args.save_every == 0:
                output = args.save_dir / f"frame_{frames:06d}.jpg"
                cv2.imwrite(str(output), frame)
                print(f"[INFO] Saved {output}")

            if args.max_frames > 0 and frames >= args.max_frames:
                print(f"[INFO] Reached max frames: {frames}")
                return 0

    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
        return 0
    finally:
        cap.release()


if __name__ == "__main__":
    raise SystemExit(main())
