import cv2
import numpy as np


def separate_touching_cells(
    binary: np.ndarray,
    min_distance_factor: float = 0.4,
    min_area: float = 50.0,
) -> np.ndarray:
    """
    Separates overlapping/clustered cells using Euclidean Distance Transform + Watershed.
    
    Args:
        binary: 8-bit single-channel binary image (foreground objects must be white=255).
        min_distance_factor: Ratio of max distance to threshold cell nuclei centers (0.2 - 0.6).
        min_area: Filter out tiny noise before splitting.
        
    Returns:
        binary mask with 1-pixel boundary lines (0) separating formerly touching cells.
    """
    # 1. Morphological clean to close small internal holes
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    clean_binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)

    # 2. Sure background area via dilation
    sure_bg = cv2.dilate(clean_binary, kernel, iterations=2)

    # 3. Distance transform to identify cell centers (peaks of distance to border)
    dist_transform = cv2.distanceTransform(clean_binary, cv2.DIST_L2, 5)
    
    if dist_transform.max() == 0:
        return binary.copy()

    # Peak thresholding: points above this threshold are guaranteed cell centers
    _, sure_fg = cv2.threshold(
        dist_transform,
        min_distance_factor * dist_transform.max(),
        255,
        cv2.THRESH_BINARY,
    )
    sure_fg = np.uint8(sure_fg)

    # 4. Unknown boundary zone between cells
    unknown = cv2.subtract(sure_bg, sure_fg)

    # 5. Marker labeling: label each distinct cell center with a unique positive integer
    num_markers, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1  # Shift so background is 1 instead of 0
    markers[unknown == 255] = 0  # Unknown border region is 0 for watershed to resolve

    # 6. Apply watershed on a 3-channel canvas
    canvas_3ch = cv2.cvtColor(clean_binary, cv2.COLOR_GRAY2BGR)
    markers = cv2.watershed(canvas_3ch, markers)

    # Watershed marks dividing boundaries as -1
    separated = clean_binary.copy()
    separated[markers == -1] = 0
    return separated

