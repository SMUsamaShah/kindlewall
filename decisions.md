# Architecture Decisions

## ADR-001 — No backend; pure static files
**Decision:** index.html + manifest.json + sw.js only. No build step, no bundler.
**Reason:** Single-user tool. Complexity budget better spent on image processing quality.
No server means nothing to maintain or pay for.

## ADR-002 — Colour sourceCanvas preserved until filter step
**Decision:** `sourceCanvas` always holds the full-colour cropped image. Greyscale
conversion happens in `applyFilter`, not at crop time.
**Reason:** Lets the user switch filters instantly without re-cropping. The 1072×1448
colour canvas costs ~6 MB RAM — acceptable.

## ADR-003 — GPU blur for unsharp mask
**Decision:** Use CSS `filter: blur(Npx)` on an offscreen canvas rather than a JS
convolution kernel.
**Reason:** GPU-accelerated, simpler code, no allocation of kernel arrays. Produces
visually identical results for our radius sizes (1.5px fine, 5px/25px clarity).

## ADR-004 — Web Share Target for input; Web Share API for output
**Decision:** Receive images via Android share sheet (Web Share Target); send
processed file via `navigator.share()` back to Android share sheet.
**Reason:** No SSH from browser (browser TCP sandbox). X-Plore accepts shared files
and handles the SSH transfer — keeps the app single-purpose.

## ADR-005 — Shared images always route through crop
**Decision:** When an image arrives via the share target, always show the crop
screen first, ignoring the Auto Fit / Manual Crop tab state.
**Reason:** The user has no control over framing when sharing from another app
(gallery, browser). Forcing crop prevents a common failure mode: the image fills
the whole screen but the interesting part is off-centre.

## ADR-006 — Crop: no resize (Manual mode)
**Decision:** `setData({ width: W, height: H })` sets crop box to exactly
1072×1448 natural pixels. Confirm uses `getData(true)` + `drawImage` at 1:1.
`getCroppedCanvas()` is not used (it always resizes).
**Reason:** Any resize introduces resampling blur. E-ink at 300 PPI shows this.
If the source image ≥ 1072×1448 px, output is a pure pixel copy. If smaller,
user is warned; upscaling is then unavoidable.

## ADR-007 — SCREEN_LUT: level stretch + gentle S, not sigmoid
**Decision:** Level stretch (black in 20, white in 230) + k=4 sigmoid blended 60/40
with linear. Previous k=8 full sigmoid was replaced after pixel analysis.
**Reason:** Pixel analysis of 5 original Kindle screensaver images showed mid-grey
(64–191) holds 26–40% of pixels — texture lives there. k=8 sigmoid crushes midtones
symmetrically, which destroys texture. Level stretch clips the extremes (matching the
real images' hard black/white clips) without touching the mid range. See failures.md.

## ADR-008 — Screen R/G/B share the same SCREEN_PIPELINE object
**Decision:** `SCREEN_PIPELINE` const spread into each Screen variant.
**Reason:** Single source of truth for clarity pass radii and unsharp amount.
Changing one value updates all four Screen variants.
