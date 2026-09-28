// next-weekend.spec.mjs: the construction simulator scope as code. Every measurement carries value, unit, label and
// source; every task carries files, commands and pass thresholds. Run `node docs/next-weekend.spec.mjs` to check that
// the spec is complete (it exits 1 and names the gap if any entry lacks a field). Written 28 Sept 2026 by the lead.
// Labels: MEASURED (read from satellite, LiDAR or shadow), DOCUMENTED (planning or datasheet), DERIVED (arithmetic from
// those), ASSUMED (a choice, no source), ESTIMATED (modelled where no camera sees), TO-SOURCE (needed, not yet found).
// Companion documents: docs/NEXT-WEEKEND-SCOPE.md (the prose), audit/GEOMETRY-AUDIT.md and audit/audit.json (numbers).

const m = (value, unit, label, source, extra = {}) => ({ value, unit, label, source, ...extra });

export const META = {
  written: '2026-09-28 14:50 Europe/London',
  target: 'A real-life construction simulator: a construction envelope inside the satellite view where you walk and build, like a 3D game, on a phone, with actual roads, trenches, module tables and stations, mm accurate on measured ground',
  repos: {
    simulator: { url: 'https://github.com/Ventusltd/energy-transition-simulator', main: '900fd7c', note: 'main only, no branches; every commit ships as a dated version within 5 minutes' },
    scanner: { url: 'https://github.com/Ventusltd/wire-frame-scanner', main: '0665f4e', note: 'this repo: rules R1-R5, the GPU audit, this scope' },
    engine: { url: 'https://globalgrid2050.com/solar-design-studio/202609270524-site-world/world/', note: 'site-world release imported BY URL: block-build.mjs, station.mjs, block-mv.mjs, cable-rating.mjs; never copied' },
    explorer: { url: 'https://ventusltd.github.io/graphics-engines-open-source/', note: 'the geometry standard (explore.mjs: pulses, walk-cable)' },
    bar: { url: 'https://globalgrid2050.com/solar-design-studio/202609262041-site-world/', note: 'the bar for a proper virtual simulated site world' },
    cableGeometry: { url: 'https://globalgrid2050.com/cable_geometry/', note: 'getGroupGeometry, data-*.js catalogue' },
  },
  live: {
    latest: 'https://globalgrid2050.com/energy-transition-simulator/latest/?lat=51.33877&lon=0.91388',
    homepagePin: { version: '202609281316', where: 'globalgrid2050.com homepage, Solar Design Studio > Energy Transition Simulator (preview)' },
  },
};

// ------------------------------------------------------------------------------------------------ measured facts
export const FACTS = {
  imagery: {
    date: m('2025-03-29', 'date', 'MEASURED', 'imagery metadata at the farm'),
    pixelZ17: m(0.7461, 'm/px', 'MEASURED', 'Esri z17 mosaic'),
    nativeResolution: m(0.34, 'm', 'DOCUMENTED', 'provider metadata'),
    statedAccuracy: m(8.47, 'm', 'DOCUMENTED', 'provider metadata; the absolute tie of any photo-fitted geometry'),
    modelToImageShift: m([-0.074, -0.316], 'm (E, N)', 'MEASURED', 'vLiDAR-vs-satellite fit, block S01; relative only'),
  },
  table: {
    type: m('E-W tent, paired back to back', '-', 'MEASURED', 'satellite rows and the reference under-table photo'),
    widthAcross: m(24.27, 'm', 'DOCUMENTED', 'planning hints 24.3 m; tables.js farmParams 24.27'),
    ridgeHeight: m(3.0, 'm', 'MEASURED', 'shadow length, +/- 0.5 m; LM fit 3.34 (3.3 +/- 0.5 per row)'),
    tilt: m(8, 'deg', 'DOCUMENTED', 'planning; not identifiable from the imagery'),
    tiltMax: m(13.9, 'deg', 'DERIVED', 'low edge = ridge - 12.15 tan(tilt) >= 0'),
    lowEdge: m(1.33, 'm', 'DERIVED', '3.0 - 12.13 tan 8 deg (1.29 to 1.33 by half-width basis)'),
    pitch: m(26.8, 'm', 'DOCUMENTED', 'planning; measured 26.83 (tables.js), 26.59 (S01 lattice), 26.52 (vLiDAR witness)'),
    aisleGap: m(2.5, 'm', 'DOCUMENTED', 'planning; measured median 2.56 m between tables (GPU audit)'),
    ridgeGap: m(0.5, 'm', 'DOCUMENTED', 'station library default ridgeGap'),
    northShadowTrim: m(3.0, 'm', 'MEASURED', 'north ends of the row mask read long by the shadow'),
    moduleLength: m(2.384, 'm', 'DOCUMENTED', 'station library default moduleLength'),
    moduleWidth: m(1.303, 'm', 'DOCUMENTED', 'station library default moduleWidth'),
    moduleGap: m(0.02, 'm', 'DOCUMENTED', 'station library default moduleGap'),
    modulesAcrossPerSide: m(5, 'modules', 'DOCUMENTED', 'station library default rows'),
    columnsMax: m(90, 'columns', 'DOCUMENTED', 'station library default columns; tables are cut to the measured run'),
    rowBearing: m(2.404, 'deg east of grid-aligned north in the image', 'MEASURED', 'completion fit M1; LM fit 87.649 deg from east'),
    tablesDrawn: m(639, 'tables', 'DERIVED', 'tables.js on the measured rows (Node); 648 in the browser frame'),
    coverageOnRuns: m(96.02, '%', 'DERIVED', 'tables test'),
    posts: m(null, '-', 'TO-SOURCE', 'post spacing, section and pile type: from the reference photo and station library; else ASSUMED and labelled'),
    braces: m(null, '-', 'TO-SOURCE', 'diagonal braces as in the reference photo'),
    purlinsRafters: m(null, '-', 'TO-SOURCE', 'sections and spacing'),
  },
  trench: {
    ductPE125: m({ od: 125, id: 110.2 }, 'mm', 'DOCUMENTED', 'PE SDR17 duct table in the trench model'),
    lvSingleCoreOD: m({ default: 31.5, min: 29.7, max: 33.5 }, 'mm', 'ASSUMED', '3 x 1C 400 mm2 Al XLPE/PVC unarmoured; no catalogue entry yet'),
    lvSingleCoreMBR: m({ default: 472, min: 356, max: 503 }, 'mm', 'ASSUMED', '15 x OD single-core basis'),
    ataOD: m(37.40, 'mm', 'DOCUMENTED', 'Cable Geometry catalogue sc_al_ata_ac_400'),
    ataMBR: m(449, 'mm', 'DOCUMENTED', '12 x OD, catalogue'),
    duct90Bend: m(1800, 'mm', 'DOCUMENTED', 'PE 90 mm datasheet in the duct table'),
    trenchDepth: m(1.202, 'm', 'DOCUMENTED', 'planning hints'),
    cover: m(0.91, 'm', 'DOCUMENTED', 'farmland cover used by the trench lane'),
    ductCentreDepth: m(1.0645, 'm', 'DERIVED', 'X-ray model section'),
    ductPitch: m(0.225, 'm', 'DERIVED', 'X-ray model section'),
    sideMargin: m(0.100, 'm each side', 'DOCUMENTED', 'v2 export formula; missing in the GPU solids build'),
    width1Duct: m(0.325, 'm', 'DERIVED', 'OD + 2 x 0.100'),
    width7Ducts: m(1.675, 'm', 'DERIVED', '7 x 0.125 + 6 x 0.100 + 2 x 0.100'),
    caseA4: m({ trench_km: 58.61, routes: 668, cables: 2004, cable_km: 432.7, bend_flags: 447 }, 'mixed', 'DERIVED', 'ac-trenches-6502.json totals'),
    largestRadiusThatFitsEverywhere: m(0.633, 'm', 'DERIVED', 'GPU audit, case A4 (0.691 in the other cases)'),
    infeasibleBendsAt2m: m([84, 135], 'vertices per case (min, max)', 'DERIVED', 'GPU audit'),
  },
  station: {
    sites: m(24, 'sites', 'MEASURED', 'two scouts agree within 6.3 m: 10 skids, 12 bunds, 2 pads'),
    planningHubs: m({ hubs: 22, units: 56 }, 'count', 'DOCUMENTED', 'planning'),
    bundS01: m([17.2, 13.4], 'm', 'MEASURED', 'stations file, +/- 1.1 m'),
    unit: m({ skid: [6.1, 2.9, 3.0], base: [10.0, 7.7] }, 'm', 'DOCUMENTED', 'planning hints'),
    referenceStation: m({ inverters: 28, kVA: 352, V: 800, transformers: '2 x 5 MVA', feedersPerBus: 14 }, 'mixed', 'DOCUMENTED', 'reference 10 MVA station design'),
    padLevelS01: m(1.420, 'm ODN', 'MEASURED', 'engine lock vs EA DTM 1.422 m'),
  },
  grid: {
    towerHeight: m(48.5, 'm', 'MEASURED', 'shadow; skeptic adds +1.4 to +3.3 m'),
  },
  frames: {
    convergence: m(2.276, 'deg', 'DERIVED', 'GPU audit (Airy TM series) at the register point; engine lock read 2.260 at S01'),
    gridScaleFactor: m(1.0001071, '-', 'DERIVED', 'GPU audit at the register point'),
    ostn15Shift: m(2.17, 'm', 'MEASURED', 'play test readout'),
    earthRadius: m(6371008.8, 'm', 'DOCUMENTED', 'mean radius'),
  },
  performance: {
    fps1080: m(103.6, 'fps', 'MEASURED', 'play test, drone, RTX 5070 Ti D3D11'),
    fps4k: m(99.8, 'fps', 'MEASURED', 'live 202609281316'),
    fpsPhone: m(103.0, 'fps', 'MEASURED', 'play test, 390x844 touch profile on the desktop GPU (not a real phone)'),
    firstFrame: m(1088, 'ms', 'MEASURED', 'play test, farm, 1080p'),
  },
};

// ------------------------------------------------------------------------------------------------ the GPU audit
export const AUDIT = {
  run: 'python audit/geometry_audit.py --repo <simulator clone> --out <folder>',
  seconds: m(1.1, 's', 'MEASURED', 'RTX 5070 Ti, CuPy 14.2; NumPy witness on a sample every time'),
  precision: {
    absFloat32MaxError: m(0.834, 'm', 'MEASURED', '2,127,108 module corners, absolute Mercator float32'),
    rtcFloat32MaxError: m(0.0000622, 'm', 'MEASURED', 'same points, relative to a local origin'),
    absAtWalk2m: m(390, 'px', 'DERIVED', 'member 2 m from a 1.7 m eye, 60 deg FOV, 1080 px'),
    rtcAtWalk2m: m(0.029, 'px', 'DERIVED', 'same'),
    jitter1cmStep: m(1.267, 'm', 'MEASURED', 'absolute float32 pipeline, camera moved 1 cm'),
  },
  tables: {
    overlappingPairs: m(15, 'pairs', 'MEASURED', '0.25 m raster, 45 M cells'),
    overlapArea: m(913, 'm2', 'MEASURED', 'same'),
    aislesUnder1m: m(27, 'aisles', 'MEASURED', 'nearest east neighbour gap'),
    aisleMedian: m(2.56, 'm', 'MEASURED', 'same'),
    latticeNote: m('median 4.9 m off one global 26.83 m comb', '-', 'DERIVED', 'blocks have their own phase; the metric needs per-block combs next time'),
  },
  join: {
    oneMercatorAnchor: m({ at50m: 0.0005, at1km: 0.196, at2km: 0.785 }, 'm', 'DERIVED', '16,008,001 points, 1 m grid, 4 x 4 km'),
    gridMetresAsGround: m({ at50m: 0.0054, at1km: 0.112, at2km: 0.234 }, 'm', 'DERIVED', 'same'),
    gridNorthAsTrue: m({ at50m: 1.987, at1km: 39.9, at2km: 80.2 }, 'm', 'DERIVED', 'same'),
    flatPlaneDrop: m({ at50m: 0.0002, at1km: 0.078, at2km: 0.314 }, 'm', 'DERIVED', 'same'),
  },
  code: {
    modules: m(25, 'modules', 'MEASURED', 'prototype/mod/*.js'),
    lines: m(5459, 'lines', 'MEASURED', 'same'),
    withOwnTest: m(10, 'modules', 'MEASURED', 'tests/<module>*.cjs exists'),
  },
};

// ------------------------------------------------------------------------------------------------ rules
export const RULES = {
  join: [
    'Build each envelope in a local east-north-up frame in ground metres, origin at the envelope (or per table / trench).',
    'Convert every vertex national grid -> OSTN15 (the one place frame, PF) -> lat/lon -> map, in float64 on the CPU.',
    'Apply the grid scale factor and convergence; never assume grid north or grid metres.',
    'Lower DTM heights by d^2 / (2 R) when placing them in a flat local plane.',
    'Store GPU vertices relative to the origin in float32; fold the origin into the matrix in float64 before upload.',
  ],
  view: [
    'One close-up object at a time (the table or trench nearest the eye) at full detail; everything else instanced from the same template.',
    'The satellite is the ground texture and context, never the object you build on.',
    'Wireframe is the look; the solids behind it are exact.',
    'Phone first; WebXR optional; no headset needed.',
  ],
  process: [
    'Main only, versions not branches; the CD loop ships each gated main commit.',
    'Geometry first: render and look before claiming.',
    'The GPU does the volume; agents reason on the numbers.',
    'At most two Fable agents per round, timeboxed; scripted gates replace extra witness agents.',
    'Never kill processes by name; kill only PIDs you started.',
    'No site names, private documents, imagery or point clouds in public repos; no drive paths.',
  ],
};

// ------------------------------------------------------------------------------------------------ architecture
export const ARCH = {
  views: {
    mapShell: 'MapLibre overlay as today: arrive, typed find, satellite, drone and helicopter, plan, GridAtlas, R5 ground',
    envelope: 'first-person scene (three.js-class, MIT) in a local ENU frame; DTM mesh of the R5 tiles as ground, satellite tile as texture; free camera with look up/down, walk, kneel, fly, collision',
    handoff: 'flying down into the envelope morphs into the envelope scene at the same pose; leaving morphs back; one shared model',
  },
  files: {
    'prototype/mod/envelope.js': 'createEnvelope({ e, n, radius_m }) -> { origin, toLocal(e,n,h), toMap(x,y,z), ground(x,y), dispose() }; the join rule lives here',
    'prototype/mod/kernel/table.mjs': 'buildTable(params) -> { solids: [{ name, kind: "box"|"tube"|"prism", dims_m, transform }], dims, labels } from the station library by URL',
    'prototype/mod/kernel/trench.mjs': 'trenchSection(n, od_mm, formation, installation, duct) and sweepTrench(route, section, R_min) -> solids; section maths ported from the Python trench_section (0.0 mm vs the Cable Geometry app)',
    'prototype/mod/kernel/road.mjs': 'buildRoad(centreline, vehicle, ground, method) -> layers with thickness, width, camber, quantities; swept path check',
    'prototype/mod/kernel/mats.mjs': 'layMats(route, panel) -> panels with size, weight, count, lay/lift phases',
    'prototype/mod/kernel/station.mjs': 'buildStation(kind: "bund"|"pad"|"piles", units) and liftPlan(vehicle, crane, pad) -> radius, outriggers, exclusion zone',
    'prototype/mod/phases.js': 'the typed build loop: survey, fence, roads, piles, tables, modules, trench, duct, cable, backfill, deliver, lift, energise; states not-built / building / built; live quantities',
    'tests/envelope.cjs, tests/kernel-*.cjs, tests/phases.cjs': 'Node tests for every kernel function plus GPU Chrome checks',
  },
  literature: {
    xr: ['W3C WebXR Device API', 'Khronos OpenXR (SDK Apache-2.0)', 'Monado OpenXR runtime', 'Valve OpenVR SDK (BSD-3)', 'three.js WebXR examples (MIT)'],
    take: ['1:1 metric scene graph', 'ray picking, grab, snap, place', 'phone locomotion: virtual stick, gyro look, teleport', 'comfort: snap turn, vignette', '72-90 fps frame budget'],
    construction: ['IFC 4.3: IfcAlignment, IfcEarthworksCut, IfcTask, IfcWorkSchedule', '4D sequencing', 'crane lift planning'],
    roads: ['Giroud-Han unpaved road method', 'TRL Overseas Road Note 31', 'DMRB and Specification for Highway Works (unbound sub-base, capping, earthworks)', 'BS EN 13242 aggregates', 'geosynthetics makers\' free design guides (to verify)'],
    licenceCheck: 'every licence is checked from the package metadata at use; standards cited by number and clause, never copied',
  },
};

// ------------------------------------------------------------------------------------------------ kernel parameters
export const KERNEL = {
  table: {
    uses: ['FACTS.table.*'],
    members: ['piles', 'front posts', 'rear posts', 'diagonal braces', 'rafters', 'purlins', 'rails', 'modules (frame, glass, cell grid visible from below)', 'clamps', 'DC strings, connectors, home run'],
    rule: 'every member is a solid; the wireframe is its edges',
  },
  trench: {
    uses: ['FACTS.trench.*'],
    members: ['cut in the DTM', 'walls or batters', 'bedding sand', 'ducts (swept tubes)', 'cables inside', 'cover', 'warning tape', 'backfill layers', 'spoil heap'],
    rule: 'plan bends are arcs with R >= the governing radius (the duct); the audit bend test is the gate',
  },
  road: {
    vehicles: {
      moduleLorry: m({ gross_t: 44, type: 'articulated HGV' }, 'mixed', 'TO-SOURCE', 'UK maximum gross weight is 44 t; axle loads and swept path from a manufacturer'),
      transformerLowLoader: m(null, '-', 'TO-SOURCE', 'transformer mass and trailer data from the supplier'),
      crane: m(null, '-', 'TO-SOURCE', 'mobile crane or HIAB: radius, outrigger spread and pad loads'),
      telehandler: m(null, '-', 'TO-SOURCE', 'module handling on site'),
      pileRig: m(null, '-', 'TO-SOURCE', 'pile rig track pressure'),
    },
    layers: ['formation on the DTM', 'geotextile or geogrid', 'capping', 'unbound sub-base', 'running surface'],
    design: m('Giroud-Han against an ASSUMED CBR until soil data exists', '-', 'ASSUMED', 'method choice'),
    checks: ['swept path stays on the road', 'gradient within the vehicle limit', 'passing places and turning heads', 'crane hardstanding bearing pressure'],
    temporaryMats: {
      options: ['steel mesh', 'aluminium panels', 'composite mats'],
      compare: ['bearing and rutting vs CBR', 'mats needed and lay/lift days', 'hire vs build cost (inputs labelled)', 'farmland reinstatement: topsoil kept, no aggregate left'],
    },
  },
  station: {
    uses: ['FACTS.station.*'],
    members: ['pad or piles', 'bund with pre-drilled entry holes (7 per side, scenario A)', 'skid', 'transformer', 'RMU', 'LV boards'],
    unloading: ['delivery vehicle', 'lift plan envelope (crane or HIAB radius, outriggers)', 'lay-down area', 'exclusion zone'],
  },
};

// ------------------------------------------------------------------------------------------------ gates (every push)
export const GATES = [
  { name: 'smoke', cmd: 'node tests/overlay-smoke.cjs', pass: '14 passed, 0 failed' },
  { name: 'module tests', cmd: 'node tests/<module>.cjs for every changed module', pass: 'all PASS' },
  { name: 'GPU blank check', cmd: 'blank-check.cjs <url> <png> then dark.py <png>', pass: 'VISIBLE (dark < 35 %), window.SIM and the canvas present' },
  { name: 'fps 4K', cmd: 'fps4k.cjs <url>', pass: '>= 90 fps, 0 page errors' },
  { name: 'phone', cmd: 'Pixel 7 profile, 20 s at the farm', pass: '>= 60 fps, 0 page errors, no caption taller than 25 % of the viewport' },
  { name: 'GPU audit', cmd: 'python audit/geometry_audit.py --repo . --out audit-out', pass: 'RTC error < 0.1 mm; table overlaps 0; aisles >= 1.0 m; bends feasible at the governing radius' },
  { name: 'privacy', cmd: 'names scan (hashed list) + drive-path grep', pass: '0 hits' },
];

// ------------------------------------------------------------------------------------------------ the three iterations
const t = (name, cmd, threshold) => ({ name, cmd, threshold });
export const ITERATIONS = [
  {
    id: 1, goal: 'The envelope and ONE table, mm accurate, from drone to under the table, on a phone',
    files: ['prototype/mod/envelope.js', 'prototype/mod/kernel/table.mjs', 'tests/envelope.cjs', 'tests/kernel-table.cjs'],
    tests: [
      t('table dimensions', 'node tests/kernel-table.cjs', 'every dimension = FACTS/library to 1 mm; labels present'),
      t('join check points', 'GPU Chrome: 3 check points (pad corner, table corner, trench end) placed and read back', '<= 1 mm vs float64 truth'),
      t('on the satellite', 'offs.cjs + prof.py at z19.3 top-down', 'outline within 1.0 m of the satellite row edges'),
      t('still-camera jitter', 'GPU Chrome, camera still at 1.7 m eye, 60 frames', 'every vertex within 0.5 px'),
      t('flight without breaking', 'record drone z16 pitch 60 -> 1.7 m eye under the table', 'no frame changes > 10 % of pixels'),
      t('look up', 'ArrowUp / drag under the table', 'pitch changes >= 10 deg; module undersides in view'),
      t('frame rate', 'fps4k.cjs and the phone profile', '>= 90 at 4K, >= 60 phone, 0 errors'),
    ],
    sees: 'His photo rebuilt: standing under a real table, looking along the aisle, the light slot above.',
    agentHours: m(3, 'h', 'ASSUMED', 'one Fable modeller plus scripted gates'),
    cutIfShort: 'the cell grid texture (keep module frames)',
  },
  {
    id: 2, goal: 'ONE trench and ONE road (or mat road), actual, and the first typed build loop',
    files: ['prototype/mod/kernel/trench.mjs', 'prototype/mod/kernel/road.mjs', 'prototype/mod/kernel/mats.mjs', 'prototype/mod/phases.js', 'tests/kernel-trench.cjs', 'tests/kernel-road.cjs', 'tests/phases.cjs'],
    tests: [
      t('trench section', 'node tests/kernel-trench.cjs vs Python trench_section', 'width and depth equal to 1 mm for 1, 5, 7, 17 ducts'),
      t('bends feasible', 'GPU audit bend test on the built route', '0 bends tighter than the governing radius'),
      t('on the ground', 'trench top vs lidar-stream heightAt', '<= 2 cm along the segment'),
      t('road layers', 'node tests/kernel-road.cjs vs a hand calculation', 'thickness and quantities within 1 %'),
      t('swept path', 'design vehicle along the centreline', 'envelope stays on the road'),
      t('build loop', 'typed dig, lay duct, pull cable, backfill, build road', 'phases play in order; quantities update'),
    ],
    sees: 'A trench dug, ducted, cabled and backfilled, and a road built in layers, beside the table.',
    agentHours: m(4, 'h', 'ASSUMED', 'two Fable modellers in parallel'),
    cutIfShort: 'the mat road animation (keep its quantities)',
  },
  {
    id: 3, goal: 'The procedural block and the station with transformer unloading',
    files: ['prototype/mod/kernel/station.mjs', 'instancing in prototype/mod/envelope.js', 'tests/kernel-station.cjs'],
    tests: [
      t('block from templates', 'build a 10 MVA block by typed phases', 'tables, trenches, roads and station all from kernel templates'),
      t('draw calls', 'renderer info', '< 50'),
      t('phone frame rate', 'phone profile', '>= 60 fps'),
      t('lift plan', 'kernel-station test', 'radius and exclusion zone drawn and checked against the pad'),
      t('hand-off', 'fly in and out of the envelope', 'pose kept to 0.1 m and 0.5 deg'),
    ],
    sees: 'A block built from nothing by typed phases, walkable, with a transformer lifted onto its pad.',
    agentHours: m(4, 'h', 'ASSUMED', 'two Fable modellers'),
    cutIfShort: 'the lift animation (keep the envelope drawing)',
  },
];

// ------------------------------------------------------------------------------------------------ carried faults
const f = (id, repro, observed, expected) => ({ id, repro, observed, expected });
export const FAULTS = [
  f('F01', 'arrive; press / or f; open every menu', 'the find box (#fg-in) stays hidden', 'visible top centre on load'),
  f('F02', 'go SN 92 65; click Walk', 'black screen, z17.2, pitch 24', 'walk on map terrain anywhere; Wire view never empty'),
  f('F03', 'in Walk press ArrowUp / drag', 'pitch fixed at 80', 'look up and down'),
  f('F04', 'press G; look for a GridAtlas link', 'nothing', 'a switch carrying the current lat/lon'),
  f('F05', 'Scope > Assess land in Wales', 'nothing drawn', 'land grade, fields and flood on screen'),
  f('F06', 'plant 50mw where the receipt shows EA LiDAR', 'caption: ground taken as flat', 'design on the streamed ground'),
  f('F07', 'phone Walk at the farm', 'tables caption fills half the screen', 'no caption over 25 % of the viewport'),
  f('F08', 'arrive by URL at the farm', 'tile not streamed until Walk', 'stream on arrival'),
  f('F09', 'move 100 m', 'URL unchanged', 'URL carries the current position'),
  f('F10', 'tables 49 and 423 top-down', '0.8 to 1.55 m off the satellite gaps', 'within 1.0 m'),
  f('F11', 'tables module pole claims', '607 of 648 tables with library poles no AC route reaches', 'every table fed by a modelled route or flagged'),
  f('F12', 'walker ground at 4 aisles', 'a constant 1.04 m above queryTerrainElevation', 'one height frame, explained'),
  f('F13', 'engine lock at 1920x1080', 'its caption overlaps the tables caption', 'no overlap'),
  f('F14', 'GPU solids trench width', '125 / 1,475 mm (no side margins)', '325 / 1,675 mm'),
  f('F15', 'CI on main', 'two menu-bar checks and plan-view tolerated', 'all green on a GPU runner'),
];

// ------------------------------------------------------------------------------------------------ how to continue
export const CONTINUE = [
  '1. Read docs/NEXT-WEEKEND-SCOPE.md, then this file, then audit/GEOMETRY-AUDIT.md.',
  '2. Clone the simulator main; run the gates once to get the baseline (GATES).',
  '3. Iteration 1: build envelope.js with the join rule first, prove the 3 check points to 1 mm, then the table kernel.',
  '4. Push to main only when the gates pass; the CD loop ships a dated version; pin a checked version to the homepage at the end of each iteration.',
  '5. After each iteration rerun the GPU audit and update audit/GEOMETRY-AUDIT.md and this spec (FACTS gain values, TO-SOURCE items shrink).',
];

// ------------------------------------------------------------------------------------------------ self-check
if (import.meta.url === `file://${process.argv[1].replace(/\\/g, '/').replace(/^([A-Za-z]):/, '/$1:')}` || process.argv[1]?.endsWith('next-weekend.spec.mjs')) {
  const gaps = []; let n = 0;
  const walk = (o, p) => { if (o && typeof o === 'object' && 'label' in o && 'unit' in o) { n++; for (const k of ['value', 'unit', 'label', 'source']) if (!(k in o)) gaps.push(`${p}.${k}`); if (o.value == null && o.label !== 'TO-SOURCE') gaps.push(`${p}: null value not TO-SOURCE`); return; }
    if (o && typeof o === 'object') for (const [k, v] of Object.entries(o)) walk(v, `${p}.${k}`); };
  walk({ FACTS, AUDIT, KERNEL }, 'spec');
  for (const it of ITERATIONS) for (const x of it.tests) for (const k of ['name', 'cmd', 'threshold']) if (!x[k]) gaps.push(`iteration ${it.id} test ${x.name}: ${k}`);
  const toSource = JSON.stringify({ FACTS, KERNEL }).match(/"TO-SOURCE"/g)?.length || 0;
  console.log(`${n} measurements, ${ITERATIONS.reduce((a, i) => a + i.tests.length, 0)} pass tests, ${FAULTS.length} faults, ${GATES.length} gates, ${toSource} TO-SOURCE items; gaps ${gaps.length}`);
  if (gaps.length) { console.log(gaps.join('\n')); process.exit(1); }
}
