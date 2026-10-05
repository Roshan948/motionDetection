"""Run with:  python main.py   (press q to quit, m to show the motion mask)"""
import argparse

import cv2

from motion_app.app import run
from motion_app.config import Config


def parse_args(argv=None):
    d = Config()
    p = argparse.ArgumentParser(
        description="Webcam motion and direction detector. "
                    "Keys: q = quit, m = toggle motion mask window."
    )
    p.add_argument("--camera", type=int, default=d.camera_index, help="camera index (default 0)")
    p.add_argument("--no-mirror", action="store_true", help="do not flip the video horizontally")
    p.add_argument("--threshold", type=float, default=d.motion_threshold_pct,
                   help="percent of the frame that must change to count as motion (default 0.33)")
    p.add_argument("--min-shift", type=int, default=d.min_shift, help="dead zone in pixels for direction")
    p.add_argument("--history", type=int, default=d.history_length, help="frames used to measure direction")
    p.add_argument("--rest-delay", type=int, default=d.rest_delay_frames, help="still frames before 'Body in rest'")
    p.add_argument("--blur", type=int, default=d.blur_kernel, help="Gaussian blur kernel size")
    p.add_argument("--process-width", type=int, default=d.process_width,
                   help="frames are resized to this width before analysis (default 640)")
    p.add_argument("--log", action="store_true", help="save state changes to logs/*.csv")
    p.add_argument("--max-logs", type=int, default=d.max_log_files, help="keep only this many newest log files")
    return p.parse_args(argv)


def main():
    args = parse_args()
    try:
        config = Config(
            camera_index=args.camera, mirror=not args.no_mirror,
            motion_threshold_pct=args.threshold, min_shift=args.min_shift,
            history_length=args.history, rest_delay_frames=args.rest_delay,
            blur_kernel=args.blur, process_width=args.process_width,
            log_events=args.log, max_log_files=args.max_logs,
        )
        run(config)
    except KeyboardInterrupt:
        pass
    except (RuntimeError, ValueError, OSError, cv2.error) as err:
        raise SystemExit(f"Error: {err}")


if __name__ == "__main__":
    main()
