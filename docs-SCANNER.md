# The Wire Frame Scanner

The scanner uses measured, deterministic maths to turn imagery and GIS geometry into wireframe models. The same code runs on the GPU (CuPy) and on the CPU (NumPy), and the two must agree.

## Rules (scanner/core.py)
- **R1.** Panel blocks are the connected regions of the panel mask (dark, not green).
- **R2.** Within a block, rows are parallel. The row normal comes first from the row edges (the structure tensor). A brute-force sweep then refines it: ±8° in 0.1° steps, keeping the angle whose cross-row profile has the sharpest spectral peak.
- **R3.** Rows are equally spaced. The pitch is the fundamental of the cross-row profile, limited to 4–15 m. The phase comes from that fundamental.
- **R4.** Each row is a line at phase + k × pitch, clipped to the block.
- **R5, the site tile (measured ground in).** The scanner reads measured ground only as it arrives: fixed 2,048 m lattice tiles in British National Grid, streamed where someone has arrived. That means one request per product per tile, at least 40 s apart and at most 16 a day per client. Only the derived wireframe and a receipt are kept, and nothing is downloaded in bulk. Rows are scanned from LiDAR only where the survey postdates the build. Otherwise the heights are pre-construction ground. The full rule, signed by three witnesses, is [docs/R5-SITE-TILE.md](docs/R5-SITE-TILE.md). Its pure maths and 40 proofs are in ventus-grid-engine (engine/site-tile.js).

## Known-answer tests (tests/test_known_answer.py)
The tests build synthetic farms whose row direction and pitch are exact by construction:
- directions of 0°, 17°, 63°, 90°, 104° and 135°;
- pitches of 6–13.5 m;
- with and without 5% pixel noise;
- inside irregular block outlines.

The scanner must recover the pitch within 0.25 m and the direction within 1°, on both engines, and the two engines must agree.

**Result, 27 Sept 2026 (RTX 5070 Ti):** 12/12 pass on the GPU and on the CPU, and the two agree exactly.

## History of fixes, each found by looking and then measuring
- **Block shape.** Taking the direction from the whole block's 2D spectrum was fooled by the block's shape. R2 now uses the row edges instead.
- **Harmonics.** Taking the strongest spectral peak picked harmonics and texture. R3 now takes the fundamental inside 4–15 m.
- **Slanted rows.** The structure tensor alone was 3–5° off on slanted rows, because of pixel staircases. The brute-force sweep fixed that: 6/12 passed before, and 12/12 after the sweep was widened to ±8°.

Everything the scanner draws from real imagery is labelled "estimated from imagery, not measured". The repository holds no imagery files. Tiles are fetched and cached locally under their providers' terms.

## Filling what cannot be seen (procedural maths), with provenance on every field
Every value in a site model carries a tag and its source:
- **measured:** seen directly in imagery or GIS data. Examples: row direction, pitch, block outlines, fences, station footprints, tower positions, LiDAR heights.
- **derived:** computed from measured values by exact geometry. Examples: tilt from measured table depth, pitch and latitude; table count from block area and pitch; MW from tables × module rating.
- **estimated:** filled in by an engineering rule where nothing is visible. Examples:
  - module size and rating from public datasheets;
  - inverter size and count from MW and the stations seen;
  - cable size from current and route length;
  - trench depth and spacing from the cited standard clauses (BS 7671 and others, cited by number and clause only, never copied);
  - soil thermal resistivity from the soil data;
  - pulling tension from cable mass and route bends.
- **assumed:** a stated default, used only when nothing better exists.

The same pattern works for any structure. For example, a tower building: a few measured pins (footprint centre and radius, widest radius, LiDAR height, top cap), then a rule-shaped skeleton between them (a profile curve, floor rings, a diagrid). It is labelled "measured at these points, rule-shaped between".

## Virtual LiDAR (scanner/vlidar.py): the scanner run in reverse
A site model (ground plus tilted tables) is surveyed by simulated laser pulses: a jittered scan pattern at a set number of points per m², with first and last returns and range noise. The pulses are gridded into a DSM and a DTM, like a real airborne survey.

**Closed-loop test (tests/test_vlidar_loop.py).** The chain is model, then virtual LiDAR, then the scanner reading only DSM − DTM > 1 m, then back to rows.
- **Result, 27 Sept 2026:** 4/4 pass, over 204,304 pulses per case on rolling ground.
- **Accuracy:** direction within 0.1° and pitch within 0.03 m.
- **Engines:** GPU and CPU agree exactly.

This proves consistency. The truth test is the next step: comparing the virtual DSM with a real survey flown after a farm was built.
