# How Infinity Ward built a CoD2 SP map — `newvillers` anatomy (measured)

`map_source/newvillers.map` and `newvillers_geo.map` are the only stock SP sources that ship
with the Mod Tools. All numbers below come from `scripts/map_inspect.py` and a measurement
script run on those two files. Use them as the **quality bar** for every map you build, and the
"why" notes as design rules.

## 1. The file split: script layer vs. visual layer

| File | Entities | What lives there |
|---|---|---|
| `newvillers.map` | 3 026 | gameplay: 2 283 AI nodes, 306 trigger brushes, 251 spawners, 106 vehicle nodes, 5 vehicles, turrets, volumes, script origins |
| `newvillers_geo.map` | 6 208 | visuals: 1 369 terrain/road patches, 560 brushes, 693 `misc_prefab`, 4 718 `misc_model`, 132 lights |

The main file includes the visual file as **one prefab**:

```
{ "origin" "0 0 0"  "model" "newvillers_geo.map"  "classname" "misc_prefab" }
```

**Why:**
- The level designer (nodes, triggers, spawners) and the environment artist (terrain, buildings,
  props, lights) never edit the same file.
- The visual file can be rebuilt without touching the gameplay layer.

**Rule for us:** generate `<map>_geo.map` (visuals) and `<map>.map` (gameplay) separately, and
include the geo file with a `misc_prefab` at origin 0. `cod2map` expands it at compile time;
this is verified in `prefab_test`.

## 2. Buildings are prefabs, not hand brushes

693 `misc_prefab` entities place 68 distinct prefab files with `origin` + `angles` (yaw):

| count | prefab |
|---|---|
| 208 / 167 | `newvillers/walls/wallcolumn1_tall`, `wallsection1_tall` (garden walls built from column + section modules) |
| 53 / 45 | `wallcolumn1`, `wallsection1` (low variant) |
| 50 | `newvillers/props/villers_wood_barb` (wooden barbed fence) |
| 18 / 10 / 8 / 7 | `*_destroyed1/2` variants of the same wall modules mixed in |
| 7+5+4 | `windows/loft1-4`, `chimneys/*` (roof dressing added on top of building prefabs) |
| 3 / 2 | `corevillers/bldgs/noentry_bldg1_addon1_destroyed`, `2story2_destroyed` — the **American map uses corevillers buildings** |

Building prefabs are self-contained:
- walls, floors and stairs;
- doors, windows and shutters (nested prefabs);
- furniture (`misc_model`);
- interior lights;
- `portal` brushes in doorways and windows;
- often their own AI nodes.

Wall lines are **modules**: a column prefab every N units with a section prefab between, plus a
few destroyed variants for rhythm.
See `prefab-catalog.md` for every size, floor offset and front side.

## 3. Terrain and roads are many small mesh patches

- 1 321 `mesh` + 48 `curve` patches. Typical size is 4x4 (141), 2x2 (84), 3x3 (83) or 5x5 (70)
  control points. There is no single huge grid.
- Median edge length is **~85 units** for grass and mud, and ~69 for asphalt.
- Materials are layered as separate strips, not painted:

| material | patches | role |
|---|---|---|
| `v_grass` / `v_grass01` | 424 / 80 | fields |
| `v_mud_blend` / `v_mud` | 262 / 115 | yards, worn ground |
| `v_asphalt`, `v_asphaltdirt*`, `v_asphaltcrack_01` | 98 / 30 / 24 | streets |
| `v_dec_grassroad_edge` | 73 | **decal strip ~36 u wide** along every road edge (blends asphalt into grass) |
| `v_dec_mudtrack` | 63 | tyre tracks over mud |
| `v_dec_debris`, `v_rubble01` | 48 / 43 | rubble pads around destroyed buildings |
| `v_sidewalk01` / `v_sidewalktrim01` (+ curves) | 19 / 27 | kerbs |

**Rule for us:**
- Build terrain as many patches with ~64–96 u vertex spacing.
- Put a separate road mesh on top.
- Add **edge decal strips** (`*_edge`, `*_track`, `dec_*`) along roads and around ruins. The
  hard road/terrain border is the #1 thing that looks amateur.

## 4. World dressing density

| item | count | rule |
|---|---|---|
| grass clumps (`brush_newgrass_*`) | 3 966 | median **38 per 1000x1000 cell**, up to 257 in dense spots |
| weeds / flower clumps / tufts | 128 + 119 + 68 | around walls, under fences |
| hedges (`caen_hedge_wall_*`) | 133 | rows along field borders |
| trees (`tree_grey_oak_*`) | 65 | scales 1.0–2.3; never a single scale |
| barbed wire, dragon's teeth, hedgehogs | 69 / 26 / 16 | defensive lines at the town edge |
| barrels, crates, debris, haybales | ~80 | in yards and doorways, burnt debris near ruins |

`modelscale` is used on most models (257x 1.0, 44x 2, 39x 1.5, 26x 0.7, plus odd values such as
1.07 and 2.29). Varied scale and yaw are what make repetition invisible.

## 5. Borders and sky

- **Sky box:** 8 `sky_rainvillers` brushes form a 29 696 x 29 696 box, only 2 048 high, 64 thick.
- **Horizon:** a `mtl_caen_hedgerowbackdrop_01` backdrop mesh hides the field edge. Other stock
  maps place `backdrop_*` xmodels from script; see `stock-scripts-study.md`.
- **Fog and draw distance:** set in script with `setCullFog(300, 3500, ...)` (newvillers) or
  `setExpFog` plus `setCullDist` (desert maps).
- **Clip brushes:**
  - 91 `clip_player` blocks seal no-entry buildings and the play area (366–820 high).
  - 22 `clip_ai` pillars (~48x48x184) keep AI off props.
  - 12 `clip_nosight` volumes (up to 1588 long, 552–608 high) stand over hedgerows, so AI cannot
    see or shoot through foliage.
  - 14 `mantle_over` brushes (72–152 high) mark climbable walls.

## 6. Visibility portals

- There are 170 `portal` brushes, most of them 8–15 u thick slabs in doorways, windows and
  between floors.
- They come with the building prefabs. They only work where the cell is sealed: in an open test
  field, `cod2map` reports "portal ... has the same cell on both sides, portal ignored" and writes
  a portal leak file. This is harmless and the map still compiles (measured).
- In a sealed town they cut overdraw. Keep the prefab's portals and seal the town with
  structural walls and buildings.

## 7. AI layer (gameplay file)

**Nodes**
- 2 283 nodes. Nearest-neighbour spacing: median **53 u** (p10 29, p90 135, max 224).
- 47% are cover or concealment nodes:
  - 323 cover_stand, 230 cover_right, 221 cover_left, 94 cover_crouch, 77 cover_crouch_window;
  - 78 + 23 + 13 concealment.
- **Rule for us:** our old 180 u grids are 3x too sparse. Place nodes at ~48–96 u along streets,
  and put cover nodes on every wall corner, window and low wall.

**Triggers**

306 `trigger_multiple` brushes. The **texture tells the designer what the trigger does**; the
behaviour comes from its keys:

| texture | n | keys | meaning |
|---|---|---|---|
| `aitrig` | 84 | target, script_objective_active (53), script_baseoffire, script_deathchain | friendly-chain / squad movement triggers |
| `escort` | 55 | target | friendly escort chain links |
| `spawner_trigger` | 53 | target (spawners), spawnflags, script_killspawner | spawns the targeted spawners when touched |
| `kill` | 43 | script_killspawner (39) | deletes every spawner with the same killspawner number |
| `stopspawn` | 22 | target, script_linkName | stops flood spawners |
| `ambient` | 20 | script_ambient_outside / _inside | switches exterior / interior ambience |
| `trigger` | 29 | script_autosave (9), script_vehiclespawngroup | autosaves, vehicle spawns |

**Spawners**
- 251 spawners. Every one has `export`, 229 have `script_killspawner` and 132 have
  `script_deathchain`.
- spawnflags is 3 for 223 of them; `count` 3 marks multi-use spawners.

**Other entities**
- Volumes: 11 `info_volume` (`script_deathchain`).
- Vehicles: `script_vehicle` with `script_turret 0`, `script_avoidvehicles`,
  `script_vehiclestartmove`; 106 path nodes with `speed` 2–6 and `lookahead`.

## 8. Lights

132 lights:
- 84 `light_point_quadratic` (radius 250–400, intensity 0.3–0.5);
- 48 `light_point_linear_nocenter` spots (`exponent 4`, `fov_inner 80`, `fov_outer 180`).

Colours are cool blue-grey (`.4 .65 .70`) for the rainy night, with a few warm interior lamps
(`1 .8 .4`). The worldspawn sun is cool, with `ambient` 0.1–0.125 and `diffusefraction`
0.5–0.82.

## 9. Checklist: "does my map look like IW made it?"

- [ ] Gameplay and visuals are split (`_geo` prefab).
- [ ] Buildings come from theme prefabs (`prefab-catalog.md`) with their nested windows, doors and interiors.
- [ ] Walls and fences are modular prefab rows with destroyed variants.
- [ ] Terrain uses many patches at ~85 u; roads have edge-decal strips; ruins have rubble pads.
- [ ] 30–60 grass/weed clumps per 1000², trees at 3+ scales, hedges or dressing on every border.
- [ ] `clip_nosight` over foliage; `clip_player` around no-entry buildings; `mantle_over` on low walls.
- [ ] AI nodes ~50–100 u apart, about half of them cover nodes.
- [ ] Triggers use the stock key system (see `stock-scripts-study.md`) instead of custom loops.
- [ ] The horizon is closed by backdrop models or meshes; fog and cull distance are set in script.
