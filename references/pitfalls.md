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
