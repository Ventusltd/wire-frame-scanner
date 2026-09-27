# Cloud overnight status (updated hourly until 07:00 London)

## 22:18 London
| Job | State | Pull request | Evidence (local; CI on the PR is the final proof) |
|---|---|---|---|
| 1 Carry-overs | PR open | wire-frame-scanner#10 | 6 scripts pass; pylon 45/45; fictional loop 5/5 at ±0.10 m / 0.5°; vLiDAR prints n/a without a GPU |
| 2 Review local build/* | starts 22:45, hourly | - | no build/* branches yet |
| 3 Hard known-answer cases | PR open | wire-frame-scanner#11 | 48 cases: 36 pass, 12 documented XFAIL; core.py unchanged |
| 4 Skeletons overlay module | PR open | energy-transition-simulator#6 | skeletons-smoke 10/10 (SwiftShader, MapLibre from npm); 1950 lines through window.SIM |
| 5 Morning report | scheduled 06:30 | - | - |

Key finding: the scanner's pitch error comes from row_pitch rounding to the FFT grid step (n=1024 under ~128 m), not from having few rows. Details in docs/HARD-CASES.md (#11).

## 22:47 London
- CI green: #10 carry-overs (run 36351168455), #11 hard cases (run 36351203342), #8 report.
- energy-transition-simulator #6 skeletons: CI 9/10. With a live network the pylons module overwrites the shared #info line, so the provenance check read pylon text. Fixed: the provenance is kept in module state and on the button ("Skeletons (N, illustrative)"). 10/10 locally; the CI re-run is pending. The overlay smoke test was 14/14 in the same run.
- The local team posted its night plan (plan/night-20260927) and the coordination issue #13. No build/* branches yet. The lane/grid-assets, lane/measure and lane/scanner-rows branches on the simulator have no pull requests yet.
- Next: review build/* branches as they land; XFAIL promotion report for the local core.py fixes.
