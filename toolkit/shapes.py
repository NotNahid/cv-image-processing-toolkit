import math
import cv2
import numpy as np


# -------------------------------------------------------------
# 1. Classical Geometric Shape Classification (Synthetic / Objects)
# -------------------------------------------------------------

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
        cv2.drawContours(canvas, [cnt], -1, color, 2)

        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        else:
            cx, cy = cnt[0][0][0], cnt[0][0][1]

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


# -------------------------------------------------------------
# 2. Health & Biomedical Morphometry (Cells & Lesions)
# -------------------------------------------------------------

def classify_cell(contour: np.ndarray) -> str:
    """
    Classifies a blood cell based on circularity and elongation:
    - 'normal_rbc': biconcave disc with circular 2D projection (circularity >= 0.75)
    - 'sickle_cell': abnormal crescent/elongated sickle erythrocyte (circularity < 0.65, high aspect ratio)
    - 'irregular_cell': intermediate or distorted morphology
    """
    peri = cv2.arcLength(contour, True)
    if peri == 0:
        return "unknown"

    area = cv2.contourArea(contour)
    circularity = (4 * math.pi * area) / (peri * peri)

    # Calculate elongation via minimum area bounding box
    rect = cv2.minAreaRect(contour)
    w, h = rect[1]
    aspect_ratio = (max(w, h) / min(w, h)) if (min(w, h) > 0) else 1.0

    if circularity >= 0.75 and aspect_ratio < 1.35:
        return "normal_rbc"
    elif circularity < 0.68 and aspect_ratio >= 1.4:
        return "sickle_cell"
    else:
        return "irregular_cell"


def measure_lesion_irregularity(contour: np.ndarray) -> dict:
    """
    Measures clinical ABCDE morphometry for skin lesions (melanoma vs benign mole):
    - Area (in pixels)
    - Solidity: Area / ConvexHull Area (low solidity indicates jagged/scalloped border)
    - Border Irregularity: Flagged if solidity < 0.88
    """
    area = cv2.contourArea(contour)
    peri = cv2.arcLength(contour, True)
    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull)

    solidity = float(area) / hull_area if hull_area > 0 else 0.0
    circularity = (4 * math.pi * area) / (peri * peri) if peri > 0 else 0.0

    return {
        "area_pixels": float(area),
        "perimeter_pixels": float(peri),
        "solidity": round(solidity, 3),
        "circularity": round(circularity, 3),
        "is_border_irregular": bool(solidity < 0.88),
    }


def annotate_cells(
    image: np.ndarray,
    contours: list[np.ndarray],
    cell_types: list[str],
) -> np.ndarray:
    """
    Annotates cells with color-coded boundaries:
    - Green for normal_rbc
    - Red for sickle_cell
    - Yellow for irregular_cell
    """
    canvas = image.copy()
    if len(canvas.shape) == 2 or canvas.shape[2] == 1:
        canvas = cv2.cvtColor(canvas, cv2.COLOR_GRAY2RGB)

    colors = {
        "normal_rbc": (0, 255, 0),       # Green
        "sickle_cell": (255, 0, 0),      # Red
        "irregular_cell": (255, 200, 0),  # Yellow
    }

    for cnt, ctype in zip(contours, cell_types):
        color = colors.get(ctype, (0, 255, 255))
        cv2.drawContours(canvas, [cnt], -1, color, 2)

    return canvas



# -------------------------------------------------------------
# 2. Health & Biomedical Morphometry (Cells & Lesions)
# -------------------------------------------------------------

def classify_cell(contour: np.ndarray) -> str:
    """
    Classifies a blood cell based on circularity and elongation:
    - 'normal_rbc': biconcave disc with circular 2D projection (circularity >= 0.75)
    - 'sickle_cell': abnormal crescent/elongated sickle erythrocyte (circularity < 0.65, high aspect ratio)
    - 'irregular_cell': intermediate or distorted morphology
    """
    peri = cv2.arcLength(contour, True)
    if peri == 0:
        return "unknown"

    area = cv2.contourArea(contour)
    circularity = (4 * math.pi * area) / (peri * peri)

    # Calculate elongation via minimum area bounding box
    rect = cv2.minAreaRect(contour)
    w, h = rect[1]
    aspect_ratio = (max(w, h) / min(w, h)) if (min(w, h) > 0) else 1.0

    if circularity >= 0.75 and aspect_ratio < 1.35:
        return "normal_rbc"
    elif circularity < 0.68 and aspect_ratio >= 1.4:
        return "sickle_cell"
    else:
        return "irregular_cell"


def measure_lesion_irregularity(contour: np.ndarray) -> dict:
    """
    Measures clinical ABCDE morphometry for skin lesions (melanoma vs benign mole):
    - Area (in pixels)
    - Solidity: Area / ConvexHull Area (low solidity indicates jagged/scalloped border)
    - Border Irregularity: Flagged if solidity < 0.88
    """
    area = cv2.contourArea(contour)
    peri = cv2.arcLength(contour, True)
    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull)

    solidity = float(area) / hull_area if hull_area > 0 else 0.0
    circularity = (4 * math.pi * area) / (peri * peri) if peri > 0 else 0.0

    return {
        "area_pixels": float(area),
        "perimeter_pixels": float(peri),
        "solidity": round(solidity, 3),
        "circularity": round(circularity, 3),
        "is_border_irregular": bool(solidity < 0.88),
    }


def annotate_cells(
    image: np.ndarray,
    contours: list[np.ndarray],
    cell_types: list[str],
) -> np.ndarray:
    """
    Annotates cells with color-coded boundaries:
    - Green for normal_rbc
    - Red for sickle_cell
    - Yellow for irregular_cell
    """
    canvas = image.copy()
    if len(canvas.shape) == 2 or canvas.shape[2] == 1:
        canvas = cv2.cvtColor(canvas, cv2.COLOR_GRAY2RGB)

    colors = {
        "normal_rbc": (0, 255, 0),       # Green
        "sickle_cell": (255, 0, 0),      # Red
        "irregular_cell": (255, 200, 0),  # Yellow
    }

    for cnt, ctype in zip(contours, cell_types):
        color = colors.get(ctype, (0, 255, 255))
        cv2.drawContours(canvas, [cnt], -1, color, 2)

    return canvas