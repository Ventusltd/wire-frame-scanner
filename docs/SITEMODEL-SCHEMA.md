# Site model schema (design proposals and scanned sites)

A site model is a plain JSON-compatible dict. Every numeric value is a **tagged value**:

```json
{"value": 6.0, "unit": "m", "provenance": "assumed (design proposal)"}
```

- `value`: a number (int or float). No bare numbers appear anywhere else in a model.
- `unit`: one of `m`, `m2`, `m3`, `deg`, `MW`, `Wp`, `count`, `index`.
- `provenance`: one of the four tags in docs-SCANNER.md: `measured`, `derived`, `estimated`, `assumed`. A qualifier in brackets states the source. `scanner/fictional.py` always writes `assumed (design proposal)`. A scanner result would write, for example, `estimated from imagery, not measured`.

## Frame and conventions
- Local metres: x east, y north, z up, with the local ground at z = 0. Negative z is below ground (trenches).
- Bearings and azimuths are compass degrees: 0 = north, 90 = east.
- Points are lists of tagged values: `[x, y]` or `[x, y, z]`.
- Each builder also returns wireframe segments `((x, y, z), (x, y, z))` for display. Segments are plain floats, not part of the model.

## Object types (field `type`)
| type | input fields | output fields |
|---|---|---|
| `box` | origin[3], width, depth, height (m) | none |
| `solar_block` | target_capacity (MW), module_rating (Wp), module_length, module_width (m), modules_per_table, table_rows (count), pitch (m), tilt, azimuth (deg), table_gap, front_height (m), origin[2] | table_length, table_slope_length, table_depth_horizontal, back_height (m); tables, tables_per_row, rows, modules (count); capacity (MW); table_rects[] |
| `fenced_compound` | width, depth, fence_height, post_spacing (m), origin[2] | perimeter (m), area (m2), posts (count) |
| `cable_route` | start[2], end[2], trench_depth, trench_width (m) | length (m), bearing (deg), trench_volume (m3) |
| `pylon_row` | start[2], bearing (deg), span (m), count, height (m) | positions[][2], route_length (m) |

### `table_rects[]` entries (enough for a DSM rasteriser)
- `row`, `index`: the row number (0 at the front) and the table's position in that row (unit `index`).
- `corners`: four `[x, y, z]` points, in this order: front-left, front-right, back-right, back-left. The front edge is at `front_height`, and the back edge is at `back_height`.
- `tilt` and `azimuth` (deg): the direction the table faces.
- `front_height` and `back_height` (m): heights above ground.

`scanner.fictional.solar_block_heights(model, extent, cell)` returns a height-above-ground grid (DSM − DTM) at cell centres. Row 0 of the grid is at y min. It can be compared directly with the virtual LiDAR loop.

## Rules
- `capacity` = tables × modules_per_table × module_rating. This is the target rounded up to whole tables, so it is always within one table of the target.
- Row r's front edge lies exactly r × pitch behind row 0, measured horizontally along the facing direction.
- When a value is later measured, replace its tag. Never average values across tags.
