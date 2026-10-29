import cv2
import numpy as np


def blur(gray: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """Apply Gaussian blur to smooth noise while preserving major boundaries."""
    if kernel_size % 2 == 0:
        raise ValueError(f"kernel_size must be an odd integer, got {kernel_size}")
    return cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)


def threshold_otsu(gray: np.ndarray, invert: bool = False) -> np.ndarray:
    """
    Automatic binarization using Otsu's method.
    If invert is True, produces white objects on black background for dark features.
    """
    flag = cv2.THRESH_BINARY_INV if invert else cv2.THRESH_BINARY
    _, binary = cv2.threshold(gray, 0, 255, flag + cv2.THRESH_OTSU)
    return binary


def apply_clahe(gray: np.ndarray, clip_limit: float = 2.0, tile_grid_size: int = 8) -> np.ndarray:
    """
    Contrast Limited Adaptive Histogram Equalization (CLAHE).
    Standard enhancement for medical imaging (X-rays, CTs, mammograms).
    Brings out subtle contrast in bone fractures and lung soft tissue without over-amplifying noise.
    """
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_grid_size, tile_grid_size))
    return clahe.apply(gray)


def morphological_clean(binary: np.ndarray, kernel_size: int = 3, iterations: int = 1) -> np.ndarray:
    """
    Cleans noisy binary masks using morphological opening (speck removal)
    and closing (hole filling). Ideal for microscope slide artifacts.
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=iterations)
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel, iterations=iterations)
    return closed



def apply_clahe(gray: np.ndarray, clip_limit: float = 2.0, tile_grid_size: int = 8) -> np.ndarray:
    """
    Contrast Limited Adaptive Histogram Equalization (CLAHE).
    Standard enhancement for medical imaging (X-rays, CTs, mammograms).
    Brings out subtle contrast in bone fractures and lung soft tissue without over-amplifying noise.
    """
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_grid_size, tile_grid_size))
    return clahe.apply(gray)


def morphological_clean(binary: np.ndarray, kernel_size: int = 3, iterations: int = 1) -> np.ndarray:
    """
    Cleans noisy binary masks using morphological opening (speck removal)
    and closing (hole filling). Ideal for microscope slide artifacts.
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=iterations)
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel, iterations=iterations)
    return closed