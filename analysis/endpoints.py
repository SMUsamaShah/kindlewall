import numpy as np
from PIL import Image
import glob, os

files = sorted(glob.glob('original_kindle_screensavers/*.jpg'))
print(f"{'image':<18} {'max':>4} {'min':>4} | near-white breakdown (% of pixels)        | near-black")
print(f"{'':18} {'':>4} {'':>4} | =255  >=254 >=250 >=245 >=240 >=230        | =0    <=2   <=5   <=15")
print('-'*108)

for f in files:
    name = os.path.basename(f).replace('.jpg','')
    rgb = np.asarray(Image.open(f).convert('RGB'), dtype=np.float64)
    lum = 0.2126*rgb[...,0]+0.7152*rgb[...,1]+0.0722*rgb[...,2]
    flat = lum.ravel(); N = flat.size
    # also per-channel green (these are greyscale)
    g = rgb[...,1].ravel()
    def pf(arr, cond): return 100*np.mean(cond)
    print(f"{name:<18} {flat.max():>4.0f} {flat.min():>4.0f} | "
          f"{100*np.mean(flat>=255):>4.1f} {100*np.mean(flat>=254):>5.1f} {100*np.mean(flat>=250):>5.1f} "
          f"{100*np.mean(flat>=245):>5.1f} {100*np.mean(flat>=240):>5.1f} {100*np.mean(flat>=230):>5.1f}       | "
          f"{100*np.mean(flat<=0):>4.1f} {100*np.mean(flat<=2):>5.1f} {100*np.mean(flat<=5):>5.1f} {100*np.mean(flat<=15):>5.1f}")

print()
print("Same, measured on GREEN channel directly (greyscale source):")
print(f"{'image':<18} {'max':>4} | g=255  g>=250 g>=245 | g=0   g<=5")
print('-'*60)
for f in files:
    name = os.path.basename(f).replace('.jpg','')
    g = np.asarray(Image.open(f).convert('RGB'), dtype=np.float64)[...,1].ravel()
    print(f"{name:<18} {g.max():>4.0f} | {100*np.mean(g>=255):>4.1f} {100*np.mean(g>=250):>6.1f} "
          f"{100*np.mean(g>=245):>6.1f} | {100*np.mean(g<=0):>4.1f} {100*np.mean(g<=5):>5.1f}")
