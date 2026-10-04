"""The run loop: camera -> pipeline -> overlay -> window."""
from __future__ import annotations

import cv2

from .camera import Camera
from .config import Config
from .event_log import EventLogger
from .overlay import draw_status
from .pipeline import MotionPipeline

MASK_WINDOW = "Motion mask"


def run(config: Config) -> None:
    pipeline = MotionPipeline(config)
    logger = EventLogger(config.log_dir) if config.log_events else None
    show_mask = False

    try:
        with Camera(config.camera_index, config.mirror) as camera:
            while True:
                frame = camera.read()
                if frame is None:
                    print("The camera stopped delivering frames.")
                    break

                result = pipeline.process(frame)
                if logger:
                    logger.log(result)

                cv2.imshow(config.window_name, draw_status(frame, result))
                if show_mask and result.mask is not None:
                    cv2.imshow(MASK_WINDOW, result.mask)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                if key == ord("m"):
                    show_mask = not show_mask
                    if not show_mask:
                        try:
                            cv2.destroyWindow(MASK_WINDOW)
                        except cv2.error:
                            pass
    finally:
        if logger:
            logger.close()
            print(f"Event log saved to {logger.path}")
        cv2.destroyAllWindows()
