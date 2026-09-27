"""Lattice pylon skeleton: geometry and determinism checks, then renders test-output/pylon.png.
Run: python tests/test_pylon.py
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scanner.pylon import lattice_pylon, leg_point, half_width, panel_levels, _ASSUMED_DIMS, CORNERS, ASSUMED_SRC

TOL = 1e-9
results = []


def check(name, ok, detail=''):
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")


def on_leg(p, d):
    x, y, z = p
    if z < -TOL or z > d['h_top'] + TOL:
        return False
    h = half_width(z, d)
    return any(abs(x - sx * h) < 1e-6 and abs(y - sy * h) < 1e-6 for sx, sy in CORNERS)


for v in (132, 275, 400):
    d = _ASSUMED_DIMS[v]
    for br in ('K', 'X'):
        lines, m = lattice_pylon(v, bracing=br)
        tag = f"{v} kV {br}"
        base = [leg_point(i, 0.0, d) for i in range(4)]
        want = {(sx * d['base_half'], sy * d['base_half'], 0.0) for sx, sy in CORNERS}
        check(f"{tag} legs meet ground at base corners", {tuple(round(c, 9) for c in p) for p in base} == want)
        waist = [leg_point(i, d['h_waist'], d) for i in range(4)]
        conv = all(abs(abs(p[0]) - d['waist_half']) < TOL and abs(abs(p[1]) - d['waist_half']) < TOL for p in waist)
        mono = all(half_width(z1, d) <= half_width(z0, d) + TOL for z0, z1 in zip(panel_levels(d)[:-1], panel_levels(d)[1:]))
        check(f"{tag} legs converge to waist and never widen", conv and mono)
        # bracing: lines whose endpoints are at different legs and different heights within the body/top panels
        n_p = d['n_body'] + d['n_top']
        brace = []
        for k in range(n_p):
            s = 4 + k * 16 + 8
            brace += lines[s:s + 8]
        allon = all(on_leg(a, d) and on_leg(b, d) for a, b in brace)
        check(f"{tag} every bracing endpoint lies on a leg", allon and len(brace) == 8 * n_p, f"({len(brace)} members)")
        exp = n_p * 16 + 4 + 2 * 3 * 5
        again, m2 = lattice_pylon(v, bracing=br)
        check(f"{tag} panel/line count deterministic and match formula",
              m['n_panels']['value'] == n_p and len(lines) == exp == m['n_lines']['value'] and again == lines,
              f"(panels {n_p}, lines {len(lines)})")
        drops = m['insulator_drops']['value']
        r = {(q['level']): q['tip'] for q in drops if q['side'] == 1}
        l = {(q['level']): q['tip'] for q in drops if q['side'] == -1}
        sym = len(r) == len(l) == 3 and all(abs(r[k][0] + l[k][0]) < TOL and r[k][2] == l[k][2] for k in r)
        arm_roots_on_leg = all(on_leg(a, d) for a, b in lines[4 + n_p * 16:] if abs(abs(a[0]) - d['waist_half']) < TOL)
        check(f"{tag} cross-arm tips symmetric, roots on legs", sym and arm_roots_on_leg)
        prov = all(m[k]['source'] == ASSUMED_SRC for k in ('height_top_m', 'base_width_m', 'waist_width_m', 'arm_lengths_m'))
        check(f"{tag} dimensions tagged assumed", prov)

hs = [lattice_pylon(v)[1]['height_top_m']['value'] for v in (132, 275, 400)]
ws = [lattice_pylon(v)[1]['base_width_m']['value'] for v in (132, 275, 400)]
check("heights ordered by voltage class", hs[0] < hs[1] < hs[2], f"(top {hs} m, base width {ws} m)")

# render
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
out = os.path.join(os.path.dirname(__file__), '..', 'test-output')
os.makedirs(out, exist_ok=True)
fig = plt.figure(figsize=(12, 5))
for k, (v, br) in enumerate([(132, 'K'), (275, 'X'), (400, 'K')]):
    ax = fig.add_subplot(1, 3, k + 1, projection='3d')
    for a, b in lattice_pylon(v, bracing=br)[0]:
        ax.plot([a[0], b[0]], [a[1], b[1]], [a[2], b[2]], lw=0.6, color='#333')
    ax.set_title(f"{v} kV, {br} bracing (assumed dims)", fontsize=9)
    ax.set_box_aspect((1, 1, 3)); ax.set_xlim(-8, 8); ax.set_ylim(-8, 8); ax.set_zlim(0, 50)
png = os.path.abspath(os.path.join(out, 'pylon.png'))
fig.savefig(png, dpi=110); plt.close(fig)
check("rendered", os.path.getsize(png) > 0, png)

print(f"\n{sum(results)}/{len(results)} pass")
sys.exit(0 if all(results) else 1)
