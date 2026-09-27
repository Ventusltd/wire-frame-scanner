"""Wire Frame Scanner core: measured, deterministic maths that runs on the GPU (CuPy) and the CPU (NumPy) alike.

Every function takes the array module `xp` (cupy or numpy), so the same code is its own witness: run it twice
and the answers must agree. Units: pixels in, metres out once `mpp` (metres per pixel) is given.

  panel_mask(xp, rgb)                 dark, not green: where panels are in satellite imagery
  label_blocks(xp, mask)              connected regions (R1), labels with areas
  row_normal(xp, block)               R2: the direction across the rows, from the row EDGES (structure tensor),
                                      not from the block's outline
  row_pitch(xp, block, theta, mpp)    R3: the fundamental spacing across the rows, limited to 4-15 m, with the phase
  row_lines(xp, block, theta, pitch, phase)  R4: one segment per row, clipped to the block
"""
import math

PITCH_MIN_M, PITCH_MAX_M = 4.0, 15.0


def panel_mask(xp, rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (0.3 * r + 0.59 * g + 0.11 * b < 75) & (g < r + 12) & (b > g - 18)


def label_blocks(xp, mask, ndimage, min_px=400):
    lab, n = ndimage.label(mask)
    areas = ndimage.sum(mask, lab, xp.arange(1, n + 1)) if n else xp.zeros(0)
    keep = [int(i) + 1 for i in range(n) if float(areas[i]) >= min_px]
    return lab, keep


def row_normal(xp, block):
    """Angle (radians, image x right / y down) of the normal to the rows, from the structure tensor of the mask edges.
    Rows are long thin stripes: their edges' gradients point across the rows, so the dominant gradient orientation
    is the row normal. The block's outline contributes little, because the rows' edges vastly outnumber it."""
    B = block.astype(xp.float32)
    gy, gx = xp.gradient(B)
    jxx, jyy, jxy = float((gx * gx).sum()), float((gy * gy).sum()), float((gx * gy).sum())
    return 0.5 * math.atan2(2 * jxy, jxx - jyy)


def row_pitch(xp, block, theta, mpp):
    """(pitch_px, phase_px, profile_origin) from the 1D profile of the block across the rows. The pitch is the
    FUNDAMENTAL inside 4-15 m: the lowest-frequency peak holding at least half the strongest peak's power in range."""
    Y, X = xp.nonzero(block)
    nx, ny = math.cos(theta), math.sin(theta)
    proj = X.astype(xp.float32) * nx + Y.astype(xp.float32) * ny
    lo = float(proj.min()); L = int(float(proj.max()) - lo) + 2
    prof = xp.bincount((proj - lo).astype(xp.int32), minlength=L).astype(xp.float32)
    n = 1 << max(10, (L * 4 - 1).bit_length())                       # zero-padded for a fine frequency grid
    G = xp.abs(xp.fft.rfft(prof - prof.mean(), n=n))
    f = xp.arange(G.size, dtype=xp.float32) / n                       # cycles per pixel
    fmin, fmax = mpp / PITCH_MAX_M, mpp / PITCH_MIN_M
    inr = (f >= fmin) & (f <= fmax)
    if not bool(inr.any()):
        return None
    Gi = xp.where(inr, G, 0)
    peak = float(Gi.max())
    # local maxima in range with at least half the strongest power: take the lowest frequency (the fundamental)
    loc = (Gi[1:-1] > Gi[:-2]) & (Gi[1:-1] >= Gi[2:]) & (Gi[1:-1] >= 0.5 * peak)
    idx = xp.nonzero(loc)[0]
    k = int(idx[0]) + 1 if idx.size else int(Gi.argmax())
    pitch = 1.0 / float(f[k])
    # phase: where the stripes sit, from the profile's projection onto the fundamental
    t = xp.arange(L, dtype=xp.float32)
    c, s = float((prof * xp.cos(2 * math.pi * t / pitch)).sum()), float((prof * xp.sin(2 * math.pi * t / pitch)).sum())
    phase = (math.atan2(s, c) / (2 * math.pi)) * pitch % pitch
    return pitch, phase, lo


def row_lines(xp, block, theta, pitch, phase, lo, min_px=6):
    """One segment per row: the extent of block pixels within 1 px of each row centre line (pixel coordinates)."""
    Y, X = xp.nonzero(block)
    nx, ny = math.cos(theta), math.sin(theta); tx, ty = -ny, nx
    off = X.astype(xp.float32) * nx + Y.astype(xp.float32) * ny - lo
    along = X.astype(xp.float32) * tx + Y.astype(xp.float32) * ty
    segs, d, top = [], phase, float(off.max())
    while d <= top:
        on = xp.abs(off - d) < 1.0
        if int(on.sum()) >= min_px:
            a0, a1 = float(along[on].min()), float(along[on].max())
            base = lo + d
            segs.append((base * nx + a0 * tx, base * ny + a0 * ty, base * nx + a1 * tx, base * ny + a1 * ty))
        d += pitch
    return segs


def refine_normal(xp, block, theta0, mpp, span_deg=8.0, step_deg=0.1):
    """Brute force: sweep the row normal +/- span around theta0 and keep the angle whose cross-row profile has the
    sharpest in-range spectral peak. Rows seen exactly edge-on give the tallest, narrowest peak. Deterministic."""
    Y, X = xp.nonzero(block)
    Xf, Yf = X.astype(xp.float32), Y.astype(xp.float32)
    best, best_t = -1.0, theta0
    k = int(round(span_deg / step_deg))
    for i in range(-k, k + 1):
        t = theta0 + math.radians(i * step_deg)
        proj = Xf * math.cos(t) + Yf * math.sin(t)
        lo = float(proj.min()); L = int(float(proj.max()) - lo) + 2
        prof = xp.bincount((proj - lo).astype(xp.int32), minlength=L).astype(xp.float32)
        n = 1 << max(10, (L * 4 - 1).bit_length())
        G = xp.abs(xp.fft.rfft(prof - prof.mean(), n=n))
        f = xp.arange(G.size, dtype=xp.float32) / n
        G = xp.where((f >= mpp / PITCH_MAX_M) & (f <= mpp / PITCH_MIN_M), G, 0)
        v = float(G.max())
        if v > best:
            best, best_t = v, t
    return best_t
