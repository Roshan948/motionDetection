"""Stage 2 - resize to a fixed width, grayscale and blur.

Resizing first makes every later pixel-based number (blur size, direction dead zone,
changed-pixel percentage) mean the same thing whatever the camera resolution is.
"""
import cv2
import numpy as np


def preprocess(frame: np.ndarray, blur_kernel: int = 21, width: int = 640) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    h, w = gray.shape[:2]
    if w != width:
        new_h = max(1, round(h * width / w))
        interpolation = cv2.INTER_AREA if width < w else cv2.INTER_LINEAR
        gray = cv2.resize(gray, (width, new_h), interpolation=interpolation)

    k = max(1, blur_kernel) | 1  # Gaussian kernels must be odd
    return cv2.GaussianBlur(gray, (k, k), 0)
