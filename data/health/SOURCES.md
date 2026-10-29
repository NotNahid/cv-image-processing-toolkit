# Health & Biomedical Image Dataset Sources

All images in this directory are open-access, public domain, or openly licensed (CC0 / CC BY) from Wikimedia Commons and US Federal Health Agencies (National Institutes of Health / National Cancer Institute / NHLBI).

| File | Domain | Source | Author / Institution | License |
| :--- | :--- | :--- | :--- | :--- |
| `blood_smear.jpg` | Hematology / Microscopy | [Blood smear.jpg](https://commons.wikimedia.org/wiki/File:Blood_smear.jpg) | Dr. Graham Beards | CC BY 4.0 |
| `sickle_cell.jpg` | Hematology / Pathology | [Sickle cell 01.jpg](https://commons.wikimedia.org/wiki/File:Sickle_cell_01.jpg) | National Heart, Lung, and Blood Institute (NHLBI) | Public Domain |
| `chest_xray.png` | Radiology / X-Ray | [Chest Xray PA 3-8-2010.png](https://commons.wikimedia.org/wiki/File:Chest_Xray_PA_3-8-2010.png) | User:Stillwaterising | CC0 1.0 Universal |
| `skin_lesion_melanoma.jpg` | Dermatology / Dermoscopy | [Melanoma.jpg](https://commons.wikimedia.org/wiki/File:Melanoma.jpg) | National Cancer Institute (NCI) | Public Domain |
| `retina_fundus.jpg` | Ophthalmology / Fundus | [Fundus photograph of normal left eye.jpg](https://commons.wikimedia.org/wiki/File:Fundus_photograph_of_normal_left_eye.jpg) | Mikael Häggström (MD) | CC0 1.0 Universal |

---

### Computer Vision Challenges & Relevance:

1. **`blood_smear.jpg` (Cell Counting & Segmentation)**:
   - High-resolution peripheral blood smear (Wright/Giemsa stain).
   - **CV Target**: Distinguish Red Blood Cells (RBCs) from White Blood Cells (WBCs), isolate the purple cell nucleus, and test **Watershed segmentation** to separate touching/clustered red blood cells.

2. **`sickle_cell.jpg` (Morphometry & Circularity)**:
   - Blood smear featuring sickle-cell disease erythrocytes alongside normal round discoid cells.
   - **CV Target**: Test contour **circularity**, **eccentricity**, and **aspect ratio** to distinguish elongated/crescent sickled cells from normal circular RBCs.

3. **`chest_xray.png` (Contrast Enhancement & Anatomical Contours)**:
   - High-resolution posteroanterior (PA) chest radiograph.
   - **CV Target**: Test **CLAHE** (Contrast Limited Adaptive Histogram Equalization) to bring out rib and spine detail without saturation, followed by lung cavity thresholding.

4. **`skin_lesion_melanoma.jpg` (Dermatological ABCDE Profiling)**:
   - Clinical close-up of a malignant melanoma skin lesion.
   - **CV Target**: Contour extraction on soft skin gradients, measuring **Asymmetry (A)** and **Border irregularity (B)** using contour solidity ($\text{Area} / \text{ConvexHull Area}$).

5. **`retina_fundus.jpg` (Vessel Segmentation)**:
   - Fundus photography of human retina showing optic disc and retinal vascular tree.
   - **CV Target**: Extracting the green channel (highest contrast for blood vessels) and applying edge/ridge detection to trace microvasculature.

