"""Virtual LiDAR: simulate an airborne laser survey of a wireframe site model, on the GPU (CuPy) or the CPU (NumPy).

A site model gives surfaces: the ground (a height function) and solid objects (here, tilted solar tables as planes
between a front edge height and a back edge height). The simulator fires pulses on a regular scan pattern with
jitter (points per square metre is a parameter), finds each pulse's first return (the highest surface hit) and last
return (the ground), adds range noise, and rasterises a DSM (first return) and DTM (last return), like the EA's.
Deterministic: the jitter comes from a seeded generator, so the same model and seed give the same cloud.

This is the scanner run in reverse. scanner(vlidar(model)) must give back the model's rows: a closed loop.
"""
import math
import numpy as np


def tables_height(xp, x, y, rows_bearing_deg, pitch_m, depth_m, front_m=0.8, back_m=2.4, mask=None):
    """Height of tilted tables at points (x, y) in metres (0 where there is no table). Rows run along the bearing;
    across the row, the table rises from front_m to back_m over depth_m, then there is a gap to the next row."""
    th = math.radians(rows_bearing_deg) + math.pi / 2
    u = (x * math.cos(th) + y * math.sin(th)) % pitch_m                # position across the row cycle
    on = u < depth_m
    h = xp.where(on, front_m + (back_m - front_m) * (u / depth_m), 0.0)
    if mask is not None:
        h = xp.where(mask, h, 0.0)
    return h


def survey(xp, extent_m, ground_fn, object_fn, ppsm=8.0, noise_m=0.05, seed=1):
    """Simulate pulses over a square extent (metres). Returns x, y, first-return z, last-return z (arrays)."""
    n = int(extent_m * extent_m * ppsm)
    side = int(math.sqrt(n))
    g = np.linspace(0, extent_m, side, endpoint=False, dtype=np.float32)
    gx, gy = np.meshgrid(g, g)
    rng = np.random.default_rng(seed)
    jx = rng.uniform(-0.5, 0.5, gx.shape).astype(np.float32) * (extent_m / side)
    jy = rng.uniform(-0.5, 0.5, gy.shape).astype(np.float32) * (extent_m / side)
    nz = rng.normal(0, noise_m, gx.shape).astype(np.float32)
    x, y = xp.asarray((gx + jx).ravel()), xp.asarray((gy + jy).ravel())
    ground = ground_fn(xp, x, y)
    first = ground + object_fn(xp, x, y) + xp.asarray(nz.ravel())
    last = ground + xp.asarray(nz.ravel())
    return x, y, first, last


def rasterise(xp, x, y, z, extent_m, cell_m=0.5, how='max'):
    """Grid points into a raster (the highest point per cell for a DSM). Empty cells are filled from the left."""
    n = int(extent_m / cell_m)
    ix = xp.clip((x / cell_m).astype(xp.int32), 0, n - 1); iy = xp.clip((y / cell_m).astype(xp.int32), 0, n - 1)
    flat = iy * n + ix
    out = xp.full(n * n, -1e9, dtype=xp.float32)
    if xp is np:
        np.maximum.at(out, flat, z)
    else:
        import cupyx
        cupyx.scatter_max(out, flat, z)
    out = out.reshape(n, n)
    empty = out < -1e8
    if bool(empty.any()):
        out = xp.where(empty, xp.roll(out, 1, axis=1), out)
        out = xp.where(out < -1e8, 0.0, out)
    return out
