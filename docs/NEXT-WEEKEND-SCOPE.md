# Next weekend: the construction simulator (scope, 28 September 2026)

This is the public version. A private version with paths, costs and private data pointers sits in the project stones.
It is written by the lead, and the two independent Fable reviews are merged in section 12 after their furnace runs.

## 1. The target, in the direction's own words
- "I want it build a real life simulator, not high level drawings and graphics, a real simulator."
- "A proper construction onsite envelope within the satellite view to do a construction view walk and build like a 3D game."
- "I want to build actual roads, actual trenches, actual module tables."
- "Our app shouldn't need a VR headset, just a phone, but we are using the VR code to model the wire frame environment
  to be mm accurate to trenching, building and laying cables and modules and unloaded transformers and building roads."
- "The user only ever needs to see one table at a time close up or one trench at a time. The rest can be served from
  drone / helicopter views." "Procedurally generate the world if you can model the accurate geometry."
- The bar: "a proper virtual simulated site world" (site-world release 202609262041), and the geometry standard of
  graphics-engines-open-source (explore.mjs).
- The mission: solar farming with power grids, to power the energy transition and save British farming.

**In one paragraph.** Draw a construction envelope (the site fence line) inside the satellite view. Inside it, the world
becomes a construction site you can walk and build, like a 3D game, on a phone. Everything is real geometry on measured
ground: piles, table structures, modules, trenches with ducts and cables, stations with transformers being unloaded,
and roads built in layers. Wireframe is the chosen look, but the solids behind it are accurate to the millimetre.
Outside the envelope, the satellite, drone and helicopter views carry the rest. Only one table or one trench is ever
at full detail. The rest of the site is generated procedurally from the same accurate templates.

## 2. Where it stands (measured today)
- **Live:** a pinned, checked version nests under Solar Design Studio on the homepage (202609281316). Main ships every
  change within 5 minutes through the CD loop.
- **Play test (Fable, real GPU Chrome, desktop and phone):** about **35 to 40 %** of the vision. Scores out of 10:

  | Area | Score |
  |---|---|
  | Typed find | 3 |
  | Measured ground on arrival | 6 |
  | Honest and anchored | 6 |
  | Walk and drone | 5 |
  | Real farms | 6 |
  | Dig, trench and X-ray | 4 |
  | Plan into 3D | 7 |
  | Build by typing | 6 |
  | Substation to site | 4 |
  | GridAtlas switch | 0 |
  | The farming mission | 1 |
  | Any device | 7 |

  - **Blockers:**
    - the find box is hidden;
    - you cannot look up or down (pitch is fixed);
    - Walk outside England goes black;
    - no GridAtlas switch;
    - "Assess land" shows nothing.
  - **Numbers:** 100+ fps on desktop and phone, 0 page errors.
- **GPU CI audit (section 9):**
  - absolute float32 Mercator storage errs by up to **0.83 m**, which is **390 px** for a member 2 m from the eye; storage relative to a local origin errs by **0.06 mm**;
  - the tables module's 639 tables include **15 overlapping pairs** and **27 aisles under 1 m**;
  - at a 2 m duct bend radius, **84 to 135 bends per trench case cannot be built as drawn**;
  - **10 of 25** modules have a test of their own.
- **Built and proven, but not in the product:**
  - GPU solids (tables, bunds, trenches, roads; watertight, walkable, ray-traced);
  - virtual LiDAR against the satellite (a 0.3 m model tie, and a light photoreal texture plan);
  - X-ray physics (GPR and the magnetic locator);
  - virtual instruments (triangulation, thermal, electrical resonance).

## 3. Why it is still "drawings", in four causes
1. **Lines, not solids.** Tables are outlines from a shape function. There are no posts, rafters, purlins, modules or cells as objects.
2. **A map camera, not a person.** The map camera cannot look up, stands at a fixed pitch, and is not built for a first-person walk under a table.
3. **No construction state.** Nothing is "not yet built", "being built" or "built". There are no quantities, no sequence and no constraints you can feel.
4. **Precision is not enforced.** Today's block layers are anchor-relative, which is good, but no test proves each layer is stable at walk scale. Any new close-up layer can break the way the audit shows.

## 4. The architecture: two views, one world
- **The map shell (MapLibre, as today):** arrive, typed find, satellite, drone and helicopter views, the plan, GridAtlas, streamed EA ground (rule R5).
- **The site envelope (new):** a first-person scene in a local east-north-up frame in metres. Its origin is at the envelope (OSTN15 through the one place frame), with vertices relative to that origin and the origin held in float64.
  - **Ground:** the EA DTM mesh of the envelope's R5 tiles, textured with the satellite tile.
  - **Camera:** a free first-person camera: look up and down, walk, kneel, fly, and collision with solids.
  - **Renderer:** a three.js-class WebGL renderer (MIT), because it brings a scene graph, picking, instancing and WebXR in one open package. WebXR stays optional; the phone is the target.
- **The hand-off:** flying down into the envelope in the drone view morphs into the envelope scene at the same pose, and leaving it morphs back. The shell's plan view and the envelope share one model.
- **One close-up at a time:** the table or trench nearest the eye is built at full detail (every member and module). Everything else is an instance of the same template at lower detail.

## 5. The literature to study (open sources; read and cite, never copy)
**VR and XR, used for modelling and interaction, not for a headset.** The licences below are to be checked at use.
- The W3C WebXR Device API.
- The Khronos OpenXR specification (its SDK is Apache 2.0).
- Monado, the open-source OpenXR runtime.
- Valve's OpenVR SDK (BSD 3-clause).
- The three.js WebXR examples (MIT).

**What we take from them:**
- a 1:1 metric scene;
- ray picking, grab, snap and place;
- locomotion on a phone (a virtual stick, optional gyro look, teleport);
- comfort rules (snap turn, a vignette when moving fast);
- a 72 to 90 fps frame budget.

**Construction simulation:**
- IFC 4.3 (buildingSMART), for alignments, earthworks and tasks (IfcAlignment, IfcEarthworksCut, IfcTask, IfcWorkSchedule);
- 4D sequencing (the build order as a schedule);
- crane and lift planning for transformer unloading (lift radius, outrigger footprint, exclusion zone).

**Roads (farm tracks and site roads).** To verify; these are mostly free guides, not open-source software:
- geosynthetics makers' design guides and calculators for unpaved roads;
- the Giroud–Han method;
- TRL Overseas Road Note 31;
- the Design Manual for Roads and Bridges and the Specification for Highway Works (unbound sub-base, capping, earthworks);
- BS EN 13242 for aggregates.

**Cables and trenches:**
- the Cable Geometry app (our own, proven to 0.0 mm against the Python section);
- IEC 60287 for ratings;
- duct and cable datasheets for bend radius.

Standards are cited by number and clause, never copied.

## 6. The geometry kernel: actual objects, mm accurate
One parametric library in JS. It takes the station library by URL where it exists. Every dimension is labelled MEASURED, DOCUMENTED, DERIVED, ASSUMED or ESTIMATED.

- **Module table (E-W tent):**
  - piles and posts (front and rear), diagonal braces, rafters, purlins and rails;
  - modules, each with its frame, glass and cell grid (bifacial, visible from below), and clamps;
  - DC strings, connectors and the home run.
  - Constraints: the ridge is 3.0 m MEASURED, tilt 8 deg DOCUMENTED, width 24.3 m DOCUMENTED. Tilt cannot exceed 13.9 deg with that ridge and width.
- **Trench:**
  - the dug section: walls or batters, depth, spoil heap volume;
  - bedding sand, ducts as swept tubes, cables inside, cover, warning tape and backfill layers.
  - Width comes from the Cable Geometry maths, with 2 x 100 mm side margins: 325 mm for 1 duct, 1,675 mm for 7.
  - Plan bends are real arcs with radius at least the governing one (the duct's). The audit's bend test is the gate.
- **Road, built for the heavy vehicles that build the site:** "we need to build roads to be able to get heavy vehicles in to lay modules and move transformers around".
  - **Design vehicles:**
    - the module delivery lorry (a 44 t articulated HGV);
    - the transformer low-loader;
    - the mobile crane or HIAB;
    - telehandlers and pile rigs.
    Their dimensions and axle loads are DOCUMENTED from manufacturer data, or ASSUMED and labelled.
  - **Swept path:** turning circles, turning heads and passing places, checked as geometry (the swept envelope of the vehicle along the road centreline must stay on the road).
  - **Build-up from the axle loads and the ground:** formation on the DTM, geotextile or geogrid, capping, unbound sub-base and running surface. Thickness is set by a published method (for example Giroud–Han for unpaved roads) against an ASSUMED CBR until soil data exists. Also width, camber, verges, ditches and gradients the vehicles can climb.
  - **Hardstanding:** crane pads with outrigger bearing pressure, lay-down areas and the transformer set-down beside each station.
  - **Quantities:** m3 and tonnes by layer, and lorry loads of aggregate.
  - **Temporary roads to evaluate as an option:** "some sites might not build roads, they may use a wire mesh temporary road, especially on smaller projects".
    - The options: temporary track mats or panels (steel mesh, aluminium or composite) laid on the ground, against a built aggregate road.
    - Compare, per site, for the same design vehicles:
      - bearing and rutting against the ground (an ASSUMED CBR until soil data exists);
      - the length of mats needed, and laying and lifting days;
      - hire cost against build cost (inputs labelled);
      - reinstatement of the farmland afterwards (topsoil kept, no aggregate left), which matters to the farmer.
    - In the simulator, the mats are real objects: panels with their size and weight, laid along the route by a machine as a phase, lifted and moved to the next area, and the ground under them shown.
- **Station:**
  - pad or piles, bund with pre-drilled entry holes, skid, transformer, RMU and LV boards;
  - **transformer unloading:** the delivery vehicle, the lift plan envelope (crane or HIAB radius, outriggers), the lay-down area and the exclusion zone.
- **Precision rule:** every close-up object stores its vertices relative to a local origin, with the origin in float64. The audit's jitter test is the gate.
- **Procedural world:** the accurate template is instanced across every measured row. Detail steps down with distance; the geometry does not change.

## 6b. Joining the wireframe world to reality in the correct dimensions (measured by the audit)
This is the headache: "we are having issues joining it to the actual reality in the correct dimensions". The audit measured each way a model built in metres goes wrong at the farm (16 million points on a 1 m grid, 0.3 s on the GPU):

| How the model is joined | Error within 50 m | 1 km |
|---|---|---|
| Grid north used as true north (convergence 2.28 deg here) | 2.0 m | 40 m |
| One map anchor, metres scaled at the anchor | 0.5 mm | 196 mm |
| National Grid metres used as ground metres (scale factor 1.000107 here) | 5.4 mm | 112 mm |
| A flat local plane, heights not lowered for the Earth's curve | 0.2 mm | 78 mm |

**The joining rule:**
1. Build every envelope in a local east-north-up frame in ground metres.
2. Convert each vertex from the national grid through the one place frame (OSTN15) to latitude and longitude, and then to the map, in float64.
3. Apply the grid scale factor and the convergence; never assume them.
4. Lower DTM heights by the curve drop.
5. Re-anchor per table or per trench. One close-up at a time makes that cheap, and it keeps the joining error under 1 mm within 50 m.

The pass test for every iteration: three surveyed-style check points per envelope (a pad corner, a table corner, a trench end) placed through the kernel and read back from the rendered map agree with their float64 truth to 1 mm, and with the satellite to the imagery's stated accuracy.

## 7. The construction game loop (typed first, then touch)
- **Phases, each a typed command and an animation, all on measured ground:**
  1. survey;
  2. fence the envelope;
  3. strip topsoil and build roads;
  4. drive piles;
  5. erect tables;
  6. mount modules;
  7. dig trenches, lay ducts and pull cables;
  8. deliver and unload transformers;
  9. energise.
- **Each phase shows:**
  - the state of every object: not built, being built, built;
  - live quantities: trench m, spoil m3, road tonnes, piles, cable km;
  - constraints you can see: bend radius, clearances, the overhead line safety zone, and slope limits for the lift.
- **The build order comes from the site-world engine's own build sequence** (buildBlock marks), imported by URL, never copied.

## 8. Next weekend: three build iterations (the lead's view; merged with the reviewers in section 12)
Each iteration ships as dated versions on main through the CD loop, with a checked version pinned to the homepage at the end.

**Iteration 1: the envelope and ONE table, mm accurate, from drone to under the table on a phone.**
- **Files:** a new envelope scene module, a table kernel module, and their tests.
- **Pass tests:**
  - table dimensions equal the kernel values to 1 mm;
  - outline within 1.0 m of the satellite row edges (top-down z19.3);
  - at walk scale a still camera holds every vertex to 0.5 px;
  - a flight from drone to 1.7 m eye pops no frame over 10 % of pixels;
  - you can look up at the module undersides;
  - 60 fps or more on a mid-range phone profile and 90 or more at 4K;
  - 0 page errors.
- **What you see:** his photo, rebuilt: standing under a real table, looking along the aisle.

**Iteration 2: ONE trench and ONE road, actual, and the first build loop.**
- **Files:** trench and road kernels, and the phase engine.
- **Pass tests:**
  - trench section equals the Python section to 1 mm for 1, 5, 7 and 17 ducts;
  - every bend is feasible at the governing radius;
  - the trench top sits on the DTM to 2 cm;
  - road layers and quantities match a hand calculation to 1 %;
  - typed `dig`, `lay duct`, `pull cable`, `backfill` and `build road` play in order and update the quantities.
- **What you see:** a trench dug, ducted, cabled and backfilled, and a road built in layers, beside the table.

**Iteration 3: the procedural block and the station with transformer unloading.**
- **Files:** instancing from the kernel templates, and the station kernel with the lift plan.
- **Pass tests:**
  - a whole 10 MVA block (tables, trenches, roads, station) builds from templates;
  - draw calls stay under 50;
  - 60 fps on the phone profile;
  - the lift plan's radius and exclusion zone are drawn and checked against the pad;
  - the hand-off in and out of the envelope keeps the pose.
- **What you see:** a block built from nothing by typed phases, walkable, with a transformer lifted onto its pad.

**Why the satellite is not enough:** at close range the satellite view is pixelated (0.34 to 0.75 m pixels) and was "a little unstable" in today's build. The envelope scene carries the close-up world as geometry on measured ground. The satellite stays as the ground texture and the context, never as the object you build on.

**What to cut if credit runs short:**
1. first, the photoreal satellite texture (keep wireframe);
2. then, the lift animation (keep the envelope drawing);
3. never the precision and bend gates.

## 9. The GPU CI audit
- **Code:** `audit/geometry_audit.py` in this repo. It runs on CuPy on the GPU with a NumPy witness on a sample, or NumPy only where there is no GPU.
- **What it measures:**
  1. float32 precision per zoom and at walk scale, for absolute against local-origin storage;
  2. tables as solids on a 0.25 m raster: overlaps, aisles, lattice;
  3. trench bends that physically fit, for radii 0.25 to 3.0 m;
  4. per-module code facts: tests, GL layers, coordinate handling, words and paths that must not be public.
- **Today's numbers:** `audit/GEOMETRY-AUDIT.md`. The whole run took 0.8 s on the RTX 5070 Ti.
- **Gates for next weekend:**

  | Check | Threshold |
  |---|---|
  | Local-origin error | under 0.1 mm |
  | Per-layer jitter at z22 and at walk scale | under 0.5 px |
  | Table overlaps | 0 |
  | Aisles | 1.0 m or more |
  | Bends at the governing radius | 0 infeasible |
  | Modules with a test | at least 80 % |

- **CI:** the NumPy path runs on hosted CI for every push. The CuPy path runs on the self-hosted GPU runner on demand.

## 10. Carried faults (from today's play test and witnesses)
- **Controls and find:**
  - the find box is hidden;
  - the URL does not update as you move;
  - arrival by URL does not stream the tile until you press Walk.
- **Walk and the camera:**
  - Walk outside England is black, and the Wire view there is empty;
  - pitch is fixed in Walk.
- **The plant design ignores measured ground** it has just loaded.
- **Captions fight for the screen,** worst on a phone.
- **Tables:** 2 tables sit 0.8 to 1.55 m off the satellite gaps; 607 tables have poles no AC route reaches; walker ground is 1.04 m off the map terrain at 4 aisles.
- **Engine lock:** its caption overlaps the tables caption; it needs `arrive(why, {e, n})` from the stream.
- **GPU solids:** the trench width misses the side margins; the cutaway drops ducts per segment.
- **CI tolerates two checks** the menu bar broke, and plan-view needs a real GPU.

## 11. Rules
- **Versions:** main only, versions not branches. Every change is a dated, checked version.
- **Geometry first:** nothing counts until it is rendered and looked at.
- **The GPU does the volume;** agents reason on the numbers.
- **Budget:** two Fable agents per round at most, each on a timebox, with scripted gates instead of extra witness agents.
- **Privacy:** no site names on screen or in public files. No private documents, imagery or point clouds in public repos.

## 12. The merged plan: three independent reviews through the furnace
Three reviews were written independently, and each put its claims through the GPU three times:
- the lead's (sections 1 to 11, with the audit);
- **Reviewer 1** (geometry and rendering): about 35 %;
- **Reviewer 2** (engineering truth and process): 25 to 30 %.

### 12.1 What all three agree on, measured
- **Precision is sound: keep it.** Anchor-relative float32 with the anchor folded into a float64 matrix errs by 0.003 px (Reviewer 2) to 0.0076 px (Reviewer 1) at z22 to z24, pitch 85. Absolute float32 would be 18 px at p50 and 1,499 px at max. So the geometry does NOT break from precision; the audit's section 1 is the rule for any new layer.
- **What really breaks when you zoom in:**
  1. **The ground.**
     - The base overlay takes ONE terrain height per block (`overlay.html` wire.render, `queryTerrainElevation` at the anchor). On the farm's DTM, a 200 x 120 m block is 2.7 m out at p50 and 8.6 m at p95 (Reviewer 2).
     - The satellite is draped on a 4.8 m AWS DEM while the wire stands on the 1 m EA DTM (Reviewer 1: median 0.49 m, p95 8 m on a test tile; Reviewer 2: p50 0.10 m, p95 0.98 m at the farm).
     - **Two grounds, and a block that ignores both between its corners.**
  2. **The camera.** MapLibre 4.7.1 caps pitch at 85 deg (`walk-fps.js` PMAX 85), so the view axis reaches only 15 % of the members above you under a table. MapLibre 5 allows pitch beyond 90.
  3. **The members.** Posts, braces, purlins and rafters are single dashed hairlines (`tables.js` 181-206). A 100 mm post at 2 m is 143 px wide at 4K.
  4. **The trench.** Ducts are drawn with sharp corners. In case A4 the largest radius that fits every bend is 0.633 m, and 116 bends fail at 2.0 m.
- **Sprawl:**
  - three table libraries in one page: `mod/engine/` (a v12 copy of 45 files), release 202609270524 (engine-lock), release 202609271853 (tables.js), plus the overlay's own toy `block()`;
  - three generations of rows-from-satellite;
  - five local-frame conventions, and a 0.5 m cell-centre mismatch against the furnace lattice;
  - 4 shader programs and 9 draw sites.
- **The module loader works by luck.** Dynamically inserted scripts are async, but the order matters. The one-line fix is `t.async = false`.
- **CI is not the gate it claims to be.**
  - It runs on SwiftShader, not a real GPU.
  - 4 of 14 test files are tolerated red.
  - 11 checks assert regexes on the module's own source (they test text, not geometry).
  - The 50 self-hosted GPU runners are unused.
- **Labels:** "MEASURED row runs" should read "measured from imagery, relative". The provider georeference is 8.47 m.
- **Pitch:** the code's 26.77 m (24.27 + 2.5) against the fitted 26.5 to 26.6 m (FFT 26.53, S01 26.59, vLiDAR 26.52). The 2.5 m row gap should be a fitted 2.3 m. That 0.24 m per row is the column drift the tables witness caught.
- **The furnace needs guards:** `earthworks` crashes on a box outside the site, and a `layout` job was consumed and never answered.
- **Process cost:** about 3 agent-hours per 100 merged lines last night. At 6 % credit, the GPU runner and the furnace must do the checking, not witness agents.

### 12.2 The one open risk nobody can measure from the air
The under-table structure (posts, braces, purlins, rafters, rails) has no measurement source: no satellite or LiDAR sees it. Without the mounting system maker's general arrangement drawing, or a scaled site photo, those members stay ASSUMED in exactly the place the viewer looks. **Decision needed: the mounting structure drawing (or the maker and model) for the reference table.**

### 12.3 The three iterations for next weekend (merged; the order is binding, the cuts are listed)

**Iteration 1: ONE ground, ONE hero table. From the satellite to under the table without breaking.**
- **Build:**
  - the EA 1 m DTM served as terrarium tiles (a route on the furnace service), so the map's terrain, the satellite drape and the wire stand on the same measured ground;
  - `t.async = false` in the loader;
  - the base wire grounded per vertex, not per block anchor;
  - a HERO tier in `tables.js`: the table nearest the eye gets solid members (12-edge prisms), module frames, rails and the ridge light slot, with its own anchor at the table centre;
  - walk collision includes the tables;
  - a kneel key (eye at 1.0 m).
- **Pass tests:**
  1. decoded terrarium heights within 0.03 m of the DTM at 1,000 nodes;
  2. wire ground within 0.05 m of `queryTerrainElevation` at 1,000 points (today p95 1 to 8 m);
  3. zoom sweep z15 to z22.75 in 0.25 steps: the four table corners' pixels within 0.5 px of the CPU projection;
  4. the table's feet within 0.05 m of the DTM, 0 floating;
  5. width 24.27 +/- 0.01, ridge 3.00, low edge 1.33 m unchanged;
  6. 4K at least 90 fps with the hero plus 80 detail tables;
  7. smoke 14/14 and the privacy scan clean.
- **You see:** the farm photo, one table on its row, and as you zoom it becomes a real frame you walk under, on the same ground the photo sits on.
- **Cut if short:** the kneel key and rails. Never cut tests 2, 3 or 4.

**Iteration 2: look up, and ONE trench dug on real ground.**
- **Build:**
  - MapLibre 5 (pitch beyond 90 in Walk; `transform.elevation` replaced by the 5.x API);
  - the one-close-up LOD by pixels (hero when a post exceeds 1 px, detail when a table exceeds 65 px, outlines beyond);
  - perf.js folded into ONE wire render;
  - one trench chain with filleted bends (R at least the governing duct radius where it fits; every bend that cannot fit listed and drawn red), the floor at DTM minus 1.202 m, and the section at the walker with the real duct count.
- **Pass tests:**
  1. under the table the view axis reaches at least 90 % of hero members within 15 m (today 15 %);
  2. every existing browser test passes on 5.x on a real GPU;
  3. one wire program, one block draw site;
  4. the LOD swap changes under 0.5 % of pixels;
  5. the trench floor on the DTM to 0.01 m along the chain;
  6. the swept volume equals the GPU raster volume within 1 %;
  7. 0 chains across a table.
- **You see:** under the table you tilt up to the purlins, the module undersides and the light slot; you then walk one AC trench from a table to its station, dug into the real ground profile.
- **Cut if short:** the deletions of the old row detectors, and the X-ray view. Never cut the upgrade or the fillets.
- **Fallback:** if MapLibre 5 cannot hold eye-level walking at 90 fps, build the separate envelope scene of section 4 instead. The pass test is the same.

**Iteration 3: the construction envelope, the procedural site, roads, and CI on the GPU.**
- **Build:**
  - `site-box.js`: the fence-line envelope in one ENU frame, re-anchored every 250 m, with the joining rule;
  - every measured row gets an instance of the hero template, placed per pile on the DTM by the site-world block-build rule (the frame follows the ground per pile line);
  - ONE table library pinned by URL, with the `mod/engine/` copy and the toy `block()` deleted;
  - a road kernel for the design vehicles (build-up, quantities, swept path) and the temporary mat option;
  - the GPU audit plus the reviewers' checks in CI on a self-hosted GPU runner (matrix at most 12), with 0 tolerated tests;
  - the furnace guards;
  - a checked version pinned on the homepage with the audit JSON's sha.
- **Pass tests:**
  1. join error under 15 mm at 250 m inside the envelope;
  2. pile feet within 0.05 m of the DTM at 10,000 feet;
  3. top-down render against the satellite: IoU at least 0.10 above the dark-everywhere baseline, edge residual p50 under 1.0 m;
  4. table overlaps 0 m2 and aisles under 1 m 0 (today 913 m2 and 27);
  5. one engine import URL in the repo;
  6. the GPU CI green in under 15 minutes;
  7. 639 instances at 4K at least 90 fps, one draw call per LOD tier.
- **You see:** a fenced construction site cut into the satellite, every table the one you approved, standing on measured ground, roads with their layers and quantities, and a CI page with the numbers.
- **Cut if short:** in order, (a) the DSM-hillshade lock test, (b) the mat animation, (c) the fence animation.

**Estimates:**

| Plan | Agent-hours |
|---|---|
| Reviewer 1 | 48 (14 + 16 + 18) |
| Reviewer 2 | 28 to 40 |
| Lead | 11 |

**Budget:** plan for two Fable builders per iteration with the GPU doing the checking. If the credit allows only one iteration, do iteration 1 whole.

**Transformer unloading** (the lift plan and the station kernel) moves to the weekend after, unless iteration 3 finishes early.

## 13. THE AGREED PLAN (supersedes section 12.3): argued with a Fable challenger, PLAN SOLD

The direction on 28 Sept at 15:50: a first-person walk, and a dashboard to choose the table arrangement (portrait or landscape, modules per column, modules in series; fixed south, east-west as REPD 6502 (5P per face) or sample L (5L per face), or a tracker 1P or 2P), reusing the Kuiper 2D engine and its layout chooser. Round 1 made 10 objections; the lead conceded 10 with three pushbacks and five demands; round 2 ruled 14 of 15 items SOLD and sold item 9 with one change (plain solids in iteration 1, the hero look in iteration 3). The spec's ITERATIONS block is the agreed plan (22 pass tests, at most 24 agent-hours).


The product for the weekend: the FPS walk and the layout dashboard, driving ONE table kernel on ONE ground.
Cap 24 agent-hours; at most two Fable builders at once; scripted gates, no witness agents.
Trench, roads, mats, fence and the lift go to the weekend after, with the kernel interfaces ready.
No site names: "REPD 6502" and "sample L" only.

## Rulings on the lead's ten answers

1. SOLD. The dashboard driving one kernel is iteration 1; the 48-combination kernel matrix is its pass test.
2. SOLD. 2P carries the cartridge's tube gap between tiers; rotation limit (55 deg seen) and stow (0) are parameters
   labelled TO-SOURCE; tube height 1.7 m 1P ESTIMATED, 2.3 m 2P ASSUMED. Labels stay on until a maker source arrives.
3. SOLD. structures.mjs FORMATS widened (the product's own copy). station.mjs is imported by URL and never copied.
   One note, not a condition: station.mjs defaults are tilt 10 and height 1.2, so the 1 mm reconciliation test must
   pass the REPD 6502 params explicitly (rows 5, columns 90, tilt 8, height 1.33, ridgeGap 0.5). Checked in the
   0524 release: tableShape(:42) gives width 2 x depth + ridgeGap = 24.27 m with those numbers.
4. SOLD. One ground first; the walk tests do not count until "wire ground vs queryTerrainElevation <= 0.05 m at
   1,000 points" passes. The ground gate is rerun at the top of iteration 2.
5. SOLD. Kernel output carries inverter position, string home-run points, pile list, aisle and corridor widths; the
   test is sharpened to "present AND non-null" for every structure and preset (an empty field would pass "exists").
6. SOLD. One kernel at prototype/mod/kernel/table.mjs; tables.js FARM and the toy block() go; the grep counts the
   product's own code only, station.mjs by URL excepted.
7. SOLD. The round 1 notes found the live /kuiper/ pointer still carries cartridge 202609200009 (no `fire string`);
   the maths is in the i0097 dev build only. So the plan writes the port as the default path (header naming
   009700000000-kuiper-programs.js:706-722 and BOXES :1102-1112; 20-case match test) and the URL import as a
   one-curl check first, not a branch of work.
8. SOLD.
9. NOT SOLD as stated; sold with one change. The spec's reviewers put ground + hero table at 10 to 14 h; the lead
   now caps iteration 1 at 9 h and adds the kernel and the dashboard to it. That only fits if the hero look
   (12-edge prisms, module frames, rails, light slot, the explorer standard) leaves iteration 1. AGREED: iteration 1
   draws plain solids (modules as boxes, posts and tubes as tubes); the hero close-up is iteration 3.
   Hours: iteration 1 7-9 h, iteration 2 6-8 h, iteration 3 5-7 h; maximum 24.
10. SOLD. Presets: REPD 6502 tent (5P per face, 24.27 m), sample L tent (5L per face, 13.49 m), a 2P tracker, and
    the south fixed default.

## Rulings on the five demands

A. SOLD, and checked. protocol.js:107-114 holds coldVoc, hotVmp, coldVmp and the checks against maxVoltage,
   minMpptVoltage and maxMpptVoltage. With the DEFAULT module (voc 45.9 V, betaVoc -0.25 %/K) at -10 C:
   30 in series = 1,497.5 V, accepted against 1,500 V; 31 = 1,547.4 V, refused; hot Vmp at 70 C = 988.7 V,
   above the 500 V minimum. The test now asserts both 30 and 31 so it discriminates, not just "matches".
B. SOLD (see 4).
C. SOLD. the direction's engines are the standard: station.mjs reconciled to 1 mm for the REPD 6502 preset; the
   explorer (graphics-engines-open-source) is the look for the hero close-up in iteration 3.
D. SOLD. Kernel output in local ENU metres anchored per table; join under 1 mm within 50 m (the audit shows
   0.0005 m at 50 m for one Mercator anchor, so the gate is achievable); 0 infeasible bends is the trench gate for
   the weekend after and stays in the spec's GATES.
E. SOLD. Two Fable builders at most; the GPU runner runs the matrix; gates are scripts.

## PLAN SOLD

Sold once item 9 is taken as written above (plain solids in iteration 1, hero look in iteration 3).

## The three iterations (the code is in iterations-agreed.mjs; checked against the spec's self-check: gaps 0)

### Iteration 1 (7-9 h): ONE ground, ONE kernel, ONE dashboard
- EA 1 m DTM as terrarium tiles and the map terrain; wire grounded per vertex; t.async = false.
- prototype/mod/kernel/table.mjs: buildTable(params) -> solids (box | tube | prism), dims, labels, inverter,
  homeRuns, piles, widths; local ENU metres anchored at the table centre. Parameters: mounting fixed | east-west |
  tracker; orientation portrait | landscape; modulesUpSlope 1..6 per face; faces; modulesInSeries 1..60; bayModules;
  postLinesPerFace; tilt; lowEdge; rotationLimitDeg; stowDeg; tubeHeight; the 2P tube gap.
- Series is electrical: Kuiper BOXES as the dashboard schema, validate() ranges, the three voltage checks live; an
  illegal count is refused with the numbers shown.
- station.mjs by URL as the reference; structures.mjs FORMATS widened; FARM and block() deleted.
- Tests: terrarium decode 0.03 m; one ground 0.05 m at 1,000 points; reconcile station.mjs to 0.001 m; the 48-way
  kernel matrix on the GPU runner; series electrical (30 accepted, 31 refused); feet on ground; dashboard drives
  kernel in GPU Chrome; baseline.
- Cut if short: the sample L preset and the stow parameter. Never the one-ground, reconciliation or series tests.

### Iteration 2 (6-8 h): walk it
- walk-fps.js: WALK about 10 m/s, RUN 33 m/s, pitch cap removed, kneel (eye 1.0 m); collision against kernel posts
  and table solids; phone stick and gyro look; every measured row instanced from the kernel, placed per pile.
- Tests: ground gate rerun; speeds from the URL position delta; 0 pass-throughs on 20 posts; look-up coverage
  >= 90 %; kneel 1.0 m; 10,000 pile feet <= 0.05 m; 90 fps at 4K and 60 fps on the phone profile.
- Cut if short: gyro look and the phone stick. Never the ground gate, collision or speeds tests.

### Iteration 3 (5-7 h): the hero close-up, the join rule, CI, the interfaces
- Hero tier from the same kernel output at the explorer standard; envelope.js join checked at 50 m; per-table JSON
  of inverter, homeRuns, piles and widths for the weekend-after kernels; the kernel, reconciliation, series and walk
  tests in CI on the self-hosted GPU runner (matrix <= 12, 0 tolerated); a checked version pinned.
- Tests: hero dimensions (24.27 and 13.49 +/- 0.01, ridge 3.00, low edge 1.33); hero look passed by the direction,
  not an agent; join < 0.001 m within 50 m; interfaces non-null for every structure; one engine (grep); GPU CI
  green under 15 min; baseline.
- Cut if short: the tracker clamps, then the homepage pin. Never the join or interfaces tests.

## Open items carried, labelled
- TO-SOURCE: tracker rotation range, stow and drive-post spacing; member sections and spacings; the mounting GA.
- ESTIMATED: tube height 1.7 m (1P). ASSUMED: 2.3 m (2P).
- walk-fps.js today: WALK 1.4, RUN 6, PMAX 85 (round 1 notes); the direction's values replace them in iteration 2.

## 14. THE TIGHT SCOPE (28 Sept, 3 % credit; overrides section 13's order where they differ)

**Why tighten.** A Fable critic judged the sold plan about 40 % likely to get the wireframe working in one weekend. The two hardest jobs had no hours: serving the EA terrain as map tiles, and freeing the camera. With those two done first by the machine and iteration 3 deferred, it judged the chance about 65 %.

**The order:**
- **A.** Bake the terrain tiles (a script).
- **B.** A one-page MapLibre 5 spike, in a scratch copy only.
- **C.** Five safe fixes.
- **D.** One ground.
- **E.** One table kernel lifted from tableAssembly.
- **F.** The Kuiper chooser and the series check.
- **G.** The layout dashboard.
- **H.** Stretch: a cable schedule from the kernel. The owner is a cable company, so the quantities are the commercial point.

**Deferred:**
- iteration 3;
- MapLibre 5 on main;
- trenches, roads, mats, fence and lift;
- the proximity and capacity layer;
- any homepage pin change.

**Done means:**
- one ground at or under 0.05 m;
- the 48-way kernel matrix builds, and the REPD 6502 preset reconciles to 1 mm;
- 30 in series accepted and 31 refused;
- the dashboard redraws the farm;
- the baseline gates are green, and the audit has been rerun.

**Cost.** The honest estimate is 27 to 40 agent-hours. The 24 h cap holds only if A runs as a script and H is dropped. The machine-readable version is `TIGHT` in docs/next-weekend.spec.mjs.

