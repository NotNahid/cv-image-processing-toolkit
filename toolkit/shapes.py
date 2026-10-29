import math
import cv2
import numpy as np


def classify_contour(contour: np.ndarray) -> str:
    """
    Classify a single contour into a geometric shape:
    circle, triangle, square, rectangle, pentagon, or polygon.
    """
    peri = cv2.arcLength(contour, True)
    if peri == 0:
        return "unknown"

    area = cv2.contourArea(contour)
    circularity = (4 * math.pi * area) / (peri * peri)

    # 1. Check for circle first using circularity metric
    if circularity > 0.82:
        return "circle"

    # 2. Approximate polygon using Douglas-Peucker algorithm
    approx = cv2.approxPolyDP(contour, 0.035 * peri, True)
    num_vertices = len(approx)

    if num_vertices == 3:
        return "triangle"

    elif num_vertices == 4:
        # Distinguish square vs rectangle using rotated bounding box
        rect = cv2.minAreaRect(contour)
        w, h = rect[1]
        if w == 0 or h == 0:
            return "rectangle"
        aspect_ratio = max(w, h) / min(w, h)
        return "square" if aspect_ratio < 1.15 else "rectangle"

    elif num_vertices == 5:
        return "pentagon"

    elif circularity > 0.75:
        return "circle"

    else:
        return "polygon"


def annotate_shapes(
    image: np.ndarray,
    contours: list[np.ndarray],
    labels: list[str],
    color: tuple[int, int, int] = (0, 255, 0),
) -> np.ndarray:
    """
    Draw contours and their predicted shape label on a copy of the image.
    """
    canvas = image.copy()
    if len(canvas.shape) == 2 or canvas.shape[2] == 1:
        canvas = cv2.cvtColor(canvas, cv2.COLOR_GRAY2RGB)

    for cnt, label in zip(contours, labels):
        # Draw contour border
        cv2.drawContours(canvas, [cnt], -1, color, 2)

        # Find center of contour using spatial moments
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        else:
            cx, cy = cnt[0][0][0], cnt[0][0][1]

        # Draw text label
        cv2.putText(
            canvas,
            label,
            (cx - 25, cy),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 0, 0),
            2,
        )

    return canvas