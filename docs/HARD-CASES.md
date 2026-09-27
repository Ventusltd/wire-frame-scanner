# Hard known-answer cases for the scanner core

`tests/test_hard_cases.py` pushes the unmodified scanner core (`core.row_normal`, `core.refine_normal`,
`core.row_pitch`, and `core.panel_mask` on the image path) through synthetic sites whose row direction and pitch
are fixed by construction. Everything is synthetic: fictional designs (`fictional.solar_block`,
`fictional.solar_block_heights`), the virtual LiDAR (`vlidar.survey`, `vlidar.rasterise`), or striped masks and
RGB images like those in `tests/test_known_answer.py`. No data files, no real sites.

Paths used (identical to the existing tests):

* **image**: RGB -> `panel_mask` -> `refine_normal(row_normal)` -> `row_pitch`, 0.746 m/px, directions in the
  image-x convention of `test_known_answer.py`.
* **lidar**: height model -> `vlidar.survey` (8 pulses/m2, 0.05 m noise, seed 7 unless stated) -> DSM, DTM at
  0.5 m -> `(DSM - DTM) > 1 m` -> same core calls. Directions are compass degrees mod 180 (rows' run direction),
  as in `test_fictional_loop.py`.

Tolerances are the existing ones: direction +/- 1 deg, pitch +/- 0.25 m. A case marked `xfail` is a known,
documented failure of the current core; the script prints XFAIL and still exits 0. It exits 1 only if an
expected-pass case fails. An xfail that starts passing prints XPASS (update the expectation).

Result on this commit: **36 PASS, 12 XFAIL, 0 unexpected failures** (48 cases, about 17 s on CPU).

## Case table

Directions in degrees, pitch and pitch error in metres (error = recovered - designed).

| group | case | designed dir | designed pitch | recovered dir | recovered pitch | dir err | pitch err | result |
|---|---|---|---|---|---|---|---|---|
| contrast | dark panels on grass (baseline) | 17.0 | 7.50 | 17.03 | 7.489 | 0.03 | -0.011 | PASS |
| contrast | dark panels on grass, pixel noise sd 12 | 17.0 | 7.50 | 17.00 | 7.489 | 0.00 | -0.011 | PASS |
| contrast | grey panels (luma ~98) on grass | 17.0 | 7.50 | None | None | None | None | XFAIL |
| contrast | bright/glinting panels on grass | 63.0 | 9.00 | None | None | None | None | XFAIL |
| contrast | dark panels on dark bare soil | 17.0 | 7.50 | 87.20 | 14.979 | 70.20 | +7.479 | XFAIL |
| contrast | dark panels on concrete/gravel | 135.0 | 8.20 | 134.87 | 8.214 | 0.13 | +0.014 | PASS |
| broken | 20% of tables missing at random | 70.0 | 7.50 | 69.98 | 7.529 | 0.02 | +0.029 | PASS |
| broken | 45% of tables missing at random | 70.0 | 7.50 | 69.96 | 7.529 | 0.04 | +0.029 | PASS |
| broken | every 3rd row missing (rows at 7.5 m, 22.5 m super-period) | 70.0 | 7.50 | 70.00 | 11.130 | 0.00 | +3.630 | XFAIL |
| broken | every 2nd row missing (as built: 15 m pitch) | 70.0 | 15.00 | 69.90 | 14.629 | 0.10 | -0.371 | XFAIL |
| broken | wide 6 m gaps between tables | 123.0 | 9.00 | 123.01 | 8.982 | 0.01 | -0.018 | PASS |
| slope | steep 30% slope along rows | 90.0 | 7.50 | 90.09 | 7.529 | 0.09 | +0.029 | PASS |
| slope | steep 30% slope across rows | 90.0 | 7.50 | 90.09 | 7.529 | 0.09 | +0.029 | PASS |
| slope | cross-slope 25% + 25% diagonal | 123.0 | 9.00 | 123.15 | 8.982 | 0.15 | -0.018 | PASS |
| slope | very steep 60% slope across rows | 90.0 | 7.50 | 90.19 | 7.529 | 0.19 | +0.029 | PASS |
| slope | rough hills (8 m amplitude, 20 m wavelength) | 70.0 | 7.50 | 69.96 | 7.529 | 0.04 | +0.029 | PASS |
| mixed | two blocks 6 m + 10 m pitch, whole site (vs 6 m) | 90.0 | 6.00 | 89.70 | 10.039 | 0.30 | +4.039 | XFAIL |
| mixed | two blocks 6 m + 10 m pitch, west block cropped | 90.0 | 6.00 | 90.00 | 6.024 | 0.00 | +0.024 | PASS |
| mixed | two blocks 6 m + 10 m pitch, east block cropped | 90.0 | 10.00 | 90.00 | 10.039 | 0.00 | +0.039 | PASS |
| mixed | two blocks 5 m + 10 m (harmonic), whole site (vs 5 m) | 90.0 | 5.00 | 90.09 | 10.039 | 0.09 | +5.039 | XFAIL |
| mixed | two blocks 7.5 m @ az180 + 7.5 m @ az150, whole site | 90.0 | 7.50 | 64.22 | 7.420 | 25.78 | -0.080 | XFAIL |
| mixed | two blocks 8 m @ az180 + 8 m @ az210, each cropped (az210) | 120.0 | 8.00 | 120.28 | 8.000 | 0.28 | +0.000 | PASS |
| tracker | N-S trackers flat, pitch 5.5 m | 0.0 | 5.50 | 179.95 | 5.505 | 0.05 | +0.005 | PASS |
| tracker | N-S trackers tilted 45 deg E/W, pitch 5.5 m | 0.0 | 5.50 | 0.01 | 5.505 | 0.01 | +0.005 | PASS |
| tracker | N-S trackers tilted 55 deg, hub 1.6 m, pitch 6 m | 0.0 | 6.00 | 0.06 | 6.024 | 0.06 | +0.024 | PASS |
| tracker | N-S trackers flat, 40 m units with gaps, pitch 7 m | 0.0 | 7.00 | 0.00 | 7.014 | 0.00 | +0.014 | PASS |
| tracker | N-S trackers flat, dense pitch 4.2 m (width 2.2 m) | 0.0 | 4.20 | 0.08 | 4.197 | 0.08 | -0.003 | PASS |
| objects | 25 inverter/cabin boxes between rows | 70.0 | 7.50 | 69.99 | 7.529 | 0.01 | +0.029 | PASS |
| objects | 120 boxes between rows | 70.0 | 7.50 | 69.96 | 7.529 | 0.04 | +0.029 | PASS |
| objects | diagonal tree line 6 m wide across block | 90.0 | 7.50 | 90.09 | 7.529 | 0.09 | +0.029 | PASS |
| objects | 10 m access track / shading gap across rows | 90.0 | 7.50 | 89.99 | 7.529 | 0.01 | +0.029 | PASS |
| few rows | 3 rows @ 12 m | 90.0 | 12.00 | 89.92 | 12.488 | 0.08 | +0.488 | XFAIL |
| few rows | 4 rows @ 12 m | 90.0 | 12.00 | 90.05 | 12.190 | 0.05 | +0.190 | PASS |
| few rows | 6 rows @ 12 m | 90.0 | 12.00 | 90.00 | 12.190 | 0.00 | +0.190 | PASS |
| few rows | 8 rows @ 12 m (known +0.19 m bias) | 90.0 | 12.00 | 89.93 | 12.190 | 0.07 | +0.190 | PASS |
| few rows | 16 rows @ 12 m | 90.0 | 12.00 | 89.98 | 12.047 | 0.02 | +0.047 | PASS |
| few rows | 4 rows @ 6 m | 90.0 | 6.00 | 89.64 | 6.024 | 0.36 | +0.024 | PASS |
| few rows | 3 rows @ 14 m | 90.0 | 14.00 | 90.00 | 14.629 | 0.00 | +0.629 | XFAIL |
| noise | mask flip 10% (image path) | 63.0 | 11.00 | 62.95 | 10.991 | 0.05 | -0.009 | PASS |
| noise | mask flip 20% (image path) | 63.0 | 11.00 | 62.99 | 10.991 | 0.01 | -0.009 | PASS |
| noise | mask flip 35% (image path) | 63.0 | 11.00 | 62.82 | 10.991 | 0.18 | -0.009 | PASS |
| noise | LiDAR range noise 0.2 m | 70.0 | 7.50 | 70.00 | 7.529 | 0.00 | +0.029 | PASS |
| noise | LiDAR range noise 0.4 m | 70.0 | 7.50 | 69.98 | 7.529 | 0.02 | +0.029 | PASS |
| noise | LiDAR sparse 2 pulse/m2, 0.5 m cells | 70.0 | 7.50 | 70.16 | 7.529 | 0.16 | +0.029 | PASS |
| noise | LiDAR sparse 1 pulse/m2, 0.5 m cells | 70.0 | 7.50 | 65.53 | 7.420 | 4.47 | -0.080 | XFAIL |
| noise | LiDAR sparse 0.5 pulse/m2, 0.5 m cells | 70.0 | 7.50 | 58.73 | 14.629 | 11.27 | +7.129 | XFAIL |
| noise | LiDAR sparse 1 pulse/m2, 1 m cells | 70.0 | 7.50 | 70.01 | 7.529 | 0.01 | +0.029 | PASS |
| noise | LiDAR sparse 0.5 pulse/m2, 1.5 m cells | 70.0 | 7.50 | 69.97 | 7.529 | 0.03 | +0.029 | PASS |

## Where and why the scanner fails

### 1. Pitch quantisation, not row count, is the "few rows" bias

The known reading of 12.19 m for 8 rows at 12 m is **not** caused by having only 8 rows. `row_pitch` takes the
peak on the zero-padded FFT grid, `n = max(1024, next_pow2(4 L))`, and reports `pitch = n / k` pixels with an
integer bin `k`. With 0.5 m cells any block whose cross-row extent is under about 128 m gets `n = 1024`; a 12 m
pitch is 24 px, the exact bin is 1024/24 = 42.67, and the two nearest bins read **12.190 m** (k = 42) and
11.907 m (k = 43). That is why 4, 6 and 8 rows at 12 m all read exactly 12.190 m, while 16 rows (extent over
128 m, so `n = 2048`, bin spacing halved) reads 12.047 m. The same effect gives the ubiquitous 7.529 m for 7.5 m
(2048/136 px) and the -0.37 m error for 15 m (14.629 m, `every 2nd row missing`). The pitch-grid spacing grows as
pitch squared: roughly `p^2 / (n * cell)`, so 0.28 m at 12 m and 0.44 m at 15 m with `n = 1024` and 0.5 m cells,
which alone can exceed the 0.25 m tolerance near the top of the 4-15 m range.

With **3 rows** a second effect appears: the spectral main lobe is so wide (about n/L bins) that the
"lowest-frequency local maximum holding half the peak" rule, together with the leakage of the mean-subtracted
rectangular envelope toward low frequencies, lands 1-2 bins low: 12.49 m for 12 m and 14.63 m for 14 m. These are
XFAIL.

### 2. Missing rows and mixed pitches: the fundamental rule picks the wrong peak

`row_pitch` deliberately prefers the lowest in-range frequency with at least half the strongest power, to avoid
reporting a harmonic. That rule fails whenever the profile holds real power at a longer period:

* **every 3rd row missing**: the row pattern repeats every 22.5 m (out of range); its second harmonic 11.25 m is
  in range and strong, so the scanner reports 11.13 m instead of the 7.5 m row spacing.
* **two blocks 6 m + 10 m** (and 5 m + 10 m, an exact harmonic pair) measured as one mask: the 10 m block's peak
  is at a lower frequency and above half height, so the whole site reads 10.04 m. The 6 m block is invisible.
* **two blocks with different azimuths** (180 and 150) in one mask: the structure tensor and the +/- 8 deg sweep
  settle on a compromise (64 deg vs 90 and 60), matching neither block.

Each block measured on its own (cropped) passes, so the failure is the single-answer-per-mask design, not the
spectral maths.

### 3. Image mask: brightness threshold, not contrast

`panel_mask` is an absolute rule (luma < 75, not green). Grey panels (luma about 98) and bright or glinting panels
produce an empty mask (no answer at all). Dark panels on dark bare soil produce a mask of the whole block, so the
stripes are lost and the result is nonsense (70 deg, 15 m). Dark panels on bright concrete pass. The failure is
about absolute thresholds, not about the contrast between panels and background.

### 4. Sparse LiDAR rasterised too finely

At 1 pulse/m2 (and 0.5) with 0.5 m cells most cells are empty; `vlidar.rasterise` fills empties from the left
neighbour, which smears the mask along +x and biases the direction (4.5 deg and 11 deg errors). Rasterising at a
cell near `1/sqrt(ppsm)` (1 m for 1 pulse/m2, 1.5 m for 0.5) fixes it with no core change: both pass.

### Robust (all pass)

Random missing tables (20% and 45%), wide gaps between tables, steep, cross and very steep (60%) slopes, rough
hills (DSM - DTM cancels the ground), single-axis trackers north-south (flat, 45 and 55 deg tilt, broken into
units, dense 4.2 m pitch), inverter boxes and cabins between rows (25 and 120), a diagonal tree line, a 10 m
access track, 35% mask flip noise, and 0.4 m range noise.

## Suggestions for the core owners

1. **Sub-bin pitch estimate.** Refine the chosen peak by parabolic (or Gaussian) interpolation of log |G| over
   bins k-1, k, k+1, or by a local golden-section search of the DFT magnitude at non-integer frequencies (cheap:
   one dot product per probe). Alternatively raise the padding floor with the pitch range, e.g.
   `n >= 16 * PITCH_MAX_M / cell` so the grid spacing is under 0.1 m at 15 m. This removes the 12.19 m bias.
2. **Time-domain cross-check.** After the FFT, fit the row centres (from `row_lines` or profile peaks) with a
   least-squares line index -> offset; its slope is the pitch without bin error and is well defined with 3 rows.
3. **Missing-row aware fundamental.** Before accepting the lowest-frequency candidate, test whether the
   higher-frequency candidate is an integer multiple (2x, 3x within a few %) and whether the profile's row
   occupancy at the finer pitch is consistent with gaps; prefer the finer pitch when the coarser one is explained
   as a missing-row super-period. Report both with a confidence flag rather than silently choosing.
4. **One answer per block.** Split masks into blocks before measurement (connected components after a closing
   across the expected gap, or a sliding-window local pitch/angle map clustered into regions), then measure each
   block. Mixed pitches and mixed azimuths both pass once separated.
5. **Relative image mask.** Make `panel_mask` adaptive: threshold relative to the local background (e.g. local
   median or Otsu per tile) and add a texture test (stripe energy in the row band), so grey or bright panels and
   dark soil backgrounds are handled. Report "no mask" explicitly rather than returning None silently.
6. **Raster cell from point density.** Wherever DSM/DTM are rasterised from points, choose the cell from the
   survey density (about `1/sqrt(ppsm)`), or fill empty cells isotropically rather than from the left.
