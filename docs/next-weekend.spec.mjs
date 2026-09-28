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
    modulesPerFace: m(5, 'modules in portrait', 'DERIVED', '2 x 5 x 2.384 m x cos 8 deg + 0.5 m ridge gap = 24.3 m, the measured width'),
    postLinesPerFace: m(3, 'post lines across each face (6 per tent frame)', 'ESTIMATED', 'two under-table site photos (private); a 5-in-portrait face needs a triple-post type or more (a fixed-tilt maker range shows single, twin and triple post); range 2 to 3'),
    frameSpacing: m(3.97, 'm (3 module widths)', 'ESTIMATED', 'post rhythm along the row in the site photos; range 2.65 to 5.29 m (2 to 4 modules)'),
    pileType: m('driven galvanised post, the post is the pile', '-', 'ESTIMATED', 'site photos: perforated sections going straight into the ground'),
    postHeightAbove: m([1.3, 2.8], 'm (low edge to ridge side)', 'DERIVED', 'low edge 1.33 m and ridge 3.0 m less the rafter depth'),
    embedment: m([1.5, 2.5], 'm', 'ASSUMED', 'typical driven-post embedment; set by pull-out tests on site'),
    braces: m('diagonals from the post heads outward in the frame plane', '-', 'ESTIMATED', 'site photos'),
    purlinsRafters: m(null, '-', 'TO-SOURCE', 'sections and spacing: from the structure maker drawing'),
    pilesFarm: m({ central: 58626, low: 29556, high: 86760, perMWp: [136, 399], centralPerMWp: 269 }, 'piles', 'ESTIMATED', '639 drawn tables, 37.87 km of table, 9,771 frames at 3.97 m x 6 posts; range from 2 to 4 module spacing and 4 to 6 posts per frame; 218 MWp drawn at a 760 W class module (the tables module does not yet draw every block)'),
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
    'Distances: GridAtlas haversine (sphere, about 0.3 to 0.5 % from WGS84) stays for map-scale questions (substation to site, first-pass route length); construction uses place-frame (WGS84 tangent plane + OSTN15, 62/62 OS test points at 0.0078 m); CI checks kernel corners against an ellipsoid geodesic (Karney, GeographicLib, MIT) to 1 mm, and the geodesic azimuth minus the grid bearing must equal the convergence.',
    'One shared distance/frame function: the sphere constant 6371008.8 is copied into 7 files today; replace them.',
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
  perimeter: {
    members: ['security fence (mesh on posts, about 2 m; deer fence on farmland)', 'gates', 'perimeter track just inside the fence', 'meadow or grazing margin between the track and the table ends'],
    dims: m(null, '-', 'TO-SOURCE', 'fence height and post spacing, track width, margin width from the planning drawings; about 2 m, 3 m and 8 to 12 m read from a close-up photo'),
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
  substation: {
    sample: 'L (an outdoor substation at the edge of a large E-W farm)',
    members: ['grid transformers in bays', 'busbar gantries and outdoor switchgear (AIS)', 'control buildings', 'the security fence', 'an overhead line coming in on lattice towers', 'an internal road'],
    dims: m(null, '-', 'TO-SOURCE', 'bay widths, gantry heights, clearances and transformer sizes from a substation standard layout; the grid-building part of the simulator'),
  },
  station: {
    uses: ['FACTS.station.*'],
    members: ['pad or piles', 'bund with pre-drilled entry holes (7 per side, scenario A)', 'skid', 'transformer', 'RMU', 'LV boards'],
    unloading: ['delivery vehicle', 'lift plan envelope (crane or HIAB radius, outriggers)', 'lay-down area', 'exclusion zone'],
  },
};

// ------------------------------------------------------------------------------------------------ structure types
// The table kernel is parametric over structure TYPE, not one table. Foundations per MWp follow from four numbers:
//   foundations/MWp = postsPerFrame x 1000 / (modulesUpSlope x faces x modulesAlongPerBay x moduleKW)
// Checked on the farm: 6 posts / (5 x 2 x 3 x 0.760 kW) = 263 per MWp against 269 counted table by table.
export const foundationsPerMWp = ({ postsPerFrame, modulesUpSlope, faces = 1, modulesAlongPerBay, moduleKW }) =>
  postsPerFrame * 1000 / (modulesUpSlope * faces * modulesAlongPerBay * moduleKW);
export const STRUCTURES = {
  eastWestTent: {
    sample: 'C (the farm): two under-table site photos',
    orientation: m('E-W tent, two faces back to back, ridge gap 0.5 m', '-', 'MEASURED', 'satellite rows and site photos'),
    modulesUpSlope: m(5, 'in portrait per face', 'DERIVED', 'measured width 24.3 m'),
    postsPerFrame: m(6, 'posts (3 per face)', 'ESTIMATED', 'site photos'),
    modulesAlongPerBay: m(3, 'modules', 'ESTIMATED', 'site photos; range 2 to 4'),
    foundation: m('driven galvanised post (the post is the pile)', '-', 'ESTIMATED', 'site photos'),
    perMWp: m(263, 'foundations per MWp at 760 W', 'DERIVED', 'foundationsPerMWp; 136 to 399 over the ranges'),
  },
  southTwinPostBallast: {
    sample: 'A (a 21 MWp site in a structure maker portfolio photo)',
    orientation: m('south-facing single face', '-', 'ESTIMATED', 'portfolio photo'),
    postsPerFrame: m(2, 'posts (short front, tall rear, one diagonal)', 'ESTIMATED', 'portfolio photo'),
    modulesUpSlope: m(null, '-', 'TO-SOURCE', 'not resolved at the photo size; 2 in portrait or 4 in landscape are the usual reads'),
    foundation: m('concrete ballast or footing blocks at the post feet', '-', 'ESTIMATED', 'dark blocks at the post feet in the photo'),
    roughCount: m({ low: 12963, high: 19444, basis: '4 in landscape, 270 W class modules of that era, a frame every 2 to 3 modules' }, 'foundations for 21 MWp', 'ESTIMATED', 'foundationsPerMWp with ASSUMED module and bay; a rough guide only'),
  },
  southDrivenPosts: {
    sample: 'B (an 18 MWp site in the same portfolio)',
    orientation: m('south-facing single face, wide grassed aisles', '-', 'ESTIMATED', 'portfolio photo'),
    postsPerFrame: m(2, 'posts (tall rear, front, diagonals)', 'ESTIMATED', 'portfolio photo'),
    modulesUpSlope: m(null, '-', 'TO-SOURCE', 'not resolved at the photo size'),
    foundation: m('driven posts into grassland', '-', 'ESTIMATED', 'portfolio photo'),
    roughCount: m({ low: 11111, high: 16667, basis: 'same assumptions as sample A' }, 'piles for 18 MWp', 'ESTIMATED', 'foundationsPerMWp with ASSUMED module and bay; a rough guide only'),
  },
  southSinglePost: {
    sample: 'D (a structure maker render, single post, 2 in portrait)',
    orientation: m('south-facing single face', '-', 'ESTIMATED', 'maker render'),
    modulesUpSlope: m(2, 'in portrait', 'ESTIMATED', 'maker render'),
    postsPerFrame: m(1, 'post', 'ESTIMATED', 'maker render'),
    modulesAlongPerBay: m([3, 4], 'modules between frames', 'ESTIMATED', 'back-view site photo: post rhythm along the row'),
    purlins: m(4, 'purlins along the row (2 per module up-slope)', 'ESTIMATED', 'back-view site photo and maker render agree'),
    strut: m('one diagonal from the post to the rafter', '-', 'ESTIMATED', 'back-view site photo and maker render agree'),
    dcDrops: m('string cables drop from the module junction boxes down the post line to the ground', '-', 'ESTIMATED', 'back-view site photo; the kernel draws the drop at each post and the tie points along a purlin'),
    ground: m('driven posts also work in gravel (brownfield) ground', '-', 'ESTIMATED', 'back-view site photo'),
    perMWp: m([164, 370], 'foundations per MWp (a frame every 3 to 4 modules; 760 W to 450 W modules)', 'DERIVED', 'foundationsPerMWp'),
  },
  singleAxisTracker: {
    sample: 'E (a single-axis tracker photo, modules being mounted)',
    orientation: m('rows north-south, modules turn east to west about a torque tube', '-', 'ESTIMATED', 'photo'),
    modulesUpSlope: m(1, 'in portrait (1P)', 'ESTIMATED', 'photo'),
    postsPerFrame: m(1, 'post per bearing', 'ESTIMATED', 'photo: one post and bearing per bay'),
    modulesAlongPerBay: m(7, 'modules between bearings', 'ESTIMATED', 'photo; range 5 to 8'),
    torqueTubeHeight: m(1.7, 'm', 'ESTIMATED', 'about chest height of the crew in the photo'),
    rotation: m(null, '-', 'TO-SOURCE', 'rotation range, stow angle and drive post spacing from the tracker maker'),
    rotationSeen: m(55, 'deg or more from flat', 'ESTIMATED', 'second tracker photo: modules turned steeply at the row end'),
    torqueTube: m('round tube on bearings at the post heads', '-', 'ESTIMATED', 'tracker photos'),
    moduleClamps: m('one bracket pair per module on the torque tube', '-', 'ESTIMATED', 'aisle-view tracker photo'),
    heroView: m('from the aisle at ground level, looking along two rows at midday (modules near flat, undersides and tubes in view)', '-', 'ESTIMATED', 'aisle-view tracker photo: the tracker reference image the simulator must reproduce, as the under-table photo is for the tent'),
    rowEndInverter: m('a string inverter on its own two-post stand with a small sun canopy at the row end', '-', 'ESTIMATED', 'second tracker photo; the farm puts its inverters under the tables instead, so the kernel supports both sites'),
    cableEntry: m('DC strings down the first tracker post in flexible conduit to the inverter; AC out in conduit straight into the ground, where the LV AC trench starts', '-', 'ESTIMATED', 'second tracker photo; the trench kernel starts its route at the inverter stand'),
    perMWp: m([164, 263], 'foundations per MWp (5 to 8 modules per bay, 760 W)', 'DERIVED', 'foundationsPerMWp with faces 1 and modulesUpSlope 1; 188 at 7 modules'),
    buildStep: m('two people lift each module onto the torque tube and clamp it at chest height; the rows then turn', '-', 'ESTIMATED', 'photo; the simulator animates the mounting and the rotation'),
  },
  southTwinPostBeams: {
    sample: 'F (a maker twin-post system photographed mid-build, bare steel)',
    orientation: m('south-facing single face', '-', 'ESTIMATED', 'mid-build photo'),
    postsPerFrame: m(2, 'posts (tall rear line, short front line)', 'ESTIMATED', 'mid-build photo'),
    topology: m('posts -> a longitudinal beam along each post line at the post heads -> rafters up the slope resting on both beams, overhanging the rear -> modules (purlins not yet fitted in the photo)', '-', 'ESTIMATED', 'mid-build photo; a second topology the kernel must support'),
    rafterSpacing: m('about 2 rafters per post bay (half the post spacing)', '-', 'ESTIMATED', 'second mid-build photo (sample I); the maker drawing gives the exact value'),
    sections: m('slotted C-section beams, lipped C-section rafters', '-', 'ESTIMATED', 'second mid-build photo'),
    postFeet: m('a ring of crushed stone around each post foot (a pre-drilled hole backfilled, or a gravel collar)', '-', 'ESTIMATED', 'second mid-build photo; to confirm on site'),
    siteTrack: m('an unpaved construction track with tyre ruts along the array edge', '-', 'ESTIMATED', 'second mid-build photo; the temporary access the road kernel compares with a built road or mats'),
    buildStageSeen: m('after rafters, before purlins and modules', '-', 'MEASURED', 'what the photo shows'),
  },
  eastWestTentLandscape: {
    sample: 'L (a large E-W farm abroad, drone view; a smaller version of the REPD 6502 tent)',
    orientation: m('E-W tent, two faces back to back, low tilt', '-', 'ESTIMATED', 'drone photo'),
    moduleOrientation: m('landscape (long side along the row)', '-', 'ESTIMATED', 'drone photo; REPD 6502 uses 5 in portrait per face'),
    modulesUpSlope: m(5, 'landscape modules per face', 'ESTIMATED', 'drone photo with a car for scale (sample L3); about 4 to 6 in the first drone photo'),
    vehicleCorridor: m(5, 'm between table blocks, sand, used by site cars and vans', 'ESTIMATED', 'drone photo: a car about 1.85 m wide drives through with room each side'),
    constructionFront: m('fence posts set before the mesh; a new block with only piles driven in rows before its frames', '-', 'MEASURED', 'what the drone photo shows: the build sequence visible across one site'),
    faceWidth: m('modulesUpSlope x module short side (1.13 to 1.30 m) x cos(tilt)', '-', 'DERIVED', 'the same kernel as the portrait tent with the module turned; about half the REPD 6502 width'),
    stationsBetweenTables: m('small kiosks set in gaps between the tables', '-', 'ESTIMATED', 'drone photo'),
    tentFrame: m('an A-frame: two rafters meeting at the ridge, a horizontal tie low across the A, posts under each face, C-section purlins along the row', '-', 'ESTIMATED', 'close-up of the table ends; the tent topology for the kernel'),
    height: m('low and compact: posts about 1 m above ground, the ridge well under the REPD 6502 3.0 m', '-', 'ESTIMATED', 'close-up; to measure'),
    perimeter: m('a mesh security fence, a gravel track just inside it, and a wide meadow margin between the track and the table ends', '-', 'ESTIMATED', 'close-up; the fence-the-envelope phase builds these'),
  },
  terrainFollowing: {
    sample: 'J (a hillside site mid-build, bare beam-system frames)',
    rule: m('each frame sits on the ground at its own pile line, so a table curves along the row with the terrain', '-', 'ESTIMATED', 'hillside photo; the same rule as the site-world block-build (frame follows the ground per pile line)'),
    kernelTest: m('every frame foot within 0.05 m of the DTM, and the change of slope between neighbouring frames within the structure limit', '-', 'DERIVED', 'from the rule'),
    slopeLimit: m(null, '-', 'TO-SOURCE', 'the maximum slope along the row and the maximum change between frames, from the structure maker'),
    accessTrack: m('an access track up the middle between two arrays, with a cable or hose laid along it', '-', 'ESTIMATED', 'hillside photo'),
  },
  // THE BUILD SEQUENCE the construction game animates, from the site photos (each step a typed command and a state):
  buildSequence: ['set out the rows (survey)', 'drive posts (or place ballast blocks, or screw in ground screws)', 'fix longitudinal beams (beam systems) or rafters on the post heads', 'fix rafters on the beams (beam systems)', 'fix purlins along the row', 'clamp modules (a two-person lift, as in the tracker photo)', 'tie string cables along a purlin and drop them at the posts', 'set the inverter (under the table, or on its own stand at the row end)', 'dig the LV AC trench from the inverter and lay ducts and cables'],
  southTwinPostRafters: {
    sample: 'G (a maker render of a twin-post 2P section, half fitted with modules)',
    orientation: m('south-facing single face', '-', 'ESTIMATED', 'maker render'),
    modulesUpSlope: m(2, 'in portrait', 'ESTIMATED', 'maker render'),
    postsPerFrame: m(2, 'posts (short front, tall rear) and one diagonal from the rear post to the rafter', 'ESTIMATED', 'maker render'),
    modulesAlongPerBay: m([2, 3], 'modules between frames', 'ESTIMATED', 'maker render: 3 frames over about 6 module widths'),
    purlins: m(4, 'purlins along the row with module clamps', 'ESTIMATED', 'maker render'),
    postJoint: m('two-part post: a pile in the ground with the post spliced on above it', '-', 'ESTIMATED', 'maker render; changes the build (pile first, post after, levelled at the splice)'),
    perMWp: m([439, 1111], 'foundations per MWp (3 to 2 modules per bay; 760 W to 450 W)', 'DERIVED', 'foundationsPerMWp with 2 posts, 2 up-slope'),
    stateSeen: m('half built: frames complete, half the modules clamped', '-', 'MEASURED', 'what the render shows; the being-built state the game draws'),
  },
  southSinglePostConcrete: {
    sample: 'H (a single-post bifacial table from behind, dry stony ground)',
    orientation: m('south-facing single face', '-', 'ESTIMATED', 'site photo'),
    modulesUpSlope: m(2, 'in portrait, bifacial', 'ESTIMATED', 'site photo'),
    postsPerFrame: m(1, 'tall rear post with a diagonal from its foot up to the rafter', 'ESTIMATED', 'site photo'),
    modulesAlongPerBay: m(3, 'modules between frames', 'ESTIMATED', 'site photo'),
    foundation: m('post set in a small cast concrete footing', '-', 'ESTIMATED', 'site photo: the fourth foundation type, where rock or stones stop a driven post'),
    setOut: m('string lines on the ground mark the post lines before driving or casting', '-', 'ESTIMATED', 'site photo; the survey step of the build sequence draws them'),
    perMWp: m([219, 370], 'foundations per MWp (3 modules per bay; 760 W to 450 W)', 'DERIVED', 'foundationsPerMWp with 1 post, 2 up-slope'),
  },
  // The member topology every type shares, read most clearly from sample D and confirmed under the farm's tables:
  // post (driven) -> rafter (inclined, one per frame per face) -> purlins (along the row, 2 per module in portrait,
  // at the clamp zones) -> modules clamped to the purlins; a strut from the post foot to the rafter end; E-W tents
  // add a second face and a ridge gap. Member sections and exact spacings stay TO-SOURCE (the maker drawing).
  memberTopologyBeamVariant: ['post', 'longitudinal beam per post line', 'rafters up the slope on the beams', 'purlins (if used)', 'modules'],
  memberTopology: ['post', 'rafter per frame per face', 'strut post-foot to rafter end', 'purlins along the row, 2 per module up-slope', 'modules clamped to purlins', 'ridge gap (tent only)'],
  purlinsPerFace: m({ farm: 10, sampleD: 4 }, 'purlins (2 per module up-slope)', 'ESTIMATED', 'maker render and site photos'),
  kernelParameters: ['orientation (E-W tent | south single face | single-axis tracker)', 'modulesUpSlope and portrait/landscape', 'postsPerFrame (1 | 2 | 3 per face)', 'modulesAlongPerBay', 'foundation (driven post | ground screw | concrete ballast | cast concrete footing)', 'embedment or ballast mass', 'tilt, low edge, ridge'],
  whyItMatters: 'the foundation type changes the build: a pile rig and pull-out tests for driven posts or screws; lorry loads of concrete blocks, a crane or telehandler and no ground penetration for ballast (archaeology, landfill, cable easements)',
};

// ------------------------------------------------------------------------------------------------ the table as code
// "We are just changing the orientation, landscape or portrait, and how many per row; basic shapes around modules,
// impact piles or screw piles, and their height adjustable from the LiDAR." Yes: every structure sample above is this
// one function with different numbers. groundAt(x, y) is the EA DTM in the table frame (x across, y along the row).
const D2R = Math.PI / 180;
export function tableAssembly(p, groundAt = () => 0) {
  const { module: [mLong, mShort], orientation, upSlope, along, faces, tilt, lowEdge, bayModules, postLinesPerFace,
    foundation, ridgeGap = 0.5, gap = 0.02, follow = 'straight', reveal = [0.6, 3.5] } = p;
  const up = orientation === 'portrait' ? mLong : mShort, alongW = orientation === 'portrait' ? mShort : mLong;
  const faceRun = upSlope * (up + gap) - gap, faceW = faceRun * Math.cos(tilt * D2R), rise = faceRun * Math.sin(tilt * D2R);
  const length = along * (alongW + gap) - gap, width = faces === 2 ? 2 * faceW + ridgeGap : faceW;
  const bay = bayModules * (alongW + gap), nFrames = Math.floor(length / bay + 1e-9) + 1;
  const lines = [];                                      // post lines across the table: 10 % to 90 % of each face
  for (let f = 0; f < faces; f++) for (let k = 0; k < postLinesPerFace; k++) {
    const t = postLinesPerFace === 1 ? 0.5 : 0.1 + 0.8 * k / (postLinesPerFace - 1), xf = t * faceW;
    lines.push({ x: faces === 2 ? (f ? width / 2 - xf : -width / 2 + xf) : -faceW / 2 + xf, h: lowEdge + t * rise });
  }
  const ys = Array.from({ length: nFrames }, (_, i) => Math.min(i * bay, length));
  // the table's design line along the row: STRAIGHT = least-squares line through the ground under the frames, lifted
  // so every post keeps at least its design height; FOLLOW = each frame sits on its own ground (terrain following)
  const gMean = ys.map(y => lines.reduce((a, L) => a + groundAt(L.x, y), 0) / lines.length);
  let line;
  if (follow === 'straight') {
    const n = ys.length, my = ys.reduce((a, b) => a + b, 0) / n, mg = gMean.reduce((a, b) => a + b, 0) / n;
    const k = ys.reduce((a, y, i) => a + (y - my) * (gMean[i] - mg), 0) / (ys.reduce((a, y) => a + (y - my) ** 2, 0) || 1);
    const base = y => mg + k * (y - my);
    const lift = Math.max(0, ...ys.flatMap(y => lines.map(L => groundAt(L.x, y) - base(y))));
    line = y => base(y) + lift;
  } else line = y => gMean[ys.indexOf(y)];
  const piles = [];
  for (const y of ys) for (const L of lines) {
    const g = groundAt(L.x, y), top = line(y) + L.h;
    piles.push({ x: +L.x.toFixed(3), y: +y.toFixed(3), ground: +g.toFixed(3), reveal: +(top - g).toFixed(3) });
  }
  const rv = piles.map(q => q.reveal), out = piles.filter(q => q.reveal < reveal[0] || q.reveal > reveal[1]).length;
  return { dims: { width: +width.toFixed(3), length: +length.toFixed(3), faceWidth: +faceW.toFixed(3), lowEdge, highEdge: +(lowEdge + rise).toFixed(3) },
    counts: { modules: upSlope * faces * along, frames: nFrames, piles: piles.length }, foundation,
    reveal: { min: Math.min(...rv), max: Math.max(...rv), outOfRange: out }, piles };
}
export const TABLE_EXAMPLES = {
  farmTent5P: { module: [2.384, 1.303], orientation: 'portrait', upSlope: 5, along: 90, faces: 2, tilt: 8, lowEdge: 1.33, bayModules: 3, postLinesPerFace: 3, foundation: 'impact-driven post' },
  landscapeTent5L: { module: [2.384, 1.303], orientation: 'landscape', upSlope: 5, along: 40, faces: 2, tilt: 10, lowEdge: 0.9, bayModules: 2, postLinesPerFace: 2, foundation: 'impact-driven post' },
  southSinglePost2P: { module: [2.384, 1.303], orientation: 'portrait', upSlope: 2, along: 30, faces: 1, tilt: 20, lowEdge: 0.8, bayModules: 3, postLinesPerFace: 1, foundation: 'screw pile', reveal: [0.8, 2.5] },
  farmTent5PFollow: { module: [2.384, 1.303], orientation: 'portrait', upSlope: 5, along: 90, faces: 2, tilt: 8, lowEdge: 1.33, bayModules: 3, postLinesPerFace: 3, foundation: 'impact-driven post', follow: 'follow' },
};

// ------------------------------------------------------------------------------------------------ machines and crews
// The actors of the construction game, from the site photos. Each carries its footprint and its constraints so the
// simulator can check that the work physically fits (aisles, ground, reach) before it animates it.
export const PLANT = {
  postDriver: {
    sample: 'K (a UK grass site, drone view)',
    machine: m('compact tracked excavator with a post-driving (rammer) attachment on the arm', '-', 'ESTIMATED', 'photo'),
    workingPosition: m('sits in the aisle beside the row and drives each post in reach, then tracks along the aisle', '-', 'ESTIMATED', 'photo: track marks along the grass aisles'),
    crew: m(['operator', 'one steadies and aligns the post', 'one checks line and level'], 'people', 'ESTIMATED', 'photo: three on foot plus the operator'),
    trackWidth: m(null, '-', 'TO-SOURCE', 'track gauge and overall width, mass, reach and ground pressure from the machine maker'),
    rate: m(null, '-', 'TO-SOURCE', 'posts per day per rig, from a contractor or a trade source'),
    constraints: ['the aisle clear width fits the tracks plus a working clearance', 'the arm reaches the post line from the aisle', 'ground pressure within what the grass or soil carries (no road needed for tracked plant)'],
  },
  deliveries: m('wheeled lorries (modules, steel, transformers) need a road or mats; tracked plant can work on grass', '-', 'ESTIMATED', 'photos K and I; this is why the road kernel sizes roads for wheeled design vehicles'),
  moduleCrew: m('two people lift and clamp each module', 'people', 'ESTIMATED', 'tracker photo (sample E)'),
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
// MERGED from three independent reviews (the lead, reviewer 1 geometry, reviewer 2 engineering), each through the GPU
// three times. All three agree: precision is sound (0.003 to 0.0076 px at z22-24); what breaks is the GROUND (one
// height per block anchor: 2.7 m p50, 8.6 m p95 on the farm DTM; two terrain sources), the CAMERA (pitch cap 85),
// the MEMBERS (hairlines), the TRENCH (sharp corners) and SPRAWL (three table libraries). The order is binding.
const t = (name, cmd, threshold) => ({ name, cmd, threshold });
export const ITERATIONS = [
  {
    id: 1, goal: 'ONE ground and ONE hero table: from the satellite to under the table without breaking',
    build: [
      'EA 1 m DTM served as terrarium tiles (furnace service route /terrarium/{z}/{x}/{y}.png; 0xFFFF no data) and used as the map terrain, so satellite drape and wire share one ground',
      'overlay.html loader: t.async = false (module order by design, not luck)',
      'base wire grounded per vertex, not per block anchor',
      'tables.js HERO tier: the nearest table gets solid members (12-edge prisms), module frames, rails, ridge light slot; its own anchor at the table centre',
      'walk-fps.js: tables are solid for collision; a kneel key (eye 1.0 m)',
    ],
    files: ['prototype/overlay.html', 'prototype/mod/tables.js', 'prototype/mod/walk-fps.js', 'furnace service (terrarium route)', 'tests/hero-table.cjs'],
    tests: [
      t('terrarium decode', 'decode 1,000 random nodes vs the u16 DTM tile', '<= 0.03 m'),
      t('one ground', 'wire ground vs map.queryTerrainElevation at 1,000 points', '<= 0.05 m (today p95 1 to 8 m)'),
      t('zoom sweep', 'z15 to z22.75 in 0.25 steps, screenshot each; 4 table corners vs CPU projection', '<= 0.5 px'),
      t('feet on ground', 'hero table feet vs EA DTM', '<= 0.05 m, 0 floating'),
      t('dimensions', 'node tests/hero-table.cjs', 'width 24.27 +/- 0.01, ridge 3.00, low edge 1.33 m'),
      t('frame rate', 'fps4k.cjs with hero + 80 detail tables', '>= 90 fps at 4K'),
      t('baseline', 'overlay-smoke + privacy scan', '14/14, 0 hits'),
    ],
    sees: 'The farm photo, one table on its row; zooming in it becomes a real frame you walk under, on the ground the photo sits on.',
    agentHours: m([10, 14], 'h', 'ESTIMATED', 'reviewers 1 and 2'),
    cutIfShort: 'kneel key and rails; NEVER the one-ground, zoom-sweep or feet tests',
  },
  {
    id: 2, goal: 'Look up, and ONE trench dug on real ground',
    build: [
      'MapLibre 5 (pitch beyond 90 in Walk; transform.elevation replaced by the 5.x API)',
      'one-close-up LOD by pixels: hero when a post exceeds 1 px, detail when a table exceeds 65 px, outlines beyond',
      'perf.js folded into ONE wire render (one program, one block draw site)',
      'one trench chain with filleted bends (R >= governing duct radius where it fits; bends that cannot fit listed and drawn red), floor at DTM - 1.202 m, the section at the walker with the real duct count',
    ],
    files: ['package.json', 'prototype/overlay.html', 'prototype/mod/walk-fps.js', 'prototype/mod/perf.js (folded)', 'prototype/mod/tables.js', 'prototype/mod/ac-trenches.js', 'prototype/mod/trench-measure.js', 'tests/trench-geometry.cjs'],
    tests: [
      t('look up', 'under the table, view axis coverage of hero members within 15 m', '>= 90 % (today 15 %)'),
      t('no regressions', 'every browser test on 5.x on a real GPU', 'all pass'),
      t('one render', 'grep wire programs and block draw sites', '1 and 1'),
      t('invisible LOD', 'consecutive screenshots across a LOD swap', '< 0.5 % pixels changed'),
      t('trench floor', 'floor vs DTM - 1.202 m along the chain', '<= 0.01 m'),
      t('trench volume', 'swept volume vs GPU raster volume', 'within 1 %'),
      t('clear of tables', 'chains vs table footprints', '0 crossings'),
    ],
    sees: 'Under the table you tilt up to the purlins, module undersides and the light slot; then walk one AC trench from a table to its station, dug into the real ground.',
    agentHours: m([12, 16], 'h', 'ESTIMATED', 'reviewers 1 and 2'),
    cutIfShort: 'row-detector deletions and the X-ray view; NEVER the upgrade or the fillets. Fallback: if MapLibre 5 cannot walk at 90 fps, build the separate envelope scene (ARCH.views.envelope) against the same tests',
  },
  {
    id: 3, goal: 'The construction envelope, the procedural site from the hero template, roads, and CI on the GPU',
    build: [
      'site-box.js: fence-line envelope in one ENU frame, re-anchored every 250 m, the RULES.join rule',
      'every measured row instanced from the hero template, placed per pile on the DTM by the site-world block-build rule (frame follows the ground per pile line)',
      'ONE table library pinned by URL; delete the mod/engine/ copy and the toy block()',
      'road kernel for the design vehicles (build-up, quantities, swept path) and the temporary mat option',
      'the GPU audit plus the reviewers\' checks in CI on a self-hosted GPU runner (matrix <= 12), 0 tolerated tests',
      'furnace guards (earthworks outside the site answers "not covered"; every job answered or refused)',
      'a checked version pinned on the homepage with the audit JSON sha',
    ],
    files: ['prototype/mod/site-box.js', 'prototype/mod/tables.js', 'prototype/mod/engine-lock.js', 'prototype/mod/kernel/road.mjs', 'prototype/mod/kernel/mats.mjs', '.github/workflows/overlay.yml', 'tests/geometry-ci.py', 'tests/instances.cjs'],
    tests: [
      t('join', 'site-box check points at 250 m', '< 15 mm'),
      t('pile feet', '10,000 feet vs DTM', '<= 0.05 m'),
      t('fit to the photo', 'top-down render vs satellite', 'IoU >= baseline + 0.10; edge residual p50 < 1.0 m'),
      t('solid tables', 'GPU audit', 'overlaps 0 m2 (today 913); aisles under 1 m 0 (today 27)'),
      t('one engine', 'grep engine import URLs', 'exactly 1'),
      t('GPU CI', 'self-hosted runner workflow', 'green in < 15 min, 0 tolerated'),
      t('scale', '639 instances at 4K', '>= 90 fps, one draw call per LOD tier'),
    ],
    sees: 'A fenced construction site cut into the satellite; every table the one approved, on measured ground; roads with layers and quantities; a CI page with the numbers.',
    agentHours: m([10, 18], 'h', 'ESTIMATED', 'reviewers 1 and 2'),
    cutIfShort: 'in order: the DSM-hillshade lock test, the mat animation, the fence animation. Transformer unloading moves to the weekend after unless this finishes early',
  },
];

export const REVIEWS = {
  lead: { verdict: m([35, 40], '%', 'ESTIMATED', 'play test pillars, 12 scores'), where: 'docs/NEXT-WEEKEND-SCOPE.md sections 1-11' },
  reviewer1: { lens: 'geometry and rendering', verdict: m(35, '%', 'ESTIMATED', 'three furnace iterations'), key: m(0.0076, 'px', 'MEASURED', 'worst anchor-relative error at 4K, z24') },
  reviewer2: { lens: 'engineering truth and process', verdict: m([25, 30], '%', 'ESTIMATED', 'three furnace iterations'), key: m({ p50: 2.73, p95: 8.55, max: 10.87 }, 'm', 'MEASURED', 'one terrain height per 200 x 120 m block vs the farm DTM') },
  openRisk: m(null, '-', 'TO-SOURCE', 'the mounting structure GA drawing (or maker and model): no satellite or LiDAR sees posts, braces, purlins or rails'),
};

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
  f('F16', 'any block on sloping ground', 'one terrain height per block anchor: 2.73 m p50, 8.55 m p95 off the DTM', 'ground per vertex'),
  f('F17', 'compare the satellite drape with the wire ground', 'AWS 4.8 m DEM vs EA 1 m DTM: two grounds', 'one ground (EA DTM as the map terrain)'),
  f('F18', 'overlay.html module loader', 'dynamic scripts async, order by luck', 't.async = false'),
  f('F19', 'walk into a table', 'tables.js and engine-lock blocks are not solid', 'collision with every table'),
  f('F20', 'grep table libraries', 'mod/engine/ v12 copy, releases 0524 and 1853, toy block()', 'one library by URL'),
  f('F21', 'tests asserting source text', '11 checks regex the module source', 'geometry assertions'),
  f('F22', 'CI overlay.yml', 'SwiftShader; 4 of 14 test files tolerated', 'GPU runner, 0 tolerated'),
  f('F23', 'tables.js FARM pitch', '26.77 m (24.27 + 2.5)', 'fitted 26.5 to 26.6 m (row gap about 2.3 m)'),
  f('F24', 'furnace earthworks outside the site', 'crash: Index 0 is out of bounds', 'answer "not covered"'),
  f('F25', 'furnace layout job', 'consumed, never answered in 8 minutes', 'answered or refused'),
  f('F26', 'scanner-rows.js local()', 'comment claims < 0.1 %; measured 0.35 % per km east', 'one frame (place-frame) everywhere'),
];

// ------------------------------------------------------------------------------------------------ how to continue
export const CONTINUE = [
  '1. Read docs/NEXT-WEEKEND-SCOPE.md, then this file, then audit/GEOMETRY-AUDIT.md.',
  '2. Clone the simulator main; run the gates once to get the baseline (GATES).',
  '3. Iteration 1 (merged plan): one ground first (EA DTM as the map terrain, wire grounded per vertex, t.async = false), prove the one-ground and zoom-sweep tests, then the hero table tier.',
  '4. Push to main only when the gates pass; the CD loop ships a dated version; pin a checked version to the homepage at the end of each iteration.',
  '5. After each iteration rerun the GPU audit and update audit/GEOMETRY-AUDIT.md and this spec (FACTS gain values, TO-SOURCE items shrink).',
];

// ------------------------------------------------------------------------------------------------ self-check
if (import.meta.url === `file://${process.argv[1].replace(/\\/g, '/').replace(/^([A-Za-z]):/, '/$1:')}` || process.argv[1]?.endsWith('next-weekend.spec.mjs')) {
  const gaps = []; let n = 0;
  const walk = (o, p) => { if (o && typeof o === 'object' && 'label' in o && 'unit' in o) { n++; for (const k of ['value', 'unit', 'label', 'source']) if (!(k in o)) gaps.push(`${p}.${k}`); if (o.value == null && o.label !== 'TO-SOURCE') gaps.push(`${p}: null value not TO-SOURCE`); return; }
    if (o && typeof o === 'object') for (const [k, v] of Object.entries(o)) walk(v, `${p}.${k}`); };
  walk({ FACTS, AUDIT, KERNEL, REVIEWS, STRUCTURES, PLANT, IT: ITERATIONS.map(i => i.agentHours) }, 'spec');
  for (const it of ITERATIONS) for (const x of it.tests) for (const k of ['name', 'cmd', 'threshold']) if (!x[k]) gaps.push(`iteration ${it.id} test ${x.name}: ${k}`);
  const toSource = JSON.stringify({ FACTS, KERNEL, REVIEWS, STRUCTURES, PLANT }).match(/"TO-SOURCE"/g)?.length || 0;
  console.log(`${n} measurements, ${ITERATIONS.reduce((a, i) => a + i.tests.length, 0)} pass tests, ${FAULTS.length} faults, ${GATES.length} gates, ${toSource} TO-SOURCE items; gaps ${gaps.length}`);
  const slope = (x, y) => 0.03 * y + 0.4 * Math.sin(y / 15) + 0.01 * x;      // 3 % along the row, a 0.4 m swell, 1 % across
  for (const [k, pr] of Object.entries(TABLE_EXAMPLES)) for (const [gn, g] of [['flat', () => 0], ['sloping', slope]]) {
    const r = tableAssembly(pr, g); console.log(`${k} on ${gn} ground: ${r.dims.width} x ${r.dims.length} m, ${r.counts.modules} modules, ${r.counts.frames} frames, ${r.counts.piles} ${r.foundation}s, reveal ${r.reveal.min} to ${r.reveal.max} m (${r.reveal.outOfRange} out of range)`);
    if (!(r.counts.piles > 0) || (k.startsWith('farmTent5P') && Math.abs(r.dims.width - 24.27) > 0.05)) gaps.push(`table example ${k} ${gn}`);
  }
  if (gaps.length) { console.log(gaps.join('\n')); process.exit(1); }
}
