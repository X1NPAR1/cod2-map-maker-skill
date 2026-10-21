---
name: cod2-map-maker
description: Build, script, compile and debug Call of Duty 2 (2005, IW engine) single-player maps end to end — generated .map geometry (iwmap 4), AI path networks, entities, GSC level scripts, sound aliases, localized strings, vehicles, mortar crews, friendly squads, objectives, intro/outro and mission chaining. Use whenever the user wants to create or fix a CoD2 map, GSC script, cod2map/cod2rad compile, connectpaths problem, or in-game bug in a CoD2 mod tools install.
---

# CoD2 Map Maker

This skill turns Claude into a working Call of Duty 2 single-player level designer and scripter.
Everything here was **measured in a real CoD2 1.3 + Mod Tools install** while shipping several
complete campaign maps (a village assault, a three-objective outpost assault with a 50-enemy
defense wave, vehicles, mortar crews, door breaches, a scoped-rifle swap station, and a final
cutscene that chains into the credits). Stock-script line references point at the files shipped
inside `main/iw_07.iwd` (`maps/_utility.gsc`, `_spawner.gsc`, `_vehicle.gsc`, ...).

> Golden rule: **the engine and tools lie by omission.** A compile that "succeeds" may have
> dropped half your paths; a script that loads may never fire; a sound alias that exists may be
> restricted to another level. Every phase ends with a *measurement*, never an assumption.

Detailed references (read the one you need, do not guess):

| File | When |
|---|---|
| `references/planning-interview.md` | Plan mode: the questions to ask before coding, plan template |
| `references/visual-qa.md` | Screenshot tours, view list, what to check in each image |
| `references/install-layout.md` | Finding tools, folders, iwd contents, what goes where |
| `references/map-format.md` | Writing `.map` (iwmap 4) brushes, terrain, entities, materials |
| `references/compile-pipeline.md` | cod2map / cod2rad / connectpaths, logs, success criteria |
| `references/terrain-borders-hidden-roads.md` | Sky box, outer ridges, player clip, approach roads that bend out of sight |
| `references/ai-paths.md` | Path nodes, lump 38 decoding, reachability audits, stairs, clips |
| `references/gsc-scripting.md` | Level skeleton, helpers, friendly chains, spawners, flags |
| `references/vehicles-mortars.md` | Trucks, halftracks, riders, godmode, mortar teams, planes |
| `references/assets-sound-strings.md` | Sound alias loadspec trap, .str / _platform.str, models, FX |
| `references/pitfalls.md` | Every bug we hit, its symptom, cause and fix |
| `references/testing.md` | Load checks, automated test modes, console.log mining |

---

## 1. Mental model of a CoD2 SP level

A playable level is **eight files**, all with the same base name `<map>`:

```
map_source/<map>.map                 # Radiant source (generated or hand-made)
main/maps/<map>.d3dbsp               # compiled BSP + light + AI paths (lump 38)
main/maps/<map>.gsc                  # level script (entry: main())
main/maps/<map>_fx.gsc               # loadfx() table, ambient FX
main/maps/<map>_anim.gsc             # level.scr_anim / level.scrsound dialogue table
main/maps/<map>.csv                  # loadscreen + victory/defeat backdrops
main/sun/<map>.sun                   # sun / fog / lighting tweaks
main/soundaliases/<map>.csv          # every alias the level uses, loadspec = <map>
main/localizedstrings/<map>.str      # objective/intro text  (&"MAP_KEY")
main/localizedstrings/<map>_platform.str  # strings that contain key bindings [&&1]
```

Missing `.csv`, `.sun`, `.str` or alias file does not always error — it silently produces a
black loadscreen, wrong light, `MAP_KEY` raw text or a fatal `unknown sound alias` mid-mission.

## 2. Workflow (follow in order, measure at every gate)

0. **Plan mode first, for every new map or big change.** Enter plan mode and interview the user
   in depth with batches of concrete multiple-choice questions until identity, layout, border and
   hidden roads, player, friendlies, enemies and waves, vehicles, events, audio and delivery are
   all specified (`references/planning-interview.md`). Write the plan with evidence gates, get
   approval, then code. Small bug-fix rounds from a playtest list do not need a new interview,
   but ask whenever a request is ambiguous.
1. **Read the brief critically.** Briefs routinely contain invented API (`spawnVehicle()`,
   `setObjectiveText()`, etc.). Map every requested behaviour to a *real* stock function by
   grepping the stock scripts or a stock level that does the same thing. If none exists, write it.
2. **Plan the layout** in world units: player 72u tall, doors 72-96u, steps <= 16u (AI need
   ramps). Plan the sky box, the outer ridge ring, the clip polygon and approach roads that bend
   out of sight (`terrain-borders-hidden-roads.md`) before any geometry.
3. **Generate geometry** with a Python generator (`gen_<map>.py`) plus `ent_<map>.py`.
   Never hand-edit a generated `.map`. Look at every texture you use (`scripts/iwi_preview.py`).
4. **Compile BSP + light.** Gate: `LEAK` 0, no `MAX_`, fresh `.d3dbsp`.
5. **Connect paths.** Gate: paths saved, 0 `in solid`, 0 `no connections`, reachability BFS 0.
6. **Script.** Gate: load test shows 0 script errors, 0 `unknown sound alias`.
7. **Visual QA: mandatory.** Run the screenshot tour (`references/visual-qa.md`,
   `scripts/screenshot_tour.ps1`):
   - bird's-eye of the whole map and each zone;
   - the start in all directions;
   - every approach road from every defended spot;
   - every room, stair and door in its closed and open state;
   - props and border edges.
   Read every image yourself, fix what is wrong, recompile and re-shoot until nothing visible is
   wrong. Send the key images to the user.
8. **Optional automated runtime test** (test-mode cvars that play the mission and log via `setcvar`).
9. **Hand to the user** fullscreen, without developer mode, and *ask them to play and test it*.
   Their feedback list is the next iteration: fix every item surgically, re-run the gates and the
   relevant screenshot views, then hand back again.

## 3. Hard rules (each one cost a debugging session)

### Geometry
- `.map` header is `iwmap 4`. Each brush is ≥4 planes `( x y z ) ( x y z ) ( x y z ) material
  sx sy rot ox oy 0 0 lightmap_gray 16384 16384 0 0 0 0`. Plane points are clockwise seen from
  outside. Write CRLF.
- A helper `box(x0,y0,z0,x1,y1,z1,top,side,bottom)` that takes "top" as **only the +z face**
  will put the wrong texture on big vertical faces (doors!). Use a per-face material dict.
- Detail/props: `func_group` or `contents detail` so they don't split BSP.
- Movable brushes: `script_brushmodel` + an `origin`-textured brush; its centre becomes the
  entity origin and **rotation pivot** (door hinge). `rotateyaw` around it.
- A `script_brushmodel` that calls `connectpaths()`/`disconnectpaths()` MUST have
  `spawnflags 1` (DYNAMICPATH). Without it the game stops with a fatal script runtime error the
  moment the door opens — a load test never sees it; only running the open code path does.
- Fitting a texture to a face: repeat size = face size, offset = **+min** coordinate
  horizontally (`u = (coord - offset) / size`) and **-min vertically** (v runs downward). A wrong
  sign leaves a visible wrap seam (measured on a 92x124 door leaf).
- Floating objects are the #1 visual complaint. Compute model z from the actual surface
  (terrain triangle, crate top = floor + 26 for `prop_crate*`), never from a constant.
- Posts, rails and planks must reach the surface they stand on; a ramp lowers the floor.
- Overlapping coplanar faces (stair tops vs floor) z-fight — stop one 1u short or delete it.
- The sky is a closed box; objects outside it (planes!) are not drawn. Spawn flybys inside.
- Leaks: every map must be sealed by `sky`/caulk hull; check `<map>.lin` after a LEAK.

### AI navigation
- `clip_player` and `clip` brushes present at connectpaths time **cut path links** for AI.
  Build player-only blockers +2000u high and `moveZ(-2000, 0.05)` them into place at runtime.
- AI make **no uphill link** across 16–17u steps. Every stair needs an invisible solid
  (caulk) ramp under it; `clip` does not count as floor for AI.
- Node z must sit on the real floor triangle (±2u). Nodes floating 8u above a slope freeze AI.
- Isolated islands are silent. Decode lump 38 and BFS from the player start (script in
  `ai-paths.md`). Target: 0 unreachable nodes.
- Closed volumes (rooms with no gap at connectpaths time) produce islands → keep doors open
  (or raised) during connectpaths.

### Scripting
- `level.totalfriends = 0; level.maxfriendlies = N;` **before** `maps\_load::main()`.
- The player must always be on a friendly chain if friendlies/friendly_wave are used.
- `waittill_aigroupcleared` counts spawners: delete spawners after spawning.
- `getent()` asserts on duplicate targetnames → `getentarray(name,"targetname")[0]`.
- GSC vectors have 1 or 3 components — never 2 or 4. Negative literal: `(0, 0 - 5, 0)` if parser complains.
- Write GSC as plain ASCII/latin-1. Non-latin characters (ş, ğ, ı) break the parser; write via
  temp file + atomic replace (a failed encode once truncated a 3000-line script to 0 bytes).
- `abs`, `random`, `flag*` already exist in `_utility`; redefining = compile error.
- `dodamage(amount, origin)` takes 2 args in SP.
- `anim.noWeaponToss = true` after AI init stops Germans swapping to dropped Lugers.
- Key bindings in hints (`[&&1]`) resolve **only** in `<map>_platform.str` strings
  (`&"MAP_PLATFORM_KEY"`). In `<map>.str` they print raw.
- Keep **total live AI under ~26**; above that vehicles spawn without riders. Throttle waves.
- Stock `spawn_group` spawns riders with `doSpawn()`, which silently fails (player sight, blocked
  space) → half-empty trucks. Spawn riders yourself with `stalingradspawn()`, set
  `level.script_vehiclerideai[group] = ai` and `level.script_vehicleridespawners[group] = []`
  before `scripted_spawn(group)`; stock code then seats them.
- Hint key text in platform strings uses the stock form `[&&1]` (engine fills the use key).

- **Look before you texture:** export the material's image (`scripts/iwi_preview.py`) and view it.
  Many names (`*_door_wood01`) point to `case*` placeholder images.

### Sound
- Stock aliases are restricted with a `loadspec` column to their own level. Using
  `cityhall_vsk_itsover` in your map = `unknown sound alias` fatal *when it first plays*.
  Copy every used alias (and the secondary aliases it references) into
  `soundaliases/<map>.csv` with loadspec `<map>`; verify the wav exists in the iwds.

### Player experience
- **No visible sky box edge.** Every approach/spawn road bends 60-120 deg behind a hill and ends
  against terrain >= 500u higher, with >= 1500u between road end and sky-box wall. Measure sight
  lines with the height function, then verify with a screenshot tour. See `terrain-borders-hidden-roads.md`.
- Don't teleport AI in view. Don't let enemies spawn in view. Route spawns along curved valleys.
- Autosave at objective completion and when entering a defense position (`autosavebyname`).
- Intro: black HUD overlay fades over 3s; outro: fade to black, then `missionSuccess(next,false)`.

## 4. Proven gameplay patterns (details in references)

- **Own squad brain** instead of only friendly chains: a level thread with modes
  `wait / follow / assault / windows / circle`; follow = setgoalpos near player;
  assault = bounding overwatch (half moves, half fires, `pathenemyfightdist 600`).
- **Zone spawning on approach:** trigger_radius / distance loop → `stalingradspawn()` the
  zone's spawners → delete spawners → `waittill_aigroupcleared`.
- **Defense wave:** N enemies, 5–7 every 6s from three off-map valleys, each spawner index
  paired with its own route (`yi` used for both!), follow waypoints then building interior;
  after 6s they react to damage/sight by taking cover; at K left they flee to their own spawn
  with health 1 and are deleted out of sight.
- **Vehicle wave:** truck → halftrack (+5s) → second halftrack 10s after the MG gunner dies.
  Riders placed **beside** the vehicle (±110u lateral) with `script_vehicleride`.
- **Invulnerable friendly vehicle:** loop `self.health = 100000; self waittill("damage");`.
- **Mortar crew:** stock `_mortarteam` (trainyard pattern) with `self.mortarEnt`, `self.mortar`,
  `self.mortar_targets`, `level.mortar` effect; crew leaves the tube only when hit.
- **Door breach:** brushmodel door (real door texture fitted to the leaf), `disconnectpaths()` while
  closed, F-use trigger (off until phase), on open `connectpaths()` then `rotateyaw(178,0.9,0.1,0.4)`
  (fully open, not 90). Put the hinge (origin brush) on the ROOM-SIDE wall-face corner of the
  opening, not the wall centre, or the open leaf cuts into the wall thickness (measured), stays solid, only the `eldaba_doorbreak` sound (players read FX as gunfire).
- **Ambush door:** player reaches top step → spawn 2 behind door, OUTSIDE the leaf's swing radius,
  `ignoreall/ignoreme` until the leaf is fully open → wait 1 → door bursts → release them.
- **Weapon swap station:** script_model on a crate + trigger_use; swap current weapon,
  dropped weapon shown with the non-`_obj` model (the `_obj` variant glows).
- **Final circle:** squad forms a ring with one empty slot; speech only when all arrived and
  the player is within radius; 3s → 7s fade → `missionSuccess("credits")`.

## 5. Communicating with the user

- New map: plan mode and an in-depth question interview BEFORE coding (`planning-interview.md`).
- Report measurements, not hopes: "LEAK 0, 1 434 nodes, 0 unreachable, 0 script errors".
- Show your work. Send screenshots of what changed (doors closed and open, roads, rooms) before
  asking for a playtest. Fix whatever you see wrong first.
- Then launch the game for the user and ask them to play through and report everything. Their
  list is the next iteration; fix *every* item and re-verify each one (gates + screenshot views).
- Never push to git, publish, or shut down the machine unless the user says so in that turn.
- Explain how to open the project: `bin/CoD2Radiant.exe` -> first run load `bin/cod2.prj` ->
  File > Open `map_source/<map>.map`. Warn that regenerating from Python overwrites hand edits.
