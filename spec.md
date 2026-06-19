# KindleWall — Spec

## Purpose
Convert any image to a Kindle Paperwhite 10th gen screensaver:
**1072×1448 px, greyscale JPEG**.

---

## Architecture
Single-file PWA — no build step, no backend.

| File | Role |
|------|------|
| `index.html` | Entire app: shell, CSS, JS |
| `sw.js` | Service worker — share POST handler + caching |
| `manifest.json` | PWA manifest, declares Web Share Target |

---

## User flow

```
[Drop/Pick image] → [Auto Fit OR Manual Crop] → [Channel + Adjustments] → [Send/Download]
```

**Section: drop** — drag-drop or file picker, Auto Fit / Manual Crop tab.

**Section: crop** — Manual Crop only. Cropper.js with fixed, non-resizable 1072×1448 box.
`getData(true)` → drawImage at natural pixels (zero resize when source ≥ target).

**Section: filter** — Channel strip (Lum/R/G/B thumbnails) + adjustment sliders + Send/Download.

---

## Image pipeline

```
Blob → [crop/autofit] → sourceCanvas (colour, 1072×1448)
  → applyFilter()     (full pipeline — channel + clarity + LUT + sharpen)
  → filteredImageData (grey snapshot)
  → applyAdjustments() (fast post-pass — brightness / contrast / noise)
  → workCanvas → JPEG blob → preview
```

`sourceCanvas` stays colour (ADR-002) so channel switching re-runs cheaply.

---

## Two-tier pipeline

**applyFilter()** — full pipeline, runs on: channel change, filter change, sharpness change (150 ms debounce).
1. `toGrey(r,g,b)` — greyscale conversion (from CHANNELS, keyed by `adjustments.channel`)
2. Clarity passes (only if the selected filter defines `clarity`): unsharp at the filter's radii
3. Tone — the selected filter's LUT, or histogram match if the filter sets `match: true`
4. Glow (only if the filter defines `glow`): highlight halation bloom (Infrared)
5. Fine unsharp 1.5 px — amount = `sharpness/100`
6. Snapshot grey result → `filteredImageData`
7. Calls `applyAdjustments()`

**applyAdjustments()** — fast post-pass (single pixel loop), runs on: brightness/contrast/noise change.
Reads `filteredImageData`, writes adjusted pixels to `workCanvas`, encodes JPEG blob.

---

## Channel selector

Universal greyscale basis (`adjustments.channel`, default `lum`), shown as a 4-thumbnail
strip (Lum / R / G / B). Thumbnails show the **raw** greyscale (no tone curve) so the
comparison is about colour→grey mixing only; on an already-grey image all four look
identical. Only relevant for colour input.

---

## Filters

The look (`adjustments.filter`, default `kindle`), shown as a thumbnail strip. Each filter
is a complete B&W treatment applied after greyscale. Most are a pure tone curve built into
a 256-entry LUT once at load; a few carry extra spatial work:

| Filter | Tone | Extra | Notes |
|--------|------|-------|-------|
| Kindle | SCREEN_LUT (level-stretch + gentle-S, white 245) | clarity (25/5 px) | the screensaver look |
| K-Match | histogram-match to canonical target | clarity (25/5 px) | forces the exact bathtub |
| Neutral | identity | — | plain greyscale |
| Hi-Con | steep S (k=6) | — | punchy |
| Soft | low-contrast S, mild | — | gentle, full range |
| Noir | crushed blacks + strong S | — | dramatic |
| Hi-Key | gamma-lift + raised floor | — | bright, airy |
| Lo-Key | gamma 1.9 | — | dark, moody |
| Matte | lifted black floor + capped white | — | faded film look |
| Silver | deep endpoints + smooth S | — | darkroom silver-gelatin |
| Tri-X | S + lifted toe (base fog) | grain 22 | punchy, midtone separation |
| HP5 | flatter, long toe, soft shoulder | grain 14 | gentle, shadow detail |
| Lith | hard crushed shadows + creamy highlights | grain 30 | "charcoal" |
| Bleach | high-contrast + deep blacks | clarity (8 px) + grain 18 | bleach bypass |
| Solar | partial highlight inversion | — | Sabattier (non-monotonic) |
| Infrared | bright midtones + crushed shadow | glow + grain 15 | halation |

Non-Kindle curves are grounded in real film/darkroom characteristics (see ADR-016).
Selecting a filter sets the Noise slider to that filter's `grain` default (film grain;
0 for non-grain filters). Filter thumbnails apply greyscale(channel) + the filter LUT;
clarity/glow are skipped at thumb size, histogram-match runs on the thumb histogram.

---

## Adjustment sliders

| Slider | Range | Default | Tier | Notes |
|--------|-------|---------|------|-------|
| Brightness | −100 to +100 | 0 | fast | Pixel offset |
| Contrast | −100 to +100 | 0 | fast | factor=(100+c)/100; 0→flat grey, 2→double |
| Sharpness | 0–200 (= 0×–2×) | 100 | full | Scales final 1.5 px unsharp only |
| Noise | 0–50 | 0 | fast | ±noise per pixel, re-randomised each call |

---

## Share flow

**Receive** — Android share → POST multipart → SW stores blob in `kw-pending-v1` cache →
redirect `?shared=1` → page reads blob, routes to Manual Crop (ADR-005).

**Send** — `navigator.share({ files })` → Android share sheet → X-Plore SSH to Kindle.
Falls back to `<a download>` if Web Share API absent.

---

## Service worker

- CDN (Cropper.js): cache-first (versioned URL)
- Own-origin: network-first, caches as offline fallback
- `skipWaiting()` + `clients.claim()` on install/activate (ADR-009)
