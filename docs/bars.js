/* Bar counter: 24 bars slide around to form 0-9 (idea + motion data from a CSS if()/@function demo,
   driven by JS so it works in every browser).  States: 0 = stacked, 1 = single column, 2..11 = digits 0..9, 12 = column again.
   Per bar, one char per state:  c = stacked at centre, 0 = home, m = move one slot (right for cols 1-2, left for col 3),
   d = move two slots (toward the far side), L = one slot left. */
const BAR_STATES = ["cmmmmm00m0mmm","c00000m000000","cmmmmm00m0mmm","cm0000000d00m","c0m0mmmLLmmm0","cm0m000d0000m","cm0mdd000d00m","c0m0mmmLLmmm0","cm0m000dd000m","cm0mdm0m0mmmm","c0m0m0m000000","cm0m0m00mmm0m","cm0mmdmd0m0dm","c0m00m0mL0mm0","cm0mm0000m00m","cm0m0ddd0m0dm","c0m0Lmmmm0mm0","cm0md0000m00m","cm0m00d00m00m","c0m0Lmmmm0mm0","cm0md0000m00m","cmm00mdmmmmmm","c00000m000000","cmm00m0mmmmmm"];
class BarCounter {
  constructor(parent, { step = 0.34, ease = "cubic-bezier(.65,0,.35,1)", delayScale = 0.5 } = {}) {
    this.el = document.createElement("div"); this.el.className = "bars"; this.el.setAttribute("aria-hidden", "true");
    this.bars = BAR_STATES.map((_, i) => {
      const s = document.createElement("span"), n = i + 1; let d = 0;       // stagger copied from the original
      if (n % 2 === 1) d = 123; if (n % 2 === 1 && n >= 3) d = 222; if ((n - 1) % 5 === 0) d = 69; if ((n - 2) % 3 === 0) d = 99;
      s.dataset.delay = d * delayScale; this.el.appendChild(s); return s;
    });
    this.step = step; this.ease = ease; parent.appendChild(this.el);
  }
  show(state, instant = false) {
    this.bars.forEach((s, i) => {
      const col = i % 3, row = (i / 3) | 0, ch = BAR_STATES[i][state];
      const slots = { 0: 0, L: -1, m: col === 2 ? -1 : 1, d: col === 0 ? 2 : col === 1 ? 0 : -2, c: col === 1 ? 0 : col === 0 ? 1 : -1 }[ch];
      const y = ch === "c" ? `calc(${3 - row} * (var(--h) + var(--gap)) + var(--h) / 2)` : "0px";
      s.style.transition = instant ? "none" : `transform ${this.step}s ${s.dataset.delay}ms ${this.ease}`;
      s.style.transform = `translate(calc(var(--pitch) * ${slots}), ${y})`;
    });
  }
}
