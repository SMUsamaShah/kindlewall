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

## ADR-009 — Network-first for own-origin; cache-first for CDN
**Decision:** `sw.js` fetch handler uses network-first for `self.location.hostname`
files, cache-first only for CDN (Cropper.js).
**Reason:** Cache-first for own-origin meant pushing a new `index.html` to GitHub
had no effect on installed PWA users. The browser only reinstalls the SW when
`sw.js` changes byte-for-byte; if only `index.html` changed, the old cached copy
was served indefinitely. CDN resources use versioned URLs and never change, so
cache-first is safe and faster there.

## ADR-010: Replace Screen R/G/B filter variants with a channel selector

**Context**: Had four FILTERS entries (Screen, Screen R, Screen G, Screen B) that were identical
except for `toGrey`. This caused duplication and a growing filter strip for what is conceptually
one knob.

**Decision**: Collapse to a single `CHANNELS` array with four entries (Lum/R/G/B). The channel
strip re-uses the same `.filter-item` thumbnail UI. A single `SCREEN_PIPELINE` const holds the
shared config. `adjustments.channel` drives `toGrey` selection at pipeline run-time.

**Consequence**: The `FILTERS` array and `currentFilter` state are removed. Filter section now
has no "which filter am I on" state — there is only one pipeline.

---

## ADR-011: Two-tier pipeline (applyFilter / applyAdjustments)

**Context**: Brightness, contrast, and noise are per-pixel arithmetic — sub-millisecond on a
full 1072×1448 image. Clarity passes (async GPU blur) and the LUT are more expensive.
Sharpness scales the final unsharp, so it requires re-running the last step of applyFilter.

**Decision**: Split into two functions:
- `applyFilter()` — full pipeline (greyscale → clarity → LUT → sharpen). Triggered by channel
  and sharpness changes (sharpness debounced 150 ms). Stores result as `filteredImageData`.
- `applyAdjustments()` — fast post-pass (brightness/contrast/noise). Reads `filteredImageData`,
  writes to workCanvas, encodes blob. Triggered directly by B/C/N slider input events.

Clarity passes are NOT scaled by the Sharpness slider — they control local contrast/structure
and their amounts are part of the Screen filter's identity, not a user tuning knob.

**blobGen guard**: rapid slider moves queue multiple `toBlob()` calls. A monotonically
increasing `blobGen` counter ensures only the latest callback updates `outputBlob` and the
preview. Stale callbacks return early.

---

## ADR-012: Noise re-randomised per applyAdjustments call

**Context**: The noise field adds `±noise` random per-pixel. Because `applyAdjustments()` calls
`Math.random()` inline, moving *any* fast slider (brightness, contrast) after setting noise will
re-roll the grain pattern.

**Decision**: Accept this for now. The alternative — a pre-generated static noise canvas blended
at a variable opacity — would fix the pattern drift but adds a canvas allocation and a blend pass.
Noise is a cosmetic option; pattern drift on slider drag is tolerable.

**Revisit if**: users find the shifting grain distracting when tuning brightness/contrast.
