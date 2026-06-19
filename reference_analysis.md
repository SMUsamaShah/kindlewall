# Kindle Screensaver Reference Analysis

> **Purpose.** A complete, self-contained characterisation of the five original
> Kindle Paperwhite screensaver images (the "Bruce Ashley" 2011 set: fountain pens,
> letterpress type, pen nibs, pencils, typewriter keys). Once you've read this, you
> should be able to replicate the look **without the original images**. Every target
> number a replicated image must hit is recorded here, plus the canonical target
> histogram as raw data for histogram matching.
>
> Measurements produced by `analysis/analyze.py`, `analysis/endpoints.py`, and
> `analysis/grain_and_target.py`. Raw output in `analysis/metrics.json` and
> `analysis/target_hist.json`.

---

## 0. TL;DR — the signature in one paragraph

These are **mathematically perfect 8-bit greyscale** images (R=G=B exactly) with a
**bathtub-shaped histogram**: ~31% of pixels are crushed into the near-black floor
(0–15), ~14% are blown into the near-white ceiling (240–255), and the **entire midtone
between them is strikingly flat** (~2.5 per-mille per level, 64–191). About **15% of
pixels are *exactly* 0** and **7% are *exactly* 255**. The global standard deviation is
**~91** — roughly double a normal photograph (~50) — and edge gradients hit a
**p99 of ~205–218 regardless of subject matter**, a fingerprint of strong, uniform
sharpening. Contrast is present **at every spatial scale** (multi-scale local-contrast /
"clarity"), and the fine grain **decorrelates within 1–2 pixels**. The recipe that
reproduces this is: aggressive multi-radius local-contrast enhancement → a level-stretch +
gentle-S tone curve that clips both endpoints hard → strong final edge sharpening.

---

## 1. Source material

| Property | Value |
|----------|-------|
| Count | 5 images |
| Stored dimensions | 900 × 1200 px (portrait), JPEG |
| Stored mode | RGB container, but **R=G=B in every pixel** |
| Subjects | fountain pens, letterpress type, pen nibs, pencils, typewriter keys |
| Common treatment | High-contrast B&W, heavy local contrast, crushed blacks, blown whites, pronounced texture |

The Kindle Paperwhite renders at 1072 × 1448 (a 4:3 ≈ 0.74 aspect, same as 900 × 1200).
The processing characterised here is **resolution-independent** — it's a tone + texture
treatment, not tied to the capture size.

---

## 2. Methodology & one critical caveat

All statistics are computed on the **8-bit greyscale value**. Because the sources are
already grey, the greyscale value equals any single channel.

### ⚠ Luminance rounding hides the white clip

If you measure the histogram using **BT.709 luminance** (`0.2126R + 0.7152G + 0.0722B`)
of an *already-grey* image, a blown highlight stored as `(255,255,250)` computes to
luminance **254.6**, not 255 — so a naive luminance histogram reports **0.0% pure white**
even though the green/grey channel shows **3.5–13%** at exactly 255.

**Consequence for measurement:** state highlight-clip targets on the **single grey
channel**, never on weighted luminance, or you will understate the white mass and
mis-tune the white point.

**Consequence for the app pipeline:** this does not affect KindleWall's output, because
the pipeline converts to a single grey value *first* and then applies the LUT to that
value. The caveat only matters when *analysing* grey images or comparing histograms.

(This corrects the earlier `spec.md` zone note, which was measured inconsistently and
overstated both endpoints.)

---

## 3. Colour / greyscale findings

| Image | Max channel deviation | Mean channel deviation | % pixels chromatic (Δ>2) |
|-------|----------------------:|-----------------------:|-------------------------:|
| fountain_pens | 0 | 0.000 | 0.0% |
| letterpress_type | 0 | 0.000 | 0.0% |
| pen_nibs | 0 | 0.000 | 0.0% |
| pencils | 0 | 0.000 | 0.0% |
| typewriter_keys | 0 | 0.000 | 0.0% |

**Finding.** Perfectly neutral. There is **no toning, no split-tone, no residual colour
cast** — R, G and B are bit-identical. Any greyscale conversion (luminosity, single
channel, or average) reproduces the source exactly, because the colour was already
discarded upstream. The choice of channel mixer in KindleWall therefore only matters for
*colour input* images; it has no bearing on matching these references.

---

## 4. The canonical histogram (the centrepiece)

Average of all five normalised histograms. This **is** the target distribution — match
an arbitrary image to this and you have the core of the look.

### 4.1 Shape (16-bin, each bin = 16 grey levels)

```
   0- 15  31.4% |########################################
  16- 31   4.1% |#####
  32- 47   4.1% |#####
  48- 63   4.2% |#####
  64- 79   4.2% |#####
  80- 95   4.3% |#####
  96-111   4.3% |#####
 112-127   4.7% |######
 128-143   4.5% |######
 144-159   3.8% |#####
 160-175   3.5% |####
 176-191   3.3% |####
 192-207   3.1% |####
 208-223   3.1% |####
 224-239   3.2% |####
 240-255  14.4% |##################
```

The two towers at the ends with a flat plateau between them is the **bathtub**. Read it
as: a large black mass, a moderate white mass, and a **deliberately equalised midtone** —
the histogram is nearly uniform across 16–223, which is exactly what aggressive
local-contrast (clarity) does: it flattens the global histogram while maximising *local*
differences.

### 4.2 Fine zone masses (canonical)

| Zone | Mass | Role |
|------|-----:|------|
| **0 (pure black)** | **15.2%** | hard floor — deep inter-object shadow, clipped |
| 1–15 | 16.3% | near-black falloff |
| 16–31 | 4.1% | |
| 32–63 | 8.3% | deep shadow |
| 64–95 | 8.5% | lower midtone — **texture lives here** |
| 96–127 | 9.0% | mid |
| 128–159 | 8.2% | upper mid |
| 160–191 | 6.7% | |
| 192–223 | 6.2% | highlight shoulder |
| 224–239 | 3.2% | |
| 240–254 | 7.1% | near-white |
| **255 (pure white)** | **7.3%** | hard ceiling — specular metal, clipped |

So roughly: **~31% black-ish**, **~14% white-ish**, **~55% spread evenly across the
middle**. The midtone is *not* depopulated — crushing the midtones (e.g. a steep k=8
sigmoid) is the classic mistake and is wrong for this set (see §9).

### 4.3 Percentile ladder (canonical CDF)

| Percentile | Grey value |
|-----------:|-----------:|
| p1 | 0 |
| p5 | 0 |
| p10 | 0 |
| p20 | 1 |
| p30 | 11 |
| p40 | 49 |
| p50 (median) | 87 |
| p60 | 124 |
| p70 | 162 |
| p80 | 211 |
| p90 | 252 |
| p95 | 255 |
| p99 | 255 |

Note how fast it climbs once it leaves the black floor: **p20=1 → p80=211**. Sixty
percent of the pixels traverse almost the entire tonal range. That steepness *is* the
contrast.

---

## 5. Global tonal statistics (per image)

| Image | Mean | Median | Std | Skew | Kurtosis |
|-------|-----:|-------:|----:|-----:|---------:|
| fountain_pens | 110.7 | 105 | 95.8 | 0.29 | — |
| letterpress_type | 117.9 | 118 | 96.6 | 0.05 | — |
| pen_nibs | 83.8 | 41 | 93.9 | 0.68 | — |
| pencils | 124.0 | 118 | 87.8 | 0.13 | — |
| typewriter_keys | 76.0 | 51 | 82.1 | 0.83 | — |
| **range** | **76–124** | **41–118** | **82–97** | **0.05–0.83** | **−1.58…−0.54** |

**Readings.**
- **Std 82–97.** This is the single most diagnostic global number. Ordinary photographs
  sit at 40–60. Anything below ~80 here is under-processed.
- **Negative kurtosis (−1.6 to −0.5).** Platykurtic — flatter than Gaussian, with mass
  pushed to the tails. Consistent with the bathtub, not a peaked midtone.
- **Skew 0.05–0.83, always ≥ 0.** Slight-to-moderate right skew: the black floor is the
  dominant mass; brightness of the subject sets how far right the bulk sits. Subjects on
  dark backgrounds (typewriter keys, pen nibs) skew most.
- **Mean is subject-dependent (76–124); the *shape* is not.** Don't target a fixed mean —
  target the **bathtub shape and the std**, and let the subject place the centre.

---

## 6. Endpoint clipping (measured on the grey channel)

| Image | =255 | ≥250 | ≥245 | ≥240 | =0 | ≤5 | ≤15 |
|-------|-----:|-----:|-----:|-----:|----:|----:|----:|
| fountain_pens | 13.1% | 17.8% | 19.2% | 19.9% | 17.7% | 24.7% | 28.6% |
| letterpress_type | 3.5% | 8.8% | 12.5% | 15.4% | 14.5% | 26.3% | 28.5% |
| pen_nibs | 6.2% | 9.9% | 11.2% | 12.1% | 9.1% | 41.8% | 45.4% |
| pencils | 10.2% | 15.2% | 16.7% | 17.7% | 3.5% | 8.0% | 16.3% |
| typewriter_keys | 3.6% | 5.8% | 6.6% | 7.1% | 31.0% | 34.9% | 38.2% |
| **range** | **3.5–13%** | **5.8–18%** | **6.6–19%** | **7.1–20%** | **3.5–31%** | **8–42%** | **16–45%** |

**Findings.**
- **Both endpoints are genuinely clipped**, but **not symmetrically**. Black clipping is
  heavier and more variable (3.5–31% at exactly 0) than white (3.5–13% at exactly 255).
- The black floor is driven by **subject and lighting** (dark backgrounds between densely
  packed objects under directional light), not purely by the curve. typewriter_keys has a
  huge black background → 31% pure black; pencils fills the frame edge-to-edge → only 3.5%.
- The white clip is **specular** — blown metal/varnish highlights — and is more consistent
  because it comes from the curve's shoulder rather than the scene.
- **Implication:** a fixed black-point clip that produces 31% black would be wrong for
  pencils and right for typewriter_keys. The clip should be **moderate and let subject
  matter supply the rest** — clip enough to guarantee a true-black floor and true-white
  ceiling exist, then rely on local contrast to deepen shadows where the scene is dark.

---

## 7. Local contrast / "clarity" — multi-scale

Mean local standard deviation, measured in square windows of increasing size:

| Image | w=3 | w=7 | w=15 | w=31 | w=63 |
|-------|----:|----:|-----:|-----:|-----:|
| fountain_pens | 18.3 | 35.1 | 53.9 | 71.3 | 85.4 |
| letterpress_type | 16.7 | 27.1 | 42.0 | 62.0 | 80.7 |
| pen_nibs | 22.1 | 33.9 | 49.6 | 69.7 | 86.4 |
| pencils | 33.4 | 46.5 | 54.7 | 63.7 | 74.4 |
| typewriter_keys | 14.7 | 24.9 | 35.3 | 47.2 | 59.7 |

**Findings.**
- Local std **rises monotonically with window size** and stays high even at small windows.
  Contrast exists at **every scale** — fine grain (w3 ≈ 15–33), texture (w15 ≈ 35–55), and
  large structure (w63 ≈ 60–86).
- This is the **direct justification for multiple clarity radii**. A single sharpening
  radius cannot produce energy at all these scales simultaneously. The current KindleWall
  recipe uses two (25 px macro + 5 px micro); the data suggests the macro pass is doing
  real, necessary work — the w31/w63 columns would collapse without it.
- **pencils** is the outlier: highest fine-scale contrast (w3=33) but *lowest* large-scale
  (w63=74). It's the most uniformly textured subject (sharpened wood grain everywhere, no
  large flat regions), which also explains its low pure-black mass.

---

## 8. Sharpening & grain fingerprint

### 8.1 Edge gradient (Sobel magnitude)

| Image | mean | p90 | p99 | % strong edge (>40) | % flat (<5) |
|-------|-----:|----:|----:|--------------------:|------------:|
| fountain_pens | 37.6 | 116.8 | 218.5 | 31.0% | 38.5% |
| letterpress_type | 29.9 | 68.0 | 210.8 | 24.0% | 28.9% |
| pen_nibs | 38.8 | 108.1 | 213.0 | 37.2% | 42.4% |
| pencils | 61.1 | 136.1 | 217.1 | 58.2% | 17.3% |
| typewriter_keys | 29.9 | 79.9 | 166.7 | 28.7% | 37.0% |

**Findings.**
- **p99 clusters at 205–218** across four of five images (typewriter_keys lower at 167
  because so much of its frame is flat black, which dilutes the percentile). This tight
  clustering of the *strong-edge ceiling* across wildly different subjects is the
  signature of **a uniform sharpening operation applied to all of them** — the edges are
  pushed to a consistent acutance ceiling.
- The **bimodal split** (high "% strong edge" *and* high "% flat") is the unsharp-mask
  fingerprint: edges are aggressively enhanced while flat regions stay flat. A global
  contrast curve alone would not produce this — it would lift flat-region gradients too.

### 8.2 Grain correlation length

High-pass residual autocorrelation, horizontal lag:

| Image | lag1 | lag2 | lag3 | half-width (<0.5) |
|-------|-----:|-----:|-----:|------------------:|
| fountain_pens | +0.77 | +0.44 | +0.20 | 2 px |
| letterpress_type | +0.60 | +0.26 | +0.16 | 2 px |
| pen_nibs | +0.42 | −0.04 | −0.07 | 1 px |
| pencils | +0.48 | −0.09 | −0.26 | 1 px |
| typewriter_keys | +0.63 | +0.11 | −0.10 | 2 px |

**Finding.** Grain **decorrelates within 1–2 pixels** and several images show *negative*
correlation at lag 2–3 (the tell-tale overshoot/undershoot ring of unsharp masking). The
texture is **fine and crisp**, not soft film grain. This is consistent with a small-radius
final sharpen (≈1–1.5 px) on top of the larger clarity passes.

---

## 9. Frequency content

Radial power spectrum, energy by frequency band (fraction of Nyquist):

| Image | low (0–10%) | mid (10–40%) | high (40–100%) |
|-------|------------:|-------------:|---------------:|
| fountain_pens | 90.9% | 8.4% | 0.7% |
| letterpress_type | 95.3% | 4.5% | 0.2% |
| pen_nibs | 90.8% | 8.6% | 0.5% |
| pencils | 95.8% | 3.3% | 1.0% |
| typewriter_keys | 96.6% | 3.1% | 0.3% |

**Finding.** As with any natural image, most energy is low-frequency. The diagnostic part
is the **high-frequency tail at 0.2–1.0%**, which is *elevated* relative to an unsharpened
photo (typically <0.1%). pencils, the most textured subject, has the most high-freq energy
(1.0%) and the highest fine-scale local std — internally consistent. This corroborates the
sharpening seen in §8 from an independent measure.

---

## 10. Replication recipe

Mapping each finding to a concrete, ordered processing step. Operate on a single grey
channel throughout.

1. **Greyscale conversion** *(only matters for colour input)*
   The references are already neutral (§3), so any sensible conversion works. Luminosity
   `0.2126R + 0.7152G + 0.0722B` is the safe default; a channel mixer is a creative knob,
   not a matching requirement.

2. **Multi-scale local contrast (clarity) — do this BEFORE the tone curve** *(§7, §8)*
   Two or more unsharp passes at different radii. Current working values:
   - macro: radius ≈ 25 px, amount ≈ 0.5 → builds the w31/w63 structure contrast
   - micro: radius ≈ 5 px, amount ≈ 0.4 → builds the w7/w15 texture
   These flatten the global histogram (toward the bathtub plateau) while raising local std
   at every scale. This is the step that does the heavy lifting; the tone curve only
   finishes it.

3. **Tone curve: level-stretch + gentle S, clip both ends** *(§4, §6)*
   - Black point: input ≤ ~20 → 0. Guarantees a true-black floor exists.
   - White point: input ≥ ~245 → 255. Guarantees a true-white ceiling. **Use ~245, not
     230** — the references clip ~7–13% to pure white, and a 230 white point tends to
     overproduce white (the §6 "≥240" column is only 7–20%, and *exactly 255* is just
     3.5–13%). 245 lands closer to target.
   - Between the clips: gentle S (sigmoid k≈4) blended ~60/40 with the linear ramp. This
     adds snap **without** depopulating the midtone — the §4.1 plateau must stay flat.
     Do **not** use a steep sigmoid (k≈8); it crushes the texture-rich 64–191 band that
     holds ~33% of the pixels.
   - Let the **black mass come mostly from the scene**, not the curve (§6). A moderate clip
     plus the macro clarity pass deepening real shadows reproduces the 3.5–31% spread
     naturally across different subjects, where a fixed aggressive clip would not.

4. **Final edge sharpen** *(§8)*
   Small radius (≈1–1.5 px), strong amount (≈1.0). Pushes edge gradients to the
   p99 ≈ 205–218 ceiling and produces the 1–2 px grain correlation with slight overshoot.
   Keep flat regions flat (unsharp mask does this inherently) to preserve the
   high-strong-edge / high-flat bimodality.

**Optional — exact histogram match.** For a near-exact tonal reproduction, skip hand-tuning
the curve in step 3 and instead **histogram-match** the post-clarity image to the canonical
target distribution in §12. Clarity (step 2) + histogram match to §12 + sharpen (step 4)
will land on the look mechanically. Hand-tuned curve is cheaper and good enough for a
preview pipeline; histogram matching is the "perfect" path.

---

## 11. Validation targets

A successfully replicated image should land inside these ranges (measured on the final
grey output):

| Metric | Target range | Ideal |
|--------|-------------|-------|
| Global std | 82 – 97 | ~91 |
| Skewness | 0.0 – 0.85 (always ≥ 0) | subject-dependent |
| Kurtosis | −1.6 – −0.5 (negative) | ~−1.2 |
| % pure black (=0) | 3.5 – 31% | ~15% (subject-driven) |
| % near-black (≤15) | 16 – 45% | ~31% |
| % pure white (=255) | 3.5 – 13% | ~7% |
| % near-white (≥240) | 7 – 20% | ~14% |
| % midtone (64–191) | 26 – 41% | ~32% (must NOT be crushed) |
| Gradient p99 | 167 – 218 | ~205 |
| Gradient mean | 30 – 61 | ~39 |
| % strong edge (>40) | 24 – 58% | ~36% |
| Local std (w15) | 35 – 55 | ~47 |
| Grain half-width | 1 – 2 px | ~1.5 px |
| High-freq energy (40–100%) | 0.2 – 1.0% | ~0.6% |

If global std comes in under ~80, the image is under-processed (more clarity/curve). If
the midtone band (64–191) drops under ~26%, the curve is too steep and is crushing texture
— back off the sigmoid k. If gradient p99 is under ~165, the final sharpen is too weak.

---

## 12. Canonical target histogram (raw data, for histogram matching)

256-bin normalised target distribution (average of the five references), expressed as
**per-mille** (‰, ×1000) per grey level, row-major in groups of 16. Sum ≈ 1000. Use this
to histogram-match an arbitrary image to the Kindle look **without the originals**.

```
# value range: per-mille mass at each of the 16 levels in the row
#   0- 15: 151.54, 78.17, 14.38, 10.92, 8.85, 7.62, 6.75, 5.99, 5.32, 4.68, 4.25, 3.65, 3.34, 3.10, 2.89, 2.73
#  16- 31:   2.67,  2.61,  2.56,  2.52, 2.58, 2.52, 2.52, 2.51, 2.47, 2.52, 2.50, 2.51, 2.54, 2.53, 2.58, 2.51
#  32- 47:   2.55,  2.54,  2.56,  2.56, 2.57, 2.54, 2.55, 2.57, 2.56, 2.54, 2.56, 2.55, 2.58, 2.57, 2.60, 2.62
#  48- 63:   2.60,  2.58,  2.60,  2.58, 2.60, 2.61, 2.59, 2.62, 2.60, 2.66, 2.64, 2.65, 2.65, 2.62, 2.62, 2.61
#  64- 79:   2.64,  2.59,  2.62,  2.64, 2.66, 2.64, 2.62, 2.62, 2.66, 2.66, 2.65, 2.64, 2.66, 2.64, 2.67, 2.68
#  80- 95:   2.70,  2.65,  2.66,  2.63, 2.67, 2.67, 2.68, 2.64, 2.62, 2.62, 2.68, 2.65, 2.64, 2.64, 2.66, 2.70
#  96-111:   2.67,  2.64,  2.66,  2.67, 2.67, 2.70, 2.65, 2.68, 2.64, 2.69, 2.65, 2.67, 2.69, 2.69, 2.72, 2.72
# 112-127:   2.75,  2.80,  2.78,  2.74, 2.82, 2.85, 2.82, 2.88, 2.86, 2.94, 2.99, 3.01, 3.06, 3.12, 3.19, 3.27
# 128-143:   3.51,  3.34,  3.15,  3.06, 2.88, 2.83, 2.78, 2.70, 2.67, 2.60, 2.61, 2.57, 2.54, 2.52, 2.54, 2.47
# 144-159:   2.42,  2.41,  2.38,  2.43, 2.39, 2.36, 2.36, 2.35, 2.34, 2.34, 2.30, 2.30, 2.33, 2.28, 2.28, 2.28
# 160-175:   2.27,  2.23,  2.21,  2.19, 2.20, 2.19, 2.19, 2.18, 2.16, 2.16, 2.17, 2.12, 2.12, 2.13, 2.14, 2.10
# 176-191:   2.10,  2.10,  2.05,  2.05, 2.06, 2.05, 2.06, 2.04, 2.06, 2.04, 2.03, 2.03, 2.04, 2.02, 2.00, 1.95
# 192-207:   1.99,  1.96,  2.03,  2.00, 1.97, 1.95, 1.95, 1.98, 1.94, 1.91, 1.89, 1.94, 1.91, 1.93, 1.88, 1.90
# 208-223:   1.93,  1.95,  1.92,  1.90, 1.91, 1.90, 1.89, 1.89, 1.89, 1.88, 1.90, 1.93, 1.87, 1.90, 1.92, 1.91
# 224-239:   1.92,  1.90,  1.92,  1.92, 1.91, 1.92, 1.95, 1.94, 2.01, 2.01, 2.04, 2.05, 2.07, 2.09, 2.13, 2.15
# 240-255:   2.22,  2.29,  2.40,  2.49, 2.65, 2.76, 3.05, 3.41, 3.88, 4.45, 5.28, 6.29, 7.59, 9.43, 13.14, 73.17
```

The full-precision arrays (`target_256`, plus per-image histograms and every metric above)
are persisted in `analysis/target_hist.json` and `analysis/metrics.json` should you want to
load them programmatically.

### Histogram-matching sketch

```
target_cdf  = cumsum(target_256)               # from the data above
source_cdf  = cumsum(histogram(source_grey))   # the clarity-processed image
# For each grey level v in source, find t such that target_cdf[t] ≈ source_cdf[v]
lut[v] = argmin_t | target_cdf[t] - source_cdf[v] |
output = lut[source_grey]
```

Apply this *after* the clarity passes and *before* (or instead of) the hand-tuned tone
curve, then finish with the final sharpen.

---

## 13. Per-subject notes

- **fountain_pens** — heaviest white clip (13% pure white) from glossy varnish/specular
  barrels; balanced black. Good general exemplar.
- **letterpress_type** — most symmetric histogram (skew 0.05), flattest tonal balance;
  wood texture gives even midtone.
- **pen_nibs** — most right-skewed *with* the deepest near-black tail (42% ≤5) — dark
  background, bright metal nibs. High dynamic separation.
- **pencils** — fills the frame, so lowest pure-black (3.5%); most uniformly sharpened
  (58% strong edges, highest fine-scale local std). The "texture everywhere" extreme.
- **typewriter_keys** — most pure black (31%) from the large dark background; lowest white
  clip and lowest gradient p99 (the flat background dilutes edge percentiles). The "subject
  on black" extreme.

The two extremes (pencils ↔ typewriter_keys) bracket the black-mass range and confirm that
**black quantity is scene-driven**, while the **shape, std, and sharpening ceiling are the
invariant treatment**.
