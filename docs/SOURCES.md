# Open UK data sources for the scanner

Status legend (all read 2026-09-27):
- **CONFIRMED (search)**: seen in a web-search result for the cited URL this session.
  Direct page fetches of `data.gov.uk` and `environment.data.gov.uk` were **blocked by the
  network egress proxy** this session, so these were not read in full; re-verify before relying on them.
- **UNCONFIRMED (from prior knowledge)**: not confirmed this session; do not treat as fact.

## 1. Environment Agency (England) LiDAR

| # | Claim | Status | Source |
|---|-------|--------|--------|
| E1 | National LIDAR Programme gives 1m elevation data for all of England; 302 survey blocks flown in winter, Jan 2017 to Feb 2023 | CONFIRMED (search), read 2026-09-27 | https://environment.data.gov.uk/dataset/2e8d0733-4f43-48b4-9e51-631c25d1b0a9 |
| E2 | Products include classified point cloud (LAZ: ground, low/medium/high vegetation, structure), DTM and DSM | CONFIRMED (search), read 2026-09-27 | https://environment.data.gov.uk/dataset/2e8d0733-4f43-48b4-9e51-631c25d1b0a9 |
| E3 | Released under Open Government Licence v3.0 | CONFIRMED (search), read 2026-09-27 | https://cloud.csiss.gmu.edu/uddi/dataset/national-lidar-programme |
| E4 | Rasters delivered as GeoTIFF in 5km tiles aligned to the OS National Grid | CONFIRMED (search), read 2026-09-27 | https://cloud.csiss.gmu.edu/uddi/dataset/national-lidar-programme |
| E5 | Composite DTM/DSM: 1m raster covering ~99% of England, vertical accuracy +/-15cm RMSE | CONFIRMED (search), read 2026-09-27 | https://developers.google.com/earth-engine/datasets/catalog/UK_EA_ENGLAND_1M_TERRAIN_2022 |
| E6 | Composite DTM also published at 2m and 10m | CONFIRMED (search, dataset titles only), read 2026-09-27 | https://environment.data.gov.uk/dataset/09ea3b37-df3a-4e8b-ac69-fb0842227b04 ; https://environment.data.gov.uk/dataset/ce8fe7e7-bed0-4889-8825-19b042e128d2 |
| E7 | Composite merges the Time Stamped archive and NLP surveys; the 2022 composite spans surveys 6 Jun 2000 to 2 Apr 2022 | CONFIRMED (search), read 2026-09-27 | https://environment.data.gov.uk/dataset/13787b9a-26a4-4775-8523-806d13af58fc |
| E8 | Metadata index catalogues show, per location, which survey fed the composite | CONFIRMED (search), read 2026-09-27 | https://environment.data.gov.uk/dataset/13787b9a-26a4-4775-8523-806d13af58fc |
| E9 | DTM Time Stamped Tiles: archive of site surveys since 1998; its index gives survey dates, resolution, transformation and geoid model; organised by year then resolution | CONFIRMED (search), read 2026-09-27 | https://environment.data.gov.uk/dataset/dbadf364-0192-4bcf-a223-f3d403f08682 |
| E10 | NLP point density is about 16 points per m2 | UNCONFIRMED (from prior knowledge) | none this session |
| E11 | A separate "First Return" DSM product and older 25cm/50cm/2m composites exist | UNCONFIRMED (from prior knowledge) | none this session |

Scanner note: record the survey date per tile from the index (E8/E9). A composite pixel is not one date.

## 2. Environment Agency Vertical Aerial Photography

| # | Claim | Status | Source |
|---|-------|--------|--------|
| V1 | Captured project by project since 2006, 10cm to 50cm resolution, RGB (some with near infra-red), orthorectified using LiDAR and GPS | CONFIRMED (search), read 2026-09-27 | https://www.data.gov.uk/dataset/4921f8a1-d47e-458b-873b-2a489b1c8165/vertical-aerial-photography |
| V2 | Supplied as 5km zips per survey year containing ECW files on the OS grid | CONFIRMED (search), read 2026-09-27 | https://environment.data.gov.uk/dataset/dae203a8-ba24-4c54-bab0-866b9faadb58 |
| V3 | Licence is OGL v3.0, with no public access constraints | CONFIRMED (search; licence line may be the portal footer, not dataset metadata), read 2026-09-27 | https://www.data.gov.uk/dataset/4921f8a1-d47e-458b-873b-2a489b1c8165/vertical-aerial-photography |
| V4 | Coverage is partial (project areas), not national | CONFIRMED (search), read 2026-09-27 | https://www.data.gov.uk/dataset/4921f8a1-d47e-458b-873b-2a489b1c8165/vertical-aerial-photography |

## 3. Scotland: Scottish Remote Sensing Portal

| # | Claim | Status | Source |
|---|-------|--------|--------|
| S1 | Primary public-sector LiDAR was captured in 6 phases, 2011 to 2022 | CONFIRMED (search), read 2026-09-27 | https://registry.opendata.aws/scottish-lidar/ |
| S2 | Point clouds (LAS/LAZ) plus DTM and DSM as COG or GeoTIFF | CONFIRMED (search), read 2026-09-27 | https://registry.opendata.aws/scottish-lidar/ |
| S3 | OGL v3 unless stated otherwise; **Phase 2 LAZ is under a non-commercial government licence** | CONFIRMED (search), read 2026-09-27 | https://remotesensingdata.gov.scot/about |
| S4 | New Scottish Land LiDAR Programme runs May 2025 to July 2027, with a first release announced Jan 2026 | CONFIRMED (search), read 2026-09-27 | https://blogs.gov.scot/digital/2026/01/29/scotlands-lidar-revolution-first-data-release-to-reveal-scotlands-landscape-in-unprecedented-detail/ |
| S5 | Resolutions per phase (for example, 50cm DTM for some phases, 25cm or 1m for others) | UNCONFIRMED (from prior knowledge) | https://remotesensingdata.gov.scot/data (not read) |

## 4. Wales: DataMapWales

| # | Claim | Status | Source |
|---|-------|--------|--------|
| W1 | Tile catalogue of Welsh Government LiDAR DTMs and DSMs (2020 to 2023), plus an NRW historic archive | CONFIRMED (search), read 2026-09-27 | https://datamap.gov.wales/layers/geonode:welsh_government_lidar_tile_catalogue_2020_2023 ; https://datamap.gov.wales/layers/geonode:nrw_lidar_tile_catalogue_archive |
| W2 | 1m resolution; 32-bit, 16-bit and hillshade COGs | CONFIRMED (search), read 2026-09-27 | https://datamap.gov.wales/layers/geonode:LiDAR_1m_2020_22_DSM_16bit_COG |
| W3 | OGL, commercial and non-commercial use allowed; attribution "Contains Welsh Government LiDAR data" | CONFIRMED (search), read 2026-09-27 | https://datamap.gov.wales/maps/lidar-data-download/ |
| W4 | Welsh point clouds (LAZ) are downloadable from the same portal | UNCONFIRMED (from prior knowledge) | none this session |

## 5. Ordnance Survey: open vs licensed

| # | Claim | Status | Source |
|---|-------|--------|--------|
| O1 | OS OpenData is under OGL v3 (it replaced the OS OpenData Licence in Feb 2015) and may be used for any purpose | CONFIRMED (search), read 2026-09-27 | https://wiki.openstreetmap.org/wiki/Ordnance_Survey_OpenData ; https://www.ordnancesurvey.co.uk/products/open-data |
| O2 | OS Terrain 50: open contours, spot heights and breaklines for GB | CONFIRMED (search), read 2026-09-27 | https://osdatahub.os.uk/downloads/open/Terrain50 |
| O3 | OS Open Roads (high-level road network), OS OpenMap Local (building outlines, roads, greenspace) and OS Open Zoomstack (vector basemap) are open | CONFIRMED (search), read 2026-09-27 | https://www.ordnancesurvey.co.uk/products/open-data ; https://docs.os.uk/os-downloads/products/maps-and-imagery-portfolio/os-openmap-local |
| O4 | OS Terrain 50 grid is a 50m DTM | UNCONFIRMED (from prior knowledge) | none this session |
| O5 | OS MasterMap (Topography and similar) and OS Terrain 5 are **licensed/premium**, not open. Private users need a commercial licence; the public sector gets them under PSGA | UNCONFIRMED (from prior knowledge) | none this session |

## 6. Not usable (for non-eligible users or without a licence)

| # | Claim | Status | Source |
|---|-------|--------|--------|
| X1 | APGB supplies 12.5cm/25cm aerial imagery, CIR and DTM/DSM/contours free at the point of use to the **public sector**; it sits alongside PSGA | CONFIRMED (search), read 2026-09-27 | https://www.europa.uk.com/map-data/uk/apgb-services/ ; https://www.ukauthority.com/articles/public-authorities-to-get-free-aerial-imagery-data/ |
| X2 | Non-eligible (private) users may not use APGB or PSGA data obtained through public-sector access | UNCONFIRMED (inferred from X1; licence text not read) | none this session |
| X3 | Google Maps Platform terms 3.2.3(a) "No Scraping" bars exporting or extracting content (including tiles and elevation); 3.2.3(b) bars caching | CONFIRMED (search), read 2026-09-27 | https://cloud.google.com/maps-platform/terms |
| X4 | Commercial satellite imagery (for example Maxar or Airbus) needs a purchased licence. Do not ingest it without one | UNCONFIRMED (from prior knowledge) | none this session |

## 7. Rate-limit etiquette (project policy, not a claim about any provider)

- No more than 1 request per second per host. Back off exponentially on HTTP 429 or 5xx, and obey `Retry-After`.
- Prefer bulk tile downloads, COGs with HTTP range reads, or the AWS Open Data mirror (S2) over repeated API calls.
- Cache downloads locally with the source URL, licence, retrieval date and survey date, and never re-download unchanged tiles.
- Send an identifying User-Agent. Do not run parallel crawlers against government portals.
- Provider-specific published rate limits: UNCONFIRMED. None were read this session.

## Attribution strings (to carry into outputs)

- OGL v3 sources: "Contains public sector information licensed under the Open Government Licence v3.0." (UNCONFIRMED wording, from prior knowledge)
- OS OpenData: "Contains OS data © Crown copyright and database right [year]" (UNCONFIRMED wording, from prior knowledge)
- Wales: "Contains Welsh Government LiDAR data" (W3, CONFIRMED)
