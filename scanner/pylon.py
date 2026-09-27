"""Deterministic lattice-pylon wireframe skeleton (procedural fill, not a measurement).

lattice_pylon(voltage_class, bracing='K'|'X', ...) returns (lines, model):
  lines: list of ((x, y, z), (x, y, z)) segments in metres, tower centre at origin, z up, arms along +/-x.
  model: dict of every dimension, each as {'value', 'tag', 'source'} per the provenance rule in docs-SCANNER.md,
         plus counts and the insulator drop points.

Geometry:
  - 4 legs taper linearly from a square base (half-width b at z=0) to a square waist (half-width w at z=h_waist),
    then run vertical at half-width w up to the top (z=h_top). Body: n_body panels below the waist, n_top above.
  - Each panel has 4 leg segments, 4 horizontals at its top level, and on each of the 4 faces 2 bracing members:
      X: both diagonals of the face.
      K: from the midpoint of one leg to the bottom and top of the opposite leg (the letter K: two arms meeting
         on the stroke). Every bracing endpoint lies on a leg.
  - Base: 4 horizontals at z=0.
  - Cross-arms: n_arms_per_side levels on each side (3 per side = double circuit), attached to leg nodes on the
    vertical top section. Each arm: 2 upper chords + 2 lower chords to a tip on the x axis, plus 1 insulator drop.
  Line count = panels * (4 + 4 + 8) + 4 + 2 * n_arms_per_side * 5.

PROVENANCE: every height/width below is ASSUMED (illustrative, not from a published table; to be replaced by cited
values). No internet was available when this was written and no table was consulted. Sources the local team should
cite when replacing these values (to be checked, not quoted here):
  - The network operator's tower-type design schedules for the relevant suite (e.g. the L-series lattice suites used
    on the GB 275/400 kV system and the standard 132 kV suites), with issue/revision.
  - BS EN 50341 (overhead lines exceeding AC 1 kV) and its GB National Normative Aspects, for clearances.
  - ENA Technical Specification 43-8 (overhead line clearances) for ground and phase clearances.
  - Measured data (LiDAR heights, survey drawings) for the specific tower, which override any type value.
"""

ASSUMED = 'assumed'
ASSUMED_SRC = 'assumed (illustrative, not from a published table; to be replaced by cited values)'

# Illustrative only. Keys: h_top, h_waist, base_half, waist_half, arm_len (list, bottom->top), arm_depth,
# insulator_len, n_body, n_top. Metres.
_ASSUMED_DIMS = {
    132: dict(h_top=27.0, h_waist=14.0, base_half=2.6, waist_half=0.9, arm_len=[3.4, 3.8, 3.4],
              arm_depth=1.2, insulator_len=1.8, n_body=4, n_top=4),
    275: dict(h_top=42.0, h_waist=22.0, base_half=4.0, waist_half=1.3, arm_len=[5.4, 6.0, 5.4],
              arm_depth=1.8, insulator_len=3.2, n_body=5, n_top=5),
    400: dict(h_top=50.0, h_waist=26.0, base_half=4.8, waist_half=1.5, arm_len=[6.3, 7.0, 6.3],
              arm_depth=2.1, insulator_len=4.0, n_body=6, n_top=6),
}

CORNERS = [(1, 1), (-1, 1), (-1, -1), (1, -1)]      # leg order, counter-clockwise
FACES = [(0, 1), (1, 2), (2, 3), (3, 0)]            # each face spans two adjacent legs


def half_width(z, d):
    """Leg half-width at height z (linear taper to waist, then vertical)."""
    if z >= d['h_waist']:
        return d['waist_half']
    t = z / d['h_waist']
    return d['base_half'] + t * (d['waist_half'] - d['base_half'])


def leg_point(i, z, d):
    sx, sy = CORNERS[i]
    h = half_width(z, d)
    return (sx * h, sy * h, z)


def panel_levels(d):
    zb = [d['h_waist'] * k / d['n_body'] for k in range(d['n_body'] + 1)]
    zt = [d['h_waist'] + (d['h_top'] - d['h_waist']) * k / d['n_top'] for k in range(1, d['n_top'] + 1)]
    return zb + zt


def arm_levels(d, n):
    """Arm heights: on the upper panel nodes of the vertical top section, skipping the topmost (earthwire peak)."""
    zl = panel_levels(d)[d['n_body'] + 1:-1]         # nodes strictly above waist, below top
    step = max(1, len(zl) // n)
    zs = zl[-n * step::step][:n] if len(zl) >= n else zl
    if len(zs) != n:
        raise ValueError('not enough top-section panels for the requested arms')
    return zs


def lattice_pylon(voltage_class, bracing='K', n_arms_per_side=3, dims=None):
    if bracing not in ('K', 'X'):
        raise ValueError("bracing must be 'K' or 'X'")
    if dims is None:
        if voltage_class not in _ASSUMED_DIMS:
            raise ValueError(f'no assumed dimensions for {voltage_class} kV; supply dims=')
        d = dict(_ASSUMED_DIMS[voltage_class])
        src_tag, src = ASSUMED, ASSUMED_SRC
    else:
        d = dict(dims)
        src_tag, src = d.pop('tag', ASSUMED), d.pop('source', ASSUMED_SRC)
    arm_len = list(d['arm_len'])
    if len(arm_len) != n_arms_per_side:
        arm_len = [arm_len[min(k, len(arm_len) - 1)] for k in range(n_arms_per_side)]

    lines = []
    zs = panel_levels(d)
    for i, j in FACES:                                       # base horizontals
        lines.append((leg_point(i, 0.0, d), leg_point(j, 0.0, d)))
    for z0, z1 in zip(zs[:-1], zs[1:]):
        zm = 0.5 * (z0 + z1)
        for i in range(4):                                   # leg segments
            lines.append((leg_point(i, z0, d), leg_point(i, z1, d)))
        for i, j in FACES:                                   # horizontals at panel top
            lines.append((leg_point(i, z1, d), leg_point(j, z1, d)))
        for i, j in FACES:                                   # face bracing, 2 per face
            if bracing == 'X':
                lines.append((leg_point(i, z0, d), leg_point(j, z1, d)))
                lines.append((leg_point(j, z0, d), leg_point(i, z1, d)))
            else:
                lines.append((leg_point(i, zm, d), leg_point(j, z0, d)))
                lines.append((leg_point(i, zm, d), leg_point(j, z1, d)))

    w, depth = d['waist_half'], d['arm_depth']
    za = arm_levels(d, n_arms_per_side)
    drops = []
    for side in (1, -1):
        for k, z in enumerate(za):
            tip = (side * (w + arm_len[k]), 0.0, z)
            for sy in (1, -1):
                lines.append(((side * w, sy * w, z), tip))           # upper chord (leg node)
                lines.append(((side * w, sy * w, z - depth), tip))   # lower chord (on vertical leg)
            drop = (tip[0], 0.0, z - d['insulator_len'])
            lines.append((tip, drop))
            drops.append({'side': side, 'level': k, 'tip': tip, 'drop': drop})

    n_panels = d['n_body'] + d['n_top']
    expected = n_panels * 16 + 4 + 2 * n_arms_per_side * 5
    assert len(lines) == expected

    def f(v):
        return {'value': v, 'tag': src_tag, 'source': src}

    model = {
        'type': 'lattice_pylon',
        'voltage_kv': {'value': voltage_class, 'tag': 'assumed', 'source': 'caller-supplied class'},
        'bracing': {'value': bracing, 'tag': 'assumed', 'source': 'caller choice'},
        'height_top_m': f(d['h_top']), 'height_waist_m': f(d['h_waist']),
        'base_width_m': f(2 * d['base_half']), 'waist_width_m': f(2 * d['waist_half']),
        'arm_lengths_m': f(arm_len), 'arm_depth_m': f(depth), 'insulator_length_m': f(d['insulator_len']),
        'n_body_panels': f(d['n_body']), 'n_top_panels': f(d['n_top']),
        'n_panels': {'value': n_panels, 'tag': 'derived', 'source': 'n_body + n_top'},
        'arm_heights_m': {'value': za, 'tag': 'derived', 'source': 'top-section panel nodes'},
        'n_lines': {'value': len(lines), 'tag': 'derived',
                    'source': 'panels*16 + 4 + 2*arms_per_side*5'},
        'insulator_drops': {'value': drops, 'tag': 'derived', 'source': 'arm tip minus insulator length'},
        'n_circuits': {'value': 2 if n_arms_per_side == 3 else None, 'tag': 'assumed',
                       'source': '3 arms per side read as double circuit'},
        'procedural': True,
    }
    return lines, model
