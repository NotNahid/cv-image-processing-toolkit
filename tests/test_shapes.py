"""Accuracy test: classify the 30 synthetic shapes against their ground truth."""
import json
from pathlib import Path

import pytest

from toolkit import (
    blur, classify_contour, find_contours, load_image,
    threshold_otsu, to_grayscale, auto_canny,
)

SYNTH = Path(__file__).resolve().parents[1] / "data" / "synthetic"


def _predict(filename):
    img = load_image(SYNTH / "images" / filename)
    binary = threshold_otsu(blur(to_grayscale(img)), invert=True)  # dark shape, white bg
    contours = find_contours(binary, min_area=100)
    return classify_contour(contours[0]) if contours else "none"


def test_synthetic_accuracy_is_perfect():
    truth = json.loads((SYNTH / "ground_truth.json").read_text())
    wrong = [(t["filename"], t["shape"], _predict(t["filename"])) for t in truth
             if _predict(t["filename"]) != t["shape"]]
    assert not wrong, f"misclassified: {wrong}"


def test_hexagon_label():
    import cv2, numpy as np, math
    canvas = np.full((200, 200), 255, np.uint8)
    pts = np.array([[100 + 60*math.cos(math.radians(60*i)), 100 + 60*math.sin(math.radians(60*i))]
                    for i in range(6)], np.int32)
    cv2.fillPoly(canvas, [pts], 0)
    cnts = find_contours(threshold_otsu(canvas, invert=True), min_area=100)
    assert classify_contour(cnts[0]) == "hexagon"


def test_auto_canny_returns_edge_map():
    img = load_image(SYNTH / "images" / "circle_000.png")
    edges = auto_canny(blur(to_grayscale(img)))
    assert edges.shape == to_grayscale(img).shape and edges.max() == 255
