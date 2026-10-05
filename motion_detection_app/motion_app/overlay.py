"""Draws the status banner, the score and a direction arrow on the video frame."""
import cv2
import numpy as np

from .pipeline import FrameResult

GREEN = (0, 200, 0)
RED = (0, 0, 255)
WHITE = (255, 255, 255)
BANNER = (30, 30, 30)
FONT = cv2.FONT_HERSHEY_SIMPLEX

ARROWS = {"Left": (-1, 0), "Right": (1, 0), "Up": (0, -1), "Down": (0, 1)}


def draw_status(frame: np.ndarray, result: FrameResult) -> np.ndarray:
    h, w = frame.shape[:2]
    color = RED if result.moving else GREEN

    cv2.rectangle(frame, (0, 0), (w, 48), BANNER, -1)
    cv2.putText(frame, result.label, (16, 33), FONT, 0.9, color, 2, cv2.LINE_AA)
    cv2.putText(frame, f"changed {result.score:.2f}%", (16, h - 14), FONT, 0.5, WHITE, 1, cv2.LINE_AA)

    if result.direction in ARROWS:
        dx, dy = ARROWS[result.direction]
        cx, cy = w // 2, h // 2
        cv2.arrowedLine(frame, (cx - dx * 50, cy - dy * 50), (cx + dx * 50, cy + dy * 50),
                        color, 5, cv2.LINE_AA, tipLength=0.35)
    return frame
