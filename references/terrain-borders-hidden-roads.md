# Terrain, map borders and hidden approach roads

These rules come from playtests where the player saw the sky box at the end of a spawn road, saw enemies
appear out of nothing, or walked off the map. Follow all of them.

## 1. Three nested zones

```
+---------------------------- SKY BOX (sky brushes, SX0..SX1, SY0..SY1) ---------------------------+
|  OUTER RING: scenery only. High snow ridges (600-750u), cliffs, dense trees. No AI nodes.        |
|   +------------------- PLAYABLE POLYGON (player clip wall) -------------------+                  |
|   |  gameplay: zones A/B/C, building, river, bridges, start                    |                 |
|   +----------------------------------------------------------------------------+                 |
|  SPAWN VALLEYS cut through the outer ring; spawners sit deep in them, out of sight             |
+---------------------------------------------------------------------------------------------------+
```

1. **Sky box.** A closed hull of `sky_*` brushes plus a caulk floor. Everything visible must be inside it, including planes and vehicles at their spawn points.
2. **Outer ring.** Terrain rises steeply from the playable edge to ridges far higher than the eye: 600–750 units on a map whose gameplay floor is around 0–250. These ridges hide the sky-box walls. Plant trees on the ridge crests so the silhouette does not look flat.
3. **Playable polygon.** A `clip_player` wall following a polygon (we used `SINIR_PX`, a list of sketch pixels converted with `W(px,py)`). It sits a little inside the ring so the player can never climb the ridge. Back it up with a GSC border watcher that pushes the player back if they slip past. That catches holes the clip misses on steep triangles.

## 2. Spawn / approach roads must never show their end

**Symptom:** standing at the start or in the defended building, the player looks down a road valley and sees flat sky where the valley meets the sky box. It looks like the end of the world.

**Cause:** the valley was carved straight to within ~250–550 units of the sky-box wall. Terrain only rises *beside* a carved road, so the floor of the cut stays low right up to the wall.

**Rules:**
- **Bend every road.** Past the last point the player can see, a road must turn 60–120° and run behind a hill. Then extend it 600–1500 more units before it ends against a hillside.
- **End against a hill, not the sky.** The last road point must be surrounded on the far side by terrain at least 500 units above the road floor, within about 600 units.
- **Keep spawn points in the bend.** Spawners and vehicle start nodes go just past the bend, where no line of sight from playable space reaches them. Riders spawned there (with `stalingradspawn`) can't be seen.
- **Leave room for the extension.** Make the sky box big enough: at least 1500–2000 units between any road end and its wall. Enlarging `SX0/SX1/SY0/SY1` costs only brushes and trees. Watch the compile log for `MAX_` errors.
- **Extend; never move gameplay points.** Add an extension polyline (e.g. `GUNEY_UZANTI_PX`, `BATI_UZANTI_PX`, `DOGU_UZANTI_PX`) appended to the valley list and the road-surface list. Never move existing road points: vehicle node chains, spawner routes and flee routes index into them.
- **Pin fixed-position entities.** Anything whose position was computed from the sky-box bounds (for example a hidden `misc_turret` at `SX0+300`) moves when the bounds change. Pin it to absolute coordinates first.
- **Measure before compiling.** Sample the generator's height function along sight lines from every viewpoint (start, defended building eye ~z290, objective areas), through each road end and 1500 units beyond. Every line must reach terrain above the eye height before reaching the sky box.
- **Verify in game.** Run a screenshot tour (a `kr_tur`-style cvar mode) that parks the camera at the start and above the building, looking down each road. Look at the images.
- **Anchor the node grid.** If path nodes come from a grid starting at the sky-box corner
  (`range(SX0+96, ...)`), enlarging the sky box SHIFTS every grid node. On our map that turned the
  B hilltop into an island (12 unreachable nodes, 1 in solid). Anchor the grid to a fixed origin
  (`gx0 = X_FIXED - step * ((X_FIXED - (SX0+96)) // step)`) so the nodes stay where they were.
- **New ground gets no AI nodes,** so no stray nodes in scenery. If the bounds change shifts a node grid, re-run the reachability audit. New isolated nodes appear when the grid origin moves; drop them.

## 3. Valleys and hills that hide AI

- Carve a valley floor 140–160 units wide with banks rising to the ring height over 300–500 units. That avoids cliffs AI can't path on. The valley must be a smooth corridor down which vehicles can drive (slope < ~20°).
- Enemy foot waves follow waypoint lists along the road (`giris_yol`). Their flee route is the same list reversed back to their own spawn. Delete fleeing soldiers only at the hidden spawn point.
- Valleys that cross a river need bridges with their own nodes; route intermediate goals over the bridge.
- High water (`water_*` material) in a ravine stops the player from jumping in. Make the ravine ends bend behind hills too, or the sky shows along the river.

## 4. Terrain construction tips

- Build the terrain as a triangle mesh from a height function: base noise, plus ring ramp, minus carved valleys, plus small mounds for cover. Keep the function in the generator so entities can query the exact surface z.
- Put every node, spawner, prop and tree on the triangle surface (barycentric z), not at the grid vertex height. On slopes, vertex height floats objects or buries them.
- Trees: dense on ridges, sparse in play areas. Never on roads, and never within a model radius of nodes.
- Check bird's-eye screenshots for floating rocks or trees and for gaps between terrain and building foundations.

## 5. Checklist before handing to the user

- [ ] From the start: every direction ends in terrain or trees, no flat sky box walls.
- [ ] From each defended window: every approach road bends out of sight.
- [ ] Spawn points can't be seen from anywhere the player can stand.
- [ ] Player clip polygon closed; border watcher running.
- [ ] Reachability audit 0 unreachable after any terrain or bounds change.
