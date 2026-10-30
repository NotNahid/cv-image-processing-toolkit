gsap.registerPlugin(...[window.Draggable, window.InertiaPlugin, window.CustomEase, window.Flip].filter(Boolean));
const $ = (s) => document.querySelector(s), $$ = (s) => [...document.querySelectorAll(s)];

/* ---------- repo auto-detect (GitHub Pages) ---------- */
const H = location.hostname, P = location.pathname.split("/")[1];
const OWNER = H.endsWith(".github.io") ? H.split(".")[0] : "YOUR_USERNAME";
const REPO = H.endsWith(".github.io") && P ? P : "cv-image-processing-toolkit";
const API = `https://api.github.com/repos/${OWNER}/${REPO}`;
$("#lnkRepo").href = `https://github.com/${OWNER}/${REPO}`;
$("#lnkColab").href = `https://colab.research.google.com/github/${OWNER}/${REPO}/blob/main/notebooks/cv_image_processing_toolkit_colab.ipynb`;
$("#zoomColab").href = $("#lnkColab").href;

/* ---------- tile content (31 images made by CI) ---------- */
const PHOTO = { book: "Book", dice: "Dice", stop_sign: "Stop sign", coins: "Coins" };
const STEP = {
  original: ["As loaded", "Straight out of cv2.imread. Three colour channels, nothing touched yet.", "img = load_image(path)"],
  gray: ["Just brightness", "Colour thrown away. One number per pixel is all the next steps need.", "gray = to_grayscale(img)"],
  blur: ["Softened", "A small Gaussian blur, so noise stops looking like edges.", "blurred = blur(gray, 5)"],
  mask: ["Black or white", "Otsu picks the cut-off by itself. Every pixel is object or not.", "mask = threshold_otsu(blurred)"],
  edges: ["Where it changes", "Auto-Canny takes its thresholds from this image's own median, not a magic number.", "edges = auto_canny(blurred)"]
};
const RESULT = {
  book: "A rectangle, correctly. The easy case: bright object, plain background.",
  dice: "A cube seen at an angle has a hexagonal outline, so: hexagon.",
  stop_sign: "Called a circle. An octagon and a circle both simplify to about 8 corners, which this rule can't tell apart.",
  coins: "The hard one. Shiny ridges break a single threshold, so you get polygons instead of coins."
};
const TILES = [];
Object.keys(PHOTO).forEach((p) => ["original", "gray", "blur", "mask", "edges", "result"].forEach((s) => {
  const t = { src: `${p}_${s}`, tag: PHOTO[p] };
  if (s === "result") Object.assign(t, { title: "Classified", desc: RESULT[p], code: "classify_contour(contour)" });
  else if (p === "stop_sign" && s === "mask") Object.assign(t, { title: "By colour", desc: "Not brightness this time. The street behind is too busy, so the sign is picked out by its red.", code: "inRange(hsv, red) -> morphological_clean" });
  else Object.assign(t, { title: STEP[s][0], desc: STEP[s][1], code: STEP[s][2] });
  TILES.push(t);
}));
TILES.push(
  { src: "xray_before", tag: "Health", title: "Chest X-ray", desc: "Before. Flat and washed out, so ribs are hard to tell from lung.", code: "to_grayscale(xray)" },
  { src: "xray_after", tag: "Health", title: "CLAHE", desc: "Contrast boosted tile by tile. Ribs and spine come forward.", code: "apply_clahe(gray, 2.5, 8)" },
  { src: "melanoma", tag: "Health", title: "Border check", desc: "Green is the real edge, red is the convex hull. Solidity {sol}. Demo only, not a diagnosis.", code: "measure_lesion_irregularity(c)" },
  { src: "sickle", tag: "Health", title: "Cell shapes", desc: "Circularity and aspect ratio on a teaching illustration, not a real smear. {sick} elongated, {norm} round. It shows the metrics, nothing more.", code: "classify_cell(contour)" },
  { src: "retina_before", tag: "Health", title: "Fundus photo", desc: "The green channel has the most contrast for vessels, so that's the one we keep.", code: "fundus[:, :, 1]" },
  { src: "retina_after", tag: "Health", title: "Edge map", desc: "CLAHE on the green channel, then Canny. Noisy: a proper vessel filter would do better.", code: "canny_edges(clahe, 25, 60)" },
  { src: "smear", tag: "Health", title: "Cell count", desc: "Mask the circular eyepiece view, subtract the background, then watershed splits touching cells. {cells} found.", code: "separate_touching_cells(mask)" }
);
let RES = null;
const fill = (d) => d.replace("{sol}", RES?.health.melanoma_solidity ?? "…").replace("{sick}", RES?.health.sickle_cells ?? "…").replace("{norm}", RES?.health.normal_cells ?? "…").replace("{cells}", RES?.health.cells_detected_smear ?? "…");

/* ---------- live build status + results ---------- */
const ago = (d) => { const s = Math.max(0, (Date.now() - new Date(d)) / 1e3 | 0); return s < 60 ? s + "s" : s < 3600 ? (s / 60 | 0) + "m" : s < 86400 ? (s / 3600 | 0) + "h" : (s / 86400 | 0) + "d"; };
let lastRun = null;
async function pollCI() {
  try {
    const r = await fetch(API + "/actions/runs?per_page=1"); if (!r.ok) throw 0;
    lastRun = (await r.json()).workflow_runs?.[0]; if (!lastRun) throw 0;
    const s = lastRun.status !== "completed" ? "run" : lastRun.conclusion === "success" ? "ok" : "bad";
    $("#bdot").className = "dot " + s; $("#bst").textContent = { run: "Building…", ok: "Passing", bad: "Failing" }[s]; showAgo();
  } catch { $("#bst").textContent = "Offline preview"; $("#bsub").textContent = "live on GitHub Pages"; }
}
function showAgo() { if (lastRun) $("#bsub").textContent = `${lastRun.head_sha.slice(0, 7)} · ${ago(lastRun.updated_at)} ago`; }
async function loadResults() {
  try {
    RES = await (await fetch("results.json?" + Date.now())).json();
    $("#r1").textContent = `${RES.synthetic.correct}/${RES.synthetic.total} shapes right`;
    $("#r2").textContent = `${RES.health.cells_detected_smear} cells counted`;
  } catch { /* keep placeholders */ }
}

/* ---------- preloader: bar counter driven by real image loading ---------- */
class Preloader {
  constructor(done) {
    this.done = done; this.overlay = $("#preloader-overlay");
    Object.assign(this.overlay.style, { position: "fixed", inset: "0", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", zIndex: 100000 });
    if (matchMedia("(prefers-reduced-motion:reduce)").matches) return setTimeout(() => this.finish(), 300);
    this.counter = new BarCounter(this.overlay);
    this.label = Object.assign(document.createElement("p"), { className: "pre-label" }); this.overlay.appendChild(this.label);
    const urls = [...new Set(TILES.map((t) => `assets/${t.src}.jpg`))]; let loaded = 0;
    urls.forEach((u) => { const im = new Image(); im.onload = im.onerror = () => loaded++; im.src = u; });
    setTimeout(() => (loaded = urls.length), 9000);             // never hang on a slow connection
    let state = 0, ending = false; this.counter.show(0, true);
    const timer = setInterval(() => {
      const pct = Math.min(1, loaded / urls.length), digit = state - 2, target = pct >= 1 ? 9 : Math.min(8, Math.floor(pct * 9));
      if (state < 1 || digit < target) state++;
      else if (pct >= 1 && digit >= 9 && !ending) { ending = true; state = 12; setTimeout(() => { clearInterval(timer); this.finish(); }, 500); }
      this.counter.show(state); this.label.textContent = `Loading the pipeline · ${String(Math.round(pct * 100)).padStart(3, "0")}%`;
    }, 230);
  }
  finish() { gsap.to(this.overlay, { opacity: 0, duration: .8, ease: "power2.out", onComplete: () => { this.overlay.remove(); this.done(); } }); }
}

/* ---------- gallery ---------- */
class Gallery {
  constructor() {
    this.viewport = $("#viewport"); this.wrap = $("#canvasWrapper"); this.grid = $("#gridContainer");
    this.split = $("#splitScreenContainer"); this.titleBox = $("#imageTitleOverlay"); this.closeBtn = $("#closeButton"); this.controls = $("#controlsContainer");
    this.ease = CustomEase.create("smooth", ".87,0,.13,1"); this.centerEase = CustomEase.create("center", ".25,.46,.45,.94");
    this.cfg = { size: 320, rows: 4, cols: 8, zoom: .6, gap: 32 };
    this.zs = { active: false, item: null, overlay: null, flip: null };
    this.items = []; this.dim = {}; this.last = { x: 0, y: 0 }; this.drag = null; this.io = null;
  }
  gapFor(z) { return z >= 1 ? 16 : z >= .6 ? 32 : 64; }
  calcDim(gap = this.cfg.gap) {
    const w = this.cfg.cols * (this.cfg.size + gap) - gap, h = this.cfg.rows * (this.cfg.size + gap) - gap;
    return (this.dim = { width: w, height: h, sw: w * this.cfg.zoom, sh: h * this.cfg.zoom });
  }
  build() {
    this.cfg.gap = this.gapFor(this.cfg.zoom); this.calcDim();
    this.wrap.style.width = this.dim.width + "px"; this.wrap.style.height = this.dim.height + "px";
    this.grid.innerHTML = ""; this.items = [];
    for (let r = 0; r < this.cfg.rows; r++) for (let c = 0; c < this.cfg.cols; c++) {
      const i = this.items.length, tile = TILES[i % TILES.length], el = document.createElement("div");
      el.className = "grid-item"; el.tabIndex = 0; el.setAttribute("role", "button"); el.setAttribute("aria-label", `${tile.tag}: ${tile.title}`);
      const x = c * (this.cfg.size + this.cfg.gap), y = r * (this.cfg.size + this.cfg.gap);
      Object.assign(el.style, { left: x + "px", top: y + "px", opacity: "0" });
      const img = new Image(); img.src = `assets/${tile.src}.jpg`; img.alt = `${tile.tag} - ${tile.title}`; el.appendChild(img);
      const tag = document.createElement("span"); tag.className = "tile-tag"; tag.textContent = `${String(i % TILES.length + 1).padStart(2, "0")} ${tile.tag}`; el.appendChild(tag);
      const data = { el, img, row: r, col: c, baseX: x, baseY: y, index: i % TILES.length };
      const open = () => { if (!this.zs.active) this.enterZoom(data); };
      el.addEventListener("click", open); el.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(); } });
      this.grid.appendChild(el); this.items.push(data);
    }
  }
  observe() {
    this.io?.disconnect();
    this.io = new IntersectionObserver((es) => es.forEach((e) => {
      if (this.zs.item && e.target === this.zs.item.el) return;
      gsap.to(e.target, { opacity: e.isIntersecting ? 1 : .1, duration: .6, ease: "power2.out" });
    }), { threshold: .15, rootMargin: "10%" });
    this.items.forEach((i) => this.io.observe(i.el));
  }
  splitLines(el, text) {
    el.innerHTML = ""; const w = el.offsetWidth || 400, tmp = document.createElement("div");
    tmp.style.cssText = `position:absolute;visibility:hidden;width:auto;white-space:nowrap;font:300 16px/1.4 PPNeueMontreal,'Helvetica Neue',Arial,sans-serif`;
    document.body.appendChild(tmp); const lines = []; let cur = "";
    text.split(" ").forEach((word) => { const test = cur ? cur + " " + word : word; tmp.textContent = test; if (tmp.offsetWidth > w && cur) { lines.push(cur); cur = word; } else cur = test; });
    if (cur) lines.push(cur); tmp.remove();
    lines.forEach((l) => { const s = document.createElement("span"); s.className = "description-line"; s.textContent = l; el.appendChild(s); });
    return el.querySelectorAll(".description-line");
  }
  fillOverlay(i) {
    const t = TILES[i];
    $("#imageSlideNumber span").textContent = `${String(i + 1).padStart(2, "0")} / ${TILES.length} — ${t.tag}`;
    $("#imageSlideTitle h1").textContent = t.title; $("#imageSlideCode").textContent = t.code;
    this.lines = this.splitLines($("#imageSlideDescription"), fill(t.desc));
  }
  enterZoom(d) {
    if (this.zs.active) return; this.zs.active = true; this.zs.item = d;
    this.drag?.disable(); document.body.classList.add("zoom-mode");
    this.split.classList.add("active"); gsap.to(this.split, { opacity: 1, duration: 1.2, ease: this.ease });
    const src = d.img.getBoundingClientRect(), ov = document.createElement("div"); ov.className = "scaling-image-overlay";
    const im = new Image(); im.src = d.img.src; im.alt = d.img.alt; ov.appendChild(im); document.body.appendChild(ov);
    gsap.set(ov, { left: src.left, top: src.top, width: src.width, height: src.height }); this.zs.overlay = ov; gsap.set(d.img, { opacity: 0 });
    this.zs.flip = Flip.fit(ov, $("#zoomTarget"), { duration: 1.2, ease: this.ease, absolute: true, onComplete: () => {
      this.fillOverlay(d.index);
      gsap.set("#imageSlideNumber span", { y: 20, opacity: 0 }); gsap.set("#imageSlideTitle h1", { y: 60, opacity: 0 });
      gsap.set(this.lines, { y: 80, opacity: 0 }); gsap.set("#imageSlideCode", { y: 20, opacity: 0 });
      gsap.to(this.titleBox, { opacity: 1, duration: .3 });
      gsap.to("#imageSlideNumber span", { duration: .8, y: 0, opacity: 1, ease: this.ease, delay: .1 });
      gsap.to("#imageSlideTitle h1", { duration: .8, y: 0, opacity: 1, ease: this.ease, delay: .15 });
      gsap.to(this.lines, { duration: .8, y: 0, opacity: 1, ease: this.ease, delay: .2, stagger: .12 });
      gsap.to("#imageSlideCode", { duration: .8, y: 0, opacity: 1, ease: this.ease, delay: .45 });
    } });
    this.controls.classList.add("split-mode");
    gsap.fromTo(this.closeBtn, { x: 40, opacity: 0 }, { x: 0, opacity: 1, duration: .6, ease: "power2.out", delay: .9 }); this.closeBtn.classList.add("active");
  }
  exitZoom() {
    const z = this.zs; if (!z.active || !z.item || !z.overlay) return;
    z.flip?.kill(); const img = z.item.img, el = z.item.el;
    gsap.to(this.titleBox, { opacity: 0, duration: .3 });
    gsap.to(["#imageSlideNumber span", "#imageSlideTitle h1", "#imageSlideCode"], { duration: .4, y: -30, opacity: 0, ease: "power2.out" });
    if (this.lines) gsap.to(this.lines, { duration: .4, y: -60, opacity: 0, ease: "power2.out", stagger: -.05 });
    gsap.to(this.closeBtn, { duration: .3, opacity: 0, x: 40, ease: "power2.in" });
    this.split.classList.remove("active"); this.controls.classList.remove("split-mode"); gsap.to(this.split, { opacity: 0, duration: .8, ease: "power2.out" });
    Flip.fit(z.overlay, el, { duration: 1.2, ease: this.ease, absolute: true, onComplete: () => {
      gsap.set(img, { opacity: 1 }); z.overlay?.remove(); z.overlay = null;
      document.body.classList.remove("zoom-mode"); this.closeBtn.classList.remove("active"); this.drag?.enable();
      z.active = false; z.item = null; z.flip = null;
    } });
    gsap.to(z.overlay, { opacity: .4, duration: .8, ease: "power2.out" });
  }
  bounds() {
    const vw = innerWidth, vh = innerHeight, { sw, sh } = this.dim, m = this.cfg.gap * this.cfg.zoom;
    const ax = (lo, hi, v, s) => (s <= v ? [(v - s) / 2, (v - s) / 2] : [v - s - m, m]);
    const [minX, maxX] = ax(0, 0, vw, sw), [minY, maxY] = ax(0, 0, vh, sh); return { minX, maxX, minY, maxY };
  }
  initDrag() {
    this.drag?.kill(); this.calcDim(this.cfg.gap);
    this.drag = Draggable.create(this.wrap, {
      type: "x,y", bounds: this.bounds(), edgeResistance: .8, inertia: !!window.InertiaPlugin,
      onDragStart: () => { document.body.classList.add("dragging"); this.last = { x: this.drag.x, y: this.drag.y }; },
      onDrag: () => { this.last = { x: this.drag.x, y: this.drag.y }; },
      onDragEnd: () => document.body.classList.remove("dragging")
    })[0];
  }
  mouseLeave() {
    if (!document.body.classList.contains("dragging")) return;
    document.body.classList.remove("dragging"); gsap.to(this.wrap, { duration: .6, x: this.last.x, y: this.last.y, ease: "power2.out" }); this.drag?.endDrag();
  }
  fitZoom() {
    const g = this.gapFor(1), gw = this.cfg.cols * (this.cfg.size + g) - g, gh = this.cfg.rows * (this.cfg.size + g) - g;
    return Math.max(.1, Math.min(2, Math.min((innerWidth - 80) / gw, (innerHeight - 160) / gh)));
  }
  intro() {
    const cs = new DOMMatrix(getComputedStyle(this.wrap).transform), cx = (innerWidth / 2 - cs.m41) / cs.a - this.cfg.size / 2, cy = (innerHeight / 2 - cs.m42) / cs.a - this.cfg.size / 2;
    this.items.forEach((it, i) => gsap.set(it.el, { left: cx, top: cy, scale: .8, zIndex: this.items.length - i, opacity: 0 }));
    gsap.to(this.items.map((i) => i.el), { duration: .3, left: (i) => this.items[i].baseX, top: (i) => this.items[i].baseY, scale: 1, opacity: 1, ease: "power2.out",
      stagger: { amount: 1.2, from: "start", grid: [this.cfg.rows, this.cfg.cols] },
      onComplete: () => {
        this.items.forEach((it) => gsap.set(it.el, { zIndex: 1 }));
        const pi = this.controls.querySelector(".percentage-indicator"), sw = this.controls.querySelector(".switch");
        gsap.set(this.controls, { opacity: 0 }); gsap.set(pi, { x: "-3em" }); gsap.set(sw, { y: "2em" });
        gsap.timeline().to(this.controls, { opacity: 1, duration: .5 }, 0).to(pi, { x: 0, duration: .2 }, .25).to(sw, { y: 0, duration: .2 }, .3);
        this.controls.classList.add("visible");
      } });
  }
  mark(z) { $$(".switch-button").forEach((b) => b.classList.toggle("switch-button-current", b.dataset.zoom === String(z))); }
  setZoom(z, key = z) {
    if (this.zs.active) return this.exitZoom();
    const newGap = this.gapFor(z), old = this.cfg.zoom, vw = innerWidth, vh = innerHeight; this.cfg.zoom = z; this.calcDim(this.cfg.gap);
    gsap.to(this.wrap, { duration: .6, x: (vw - this.dim.width * old) / 2, y: (vh - this.dim.height * old) / 2, ease: this.centerEase, onComplete: () => {
      if (newGap !== this.cfg.gap) {
        this.items.forEach((it) => { it.baseX = it.col * (this.cfg.size + newGap); it.baseY = it.row * (this.cfg.size + newGap); gsap.to(it.el, { duration: 1.1, left: it.baseX, top: it.baseY, ease: this.ease }); });
        gsap.to(this.wrap, { duration: 1.1, width: this.cfg.cols * (this.cfg.size + newGap) - newGap, height: this.cfg.rows * (this.cfg.size + newGap) - newGap, ease: this.ease });
        this.cfg.gap = newGap;
      }
      this.calcDim(newGap); const fx = (vw - this.dim.width * z) / 2, fy = (vh - this.dim.height * z) / 2;
      gsap.to(this.wrap, { duration: 1.2, scale: z, x: fx, y: fy, ease: this.ease, onComplete: () => { this.last = { x: fx, y: fy }; this.initDrag(); } });
    } });
    $("#percentageIndicator").textContent = Math.round(z * 100) + "%"; this.mark(key);
  }
  reset() {
    if (this.zs.active) return; this.calcDim(this.cfg.gap);
    const x = (innerWidth - this.dim.sw) / 2, y = (innerHeight - this.dim.sh) / 2;
    gsap.to(this.wrap, { duration: 1, x, y, ease: this.centerEase, onComplete: () => { this.last = { x, y }; this.initDrag(); } });
  }
  init() {
    this.build(); gsap.set(this.viewport, { opacity: 0 }); gsap.set(this.wrap, { scale: this.cfg.zoom }); this.calcDim();
    const x = (innerWidth - this.dim.sw) / 2, y = (innerHeight - this.dim.sh) / 2; gsap.set(this.wrap, { x, y }); this.last = { x, y };
    this.events();
    gsap.to(this.viewport, { duration: .6, opacity: 1, ease: "power2.inOut", onComplete: () => {
      this.intro();
      gsap.to(".header", { duration: 1.2, opacity: 1, delay: .8 }); gsap.to(".footer", { duration: 1.4, opacity: 1, delay: 1 });
      setTimeout(() => { this.initDrag(); this.observe(); }, 1500);
    } });
  }
  events() {
    let rt; addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(() => this.reset(), 150); });
    document.addEventListener("mouseleave", () => this.mouseLeave());
    $$(".switch-button").forEach((b) => b.addEventListener("click", () => { const z = b.dataset.zoom; z === "fit" ? this.setZoom(this.fitZoom(), "fit") : this.setZoom(+z); }));
    this.closeBtn.addEventListener("click", () => this.exitZoom());
    ["#splitLeft", "#splitRight"].forEach((s) => $(s).addEventListener("click", () => this.exitZoom()));
    document.addEventListener("keydown", (e) => {
      if (this.zs.active) { if (e.key === "Escape") this.exitZoom(); return; }
      if (e.key === "1") this.setZoom(.3); else if (e.key === "2") this.setZoom(.6); else if (e.key === "3") this.setZoom(1);
      else if (e.key === "f" || e.key === "F") this.setZoom(this.fitZoom(), "fit");
    });
  }
}

let gallery;
document.addEventListener("DOMContentLoaded", () => {
  loadResults(); pollCI(); setInterval(pollCI, 30000); setInterval(loadResults, 60000); setInterval(showAgo, 15000);
  new Preloader(() => { gallery = new Gallery(); gallery.init(); });
});
