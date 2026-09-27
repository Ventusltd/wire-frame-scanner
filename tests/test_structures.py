"""Tower skeleton: PCHIP profile through measured pins, floor rings, helical diagrid on the rings.
Illustrative example pins only (generic 100 m tower). Run: python tests/test_structures.py
"""
import math, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scanner import structures as S

TOL = 1e-9
ROOT = os.path.join(os.path.dirname(__file__), '..')
results = []


def check(name, ok, detail=''):
    results.append(ok); print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")


if __name__ == '__main__':
    pins, spacing, n = S.EXAMPLE_PINS, 4.0, 24
    lines, model = S.tower_skeleton(pins, spacing, n)
    prof = model['profile_fn']
    err = max(abs(prof(p['z'])[0] - p['r']) for p in pins)
    check('profile passes through every pin', err <= TOL, f'max err {err:.2e}')
    check('pins tagged measured with source field', all(p['provenance'] == 'measured' and 'source' in p for p in model['pins']))
    zs = [r['z'] for r in model['rings']]
    exp = [k * spacing for k in range(int(100 / spacing) + 1)]
    check('rings at exact heights', len(zs) == len(exp) and all(abs(a - b) <= TOL for a, b in zip(zs, exp)), f'{len(zs)} rings')
    ring_set = {(round(r['z'], 6)): r['r'] for r in model['rings']}
    worst = 0.0
    for a, b, kind in lines:
        if kind.startswith('diagrid'):
            for (x, y, z) in (a, b):
                rr = min(model['rings'], key=lambda q: abs(q['z'] - z))
                worst = max(worst, abs(rr['z'] - z), abs(math.hypot(x, y) - rr['r']))
    check('every diagrid node lies on a ring', worst <= TOL, f'max err {worst:.2e}')
    R = len(zs); formula = n * (3 * R - 2)
    lines2, _ = S.tower_skeleton(pins, spacing, n)
    check('line count deterministic and equals n*(3R-2)', len(lines) == len(lines2) == formula == model['n_lines_formula'],
          f'R={R} n={n}: {len(lines)} lines (rings {n*R}, diagrid {2*n*(R-1)}), formula {formula}')
    worst = 0.0
    for p0, p1 in zip(pins[:-1], pins[1:]):
        zz = np.linspace(p0['z'], p1['z'], 2001); rr = prof(zz)
        lo, hi = min(p0['r'], p1['r']), max(p0['r'], p1['r'])
        worst = max(worst, float(np.max(np.maximum(rr - hi, lo - rr))))
        d = np.diff(rr) * np.sign(p1['r'] - p0['r'])
        worst = max(worst, float(-d.min()) if d.min() < 0 else 0.0)
    check('no overshoot between pins (monotone)', worst <= TOL, f'max excursion {worst:.2e}')
    # odd spacing: top ring added at total height, formula still holds
    l3, m3 = S.tower_skeleton(pins, 7.0, 16)
    check('non-divisible spacing adds top ring', abs(m3['rings'][-1]['z'] - 100.0) <= TOL and len(l3) == 16 * (3 * len(m3['rings']) - 2),
          f'{len(m3["rings"])} rings, {len(l3)} lines')
    out = os.path.join(ROOT, 'test-output'); os.makedirs(out, exist_ok=True)
    png = os.path.abspath(S.render_png(lines, model, os.path.join(out, 'tower.png')))
    print(f'PNG (illustrative example): {png}')
    print(f'\n{sum(results)}/{len(results)} pass')
    sys.exit(0 if all(results) else 1)
