"""Measures how long each processing stage takes, using synthetic frames (no camera needed).

    python tools/benchmark.py            # 300 frames per resolution
    python tools/benchmark.py --frames 1000

Camera capture and window drawing depend on your hardware and are NOT measured here.
Run it on your own machine before drawing conclusions about frame rate.
"""
import argparse
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

from motion_app.config import Config  # noqa: E402
from motion_app.detector import MotionDetector  # noqa: E402
from motion_app.pipeline import MotionPipeline  # noqa: E402
from motion_app.preprocess import preprocess  # noqa: E402

RESOLUTIONS = [(640, 480), (1280, 720), (1920, 1080)]


def make_frames(w, h, n):
    rng = np.random.default_rng(0)
    base = rng.integers(0, 40, (h, w, 3), dtype=np.uint8)
    frames = []
    size = h // 6
    for i in range(n):
        f = base.copy()
        x = (i * 7) % (w - size)
        f[h // 3: h // 3 + size, x: x + size] = 255
        frames.append(f)
    return frames


def avg_ms(fn, items):
    start = time.perf_counter()
    for item in items:
        fn(item)
    return (time.perf_counter() - start) / len(items) * 1000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", type=int, default=300)
    n = ap.parse_args().frames
    cfg = Config()

    print(f"{'resolution':>11} | {'preprocess':>10} | {'detect':>7} | {'pipeline':>8} | {'pipeline+mask':>13} | {'max fps':>7}")
    print("-" * 72)
    for w, h in RESOLUTIONS:
        frames = make_frames(w, h, n)
        pre = avg_ms(lambda f: preprocess(f, cfg.blur_kernel, cfg.process_width), frames)

        grays = [preprocess(f, cfg.blur_kernel, cfg.process_width) for f in frames]
        det = MotionDetector(cfg.pixel_cutoff)
        detect = avg_ms(det.analyse, grays)

        p1 = MotionPipeline(cfg)
        total = avg_ms(p1.process, frames)
        p2 = MotionPipeline(cfg)
        total_mask = avg_ms(lambda f: p2.process(f, keep_mask=True), frames)

        print(f"{f'{w}x{h}':>11} | {pre:>7.2f} ms | {detect:>4.2f} ms | {total:>5.2f} ms | {total_mask:>10.2f} ms | {1000 / total:>7.0f}")
    print("\nProcessing only: capture and display time are not included.")


if __name__ == "__main__":
    main()
