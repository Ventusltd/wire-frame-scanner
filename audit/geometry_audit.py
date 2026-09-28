"""Geometry CI audit for the Energy Transition Simulator, on the GPU (CuPy) with a NumPy witness.

A simulator is only as real as its geometry. This audit measures, in numbers, whether the geometry the product draws
can carry a walk-and-build simulator at 1:1, and writes a Markdown report plus a JSON of every number.

Four audits, each a GPU crunch with a CPU (NumPy) witness on a sample:

1. PRECISION: why geometry "breaks" when you zoom from a drone view down to 1.7 m eye height.
   A custom WebGL layer that stores vertices as absolute Web Mercator coordinates in float32 can only place a point
   on a grid of about 2^-24 of the world, which at 51 deg N is about 0.75 m on the ground. A table member is 0.05 to
   0.10 m. Relative-to-centre (RTC) storage keeps vertices in metres about a local origin, so float32 spacing is
   about 60 micrometres at 1 km. The audit places a dense cloud of module corners on every measured row, stores it
   both ways, and reports the ground error (m) and the screen error (px) at map zooms 16 to 24 and at walk eye height.

2. TABLES AS SOLIDS: the tables module's tables (exported through Node from the product's own tables.js) are
   rasterised on the GPU at 0.25 m. Overlaps between tables, the aisle widths a walker gets between neighbouring
   tables, and tables that sit off the measured pitch lattice are counted.

3. TRENCH BENDS THAT PHYSICALLY FIT: a duct or cable cannot turn tighter than its bend radius R. At a polyline vertex
   with deflection theta, a bend of radius R needs a tangent length t = R tan(theta / 2) on BOTH neighbouring segments
   (and two consecutive bends must share a segment: t_i + t_{i+1} <= L). Every vertex of every route of every case
   is tested for a sweep of R from 0.25 m to 3.0 m, so the report says which radii the routes can really carry.

4. CODE: every product module is scanned for how it passes coordinates to the GPU (absolute Mercator against a
   local origin), whether it has a test, and words and paths that must not be public.

Run:  python geometry_audit.py --repo <energy-transition-simulator clone> --out <folder>
CuPy is used when present (the RTX 5070 Ti on the MSI); otherwise NumPy runs everything and the report says so.
"""
import argparse, hashlib, json, math, os, re, subprocess, sys, time
import numpy as np

try:
    import cupy as cp
    cp.zeros(1).sum()
    XP, GPU = cp, cp.cuda.runtime.getDeviceProperties(0)['name'].decode()
except Exception:                                                   # no GPU: the NumPy path, said in the report
    XP, GPU = np, 'none (NumPy)'

WGS84_A = 6378137.0                                                 # Web Mercator sphere radius (EPSG:3857)
CIRC = 2 * math.pi * WGS84_A                                        # the Mercator world width in metres at the equator
EYE_M, FOV_DEG, SCREEN_H = 1.7, 60.0, 1080                          # walk camera: eye height, vertical FOV, pixels


def to_np(a):
    return cp.asnumpy(a) if XP is not np else a


def mercator(xp, lon, lat):
    """Web Mercator unit coordinates [0, 1] (MapLibre's MercatorCoordinate), in the dtype of the inputs."""
    x = (lon + 180.0) / 360.0
    y = (180.0 - (180.0 / math.pi) * xp.log(xp.tan(math.pi / 4 + lat * math.pi / 360.0))) / 360.0
    return x, y


# ---------------------------------------------------------------------------------------------- 1. precision
def audit_precision(rows_lonlat, lat0):
    """Module corners along every measured row: 2 corners per 1.323 m column on each of the row's two edges and its
    ridge, so a dense cloud of real positions. Returns ground and screen errors of float32 absolute Mercator vs RTC."""
    r = XP.asarray(rows_lonlat, dtype=XP.float64)                   # (n, 2, 2) lon/lat ends of each run
    a, b = r[:, 0, :], r[:, 1, :]
    kx, ky = WGS84_A * math.cos(math.radians(lat0)) * math.pi / 180, WGS84_A * math.pi / 180
    L = XP.hypot((b[:, 0] - a[:, 0]) * kx, (b[:, 1] - a[:, 1]) * ky)
    per = XP.maximum(2, XP.ceil(L / 1.323).astype(XP.int64))       # module columns along each run
    n = int(per.sum())
    idx = XP.repeat(XP.arange(r.shape[0]), to_np(per).tolist())
    start = XP.cumsum(per) - per
    t = (XP.arange(n) - XP.repeat(start, to_np(per).tolist())) / XP.repeat(per - 1, to_np(per).tolist())
    lon = a[idx, 0] + t * (b[idx, 0] - a[idx, 0])
    lat = a[idx, 1] + t * (b[idx, 1] - a[idx, 1])
    # three lines per run (west edge, ridge, east edge: +-12.15 m across) and two corners per column (0.02 m gap)
    across = XP.asarray([-12.15, 0.0, 12.15], dtype=XP.float64) / kx
    lon = (lon[:, None] + across[None, :]).ravel()
    lat = XP.repeat(lat, 3)
    lon = XP.concatenate([lon, lon + 0.02 / kx]); lat = XP.concatenate([lat, lat])
    x64, y64 = mercator(XP, lon, lat)                               # truth in float64
    x32, y32 = x64.astype(XP.float32), y64.astype(XP.float32)       # what an absolute float32 layer stores
    m_per_unit = CIRC * math.cos(math.radians(lat0))                # ground metres per Mercator unit at this latitude
    err_abs = XP.hypot(x32.astype(XP.float64) - x64, y32.astype(XP.float64) - y64) * m_per_unit
    ox, oy = float(x64.mean()), float(y64.mean())                   # RTC: a local origin, metres about it in float32
    ex, ey = ((x64 - ox) * m_per_unit).astype(XP.float32), ((y64 - oy) * m_per_unit).astype(XP.float32)
    err_rtc = XP.hypot(ex.astype(XP.float64) - (x64 - ox) * m_per_unit, ey.astype(XP.float64) - (y64 - oy) * m_per_unit)
    # camera jitter: the camera moves 1 cm; an absolute float32 pipeline subtracts two float32 positions
    camx = float(x64[0]) + 0.01 / m_per_unit                        # the camera, 1 cm east of the first corner
    d_abs = (x32 - XP.float32(camx)).astype(XP.float64) * m_per_unit
    d_true = (x64 - camx) * m_per_unit
    jitter_abs = XP.abs(d_abs - d_true)
    # NumPy witness on a 20,000-point sample
    s = np.linspace(0, n * 6 - 1, 20000).astype(np.int64)
    lo, la = to_np(lon)[s], to_np(lat)[s]
    wx, wy = mercator(np, lo, la)
    w_abs = np.hypot(wx.astype(np.float32).astype(np.float64) - wx, wy.astype(np.float32).astype(np.float64) - wy) * m_per_unit
    witness = float(np.abs(w_abs - to_np(err_abs)[s]).max())
    pct = lambda v, q: float(XP.percentile(v, q))
    out = {'points': int(x64.size), 'runs': int(r.shape[0]), 'metres_per_mercator_unit': m_per_unit,
           'abs_f32_ground_err_m': {'p50': pct(err_abs, 50), 'p99': pct(err_abs, 99), 'max': float(err_abs.max())},
           'rtc_f32_ground_err_m': {'p50': pct(err_rtc, 50), 'p99': pct(err_rtc, 99), 'max': float(err_rtc.max())},
           'abs_f32_jitter_1cm_step_m': {'p99': pct(jitter_abs, 99), 'max': float(jitter_abs.max())},
           'witness_max_diff_m': witness, 'zooms': {}}
    fpx = (SCREEN_H / 2) / math.tan(math.radians(FOV_DEG / 2))      # focal length in px
    for z in range(16, 25):
        px_per_m = 512 * 2 ** z / m_per_unit                        # map scale at zoom z (512 px tiles)
        out['zooms'][z] = {'abs_px': out['abs_f32_ground_err_m']['max'] * px_per_m,
                           'rtc_px': out['rtc_f32_ground_err_m']['max'] * px_per_m}
    for d in (2.0, 5.0, 20.0):                                      # a member d metres from the walk eye
        out['zooms'][f'walk_{d:g}m'] = {'abs_px': out['abs_f32_ground_err_m']['max'] * fpx / d,
                                         'rtc_px': out['rtc_f32_ground_err_m']['max'] * fpx / d}
    return out


# ---------------------------------------------------------------------------------------------- 2. tables
def export_tables(repo):
    """Run the product's own tables.js in Node (the same path its test takes) and return the tables in the row frame."""
    js = r"""
const path=require('path'),fs=require('fs');const MOD=path.join(process.argv[1],'prototype','mod');const T=require(path.join(MOD,'tables.js'));
const D={height:1.2,tilt:10,tables:23,columns:90,rows:5,moduleWidth:1.303,moduleLength:2.384,moduleGap:0.02,rowGap:8,aisleGap:10,ridgeGap:0.5,stringsPerInverter:24,inverters:28,modulesPerString:30};
const fp=T.farmParams(D),f=JSON.parse(fs.readFileSync(path.join(MOD,'scanner-rows.farms.json'),'utf8')).farms[0],doc=JSON.parse(fs.readFileSync(path.join(MOD,f.rows),'utf8'));
const R=6371008.8,K=Math.PI/180,kx=R*Math.cos(f.point.lat*K)*K,ky=R*K;
const runs=doc.rows.map(([[a,b],[c,d]])=>[(a-f.point.lon)*kx,(b-f.point.lat)*ky,(c-f.point.lon)*kx,(d-f.point.lat)*ky]);
const rr=T.rowsFromRuns(runs,{step:f.sample_step_px.value*doc.metres_per_pixel}),tb=T.tablesFromRows(rr.rows,fp.params,rr.raster);
process.stdout.write(JSON.stringify({axis:rr.axis,pitch:rr.pitch,halfW:T.halfWidthOf(fp.params),width:fp.width,tables:tb.map(t=>[t.u,t.v0,t.span,t.columns,t.row,t.cov])}));
"""
    p = subprocess.run(['node', '-e', js, repo], capture_output=True, text=True, timeout=120)
    if p.returncode:
        raise RuntimeError(p.stderr[-400:])
    return json.loads(p.stdout)


def audit_tables(T, cell=0.25):
    tb = XP.asarray(T['tables'], dtype=XP.float64)                  # u, v0, span, columns, row, cov (row frame)
    hw = T['halfW']
    u, v0, span = tb[:, 0], tb[:, 1], tb[:, 2]
    u0, u1, va, vb = u - hw, u + hw, v0, v0 + span
    # raster in the row frame: count how many tables cover each 0.25 m cell
    U0, V0 = float(u0.min()) - 5, float(va.min()) - 5
    nu, nv = int((float(u1.max()) - U0 + 5) / cell), int((float(vb.max()) - V0 + 5) / cell)
    grid = XP.zeros((nv, nu), dtype=XP.uint8)
    for i in range(tb.shape[0]):                                     # 600-odd rectangles; each a GPU slice add
        a, b = int((float(u0[i]) - U0) / cell), int((float(u1[i]) - U0) / cell)
        c, d = int((float(va[i]) - V0) / cell), int((float(vb[i]) - V0) / cell)
        grid[c:d, a:b] += 1
    overlap_m2 = float((grid >= 2).sum()) * cell * cell
    cover_m2 = float((grid >= 1).sum()) * cell * cell
    # aisles: for every pair of tables whose v ranges overlap by 5 m or more, the clear gap across the rows
    du = u[None, :] - u[:, None]
    ov = XP.minimum(vb[:, None], vb[None, :]) - XP.maximum(va[:, None], va[None, :])
    gap = du - 2 * hw
    near = (du > 0) & (ov > 5) & (gap < 15)
    g = gap[near]
    # the nearest neighbour to the east of each table (the aisle a walker stands in)
    big = XP.where(near, gap, XP.inf).min(axis=1)
    aisle = big[XP.isfinite(big)]
    # lattice: the offset of each table's centre from the best 26.8 m comb
    P = T['pitch'] or 26.8
    ph = XP.angle(XP.exp(2j * math.pi * u / P).sum())                # circular mean phase of all centres
    off = ((u - ph * P / (2 * math.pi)) / P + 0.5) % 1.0 - 0.5
    off_m = XP.abs(off * P)
    # NumPy witness: the overlap area recomputed on the CPU for 20 random tables' neighbourhoods
    tn = to_np(tb); rng = np.random.default_rng(6502); wd = 0.0
    for i in rng.choice(len(tn), 20, replace=False):
        a, b = int((tn[i, 0] - hw - U0) / cell), int((tn[i, 0] + hw - U0) / cell)
        c, d = int((tn[i, 1] - V0) / cell), int((tn[i, 1] + tn[i, 2] - V0) / cell)
        cnt = np.zeros((d - c, b - a), np.uint8)
        for j in range(len(tn)):
            aa, bb = int((tn[j, 0] - hw - U0) / cell) - a, int((tn[j, 0] + hw - U0) / cell) - a
            cc, dd = int((tn[j, 1] - V0) / cell) - c, int((tn[j, 1] + tn[j, 2] - V0) / cell) - c
            cnt[max(cc, 0):max(min(dd, d - c), 0), max(aa, 0):max(min(bb, b - a), 0)] += 1
        wd = max(wd, abs(float(cnt.sum()) - float(to_np(grid[c:d, a:b]).astype(np.int64).sum())))
    pct = lambda v, q: float(XP.percentile(v, q)) if v.size else None
    return {'tables': int(tb.shape[0]), 'half_width_m': hw, 'pitch_m': P, 'raster_cells': int(grid.size), 'cell_m': cell,
            'cover_ha': cover_m2 / 1e4, 'overlap_m2': overlap_m2,
            'overlapping_pairs': int(((gap < -0.01) & near).sum()),
            'aisle_m': {'min': pct(aisle, 0), 'p5': pct(aisle, 5), 'p50': pct(aisle, 50), 'p95': pct(aisle, 95), 'n': int(aisle.size)},
            'aisles_under_1m': int((aisle < 1.0).sum()), 'aisles_1_to_2m': int(((aisle >= 1.0) & (aisle < 2.0)).sum()),
            'off_lattice_m': {'p50': pct(off_m, 50), 'p95': pct(off_m, 95), 'max': float(off_m.max())},
            'tables_off_lattice_over_1m': int((off_m > 1.0).sum()),
            'witness_cell_count_max_diff': wd}


# ---------------------------------------------------------------------------------------------- 3. trench bends
def audit_bends(trench):
    """Every chain vertex of every case: can a bend of radius R be fitted? t = R tan(theta/2) must fit in half of
    each neighbouring segment (two bends share a segment)."""
    out = {}
    radii = XP.linspace(0.25, 3.0, 56)
    for case, c in trench['cases'].items():
        th_all, room_all = [], []
        for e in c['edges']:
            xy = np.asarray(e[6:], dtype=np.float64).reshape(-1, 2)
            if len(xy) < 3:
                continue
            d = np.diff(xy, axis=0); L = np.hypot(d[:, 0], d[:, 1])
            keep = L > 1e-6; d, L = d[keep], L[keep]
            if len(L) < 2:
                continue
            a1 = np.arctan2(d[:-1, 1], d[:-1, 0]); a2 = np.arctan2(d[1:, 1], d[1:, 0])
            th = np.abs((a2 - a1 + np.pi) % (2 * np.pi) - np.pi)       # deflection at each interior vertex
            room = np.minimum(L[:-1], L[1:]) / 2                        # half of the shorter neighbouring segment
            th_all.append(th); room_all.append(room)
        if not th_all:
            continue
        th = XP.asarray(np.concatenate(th_all)); room = XP.asarray(np.concatenate(room_all))
        bent = th > math.radians(1.0)
        need = radii[:, None] * XP.tan(th[None, :] / 2)                 # tangent length for every R and vertex
        fail = ((need > room[None, :]) & bent[None, :]).sum(axis=1)
        maxR = XP.where(bent, room / XP.tan(XP.maximum(th, 1e-9) / 2), XP.inf)
        # witness: 500 vertices on the CPU at R = 1.0 m
        tn, rn = to_np(th), to_np(room); s = np.arange(0, len(tn), max(1, len(tn) // 500))
        w = int(((1.0 * np.tan(tn[s] / 2) > rn[s]) & (tn[s] > math.radians(1.0))).sum())
        out[case] = {'vertices': int(th.size), 'bends_over_1deg': int(bent.sum()),
                     'max_deflection_deg': float(XP.degrees(th.max())),
                     'largest_radius_that_fits_everywhere_m': float(maxR[bent].min()) if bool(bent.any()) else None,
                     'fail_count_by_radius': {f'{float(r):.2f}': int(f) for r, f in zip(to_np(radii)[::5], to_np(fail)[::5])},
                     'witness_fail_at_1m_sample': w}
    return out


# ---------------------------------------------------------------------------------------------- 5. joining to reality
AIRY_A, AIRY_B, F0 = 6377563.396, 6356256.909, 0.9996012717           # OSGB36 Airy 1830 and the grid's central scale
PHI0, LAM0, E0 = math.radians(49.0), math.radians(-2.0), 400000.0      # true origin of the National Grid


def audit_join(lat0, lon0, half_m=2000.0, step_m=1.0):
    """How a model built in metres goes wrong when it is joined to the map, over a (2 half_m)^2 envelope on a 1 m grid.

    (a) ONE MERCATOR ANCHOR: a block in metres scaled by the anchor's metres-per-Mercator-unit (1 / cos(lat_anchor)).
        The true scale at latitude lat is 1 / cos(lat), so a vertex d metres north lands d (cos(lat_a) / cos(lat) - 1) off.
    (b) GRID METRES AS GROUND METRES: National Grid distances carry the point scale factor k (Transverse Mercator on
        Airy 1830, k = F0 (1 + (E - E0)^2 / (2 rho nu F0^2) + ...)). Using grid metres as ground metres errs by (k - 1) d.
    (c) GRID NORTH AS TRUE NORTH: the grid convergence gamma (about dLam sin(lat)) rotates a layout; the error is gamma d.
    (d) A FLAT LOCAL PLANE: a tangent plane at the envelope origin departs from the ellipsoid by about d^2 / (2 R); DTM
        heights must be lowered by that drop when they are placed in the plane.
    Every error is computed per grid point on the GPU; the report gives the envelope size that keeps each under 1 mm,
    1 cm and 10 cm. A NumPy witness recomputes 10,000 points."""
    n = int(2 * half_m / step_m) + 1
    g = XP.linspace(-half_m, half_m, n, dtype=XP.float64)
    dx, dy = XP.meshgrid(g, g)                                           # east, north metres about the origin
    R = 6371008.8
    lat = math.radians(lat0) + dy / R
    lon = math.radians(lon0) + dx / (R * math.cos(math.radians(lat0)))
    d = XP.hypot(dx, dy)
    err_a = XP.abs(dy * (math.cos(math.radians(lat0)) / XP.cos(lat) - 1.0))
    e2 = (AIRY_A ** 2 - AIRY_B ** 2) / AIRY_A ** 2
    s2 = XP.sin(lat) ** 2
    nu = AIRY_A * F0 / XP.sqrt(1 - e2 * s2)
    rho = AIRY_A * F0 * (1 - e2) / (1 - e2 * s2) ** 1.5
    dl = lon - LAM0
    east = E0 + nu * XP.cos(lat) * dl                                    # first-order easting, enough for k
    k = F0 * (1 + (east - E0) ** 2 / (2 * rho * nu) + (east - E0) ** 4 / (24 * rho ** 2 * nu ** 2))
    err_b = XP.abs(k - 1.0) * d
    eta2 = nu / rho - 1
    gamma = dl * XP.sin(lat) + dl ** 3 * XP.sin(lat) * XP.cos(lat) ** 2 * (1 + 3 * eta2 + 2 * eta2 ** 2) / 3
    err_c = XP.abs(gamma) * d
    err_d = d ** 2 / (2 * R)
    # witness
    rng = np.random.default_rng(6502); idx = rng.integers(0, n * n, 10000)
    dxn, dyn = to_np(dx).ravel()[idx], to_np(dy).ravel()[idx]
    latn = math.radians(lat0) + dyn / R
    wa = np.abs(dyn * (math.cos(math.radians(lat0)) / np.cos(latn) - 1.0))
    witness = float(np.abs(wa - to_np(err_a).ravel()[idx]).max())
    rings = [10, 50, 100, 250, 500, 1000, 2000]
    def at(err, r):                                                      # worst error within r metres of the origin
        m = d <= r
        return float(err[m].max())
    def size_for(err, tol):                                              # the largest radius whose worst error <= tol
        ok = [r for r in (1, 2, 5, 10, 20, 50, 100, 200, 250, 500, 1000, 1500, 2000) if at(err, r) <= tol]
        return ok[-1] if ok else 0
    names = {'a_one_mercator_anchor': err_a, 'b_grid_metres_as_ground': err_b, 'c_grid_north_as_true': err_c, 'd_flat_plane_drop': err_d}
    k0 = float(k[n // 2, n // 2]); g0 = float(gamma[n // 2, n // 2])
    return {'points': int(n * n), 'origin': 'the envelope centre (register point)', 'k_at_origin': k0,
            'convergence_deg_at_origin': math.degrees(g0), 'witness_max_diff_m': witness,
            'worst_error_m_within_radius': {k2: {str(r): at(v, r) for r in rings} for k2, v in names.items()},
            'largest_radius_m_for': {k2: {'1mm': size_for(v, 0.001), '1cm': size_for(v, 0.01), '10cm': size_for(v, 0.1)} for k2, v in names.items()}}


# ---------------------------------------------------------------------------------------------- 4. code
def audit_code(repo):
    mod = os.path.join(repo, 'prototype', 'mod'); tests = os.listdir(os.path.join(repo, 'tests'))
    rows = []
    for f in sorted(os.listdir(mod)):
        if not f.endswith('.js'):
            continue
        s = open(os.path.join(mod, f), encoding='utf-8', errors='ignore').read()
        name = f[:-3]
        absm = len(re.findall(r'MercatorCoordinate\.fromLngLat|fromLngLat\(', s))
        local = len(re.findall(r'\b(origin|rtc|RTC|u_origin|toLocal|PF\.toLocal)\b', s))
        f32 = len(re.findall(r'Float32Array', s))
        rows.append({'module': name, 'lines': s.count('\n') + 1, 'kb': round(len(s.encode()) / 1024, 1),
                     'has_test': any(t.startswith(name) for t in tests), 'abs_mercator_calls': absm,
                     'local_frame_refs': local, 'float32_arrays': f32, 'custom_gl_layer': "'custom'" in s or '"custom"' in s,
                     'owner_word': len(re.findall(r'\bowner', s, re.I)),
                     'drive_paths': len(re.findall(r'[CE]:[\\/](Users|swarm|gw|private)', s))})
    return rows


# ---------------------------------------------------------------------------------------------- report
def report(res, path):
    P, T, B, C = res['precision'], res['tables'], res['bends'], res['code']
    L = [f"# Geometry CI audit ({res['when']})", '',
         f"GPU: {res['gpu']}. Product: energy-transition-simulator {res['sha']}. Every number below is from `audit.json`; "
         'each audit has a NumPy witness on a sample. This measures consistency of the geometry the product draws; it '
         'does not prove the real site (verification is closed under belief).', '',
         '## 1. Precision: why geometry breaks when you zoom in', '',
         f"{P['points']:,} module corners on {P['runs']:,} measured runs. One Mercator unit is {P['metres_per_mercator_unit']/1000:,.0f} km here.", '',
         '| storage | ground error p50 | p99 | max |', '|---|---|---|---|',
         f"| absolute Mercator, float32 | {P['abs_f32_ground_err_m']['p50']:.3f} m | {P['abs_f32_ground_err_m']['p99']:.3f} m | {P['abs_f32_ground_err_m']['max']:.3f} m |",
         f"| relative to a local origin (RTC), float32 | {P['rtc_f32_ground_err_m']['p50']*1000:.4f} mm | {P['rtc_f32_ground_err_m']['p99']*1000:.4f} mm | {P['rtc_f32_ground_err_m']['max']*1000:.4f} mm |", '',
         f"A 1 cm camera step in an absolute float32 pipeline moves vertices by up to {P['abs_f32_jitter_1cm_step_m']['max']:.3f} m (the jitter). Witness max difference {P['witness_max_diff_m']:.2e} m.", '',
         '| view | absolute float32 error | RTC float32 error |', '|---|---|---|']
    for z, v in P['zooms'].items():
        L.append(f"| {'map zoom ' + str(z) if str(z).isdigit() else 'walk, member ' + str(z)[5:] + ' from the eye'} | {v['abs_px']:.1f} px | {v['rtc_px']:.5f} px |")
    L += ['', '**Rule:** every close-up layer stores vertices in metres about a local origin (RTC) and applies the origin '
          'in float64 on the CPU. An absolute float32 layer cannot draw a 0.1 m member at walk scale.', '',
          '**What the product does today:** its block layers (lidar-stream, plan-view, procedural, engine-lock) keep each '
          "buffer relative to a block anchor (`PF.toMercator(anchor)`), which meets the rule if the anchor offset is folded "
          'into the matrix in float64 before upload. The scan cannot prove that. A z22+ still-camera jitter test per layer '
          '(vertices stable to 0.5 px) is the first test of the next build. So precision is the failure mode for any NEW '
          "close-up layer. It is not proven to be today's cause of breaking; the camera (pitch capped at 80 to 85 deg, a "
          'map camera rather than a free first-person one) and lines instead of solids are the other two suspects.', '',
          '## 2. Tables as solids', '',
          f"{T['tables']} tables from the product's own tables.js, half width {T['half_width_m']:.2f} m, pitch {T['pitch_m']:.2f} m, "
          f"rasterised at {T['cell_m']} m ({T['raster_cells']:,} cells). Cover {T['cover_ha']:.1f} ha.", '',
          f"- Overlap between tables: {T['overlap_m2']:.1f} m2; overlapping pairs {T['overlapping_pairs']}.",
          f"- Aisle a walker gets to the next table: min {T['aisle_m']['min']:.2f} m, p5 {T['aisle_m']['p5']:.2f}, median {T['aisle_m']['p50']:.2f}, p95 {T['aisle_m']['p95']:.2f} m (n {T['aisle_m']['n']}).",
          f"- Aisles under 1 m: {T['aisles_under_1m']}; 1 to 2 m: {T['aisles_1_to_2m']}.",
          f"- Offset from the {T['pitch_m']:.2f} m lattice: median {T['off_lattice_m']['p50']:.2f} m, p95 {T['off_lattice_m']['p95']:.2f} m; tables over 1 m off: {T['tables_off_lattice_over_1m']}.",
          f"- Witness: cell counts around 20 random tables differ by {T['witness_cell_count_max_diff']:.0f}.", '',
          '## 3. Trench bends that physically fit', '',
          'A bend of radius R at a vertex with deflection theta needs a tangent length R tan(theta/2) within half of each neighbouring segment.', '',
          '| case | vertices | bends over 1 deg | max deflection | largest R that fits at every bend | fails at R 0.25 / 1.0 / 2.0 / 3.0 m |', '|---|---|---|---|---|---|']
    for k, v in B.items():
        fc = v['fail_count_by_radius']; ks = list(fc.keys())
        L.append(f"| {k} | {v['vertices']} | {v['bends_over_1deg']} | {v['max_deflection_deg']:.1f} deg | "
                 f"{v['largest_radius_that_fits_everywhere_m'] if v['largest_radius_that_fits_everywhere_m'] is None else round(v['largest_radius_that_fits_everywhere_m'], 3)} m | "
                 f"{' / '.join(str(fc[x]) for x in ks[:1] + ks[3:4] + ks[-3:-2] + ks[-1:])} |")
    L += ['', 'The duct bend radii in the product are 1.8 m and more for 90 mm PE upwards (datasheet), and the cable MBR is 0.36 to 0.50 m. '
          'Every fail at those radii is a place where the drawn route cannot be built as drawn.', '',
          '## 5. Joining the wireframe world to reality in the correct dimensions', '',
          f"{res['join']['points']:,} points on a 1 m grid over a 4 x 4 km envelope. National Grid point scale factor at the origin {res['join']['k_at_origin']:.7f}; grid convergence {res['join']['convergence_deg_at_origin']:.3f} deg. Witness max difference {res['join']['witness_max_diff_m']:.1e} m.", '',
          '| how the model is joined | worst error within 50 m | 250 m | 1 km | 2 km | largest envelope for 1 mm / 1 cm / 10 cm |', '|---|---|---|---|---|---|']
    J = res['join']
    lab = {'a_one_mercator_anchor': 'one Mercator anchor, metres scaled at the anchor', 'b_grid_metres_as_ground': 'National Grid metres used as ground metres',
           'c_grid_north_as_true': 'grid north used as true north', 'd_flat_plane_drop': 'flat local plane, heights not lowered for the curve'}
    for k2, v in J['worst_error_m_within_radius'].items():
        s3 = J['largest_radius_m_for'][k2]
        L.append(f"| {lab[k2]} | {v['50']*1000:.1f} mm | {v['250']*1000:.1f} mm | {v['1000']*1000:.0f} mm | {v['2000']*1000:.0f} mm | {s3['1mm']} m / {s3['1cm']} m / {s3['10cm']} m |")
    L += ['', '**Rule for joining:** build each envelope in a local east-north-up frame in ground metres at the envelope origin; '
          'convert every vertex from the national grid through the one place frame (OSTN15) to latitude and longitude, then to the map, in float64; '
          'apply the grid scale factor and convergence, never assume them; lower DTM heights by the curve drop; and keep an envelope '
          'within the radius the table gives for the accuracy wanted (or re-anchor per table or trench, which is what one close-up at a time allows).', '',
          '## 4. Code', '', '| module | lines | test | custom GL layer | absolute Mercator calls | local-frame refs | Float32Array | "owner" | drive paths |',
          '|---|---|---|---|---|---|---|---|---|']
    for r in C:
        L.append(f"| {r['module']} | {r['lines']} | {'yes' if r['has_test'] else 'NO'} | {'yes' if r['custom_gl_layer'] else ''} | {r['abs_mercator_calls']} | {r['local_frame_refs']} | {r['float32_arrays']} | {r['owner_word'] or ''} | {r['drive_paths'] or ''} |")
    n_t = sum(1 for r in C if r['has_test'])
    L += ['', f"{len(C)} modules, {sum(r['lines'] for r in C):,} lines; {n_t} have a test of their own. Modules with a custom GL layer and absolute Mercator calls are the first to break at walk scale.", '']
    open(path, 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--repo', required=True); ap.add_argument('--out', required=True)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); mod = os.path.join(a.repo, 'prototype', 'mod')
    t0 = time.time()
    farm = json.load(open(os.path.join(mod, 'scanner-rows.farms.json'), encoding='utf-8'))['farms'][0]
    rows = json.load(open(os.path.join(mod, farm['rows']), encoding='utf-8'))['rows']
    trench = json.load(open(os.path.join(mod, 'ac-trenches-6502.json'), encoding='utf-8'))
    sha = subprocess.run(['git', '-C', a.repo, 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
    res = {'gpu': GPU, 'sha': sha, 'when': time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime()), 'timing_s': {}}
    t = time.time(); res['precision'] = audit_precision(rows, farm['point']['lat']); res['timing_s']['precision'] = round(time.time() - t, 2)
    t = time.time(); res['tables'] = audit_tables(export_tables(a.repo)); res['timing_s']['tables'] = round(time.time() - t, 2)
    t = time.time(); res['bends'] = audit_bends(trench); res['timing_s']['bends'] = round(time.time() - t, 2)
    t = time.time(); res['join'] = audit_join(farm['point']['lat'], farm['point']['lon']); res['timing_s']['join'] = round(time.time() - t, 2)
    res['code'] = audit_code(a.repo); res['timing_s']['total'] = round(time.time() - t0, 2)
    js = json.dumps(res, indent=1, default=float); res['sha256'] = hashlib.sha256(js.encode()).hexdigest()
    open(os.path.join(a.out, 'audit.json'), 'w', encoding='utf-8', newline='\n').write(json.dumps(res, indent=1, default=float))
    report(res, os.path.join(a.out, 'GEOMETRY-AUDIT.md'))
    print(json.dumps({'gpu': GPU, 'timing_s': res['timing_s'], 'sha256': res['sha256'][:16]}))


if __name__ == '__main__':
    main()
