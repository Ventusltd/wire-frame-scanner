# wire-frame-scanner
Generated Wire Frame 3D worlds using REAL measured data or FICTIONAL for design proposals, for example a box 1x1cm or REAL GIS coordinates or AI generated

## Status
- **scanner/core.py:** deterministic rules R1–R4, which run on the GPU (CuPy) or the CPU (NumPy).
- **tests/test_known_answer.py:** passes 12/12 on both engines, and the two engines agree exactly.
- **Details:** see docs-SCANNER.md.
