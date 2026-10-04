"""Stage 2 - grayscale and blur to suppress sensor noise and lighting flicker."""
import cv2
import numpy as np


def preprocess(frame: np.ndarray, blur_kernel: int = 21) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    k = max(1, blur_kernel) | 1  # Gaussian kernels must be odd
    return cv2.GaussianBlur(gray, (k, k), 0)
