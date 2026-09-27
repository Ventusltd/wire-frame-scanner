"""Hard known-answer cases: synthetic sites whose row direction and pitch are fixed by construction, pushed into
conditions where the scanner core is expected to struggle. Every value here is synthetic; nothing is measured.

Two paths, the same ones the existing tests use:
  image  : synthetic RGB -> core.panel_mask -> refine_normal(row_normal) -> row_pitch   (tests/test_known_answer.py)
  lidar  : height model -> vlidar.survey -> rasterise DSM, DTM -> (DSM - DTM) > 1 m -> same core calls
           (tests/test_vlidar_loop.py, tests/test_fictional_loop.py; fictional.solar_block where natural)

Tolerances are the existing ones: row direction +/- 1 deg (mod 180), pitch +/- 0.25 m.

Each case carries an expectation. 'pass' cases must pass. 'xfail' cases are KNOWN, documented failures of the
current core (see docs/HARD-CASES.md); they are reported and never fail the run. An xfail that starts passing is
reported as XPASS (good news, not a failure: update the expectation). The script exits 1 only if an expected-pass
case fails (an unexpected regression).

Direction convention: all designed and recovered row directions are compass degrees mod 180 (0 = rows run north,
90 = rows run east), except the image path, which uses the image-x convention of tests/test_known_answer.py.

Run: python tests/test_hard_cases.py
"""
import math, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scanner import core, vlidar, fictional

TOL_PITCH_M, TOL_DIR_DEG = 0.25, 1.0
CELL, HCELL, MARGIN = 0.5, 0.25, 12.0
MPP = 0.746
MOD = dict(module_w_wp=450.0, module_len_m=2.1, module_wid_m=1.1, modules_per_table=24)


def cdiff(a, b):
    d = abs(a - b) % 180
    return min(d, 180 - d)


def rolling(xp, x, y):
    return 5.0 + 1.5 * xp.sin(x / 37.0) + 1.0 * xp.cos(y / 29.0)


# ---------------------------------------------------------------- measurement (core only, unmodified)
def measure_mask(mask, mpp):
    """Row normal and pitch exactly as the existing tests do. Returns (math-angle rows deg mod 180, pitch m)."""
    if not mask.any():
        return None, None
    th = core.refine_normal(np, mask, core.row_normal(np, mask), mpp)
    r = core.row_pitch(np, mask, th, mpp)
    return (math.degrees(th) - 90) % 180, (r[0] * mpp if r else None)


def lidar_measure(H, E, ground=rolling, ppsm=8.0, noise_m=0.05, seed=7, cell=CELL):
    """Height grid H (HCELL cells, row index = y) -> virtual survey -> DSM-DTM > 1 m -> core.
    Returns (compass rows deg mod 180, pitch m)."""
    n = H.shape[0]
    Hx = np.asarray(H, np.float32)
    obj = lambda xp, x, y: xp.asarray(Hx)[xp.clip((y / HCELL).astype(np.int32), 0, n - 1),
                                          xp.clip((x / HCELL).astype(np.int32), 0, n - 1)]
    x, y, first, last = vlidar.survey(np, E, ground, obj, ppsm=ppsm, noise_m=noise_m, seed=seed)
    dsm = vlidar.rasterise(np, x, y, first, E, cell)
    dtm = vlidar.rasterise(np, x, y, last, E, cell)
    got_math, got_p = measure_mask((dsm - dtm) > 1.0, cell)
    return (None if got_math is None else (90 - got_math) % 180), got_p


# ---------------------------------------------------------------- site builders (all synthetic)
def placed_block(mw, pitch, tilt, az, origin_shift=(0.0, 0.0), **kw):
    """fictional.solar_block shifted so its bounding box starts at MARGIN (+ origin_shift). Returns (model, extent)."""
    m, _ = fictional.solar_block(mw, pitch_m=pitch, tilt_deg=tilt, azimuth_deg=az, **MOD, **kw)
    pts = np.array([[q['value'] for q in p][:2] for t in m['table_rects'] for p in t['corners']])
    lo, hi = pts.min(0), pts.max(0)
    m, _ = fictional.solar_block(mw, pitch_m=pitch, tilt_deg=tilt, azimuth_deg=az,
                                 origin=(MARGIN - lo[0] + origin_shift[0], MARGIN - lo[1] + origin_shift[1]), **MOD, **kw)
    return m, float(math.ceil((hi - lo).max() + 2 * MARGIN))


def heights_of(m, E):
    return fictional.solar_block_heights(m, E, HCELL)[0]


def drop_tables(m, keep):
    m = dict(m); m['table_rects'] = [t for k, t in enumerate(m['table_rects']) if keep(k, t)]
    return m


def grid(E):
    xs = HCELL / 2 + HCELL * np.arange(int(round(E / HCELL)))
    return np.meshgrid(xs, xs)


def tracker_heights(E, pitch, width, hub_h, tilt_deg, row_len=None, gap_every=None):
    """Single-axis trackers: rows run north-south (compass 0), torque tubes at x = MARGIN + k*pitch, panels
    `width` m wide across, rotated tilt_deg about the tube (0 = flat) so height ramps E-W across the panel."""
    X, Y = grid(E)
    H = np.zeros_like(X)
    half = width / 2 * math.cos(math.radians(tilt_deg))
    k = 0
    x0 = MARGIN + width / 2
    while x0 + width / 2 <= E - MARGIN:
        d = X - x0
        on = (np.abs(d) <= half) & (Y >= MARGIN) & (Y <= (MARGIN + row_len if row_len else E - MARGIN))
        if gap_every:  # break the row into tracker units with gaps (e.g. 40 m units, 1.5 m gaps)
            on &= ((Y - MARGIN) % gap_every) < gap_every - 1.5
        h = hub_h + d * math.tan(math.radians(tilt_deg))
        H = np.where(on, np.maximum(H, h), H)
        x0 += pitch; k += 1
    return H, k


# ---------------------------------------------------------------- image path (RGB colours)
GRASS, SOIL_DARK, CONCRETE = (70, 110, 50), (58, 52, 48), (150, 150, 145)
PANEL_DARK, PANEL_GREY, PANEL_BRIGHT = (30, 38, 60), (95, 100, 108), (160, 165, 175)


def rgb_farm(bearing_deg, pitch_m, depth_m, panel, background, w=320, h=260, noise_sd=0.0, seed=0):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    th = math.radians(bearing_deg) + math.pi / 2
    off = (xx * math.cos(th) + yy * math.sin(th)) * MPP
    stripes = ((off % pitch_m) < depth_m) & (xx > 10 + 0.15 * yy) & (xx < w - 10) & (yy > 10) & (yy < h - 10 - 0.1 * xx)
    img = np.where(stripes[..., None], np.array(panel, np.float32), np.array(background, np.float32))
    if noise_sd:
        img = img + np.random.default_rng(seed).normal(0, noise_sd, img.shape)
    return np.clip(img, 0, 255)


def image_case(bearing, pitch, depth, panel, bg, noise_sd=0.0):
    got_b, got_p = measure_mask(core.panel_mask(np, rgb_farm(bearing, pitch, depth, panel, bg, noise_sd=noise_sd)), MPP)
    return bearing, pitch, got_b, got_p


def binary_farm_case(bearing, pitch, depth, flip):
    """Pure mask noise (test_known_answer.farm with a higher flip rate)."""
    yy, xx = np.mgrid[0:260, 0:320].astype(np.float32)
    th = math.radians(bearing) + math.pi / 2
    off = (xx * math.cos(th) + yy * math.sin(th)) * MPP
    outline = (xx > 10 + 0.15 * yy) & (xx < 310) & (yy > 10) & (yy < 250 - 0.1 * xx)
    m = ((off % pitch) < depth) & outline
    m ^= (np.random.default_rng(0).random(m.shape) < flip) & outline
    got_b, got_p = measure_mask(m, MPP)
    return bearing, pitch, got_b, got_p


# ---------------------------------------------------------------- the cases
def fict_case(mw, pitch, tilt, az, ground=rolling, noise_m=0.05, ppsm=8.0, edit=None, extra=None, cell=CELL,
              as_built=None, **kw):
    m, E = placed_block(mw, pitch, tilt, az, **kw)
    if edit:
        m = edit(m)
    H = heights_of(m, E)
    if extra:
        H = extra(H, E)
    got_d, got_p = lidar_measure(H, E, ground=ground, ppsm=ppsm, noise_m=noise_m, cell=cell)
    return (az + 90) % 180, (as_built or pitch), got_d, got_p


def mixed_case(p1, p2, az1, az2, part=None):
    """Two fictional blocks side by side (west: p1/az1, east: p2/az2), 30 m apart, on one site.
    part=None measures the whole-site mask (one pitch expected to fit both: it cannot); part=0/1 crops each
    block's half of the site first (what a per-block pipeline would do)."""
    a, Ea = placed_block(0.5, p1, 25.0, az1, tables_per_row=5)
    pa = np.array([[q['value'] for q in p][:2] for t in a['table_rects'] for p in t['corners']])
    b, Eb = placed_block(0.5, p2, 25.0, az2, tables_per_row=5, origin_shift=(pa[:, 0].max() + 30.0 - MARGIN, 0.0))
    pb = np.array([[q['value'] for q in p][:2] for t in b['table_rects'] for p in t['corners']])
    E = float(math.ceil(max(pb[:, 0].max(), pb[:, 1].max(), pa[:, 1].max()) + MARGIN))
    H = np.maximum(heights_of(a, E), heights_of(b, E))
    split = pa[:, 0].max() + 15.0
    X, _ = grid(E)
    if part == 0:
        H = np.where(X < split, H, 0.0)
    elif part == 1:
        H = np.where(X >= split, H, 0.0)
    got_d, got_p = lidar_measure(H, E)
    if part == 1:
        return (az2 + 90) % 180, p2, got_d, got_p
    return (az1 + 90) % 180, p1, got_d, got_p


def tracker_case(pitch, tilt, width=2.2, hub_h=2.0, noise_m=0.05, gap_every=None):
    E = 150.0
    H, _ = tracker_heights(E, pitch, width, hub_h, tilt, gap_every=gap_every)
    got_d, got_p = lidar_measure(H, E, noise_m=noise_m)
    return 0.0, pitch, got_d, got_p


def objects_between(n, size=2.0, h=2.5, seed=3):
    """n synthetic boxes (inverters, cabins) dropped at random, including between rows."""
    def f(H, E):
        rng = np.random.default_rng(seed); X, Y = grid(E); H = H.copy()
        for _ in range(n):
            cx, cy = rng.uniform(MARGIN, E - MARGIN, 2)
            H = np.where((np.abs(X - cx) < size / 2) & (np.abs(Y - cy) < size / 2), np.maximum(H, h), H)
        return H
    return f


def tree_line(width=6.0, h=9.0):
    """A hedge/tree line crossing the block diagonally (shading object taller than the tables)."""
    def f(H, E):
        X, Y = grid(E)
        return np.where(np.abs((X - Y) / math.sqrt(2)) < width / 2, np.maximum(H, h), H)
    return f


def shade_strip(width=10.0):
    """An access track / shading gap: all tables removed in a strip across the rows."""
    def f(H, E):
        X, Y = grid(E)
        return np.where(np.abs(X - E / 2) < width / 2, 0.0, H)
    return f


def few_rows(rows, pitch, tpr=6):
    mw = rows * tpr * 24 * 450 / 1e6 - 1e-6
    return lambda: fict_case(mw, pitch, 25.0, 180.0, tables_per_row=tpr)


def plane(sx, sy, base=20.0):
    return lambda xp, x, y: base + sx * x + sy * y


def rough(amp, wl):
    return lambda xp, x, y: 20.0 + amp * xp.sin(x / wl) * xp.cos(y / (0.7 * wl)) + 0.3 * x


CASES = [
    # (group, name, fn, expect)
    ('contrast', 'dark panels on grass (baseline)', lambda: image_case(17.0, 7.5, 4.0, PANEL_DARK, GRASS), 'pass'),
    ('contrast', 'dark panels on grass, pixel noise sd 12', lambda: image_case(17.0, 7.5, 4.0, PANEL_DARK, GRASS, 12.0), 'pass'),
    ('contrast', 'grey panels (luma ~98) on grass', lambda: image_case(17.0, 7.5, 4.0, PANEL_GREY, GRASS), 'xfail'),
    ('contrast', 'bright/glinting panels on grass', lambda: image_case(63.0, 9.0, 4.5, PANEL_BRIGHT, GRASS), 'xfail'),
    ('contrast', 'dark panels on dark bare soil', lambda: image_case(17.0, 7.5, 4.0, PANEL_DARK, SOIL_DARK), 'xfail'),
    ('contrast', 'dark panels on concrete/gravel', lambda: image_case(135.0, 8.2, 4.4, PANEL_DARK, CONCRETE), 'pass'),

    ('broken', '20% of tables missing at random', lambda: fict_case(0.9, 7.5, 25.0, 160.0,
        edit=lambda m: drop_tables(m, lambda k, t: np.random.default_rng(k).random() > 0.2)), 'pass'),
    ('broken', '45% of tables missing at random', lambda: fict_case(0.9, 7.5, 25.0, 160.0,
        edit=lambda m: drop_tables(m, lambda k, t: np.random.default_rng(k + 100).random() > 0.45)), 'pass'),
    ('broken', 'every 3rd row missing (rows at 7.5 m, 22.5 m super-period)', lambda: fict_case(0.9, 7.5, 25.0, 160.0,
        edit=lambda m: drop_tables(m, lambda k, t: t['row']['value'] % 3 != 2)), 'xfail'),
    ('broken', 'every 2nd row missing (as built: 15 m pitch)', lambda: fict_case(0.9, 7.5, 25.0, 160.0, as_built=15.0,
        edit=lambda m: drop_tables(m, lambda k, t: t['row']['value'] % 2 == 0)), 'xfail'),
    ('broken', 'wide 6 m gaps between tables', lambda: fict_case(0.8, 9.0, 30.0, 213.0, table_gap_m=6.0), 'pass'),

    ('slope', 'steep 30% slope along rows', lambda: fict_case(0.8, 7.5, 25.0, 180.0, ground=plane(0.30, 0.0)), 'pass'),
    ('slope', 'steep 30% slope across rows', lambda: fict_case(0.8, 7.5, 25.0, 180.0, ground=plane(0.0, 0.30)), 'pass'),
    ('slope', 'cross-slope 25% + 25% diagonal', lambda: fict_case(0.8, 9.0, 25.0, 213.0, ground=plane(0.25, 0.25)), 'pass'),
    ('slope', 'very steep 60% slope across rows', lambda: fict_case(0.8, 7.5, 25.0, 180.0, ground=plane(0.0, 0.60)), 'pass'),
    ('slope', 'rough hills (8 m amplitude, 20 m wavelength)', lambda: fict_case(0.8, 7.5, 25.0, 160.0, ground=rough(8.0, 20.0)), 'pass'),

    ('mixed', 'two blocks 6 m + 10 m pitch, whole site (vs 6 m)', lambda: mixed_case(6.0, 10.0, 180.0, 180.0), 'xfail'),
    ('mixed', 'two blocks 6 m + 10 m pitch, west block cropped', lambda: mixed_case(6.0, 10.0, 180.0, 180.0, part=0), 'pass'),
    ('mixed', 'two blocks 6 m + 10 m pitch, east block cropped', lambda: mixed_case(6.0, 10.0, 180.0, 180.0, part=1), 'pass'),
    ('mixed', 'two blocks 5 m + 10 m (harmonic), whole site (vs 5 m)', lambda: mixed_case(5.0, 10.0, 180.0, 180.0), 'xfail'),
    ('mixed', 'two blocks 7.5 m @ az180 + 7.5 m @ az150, whole site', lambda: mixed_case(7.5, 7.5, 180.0, 150.0), 'xfail'),
    ('mixed', 'two blocks 8 m @ az180 + 8 m @ az210, each cropped (az210)', lambda: mixed_case(8.0, 8.0, 180.0, 210.0, part=1), 'pass'),

    ('tracker', 'N-S trackers flat, pitch 5.5 m', lambda: tracker_case(5.5, 0.0), 'pass'),
    ('tracker', 'N-S trackers tilted 45 deg E/W, pitch 5.5 m', lambda: tracker_case(5.5, 45.0), 'pass'),
    ('tracker', 'N-S trackers tilted 55 deg, hub 1.6 m, pitch 6 m', lambda: tracker_case(6.0, 55.0, hub_h=1.6), 'pass'),
    ('tracker', 'N-S trackers flat, 40 m units with gaps, pitch 7 m', lambda: tracker_case(7.0, 0.0, gap_every=40.0), 'pass'),
    ('tracker', 'N-S trackers flat, dense pitch 4.2 m (width 2.2 m)', lambda: tracker_case(4.2, 0.0), 'pass'),

    ('objects', '25 inverter/cabin boxes between rows', lambda: fict_case(0.9, 7.5, 25.0, 160.0, extra=objects_between(25)), 'pass'),
    ('objects', '120 boxes between rows', lambda: fict_case(0.9, 7.5, 25.0, 160.0, extra=objects_between(120)), 'pass'),
    ('objects', 'diagonal tree line 6 m wide across block', lambda: fict_case(0.9, 7.5, 25.0, 180.0, extra=tree_line()), 'pass'),
    ('objects', '10 m access track / shading gap across rows', lambda: fict_case(0.9, 7.5, 25.0, 180.0, extra=shade_strip()), 'pass'),

    ('few rows', '3 rows @ 12 m', few_rows(3, 12.0), 'xfail'),
    ('few rows', '4 rows @ 12 m', few_rows(4, 12.0), 'pass'),
    ('few rows', '6 rows @ 12 m', few_rows(6, 12.0), 'pass'),
    ('few rows', '8 rows @ 12 m (known +0.19 m bias)', few_rows(8, 12.0), 'pass'),
    ('few rows', '16 rows @ 12 m', few_rows(16, 12.0, tpr=4), 'pass'),
    ('few rows', '4 rows @ 6 m', few_rows(4, 6.0), 'pass'),
    ('few rows', '3 rows @ 14 m', few_rows(3, 14.0), 'xfail'),

    ('noise', 'mask flip 10% (image path)', lambda: binary_farm_case(63.0, 11.0, 5.5, 0.10), 'pass'),
    ('noise', 'mask flip 20% (image path)', lambda: binary_farm_case(63.0, 11.0, 5.5, 0.20), 'pass'),
    ('noise', 'mask flip 35% (image path)', lambda: binary_farm_case(63.0, 11.0, 5.5, 0.35), 'pass'),
    ('noise', 'LiDAR range noise 0.2 m', lambda: fict_case(0.9, 7.5, 25.0, 160.0, noise_m=0.2), 'pass'),
    ('noise', 'LiDAR range noise 0.4 m', lambda: fict_case(0.9, 7.5, 25.0, 160.0, noise_m=0.4), 'pass'),
    ('noise', 'LiDAR sparse 2 pulse/m2, 0.5 m cells', lambda: fict_case(0.9, 7.5, 25.0, 160.0, ppsm=2.0), 'pass'),
    ('noise', 'LiDAR sparse 1 pulse/m2, 0.5 m cells', lambda: fict_case(0.9, 7.5, 25.0, 160.0, ppsm=1.0), 'xfail'),
    ('noise', 'LiDAR sparse 0.5 pulse/m2, 0.5 m cells', lambda: fict_case(0.9, 7.5, 25.0, 160.0, ppsm=0.5), 'xfail'),
    ('noise', 'LiDAR sparse 1 pulse/m2, 1 m cells', lambda: fict_case(0.9, 7.5, 25.0, 160.0, ppsm=1.0, cell=1.0), 'pass'),
    ('noise', 'LiDAR sparse 0.5 pulse/m2, 1.5 m cells', lambda: fict_case(0.9, 7.5, 25.0, 160.0, ppsm=0.5, cell=1.5), 'pass'),
]


def run():
    out = []
    for group, name, fn, expect in CASES:
        des_d, des_p, got_d, got_p = fn()
        de = None if got_d is None else cdiff(got_d, des_d)
        pe = None if got_p is None else got_p - des_p
        ok = de is not None and pe is not None and de <= TOL_DIR_DEG and abs(pe) <= TOL_PITCH_M
        out.append(dict(group=group, name=name, des_d=des_d, des_p=des_p, got_d=got_d, got_p=got_p,
                        dir_err=de, pitch_err=pe, ok=ok, expect=expect))
    return out


def fmt(v, nd=2):
    return 'None' if v is None else f"{v:.{nd}f}"


if __name__ == '__main__':
    res = run()
    unexpected = 0
    counts = {}
    for r in res:
        if r['ok']:
            tag = 'PASS' if r['expect'] == 'pass' else 'XPASS'
        else:
            tag = 'XFAIL' if r['expect'] == 'xfail' else 'FAIL'
        unexpected += tag == 'FAIL'
        counts[tag] = counts.get(tag, 0) + 1
        print(f"{tag:5s} [{r['group']}] {r['name']}: designed {fmt(r['des_d'], 1)} deg {fmt(r['des_p'])} m"
              f"  ->  recovered {fmt(r['got_d'])} deg {fmt(r['got_p'], 3)} m"
              f"  (err {fmt(r['dir_err'])} deg, {('+' if (r['pitch_err'] or 0) >= 0 else '')}{fmt(r['pitch_err'], 3)} m)")
    print('\n' + ', '.join(f"{k} {v}" for k, v in sorted(counts.items())) + f" of {len(res)} hard cases;"
          f" unexpected failures: {unexpected}")
    print("Synthetic by construction: this measures the scanner against our own generators, not any real site.")
    sys.exit(1 if unexpected else 0)
