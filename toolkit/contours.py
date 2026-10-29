import cv2
import numpy as np

def find_contours(
    binary: np.ndarray, 
    min_area: float = 50.0, 
    external_only: bool = True
) -> list[np.ndarray]:
    mode = cv2.RETR_EXTERNAL if external_only else cv2.RETR_LIST
    contours, _ = cv2.findContours(binary, mode, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter out tiny noise contours
    valid_contours = [c for c in contours if cv2.contourArea(c) >= min_area]
    
    # Sort descending by area
    valid_contours.sort(key=cv2.contourArea, reverse=True)
    return valid_contours


def draw_contours(
    image: np.ndarray, 
    contours: list[np.ndarray], 
    color: tuple[int, int, int] = (0, 255, 0), 
    thickness: int = 2
) -> np.ndarray:
    """
    Draw contours on a copy of the input image.
    """
    # If grayscale, convert to BGR so we can draw colorful outlines
    if len(image.shape) == 2 or image.shape[2] == 1:
        canvas = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        canvas = image.copy()
        
    cv2.drawContours(canvas, contours, -1, color, thickness)
    return canvas