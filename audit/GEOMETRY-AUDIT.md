# Geometry CI audit (2026-09-28 13:13 UTC)

GPU: NVIDIA GeForce RTX 5070 Ti. Product: energy-transition-simulator 900fd7c. Every number below is from `audit.json`; each audit has a NumPy witness on a sample. This measures consistency of the geometry the product draws; it does not prove the real site (verification is closed under belief).

## 1. Precision: why geometry breaks when you zoom in

2,127,108 module corners on 5,077 measured runs. One Mercator unit is 25,035 km here.

| storage | ground error p50 | p99 | max |
|---|---|---|---|
| absolute Mercator, float32 | 0.435 m | 0.788 m | 0.834 m |
| relative to a local origin (RTC), float32 | 0.0106 mm | 0.0316 mm | 0.0622 mm |

A 1 cm camera step in an absolute float32 pipeline moves vertices by up to 1.267 m (the jitter). Witness max difference 2.78e-09 m.

| view | absolute float32 error | RTC float32 error |
|---|---|---|
| map zoom 16 | 1.1 px | 0.00008 px |
| map zoom 17 | 2.2 px | 0.00017 px |
| map zoom 18 | 4.5 px | 0.00033 px |
| map zoom 19 | 8.9 px | 0.00067 px |
| map zoom 20 | 17.9 px | 0.00133 px |
| map zoom 21 | 35.8 px | 0.00267 px |
| map zoom 22 | 71.5 px | 0.00533 px |
| map zoom 23 | 143.1 px | 0.01066 px |
| map zoom 24 | 286.2 px | 0.02133 px |
| walk, member 2m from the eye | 390.0 px | 0.02907 px |
| walk, member 5m from the eye | 156.0 px | 0.01163 px |
| walk, member 20m from the eye | 39.0 px | 0.00291 px |

**Rule:** every close-up layer stores vertices in metres about a local origin (RTC) and applies the origin in float64 on the CPU. An absolute float32 layer cannot draw a 0.1 m member at walk scale.

**What the product does today:** its block layers (lidar-stream, plan-view, procedural, engine-lock) keep each buffer relative to a block anchor (`PF.toMercator(anchor)`), which meets the rule if the anchor offset is folded into the matrix in float64 before upload. The scan cannot prove that. A z22+ still-camera jitter test per layer (vertices stable to 0.5 px) is the first test of the next build. So precision is the failure mode for any NEW close-up layer. It is not proven to be today's cause of breaking; the camera (pitch capped at 80 to 85 deg, a map camera rather than a free first-person one) and lines instead of solids are the other two suspects.

## 2. Tables as solids

639 tables from the product's own tables.js, half width 12.13 m, pitch 26.83 m, rasterised at 0.25 m (45,431,204 cells). Cover 91.8 ha.

- Overlap between tables: 913.0 m2; overlapping pairs 15.
- Aisle a walker gets to the next table: min -4.15 m, p5 0.33, median 2.56, p95 2.57 m (n 474).
- Aisles under 1 m: 27; 1 to 2 m: 142.
- Offset from the 26.83 m lattice: median 4.90 m, p95 11.31 m; tables over 1 m off: 538.
- Witness: cell counts around 20 random tables differ by 0.

## 3. Trench bends that physically fit

A bend of radius R at a vertex with deflection theta needs a tangent length R tan(theta/2) within half of each neighbouring segment.

| case | vertices | bends over 1 deg | max deflection | largest R that fits at every bend | fails at R 0.25 / 1.0 / 2.0 / 3.0 m |
|---|---|---|---|---|---|
| A1 | 1859 | 1856 | 122.9 deg | 0.691 m | 0 / 1 / 88 / 225 |
| A2 | 1850 | 1847 | 122.9 deg | 0.691 m | 0 / 1 / 97 / 232 |
| A3 | 1843 | 1840 | 122.9 deg | 0.691 m | 0 / 1 / 95 / 231 |
| A4 | 1859 | 1856 | 122.9 deg | 0.633 m | 0 / 2 / 116 / 247 |
| B1 | 1860 | 1856 | 122.9 deg | 0.691 m | 0 / 2 / 84 / 220 |
| B2 | 1893 | 1890 | 122.9 deg | 0.691 m | 0 / 1 / 117 / 261 |
| B3 | 1913 | 1910 | 122.9 deg | 0.691 m | 0 / 1 / 133 / 278 |
| B4 | 1928 | 1924 | 122.9 deg | 0.691 m | 0 / 2 / 135 / 286 |

The duct bend radii in the product are 1.8 m and more for 90 mm PE upwards (datasheet), and the cable MBR is 0.36 to 0.50 m. Every fail at those radii is a place where the drawn route cannot be built as drawn.

## 5. Joining the wireframe world to reality in the correct dimensions

16,008,001 points on a 1 m grid over a 4 x 4 km envelope. National Grid point scale factor at the origin 1.0001071; grid convergence 2.276 deg. Witness max difference 4.4e-13 m.

| how the model is joined | worst error within 50 m | 250 m | 1 km | 2 km | largest envelope for 1 mm / 1 cm / 10 cm |
|---|---|---|---|---|---|
| one Mercator anchor, metres scaled at the anchor | 0.5 mm | 12.3 mm | 196 mm | 785 mm | 50 m / 200 m / 500 m |
| National Grid metres used as ground metres | 5.4 mm | 27.1 mm | 112 mm | 234 mm | 5 m / 50 m / 500 m |
| grid north used as true north | 1986.8 mm | 9943.6 mm | 39922 mm | 80236 mm | 0 m / 0 m / 2 m |
| flat local plane, heights not lowered for the curve | 0.2 mm | 4.9 mm | 78 mm | 314 mm | 100 m / 250 m / 1000 m |

**Rule for joining:** build each envelope in a local east-north-up frame in ground metres at the envelope origin; convert every vertex from the national grid through the one place frame (OSTN15) to latitude and longitude, then to the map, in float64; apply the grid scale factor and convergence, never assume them; lower DTM heights by the curve drop; and keep an envelope within the radius the table gives for the accuracy wanted (or re-anchor per table or trench, which is what one close-up at a time allows).

## 4. Code

| module | lines | test | custom GL layer | absolute Mercator calls | local-frame refs | Float32Array | "owner" | drive paths |
|---|---|---|---|---|---|---|---|---|
| ac-trenches | 451 | yes | yes | 0 | 1 | 1 |  |  |
| addresses | 152 | yes |  | 0 | 1 | 0 |  |  |
| connect-here | 178 | NO |  | 0 | 8 | 0 |  |  |
| coords-readout | 134 | NO |  | 0 | 0 | 0 |  |  |
| engine-lock | 306 | yes | yes | 0 | 3 | 4 |  |  |
| farm-assess | 434 | yes |  | 0 | 2 | 0 |  |  |
| find-go | 124 | NO |  | 0 | 1 | 0 |  |  |
| gpu-rows | 40 | NO |  | 0 | 2 | 0 |  |  |
| lidar-onsite | 75 | NO |  | 0 | 0 | 0 |  |  |
| lidar-stream | 345 | yes | yes | 0 | 0 | 3 |  |  |
| menu-bar | 295 | NO |  | 0 | 0 | 0 |  |  |
| menu-style | 50 | NO |  | 0 | 0 | 0 |  |  |
| morph | 123 | NO | yes | 0 | 0 | 1 |  |  |
| perf | 137 | NO |  | 0 | 1 | 2 |  |  |
| plan-view | 422 | yes | yes | 0 | 0 | 0 |  |  |
| plant | 154 | NO |  | 0 | 2 | 0 |  |  |
| procedural | 266 | yes | yes | 0 | 9 | 1 |  |  |
| pylons-real | 186 | NO |  | 0 | 2 | 0 |  |  |
| rows-geometry | 223 | NO |  | 0 | 1 | 2 |  |  |
| scanner-rows | 156 | yes |  | 0 | 4 | 0 |  |  |
| substations | 199 | NO |  | 0 | 3 | 0 |  |  |
| tables | 345 | yes |  | 0 | 9 | 0 |  |  |
| trench-measure | 362 | yes | yes | 0 | 4 | 1 |  |  |
| walk-fps | 166 | NO |  | 0 | 0 | 0 |  |  |
| wire-look | 136 | NO | yes | 0 | 3 | 1 |  |  |

25 modules, 5,459 lines; 10 have a test of their own. Modules with a custom GL layer and absolute Mercator calls are the first to break at walk scale.

