# Night build plan, 27 to 28 September 2026 (22:25 to 07:00 London)

## Top priority: a correct, real-mapped world first
Every object sits at its true coordinates, tied to real addresses and real measurements. In Great Britain that means one conversion: OSTN15, via the place contract. Trenches, pipes, cable routes, pylon footings and solar rows all carry real dimensions in metres, checked against a known reference. Looks come second. Invisible layers come only after the world is proven.

## Rules for both teams
- **Geometry first.** Every task submits geometry, and it must be rendered and looked at before it counts. A passing unit test with no rendered picture is not done.
- **Anchored, never floating.** Everything sits at a real latitude and longitude, including imagined designs, which are labelled "imagined". The only exception is a deliberate test object, which sits at a stated origin.
- **Provenance on every value:** measured, derived, estimated or assumed, with its source.
- **Twins:** every modelled geometry has a twin (a design and its scan, the GPU and the CPU, the map and the world). At least one twin in each pair comes from measured reality. Agreement between two things we built proves consistency, not truth.
- **Import, never copy:** core.py, vlidar.py, fictional.py, structures.py and pylon.py.
- **No names, and no imagery, point clouds, tiles or third-party data files in the repository.**
- **One writer per branch.** Small pull requests, each passing CI. Never push directly to main.

## Local team (owner's PC: GPU, local data caches)
The local team builds these modules, each on its own `build/<name>` branch, each with an adversarial tester:
- `scanner/fetch.py`: verified open data sources (EA LiDAR point clouds and grids with survey year, EA aerial photography, the Scotland and Wales portals) plus a fallback. Polite and cached, never committed.
- `scanner/pointcloud.py`: LAZ to DSM, DTM and nDSM on the GPU.
- `scanner/measure.py`: an image or nDSM gives blocks, rows, stations and fences in lon/lat.
- `scanner/sitemodel.py`: builds site models following `docs/SITEMODEL-SCHEMA.md`, with procedural fills and provenance.
- `scanner/compare.py`: compares the virtual LiDAR of a model against a real survey, producing residuals and a residual map.
- `scanner/cli.py`: `python -m scanner.cli scan --lat --lon --radius`, which writes the model, an overlay picture, residuals and a report.

**Proof:** full scans at public register points REPD 6502, 2347 and 2203, each looked at by a visual judge. The integrator merges to `scanner/20260927`, then to main through a pull request.

## Cloud team (GitHub only, synthetic data)
See the coordination issue for its jobs. It does not edit the six local modules or the local branches.

## Communication
One GitHub issue titled **"Night coordination: local and cloud"**. Both teams post there at least once an hour:
- **what landed**: branch, pull request, CI link, and a picture link or description;
- **what's blocked**;
- **questions for the other team**;
- **claims**: "I'm taking X", so nobody duplicates work.

Read the other team's latest comment before starting any new task.

## Stop
The local team stops at 01:30 and makes its final push at 01:45. The cloud team posts its morning report at 06:30 and stops at 07:00.
