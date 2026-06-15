# Kindle Wallpaper PWA — Specifications

## Purpose
Single-purpose tool: convert any image to a Kindle Paperwhite wallpaper (resize + grayscale),
then send it directly to X-Plore (or any SSH/file app) via the Android share sheet.

## Target Device
- **Model**: Kindle Paperwhite 10th Generation (PQ94WIF)
- **Resolution**: 1072 × 1448 px
- **Display**: 6", grayscale e-ink

## Output
- **Dimensions**: 1072 × 1448 px
- **Colour**: Grayscale via `ctx.filter = 'grayscale(100%)'`
- **Format**: PNG
- **Crop**: Scale to cover, centre-crop

## Workflow

### Receive (Web Share Target API)
1. User shares any image from any Android app
2. Android POST multipart/form-data to `./share-target` (field: `image`)
3. `sw.js` intercepts POST, writes blob to Cache Storage (`kw-pending-v1` / `/pending-image`)
4. SW redirects to `<origin><basepath>?shared=1` (303)
5. `index.html` detects `shared=1`, awaits `serviceWorker.ready`, reads blob from cache
6. Deletes blob from cache, clears URL param, processes image

### Send (Web Share API)
- "Send to Kindle" button calls `navigator.share({ files: [processedPng] })`
- Opens Android share sheet → user picks X-Plore (or any SSH app)
- Falls back to download if `navigator.share` / `navigator.canShare` unavailable

## File Structure
| File | Role |
|---|---|
| `index.html` | App shell, all CSS, all JS |
| `manifest.json` | PWA manifest; declares `share_target` |
| `sw.js` | Service worker; handles share POST |
| `icon.svg` | App icon |
| `specifications.md` | This file |
| `failures.md` | [Things that didn't work](failures.md) |

## Hosting Requirements
- **HTTPS required** for PWA install, Web Share Target, and Web Share API
- Recommended: GitHub Pages or Netlify (both free)
- Sub-path hosting (e.g. GitHub Pages) handled dynamically in `sw.js`

## Install (One-time)
1. Open hosted URL in Chrome on Android
2. ⋮ → "Add to Home Screen"
3. App now appears in Android share sheet AND on home screen

## Constraints & Decisions
- No build step, no dependencies — pure static HTML/JS/JSON
- No crop UI in v1; centre-crop suits wallpapers well enough
- SSH directly from browser is impossible (TCP sandbox); Web Share API to X-Plore is the right model
- `grayscale(100%)` via canvas filter is sufficient; no manual curve adjustment
