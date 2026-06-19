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

## ADR-013: White point 230 → 245 in SCREEN_LUT (curve mode)

**Context**: Analysis of the 5 reference images (reference_analysis.md §6) showed they clip
only ~7–13% of pixels to pure white, measured on the grey channel. The old WHITE_IN=230
overproduced white. (The earlier "7–20% pure white" figure in spec.md was measured on BT.709
luminance of an already-grey image, which rounds blown highlights just under 255 and understated
the true clip — see reference_analysis.md §2.)

**Decision**: Raise WHITE_IN to 245.

**Consequence (traced, not assumed)**: WHITE_IN is both the clip threshold and the denominator
of the midtone remap `t=(i-BLACK_IN)/(WHITE_IN-BLACK_IN)`, so the change does two coupled things:
- Highlight rescue: inputs 230–244 (15 levels) that were slammed flat to 255 now keep a 13-level
  gradient (242→254) — bright texture is preserved instead of clipped to a white blob.
- Midtone darkening: the wider denominator rescales the whole curve down ~8.7 levels on average
  (peak −14 around input 200). Intended — moves toward the references' heavier shadows / median ~87.

These cannot be separated in a single-curve design. Accepted the coupling; users who want lighter
output have the Brightness slider. Match mode (ADR-014) is unaffected — it bypasses this curve.

---

## ADR-014: Histogram-match tone mode

**Context**: The curve is a hand-tuned approximation. reference_analysis.md §12 provides the
canonical target distribution as data, enabling exact tonal reproduction via histogram matching.

**Decision**: Add a `tone` toggle (Curve / Match). Match builds a per-image LUT mapping each
source grey level to the target level with the nearest cumulative mass (TARGET_CDF, embedded as
TARGET_PMF). Runs after clarity, before the final sharpen — same pipeline slot as the curve LUT.

**Why both, not replace**: Curve is predictable and gentle (good default for a live preview);
Match is aggressive and exact but can look harsh on images that don't suit the bathtub (it forces
15% black + 7% white onto any input). Keeping both is one small toggle and ~30 lines; gives the
user the cheap path and the perfect path.

**Properties**: Endpoint clipping falls out for free (no BLACK_IN/WHITE_IN needed in this mode).
Monotonic CDFs → O(256) LUT build via single forward pointer, no per-pixel allocation. Verified
on uniform, real-reference, and flat-midtone gaussian inputs: all land within ~0.5% of every
target zone. Known limit: discrete levels can't be split, so spiky inputs may slightly overshoot
an over-full level.

## ADR-015: Remove fountain_pens.jpg from the reference corpus

**Context**: fountain_pens.jpg looked like an aesthetic outlier — more "paint-like" /
posterised than the other four screensavers.

**Decision**: Remove it from `original_kindle_screensavers/`. Recompute the canonical
target and all analysis figures on the remaining four (letterpress, pen nibs, pencils,
typewriter keys). Update reference_analysis.md and the embedded TARGET_PMF in index.html.

**What the data said** (recorded honestly, since the stated reason was only partly right):
- "More binary" — **not supported**. Its midtone (33.5%) was higher than three of the
  other four; pen_nibs (25.9%) is the genuinely most-bimodal image.
- "Paint-like / smooth regions" — **supported**. Highest grain correlation (lag-1 0.77 vs
  0.42–0.63) and lowest fine-texture-to-structure ratio.
- "Blown to white" — **supported**. Highest pure-white clip (13.1% vs 3.5–10.2%).

**Consequence**: The target shifted mostly at the **white end** — canonical pure-white
7.3%→5.9%, near-white 14.4%→13.1%, white-clip max 13.1%→10.2%. Black and midtone barely
moved (pure-black 15.2%→14.5%, midtone 32.4%→32.2%), confirming it was the blown-white
outlier, not the bimodal one. The Match tone mode (ADR-014) now targets a slightly more
black-dominant distribution. Strengthens the ADR-013 raised-white-point rationale — even
less pure white to reproduce.

## ADR-016: Add a filter set (14 B&W looks) + fold tone toggle into it

**Context**: The app had only the Kindle screensaver treatment (Curve/Match toggle).
Not every wallpaper wants the aggressive Kindle look; a palette of general B&W looks is
useful. Requested: at least 10 non-Kindle B&W filters, researched from real references.

**Decision**: Introduce a `FILTERS` array — each entry a complete look. Two Kindle entries
(Kindle = SCREEN_LUT + clarity; K-Match = histogram match + clarity) plus 14 B&W tonal
treatments. The Curve/Match toggle (ADR-014) is removed; those two are now just the first
two filter entries. Channel selector (ADR-010) stays as a separate universal greyscale
basis. UI: two thumbnail strips (Channel = raw greyscale, Filter = toned), labelled.

**Filter model (kept minimal)**: most filters are a pure tone curve compiled to a 256-LUT
once at load via three helpers (scurve / levels / band). Optional per-filter fields add
spatial work only where needed: `clarity` (Kindle, Bleach), `match` (K-Match), `glow`
(Infrared). `grain` sets the Noise slider default — reuses the existing noise post-pass
rather than adding a grain stage. One new spatial function (`glowPass`, ~15 lines) for
halation; everything else reuses unsharpMask / buildMatchLUT.

**Sources** (researched, B&W film/darkroom characteristics):
- Tri-X vs HP5 characteristic curves — Tri-X punchier with highlight contrast, HP5 flatter
  with a longer shadow toe and softer highlight roll-off (35mmc, kubusphoto, emulsive).
- Lith printing — "creamy highlights and hard shadows… like a charcoal drawing"
  (en.wikipedia.org/wiki/Lith_print, alternativephotography, emulsive).
- Bleach bypass — retained silver = high contrast, rich/deep blacks, retained detail
  (en.wikipedia.org/wiki/Bleach_bypass).
- Solarization / Sabattier — partial tonal inversion (alternativephotography, photrio).
- Vintage film tone-curve preset reference — gentle roll-off, lifted shadows, grain
  (presetpedia).

**Consequence**: `adjustments.tone` → `adjustments.filter`. Selecting a filter overrides the
Noise slider with that filter's grain default. Filters' clarity/sharpen reuse the slider's
final-sharpen stage (default 1.0×) — non-Kindle filters get sharpened too; users can lower
it. Verified: all 16 filters build valid LUTs (executed from source); curves are distinct
and match design; Solar is the only non-monotonic one.
