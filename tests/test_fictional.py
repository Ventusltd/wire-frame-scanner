"""Exact geometry of the fictional parametric design proposals (scanner/fictional.py).
Run: python3 tests/test_fictional.py
"""
import math, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scanner import fictional as F

E = 1e-9
results = []


def check(name, ok):
    results.append((name, bool(ok)))


def seglen(s):
    return math.dist(s[0], s[1])


def all_tagged(obj):
    """Every number in the model sits in a {'value','unit','provenance'} dict with the design-proposal tag."""
    if isinstance(obj, dict):
        if 'value' in obj:
            return obj.get('provenance') == F.PROV and 'unit' in obj and isinstance(obj['value'], (int, float))
        return all(all_tagged(v) for v in obj.values())
    if isinstance(obj, (list, tuple)):
        return all(all_tagged(v) for v in obj)
    return not isinstance(obj, (int, float))  # a bare number anywhere fails


# box
m, s = F.box(3.0, 4.0, 5.0)
L = sorted(round(seglen(x), 12) for x in s)
check('box has 12 edges', len(s) == 12)
check('box edge lengths 4x3, 4x4, 4x5', L == [3.0] * 4 + [4.0] * 4 + [5.0] * 4)
check('box tagged', all_tagged(m))

# solar block, several cases
for (mw, wp, ml, mwid, mpt, p, tilt, az, tr) in [(5.0, 550, 2.278, 1.134, 28, 6.0, 20, 180, 2),
                                                 (12.3, 600, 2.384, 1.303, 26, 7.5, 25, 165, 2),
                                                 (1.0, 450, 1.9, 1.0, 36, 5.0, 15, 200, 3)]:
    m, s = F.solar_block(mw, wp, ml, mwid, mpt, p, tilt, az, table_rows=tr)
    t = m['tables']['value']
    cap = t * mpt * wp / 1e6
    one = mpt * wp / 1e6
    check(f'{mw} MW: tables x modules x Wp within one table of MW', cap >= mw - E and cap - mw < one)
    check(f'{mw} MW: rects == tables, 4 edges each', len(m['table_rects']) == t and len(s) == 4 * t)
    fx, fy = math.sin(math.radians(az)), math.cos(math.radians(az))
    fronts = {}
    for r in m['table_rects']:
        c0 = [q['value'] for q in r['corners'][0]]
        fronts.setdefault(r['row']['value'], c0)
    ok = all(abs(((fronts[k][0] - fronts[k + 1][0]) * fx + (fronts[k][1] - fronts[k + 1][1]) * fy) - p) < E
             for k in range(len(fronts) - 1))
    check(f'{mw} MW: row spacing equals pitch ({len(fronts)} rows)', ok and len(fronts) == m['rows']['value'])
    r0 = m['table_rects'][0]; c = [[q['value'] for q in pt] for pt in r0['corners']]
    slope = math.dist(c[0], c[3]); rise = c[3][2] - c[0][2]
    check(f'{mw} MW: table slope length and tilt exact', abs(slope - tr * ml) < E and
          abs(math.degrees(math.asin(rise / slope)) - tilt) < 1e-9 and abs(math.dist(c[0], c[1]) - mpt // tr * mwid) < E)
    check(f'{mw} MW: every value tagged', all_tagged(m))

# heights raster: table heights between front and back, zero elsewhere; tilt recoverable
m, _ = F.solar_block(0.5, 500, 2.0, 1.0, 20, 6.0, 20, 180, table_rows=2, origin=(90.0, 5.0))
H, xs, ys = F.solar_block_heights(m, (-10.0, -5.0, 110.0, 70.0), 0.25)
fh, bh = m['front_height']['value'], m['back_height']['value']
on = H > 0
check('heights raster: covered cells within front..back height', on.any() and H[on].min() >= fh - E and H[on].max() <= bh + E)
check('heights raster: covered area ~ tables x footprint', abs(on.sum() * 0.0625 - m['tables']['value'] *
      m['table_length']['value'] * m['table_depth_horizontal']['value']) / on.sum() / 0.0625 < 0.1)

# fenced compound
m, s = F.fenced_compound(40.0, 25.0, 2.4, 3.0)
rails = [x for x in s if x[0][2] == x[1][2] == 0.0]
check('compound perimeter 2(w+d)', abs(sum(seglen(x) for x in rails) - 130.0) < E and m['perimeter']['value'] == 130.0)
posts = [x for x in s if x[0][:2] == x[1][:2]]
check('compound posts spaced <= spacing, all fence height', len(posts) == m['posts']['value'] == 14 + 9 + 14 + 9
      and all(abs(seglen(x) - 2.4) < E for x in posts))
check('compound tagged', all_tagged(m))

# cable route
m, s = F.cable_route((0.0, 0.0), (300.0, 400.0), 0.9, 0.45)
check('route length exact', abs(m['length']['value'] - 500.0) < E and abs(seglen(s[0]) - 500.0) < E)
check('trench cross-section width and depth', abs(seglen(s[2]) - 0.45) < E and abs(seglen(s[1]) - 0.9) < E)
check('route tagged', all_tagged(m))

# pylon row
m, s = F.pylon_row((5.0, 5.0), 37.0, 350.0, 6)
wires = s[6:]
check('pylon spans exact', len(wires) == 5 and all(abs(seglen(x) - 350.0) < 1e-9 for x in wires))
check('pylon route length', abs(m['route_length']['value'] - 1750.0) < E)
check('pylon tagged', all_tagged(m))

for n, ok in results:
    print(f"{'PASS' if ok else 'FAIL'}  {n}")
npass = sum(ok for _, ok in results)
print(f"\n{npass}/{len(results)} pass")
sys.exit(0 if npass == len(results) else 1)
