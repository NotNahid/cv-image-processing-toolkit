import cv2
import numpy as np


def sobel_edges(gray: np.ndarray) -> np.ndarray:
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
    return cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)


def canny_edges(gray: np.ndarray, low: int = 50, high: int = 150) -> np.ndarray:
    return cv2.Canny(gray, low, high)


def auto_canny(gray: np.ndarray, sigma: float = 0.33) -> np.ndarray:
    """
    Canny with thresholds derived from the image's own median intensity.
    Addresses the finding in RESULTS.md that one fixed (low, high) pair
    does not generalize across photos.
    """
    v = np.median(gray)
    low = int(max(0, (1.0 - sigma) * v))
    high = int(min(255, (1.0 + sigma) * v))
    return cv2.Canny(gray, low, high)
