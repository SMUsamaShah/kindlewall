# Kindle Screensaver Reference Analysis

> **Purpose.** A complete, self-contained characterisation of the original Kindle
> Paperwhite screensaver images so the look can be replicated **without the source
> images**. Every target number a replicated image must hit is recorded here, plus the
> canonical target histogram as raw data for histogram matching.
>
> **Scope note (set reduced to 4 images).** Originally five images (the "Bruce Ashley"
> 2011 set). `fountain_pens.jpg` was removed from the corpus because it is an aesthetic
> outlier — see §0.1 for the data behind that call and what its removal changed. The
> figures below are computed on the **remaining four**: letterpress type, pen nibs,
> pencils, typewriter keys.
>
> Measurements produced by `analysis/analyze.py`, `analysis/endpoints.py`, and
> `analysis/grain_and_target.py`. Raw output in `analysis/metrics.json` and
> `analysis/target_hist.json`.

---

## 0. TL;DR — the signature in one paragraph

These are **mathematically perfect 8-bit greyscale** images (R=G=B exactly) with a
**bathtub-shaped histogram**: ~32% of pixels are crushed into the near-black floor
(0–15), ~13% are blown into the near-white ceiling (240–255), and the **entire midtone
between them is strikingly flat** (~3–4% per 16-level bin, 32–223). About **14.5% of
pixels are *exactly* 0** and **5.9% are *exactly* 255**. The global standard deviation is
**~90** — roughly double a normal photograph (~50) — and edge gradients hit a
**p99 of ~167–217 regardless of subject matter**, a fingerprint of strong, uniform
sharpening. Contrast is present **at every spatial scale** (multi-scale local-contrast /
"clarity"), and the fine grain **decorrelates within 1–2 pixels**. The recipe that
reproduces this is: aggressive multi-radius local-contrast enhancement → a level-stretch +
gentle-S tone curve that clips both endpoints → strong final edge sharpening.

### 0.1 Why fountain_pens was removed, and what changed

`fountain_pens.jpg` was dropped on the observation that it has a "paint-like," more
posterised look than the others. The data **partly** supports that:

| Claim about fountain_pens | Verdict | Evidence |
|---------------------------|---------|----------|
| "More binary / either black or white" | ✗ **Not supported** | Its midtone (64–191) was 33.5% — *more* than three of the other four. The genuinely most-bimodal image is **pen_nibs** (25.9% midtone). |
| "Paint-like / smooth tonal regions" | ✓ **Supported** | Highest grain correlation (lag-1 = 0.77 vs 0.42–0.63 for the rest) and lowest fine-texture-to-structure ratio — its tones stay smooth across pixels instead of breaking into grain. The marbled-resin barrels read as smooth high-contrast swirls. |
| "Blown to white" | ✓ **Supported** | Highest pure-white clip at 13.1% (vs 3.5–10.2% for the rest). |

So it was removed as the **paint-like / blown-white** outlier, not the bimodal one.

**Effect of removal on the targets** (5-image → 4-image):
- **White end pulled down** (the main change): canonical pure-white **7.3% → 5.9%**;
  near-white **14.4% → 13.1%**; per-image white-clip *max* **13.1% → 10.2%**.
- **Black end and midtone barely move**: pure-black 15.2% → 14.5%; midtone 32.4% → 32.2%
  — confirming fountain_pens was not what made the set bimodal.
- **Global std essentially unchanged** (91.2 → 90.1); **median 86.6 → 82.0**.

Net: the 4-image target is **slightly more black-dominant and less white-heavy**. This
*strengthens* the case for the raised white point in the curve (see §10) — there is even
less pure white to reproduce now.

---

## 1. Source material

| Property | Value |
|----------|-------|
| Count | 4 images (was 5; fountain_pens removed — §0.1) |
| Stored dimensions | 900 × 1200 px (portrait), JPEG |
| Stored mode | RGB container, but **R=G=B in every pixel** |
| Subjects | letterpress type, pen nibs, pencils, typewriter keys |
| Common treatment | High-contrast B&W, heavy local contrast, crushed blacks, blown whites, pronounced texture |

The Kindle Paperwhite renders at 1072 × 1448 (≈ 0.74 aspect, same as 900 × 1200). The
processing characterised here is **resolution-independent** — a tone + texture treatment,
not tied to the capture size.

---

## 2. Methodology & one critical caveat

All statistics are computed on the **8-bit greyscale value**. Because the sources are
already grey, the greyscale value equals any single channel.

### ⚠ Luminance rounding hides the white clip

If you measure the histogram using **BT.709 luminance** (`0.2126R + 0.7152G + 0.0722B`)
of an *already-grey* image, a blown highlight stored as `(255,255,250)` computes to
luminance **254.6**, not 255 — so a naive luminance histogram reports **0.0% pure white**
even though the green/grey channel shows several percent at exactly 255.

**Consequence for measurement:** state highlight-clip targets on the **single grey
channel**, never on weighted luminance, or you will understate the white mass and
mis-tune the white point.

**Consequence for the app pipeline:** this does not affect KindleWall's output, because
the pipeline converts to a single grey value *first* and then applies the tone step to
that value. The caveat only matters when *analysing* grey images.

---

## 3. Colour / greyscale findings

| Image | Max channel deviation | Mean channel deviation | % pixels chromatic (Δ>2) |
|-------|----------------------:|-----------------------:|-------------------------:|
| letterpress_type | 0 | 0.000 | 0.0% |
| pen_nibs | 0 | 0.000 | 0.0% |
| pencils | 0 | 0.000 | 0.0% |
| typewriter_keys | 0 | 0.000 | 0.0% |

**Finding.** Perfectly neutral — R, G and B are bit-identical. No toning, no split-tone,
no residual cast. Any greyscale conversion reproduces the source exactly. The choice of
channel mixer in KindleWall therefore only matters for *colour input*; it has no bearing
on matching these references.

---

## 4. The canonical histogram (the centrepiece)

Average of the four normalised histograms. This **is** the target distribution — match an
arbitrary image to this and you have the core of the look.

### 4.1 Shape (16-bin, each bin = 16 grey levels)

```
   0- 15  32.1% |########################################
  16- 31   4.0% |#####
  32- 47   4.2% |#####
  48- 63   4.3% |#####
  64- 79   4.4% |#####
  80- 95   4.4% |#####
  96-111   4.3% |#####
 112-127   4.2% |#####
 128-143   4.0% |#####
 144-159   3.8% |#####
 160-175   3.6% |####
 176-191   3.5% |####
 192-207   3.3% |####
 208-223   3.3% |####
 224-239   3.5% |####
 240-255  13.1% |################
```

The two towers at the ends with a flat plateau between them is the **bathtub**. The
midtone is nearly uniform across 16–223, which is what aggressive local contrast does: it
flattens the global histogram while maximising *local* differences. Compared with the
5-image version the white tower is shorter (13.1% vs 14.4%) while the black tower and the
plateau are essentially unchanged.

### 4.2 Fine zone masses (canonical, 4-image)

| Zone | Mass | Role |
|------|-----:|------|
| **0 (pure black)** | **14.5%** | hard floor — deep shadow, clipped |
| 1–15 | 17.6% | near-black falloff |
| 16–31 | 4.0% | |
| 32–63 | 8.5% | deep shadow |
| 64–95 | 8.8% | lower midtone — **texture lives here** |
| 96–127 | 8.5% | mid |
| 128–159 | 7.8% | upper mid |
| 160–191 | 7.1% | |
| 192–223 | 6.6% | highlight shoulder |
| 224–239 | 3.5% | |
| 240–254 | 7.2% | near-white |
| **255 (pure white)** | **5.9%** | hard ceiling — specular highlight, clipped |

Roughly: **~36% black-ish (0–31)**, **~17% white-ish (224–255)**, **~47% spread evenly
across the middle**. The midtone is *not* depopulated — crushing it (e.g. a steep k=8
sigmoid) is the classic mistake and is wrong for this set (see failures.md).

### 4.3 Percentile ladder (canonical CDF, 4-image)

| Percentile | Grey value |
|-----------:|-----------:|
| p1 | 0 |
| p5 | 0 |
| p10 | 0 |
| p20 | 1 |
| p30 | 9 |
| p40 | 46 |
| p50 (median) | 83 |
| p60 | 120 |
| p70 | 161 |
| p80 | 207 |
| p90 | 249 |
| p95 | 255 |
| p99 | 255 |

Sixty percent of the pixels traverse almost the entire tonal range (**p20=1 → p80=207**).
That steepness *is* the contrast.

---

## 5. Global tonal statistics (per image)

| Image | Mean | Median | Std | Skew | Kurtosis |
|-------|-----:|-------:|----:|-----:|---------:|
| letterpress_type | 117.9 | 118 | 96.6 | 0.05 | −1.58 |
| pen_nibs | 83.8 | 41 | 93.9 | 0.68 | −1.08 |
| pencils | 124.0 | 118 | 87.8 | 0.13 | −1.33 |
| typewriter_keys | 76.0 | 51 | 82.1 | 0.83 | −0.54 |
| **range** | **76–124** | **41–118** | **82–97** | **0.05–0.83** | **−1.58…−0.54** |

**Readings.**
- **Std 82–97.** The single most diagnostic global number. Ordinary photographs sit at
  40–60. Anything below ~80 here is under-processed.
- **Negative kurtosis (−1.6 to −0.5).** Platykurtic — flatter than Gaussian, mass pushed
  to the tails. Consistent with the bathtub.
- **Skew 0.05–0.83, always ≥ 0.** Slight-to-moderate right skew: the black floor is the
  dominant mass; subject brightness sets how far right the bulk sits. Subjects on dark
  backgrounds (typewriter keys, pen nibs) skew most.
- **Mean is subject-dependent (76–124); the *shape* is not.** Don't target a fixed mean —
  target the **bathtub shape and the std**, and let the subject place the centre.

---

## 6. Endpoint clipping (measured on the grey channel)

| Image | =255 | ≥250 | ≥245 | ≥240 | =0 | ≤5 | ≤15 |
|-------|-----:|-----:|-----:|-----:|----:|----:|----:|
| letterpress_type | 3.5% | 8.8% | 12.5% | 15.4% | 14.5% | 26.3% | 28.5% |
| pen_nibs | 6.2% | 9.9% | 11.2% | 12.1% | 9.1% | 41.8% | 45.4% |
| pencils | 10.2% | 15.2% | 16.7% | 17.7% | 3.5% | 8.0% | 16.3% |
| typewriter_keys | 3.6% | 5.8% | 6.6% | 7.1% | 31.0% | 34.9% | 38.2% |
| **range** | **3.5–10%** | **5.8–15%** | **6.6–17%** | **7.1–18%** | **3.5–31%** | **8–42%** | **16–45%** |

**Findings.**
- **Both endpoints are genuinely clipped**, **not symmetrically**. Black clipping is
  heavier and more variable (3.5–31% at exactly 0) than white (3.5–10% at exactly 255).
- The black floor is driven by **subject and lighting** (dark backgrounds between densely
  packed objects under directional light), not purely by the curve. typewriter_keys has a
  huge black background → 31% pure black; pencils fills the frame → only 3.5%.
- The white clip is **specular** — blown metal/varnish — and more consistent because it
  comes from the curve's shoulder rather than the scene. With fountain_pens gone, the
  white-clip ceiling dropped from 13.1% to 10.2%.
- **Implication:** clip moderately to guarantee a true-black floor and true-white ceiling
  exist, then let local contrast and subject matter supply the rest of the black mass.

---

## 7. Local contrast / "clarity" — multi-scale

Mean local standard deviation, in square windows of increasing size:

| Image | w=3 | w=7 | w=15 | w=31 | w=63 |
|-------|----:|----:|-----:|-----:|-----:|
| letterpress_type | 16.7 | 27.1 | 42.0 | 62.0 | 80.7 |
| pen_nibs | 22.1 | 33.9 | 49.6 | 69.7 | 86.4 |
| pencils | 33.4 | 46.5 | 54.7 | 63.7 | 74.4 |
| typewriter_keys | 14.7 | 24.9 | 35.3 | 47.2 | 59.7 |

**Findings.**
- Local std **rises monotonically with window size** and stays high even at small windows.
  Contrast exists at **every scale** — fine grain (w3 ≈ 15–33), texture (w15 ≈ 35–55),
  large structure (w63 ≈ 60–86).
- This is the **direct justification for multiple clarity radii**. A single sharpening
  radius cannot produce energy at all these scales. The KindleWall recipe uses two
  (25 px macro + 5 px micro); the w31/w63 columns would collapse without the macro pass.
- **pencils** is the outlier: highest fine-scale contrast (w3=33) but *lowest* large-scale
  (w63=74) — uniformly textured wood grain with no large flat regions, which also explains
  its low pure-black mass.

---

## 8. Sharpening & grain fingerprint

### 8.1 Edge gradient (Sobel magnitude)

| Image | mean | p90 | p99 | % strong edge (>40) | % flat (<5) |
|-------|-----:|----:|----:|--------------------:|------------:|
| letterpress_type | 29.9 | 68.0 | 210.8 | 24.0% | 28.9% |
| pen_nibs | 38.8 | 108.1 | 213.0 | 37.2% | 42.4% |
| pencils | 61.1 | 136.1 | 217.1 | 58.2% | 17.3% |
| typewriter_keys | 29.9 | 79.9 | 166.7 | 28.7% | 37.0% |

**Findings.**
- **p99 clusters at 211–217** for three of four images (typewriter_keys lower at 167
  because so much of its frame is flat black, which dilutes the percentile). This tight
  clustering of the *strong-edge ceiling* across different subjects is the signature of
  **a uniform sharpening operation** — edges are pushed to a consistent acutance ceiling.
- The **bimodal split** (high "% strong edge" *and* high "% flat") is the unsharp-mask
  fingerprint: edges aggressively enhanced while flat regions stay flat. A global contrast
  curve alone would not produce this.

### 8.2 Grain correlation length

High-pass residual autocorrelation, horizontal lag:

| Image | lag1 | lag2 | lag3 | half-width (<0.5) |
|-------|-----:|-----:|-----:|------------------:|
| letterpress_type | +0.60 | +0.26 | +0.16 | 2 px |
| pen_nibs | +0.42 | −0.04 | −0.07 | 1 px |
| pencils | +0.48 | −0.09 | −0.26 | 1 px |
| typewriter_keys | +0.63 | +0.11 | −0.10 | 2 px |

**Finding.** Grain **decorrelates within 1–2 pixels**; pen_nibs and pencils show *negative*
correlation at lag 2–3 — the overshoot/undershoot ring of unsharp masking. The texture is
**fine and crisp**, not soft film grain. Consistent with a small-radius final sharpen
(≈1–1.5 px) on top of the larger clarity passes. (fountain_pens, now removed, had the
smoothest texture of the set at lag-1 = 0.77 — part of why it read as "painterly".)

---

## 9. Frequency content

Radial power spectrum, energy by frequency band (fraction of Nyquist):

| Image | low (0–10%) | mid (10–40%) | high (40–100%) |
|-------|------------:|-------------:|---------------:|
| letterpress_type | 95.3% | 4.5% | 0.2% |
| pen_nibs | 90.8% | 8.6% | 0.5% |
| pencils | 95.8% | 3.3% | 1.0% |
| typewriter_keys | 96.6% | 3.1% | 0.3% |

**Finding.** As with any natural image, most energy is low-frequency. The diagnostic part
is the **high-frequency tail at 0.2–1.0%**, *elevated* relative to an unsharpened photo
(typically <0.1%). pencils, the most textured subject, has the most high-freq energy
(1.0%) and the highest fine-scale local std — internally consistent, and corroborates the
sharpening from an independent measure.

---

## 10. Replication recipe

Mapping each finding to a concrete, ordered processing step. Operate on a single grey
channel throughout.

1. **Greyscale conversion** *(only matters for colour input)*
   The references are already neutral (§3); any sensible conversion works. Luminosity
   `0.2126R + 0.7152G + 0.0722B` is the safe default; a channel mixer is a creative knob,
   not a matching requirement.

2. **Multi-scale local contrast (clarity) — BEFORE the tone curve** *(§7, §8)*
   Two or more unsharp passes at different radii. Current working values:
   - macro: radius ≈ 25 px, amount ≈ 0.5 → builds the w31/w63 structure contrast
   - micro: radius ≈ 5 px, amount ≈ 0.4 → builds the w7/w15 texture
   These flatten the global histogram toward the bathtub plateau while raising local std
   at every scale. This step does the heavy lifting; the tone curve only finishes it.

3. **Tone: level-stretch + gentle S, clip both ends** *(§4, §6)*
   - Black point: input ≤ ~20 → 0. Guarantees a true-black floor.
   - White point: input ≥ ~245 → 255. The 4-image references clip only **~6% to pure
     white** (down from ~7% with fountain_pens), so a conservative white point near 245 is
     correct — a 230 white point overproduces white.
   - Between the clips: gentle S (sigmoid k≈4) blended ~60/40 with linear. Adds snap
     **without** depopulating the midtone — the §4.1 plateau must stay flat. Do **not** use
     a steep sigmoid (k≈8); it crushes the texture-rich 64–191 band (~32% of pixels).
   - Let the **black mass come mostly from the scene** (§6); a moderate clip plus the macro
     clarity pass deepening real shadows reproduces the 3.5–31% spread naturally.

4. **Final edge sharpen** *(§8)*
   Small radius (≈1–1.5 px), strong amount (≈1.0). Pushes edge gradients to the
   p99 ≈ 200–217 ceiling and produces the 1–2 px grain correlation with slight overshoot.
   Unsharp mask keeps flat regions flat, preserving the high-strong-edge / high-flat split.

**Optional — exact histogram match.** Skip hand-tuning the curve in step 3 and instead
**histogram-match** the post-clarity image to the canonical target in §12. Clarity (step 2)
+ histogram match to §12 + sharpen (step 4) lands on the look mechanically. The hand-tuned
curve is cheaper and good enough for a live preview; histogram matching is the "perfect"
path. (KindleWall ships both as a Curve / Match toggle.)

---

## 11. Validation targets (4-image)

A successfully replicated image should land inside these ranges (measured on the final
grey output):

| Metric | Target range | Ideal |
|--------|-------------|-------|
| Global std | 82 – 97 | ~90 |
| Skewness | 0.0 – 0.85 (always ≥ 0) | subject-dependent |
| Kurtosis | −1.6 – −0.5 (negative) | ~−1.1 |
| % pure black (=0) | 3.5 – 31% | ~14.5% (subject-driven) |
| % near-black (≤15) | 16 – 45% | ~32% |
| % pure white (=255) | 3.5 – 10% | ~6% |
| % near-white (≥240) | 7 – 18% | ~13% |
| % midtone (64–191) | 26 – 41% | ~32% (must NOT be crushed) |
| Gradient p99 | 167 – 217 | ~202 |
| Gradient mean | 30 – 61 | ~40 |
| % strong edge (>40) | 24 – 58% | ~37% |
| Local std (w15) | 35 – 55 | ~45 |
| Grain half-width | 1 – 2 px | ~1.5 px |
| High-freq energy (40–100%) | 0.2 – 1.0% | ~0.5% |

If global std comes in under ~80, the image is under-processed (more clarity/curve). If
the midtone band (64–191) drops under ~26%, the curve is too steep and crushing texture —
back off the sigmoid k. If gradient p99 is under ~165, the final sharpen is too weak.

---

## 12. Canonical target histogram (raw data, for histogram matching)

256-bin normalised target distribution (average of the **four** references), expressed as
**parts-per-100000** per grey level, row-major in groups of 16. Sum ≈ 100000. Use this to
histogram-match an arbitrary image to the Kindle look **without the originals**. This is
the exact array embedded as `TARGET_PMF` in `index.html`.

```
# value range: parts-per-100000 at each of the 16 levels in the row
#   0- 15: 14508, 9165, 1378, 1057, 877, 763, 694, 626, 558, 488, 441, 374, 334, 307, 284, 268
#  16- 31:   259,  255,  250,  247, 253, 248, 247, 246, 244, 251, 250, 252, 256, 253, 260, 253
#  32- 47:   259,  257,  259,  260, 259, 259, 261, 263, 261, 262, 261, 261, 264, 263, 266, 268
#  48- 63:   267,  265,  268,  266, 270, 270, 268, 270, 269, 275, 271, 274, 275, 271, 273, 270
#  64- 79:   275,  271,  274,  275, 277, 274, 274, 274, 277, 276, 275, 273, 277, 274, 277, 277
#  80- 95:   280,  274,  275,  273, 274, 276, 277, 273, 270, 268, 276, 272, 271, 272, 272, 275
#  96-111:   272,  267,  272,  271, 270, 273, 268, 270, 266, 270, 265, 265, 267, 262, 267, 265
# 112-127:   264,  267,  265,  257, 263, 261, 257, 260, 258, 261, 260, 259, 257, 260, 260, 257
# 128-143:   259,  255,  253,  254, 247, 251, 252, 251, 250, 245, 250, 249, 248, 246, 252, 245
# 144-159:   241,  241,  239,  246, 244, 239, 239, 241, 238, 239, 236, 235, 239, 235, 234, 235
# 160-175:   234,  229,  227,  228, 230, 229, 229, 227, 226, 227, 227, 224, 225, 224, 225, 223
# 176-191:   220,  222,  216,  218, 216, 217, 218, 216, 217, 216, 216, 217, 218, 214, 214, 208
# 192-207:   210,  209,  218,  214, 210, 209, 211, 213, 211, 206, 205, 210, 206, 209, 204, 204
# 208-223:   208,  210,  206,  206, 205, 205, 203, 204, 206, 204, 204, 208, 201, 205, 208, 209
# 224-239:   208,  205,  208,  207, 208, 208, 212, 209, 217, 217, 222, 223, 226, 228, 235, 236
# 240-255:   243,  250,  262,  273, 287, 299, 325, 362, 406, 456, 526, 609, 726, 895, 1285, 5873
```

Full-precision arrays (`target_256`, per-image histograms, every metric above) are in
`analysis/target_hist.json` and `analysis/metrics.json`.

### Histogram-matching sketch

```
target_cdf  = cumsum(target_256)               # from the data above
source_cdf  = cumsum(histogram(source_grey))   # the clarity-processed image
# For each grey level v in source, find t such that target_cdf[t] ≈ source_cdf[v]
lut[v] = argmin_t | target_cdf[t] - source_cdf[v] |
output = lut[source_grey]
```

Apply *after* the clarity passes and *before* (or instead of) the hand-tuned curve, then
finish with the final sharpen. Because both CDFs are monotonic this is an O(256)
single-pass build. Endpoint clipping (~14.5% black, ~6% white) falls out for free.
**Limitation:** discrete levels can't be split, so a spiky input (e.g. already-blown
highlights) may slightly overshoot an over-full level — inherent to monotonic LUT matching.

---

## 13. Per-subject notes

- **letterpress_type** — most symmetric histogram (skew 0.05), most platykurtic
  (kurt −1.58); wood texture gives an even midtone. Good general exemplar of the flat
  plateau.
- **pen_nibs** — the genuinely most *bimodal* image (lowest midtone, 25.9%) with the
  deepest near-black tail (42% ≤5) — dark background, bright metal nibs. High dynamic
  separation.
- **pencils** — fills the frame, so lowest pure-black (3.5%); most uniformly sharpened
  (58% strong edges, highest fine-scale local std, most high-freq energy). The "texture
  everywhere" extreme.
- **typewriter_keys** — most pure black (31%) from the large dark background; lowest white
  clip and lowest gradient p99 (the flat background dilutes edge percentiles). The "subject
  on black" extreme.

The two extremes (pencils ↔ typewriter_keys) bracket the black-mass range and confirm that
**black quantity is scene-driven**, while the **shape, std, and sharpening ceiling are the
invariant treatment**.

*(Removed: fountain_pens — highest white clip and smoothest, most painterly texture of the
original five; see §0.1.)*
