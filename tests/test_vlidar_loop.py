"""Closed loop: model -> virtual LiDAR -> scanner -> model. The scanner, reading only the virtual survey's DSM minus
DTM (object heights above 1 m), must recover the model's row direction and pitch. GPU and CPU must agree.
Run: python tests/test_vlidar_loop.py
"""
import math, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scanner import core, vlidar

EXTENT, CELL = 160.0, 0.5
CASES = [(90.0, 7.5, 4.0), (17.0, 6.0, 3.2), (63.0, 11.0, 5.5), (135.0, 8.2, 4.4)]


def ground(xp, x, y):  # gently rolling ground, metres
    return 5.0 + 1.5 * xp.sin(x / 37.0) + 1.0 * xp.cos(y / 29.0)


def run(xp):
    out = []
    for (b, p, d) in CASES:
        obj = lambda xp_, x, y: vlidar.tables_height(xp_, x, y, b, p, d)
        x, y, first, last = vlidar.survey(xp, EXTENT, ground, obj, ppsm=8.0, noise_m=0.05, seed=7)
        dsm = vlidar.rasterise(xp, x, y, first, EXTENT, CELL)
        dtm = vlidar.rasterise(xp, x, y, last, EXTENT, CELL)
        mask = (dsm - dtm) > 1.0                                          # object heights above 1 m
        th = core.refine_normal(xp, mask, core.row_normal(xp, mask), CELL)
        r = core.row_pitch(xp, mask, th, CELL)
        got_b = (math.degrees(th) - 90) % 180; got_p = r[0] * CELL if r else None
        # raster y grows with survey y (north up is not assumed here), so compare direction in the raster's own frame
        dd = min(abs(got_b - b) % 180, 180 - abs(got_b - b) % 180)
        ok = got_p is not None and dd <= 1.0 and abs(got_p - p) <= 0.25
        out.append({'bearing': b, 'pitch': p, 'got_bearing': round(got_b, 2), 'got_pitch': got_p and round(got_p, 3),
                    'points': int(x.size), 'pass': bool(ok)})
    return out


if __name__ == '__main__':
    eng = [('numpy', np)]
    try:
        import cupy as cp; cp.cuda.runtime.getDeviceCount(); eng.insert(0, ('cupy', cp))
    except Exception:
        pass
    res = {n: run(m) for n, m in eng}
    agree = 'n/a (no GPU)' if len(eng) < 2 else all(a['got_bearing'] == b['got_bearing'] and a['got_pitch'] == b['got_pitch'] for a, b in zip(res['cupy'], res['numpy']))
    for n, rs in res.items():
        for r in rs:
            print(f"{n:5s} {'PASS' if r['pass'] else 'FAIL'}  model rows {r['bearing']:6.1f} deg {r['pitch']:5.2f} m  ->  scanner from virtual LiDAR {r['got_bearing']} deg {r['got_pitch']} m  ({r['points']} pulses)")
    k = eng[0][0]; npass = sum(r['pass'] for r in res[k])
    print(f"\n{k}: {npass}/{len(res[k])} closed-loop pass; GPU and CPU agree: {agree}")
    sys.exit(0 if npass == len(res[k]) and agree is not False else 1)
