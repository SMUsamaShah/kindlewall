# Kindle Wallpaper PWA — Specifications

## Purpose
Convert any image to a Kindle Paperwhite wallpaper (resize + greyscale filter),
then send directly to X-Plore (or any app) via Android share sheet.

## Target Device
- **Model**: Kindle Paperwhite 10th Generation (PQ94WIF)
- **Resolution**: 1072 × 1448 px
- **Display**: 6", greyscale e-ink

## Output
- **Dimensions**: 1072 × 1448 px
- **Format**: PNG
- **Colour**: Greyscale, filter-dependent (see below)

## Crop Modes

### Auto Fit
Scale image to cover 1072×1448 (whichever axis needs more scaling), then
centre-crop the overflow. Both resize and crop happen automatically.

### Manual Crop
Cropper.js overlay with aspect ratio locked to 1072:1448. User drags and pinches
to select the region. `getCroppedCanvas({ width: W, height: H })` extracts and
scales the crop to output dimensions. Source colour data is preserved until filter
step — no greyscale applied yet.

## Greyscale Filters

All filters operate per-pixel on the full-colour source canvas via `fn(r,g,b) → 0–255`.
Some filters use multi-stage pipelines (see Screen).

| Filter    | Technique |
|-----------|-----------|
| Natural   | Standard luminosity: `0.2126R + 0.7152G + 0.0722B` |
| Vivid     | Luminosity → full S-curve (darkens shadows, brightens highlights) |
| Deep      | Luminosity → clip input below 25, stretch remainder to 0–255 |
| Bright    | Luminosity → gamma 0.65 (lifts shadows without blowing highlights) |
| Portrait  | Green-heavy channel mix + compressed output range (20–235) |
| Landscape | Red-heavy channel mix (0.55R 0.33G 0.12B) → dramatic skies |
| Kindle    | Luminosity → strong S-curve (strength 1.5) → level stretch → unsharp mask |
| Screen    | See below |

### Screen filter — based on pixel analysis of 5 original Kindle screensaver images

Measured histogram of Bruce Ashley's 2011 Amazon screensaver photography:

| Zone | Range | % of pixels | Notes |
|------|-------|-------------|-------|
| Pure black | 0–15 | 28–45% | Deep inter-object shadows + dark backgrounds |
| Deep shadow | 16–63 | 9–16% | |
| Mid-grey | 64–191 | 26–40% | **Texture lives here — NOT crushed** |
| Highlight | 192–239 | 6–17% | |
| Pure white | 240–255 | 7–20% | Hard-clipped metallic highlights |

Local contrast: 57–76% of pixels have local_std > 40 (11px window). Gradient p90 = 77–112.

**Key finding:** The huge black regions come from subject matter and lighting, not from a sigmoid
crushing midtones. Initial k=8 sigmoid was wrong — it depopulated midtones that the real
images preserve. See [failures.md](failures.md).

**Pipeline:** `toGrey → clarity 25px → clarity 5px → level LUT → sharpen 1.5px`

- **Clarity 25px (0.5):** Macro-level local contrast — exaggerates shadows between objects
- **Clarity 5px (0.4):** Fine texture pop — grain, scratches, metal pitting
- **Level LUT:** Black point 20→0, white point 230→255, gentle S-curve (k=4) blended 60/40 with linear to add snap without crushing texture
- **Sharpen 1.5px (1.0):** Hard edge sharpening matched to measured gradient values

### Unsharp mask (shared utility)
Uses GPU-accelerated CSS `blur(Npx)` on an offscreen canvas, then:
`sharpened = pixel + amount × (pixel − blurred)` applied per-pixel.
Used for both clarity passes (large radius) and final sharpening (small radius).

### clarityPasses (filter property)
Array of `{radius, amount}` objects run sequentially before the LUT.
Replaces old single `clarity: {}` property. applyFilter supports both for compatibility.

## Filter Thumbnails
On entering the filter step, source canvas is scaled to 36×49 px once.
Each filter's `fn` (or `toGrey + lut`) is applied to that thumbnail — gives live previews of all
8 filters instantly before touching the full 1072×1448 canvas.
Clarity passes are skipped in thumbnails (too small to matter).

## Share Flows

### Receive (Web Share Target API)
1. POST multipart/form-data to `./share-target` (field: `image`)
2. `sw.js` writes blob to `kw-pending-v1` cache at `/pending-image`
3. SW redirects to `<origin><basepath>?shared=1` (303)
4. Page detects `shared=1`, awaits `serviceWorker.ready`, reads + deletes blob

### Send (Web Share API)
- "Send to Kindle" → `navigator.share({ files: [png] })` → Android share sheet
- User picks X-Plore (or any SSH/file app) to transfer to Kindle
- Falls back to download if `navigator.canShare` is unavailable

## Offline Support
`sw.js` precaches the app shell and Cropper.js CDN files on install.
Cache-first strategy for all GET requests. App works fully offline after first load.

## File Structure
| File | Role |
|---|---|
| `index.html` | App shell, all CSS, all JS |
| `manifest.json` | PWA manifest; declares `share_target` |
| `sw.js` | Service worker; share target handler + precache + offline |
| `icon.svg` | App icon |
| `specifications.md` | This file |
| `failures.md` | [Things that didn't work](failures.md) |

## Hosting
- **HTTPS required** for PWA install, Web Share Target, Web Share API
- Deployed at: https://xosh.org/kindlewall/
- GitHub repo: https://github.com/SMUsamaShah/kindlewall

## Install (one-time)
1. Open https://xosh.org/kindlewall/ in Chrome on Android
2. ⋮ → Add to Home Screen
3. App appears in Android share sheet and home screen
