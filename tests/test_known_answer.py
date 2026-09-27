"""Known-answer tests: synthetic 'farms' with EXACTLY known row direction and pitch. The scanner must recover them,
on the GPU (CuPy) when present and on the CPU (NumPy), and both must agree. Measured reality, not made-up numbers:
the answer is fixed by construction, so a pass means the maths measures what it claims.

Run: python tests/test_known_answer.py   (exit code 0 = all pass)
"""
import math, os, sys, json
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scanner import core

MPP = 0.746                              # metres per pixel at z17, latitude about 51
CASES = [  # (row_bearing_deg: direction the rows run, measured from image x-axis; pitch_m; table_depth_m; block w,h px)
    (90.0, 7.5, 4.0, 300, 220), (0.0, 9.0, 5.0, 260, 260), (17.0, 6.0, 3.2, 320, 240),
    (63.0, 11.0, 5.5, 280, 300), (135.0, 8.2, 4.4, 300, 200), (104.0, 13.5, 6.0, 360, 260),
]
TOL_PITCH_M, TOL_DIR_DEG = 0.25, 1.0


def farm(xp, bearing_deg, pitch_m, depth_m, w, h, noise=0.0, seed=0):
    """A block of parallel stripes (tables) at a known bearing and pitch, inside an irregular (sheared) outline."""
    yy, xx = xp.mgrid[0:h, 0:w].astype(xp.float32)
    th = math.radians(bearing_deg) + math.pi / 2                      # normal to the rows
    off = (xx * math.cos(th) + yy * math.sin(th)) * MPP
    stripes = (off % pitch_m) < depth_m
    outline = (xx > 10 + 0.15 * yy) & (xx < w - 10) & (yy > 10) & (yy < h - 10 - 0.1 * xx)
    m = stripes & outline
    if noise:
        rng = np.random.default_rng(seed)
        flip = xp.asarray(rng.random((h, w)) < noise)
        m = m ^ (flip & outline)
    return m


def measure(xp, mask):
    th = core.refine_normal(xp, mask, core.row_normal(xp, mask), MPP)
    r = core.row_pitch(xp, mask, th, MPP)
    if r is None:
        return None
    pitch_px, phase, lo = r
    rows_bearing = (math.degrees(th) - 90) % 180
    return rows_bearing, pitch_px * MPP


def ang_diff(a, b):
    d = abs(a - b) % 180
    return min(d, 180 - d)


def run(xp):
    out = []
    for (bdeg, p, d, w, h) in CASES:
        for noise in (0.0, 0.05):
            got = measure(xp, farm(xp, bdeg, p, d, w, h, noise))
            ok = got is not None and ang_diff(got[0], bdeg) <= TOL_DIR_DEG and abs(got[1] - p) <= TOL_PITCH_M
            out.append({'bearing': bdeg, 'pitch': p, 'noise': noise, 'got_bearing': got and round(got[0], 2),
                        'got_pitch': got and round(got[1], 3), 'pass': bool(ok)})
    return out


if __name__ == '__main__':
    engines = [('numpy', np)]
    try:
        import cupy as cp; cp.cuda.runtime.getDeviceCount(); engines.insert(0, ('cupy', cp))
    except Exception:
        pass
    results = {name: run(m) for name, m in engines}
    agree = True
    if len(engines) == 2:
        for a, b in zip(results['cupy'], results['numpy']):
            if a['got_bearing'] != b['got_bearing'] or a['got_pitch'] != b['got_pitch']:
                agree = False
    for name, rs in results.items():
        for r in rs:
            print(f"{name:5s} {'PASS' if r['pass'] else 'FAIL'}  rows {r['bearing']:6.1f} deg, pitch {r['pitch']:5.2f} m, noise {r['noise']:.2f}"
                  f"  ->  got {r['got_bearing']} deg, {r['got_pitch']} m")
    npass = sum(r['pass'] for r in results[engines[0][0]]); ntot = len(results[engines[0][0]])
    print(f"\n{engines[0][0]}: {npass}/{ntot} pass; GPU and CPU agree: {agree if len(engines) == 2 else 'n/a (no GPU)'}")
    sys.exit(0 if npass == ntot and agree else 1)
