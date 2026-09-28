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

## 12. The merged plan (after the reviewers and the furnace)
To be appended below.
