# CV Image Processing Toolkit

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR_USERNAME/cv-image-processing-toolkit/blob/main/notebooks/cv_image_processing_toolkit_colab.ipynb)

A classical computer-vision toolkit built with OpenCV: read images, detect edges,
extract contours, and classify geometric shapes (circle, triangle, square, rectangle,
pentagon, hexagon, polygon) — plus a set of biomedical image-processing demos.

No deep learning, no training loop. The goal is fluency with the pipeline that every
later, fancier CV project depends on: image I/O → preprocessing → edge detection →
contour extraction → shape classification.

## 🌐 Live showcase

**https://YOUR_USERNAME.github.io/cv-image-processing-toolkit/** — interactive pipeline explorer, in-browser playground, health demos and live CI status.
The home page is a draggable gallery of every pipeline step (click a tile to zoom; keys `1` `2` `3` `F`); `classic.html` has the in-browser playground.
It is rebuilt automatically by GitHub Actions (`.github/workflows/ci.yml`) on every push: tests run, every image and number is regenerated from the real code, then the site redeploys.

## ▶️ Try it in your browser (no install)

Click the **Open in Colab** badge above, then **Runtime → Run all**.
`notebooks/cv_image_processing_toolkit_colab.ipynb` is a single self-contained notebook:
the whole toolkit, the synthetic dataset generator, an accuracy test, real-photo and
health demos, and a cell where you can **upload your own image**.

## Pipeline

1. **Read & preprocess** — load an image, convert color spaces, denoise/blur, threshold (Otsu), CLAHE, morphology.
2. **Detect edges** — Sobel, Canny, and `auto_canny` (thresholds derived from each image's own median).
3. **Extract contours** — turn edges/masks into closed object outlines (`cv2.findContours`).
4. **Identify shapes** — classify each contour by circularity and vertex count.
5. **Biomedical demos** — X-ray contrast (CLAHE), sickle-cell morphometry, melanoma border solidity,
   retinal vessel extraction, blood-smear watershed cell separation.

> ⚠️ The health demos are educational image-processing exercises, **not** medical diagnostics.

## Repo layout

```
toolkit/        # the library: io, preprocess, edges, contours, shapes, segmentation
docs/           # showcase site: index.html (gallery), classic.html (playground), vendor/ (GSAP), CI-generated assets/ + results.json
scripts/        # build_showcase.py: regenerates docs/ assets + results.json
.github/        # CI/CD workflow (test → build → deploy to GitHub Pages)
tests/          # synthetic-shape accuracy test + hexagon / auto_canny tests
notebooks/      # step-by-step walkthroughs (+ the single-file Colab notebook)
data/synthetic/ # generated shapes with known ground truth
data/real/      # real photos (coins, book, stop sign, dice)
data/health/    # open-licensed biomedical images
```

## Quick example

```python
from toolkit import (load_image, to_grayscale, blur, threshold_otsu,
                     find_contours, classify_contour)

img = load_image("data/real/book.jpg")
binary = threshold_otsu(blur(to_grayscale(img)))
contours = find_contours(binary, min_area=100)
print([classify_contour(c) for c in contours])   # ['rectangle']
```

## Install (development)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest
```

## Known limitations

- A single global Otsu threshold fails on reflective/textured objects (e.g. `coins.jpg`).
- A circle and an octagon both simplify to ~8 vertices, so geometric rules call a stop sign a `circle`.
- Images taken through a microscope eyepiece need the circular field of view masked first
  (see the blood-smear section of the Colab notebook).

## Credits

Original project by [@khalilurrrahmanridoykhan](https://github.com/khalilurrrahmanridoykhan/cv-image-processing-toolkit).
This fork adds the single-file Colab notebook, de-duplicated library code, `auto_canny`,
a `hexagon` shape label, a better blood-smear segmentation, and tests.
Image sources and licenses: `data/real/SOURCES.md`, `data/health/SOURCES.md`.

## License

Apache License 2.0 — see [LICENSE](LICENSE).
