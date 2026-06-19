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

**applyFilter()** — full pipeline, runs on: channel change, sharpness change (150 ms debounce).
1. `toGrey(r,g,b)` — greyscale conversion (from CHANNELS, keyed by `adjustments.channel`)
2. Clarity passes: unsharp at 25 px (macro) then 5 px (micro) — fixed amounts
3. SCREEN_LUT — level stretch (black<20→0, white>230→255) + k=4 S-curve, 60/40 blend
4. Fine unsharp 1.5 px — amount = `SCREEN_PIPELINE.unsharpAmount × (sharpness/100)`
5. Snapshot grey result → `filteredImageData`
6. Calls `applyAdjustments()`

**applyAdjustments()** — fast post-pass (single pixel loop), runs on: brightness/contrast/noise change.
Reads `filteredImageData`, writes adjusted pixels to `workCanvas`, encodes JPEG blob.

---

## Channel selector

Replaces the old Screen / Screen R / Screen G / Screen B filter variants.
Identical pipeline, only the greyscale conversion differs:

| Channel | fn(r,g,b) |
|---------|-----------|
| Lum | 0.2126r + 0.7152g + 0.0722b |
| R | r |
| G | g |
| B | b |

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
