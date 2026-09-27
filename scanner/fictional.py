"""Fictional parametric design proposals: deterministic site models built from stated parameters only.

Nothing here is measured, derived from imagery or estimated from a rule. Every numeric value is wrapped as
{'value': v, 'unit': u, 'provenance': 'assumed (design proposal)'} (see docs-SCANNER.md, provenance rule, and
docs/SITEMODEL-SCHEMA.md). Each builder returns (model, segments): a plain dict model and a list of 3D line
segments ((x, y, z), (x, y, z)) in local metres (x east, y north, z up from local ground at 0).
Bearings and azimuths are compass degrees: 0 = north, 90 = east.
"""
import math
import numpy as np

PROV = 'assumed (design proposal)'


def val(v, unit):
    """Tag one numeric value with its unit and provenance."""
    return {'value': v, 'unit': unit, 'provenance': PROV}


def _dir(bearing_deg):
    b = math.radians(bearing_deg)
    return (math.sin(b), math.cos(b))


def box(w, d, h, origin=(0.0, 0.0, 0.0)):
    """Rectangular box w (x) by d (y) by h (z), corner at origin. 12 edges."""
    ox, oy, oz = origin
    c = [(ox + i * w, oy + j * d, oz + k * h) for k in (0, 1) for j in (0, 1) for i in (0, 1)]
    idx = [(0, 1), (2, 3), (4, 5), (6, 7), (0, 2), (1, 3), (4, 6), (5, 7), (0, 4), (1, 5), (2, 6), (3, 7)]
    segs = [(c[a], c[b]) for a, b in idx]
    model = {'type': 'box', 'origin': [val(v, 'm') for v in origin],
             'width': val(w, 'm'), 'depth': val(d, 'm'), 'height': val(h, 'm')}
    return model, segs


def solar_block(mw, module_w_wp, module_len_m, module_wid_m, modules_per_table, pitch_m, tilt_deg, azimuth_deg,
                table_rows=2, tables_per_row=None, table_gap_m=0.5, front_h_m=0.8, origin=(0.0, 0.0)):
    """Solar block of fixed-tilt tables. Modules are portrait: table_rows modules up the slope, the rest side by side.
    Tables face azimuth_deg; rows run at azimuth_deg + 90. Row r's front edge lies r * pitch_m behind row 0's
    (measured horizontally along the facing direction), so row spacing equals the pitch exactly."""
    if modules_per_table % table_rows:
        raise ValueError('modules_per_table must be a multiple of table_rows')
    modules_needed = math.ceil(mw * 1e6 / module_w_wp)
    tables = math.ceil(modules_needed / modules_per_table)
    if tables_per_row is None:
        tables_per_row = math.ceil(math.sqrt(tables))
    rows = math.ceil(tables / tables_per_row)
    t_len = (modules_per_table // table_rows) * module_wid_m            # along the row
    slope = table_rows * module_len_m                                     # up the slope
    tilt = math.radians(tilt_deg)
    depth_h = slope * math.cos(tilt)                                      # horizontal footprint depth
    back_h = front_h_m + slope * math.sin(tilt)
    fx, fy = _dir(azimuth_deg)                                            # facing (front) direction
    ax, ay = _dir(azimuth_deg + 90.0)                                     # along-row direction
    ox, oy = origin
    rects, segs = [], []
    for k in range(tables):
        r, i = divmod(k, tables_per_row)
        s = i * (t_len + table_gap_m)
        b = -r * pitch_m                                                  # rows step back from the front
        def pt(u, v, z):  # u along row, v across (positive = toward front), from origin
            return (ox + u * ax + v * fx, oy + u * ay + v * fy, z)
        c = [pt(s, b, front_h_m), pt(s + t_len, b, front_h_m),
             pt(s + t_len, b - depth_h, back_h), pt(s, b - depth_h, back_h)]
        rects.append({'row': val(r, 'index'), 'index': val(i, 'index'), 'corners': [[val(q, 'm') for q in p] for p in c],
                      'front_height': val(front_h_m, 'm'), 'back_height': val(back_h, 'm'),
                      'tilt': val(tilt_deg, 'deg'), 'azimuth': val(azimuth_deg, 'deg')})
        segs += [(c[j], c[(j + 1) % 4]) for j in range(4)]
    model = {'type': 'solar_block', 'target_capacity': val(mw, 'MW'), 'module_rating': val(module_w_wp, 'Wp'),
             'module_length': val(module_len_m, 'm'), 'module_width': val(module_wid_m, 'm'),
             'modules_per_table': val(modules_per_table, 'count'), 'table_rows': val(table_rows, 'count'),
             'pitch': val(pitch_m, 'm'), 'tilt': val(tilt_deg, 'deg'), 'azimuth': val(azimuth_deg, 'deg'),
             'table_gap': val(table_gap_m, 'm'), 'front_height': val(front_h_m, 'm'),
             'origin': [val(v, 'm') for v in origin],
             'table_length': val(t_len, 'm'), 'table_slope_length': val(slope, 'm'),
             'table_depth_horizontal': val(depth_h, 'm'), 'back_height': val(back_h, 'm'),
             'tables': val(tables, 'count'), 'tables_per_row': val(tables_per_row, 'count'),
             'rows': val(rows, 'count'), 'modules': val(tables * modules_per_table, 'count'),
             'capacity': val(tables * modules_per_table * module_w_wp / 1e6, 'MW'),
             'table_rects': rects}
    return model, segs


def solar_block_heights(model, extent, cell):
    """Rasterise a solar_block model to a height-above-ground grid (a DSM minus DTM) for the virtual LiDAR loop.
    extent: a number E (grid covers [0, E] in x and y) or (xmin, ymin, xmax, ymax). Cell centres are sampled.
    Returns (heights[ny, nx], xs, ys); row 0 is ymin (y grows with row index, as in vlidar.rasterise)."""
    if np.isscalar(extent):
        extent = (0.0, 0.0, float(extent), float(extent))
    x0, y0, x1, y1 = extent
    xs = x0 + cell / 2 + cell * np.arange(int(round((x1 - x0) / cell)))
    ys = y0 + cell / 2 + cell * np.arange(int(round((y1 - y0) / cell)))
    X, Y = np.meshgrid(xs, ys)
    H = np.zeros_like(X)
    for t in model['table_rects']:
        c = np.array([[q['value'] for q in p] for p in t['corners']])
        a = c[1, :2] - c[0, :2]; L = np.hypot(*a); a /= L
        e = c[3, :2] - c[0, :2]; D = np.hypot(*e); e /= D
        u = (X - c[0, 0]) * a[0] + (Y - c[0, 1]) * a[1]
        v = (X - c[0, 0]) * e[0] + (Y - c[0, 1]) * e[1]
        on = (u >= 0) & (u <= L) & (v >= 0) & (v <= D)
        h = c[0, 2] + (c[3, 2] - c[0, 2]) * (v / D)
        H = np.where(on, np.maximum(H, h), H)
    return H, xs, ys


def fenced_compound(w, d, fence_h, post_spacing, origin=(0.0, 0.0)):
    """Rectangular fence w by d with posts every post_spacing along the perimeter (corners always posted)."""
    ox, oy = origin
    c = [(ox, oy), (ox + w, oy), (ox + w, oy + d), (ox, oy + d)]
    segs, posts = [], []
    for j in range(4):
        (xa, ya), (xb, yb) = c[j], c[(j + 1) % 4]
        segs.append(((xa, ya, 0.0), (xb, yb, 0.0)))
        segs.append(((xa, ya, fence_h), (xb, yb, fence_h)))
        side = math.hypot(xb - xa, yb - ya)
        n = math.ceil(side / post_spacing - 1e-9)
        for k in range(n):
            f = k / n
            posts.append((xa + f * (xb - xa), ya + f * (yb - ya)))
    segs += [((px, py, 0.0), (px, py, fence_h)) for px, py in posts]
    model = {'type': 'fenced_compound', 'width': val(w, 'm'), 'depth': val(d, 'm'),
             'fence_height': val(fence_h, 'm'), 'post_spacing': val(post_spacing, 'm'),
             'origin': [val(v, 'm') for v in origin],
             'perimeter': val(2 * (w + d), 'm'), 'area': val(w * d, 'm2'), 'posts': val(len(posts), 'count')}
    return model, segs


def cable_route(start, end, trench_depth_m, trench_width_m):
    """Straight cable route start->end (x, y) with a rectangular trench; cross-section drawn at both ends."""
    (xa, ya), (xb, yb) = start, end
    L = math.hypot(xb - xa, yb - ya)
    ux, uy = (xb - xa) / L, (yb - ya) / L
    nx, ny = -uy * trench_width_m / 2, ux * trench_width_m / 2
    segs = [((xa, ya, -trench_depth_m), (xb, yb, -trench_depth_m))]
    for (px, py) in (start, end):
        q = [(px + nx, py + ny, 0.0), (px + nx, py + ny, -trench_depth_m),
             (px - nx, py - ny, -trench_depth_m), (px - nx, py - ny, 0.0)]
        segs += [(q[0], q[1]), (q[1], q[2]), (q[2], q[3])]
    for s in (1, -1):
        segs.append(((xa + s * nx, ya + s * ny, 0.0), (xb + s * nx, yb + s * ny, 0.0)))
    model = {'type': 'cable_route', 'start': [val(v, 'm') for v in start], 'end': [val(v, 'm') for v in end],
             'trench_depth': val(trench_depth_m, 'm'), 'trench_width': val(trench_width_m, 'm'),
             'length': val(L, 'm'), 'bearing': val(math.degrees(math.atan2(ux, uy)) % 360, 'deg'),
             'trench_volume': val(L * trench_depth_m * trench_width_m, 'm3')}
    return model, segs


def pylon_row(start, bearing, span_m, count, height_m=50.0):
    """count pylons from start along bearing, span_m apart; masts plus one conductor between tops."""
    bx, by = _dir(bearing)
    pts = [(start[0] + k * span_m * bx, start[1] + k * span_m * by) for k in range(count)]
    segs = [((x, y, 0.0), (x, y, height_m)) for x, y in pts]
    segs += [((pts[k][0], pts[k][1], height_m), (pts[k + 1][0], pts[k + 1][1], height_m)) for k in range(count - 1)]
    model = {'type': 'pylon_row', 'start': [val(v, 'm') for v in start], 'bearing': val(bearing, 'deg'),
             'span': val(span_m, 'm'), 'count': val(count, 'count'), 'height': val(height_m, 'm'),
             'positions': [[val(x, 'm'), val(y, 'm')] for x, y in pts],
             'route_length': val(span_m * (count - 1), 'm')}
    return model, segs
