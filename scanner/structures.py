"""Tower skeleton from a few measured pins, rule-shaped between them.

Pins are measured points on the radius profile r(z): base radius at z=0, widest radius and its height, and the
total height with its top radius. Each pin carries provenance "measured" and a `source` citation field.
Between pins the profile is a Fritsch-Carlson monotone piecewise cubic (PCHIP), tagged "rule-shaped between pins":
it passes exactly through every pin and never overshoots between them.

Skeleton: floor rings at fixed spacing (circles as n_diagrid segments) and two opposing helical diagrid families
whose nodes are the ring vertices. Lines: rings R*n + diagrid 2*n*(R-1) = n*(3R-2), R = number of rings.
"""
import math
import numpy as np

PIN_TAG = 'measured'
FILL_TAG = 'rule-shaped between pins'


def pchip_slopes(x, y):
    """Fritsch-Carlson derivatives at the knots (monotone-preserving)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    n = x.size
    h = np.diff(x); d = np.diff(y) / h
    m = np.zeros(n)
    if n == 2:
        m[:] = d[0]; return m
    for k in range(1, n - 1):
        if d[k - 1] * d[k] <= 0:
            m[k] = 0.0
        else:  # weighted harmonic mean (Fritsch-Butland form used by PCHIP)
            w1 = 2 * h[k] + h[k - 1]; w2 = h[k] + 2 * h[k - 1]
            m[k] = (w1 + w2) / (w1 / d[k - 1] + w2 / d[k])
    # three-point end slopes, limited to keep monotonicity
    for k, (h0, h1, d0, d1) in ((0, (h[0], h[1], d[0], d[1])), (n - 1, (h[-1], h[-2], d[-1], d[-2]))):
        s = ((2 * h0 + h1) * d0 - h0 * d1) / (h0 + h1)
        if s * d0 <= 0:
            s = 0.0
        elif d0 * d1 <= 0 and abs(s) > abs(3 * d0):
            s = 3 * d0
        m[k] = s
    return m


def pchip_eval(x, y, m, z):
    x = np.asarray(x, float); y = np.asarray(y, float)
    z = np.atleast_1d(np.asarray(z, float))
    i = np.clip(np.searchsorted(x, z, side='right') - 1, 0, x.size - 2)
    h = x[i + 1] - x[i]; t = (z - x[i]) / h
    h00 = (1 + 2 * t) * (1 - t) ** 2; h10 = t * (1 - t) ** 2
    h01 = t * t * (3 - 2 * t); h11 = t * t * (t - 1)
    return h00 * y[i] + h10 * h * m[i] + h01 * y[i + 1] + h11 * h * m[i + 1]


def ring_heights(total_h, spacing):
    k = int(math.floor(total_h / spacing + 1e-9))
    zs = [j * spacing for j in range(k + 1)]
    if total_h - zs[-1] > 1e-9:
        zs.append(total_h)
    return zs


def line_count(n_rings, n_diagrid):
    return n_diagrid * n_rings + 2 * n_diagrid * (n_rings - 1)


def tower_skeleton(pins, ring_spacing_m, n_diagrid):
    """pins: list of dicts {z, r, label, source}. Returns (lines, model). Each line is ((x,y,z),(x,y,z), kind)."""
    pins = sorted(pins, key=lambda p: p['z'])
    zp = np.array([p['z'] for p in pins], float); rp = np.array([p['r'] for p in pins], float)
    if zp[0] != 0.0 or np.any(np.diff(zp) <= 0) or len(pins) < 2:
        raise ValueError('pins need z=0 base and strictly increasing heights')
    m = pchip_slopes(zp, rp)
    profile = lambda z: pchip_eval(zp, rp, m, z)
    zs = ring_heights(zp[-1], ring_spacing_m)
    rs = [float(profile(z)[0]) for z in zs]
    n = int(n_diagrid)
    ang = [2 * math.pi * j / n for j in range(n)]
    node = lambda k, j: (rs[k] * math.cos(ang[j % n]), rs[k] * math.sin(ang[j % n]), zs[k])
    lines = []
    for k in range(len(zs)):
        for j in range(n):
            lines.append((node(k, j), node(k, j + 1), 'ring'))
    for k in range(len(zs) - 1):
        for j in range(n):
            lines.append((node(k, j), node(k + 1, j + 1), 'diagrid+'))
            lines.append((node(k, j), node(k + 1, j - 1), 'diagrid-'))
    model = {
        'pins': [dict(p, provenance=PIN_TAG) for p in pins],
        'profile': {'method': 'Fritsch-Carlson monotone piecewise cubic (PCHIP)', 'provenance': FILL_TAG,
                    'knots_z': zp.tolist(), 'knots_r': rp.tolist(), 'slopes': m.tolist()},
        'rings': [{'z': z, 'r': r, 'provenance': FILL_TAG} for z, r in zip(zs, rs)],
        'ring_spacing_m': ring_spacing_m, 'n_diagrid': n,
        'n_lines': len(lines), 'n_lines_formula': line_count(len(zs), n),
        'label': 'measured at these points, rule-shaped between',
        'profile_fn': profile,
    }
    return lines, model


# Illustrative example only: a generic 100 m tower, not any real building. Sources are placeholders.
EXAMPLE_PINS = [
    {'z': 0.0, 'r': 20.0, 'label': 'base radius', 'source': 'measured (cite source)'},
    {'z': 45.0, 'r': 24.0, 'label': 'widest radius', 'source': 'measured (cite source)'},
    {'z': 100.0, 'r': 6.0, 'label': 'total height, top radius', 'source': 'measured (cite source)'},
]


def render_png(lines, model, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(7, 8))
    ax = fig.add_subplot(111, projection='3d')
    col = {'ring': '#1f5fa8', 'diagrid+': '#c0392b', 'diagrid-': '#8e44ad'}
    for a, b, kind in lines:
        ax.plot([a[0], b[0]], [a[1], b[1]], [a[2], b[2]], color=col[kind], lw=0.6)
    for p in model['pins']:
        ax.scatter([p['r']], [0], [p['z']], color='k', s=25)
    ax.set_xlabel('x (m)'); ax.set_ylabel('y (m)'); ax.set_zlabel('z (m)')
    ax.set_box_aspect((1, 1, 2))
    ax.set_title('Illustrative example: generic 100 m tower\nmeasured at pins (black), rule-shaped between', fontsize=10)
    fig.savefig(path, dpi=120); plt.close(fig)
    return path
