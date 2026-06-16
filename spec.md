# Kindle Wallpaper — Spec

> Source of truth. Supersedes specifications.md.

## What it does
Single-purpose PWA: convert any image to a Kindle Paperwhite 10th gen wallpaper
(1072×1448 px, greyscale), then share to X-Plore or any SSH/file app.

## Target device
- Model: Kindle Paperwhite 10th gen (PQ94WIF)
- Screen: 1072×1448 px, 6", greyscale e-ink
- Hosted at: https://xosh.org/kindlewall/

## Files
| File | Role |
|------|------|
| index.html | Entire app — shell, CSS, JS |
| manifest.json | PWA manifest; declares share_target |
| sw.js | Service worker — share POST handler, offline cache |
| icon.svg | App icon |
| spec.md | This file |
| decisions.md | Architecture decisions |
| failures.md | Things tried that didn't work |

## Crop modes

### Auto Fit
Scale image to cover 1072×1448 (whichever axis needs more), centre-crop overflow.
Colour sourceCanvas filled → filter applied after.

### Manual Crop (no-resize)
Cropper.js crop box is set to exactly 1072×1448 natural image pixels via `setData`.
Box is non-resizable (`cropBoxResizable: false`).
User drags box to choose region; pinch-zooms image.
On confirm: `getData(true)` → `drawImage(img, x, y, W, H, 0, 0, W, H)`.
Pure 1:1 pixel extraction — zero resize, zero blur.
If source image < 1072×1448: warns user, some upscaling unavoidable.

## Filter pipeline
Filters are applied AFTER crop to the colour sourceCanvas.

### Standard filters (fn only)
`fn(r, g, b) → 0–255` greyscale value. Applied per-pixel to sourceCanvas.
Then optional unsharp mask.

### Screen filters (multi-stage)
`toGrey(r, g, b) → 0–255` → clarityPasses[] (unsharp at large radius) → LUT → unsharp.

| Filter | toGrey | Notes |
|--------|--------|-------|
| Screen | luminosity | Best all-round starting point |
| Screen R | red channel | Warms tones bright, blues/greens dark |
| Screen G | green channel | Closest to luminosity, smooth |
| Screen B | blue channel | Skies/cool highlights bright, warm tones dark |
| Natural | luminosity | No tone curve |
| Vivid | luminosity | S-curve |
| Deep | luminosity | Black point clip + stretch |
| Bright | luminosity | Gamma 0.65 |
| Portrait | green-heavy | Compressed range |
| Landscape | red-heavy | Infrared-ish |
| Kindle | luminosity | Strong S-curve + level + unsharp |

### SCREEN_LUT
Level stretch (black in 20→0, white in 230→255) + gentle S-curve (k=4, 60/40 blend
with linear) to preserve texture-rich mid-grey while clipping extremes.

Rationale: pixel analysis of 5 original Kindle screensaver images showed:
- 28–45% pure black (from deep shadows, NOT from tone curve)
- 26–40% mid-grey (texture — must not be crushed)
- 7–20% pure white (hard-clipped metallic highlights)
k=8 sigmoid was wrong (see failures.md).

### Unsharp mask
GPU blur (CSS `filter: blur(Npx)`) on offscreen canvas, then:
`pixel + amount × (pixel − blurred)` per pixel.
Used at two scales: large radius = clarity pass, small radius = edge sharpen.

## Share flows

### Receive (Web Share Target)
POST multipart/form-data to `./share-target` (field: `image`).
SW stores blob in `kw-pending-v1` cache, redirects to `?shared=1`.
Page reads blob, always routes through crop screen (framing unknown when shared).

### Send (Web Share API)
`navigator.share({ files: [png] })` → Android share sheet → X-Plore / SSH app.
Falls back to download if `canShare` unavailable.

## Install (one-time)
Open https://xosh.org/kindlewall/ in Chrome → ⋮ → Add to Home Screen.
App appears in Android share sheet.
