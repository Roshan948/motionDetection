"""Run with:  python main.py   (press q to quit, m to show the motion mask)"""
import argparse

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
    p.add_argument("--threshold", type=int, default=d.motion_threshold, help="changed pixels that count as motion")
    p.add_argument("--min-shift", type=int, default=d.min_shift, help="dead zone in pixels for direction")
    p.add_argument("--history", type=int, default=d.history_length, help="frames used to measure direction")
    p.add_argument("--rest-delay", type=int, default=d.rest_delay_frames, help="still frames before 'Body in rest'")
    p.add_argument("--blur", type=int, default=d.blur_kernel, help="Gaussian blur kernel size")
    p.add_argument("--log", action="store_true", help="save state changes to logs/*.csv")
    return p.parse_args(argv)


def main():
    a = parse_args()
    try:
        config = Config(
            camera_index=a.camera, mirror=not a.no_mirror,
            motion_threshold=a.threshold, min_shift=a.min_shift,
            history_length=a.history, rest_delay_frames=a.rest_delay,
            blur_kernel=a.blur, log_events=a.log,
        )
        run(config)
    except (RuntimeError, ValueError) as err:
        raise SystemExit(f"Error: {err}")


if __name__ == "__main__":
    main()
