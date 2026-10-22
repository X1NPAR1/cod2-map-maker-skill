# Pitfalls catalogue (symptom → cause → fix)

| Symptom | Cause | Fix |
|---|---|---|
| AI stand frozen | nodes float above slope | node z from triangle surface |
| AI never reach the upper floor | 16u steps give no uphill links | caulk ramp under stairs; audit one-way links |
| Squad members stuck at start | chain with too few nodes | own follow system or more chain nodes |
| AI can't pass doorways/windows | clip_player present at connectpaths | compile it +2000 up, lower at runtime |
| Script compile error on a vector | 2- or 4-component vector | 3-vectors + a separate list |
| Script file is 0 bytes | encode error after opening for write | encode first, temp file + os.replace |
| getent assert | duplicate targetname | `getentarray(...)[0]` |
| `cold_breath` missing | `setEnvironment("cold")` needs it | add the effect to `_fx` |
| Function redefinition | own `abs`/`random` | use the `_utility` versions |
| "prop not static" error | multi-bone misc_model | script_model |
| Dev assert in pain.gsc | weaponless AI in dev mode | test without developer_script |
| Attackers wander to the wrong zone | spawner index differs from route index | use the same index for both |
| Attackers stuck at a river | intermediate goal over water | bridge waypoints |
| Vehicle riders missing or sliding | spawners far from vehicle, or AI budget full | ±110u beside the vehicle; AI < 26 |
| `in solid` spawners | slope or furniture | move them and re-verify |
| Plane invisible | outside the skybox | spawn inside |
| Hint shows raw key text | wrong format or normal .str | `[&&1]` in _platform.str (engine fills the use key) |
| Vehicle comes half empty | stock spawn_group uses doSpawn(), which silently fails (sight/space) | stalingradspawn riders yourself, put them in level.script_vehiclerideai[group], empty level.script_vehicleridespawners[group] |
| AI walk through a closed scripted door | path links computed with door open | door disconnectpaths() when closed, connectpaths() when opened |
| Fatal "script_brushmodel must have DYNAMICPATH set to connect paths" | brushmodel without spawnflags 1 | `spawnflags 1` on the door |
| Door texture shows a seam / handle on the wrong edge | wrong fit offset sign | horizontal +min, vertical -min |
| Mission flow freezes after an objective; squad stands still | `autoSaveByName()` called inline: stock `tryAutoSave` loops until `autoSaveCheck()` passes (no enemies near, health ok) and can wait forever | always `level thread autoSaveByName(...)`; never block the mission thread on saves, dialogue or music (give waits a timeout) |
| Door has the wrong texture | `box()` top-only material | per-face materials |
| Player walks through an opened door | `notsolid()` after opening | keep it solid |
| Posts or planks float | z taken from a constant | z from the surface below |
| Dropped weapon glows | `_obj` model | normal model |
| `unknown sound alias` fatal | alias restricted by loadspec | copy the alias with your own loadspec |
| Black or blank loadscreen | missing `maps/<map>.csv` | add the csv |
| aigroup never clears | unused spawners still counted | delete the spawners |
| "not on a friendly chain" fatal | player off a chain | `setfriendlychain` at start |
| `undefined < int` in `_spawner` | `totalfriends` unset | set it before `_load` |
| Vehicle path hangs | cyclic node chain | linear paths |
| Enemies seen spawning | spawn points in view | valleys bending behind hills |
| Skybox visible at the map edge | terrain too low at the ends | raise ridges, bend valleys |
| Old behaviour after a fix | stale save loaded | start fresh with devmap |
| BSP won't overwrite | game still running | kill CoD2SP_s before compiling |
| Tool says "done" but nothing changed | silent failure | measure output (mtime, counts, grep) |
| Dialogue line silent; console "issued a second playsound with notification string before the first finished" | two notify-playsounds on the same actor | play each line from its own `spawn("script_origin")` linked to the speaker, delete it after the notify/timeout |
| Line plays nothing, no subtitle | stock alias points at `null.wav` (cut line) or has no subtitle | reject null.wav / empty subtitle in the alias tool; pick another stock line |
| AI stop moving everywhere; console spams "Duplicate/overlap node errors" | new nodes (ladder/platform) closer than ~40u | keep every node >=40u apart; re-check the console after each compile |
| Ladder | - | brush with material `ladder` (player climb clip) + visible rails/rungs; AI: `node_negotiation_begin` `animscript ladder_up` at the bottom facing the ladder -> `node_negotiation_end` on top, plus a top `ladder_down` begin -> bottom end |
| Runtime error mid-sequence after `delete()` | loop reads fields of an entity deleted earlier in the same loop | copy noteworthy/origin into arrays first |
| Building should collapse but walls block paths | whole house as brushmodel breaks the path net | split walls at z (e.g. +40): low band world, upper band + roof + window frames -> script_brushmodel compiled 9000u away, moved in at start; rubble brushmodel hidden, moved in on blast |
| Tower should topple | - | whole tower one script_brushmodel with an `origin` brush at the base; `rotatepitch`/`rotateroll` slow then fast, `movegravity` debris models |
| Braces/beams make nodes "in solid" | geometry under ~72u above a node | keep beams above head height |
| Objective props visible too early | - | `hide()` the model and move its trigger 10000u down; restore when the objective starts |
| "is not a friendly chain node" fatal after regenerating nodes | chain start node changed | drop `setfriendlychain` when the squad is fully scripted |
| Vehicle riders run back to where the truck spawned | stock unload overrides the goal you set | re-issue goals every few seconds for ~30 s after unload |
| Spawns seen by the player | - | before `stalingradspawn`: skip points in the view cone (dot>0.35) that pass `sighttracepassed` from the eye |
| Brushmodel textures shifted / doors and boards look skewed after moving it in | world-aligned textures are computed where the brushmodel was compiled; an arbitrary offset (9000/2000) breaks the fit | compile-time offset must be a multiple of every texture repeat used (e.g. X 9216 = 144*64, divisible by 48/64/256/512); avoid Z offsets on fitted textures |
| Attackers stop and stand far from the target | random goal inside the camp landed inside a closed building (no path) | give an always-reachable goal (just inside the gate), then hunt the nearest defender that is on the ground |
| Attackers stop to fight instead of pushing | default pathenemyfightdist | while running: `pathenemyfightdist 0`, `pathenemylookahead 0`, `ignoresuppression true`; on `damage` fight for ~4 s, then resume |
| Player/AI walk through furniture | misc_model / script_model props have no collision | add a `clip` box per prop (radius/height table per model) |
| A squad member stays at the truck forever | unexplained path/unload glitch | watchdog: no movement for 9 s and far from player -> teleport behind the player when neither spot is visible |
| AI needed on a floor with no path nodes (upper floor, MG nest) | no nodes there | walk them into the building, then `teleport` to a window `script_origin` when unseen; keep turret users in a `useturret` loop |
| Building "vanishes" in the explosion | brushmodel deleted | sink it instead: `movez(-height)` + small `rotateroll`, keep it as debris; show the rubble brushmodel |
| Vehicles start visibly late after the fade | ~2-3 s between `gopath` and visible motion | issue the start that much earlier than the moment the user wants |
