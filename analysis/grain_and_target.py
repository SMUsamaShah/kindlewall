import numpy as np
from PIL import Image
from scipy import ndimage
import glob, os, json

files = sorted(glob.glob('original_kindle_screensavers/*.jpg'))

# ============ GRAIN / TEXTURE SCALE ============
# Local std at multiple window sizes characterises texture energy by scale.
print("=== Texture energy by window size (mean local std) ===")
print(f"{'image':<18} {'w3':>6} {'w7':>6} {'w15':>6} {'w31':>6} {'w63':>6}")
print('-'*50)
for f in files:
    name = os.path.basename(f).replace('.jpg','')
    g = np.asarray(Image.open(f).convert('L'), dtype=np.float64)
    row = [name]
    for w in [3,7,15,31,63]:
        m = ndimage.uniform_filter(g, w)
        sq = ndimage.uniform_filter(g*g, w)
        ls = np.sqrt(np.clip(sq-m*m,0,None))
        row.append(f"{ls.mean():.1f}")
    print(f"{row[0]:<18} {row[1]:>6} {row[2]:>6} {row[3]:>6} {row[4]:>6} {row[5]:>6}")

# ============ GRAIN CORRELATION LENGTH ============
# Autocorrelation of high-pass residual → how many px until grain decorrelates.
print("\n=== Grain correlation (high-pass autocorrelation half-width, px) ===")
for f in files:
    name = os.path.basename(f).replace('.jpg','')
    g = np.asarray(Image.open(f).convert('L'), dtype=np.float64)
    hp = g - ndimage.gaussian_filter(g, 2.0)   # high-pass residual
    hp = hp - hp.mean()
    # 1D horizontal autocorrelation averaged over rows, central crop
    c = hp[400:800, 300:600]
    ac = np.zeros(15)
    for lag in range(15):
        if lag==0: ac[lag]=1.0
        else:
            a = c[:, :-lag].ravel(); b = c[:, lag:].ravel()
            ac[lag] = np.corrcoef(a,b)[0,1]
    # half-width: first lag where ac drops below 0.5
    hw = next((i for i,v in enumerate(ac) if v<0.5), 15)
    print(f"{name:<18} lag0..6 = {' '.join(f'{v:+.2f}' for v in ac[:7])}  half<0.5 at {hw}px")

# ============ CANONICAL TARGET HISTOGRAM (average of 5) ============
acc = np.zeros(256)
for f in files:
    g = np.asarray(Image.open(f).convert('L'), dtype=np.uint8)
    h,_ = np.histogram(g.ravel(), bins=256, range=(0,256))
    acc += h / g.size
target = acc / len(files)

# Decile boundaries of the averaged CDF
cdf = np.cumsum(target)
print("\n=== Canonical target: value at each percentile (avg of 5) ===")
for p in [1,5,10,20,30,40,50,60,70,80,90,95,99]:
    v = np.searchsorted(cdf, p/100)
    print(f"  p{p:<3} -> grey {v}")

# Zone masses for canonical target
def zone(lo,hi): return float(target[lo:hi+1].sum())
print("\n=== Canonical target zone masses ===")
zones = {
  '0 (pure black)': zone(0,0), '1-15': zone(1,15), '16-31': zone(16,31),
  '32-63': zone(32,63), '64-95': zone(64,95), '96-127': zone(96,127),
  '128-159': zone(128,159), '160-191': zone(160,191), '192-223': zone(192,223),
  '224-239': zone(224,239), '240-254': zone(240,254), '255 (pure white)': zone(255,255),
}
for k,v in zones.items(): print(f"  {k:<18} {v*100:5.1f}%")

# 16-bin compact histogram for embedding + ASCII bar
print("\n=== Canonical 16-bin histogram (each bin = 16 grey levels) ===")
b16 = target.reshape(16,16).sum(axis=1)
mx = b16.max()
for i,v in enumerate(b16):
    bar = '#'*int(round(v/mx*40))
    print(f"  {i*16:>3}-{i*16+15:<3} {v*100:5.1f}% |{bar}")

# Save canonical target + 16-bin for the doc
with open('analysis/target_hist.json','w') as fp:
    json.dump({
        'target_256': target.tolist(),
        'target_16bin': b16.tolist(),
        'percentile_values': {str(p): int(np.searchsorted(cdf,p/100)) for p in [1,5,10,20,30,40,50,60,70,80,90,95,99]},
        'zone_masses': zones,
    }, fp, indent=2)
print("\nWrote analysis/target_hist.json")
