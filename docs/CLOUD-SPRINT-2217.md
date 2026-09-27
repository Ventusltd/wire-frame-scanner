# Cloud sprint report (scanner/20260927), 27 Sept, stopped about 22:05 London

Every job finished. Each builder's test was re-run by a separate check in its own process, and the results are below.

## 1. Jobs
| Job | Pull request | Result | Checker |
|---|---|---|---|
| 1 CI | #2 cloud/ci | green | Re-ran both tests locally: 12/12 and 4/4 |
| 2 Overlay check | read-only | 14/14 green on 31a96df | Read the CI log |
| 3 Fictional designs | #6 cloud/fictional | 29/29 | Re-ran: 29/29 |
| 4 Fictional loop | #7 cloud/fictional-loop (on top of #6) | 5/5 | Re-ran: 5/5 |
| 5 Tower | #3 cloud/tower | 7/7 | Re-ran 7/7, plus an awkward profile that built 732 lines |
| 6 Pylon | #4 cloud/pylon | 38/38 | Re-ran 38/38; existing tests still pass |
| 7 Sources | #5 cloud/sources-doc | 25 claims with URLs, 10 UNCONFIRMED | 26 URLs and 12 UNCONFIRMED marks in the file |

## 2. CI links
- Scanner: https://github.com/Ventusltd/wire-frame-scanner/actions/runs/36350068930 (push) and /runs/36350076509 (pull request). Both passed.
- Overlay: https://github.com/Ventusltd/energy-transition-simulator/actions/runs/36349882844. 14 passed, 0 failed, including "no missing local files" and "window.SIM exists". Pylons (12) sit on the 400 kV line.
- Pull requests #3 to #7 do not carry the workflow file. Their CI runs only after #2 is merged into scanner/20260927, or after rebasing onto it. The counts above are local runs (Python 3, NumPy, no GPU).

## 3. Numbers
**Fictional loop:** each design gives its row direction and then its pitch, as designed → recovered.

| Design | Row direction | Pitch |
|---|---|---|
| 1 | 90 → 89.70° | 5.00 → 5.020 m |
| 2 | 70 → 69.93° | 7.50 → 7.529 m |
| 3 | 123 → 122.99° | 9.00 → 8.982 m |
| 4 | 45 → 45.04° | 12.00 → 12.190 m |
| 5 | 151 → 151.16° | 6.50 → 6.481 m |

Tolerances are ±1° and ±0.25 m. The 12 m design has only 0.06 m of margin. This proves consistency between our own generator and our own scanner, not truth.

**Tower:**
- The profile hits every pin with 0 error.
- 26 rings.
- Diagrid nodes lie on the rings within 3.6e-15.
- 1,824 lines, equal to n(3R−2).
- No overshoot.

**Pylon:** the line counts are 162, 194 and 226 for 132, 275 and 400 kV. Every bracing endpoint lies on a leg. All dimensions are ASSUMED, because no published table was available offline.

## 4. Where things stopped, for the local team
- **Pylon:** replace the assumed heights with cited values. The docstring lists the sources to cite.
- **Sources doc:** 25 claims were confirmed from search snippets only, because the proxy blocked the data.gov.uk pages. Re-verify them on the PC.
- **test_vlidar_loop.py:** prints "GPU and CPU agree: True" with no GPU. The check is vacuous and should print n/a.
- **Merge order:** #2 (CI) first, then #6 before #7.
- **PNGs:** tower.png and pylon.png are rendered to test-output/, which is git-ignored, and CI uploads them. The cloud copies were viewed by the builders; they are not in git.

## 5. Could not do
- Test on a GPU.
- Fetch the data.gov.uk pages directly.
- Use published pylon dimensions.
- None of the files the local team owns were touched.
