# Reverse engineering stock CoD2 maps (`scripts/bsp_decompile.py`)

Use this when the user says **"make it like <stock map>"** or does not like a layout and points to
a stock level.

**Always ask first:**
- which map;
- which part: the whole layout as a blueprint, specific buildings or areas, or only the mood
  (props, lighting, fog);
- whether the result may copy the stock geometry 1:1 or should only be used as reference.

Then proceed.

## 1. What is in a compiled `.d3dbsp` (IBSP version 4, measured)

The file has a 39-entry lump table at offset 8: `int size, int offset` per lump.

| lump | record | content |
|---|---|---|
| 0 | 72 B: `char name[64]; u32 surfaceFlags; u32 contentFlags` | materials (contents: 0x1 solid, 0x08000000 detail, 0x800 sky = non-solid) |
| 4 | 16 B: `float normal[3], dist` | planes (outward normal, inside: n·x <= d) |
| 5 | 8 B: `u32 planeOrDist; u32 material` | brush sides: **the first 6 sides of every brush are axial distances** (float) in order -x,+x,-y,+y,-z,+z; the rest index lump 4 |
| 6 | 4 B: `u16 numSides; u16 material` | brushes (sum of numSides = side count, verified) |
| 7 | 16 B: `u16 material, u16 lightmap, u32 firstVertex, u16 vertexCount, u16 indexCount, u32 firstIndex` | triangle soups (draw surfaces) |
| 8 | 68 B: `xyz[3], normal[3], rgba, st[2], lmst[2], tangent[3], binormal[3]` | draw vertices |
| 9 | u16 | draw indices (relative to firstVertex) |
| 35 | 48 B: `mins[3], maxs[3], u32 firstSoup, numSoups, firstCollTri, numCollTri, firstBrush, numBrushes` | models: 0 is the world; `*N` are brush models in **local** coordinates (add the entity origin). Triggers often have 0 brushes and only bounds |
| 37 | text | entity string: every entity with all keys, including `misc_model`, `light`, AI nodes, spawners (`export`, `script_*`), vehicles and triggers |
| 38 | binary | AI path links (see `ai-paths.md`) |

## 2. What comes back

`python bsp_decompile.py <map>.d3dbsp <out>.map` writes:
- **Entities:** all of them (props, lights, nodes, spawners, vehicles, triggers) with their keys.
- **World brushes:** rebuilt from planes. Duplicate bevel planes are removed, because cod2map
  rejects "duplicate plane".
- **Brush models:** moved to world space, each with an origin brush (pivot).
- **Triggers without brushes:** rebuilt as boxes from their bounds.
- **Face materials:** a compiled brush keeps only its *contents* material on every side. Each side
  therefore gets the material of the draw triangle lying on its plane, or `caulk` if nothing is
  drawn there.
- **Detail flag:** set from the material contents (0x08000000).
- **Terrain and patches:** non-brush draw triangles become 2x2 mesh quads (triangle pairs that
  share an edge) plus thin prism brushes for unpaired triangles.
- **Texture repeat size:** estimated per material from the soups (world units per st unit).
- **Sky hull:** sky brushes are non-solid and absent from the brush lump, so a 6-brush hull with
  the map's own sky material is added.

Not recoverable:
- exact texture offsets and rotation;
- patch control grids (they come back as triangles);
- compile-only helpers.

## 3. Two ways to use it

### a) Blueprint (whole map) — reference, not a recompile

`bsp_decompile.py decoytrenches.d3dbsp out.map` (4 s; 2 586 world brushes, 2 750 entities,
18.5 k terrain pieces). Use it to:
- read the layout, building and trench positions, cover placement and node density;
- read spawner groups (`script_killspawner`, `export`), trigger chains and vehicle paths;
- open it in Radiant to study, or load it with `map_inspect.parse_map` to copy measured numbers
  into our generator.

**Do not recompile a whole stock map.** cod2map 1.1 dies with `SANITY CHECK FAILURE ...
tris_mergeconcave.cpp:560 (subArea[0] >= 0 || subArea[1] >= 0)` on the full decoytrenches
reconstruction (measured).
- Any half of the world brushes compiles on its own; only the full set crashes.
- Structural terrain prisms push the 32-bit compiler to ~2 GB and it exits silently.

The crash dialog stays on screen until closed. Always compile reconstructions with the watcher
in section 5, which closes it automatically.

### b) Region prefab — the production path (verified)

```
python bsp_decompile.py decoytrenches.d3dbsp map_source/prefabs/rev/decoy_bunker.map \
       --region 6300 -13600 7500 -12400 --prefab
```

This keeps only the geometry and visual entities (`misc_model`, `light`, `misc_prefab`) whose
centre lies in the rectangle. It moves the origin to the region centre and to the low ground
level (10th percentile of the up-facing triangles), and writes no sky hull.

Then place it like any stock prefab:

```
{ "classname" "misc_prefab" "model" "prefabs/rev/decoy_bunker.map" "origin" "x y z" "angles" "0 yaw 0" }
```

Measured result:
- 334 brushes, 1 193 terrain quads, 166 models and 22 lights;
- placed twice (yaw 0 and 90) in a fresh test map;
- compiled and lit with no errors; the screenshot tour shows the trench, bunker, sandbags, wire,
  flak and crates intact.

Keep regions about ≤ 1 500 x 1 500 so that each prefab stays well inside the compiler limits.

## 4. Workflow when the user wants a stock look

1. Ask which map and which parts (section 0). Extract the stock `.d3dbsp` from `main/iw_*.iwd`
   into the scratch folder; never modify the iwds.
2. Decompile the blueprint and run `map_inspect.py` on it to get materials, prop lists,
   densities and node spacing.
3. **Rebuild the layout in our generator:** roads, terrain and borders from our code, with the
   stock numbers.
4. Cut the signature pieces (a bunker, a market street, a gate) with `--region --prefab` and place
   them with `misc_prefab`.
5. Copy the mood from the stock `.gsc` and `_fx.gsc`: fog, `setCullDist`, sun from worldspawn,
   ambience from `_amb.gsc`, backdrops.
6. Normal gates: compile, path audit, screenshot tour, flow test. Tell the user plainly which
   parts are copied stock geometry.

## 5. Crash-safe compile (closes the SANITY dialog itself)

```powershell
$p = Start-Process "$r\bin\cod2map.exe" -ArgumentList "-platform pc `"$r\main\maps\$M`"" `
     -WorkingDirectory "$r\bin" -RedirectStandardOutput "$env:TEMP\$M.log" -PassThru -WindowStyle Hidden
for ($i = 0; $i -lt 1800; $i++) { $p.Refresh(); if ($p.HasExited) { break }
  if ($p.MainWindowTitle -match 'SANITY|ERROR') { 'CRASH'; $p | Stop-Process -Force; break }
  Start-Sleep -Milliseconds 400 }
```

Also watch `PeakWorkingSet64`. At about 2 GB, cod2map exits without writing a log line.
