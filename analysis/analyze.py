import numpy as np
from PIL import Image
from scipy import ndimage
import json, os, glob

REF_DIR = 'original_kindle_screensavers'
files = sorted(glob.glob(f'{REF_DIR}/*.jpg'))
results = {}

def luminance(rgb):
    # ITU-R BT.709
    return 0.2126*rgb[...,0] + 0.7152*rgb[...,1] + 0.0722*rgb[...,2]

def skew_kurt(x):
    m = x.mean(); s = x.std()
    if s == 0: return 0.0, 0.0
    z = (x - m) / s
    return float((z**3).mean()), float((z**4).mean() - 3.0)

for f in files:
    name = os.path.basename(f).replace('.jpg','')
    rgb = np.asarray(Image.open(f).convert('RGB'), dtype=np.float64)
    R,G,B = rgb[...,0], rgb[...,1], rgb[...,2]

    # --- Is it truly greyscale? channel deltas ---
    dRG = np.abs(R-G); dRB = np.abs(R-B); dGB = np.abs(G-B)
    max_ch_dev = float(np.max([dRG.max(), dRB.max(), dGB.max()]))
    mean_ch_dev = float(np.mean([dRG.mean(), dRB.mean(), dGB.mean()]))
    # fraction of pixels where channels differ by > 2
    frac_chromatic = float(np.mean((dRG>2)|(dRB>2)|(dGB>2)))

    # Use the green channel as the working luma (greyscale image: all ~equal).
    # Use rounded luminance to be safe.
    lum = luminance(rgb)
    g = lum.astype(np.float64)
    flat = g.ravel()
    N = flat.size

    # --- Histogram (256 bins) ---
    hist, _ = np.histogram(flat, bins=256, range=(0,256))
    hist_norm = (hist / N).tolist()

    # --- Percentiles ---
    pcts = [0.1,1,2,5,10,25,50,75,90,95,98,99,99.9]
    perc = {str(p): float(np.percentile(flat, p)) for p in pcts}

    # --- Moments ---
    mean = float(flat.mean()); median = float(np.median(flat)); std = float(flat.std())
    sk, ku = skew_kurt(flat)

    # --- Clipping & zones ---
    def frac(lo, hi):  # inclusive lo, inclusive hi
        return float(np.mean((flat>=lo)&(flat<=hi)))
    zones = {
        'pure_black_0':       frac(0,0),
        'near_black_0_15':    frac(0,15),
        'deep_shadow_16_63':  frac(16,63),
        'shadow_64_95':       frac(64,95),
        'midgrey_96_159':     frac(96,159),
        'highlight_160_223':  frac(160,223),
        'near_white_240_255': frac(240,255),
        'pure_white_255':     frac(255,255),
        'midtone_64_191':     frac(64,191),
    }

    # --- Gradient / sharpening signature (Sobel magnitude) ---
    gx = ndimage.sobel(g, axis=1)
    gy = ndimage.sobel(g, axis=0)
    gmag = np.hypot(gx, gy) / 4.0  # normalise sobel scale
    gmag_flat = gmag.ravel()
    grad = {
        'mean': float(gmag_flat.mean()),
        'median': float(np.median(gmag_flat)),
        'p90': float(np.percentile(gmag_flat,90)),
        'p99': float(np.percentile(gmag_flat,99)),
        'frac_strong_edge_gt40': float(np.mean(gmag_flat>40)),
        'frac_flat_lt5': float(np.mean(gmag_flat<5)),
    }

    # --- Local contrast (clarity) — std in sliding windows ---
    # local std via uniform filter
    win = 15
    mean_f = ndimage.uniform_filter(g, win)
    sq_f   = ndimage.uniform_filter(g*g, win)
    local_var = np.clip(sq_f - mean_f*mean_f, 0, None)
    local_std = np.sqrt(local_var)
    clarity = {
        'local_std_mean': float(local_std.mean()),
        'local_std_p50': float(np.median(local_std)),
        'local_std_p90': float(np.percentile(local_std,90)),
    }

    # --- Laplacian variance (focus / acutance) ---
    lap = ndimage.laplace(g)
    lap_var = float(lap.var())

    # --- Radial power spectrum (high-freq energy = sharpening) ---
    # downsample to square for speed
    gg = np.asarray(Image.fromarray(g.astype(np.uint8)).resize((512,512)), dtype=np.float64)
    gg = gg - gg.mean()
    F = np.fft.fftshift(np.fft.fft2(gg))
    P = np.abs(F)**2
    cy, cx = 256, 256
    yy, xx = np.indices((512,512))
    r = np.hypot(xx-cx, yy-cy).astype(int)
    radial = ndimage.mean(P, labels=r, index=np.arange(0, 256))
    radial = radial / radial.sum()
    # energy fractions by frequency band (as fraction of Nyquist)
    def band(lo, hi):
        return float(radial[int(lo*256):int(hi*256)].sum())
    freq = {
        'low_0_10pct':   band(0.0, 0.10),
        'mid_10_40pct':  band(0.10, 0.40),
        'high_40_100pct':band(0.40, 1.0),
    }

    results[name] = {
        'size': list(Image.open(f).size),
        'greyscale_check': {
            'max_channel_deviation': max_ch_dev,
            'mean_channel_deviation': mean_ch_dev,
            'frac_pixels_chromatic_gt2': frac_chromatic,
        },
        'moments': {'mean':mean,'median':median,'std':std,'skewness':sk,'kurtosis':ku},
        'percentiles': perc,
        'zones': zones,
        'gradient': grad,
        'clarity_local_std': clarity,
        'laplacian_variance': lap_var,
        'freq_energy': freq,
        'histogram_256': hist_norm,
    }
    print(f"{name}: mean={mean:.1f} median={median:.0f} std={std:.1f} "
          f"black0={zones['pure_black_0']*100:.1f}% white255={zones['pure_white_255']*100:.1f}% "
          f"mid={zones['midtone_64_191']*100:.1f}% skew={sk:.2f}")

# --- Aggregate across all 5 ---
def agg(path):
    vals = []
    for n in results:
        d = results[n]
        for k in path[:-1]: d = d[k]
        vals.append(d[path[-1]])
    return {'min':float(min(vals)),'max':float(max(vals)),'mean':float(np.mean(vals))}

results['_aggregate'] = {
    'mean':            agg(['moments','mean']),
    'median':          agg(['moments','median']),
    'std':             agg(['moments','std']),
    'skewness':        agg(['moments','skewness']),
    'kurtosis':        agg(['moments','kurtosis']),
    'pure_black_pct':  agg(['zones','pure_black_0']),
    'near_black_pct':  agg(['zones','near_black_0_15']),
    'pure_white_pct':  agg(['zones','pure_white_255']),
    'near_white_pct':  agg(['zones','near_white_240_255']),
    'midtone_pct':     agg(['zones','midtone_64_191']),
    'grad_mean':       agg(['gradient','mean']),
    'grad_p90':        agg(['gradient','p90']),
    'grad_p99':        agg(['gradient','p99']),
    'local_std_mean':  agg(['clarity_local_std','local_std_mean']),
    'lap_var':         agg(['laplacian_variance']) if False else None,
    'freq_high':       agg(['freq_energy','high_40_100pct']),
    'freq_mid':        agg(['freq_energy','mid_10_40pct']),
    'freq_low':        agg(['freq_energy','low_0_10pct']),
}

with open('analysis/metrics.json','w') as fp:
    json.dump(results, fp, indent=2)
print("\nWrote analysis/metrics.json")
