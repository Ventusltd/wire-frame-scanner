# The Wire Frame Scanner

The scanner uses measured, deterministic maths to turn imagery and GIS geometry into wireframe models. The same code runs on the GPU (CuPy) and on the CPU (NumPy), and the two must agree.

## Rules (scanner/core.py)
- **R1.** Panel blocks are the connected regions of the panel mask (dark, not green).
- **R2.** Within a block, rows are parallel. The row normal comes first from the row edges (the structure tensor). A brute-force sweep then refines it: ±8° in 0.1° steps, keeping the angle whose cross-row profile has the sharpest spectral peak.
- **R3.** Rows are equally spaced. The pitch is the fundamental of the cross-row profile, limited to 4–15 m. The phase comes from that fundamental.
- **R4.** Each row is a line at phase + k × pitch, clipped to the block.

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
