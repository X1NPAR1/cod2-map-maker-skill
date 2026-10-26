# .map format and geometry generation

## File
```
iwmap 4
// entity 0
{
"classname" "worldspawn"
"_color" "0.5 0.5 0.62 1"
"sundirection" "-145 205 0"
"suncolor" ".55 .75 .8"
"sunlight" ".8"
"ambient" ".1"
"diffusefraction" ".5"
// brush 0
{
 ( 0 0 64 ) ( 64 0 64 ) ( 0 64 64 ) caulk 64 64 0 0 0 0 lightmap_gray 16384 16384 0 0 0 0
 ...
}
}
// entity 1
{
"classname" "info_player_start"
"origin" "0 0 16"
"angles" "0 90 0"
}
```
- Use CRLF. Keep `// brush N` / `// entity N` comments sequential (Radiant tolerates gaps, tools
  that patch maps often rely on them).
- Plane = 3 points; normal points outward via winding. Generate boxes from min/max; for wedges
  (ramps) compute the sloped plane from 3 points on it.
- Texture fields: `material  hscale vscale rotation hshift vshift 0 0`. To fit a texture exactly
  on a face (doors) scale = face size / texture size, shift = -min.

## Generator architecture (recommended)
- `kmap.py`-style library: `box()`, `box6(faces_dict)`, `wedge()/ramp()`, `ent()`, terrain mesh
  writer, `write_map()` with atomic replace.
- `gen_<map>.py`: terrain + buildings + props, imports `ent_<map>.py` for nodes/actors/vehicles.
- Store all positions in one coordinate system; if you work from a sketch image use
  `W(px,py)` = image px → world units (we used 6u per px).
- Terrain: triangle mesh (`patchTerrainDef3` or brush triangles) with height function; edges rise
  into high ridges to hide the skybox; roads carved as valleys that bend behind hills so spawns
  are invisible.
- Keep a list of solid volumes (building boxes, model radii) and test every spawner/node against
  it before writing (`free(x,y)`), and compute z from the terrain triangle under (x,y).

## Materials that worked (winter/Soviet)
Terrain `stalingradwinter_snow01/02/02blend`, cliffs `d_cliff04`, rubble `stalingradwinter_rubblesnow01`,
plaster `stalingradwinter_plaster01`, brick `stalingradwinter_brick02/03`, wood floor,
door `mtl_caen_door_wood_02`, roof `roof_slate01`, water `water_hill400_assault`.
Tool materials: `caulk`, `sky`, `clip`, `clip_player`, `origin`, `trigger`, `mantle_over`.
Avoid placeholder-looking textures (`*_shutters01`, `stalingrad_interiorwall01`); always check in game.

## Entities
- Point: `origin`, `angles "pitch yaw roll"`, `targetname`, `target`, `script_noteworthy`.
- Brush entities: `script_brushmodel`, `trigger_use`, `trigger_multiple`, `trigger_radius`
  (point: `radius`, `height`), `info_volume`.
- Models: `misc_model` (static, baked) vs `script_model` (scriptable; needed for multi-bone
  models like `prop_mortar`).
- Actors: `actor_axis_*`, `actor_ally_*` spawners with `spawnflags 1` (spawner), `count`,
  `script_aigroup`, `script_vehicleride`.
- Nodes: `node_pathnode`, `node_cover_stand/crouch/left/right/prone`, `node_concealment_*`,
  `node_cover_crouch_window`, `node_turret`. Radius ~42.
- Vehicles: `script_vehicle` with `vehicletype`, `model`, `target` → `info_vehicle_node` chain
  (`speed`, `lookahead`, `script_noteworthy`), `script_vehiclespawngroup`. Paths must be LINEAR.

## misc_prefab and the geo split (measured, cod2map 1.1)
- `{ "classname" "misc_prefab" "model" "prefabs/<path>.map" "origin" "x y z" "angles" "0 yaw 0" }`
  inserts another `.map` at compile time. Paths are relative to `map_source/`; nesting works.
- IW's main file includes its visual file with `"model" "<map>_geo.map"` at origin 0
  (`stock-map-anatomy.md` §1). Generate both and keep them in `map_source/`.
- Prefab placement, floor and facing rules plus a `prefab()` helper: `prefab-catalog.md` §2–4.

