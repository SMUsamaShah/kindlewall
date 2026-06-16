# Failures

_Things we actually tried that didn't work and why._

## Screen filter v1: k=8 sigmoid (wrong model)
- **Assumed**: Kindle screensaver images have a symmetric bimodal histogram created by an aggressive sigmoid
- **What pixel analysis of the actual images showed**: The mid-grey range (64–191) holds 26–40% of pixels — texture lives there and is NOT crushed. The huge black regions (28–45%) come from subject matter (deep shadows between densely-packed objects under directional lighting), not from tone curve manipulation.
- **Why k=8 was wrong**: A k=8 sigmoid depopulates midtones symmetrically. The real images are skewed heavily toward black with intact mid-grey texture detail.
- **Fix**: Level stretch (black point 20→0, white point 230→255) + gentle S-curve (k=4, 60/40 blend with linear) — snappy but texture-preserving. Dual clarity passes (25px macro + 5px micro) do the heavy lifting on contrast.
