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
| Brushmodel compiled far away looks dark / unlit | it was compiled outside the skybox (no sun, no light grid) | compile it INSIDE the skybox at a lit, node-free spot (e.g. high above the outer ridge), shifted by multiples of 512 |
| Brushmodel textures misaligned after moving it in | geometry was generated in place and then text-shifted, so fitted textures (doors, shutters) were computed for the wrong spot | generate the part directly at the compile location (fits computed there); textures travel with the brushmodel |
| Brushmodel compiled in place cuts the building interior out of the path net | brushmodel volume over a room blocks connectpaths links | never compile a removable part in place over a room; use the in-skybox offset above |
| A whole house interior becomes unreachable after adding props | a prop's clip box sits on the door's outside node | keep clip boxes >= 120u from every door; re-run the path audit after every prop pass |
| `actor_*_mg42portable` fatal in `_spawner::mg42setup_gun` | that class needs a target node for its MG | don't use portable-MG classes without a set-up node |
| Halftrack MG silent after the gunner gets out | stock turret is manual_ai | after unload: `mgturret[0] setturretteam("axis"); setmode("auto_nonai")` |
| Tank fights in script order | stock tanks auto-shoot and kill the wrong target first | keep scripted victims invulnerable (`waittill damage` health reset loop) until their turn; fire with `setturrettargetent` -> `turret_on_target` (timeout) -> `notify turret_fire`; kill with `dodamage` + `notify death` |
| Enemies spawn while the truck is still far / squad never shoots from the truck | group spawned at arrival | spawn the defenders when the vehicle is ~3 path nodes (~720u) from its stop; the player can already aim from `playerLinkToDelta` |
| Defenders always pile into one building | positions handed out in a fixed order | split window spots by building, alternate soldiers between buildings, shuffle each time |
| Building must collapse in stages but its interior stays pathable | world walls can't be removed | keep ground-floor walls as world; put the slab + upper floor halves into separate in-skybox brushmodels; stage 1 tilts/sinks one half (`rotateroll` + `movez`) and swaps in a rubble brushmodel; stage 2 sinks the rest and swaps in a "ruin" brushmodel (triangle-topped broken walls via `kama`, rubble mounds via `konveks`, door blockers with `clip`) |
| Rubble looks blocky ("square-square") | box-only broken walls | alternate flat boxes with sloped `kama` segments rising/falling along the wall so tops form triangles |
| Falling debris stays forever | spawned debris models never removed | `movegravity` + `rotatevelocity`, then delete after ~2 s |
| Objective prop glows before its objective | the `_obj` model is set from the start | spawn the plain model; blink plain/_obj only once the objective is added |
| Vehicles arrive overlapped | spawned and started together on the same path | spawn on the requested interval, but start each `gopath` with an extra stagger (~2.5 s per vehicle) |
| Scripted vehicles pass through rocks/trees | decor scattered without knowing vehicle routes | keep vehicle route polylines in the generator and exclude rocks/trees within ~350u of them |
| Squad stands still all fight | one cover assignment, then idle | every 30-40 s move each soldier to another free cover/window 200-900u away inside the play area |
| Fly-by strafe | - | script_model `vehicle_stuka_flying`: `moveto` dive, `playloopsound("stuka_guns")`, impact fx walking along the road, `moveto` climb out of the map, delete; `setspeed(+6, accel)` on the convoy at the first impact |
| Funnel-shaped ramps in front of doors look fake | sloped `kama` ramps flaring outward | make the building floor brush only ~2u above the surrounding brush yard; no ramp needed and links stay two-way (brush -> brush) |
| Mounted MG floats above a roof | turret origin set above the roof floor with nothing under the bipod | put `misc_turret` (mg42_bipod_stand) ON a parapet/sandbag top surface; gunner spot 40u behind |
| Next wave starts the moment the player arrives | `waittill_aigroupcleared` returns before the late-spawned group exists | collect spawned AI into a list, set a "spawned" flag, then wait for flag + list empty |
| Only part of a closed building must break (a corner) | world walls | route every box fully inside the corner rect into a list (kutu6 region hook), build the roof as an L so the corner slab is separate, compile that list in-skybox as a brushmodel; swap to a triangle-rubble corner + clip on hit |
| Friendlies die too fast / leave cover | default health, big pathenemyfightdist | health 1250 for the squad, `pathenemyfightdist` ~64 at windows, move to another window of the SAME house on damage or every 30-40 s |
| Final ring members don't face the centre | goal positions only | spawn a script_origin at the centre and `lookat` it in a short loop |
| Broken corner looks "cut square" | rubble tops at random heights | zig-zag profile: start at full wall height next to the intact wall and fall toward the corner, alternating up/down sloped `kama` teeth (~34u wide); add hanging roof edge, leaning beams and 2-3 rubble mounds |
| Fitted textures (shutters) in a region-routed brushmodel misalign | offset computed for the original spot, geometry shifted later | when routing a box into the shifted list, add the shift to its fit offset (x offset for x-faced walls, -dz for z) |
| AI fall off a ladder | ladder brush/rails stick far above the roof, top negotiation end too close to the edge | ladder brush ends ~20u above the roof, top end node ~40u inside the parapet gap |
| Rubble mounds outside doors look like funnels; enemies walk through | mounds placed outside, links still exist | put door rubble INSIDE, keep clip in the doorway, add `badplace_cylinder` over the ruin after it appears |
| Reinforcements all crowd one building | they reuse the house-window assignment | give late reinforcements yard cover nodes spread over the whole village, shuffled, with occasional cover hops |
| Convoy speed-up "keeps accelerating" | multiplying the current speed | absolute speeds: `setspeed(20)` for 3 s, back to `setspeed(15)`; slower path-node speeds on the last nodes before the stop |
| Air strike on a building | - | Stuka from the enemy's entry valley: dive `moveto` (eased), spawn `prop_stuka_bomb` under it, `moveto` target with pitch, incoming whistle, impact -> staged collapse; plane climbs out and is deleted |
| Tank stops forever at a town gate | a `clip_player` blocker (keeps the player inside) also blocks vehicles | raise the blocker (`movez(4000)`) while the vehicle drives through, lower it again on `reached_end_node` |
| `removed entity is not an entity` in `animscripts/mg42/stand.gsc` | turret deleted while its gunner is still in the mg animscript | kill the gunner, then `hide()` the turret after ~1.5 s; never `delete()` it, and `notsolid()` is invalid on turrets (runtime error) |
| Replacement spawns stop at "15 left", objective never completes | spawn loop retries the SAME spawner while it is in the player's view | keep a separate cursor that advances on every attempt (visible or failed) so the next spawner is tried |
| `pair 'undefined' and '2'` when reading spawner fields | spawners deleted earlier in the same `getentarray` loop | guard with `isdefined(sp.script_noteworthy)`; pair crews/triggers to their gun by `script_noteworthy`, never by array index (`getentarray` order is not the noteworthy order) |
| Road valley through the outer ridge shows a wide open gap and the road end | ridge reduced over ~1300u around the road | narrow canyon: reduce the ridge only within ~230-820u of the road (`ss(230, 820, road_dist)`), place rock/shrub clusters along the canyon floor outside the play area |
| Player can wander far into empty desert | play polygon much bigger than the action | shrink the polygon to ~1500u beyond the furthest scripted action |
| Crusader / Panzer / trucks drive silently | engine aliases (`crusader_engine_low`, `panzer2_idle_high`, `truck_*`, `halftrack_*`; names from the `vehicles/<type>` file's `*Snd` fields) are loadspec-restricted to stock levels | copy them into `soundaliases/<map>.csv` with loadspec `<map>` |
| Enemy tank fires at the player during a stealth convoy | stock `_tank` `turret_attack_think` runs on every tank | set `script_turret 0` on the vehicle entity and `setmode("manual")` on every `mgturret[]` |
| One AI (Price) never leaves his spawn while the rest run | `setgoalpos` to a free point he has no path to: the AI silently stands still | send squads with `setgoalnode(nearest unused pathnode)`; add a phase-limited watchdog that moves a frozen AI next to a teammate while unseen |
| Watchdog teleports the hero back to an old rally point | watchdog kept running after the phase changed | end every watchdog when its phase ends |
| Road mesh looks broken on bends | 3-column road strip: inner-edge points cross at sharp corners and the triangles fold | Chaikin-smooth the polyline (3 passes) before building the strip |
| Riders of a passing convoy suddenly attack | at the end node the stock code unloads the riders and they become normal AI | keep your own copy of the rider list at spawn; delete riders and vehicle ~900u BEFORE the end node |
| Plant marker floats beside a gun/tank | spawn origin + constant z | ground markers: bulletTrace down to the floor; tank charges: `weapon_stickybomb(_obj)` linked to `tag_engine_left` (krasnoye/tankhunt pattern) |
| Player cannot reach a plant trigger | a clip box around the prop, or a player-blocker next to the vehicle's stop | no clip boxes around props (use the model's own collision); stop vehicles well clear of blockers, put the use trigger on the reachable side |
| Squad "doesn't go" after a briefing | `ekip_hucum` found no cover nodes near the target, so the mode never changed | send scripted moves with `setgoalnode` to nearest real nodes around the point; give the brain a "scene" mode that leaves them alone |
| Cinematic vehicles vanish in view | forced delete after a timeout | delete only when unseen AND far from the player; extend the exit path |
| Final truck cannot drive out | player-only gate blocker (clip_player) blocks vehicles too | raise the blocker before `gopath` |
