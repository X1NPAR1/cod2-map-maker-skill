# Stock prefabs: how to use them + measured catalogue

The Mod Tools ship 370 prefab `.map` files in `map_source/prefabs`. Infinity Ward built its towns from
them (`stock-map-anatomy.md` §2). Use them for every building, wall line and set dressing whose
theme matches the map; hand-built boxes are the fallback, not the default.

## 1. Choose the theme set by nation and setting

| map you build | use these folders | notes |
|---|---|---|
| **American / Normandy, France** (towns, villages, hedgerows) | `newvillers/` (217: bldgs, walls, windows, doors, chimneys, props, Detail), `corevillers/` (18 buildings) | newvillers itself mixes both; walls are column + section modules |
| **British / North Africa** (Egypt, Libya, Tunisia) | `libyatown/` (34 complete buildings: 1-2 storey, angled, mosque, towers, archway), `eldaba/` (balconies, windows, doors), `matmata/`, `mp_matmata/`, `toujane/` (merchants, crates, rugs, door) | eldaba/matmata are the stock British campaign maps |
| **Germany / late war** | `rhine/` (door, grave) + newvillers stone buildings | |
| **Soviet / Stalingrad** | no complete stock town kit (`stalingrad_winter` is referenced but **not shipped**) | build by hand (our kumtepe/burya generators) or reuse newvillers stone buildings with winter textures off |
| any | `interactable_objects/` (fuel barrels, crates, vase), `lamps/lantern_lit`, `traverse/` (wall_hop, jump_down_56/96, window_2: AI traverse helpers with negotiation nodes), `MP/` (objective kits) | `traverse` prefabs are how IW lets AI cross walls and windows |

## 2. Placement rules (measured with `prefab_test`)

- **Entity:** `{ "classname" "misc_prefab" "model" "prefabs/<theme>/<file>.map" "origin" "x y z" "angles" "0 yaw 0" }`.
  The path is relative to `map_source/`. Nested prefabs expand recursively (verified: the
  corevillers houses pull in their window, shutter, fireplace and door prefabs).
- **Floor:** nearly every building has `floor 0`, meaning its origin is ON the ground floor. Put
  `origin z` = ground height. A few prefabs have a negative floor (e.g. `2story4` -68,
  `church` -104) because they have cellar steps or a sunken base; raise them by that amount.
- **Facing:**
  - The `front` column is the bounding-box side that carries the doors, in prefab space.
  - The world direction of the front is that side rotated by `yaw`. `+x` at yaw 0 faces east;
    at yaw 90 it faces north.
  - To face a street whose outward direction is angle A, use `yaw = A - angle(front)`, with
    `+x` = 0, `+y` = 90, `-x` = 180, `-y` = 270.
  - Verified in the screenshot tour on 16 buildings, rotated ones included: doors were where the
    catalogue said.
- **Placing by centre:** the bounding box is not centred on the origin. To place a building by its
  centre, offset the origin by the rotated bbox centre (see `gen_prefab_test.py` in the skill
  history / `map-format.md` §prefab helper).
- **AI:**
  - Some building prefabs carry their own path and negotiation nodes. Do not lay your node grid
    through those buildings: cod2map reports "Duplicate linking nodes" on overlaps (measured on
    `townhall`). Leave a 64 u gap and run `yol_denetim.py` after connectpaths.
  - Every building prefab also contains `portal` brushes. These only work in a sealed town; in
    the open, cod2map ignores them with a warning (harmless).
- **Do not use:**
  - prefabs marked **missing nested** (they reference files that are not shipped:
    `libyatown/building_long`, `building_simple` → `toujane/tj_ladder1`;
    `newvillers/bldgs/carentan_02` → `stalingrad_winter/doorway01`);
  - `furniture_chinacabinet` / `dome_07`, which have no collision map (warnings only; they are
    still drawn).
- **Model-only prefabs** (`toujane/tj_merchant*`, lamps, MP lights) just place an xmodel at a fixed
  offset and yaw. Use them as preset dressing.

## 3. Composition patterns IW uses

- **Wall lines:**
  - Alternate `wallcolumn1(_tall)` and `wallsection1(_tall)`; a section is 152 u long, so the
    column pitch is 152 + column width.
  - Swap in every 4th–6th piece for a `_destroyed1/2` variant.
  - Use `wallsection_lowcover1*` where AI need low cover.
- **Buildings along a street:**
  - Face the doors to the street; vary the building type every 1–2 lots.
  - Fill gaps with garden walls, `villers_wood_barb` fences and gates (`props/gate1`).
- **Roof dressing:** add chimneys (`chimneys/*`) and lofts (`windows/loft*`) on plain roofs.
- **North Africa town:**
  - Mix `libyatown` 1- and 2-storey blocks with `building_angledwall*` at corners and
    `archway` over alleys.
  - Put `toujane` merchants and crate piles in the square; one `building_mosque` or tower as the
    landmark.

## 4. Generator helper (add to kmap.Harita)

```python
def prefab(self, path, x, y, z, yaw=0, cat=None, by_centre=False):
    """misc_prefab; cat = prefab-catalog.json record -> floor and centre correction."""
    if cat:
        b = cat['bounds']
        if b[2] < 0:
            z -= b[2]                          # sunken base -> lift so the floor sits on z
        if by_centre:
            cx, cy = (b[0] + b[3]) / 2.0, (b[1] + b[4]) / 2.0
            c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
            x, y = x - (cx * c - cy * s), y - (cx * s + cy * c)
    return self.ent('misc_prefab', model=path, origin=(round(x), round(y), round(z)), angles=(0, yaw, 0))
```

Regenerate the JSON with `python scripts/prefab_catalog.py "<CoD2>/map_source" catalog.md catalog.json`.

---


Generated by `scripts/prefab_catalog.py` from `map_source/prefabs`. Sizes are real brush-corner
bounds in world units (nested prefabs resolved). `floor` = lowest z relative to the prefab origin
(0 = origin sits on the floor). `front` = bounding-box side with the most door faces
(door x3 + portal + window); place the prefab with `yaw` so that side faces the street.
`-` = no openings found (wall pieces, props). `model-only` prefabs just place an xmodel with a fixed
offset/yaw. Prefabs marked **missing nested** reference prefab files that are not shipped -- do not use
them, or the compile drops those parts.


## MP — Multiplayer objective kits

| prefab | size x/y/z | floor | front | doors/win/portal | brushes | key materials / models |
|---|---|---|---|---|---|---|
| `crate_of_panzerfaust.map` | model-only | - | - | - | 0 | military_panzerfaust_box_empty |
| `ctf_flag_allies.map` | 0/0/0 | 0 | - | 0/0/0 | 0 |  |
| `ctf_flag_axis.map` | 0/0/0 | 0 | - | 0/0/0 | 0 |  |
| `lights/hangingbulb_on.map` | model-only | - | - | - | 0 | prop_lightbulb_on, prop_lightbulbwire |
| `lights/lampplain1.map` | model-only | - | - | - | 0 | light_lampplain_on |
| `lights/lantern1.map` | model-only | - | - | - | 0 | light_lantern_on |
| `sd_arrows.map` | 1536/2176/64 | 0 | - | 0/0/0 | 1 | color_blue, color_red, egypt_concrete_floor4 |
| `sd_bombtrigger.map` | 0/0/0 | 0 | - | 0/0/0 | 2 | origin, trigger |
| `sd_bombzone_a_ammodump_desert.map` | 171/290/108 | 0 | - | 0/0/0 | 15 | egypt_wood_stand_1, egypt_desertcamo_netting, origin |
| `sd_bombzone_a_ammodump_snow.map` | 64/116/8 | 0 | - | 0/0/0 | 41 | v_woodfloor01, stalingradwinter_snow02, origin |
| `sd_bombzone_a_armoredcar_desert.map` | 0/0/0 | 0 | - | 0/0/0 | 9 | clip_nosight_metal, origin, trigger |
| `sd_bombzone_a_desertflak.map` | 0/0/0 | 0 | - | 0/0/0 | 13 | clip_nosight_metal, origin, trigger |
| `sd_bombzone_a_desertflak_aa.map` | 0/0/0 | 0 | - | 0/0/0 | 3 | origin, trigger, clip_nosight |
| `sd_bombzone_a_flakveirling.map` | 0/0/0 | 0 | - | 0/0/0 | 17 | clip_nosight_metal, origin, trigger |
| `sd_bombzone_a_half_rockets_snow.map` | 0/0/0 | 0 | - | 0/0/0 | 4 | clip_nosight, origin, trigger |
| `sd_bombzone_a_half_rockets_wood.map` | 0/0/0 | 0 | - | 0/0/0 | 4 | clip_nosight, origin, trigger |
| `sd_bombzone_a_mortar.map` | 0/0/0 | 0 | - | 0/0/0 | 8 | clip_nosight, clip_nosight_metal, trigger |
| `sd_bombzone_a_normandyflak.map` | 0/0/0 | 0 | - | 0/0/0 | 12 | clip_nosight_metal, origin, trigger |
| `sd_bombzone_a_normandyflak_aa.map` | 0/0/0 | 0 | - | 0/0/0 | 3 | origin, trigger, clip_nosight |
| `sd_bombzone_a_opelblitz_desert.map` | 0/0/0 | 0 | - | 0/0/0 | 3 | origin, trigger, clip_nosight |
| `sd_bombzone_a_opelblitz_snow.map` | 0/0/0 | 0 | - | 0/0/0 | 3 | origin, trigger, clip_nosight |
| `sd_bombzone_a_opelblitz_wood.map` | 0/0/0 | 0 | - | 0/0/0 | 3 | origin, trigger, clip_nosight |
| `sd_bombzone_a_panzer2_desert.map` | 0/0/0 | 0 | - | 0/0/0 | 6 | clip_nosight_metal, origin, trigger |
| `sd_bombzone_a_panzer2_winter.map` | 0/0/0 | 0 | - | 0/0/0 | 6 | clip_nosight_metal, origin, trigger |
| `sd_bombzone_a_silo.map` | 414/419/528 | 0 | - | 0/0/0 | 283 | caulk, mtl_caen_wall_ext_10, nodraw_decal |
| `sd_bombzone_a_tiger_woodland_brush.map` | 0/0/0 | 0 | - | 0/0/0 | 4 | clip_nosight_metal, origin, trigger |
| `sd_bombzone_b_ammodump_desert.map` | 171/290/108 | 0 | - | 0/0/0 | 16 | egypt_wood_stand_1, egypt_desertcamo_netting, origin |
| `sd_bombzone_b_ammodump_snow.map` | 65/116/8 | 0 | - | 0/0/0 | 41 | v_woodfloor01, stalingradwinter_snow02, origin |
| `sd_bombzone_b_armoredcar_desert.map` | 0/0/0 | 0 | - | 0/0/0 | 9 | clip_nosight_metal, origin, trigger |
| `sd_bombzone_b_desertflak.map` | 0/0/0 | 0 | - | 0/0/0 | 13 | clip_nosight_metal, origin, trigger |
| `sd_bombzone_b_desertflak_aa.map` | 0/0/0 | 0 | - | 0/0/0 | 10 | clip_nosight_metal, origin, trigger |
| `sd_bombzone_b_flakveirling.map` | 0/0/0 | 0 | - | 0/0/0 | 17 | clip_nosight_metal, origin, trigger |
| `sd_bombzone_b_half_rockets_snow.map` | 0/0/0 | 0 | - | 0/0/0 | 4 | clip_nosight, origin, trigger |
| `sd_bombzone_b_half_rockets_wood.map` | 0/0/0 | 0 | - | 0/0/0 | 4 | clip_nosight, origin, trigger |
| `sd_bombzone_b_mortar.map` | 0/0/0 | 0 | - | 0/0/0 | 8 | clip_nosight, clip_nosight_metal, trigger |
| `sd_bombzone_b_normandyflak.map` | 0/0/0 | 0 | - | 0/0/0 | 12 | clip_nosight_metal, origin, trigger |
| `sd_bombzone_b_normandyflak_aa.map` | 0/0/0 | 0 | - | 0/0/0 | 3 | origin, trigger, clip_nosight |
| `sd_bombzone_b_opelblitz_desert.map` | 0/0/0 | 0 | - | 0/0/0 | 3 | origin, trigger, clip_nosight |
| `sd_bombzone_b_opelblitz_snow.map` | 0/0/0 | 0 | - | 0/0/0 | 3 | origin, trigger, clip_nosight |
| `sd_bombzone_b_opelblitz_wood.map` | 0/0/0 | 0 | - | 0/0/0 | 3 | origin, trigger, clip_nosight |
| `sd_bombzone_b_panzer2_desert.map` | 0/0/0 | 0 | - | 0/0/0 | 6 | clip_nosight_metal, origin, trigger |
| `sd_bombzone_b_panzer2_winter.map` | 0/0/0 | 0 | - | 0/0/0 | 6 | clip_nosight_metal, origin, trigger |
| `sd_bombzone_b_silo.map` | 224/224/528 | 0 | - | 0/0/0 | 281 | caulk, mtl_caen_wall_ext_10, nodraw_decal |
| `sd_bombzone_b_tiger_woodland_brush.map` | 0/0/0 | 0 | - | 0/0/0 | 3 | origin, trigger, clip_nosight |
| `sw_arrows.map` | 2304/768/0 | 0 | - | 0/0/0 | 0 | color_blue, color_red |

## corevillers — US / Normandy (Villers-Bocage core)

| prefab | size x/y/z | floor | front | doors/win/portal | brushes | key materials / models |
|---|---|---|---|---|---|---|
| `bldgs/2story2_destroyed.map` | 442/396/580 | 0 | -y | 1/13/0 | 308 | caulk, nodraw_decal, v_stonewall03 |
| `bldgs/2story3.map` | 444/502/624 | 0 | +x | 1/25/0 | 895 | caulk, v_plasterwall, nodraw_decal; prop_kitchenmetalpot, prop_diningplate_roundstack; nested: window8.map, underhang1.map, shutter_wood1_large.map, window8_white.map, fireplace1.map, fireplace_corner1.map, doorframe_interior_red1.map, brick_funnel_wide1.map, complex1.map, steps1.map |
| `bldgs/2story4.map` | 596/605/702 | -68 | +y | 2/16/0 | 240 | caulk, nodraw_decal, v_stonewall01; nested: window6.map, shutter_wood1_large.map, concrete_door_steps1.map, window_small2.map |
| `bldgs/2story5_detail.map` | 436/610/520 | 0 | +x | 0/20/0 | 725 | caulk, nodraw_decal, v_dec_darkstain02; light_walllightcrystal_off, furniture_plainchair; nested: shutter_wood1.map, window2.map, window2_frame.map, window_small1.map, fireplace1.map, fireplace_corner1.map, doorframe_interior_red1.map, shutter_wood1_small.map, lantern_lit.map |
| `bldgs/2story_small1_destroyed.map` | 380/398/484 | 0 | - | 1/0/0 | 494 | caulk, nodraw_decal, v_dec_darkstain08; nested: concrete_frame1.map, concrete_frame1_small.map, doorframe_interior_red1.map, concrete_door_steps1.map, gutterdrain_long_left.map, gutterdrain_long_right.map |
| `bldgs/2story_small1_lightdmg.map` | 380/408/484 | 0 | +x | 1/2/0 | 583 | caulk, nodraw_decal, v_dec_darkstain08; furniture_plainchair, furniture_walltable2; nested: gutterdrain_long_left.map, gutterdrain_long_right.map, lantern_lit.map |
| `bldgs/2story_small2.map` | 477/480/392 | 0 | +y | 0/20/0 | 489 | caulk, nodraw_decal, v_dec_darkstain08; crate01, furniture_plainchair; nested: window7.map, shutter_blue1.map, fancybrick1.map, doorframe_interior_red1.map, lantern_lit.map |
| `bldgs/2story_small3a.map` | 324/450/456 | 0 | -x | 0/0/9 | 847 | nodraw_decal, caulk, v_dec_darkstain08; nested: fancy_concrete1_wide.map, fancy_concrete1.map, concrete_fancy1.map |
| `bldgs/church.map` | 1024/1856/1191 | -104 | - | 10/21/0 | 2250 | caulk, nodraw_decal, v_dec_darkstain08; caen_churchpew_01, light_lantern_on; nested: church_arch.map, church_altar.map, church_window1.map, church_stainedglass.map, lantern_lit.map |
| `bldgs/fieldhq.map` | 864/1024/568 | 0 | - | 0/26/0 | 792 | caulk, v_dec_darkstain02, nodraw_decal; light_walllightcrystal_off, light_lantern_on; nested: wallsection_lowcover1_post.map, window1_frame.map, window1.map, shutter_blue1.map, chimney1.map, stone_funnel1.map, doorframe_interior_red1.map, wallsection_lowcover1.map, lantern_lit.map |
| `bldgs/noentry_bldg1.map` | 624/418/616 | 0 | +y | 2/27/0 | 314 | caulk, nodraw_decal, v_woodtrim01; nested: window5.map, window6.map, shutter_brown1.map, door1.map |
| `bldgs/noentry_bldg1_addon1.map` | 388/400/336 | 0 | +y | 1/6/0 | 122 | caulk, nodraw_decal, v_dec_darkstain08; nested: window5.map, door1.map |
| `bldgs/noentry_bldg1_addon1_destroyed.map` | 384/415/336 | 0 | +y | 1/6/0 | 279 | nodraw_decal, caulk, v_stonewall03; prop_wood_debris_big_burnt_01; nested: window5.map, door1.map, window5_grimy.map |
| `bldgs/noentry_bldg2.map` | 624/400/668 | 0 | +y | 2/12/0 | 603 | nodraw_decal, v_dec_darkstain08, caulk; nested: closed1.map, arched_door1.map, arched_closed1.map, chimney5.map, brick_funnel_thin1.map |
| `bldgs/noentry_bldg2_addon1.map` | 384/410/336 | 0 | +y | 1/0/0 | 81 | caulk, nodraw_decal, v_woodtrim03; nested: window_small2.map |
| `bldgs/postoffice.map` | 494/453/668 | 0 | -y | 0/53/14 | 1159 | caulk, v_plasterwall02, v_woodtrim03; furniture_plainchair, light_walllightcrystal_off; nested: postoffice_corner.map, postoffice_door1.map, postoffice_window1_open.map, shutter_blue2.map, postoffice_cubby.map, doorframe_interior_red1.map, postoffice_window1_wide_boarded.map, postoffice_window1.map, postoffice_window1_wide.map, lantern_lit.map |
| `bldgs/smalldestroyed1.map` | 324/452/336 | -16 | - | 0/0/0 | 399 | nodraw_decal, caulk, v_stonetrim04; nested: fancy_concrete1_wide.map, fancy_concrete1.map, concrete_fancy1.map |
| `bldgs/townhall.map` | 832/1288/1088 | 0 | - | 0/132/11 | 4682 | caulk, v_plasterwall02, v_dec_darkstain08; light_lantern_on, light_walllightcrystal_off; nested: wallcolumn3.map, wallsection2.map, townhall_window1.map, townhall_window1_small.map, townhall_window1_frame.map, townhall_interior_column1.map, townhall_stairdecor1.map, townhall_interior_door1.map, townhall_interior_door2.map, townhall_interior_column2.map, townhall_window2.map, townhall_stairdecor2.map, lantern_lit.map |

## eldaba — British / Egypt (El Daba)

| prefab | size x/y/z | floor | front | doors/win/portal | brushes | key materials / models |
|---|---|---|---|---|---|---|
| `ed_balcony.map` | 104/58/42 | 0 | +x | 0/3/0 | 10 | caulk, egypt_metal_balcony_side1, nodraw_decal |
| `ed_bldg_flpart2.map` | 273/394/144 | 0 | +x | 2/30/0 | 138 | caulk, nodraw_decal, egypt_wood_beam; nested: ed_window2c.map, ed_window2.map, ed_window2b.map, ed_mgtrap1_doorfrm.map, ed_window_bars.map |
| `ed_bldg_part2.map` | 324/401/136 | 0 | -x | 1/45/0 | 195 | caulk, nodraw_decal, egypt_concrete_generic1; nested: ed_window2c.map, ed_window2.map, ed_window2d.map, ed_window2b.map, ed_window_bars.map, ed_mgtrap1_doorfrm.map, ed_balcony.map |
| `ed_door3.map` | 72/12/110 | 0 | - | 0/0/0 | 15 | caulk, egypt_plaster_stucco1_body1, egypt_concrete_arch3trim |
| `ed_gutter_clamp.map` | 6/10/2 | -1 | +x | 2/0/0 | 4 | egypt_metal_rebar, nodraw_decal, toujane_door_knob1 |
| `ed_mgtrap1_doorfrm.map` | 52/12/98 | 0 | - | 0/0/0 | 3 | caulk, egypt_wood_beam |
| `ed_window2.map` | 60/16/80 | -40 | +y | 0/1/0 | 9 | caulk, egypt_wood_beam, egypt_concrete_generic1 |
| `ed_window2b.map` | 60/16/80 | -40 | +y | 0/6/0 | 14 | caulk, nodraw_decal, egypt_wood_beam |
| `ed_window2c.map` | 60/16/80 | -40 | +y | 0/2/0 | 10 | caulk, egypt_wood_beam, egypt_concrete_generic1 |
| `ed_window2d.map` | 60/16/80 | -40 | +y | 0/5/0 | 13 | caulk, egypt_wood_beam, egypt_concrete_generic1 |
| `ed_window4.map` | 44/24/64 | -32 | +y | 0/6/0 | 10 | caulk, nodraw_decal, egypt_wood_generic1 |
| `ed_window4b.map` | 44/24/64 | -32 | +x | 0/1/0 | 5 | caulk, egypt_wood_generic1, egypt_window7 |
| `ed_window4d.map` | 44/24/64 | -32 | +y | 0/6/0 | 10 | caulk, nodraw_decal, egypt_wood_generic1 |
| `ed_window8.map` | 32/8/32 | -16 | +x | 0/1/0 | 5 | caulk, egypt_wood_generic1, egypt_window6 |
| `ed_window_bars.map` | 7/48/68 | -0 | +x | 0/1/0 | 1 | nodraw_decal, egypt_decal_windowbars |

## interactable_objects — Generic props

| prefab | size x/y/z | floor | front | doors/win/portal | brushes | key materials / models |
|---|---|---|---|---|---|---|
| `benzin.map` | 0/0/0 | 0 | - | 0/0/0 | 1 | clip_nosight |
| `benzin_snow.map` | 0/0/0 | 0 | - | 0/0/0 | 1 | clip_nosight |
| `egypt_prop_vase1.map` | 0/0/0 | 0 | - | 0/0/0 | 1 | clip_nosight |
| `prop_barrel_benzin.map` | 0/0/0 | 0 | - | 0/0/0 | 1 | clip_nosight |
| `prop_barrel_benzin_snow.map` | 0/0/0 | 0 | - | 0/0/0 | 1 | clip_nosight |
| `prop_crate_dak1.map` | 0/0/0 | 0 | - | 0/0/0 | 1 | clip_nosight |
| `prop_crate_dak2.map` | 0/0/0 | 0 | - | 0/0/0 | 1 | clip_nosight |
| `prop_crate_dak3.map` | 0/0/0 | 0 | - | 0/0/0 | 1 | clip_nosight |
| `prop_crate_dak4.map` | 0/0/0 | 0 | - | 0/0/0 | 1 | clip_nosight |
| `prop_crate_dak5.map` | 0/0/0 | 0 | - | 0/0/0 | 1 | clip_nosight |
| `prop_crate_dak6.map` | 0/0/0 | 0 | - | 0/0/0 | 1 | clip_nosight |
| `prop_crate_dak7.map` | 0/0/0 | 0 | - | 0/0/0 | 1 | clip_nosight |
| `prop_crate_dak8.map` | 0/0/0 | 0 | - | 0/0/0 | 1 | clip_nosight |
| `prop_crate_dak9.map` | 0/0/0 | 0 | - | 0/0/0 | 1 | clip_nosight |

## lamps — Generic lights

| prefab | size x/y/z | floor | front | doors/win/portal | brushes | key materials / models |
|---|---|---|---|---|---|---|
| `lantern_lit.map` | 0/0/0 | 0 | - | 0/0/0 | 1 | clip_nosight_metal; light_lantern_on |

## libyatown — British / Libya (town kit)

| prefab | size x/y/z | floor | front | doors/win/portal | brushes | key materials / models |
|---|---|---|---|---|---|---|
| `archway.map` | 200/306/278 | 0 | - | 0/0/0 | 27 | egypt_plaster_exteriorwall01_body, caulk, nodraw_decal |
| `board1.map` | 149/18/2 | 0 | - | 0/0/0 | 1 | toujane_woodtrim1 |
| `building_1n1halfstory.map` | 456/344/256 | -0 | -y | 2/12/0 | 130 | egypt_wood_generic1, caulk, egypt_plaster_exteriorwall02; awning_2x4-5_3 |
| `building_2storycornerinset.map` | 520/576/296 | 0 | +x | 3/9/0 | 197 | caulk, egypt_plaster_exteriorwall02, nodraw_decal; awning_desert_market_medium1 |
| `building_2storysquare.map` | 385/454/365 | -1 | -y | 2/3/0 | 55 | caulk, egypt_plaster_exteriorwall02, toujane_metal_shelter1; awning_desert_market_large2 |
| `building_angledwall.map` | 584/450/344 | -16 | -y | 3/5/0 | 113 | caulk, toujane_plasterwall_top_s, toujane_plasterwall_bottom |
| `building_angledwall2.map` | 584/449/344 | -16 | -y | 3/5/0 | 112 | caulk, egypt_plaster_stucco1, toujane_decal_adobe1_top; awning_desert_wood_long |
| `building_brown1story.map` | 416/296/160 | 0 | -y | 1/3/0 | 72 | egypt_wood_generic1, caulk, toujane_plasterwall_bottom_s; awning_desert_wood_long |
| `building_brown2story.map` | 592/336/408 | 0 | -y | 3/8/0 | 175 | egypt_wood_generic1, caulk, egypt_plaster_exteriorwall02; prop_doorknob1, awning_desert_wood4; nested: tj_door01.map |
| `building_long.map **(missing nested: tj_ladder1.map)**` | 962/812/424 | 0 | +x | 3/5/0 | 157 | toujane_wood_post1, caulk, toujane_plasterwall_top_s; prop_doorknob1; nested: tj_ladder1.map, tj_door01.map |
| `building_mosque.map` | 360/360/892 | 0 | - | 0/6/0 | 335 | caulk, egypt_plaster_exteriorwall01_body, egypt_concrete_generic1trim1; dome_07 |
| `building_roundtop.map` | model-only | - | - | - | 0 | dome_06 |
| `building_roundtop2.map` | model-only | - | - | - | 0 | dome_05 |
| `building_simple.map **(missing nested: tj_ladder1.map)**` | 680/680/160 | 0 | +x | 1/5/0 | 80 | caulk, toujane_plasterwall_top_s, toujane_plasterwall_bottom_s; prop_doorknob1; nested: tj_ladder1.map, tj_door01.map |
| `building_simple2.map` | 640/680/186 | 0 | +x | 1/5/0 | 76 | egypt_plaster_stucco1, caulk, mtl_caen_decal_stain_plasterwall_02; prop_doorknob1, awning_desert_wood1; nested: tj_door01.map |
| `building_simplel.map` | 384/280/208 | -0 | -x | 1/6/0 | 85 | egypt_wood_generic1, caulk, egypt_plaster_stucco1; prop_doorknob1, awning_2x4-5_1; nested: tj_door01.map |
| `building_simplesmall.map` | 268/256/144 | 0 | +x | 0/1/0 | 54 | egypt_wood_generic1, caulk, egypt_plaster_stucco1 |
| `detail_brownchimney.map` | 44/32/152 | 0 | - | 0/0/0 | 3 | toujane_dirt_trim_dark, caulk, toujane_plasterwall_bottom_s |
| `detail_whitechimney.map` | 48/48/136 | 0 | - | 0/0/0 | 3 | toujane_decal_adobe1_top, caulk, egypt_plaster_stucco1 |
| `dometop.map` | 448/384/170 | 0 | +x | 0/4/0 | 17 | caulk, egypt_plaster_exteriorwall01_body, egypt_window1; dome_05; nested: building_roundtop2.map |
| `dometop_open.map` | 448/384/170 | 0 | +x | 0/3/0 | 17 | caulk, egypt_plaster_exteriorwall01_body, egypt_decal_window1; dome_05; nested: building_roundtop2.map |
| `dragontooth.map` | 42/42/47 | 0 | - | 0/0/0 | 2 | nodraw_decal, egypt_decal_brick8_bottom, egypt_concrete_floor1_body |
| `facade1.1.map` | 448/332/224 | 0 | -y | 2/6/0 | 77 | egypt_wood_generic1, caulk, egypt_plaster_exteriorwall02; awning_2x4-5_3 |
| `facade1.map` | 448/332/224 | 0 | +y | 0/6/0 | 70 | egypt_wood_generic1, caulk, egypt_plaster_exteriorwall02; awning_2x4-5_1 |
| `facade2.map` | 384/448/364 | 0 | - | 0/0/0 | 24 | caulk, nodraw_decal, egypt_plaster_exteriorwall02 |
| `facade3.map` | 584/420/328 | 0 | - | 0/0/0 | 60 | caulk, egypt_plaster_stucco1, egypt_decal_brick7_top |
| `facade4.map` | 592/336/408 | 0 | +x | 0/4/0 | 78 | egypt_wood_generic1, caulk, egypt_plaster_exteriorwall02 |
| `palmtree_tall.map` | 256/256/512 | 0 | - | 0/0/0 | 0 | africa_palm_backdrop |
| `pole_short.map` | 6/64/6 | -3 | - | 0/0/0 | 0 | egypt_wood_beam_end, egypt_wood_beam |
| `post.map` | 10/12/172 | 0 | - | 0/0/0 | 1 | caulk, toujane_woodtrim1 |
| `smallbase1.map` | 18/16/10 | 0 | - | 0/0/0 | 2 | caulk, egypt_plaster_exteriorwall02, nodraw_decal |
| `tower1.map` | 146/146/839 | 0 | +y | 0/6/0 | 82 | caulk, egypt_plaster_exteriorwall01_body, toujane_window6; dome_07 |
| `tower2.map` | 140/140/875 | 0 | +y | 0/6/0 | 97 | caulk, egypt_plaster_exteriorwall01_body, toujane_window6 |
| `wallsupport1.map` | 36/36/194 | 12 | - | 0/0/0 | 60 | caulk, egypt_plaster_stucco1, nodraw_decal |

## matmata — British / Tunisia (Matmata)

| prefab | size x/y/z | floor | front | doors/win/portal | brushes | key materials / models |
|---|---|---|---|---|---|---|
| `mat_bldg04.map` | 640/680/186 | 0 | +x | 1/5/0 | 76 | egypt_plaster_stucco1, caulk, mtl_caen_decal_stain_plasterwall_02; prop_doorknob1, awning_desert_wood1; nested: tj_door01.map |

## mp_matmata — British / Tunisia (MP Matmata)

| prefab | size x/y/z | floor | front | doors/win/portal | brushes | key materials / models |
|---|---|---|---|---|---|---|
| `2story2.map` | 372/268/290 | -20 | +y | 9/74/0 | 324 | caulk_shadow, caulk, nodraw_decal; nested: ed_mgtrap1_doorfrm.map, ed_window4.map, ed_window4d.map, ed_window4b.map, ed_window8.map, ed_gutter_clamp.map, ed_door3.map |
| `building06.map` | 592/336/408 | 0 | -y | 3/19/0 | 215 | egypt_wood_generic1, caulk, egypt_plaster_exteriorwall02; prop_doorknob1, awning_desert_wood4; nested: tj_door01.map |
| `building_brown2story2.map` | 664/336/408 | 0 | -y | 3/8/0 | 156 | egypt_wood_generic1, caulk, egypt_plaster_exteriorwall02; prop_doorknob1, awning_desert_wood4; nested: tj_door01.map |
| `building_brown2story3.map` | 592/336/408 | 0 | -y | 3/8/0 | 178 | egypt_wood_generic1, caulk, egypt_plaster_exteriorwall02; prop_doorknob1, awning_desert_wood4; nested: tj_door01.map |
| `building_simple3.map` | 640/680/186 | 0 | +x | 1/5/0 | 83 | egypt_plaster_stucco1, caulk, mtl_caen_decal_stain_plasterwall_02; prop_doorknob1, awning_desert_wood1; nested: tj_door01.map |
| `dometop.map` | 415/352/171 | 0 | +x | 0/4/0 | 21 | caulk, egypt_plaster_exteriorwall01_body, egypt_window1; dome_07 |
| `ladder_weaponclip.map` | 24/6/192 | 0 | - | 0/0/0 | 10 | toujane_woodtrim1 |
| `pole_short.map` | 6/64/6 | -3 | - | 0/0/0 | 0 | egypt_wood_beam_end, egypt_wood_beam |

## newvillers — US / Normandy (Villers-Bocage)

| prefab | size x/y/z | floor | front | doors/win/portal | brushes | key materials / models |
|---|---|---|---|---|---|---|
| `Detail/Villers_road_detail.map` | 29824/29824/2176 | -384 | - | 2/210/17 | 7364 | caulk, v_plasterwall02, v_dec_darkstain08; caen_grasstuft_group_01, light_walllightcrystal_off; nested: 2story3_destroyed.map, window8.map, underhang1.map, shutter_wood1_large.map, window8_white.map, steps1.map, brick_funnel_wide1.map, fireplace_corner1.map, fireplace1.map, 2story_small2.map, window7.map, shutter_blue1.map, fancybrick1.map, doorframe_interior_red1.map, 2story3.map, complex1.map, townhall.map, wallcolumn3.map, wallsection2.map, townhall_window1.map, townhall_window1_small.map, townhall_window1_frame.map, townhall_interior_column1.map, townhall_stairdecor1.map, townhall_interior_door1.map, townhall_interior_door2.map, townhall_interior_column2.map, townhall_window2.map, townhall_stairdecor2.map, 2story4.map, window6.map, concrete_door_steps1.map, window_small2.map, wallcolumn1_tall.map, wallsection1_tall.map, wallcolumn1.map, wallsection_lowcover1_post.map |
| `bldgs/2story1.map` | 590/410/560 | 0 | -y | 1/20/9 | 580 | caulk, nodraw_decal, mtl_caen_stair_run_int_worn_01; furniture_couch, furniture_fullbed; nested: window3.map, shutter_wood2.map, window4.map, shutter_wood_arched1.map, doorframe_archstepped1.map, gutterdrain_right.map, fireplace2.map, chimney3.map, loft2.map, doorframe_interior_red1.map, gutterdrain_left.map |
| `bldgs/2story1a.map` | 604/424/560 | 0 | -y | 0/20/11 | 695 | caulk, nodraw_decal, v_stonewall03; light_walllightcrystal_off, furniture_officechair; nested: window3.map, shutter_wood2.map, window4.map, shutter_wood_arched1.map, doorframe_archstepped1.map, gutterdrain_right.map, fireplace2.map, chimney3.map, loft2.map, doorframe_interior_red1.map, gutterdrain_left.map, fireplace1.map |
| `bldgs/2story2_destroyed.map` | 442/396/580 | 0 | -y | 1/13/0 | 309 | caulk, nodraw_decal, v_stonewall03 |
| `bldgs/2story3.map` | 444/502/624 | 0 | -x | 0/25/0 | 914 | caulk, v_plasterwall, nodraw_decal; prop_kitchenmetalpot, prop_kitchenmetalpan; nested: window8.map, underhang1.map, shutter_wood1_large.map, window8_white.map, fireplace1.map, fireplace_corner1.map, doorframe_interior_red1.map, brick_funnel_wide1.map, complex1.map, steps1.map |
| `bldgs/2story3_destroyed.map` | 480/460/624 | 0 | +x | 0/17/6 | 987 | caulk, v_stonewall03, v_dec_darkstain08; light_walllightcrystal_off, furniture_armchair; nested: window8.map, underhang1.map, shutter_wood1_large.map, window8_white.map, steps1.map, brick_funnel_wide1.map, fireplace_corner1.map, fireplace1.map |
| `bldgs/2story3_destroyed_detail.map` | 480/460/624 | 0 | +x | 0/17/0 | 1057 | caulk, v_dec_darkstain08, nodraw_decal; furniture_plainchair, furniture_ovaldiningtable; nested: window8.map, underhang1.map, shutter_wood1_large.map, window8_white.map, steps1.map, brick_funnel_wide1.map, fireplace_corner1.map, fireplace1.map |
| `bldgs/2story3_destroyed_new.map` | 1000/1150/624 | 0 | -x | 0/19/6 | 910 | caulk, v_stonewall03, v_plasterwall; light_walllightcrystal_off, furniture_armchair; nested: window8.map, underhang1.map, shutter_wood1_large.map, window8_white.map, window1_structural.map, steps1.map, brick_funnel_wide1.map, fireplace_corner1.map |
| `bldgs/2story4.map` | 596/605/702 | -68 | +y | 2/16/0 | 240 | caulk, nodraw_decal, v_stonewall01; nested: window6.map, shutter_wood1_large.map, concrete_door_steps1.map, window_small2.map |
| `bldgs/2story5.map` | 436/610/520 | 0 | +x | 0/20/0 | 820 | caulk, v_dec_darkstain02, nodraw_decal; furniture_plainchair, light_walllightcrystal_off; nested: shutter_wood1.map, window2.map, window_small1.map, fireplace1.map, fireplace_corner1.map, doorframe_interior_red1.map, shutter_wood1_small.map |
| `bldgs/2story5_detail.map` | 436/610/520 | 0 | +x | 0/20/0 | 754 | caulk, nodraw_decal, v_dec_darkstain02; light_walllightcrystal_off, furniture_plainchair; nested: shutter_wood1.map, window2.map, window2_frame.map, window_small1.map, fireplace1.map, fireplace_corner1.map, doorframe_interior_red1.map, shutter_wood1_small.map |
| `bldgs/2story_floor1only_bldg1.map` | 628/409/620 | -4 | -y | 1/22/8 | 426 | caulk, nodraw_decal, v_dec_darkstain08; furniture_plainchair, light_walllightcrystal_off; nested: window5.map, door1_frame.map, window6_frame.map, shutter_brown1.map, window6.map, doorframe_interior_red1.map |
| `bldgs/2story_small1.map` | 380/398/484 | 0 | - | 1/0/0 | 443 | caulk, nodraw_decal, v_woodtrim03; nested: gutterdrain_long_left.map, gutterdrain_long_right.map |
| `bldgs/2story_small1_destroyed.map` | 380/398/484 | 0 | - | 1/0/0 | 501 | caulk, nodraw_decal, v_dec_darkstain08; furniture_plainchair, furniture_walltable2_d; nested: concrete_frame1.map, concrete_frame1_small.map, doorframe_interior_red1.map, concrete_door_steps1.map, gutterdrain_long_left.map, gutterdrain_long_right.map |
| `bldgs/2story_small1_lightdmg.map` | 380/408/484 | 0 | +x | 1/2/0 | 591 | caulk, nodraw_decal, v_dec_darkstain08; furniture_plainchair, furniture_walltable2; nested: gutterdrain_long_left.map, gutterdrain_long_right.map |
| `bldgs/2story_small2.map` | 477/480/392 | 0 | +y | 0/20/0 | 486 | caulk, nodraw_decal, v_dec_darkstain08; crate01, furniture_plainchair; nested: window7.map, shutter_blue1.map, fancybrick1.map, doorframe_interior_red1.map |
| `bldgs/2story_small3.map` | 324/452/456 | 0 | -x | 0/0/11 | 819 | nodraw_decal, caulk, v_stonetrim04; nested: fancy_concrete1_wide.map, fancy_concrete1.map, concrete_fancy1.map |
| `bldgs/2story_small3a.map` | 324/450/456 | 0 | -x | 0/0/9 | 857 | caulk, nodraw_decal, v_dec_darkstain08; nested: fancy_concrete1_wide.map, fancy_concrete1.map, concrete_fancy1.map |
| `bldgs/2story_small_garage1.map` | 380/970/548 | -64 | -x | 0/0/12 | 626 | caulk, nodraw_decal, v_dec_darkstain08; light_walllightcrystal_off, furniture_plainchair; nested: gutterdrain_long_right.map, gutterdrain_long_left.map, concrete_frame1_clean.map, concrete_frame1_small_clean.map, concrete_door_steps1_clean.map, doorframe_interior_red1.map, fireplace_corner1.map, fireplace1.map |
| `bldgs/carentan_01.map` | 352/288/528 | 0 | +x | 0/70/0 | 155 | caulk, mtl_caen_window_shutter_03, v_stonetrim03; nested: square_window_open.map, square_doorway.map, shutter_grey1.map |
| `bldgs/carentan_02.map **(missing nested: doorway01.map)**` | 430/570/616 | -24 | - | 0/0/0 | 464 | caulk, dawnville2_concrete_floor01, v_stonetrim06; furniture_plainchair, furniture_bookshelves1; nested: doorway01.map, fancy_concrete2_wide.map, concrete_door_steps1.map, fireplace1.map |
| `bldgs/church.map` | 1024/1856/1191 | -104 | - | 10/19/0 | 2273 | caulk, v_dec_darkstain08, nodraw_decal; caen_churchpew_01; nested: church_arch.map, church_altar.map, church_window1.map, church_stainedglass.map |
| `bldgs/fieldhq.map` | 864/1024/568 | 0 | - | 0/26/0 | 816 | caulk, v_dec_darkstain02, v_colum_stonewall01; light_walllightcrystal_off, furniture_plainchair; nested: wallcolumn3.map, wallsection2.map, window1_frame.map, window1.map, shutter_blue1.map, chimney1.map, stone_funnel1.map, doorframe_interior_red1.map |
| `bldgs/noentry_bldg1.map` | 624/418/616 | 0 | +y | 2/27/0 | 314 | caulk, nodraw_decal, v_woodtrim01; nested: window5.map, window6.map, shutter_brown1.map, door1.map |
| `bldgs/noentry_bldg1_addon1.map` | 388/400/336 | 0 | +y | 1/6/0 | 124 | caulk, nodraw_decal, v_dec_darkstain08; nested: window5.map, door1.map |
| `bldgs/noentry_bldg1_addon1_destroyed.map` | 384/415/336 | 0 | +y | 1/6/0 | 276 | nodraw_decal, caulk, v_stonewall03; prop_wood_debris_big_burnt_01; nested: window5.map, door1.map, window5_grimy.map |
| `bldgs/noentry_bldg1_noback.map` | 624/407/616 | 0 | -y | 1/10/0 | 172 | caulk, nodraw_decal, mtl_caen_decal_lightstain_04; nested: window5.map, window6.map, shutter_brown1.map, door1.map |
| `bldgs/noentry_bldg2.map` | 624/400/668 | 0 | +y | 2/12/0 | 521 | caulk, nodraw_decal, v_dec_darkstain08; nested: closed1.map, arched_door1.map, arched_closed1.map, chimney5.map, brick_funnel_thin1.map |
| `bldgs/noentry_bldg2_addon1.map` | 384/410/336 | 0 | +y | 1/0/0 | 81 | caulk, nodraw_decal, v_woodtrim03; nested: window_small2.map |
| `bldgs/objbldg_2.map` | 518/600/528 | 8 | -x | 73/3/0 | 465 | caulk, mtl_caen_trim_ext_plaster_01, mtl_caen_wall_ext_04 |
| `bldgs/postoffice.map` | 494/453/668 | 0 | -y | 0/59/14 | 1270 | caulk, v_woodtrim03, v_plasterwall02; light_walllightornate_off, furniture_plainchair; nested: postoffice_corner.map, postoffice_door1.map, postoffice_window1_open.map, shutter_blue2.map, postoffice_window1.map, postoffice_cubby.map, doorframe_interior_red1.map, postoffice_window1_wide_boarded.map, postoffice_window1_wide.map |
| `bldgs/postoffice_corner.map` | 112/22/383 | 0 | - | 0/0/0 | 90 | caulk, nodraw_decal, v_dec_darkstain08 |
| `bldgs/smalldestroyed1.map` | 324/452/336 | -16 | - | 0/0/0 | 399 | nodraw_decal, caulk, v_stonetrim04; nested: fancy_concrete1_wide.map, fancy_concrete1.map, concrete_fancy1.map |
| `bldgs/townhall.map` | 832/1288/1088 | 0 | - | 0/132/11 | 4646 | caulk, v_plasterwall02, v_dec_darkstain08; light_walllightcrystal_off, furniture_bookshelveswide; nested: wallcolumn3.map, wallsection2.map, townhall_window1.map, townhall_window1_small.map, townhall_window1_frame.map, townhall_interior_column1.map, townhall_stairdecor1.map, townhall_interior_door1.map, townhall_interior_door2.map, townhall_interior_column2.map, townhall_window2.map, townhall_stairdecor2.map |
| `bldgs/villers_2story1.map` | 436/610/520 | 0 | +x | 0/22/0 | 822 | caulk, nodraw_decal, v_dec_darkstain02; light_walllightcrystal_off, furniture_plainchair; nested: shutter_wood1.map, villers_window_01_d.map, villers_window_01_open.map, fireplace1.map, doorframe_interior_red1.map, shutter_wood1_small.map, villers_window_small_01.map, villers_window_01.map, lantern_lit.map, window_2.map |
| `bldgs/villers_2story2.map` | 436/610/520 | 0 | +x | 1/25/0 | 796 | caulk, nodraw_decal, v_dec_darkstain02; light_walllightcrystal_off, prop_diningplate_roundstack; nested: shutter_wood1.map, villers_window_01_open.map, villers_window_01_d.map, villers_window_01.map, fireplace2.map, doorframe_interior_red1.map, shutter_wood1_small.map, villers_window_small_01.map, lantern_lit.map |
| `bldgs/villers_2story3.map` | 480/460/624 | 0 | +x | 0/20/0 | 846 | caulk, nodraw_decal, v_dec_darkstain08; furniture_bookshelvestall, prop_diningplate_roundplain; nested: villers_window_02.map, underhang1.map, shutter_wood1_large.map, villers_window_03.map, steps1.map, brick_funnel_wide1.map, fireplace1.map, fireplace_corner1.map, lantern_lit.map |
| `bldgs/villers_2story4.map` | 480/460/624 | 0 | +x | 0/20/0 | 898 | caulk, nodraw_decal, v_dec_darkstain08; furniture_bookshelvestall, prop_diningplate_roundplain; nested: villers_window_02.map, underhang1.map, shutter_wood1_large.map, steps1.map, brick_funnel_wide1.map, fireplace1.map, fireplace_corner1.map |
| `bldgs/villers_2story5.map` | 480/460/624 | 0 | +x | 1/20/0 | 883 | caulk, nodraw_decal, v_dec_darkstain08; prop_diningplate_roundplain, furniture_plainchair; nested: villers_window_02.map, underhang1.map, shutter_wood1_large.map, villers_window_03.map, steps1.map, brick_funnel_wide1.map, fireplace1.map, fireplace_corner1.map, lantern_lit.map |
| `bldgs/villers_2story6.map` | 380/398/484 | 0 | -x | 2/3/0 | 628 | caulk, nodraw_decal, v_dec_darkstain08; furniture_plainchair, furniture_frenchbathfaucet; nested: concrete_frame1.map, concrete_frame1_small.map, doorframe_interior_red1.map, concrete_door_steps1.map, gutterdrain_long_left.map, gutterdrain_long_right.map, lantern_lit.map |
| `bldgs/villers_2story7.map` | 477/480/392 | 0 | +y | 1/20/0 | 481 | caulk, nodraw_decal, v_dec_darkstain08; crate01, furniture_plainchair; nested: window7.map, shutter_blue1.map, fancybrick1.map, doorframe_interior_red1.map |
| `bldgs/villers_2story8.map` | 480/460/624 | 0 | +x | 0/20/0 | 928 | caulk, nodraw_decal, v_dec_darkstain08; furniture_walltable2, light_lampdesk_off; nested: villers_window_02.map, underhang1.map, shutter_wood1_large.map, steps1.map, brick_funnel_wide1.map, fireplace1.map, fireplace_corner1.map, lantern_lit.map |
| `bldgs/villers_chimney01.map` | 88/60/585 | 0 | - | 0/0/0 | 28 | caulk, v_stonewall04, v_dec_darkstain01 |
| `bldgs/villers_corner_d.map` | 388/394/462 | -14 | -y | 0/10/0 | 202 | caulk, nodraw_decal, v_dec_darkstain08; nested: villers_fireplace01.map, shutter_grey1.map |
| `bldgs/villers_fireplace01.map` | 88/60/462 | 0 | - | 0/0/0 | 23 | caulk, v_stonewall04, v_dec_darkstain01 |
| `bldgs/villers_noentry1.map` | 628/409/616 | 0 | -y | 0/24/0 | 341 | caulk, nodraw_decal, v_woodtrim01; nested: window5.map, door1_frame.map, window6.map, shutter_brown1.map |
| `bldgs/villers_noentry2.map` | 590/424/560 | 0 | -y | 0/22/0 | 406 | caulk, nodraw_decal, v_stonewall03; nested: window3.map, shutter_wood2.map, window4.map, shutter_wood_arched1.map, doorframe_archstepped1.map, gutterdrain_right.map, chimney3.map, loft2.map, gutterdrain_left.map |
| `bldgs/villers_noentry3.map` | 380/970/548 | -64 | - | 0/0/0 | 360 | caulk, nodraw_decal, v_plasterwall; nested: gutterdrain_long_right.map, gutterdrain_long_left.map, concrete_frame1_clean.map, concrete_frame1_small_clean.map, concrete_door_steps1_clean.map, doorframe_interior_red1.map |
| `chimneys/brick_funnel_thin1.map` | 16/16/44 | 0 | - | 0/0/0 | 0 | v_brick01 |
| `chimneys/brick_funnel_wide1.map` | 24/24/44 | 0 | - | 0/0/0 | 0 | v_brick01 |
| `chimneys/brick_thin1.map` | 36/80/124 | 0 | - | 0/0/0 | 5 | caulk, v_stonetrim01, nodraw_decal |
| `chimneys/brick_wide1.map` | 36/116/124 | 0 | - | 0/0/0 | 5 | caulk, v_stonetrim01, nodraw_decal |
| `chimneys/chimney1.map` | 40/72/228 | 0 | - | 0/0/0 | 17 | caulk, v_stonetrim01, v_dec_darkstain01 |
| `chimneys/chimney2.map` | 72/40/188 | 0 | - | 0/0/0 | 14 | caulk, nodraw_decal, v_dec_darkstain08 |
| `chimneys/chimney3.map` | 24/53/116 | 0 | - | 0/0/0 | 4 | v_stonetrim02, caulk, v_stonetrim01 |
| `chimneys/chimney4.map` | 32/72/98 | 0 | - | 0/0/0 | 3 | caulk, mtl_caen_trim_ext_02, mtl_caen_wall_256tile_plasterbeige_01 |
| `chimneys/chimney5.map` | 32/72/140 | 0 | - | 0/0/0 | 6 | caulk, v_stonewall04, v_stonetrim03 |
| `chimneys/complex1.map` | 72/40/112 | 0 | - | 0/0/0 | 18 | caulk, v_stonetrim04, nodraw_decal |
| `chimneys/stone_funnel1.map` | 24/24/44 | 0 | - | 0/0/0 | 0 | v_stonewall04 |
| `doors/arched_block_door.map` | 66/9/118 | -26 | - | 0/0/0 | 79 | v_plasterwall02, caulk, nodraw_decal |
| `doors/arched_brick_door.map` | 72/9/120 | -26 | - | 0/0/0 | 14 | v_plasterwall02, caulk, stalingradwinter_brick04 |
| `doors/arched_door1.map` | 80/16/132 | 0 | +y | 1/0/0 | 20 | v_dec_darkstain08, v_stonetrim04, nodraw_decal |
| `doors/arched_wood_door.map` | 58/28/129 | 1 | - | 0/0/0 | 7 | caulk, v_woodtrim01, v_dec_darkstain03 |
| `doors/arched_wood_doorframe.map` | 58/8/113 | 17 | - | 0/0/0 | 4 | v_woodtrim01, v_dec_darkstain03, caulk |
| `doors/concrete_door_steps1.map` | 64/20/124 | 0 | - | 0/0/0 | 5 | caulk, v_colum_stonewall01, v_stonetrim06 |
| `doors/concrete_door_steps1_clean.map` | 64/20/124 | 0 | - | 0/0/0 | 5 | caulk, v_woodtrim01, v_colum_stonewall02 |
| `doors/concrete_fancy1.map` | 10/72/120 | 0 | - | 0/0/0 | 24 | caulk, v_stonetrim04, nodraw_decal |
| `doors/door1.map` | 72/16/108 | 0 | +y | 1/0/0 | 8 | caulk, v_woodtrim01, nodraw_decal |
| `doors/door1_frame.map` | 72/16/108 | 0 | - | 0/0/0 | 10 | caulk, v_stonetrim01, v_woodtrim01 |
| `doors/doorframe_arch.map` | 58/8/113 | 17 | - | 0/0/0 | 4 | v_stonetrim04, v_dec_darkstain03, caulk |
| `doors/doorframe_archstepped1.map` | 58/28/129 | 1 | - | 0/0/0 | 7 | caulk, v_stonetrim04, v_dec_darkstain03 |
| `doors/doorframe_interior_red1.map` | 52/8/104 | 0 | - | 0/0/0 | 3 | caulk, v_woodtrim03 |
| `doors/fancybrick1.map` | 64/10/116 | -2 | - | 0/0/0 | 6 | caulk, v_woodtrim03, v_woodtrim02 |
| `doors/postoffice_door1.map` | 84/20/142 | 0 | - | 0/0/0 | 7 | v_plasterwall02, v_brick01, caulk |
| `doors/square_doorway.map` | 56/10/100 | -20 | - | 0/0/0 | 3 | v_stonetrim03, caulk |
| `doors/townhall_interior_door1.map` | 78/22/140 | 0 | - | 0/0/0 | 58 | caulk, v_dec_darkstain02, v_plasterwall02 |
| `doors/townhall_interior_door2.map` | 78/22/120 | 0 | - | 0/0/0 | 54 | caulk, v_dec_darkstain08, v_plasterwall02 |
| `doors/wooden_gate.map` | 6/100/134 | 0 | - | 0/0/0 | 7 | caulk, v_woodtrim03, v_wood_floor1 |
| `props/bldg_trim.map` | 16/16/256 | 0 | - | 0/0/0 | 32 | v_plasterwall02, caulk, v_stonetrim06 |
| `props/chicken_coop1.map` | 62/92/76 | 0 | - | 0/0/0 | 11 | v_woodtrim04, caulk, v_rusty_fence01 |
| `props/church_altar.map` | 226/265/253 | 0 | +x | 2/0/0 | 178 | caulk, v_plasterwall03, v_dec_darkstain08 |
| `props/church_arch.map` | 384/40/320 | -168 | - | 0/0/0 | 29 | caulk, v_wood_step_top01, v_dec_darkstain08 |
| `props/churchgate.map` | 192/83/186 | 0 | - | 0/0/0 | 30 | caulk, v_stonetrim03, v_colum_stonewall02; nested: gate2.map |
| `props/dragonstooth.map` | model-only | - | - | - | 0 | military_dragonstooth_wet |
| `props/fireplace1.map` | 76/32/128 | 1 | - | 0/0/0 | 30 | caulk, v_brick02, v_dec_darkstain01 |
| `props/fireplace2.map` | 76/32/128 | 0 | - | 0/0/0 | 16 | caulk, v_fireplace01, v_brick02 |
| `props/fireplace3.map` | 114/39/128 | 0 | - | 0/0/0 | 41 | caulk, v_stonewall11, v_stonetrim06 |
| `props/fireplace_corner1.map` | 66/66/128 | 0 | - | 0/0/0 | 17 | caulk, v_brick02, v_dec_darkstain01 |
| `props/gate1.map` | 104/6/72 | 0 | - | 0/0/0 | 10 | v_woodfloor01, caulk |
| `props/gate2.map` | 68/4/94 | 30 | - | 0/0/0 | 2 | nodraw, v_rusty_fence01, v_drain03 |
| `props/grave_stone.map` | 50/17/120 | 0 | - | 0/0/0 | 100 | caulk, nodraw_decal, v_floor_church01 |
| `props/grave_stone2.map` | 38/38/143 | 0 | - | 0/0/0 | 70 | caulk, v_floor_church01, v_fireplace01 |
| `props/grave_tomb.map` | 72/133/71 | -1 | - | 0/0/0 | 41 | caulk, v_floor_church01, v_plasterwall02 |
| `props/groundsteps1.map` | 80/104/56 | 0 | - | 0/0/0 | 18 | caulk, v_plasterwall02, v_dec_darkstain08 |
| `props/gutterdrain_left.map` | 8/6/267 | 1 | - | 0/0/0 | 0 | v_gutter01 |
| `props/gutterdrain_long_left.map` | 26/8/245 | -2 | - | 0/0/0 | 0 | v_drain02, v_dec_darkstain06, v_drain03 |
| `props/gutterdrain_long_right.map` | 26/8/245 | -2 | - | 0/0/0 | 0 | v_dec_darkstain06, v_drain02, v_drain03 |
| `props/gutterdrain_right.map` | 8/6/267 | 0.5 | - | 0/0/0 | 0 | v_gutter01 |
| `props/pallet.map` | 112/125/8 | 0 | - | 0/0/0 | 11 | v_woodfloor01, caulk |
| `props/pallet_d.map` | 108/102/8 | 0 | - | 0/0/0 | 21 | v_woodfloor01, v_dec_darkstain01, caulk |
| `props/postoffice_cubby.map` | 32/18/108 | 0 | +x | 0/1/0 | 15 | caulk, v_woodtrim03, nodraw_decal |
| `props/powerpole01.map` | 80/16/391 | 0 | - | 0/0/0 | 14 | v_drain02, v_dec_darkstain01, caulk |
| `props/rubble_brick01.map` | 89/61/8 | -4 | - | 0/0/0 | 9 | caulk, v_stonewall03 |
| `props/statue.map` | 256/256/192 | 0 | - | 0/0/0 | 15 | caulk, mtl_caen_wall_256tile_plasterbeige_01, mtl_caen_floor_int_church_01; character_german_wehrmact_josh |
| `props/steps1.map` | 96/48/32 | 0 | - | 0/0/0 | 12 | caulk, v_plasterwall, v_stonetrim06 |
| `props/temp_piano.map` | 112/36/64 | 0 | - | 0/0/0 | 2 | case256brown |
| `props/townhall_decoration.map` | 4/56/10 | 0 | +x | 0/3/0 | 3 | caulk, mtl_caen_window_frame_02 |
| `props/townhall_interior_column1.map` | 16/16/52 | 0 | - | 0/0/0 | 19 | caulk, v_dec_darkstain08, v_plasterwall02 |
| `props/townhall_interior_column2.map` | 48/12/160 | 0 | - | 0/0/0 | 17 | caulk, v_plasterwall02, v_dec_darkstain08 |
| `props/townhall_staircase.map` | 256/144/170 | 0 | - | 0/0/0 | 39 | caulk, mtl_caen_wall_plaster_03, mtl_caen_wall_256tile_stone_01 |
| `props/townhall_stairdecor1.map` | 6/6/30 | 0 | - | 0/0/0 | 13 | caulk, v_plasterwall02, v_dec_darkstain08 |
| `props/townhall_stairdecor2.map` | 6/6/30 | 0 | - | 0/0/0 | 10 | caulk, v_plasterwall02, v_dec_darkstain08 |
| `props/villers_dragonstooth.map` | 42/42/47 | 0 | - | 0/0/0 | 3 | caulk, v_plasterwall, nodraw_decal |
| `props/villers_wood_barb.map` | 41/38/46 | -4 | - | 0/0/0 | 0 | v_woodtrim02, v_dec_darkstain08 |
| `walls/carentan_arch.map` | 49/12/72 | 0 | - | 0/0/0 | 0 | v_plasterwall02 |
| `walls/carentan_arch2.map` | 58/12/72 | 0 | - | 0/0/0 | 0 | v_plasterwall02 |
| `walls/wallcolumn1.map` | 36/36/132 | -16 | - | 0/0/0 | 5 | caulk, v_stonetrim03, nodraw_decal |
| `walls/wallcolumn1_destroyed1.map` | 28/28/92 | -16 | - | 0/0/0 | 9 | caulk, v_corewalll01, nodraw_decal |
| `walls/wallcolumn1_destroyed2.map` | 36/28/163 | -64 | - | 0/0/0 | 16 | caulk, v_colum_stonewall02, nodraw_decal |
| `walls/wallcolumn1_tall.map` | 36/36/200 | -8 | - | 0/0/0 | 6 | caulk, v_stonetrim03, v_colum_stonewall02 |
| `walls/wallcolumn2.map` | 161/34/136 | -16 | - | 0/0/0 | 14 | caulk, mtl_caen_wall_ext_03, mtl_caen_wall_ext_plaster_03 |
| `walls/wallcolumn3.map` | 32/32/128 | 0 | - | 0/0/0 | 6 | v_colum_stonewall01, v_stonetrim02, caulk |
| `walls/wallcolumn4.map` | 32/32/128 | -16 | - | 0/0/0 | 2 | caulk, v_stonewall04, v_stonetrim03 |
| `walls/wallcolumn_small.map` | 20/20/70 | 0 | - | 0/0/0 | 4 | caulk, v_stonetrim03, nodraw_decal |
| `walls/wallsection1.map` | 152/24/112 | 0 | - | 0/0/0 | 5 | nodraw_decal, caulk, v_stonetrim03 |
| `walls/wallsection1_destroyed1.map` | 65/24/112 | 0 | - | 0/0/0 | 39 | v_corewalll01, nodraw_decal, caulk |
| `walls/wallsection1_destroyed2.map` | 148/16/163 | -56 | - | 0/0/0 | 45 | v_stonewall04, caulk, v_corewalll02 |
| `walls/wallsection1_short.map` | 100/24/112 | 0 | - | 0/0/0 | 5 | nodraw_decal, v_stonetrim03, caulk |
| `walls/wallsection1_tall.map` | 152/24/168 | -8 | - | 0/0/0 | 4 | caulk, nodraw_decal, v_stonewall04 |
| `walls/wallsection1_tall_destroyed1.map` | 81/24/168 | 0 | - | 0/0/0 | 26 | caulk, v_stonewall04, v_corewalll02 |
| `walls/wallsection1_tall_destroyed1_long.map` | 190/24/200 | -32 | - | 0/0/0 | 39 | caulk, v_stonewall04, v_corewalll02 |
| `walls/wallsection2.map` | 128/20/90 | 0 | - | 0/0/0 | 4 | nodraw_decal, v_ironfence01, v_stonetrim06 |
| `walls/wallsection2_c.map` | 108/20/102 | 0 | - | 0/0/0 | 4 | v_plasterwall02, v_fence_stonetop, v_stonetrim06 |
| `walls/wallsection3.map` | 192/24/160 | -56 | +y | 0/3/0 | 6 | caulk, v_windowframe01, mantle_over |
| `walls/wallsection4.map` | 208/24/112 | 0 | - | 0/0/0 | 5 | nodraw_decal, caulk, v_stonetrim03 |
| `walls/wallsection_long_destroyed.map` | 195/22/112 | 0 | - | 0/0/0 | 45 | v_corewalll02, v_stonewall04, caulk |
| `walls/wallsection_long_destroyed2.map` | 205/24/112 | 0 | - | 0/0/0 | 26 | v_corewalll02, v_stonewall04, caulk |
| `walls/wallsection_long_destroyed3.map` | 187/16/80 | 0 | - | 0/0/0 | 43 | v_corewalll02, caulk, v_stonewall04 |
| `walls/wallsection_long_destroyed_a.map` | 124/24/112 | 0 | - | 0/0/0 | 31 | v_stonewall04, v_corewalll02, caulk |
| `walls/wallsection_long_destroyed_b.map` | 103/16/49 | 0 | - | 0/0/0 | 16 | v_corewalll02, v_stonewall04, caulk |
| `walls/wallsection_lowcover1.map` | 20/144/40 | 0 | - | 0/0/0 | 4 | caulk, nodraw_decal, v_dec_stonewall10 |
| `walls/wallsection_lowcover1_long.map` | 20/192/40 | 0 | - | 0/0/0 | 4 | caulk, nodraw_decal, v_dec_stonewall10 |
| `walls/wallsection_lowcover1_post.map` | 28/28/48 | 0 | - | 0/0/0 | 4 | v_stonetrim06, nodraw_decal, v_dec_stonewall10 |
| `walls/wallsection_lowcover1_short.map` | 20/80/40 | 0 | - | 0/0/0 | 4 | caulk, v_stonewall02, nodraw_decal |
| `windows/arch_block_closed.map` | 66/10/92 | 0 | +y | 0/1/0 | 41 | v_plasterwall02, nodraw_decal, v_dec_darkstain08 |
| `windows/arch_block_nodetail.map` | 66/10/92 | 0 | +y | 0/1/0 | 49 | nodraw_decal, v_dec_darkstain08, v_plasterwall02 |
| `windows/arch_block_open.map` | 66/10/92 | 0 | - | 0/0/0 | 40 | v_plasterwall02, nodraw_decal, v_dec_darkstain08 |
| `windows/arch_block_shutter.map` | 66/10/92 | 0 | +y | 0/1/0 | 41 | mtl_caen_wall_plaster_03, nodraw_decal, mtl_caen_decal_stain_plasterwall_02 |
| `windows/arch_brick_open.map` | 72/10/98 | -4 | - | 0/0/0 | 15 | caulk, v_plasterwall02, stalingradwinter_brick04 |
| `windows/arched_closed1.map` | 80/14/112 | 0 | +y | 0/2/0 | 22 | v_dec_darkstain08, v_stonetrim04, caulk |
| `windows/arched_wood.map` | 44/11/85 | 0 | - | 0/0/0 | 6 | v_woodtrim01, caulk, v_dec_darkstain03 |
| `windows/carentan_dorm01.map` | 71/50/78 | -8 | - | 0/0/0 | 16 | caulk, v_woodtrim03, v_woodtrim01 |
| `windows/church_stainedglass.map` | 4/56/124 | 0 | +x | 0/1/0 | 1 | v_window09_unlit, caulk, v_window09 |
| `windows/church_window1.map` | 12/72/142 | 0 | - | 0/0/0 | 2 | v_stonetrim08, v_dec_darkstain08, caulk |
| `windows/closed1.map` | 80/14/112 | 0 | - | 0/0/0 | 28 | caulk, v_stonetrim04, nodraw_decal |
| `windows/concrete_frame1.map` | 10/52/76 | 0 | - | 0/0/0 | 4 | caulk, v_colum_stonewall01 |
| `windows/concrete_frame1_clean.map` | 10/52/76 | 0 | - | 0/0/0 | 4 | caulk, v_woodtrim01 |
| `windows/concrete_frame1_small.map` | 10/52/60 | 0 | - | 0/0/0 | 4 | caulk, v_colum_stonewall01 |
| `windows/concrete_frame1_small_clean.map` | 10/52/60 | 0 | - | 0/0/0 | 4 | caulk, v_woodtrim01 |
| `windows/fancy_concrete1.map` | 10/56/84 | 0 | - | 0/0/0 | 20 | caulk, v_stonetrim04, nodraw_decal |
| `windows/fancy_concrete1_wide.map` | 10/72/84 | 0 | - | 0/0/0 | 20 | caulk, v_stonetrim04, nodraw_decal |
| `windows/fancy_concrete2_wide.map` | 10/72/100 | -16 | - | 0/0/0 | 20 | caulk, v_stonetrim06, nodraw_decal |
| `windows/loft1.map` | 60/95/99 | 10 | -y | 0/2/0 | 11 | caulk, v_stonetrim03, nodraw_decal |
| `windows/loft2.map` | 56/104/84 | 0 | - | 0/1/0 | 12 | caulk, nodraw_decal, v_stonewall04 |
| `windows/loft3.map` | 60/95/99 | 10 | -y | 0/2/0 | 11 | caulk, v_stonetrim03, v_roof02 |
| `windows/loft4.map` | 56/104/84 | 0 | - | 0/1/0 | 10 | caulk, v_plasterwall02, nodraw_decal |
| `windows/postoffice_window1.map` | 84/20/126 | 0 | - | 0/0/0 | 12 | v_plasterwall02, caulk, v_woodtrim01 |
| `windows/postoffice_window1_open.map` | 84/20/126 | 0 | - | 0/0/0 | 7 | v_plasterwall02, v_brick01, caulk |
| `windows/postoffice_window1_wide.map` | 92/20/126 | 0 | - | 0/0/0 | 21 | v_woodtrim01, v_plasterwall02, caulk |
| `windows/postoffice_window1_wide_boarded.map` | 92/20/126 | 0 | +y | 0/1/0 | 8 | v_plasterwall02, caulk, v_brick01 |
| `windows/shutter_blue1.map` | 22/2/68 | 0 | +x | 0/1/0 | 1 | v_window04 |
| `windows/shutter_blue2.map` | 26/2/90 | 0 | +x | 0/2/0 | 2 | v_window04, caulk |
| `windows/shutter_brown1.map` | 17/2/65 | 4 | +x | 0/1/0 | 1 | v_shutter_01 |
| `windows/shutter_grey1.map` | 24/4/72 | 0 | +x | 0/5/0 | 5 | mtl_caen_window_shutter_03, caulk |
| `windows/shutter_wood1.map` | 22/2/60 | 0 | +x | 0/1/0 | 1 | v_shutter_01 |
| `windows/shutter_wood1_large.map` | 2/26/74 | 0 | +x | 0/1/0 | 1 | v_shutter_01 |
| `windows/shutter_wood1_small.map` | 23/2/54 | 0 | +x | 0/1/0 | 1 | v_shutter_01 |
| `windows/shutter_wood1_small_nondetail.map` | 23/2/54 | 0 | +x | 0/1/0 | 1 | mtl_caen_window_shutter_01 |
| `windows/shutter_wood2.map` | 20/2/74 | 0 | +x | 0/1/0 | 1 | v_shutter_01 |
| `windows/shutter_wood_arched1.map` | 18/2/76 | 0 | +x | 0/1/0 | 1 | v_shutter_01 |
| `windows/shutter_wood_arched2.map` | 18/2/76 | 0 | +x | 0/1/0 | 1 | mtl_caen_window_shutter_03 |
| `windows/shutter_wood_arched3.map` | 18/3/76 | 0 | +x | 0/4/0 | 4 | mtl_caen_window_shutter_03, caulk |
| `windows/shutter_wood_arched_l.map` | 18/3/76 | 0 | +x | 0/4/0 | 4 | mtl_caen_window_shutter_03, caulk |
| `windows/shutter_wood_arched_r.map` | 18/3/76 | 0 | +x | 0/4/0 | 4 | mtl_caen_window_shutter_03, caulk |
| `windows/square_window_open.map` | 56/10/80 | 0 | - | 0/0/0 | 6 | caulk, v_stonetrim03 |
| `windows/square_window_wood.map` | 56/10/80 | 0 | - | 0/0/0 | 4 | v_woodtrim01, caulk, v_stonetrim03 |
| `windows/townhall_window1.map` | 56/8/100 | 0 | +y | 0/1/0 | 4 | caulk, v_plasterwall02, v_window03 |
| `windows/townhall_window1_frame.map` | 56/8/100 | 0 | - | 0/0/0 | 3 | v_plasterwall02, caulk |
| `windows/townhall_window1_small.map` | 56/8/80 | 0 | +y | 0/1/0 | 4 | caulk, v_plasterwall02, v_window06 |
| `windows/townhall_window2.map` | 48/4/96 | 0 | - | 0/0/0 | 6 | caulk, v_woodtrim02 |
| `windows/underhang1.map` | 64/4/27 | -27 | - | 0/0/0 | 11 | caulk, v_plasterwall |
| `windows/villers_window_01.map` | 48/10/80 | 0 | - | 0/0/0 | 18 | caulk, v_woodtrim01, nodraw_decal |
| `windows/villers_window_01_d.map` | 48/10/80 | 0 | - | 0/0/0 | 19 | caulk, v_woodtrim01, nodraw_decal |
| `windows/villers_window_01_open.map` | 48/10/80 | 0 | - | 0/0/0 | 11 | nodraw_decal, v_stonetrim04, v_dec_darkstain02 |
| `windows/villers_window_02.map` | 64/14/86 | 0 | - | 0/0/0 | 15 | v_woodtrim01, caulk, v_plasterwall |
| `windows/villers_window_03.map` | 64/14/86 | 0 | - | 0/0/0 | 5 | v_plasterwall, caulk, v_stonetrim01 |
| `windows/villers_window_small_01.map` | 48/10/58 | 0 | - | 0/0/0 | 19 | v_woodtrim01, nodraw_decal, v_stonetrim04 |
| `windows/window1.map` | 48/10/82 | 0 | +x | 0/1/0 | 9 | v_plasterwall02, caulk, v_window02 |
| `windows/window1_frame.map` | 48/10/82 | 0 | - | 0/0/0 | 4 | v_plasterwall02, caulk |
| `windows/window1_structural.map` | 64/16/86 | 0 | +y | 0/2/0 | 16 | v_woodtrim01, caulk, v_plasterwall |
| `windows/window2.map` | 48/10/80 | 0 | - | 0/0/0 | 21 | v_woodtrim01, nodraw_decal, v_stonetrim04 |
| `windows/window2_frame.map` | 48/10/80 | 0 | - | 0/0/0 | 7 | v_stonetrim04, nodraw_decal, v_dec_darkstain03 |
| `windows/window3.map` | 44/11/80 | 0 | - | 0/0/0 | 7 | v_stonetrim04, caulk, nodraw_decal |
| `windows/window4.map` | 44/11/85 | 0 | - | 0/0/0 | 6 | v_stonetrim04, caulk, v_dec_darkstain03 |
| `windows/window5.map` | 64/14/104 | 0 | +y | 0/1/0 | 9 | caulk, v_woodtrim01, nodraw_decal |
| `windows/window5_frame.map` | 64/14/104 | 0 | - | 0/0/0 | 8 | v_woodtrim01, nodraw_decal, v_dec_darkstain03 |
| `windows/window5_grimy.map` | 64/14/104 | 0 | +y | 0/1/0 | 12 | nodraw_decal, v_dec_darkstain01, caulk |
| `windows/window6.map` | 48/14/88 | 0 | +x | 0/1/0 | 7 | caulk, v_woodtrim01, clip |
| `windows/window6_frame.map` | 48/14/88 | 0 | - | 0/0/0 | 4 | v_woodtrim01, caulk |
| `windows/window7.map` | 48/10/86 | 0 | - | 0/0/0 | 6 | caulk, v_woodtrim02, v_plasterwall |
| `windows/window8.map` | 64/14/86 | 0 | - | 0/0/0 | 15 | v_woodtrim03, caulk, v_plasterwall |
| `windows/window8_white.map` | 64/14/86 | 0 | - | 0/0/0 | 15 | v_woodtrim01, caulk, v_plasterwall |
| `windows/window9.map` | 48/10/88 | 0 | +x | 0/1/0 | 7 | caulk, mtl_caen_trim_ext_plaster_01, mtl_white_window_a |
| `windows/window_small1.map` | 48/10/58 | 0 | - | 0/0/0 | 19 | v_woodtrim01, nodraw_decal, v_stonetrim04 |
| `windows/window_small1_nondetail.map` | 48/10/58 | 0 | +x | 0/1/0 | 5 | mtl_caen_trim_ext_plaster_01, caulk, mtl_caen_window_white_01 |
| `windows/window_small2.map` | 40/8/24 | 0 | - | 0/0/0 | 5 | caulk, v_woodtrim03 |

## root — 

| prefab | size x/y/z | floor | front | doors/win/portal | brushes | key materials / models |
|---|---|---|---|---|---|---|
| `piano.map` | 0/0/0 | 0 | - | 0/0/0 | 7 | trigger; furniture_piano_d |

## rhine — US / Germany (Rhine)

| prefab | size x/y/z | floor | front | doors/win/portal | brushes | key materials / models |
|---|---|---|---|---|---|---|
| `misc/door02.map` | 48/14/102 | 0 | - | 0/0/0 | 0 | v_door03, v_dec_darkstain03 |
| `misc/grave_c.map` | 50/17/120 | 0 | - | 0/0/0 | 94 | v_plasterwall02, caulk, nodraw_decal |

## toujane — British / Tunisia (Toujane)

| prefab | size x/y/z | floor | front | doors/win/portal | brushes | key materials / models |
|---|---|---|---|---|---|---|
| `crates/cratepile_large3.map` | model-only | - | - | - | 0 | prop_crate_dak6, prop_crate_dak3, prop_crate_dak1, prop_crate_dak4, prop_crate_dak5, prop_crate_dak2, prop_crate_dak8 |
| `crates/cratepile_med2.map` | model-only | - | - | - | 0 | prop_crate_dak7, prop_crate_dak9, prop_crate_dak4, prop_crate_dak8, prop_crate_dak6, prop_crate_dak5 |
| `crates/cratepile_med5.map` | model-only | - | - | - | 0 | prop_crate_dak6, prop_crate_dak5, prop_crate_dak9, prop_crate_dak8, prop_crate_dak7 |
| `hanging_rug1.map` | 58/18/53 | -38 | - | 0/0/0 | 0 | toujane_decal_rug1 |
| `tj_door01.map` | 48/8/104 | 0 | +x | 1/0/0 | 1 | caulk, toujane_door_trim1, toujane_dirt_trim_dark; prop_doorknob1 |
| `tj_merchant2.map` | model-only | - | - | - | 0 | prop_market_stands1 |
| `tj_merchant3.map` | model-only | - | - | - | 0 | prop_market_stands5 |

## traverse — AI traverse helpers

| prefab | size x/y/z | floor | front | doors/win/portal | brushes | key materials / models |
|---|---|---|---|---|---|---|
| `crouch_jump_down_40.map` | 8/72/40 | 12 | - | 0/0/0 | 1 | traverse |
| `jump_down_56.map` | 32/72/52 | 0 | - | 0/0/0 | 1 | traverse |
| `jump_down_96.map` | 32/72/96 | -44.2 | - | 0/0/0 | 1 | traverse |
| `step_up.map` | 12/72/16 | 0 | - | 0/0/0 | 2 | traverse, clip_ai |
| `trench_jumpout.map` | 8/72/52 | 0 | - | 0/0/0 | 1 | traverse |
| `wall_hop.map` | 12/72/40 | 0 | - | 0/0/0 | 1 | traverse |
| `window_2.map` | 8/72/72 | 4 | - | 0/0/0 | 3 | traverse |
| `window_down.map` | 8/72/72 | 4 | - | 0/0/0 | 3 | traverse |
