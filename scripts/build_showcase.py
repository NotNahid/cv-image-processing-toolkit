"""Builds docs/assets/* (step-by-step images) and docs/results.json for the showcase page.
Run from the repo root:  python scripts/build_showcase.py
In CI this runs on every push, so the page always reflects the latest code."""
import json, os, re, subprocess, sys, datetime
from pathlib import Path
import cv2, numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from toolkit import *  # noqa

OUT = ROOT / "docs" / "assets"; OUT.mkdir(parents=True, exist_ok=True)
REAL, HEALTH, SYN = ROOT/"data/real", ROOT/"data/health", ROOT/"data/synthetic"

def save(name, img, w=520):
    if img.ndim == 2: img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    h = int(img.shape[0] * w / img.shape[1])
    cv2.imwrite(str(OUT/f"{name}.jpg"), cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 82])

def bgr(rgb): return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

def mask_for(im, name):
    if name == "stop_sign":
        hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
        m = cv2.inRange(hsv,(0,120,70),(10,255,255)) | cv2.inRange(hsv,(170,120,70),(180,255,255))
        return morphological_clean(m, 9, 2)
    bw = threshold_otsu(blur(to_grayscale(im)))
    border = np.concatenate([bw[0], bw[-1], bw[:,0], bw[:,-1]])
    return 255 - bw if border.mean() > 127 else bw

# ---- real photos: 6 pipeline steps each
summary = {}
for name in ["book", "dice", "stop_sign", "coins"]:
    im = load_image(REAL/f"{name}.jpg"); g = to_grayscale(im); b = blur(g)
    bw = mask_for(im, name)
    cnts = find_contours(bw, min_area=0.01*im.shape[0]*im.shape[1])[:3]
    labs = [classify_contour(c) for c in cnts]
    steps = {"original": im, "gray": g, "blur": b, "mask": bw, "edges": auto_canny(b),
             "result": bgr(annotate_shapes(to_rgb(im), cnts, labs, font_scale=1.4))}
    for k, v in steps.items(): save(f"{name}_{k}", v)
    summary[name] = labs

# ---- health demos
x = to_grayscale(load_image(HEALTH/"chest_xray.png"))
save("xray_before", x); save("xray_after", apply_clahe(x, 2.5, 8))

im = load_image(HEALTH/"skin_lesion_melanoma.jpg")
main = find_contours(threshold_otsu(blur(to_grayscale(im), 15), invert=True), min_area=1000)[0]
mel = measure_lesion_irregularity(main); c = im.copy()
cv2.drawContours(c, [cv2.convexHull(main)], -1, (0,0,255), 6); cv2.drawContours(c, [main], -1, (0,255,0), 6)
save("melanoma", c)

im = load_image(HEALTH/"sickle_cell.jpg"); cl = morphological_clean(threshold_otsu(to_grayscale(im), invert=True), 3)
cn = find_contours(cl, min_area=35); ty = [classify_cell(k) for k in cn]
save("sickle", bgr(annotate_cells(to_rgb(im), cn, ty)))

fu = to_rgb(load_image(HEALTH/"retina_fundus.jpg"))
save("retina_before", bgr(fu)); save("retina_after", canny_edges(apply_clahe(fu[:,:,1], 3.0, 8), 25, 60))

im = load_image(HEALTH/"blood_smear.jpg"); g = to_grayscale(im); s = .25
circ = cv2.HoughCircles(cv2.GaussianBlur(cv2.resize(g,None,fx=s,fy=s),(9,9),2), cv2.HOUGH_GRADIENT,1,50,param1=100,param2=40,minRadius=60,maxRadius=120)
fov = np.zeros_like(g)
if circ is not None:
    cx, cy, r = circ[0][0]/s; cv2.circle(fov,(int(cx),int(cy)),int(r*.88),255,-1)
else: fov[:] = 255
d = cv2.bitwise_and(cv2.subtract(cv2.GaussianBlur(im[:,:,1],(0,0),25), im[:,:,1]), fov)
sm = morphological_clean(cv2.bitwise_and(threshold_otsu(cv2.GaussianBlur(d,(3,3),0)), fov), 3)
sep = separate_touching_cells(sm, 0.4); cells = find_contours(sep, min_area=30)
save("smear", draw_contours(im, cells, (0,200,0), 2), w=420)

# ---- synthetic accuracy
truth = json.loads((SYN/"ground_truth.json").read_text()); per = {}; ok = 0
for t in truth:
    im = load_image(SYN/"images"/t["filename"])
    c = find_contours(threshold_otsu(blur(to_grayscale(im)), invert=True), min_area=100)
    p = classify_contour(c[0]) if c else "none"
    per.setdefault(t["shape"], [0, 0]); per[t["shape"]][1] += 1; per[t["shape"]][0] += (p == t["shape"]); ok += (p == t["shape"])

# ---- tests
r = subprocess.run([sys.executable, "-m", "pytest", "-q", "--no-header"], cwd=ROOT, capture_output=True, text=True)
m = re.search(r"(\d+) passed", r.stdout); f = re.search(r"(\d+) failed", r.stdout)

results = {
    "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    "commit": os.environ.get("GITHUB_SHA", "local")[:7],
    "tests_passed": int(m.group(1)) if m else 0, "tests_failed": int(f.group(1)) if f else 0,
    "synthetic": {"correct": ok, "total": len(truth), "accuracy": round(ok/len(truth), 4),
                  "per_shape": {k: {"correct": a, "total": n} for k, (a, n) in per.items()}},
    "real_photo_labels": summary,
    "health": {"cells_detected_smear": len(cells), "sickle_cells": ty.count("sickle_cell"),
               "normal_cells": ty.count("normal_rbc"), "melanoma_solidity": mel["solidity"],
               "melanoma_irregular": mel["is_border_irregular"]},
}
(ROOT/"docs"/"results.json").write_text(json.dumps(results, indent=2))
print(json.dumps(results, indent=2)); sys.exit(1 if results["tests_failed"] else 0)
