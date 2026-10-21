# GSC scripting

## Skeleton
```c
#include maps\_utility;
#include maps\_anim;
#using_animtree("generic_human");

main()
{
	setExpFog(0.0002, 0.75, 0.8, 0.85, 0);
	setCullDist(9000);
	precacheString(&"MAP_OBJ_1");          // every objective / intro / hint string
	precacheModel("xmodel/vehicle_stuka_flying");
	precacheItem("mosin_nagant_sniper");
	level.campaign = "russian";
	maps\_truck::main("xmodel/vehicle_opel_blitz_snow");
	level.totalfriends = 0;                 // BEFORE _load
	level.maxfriendlies = 7;
	maps\<map>_fx::main();
	maps\_mortar::generic_style_init();     // only if incoming mortars are used
	maps\_load::main();
	maps\<map>_anim::main();
	maps\_mortarteam::main();               // only if AI mortar crews are used
	setEnvironment("cold");                 // needs level._effect["cold_breath"]
	flag_init("zone_a_clear");
	level thread mission();
}
```
Each vehicle model needs its own `main()` call, including damaged-tread variants. Check that a model name exists in the `xmodel/` folder of iw_13 before using it.

## Helpers (`_utility.gsc`)
| Area | Functions |
|---|---|
| Flags | `flag_init`, `flag_set`, `flag_clear`, `flag`, `flag_wait`, `flag_waitopen` |
| Triggers | `triggerOff`, `triggerOn` |
| Saves | `autoSaveByName`, `autosave` |
| AI groups | `waittill_aigroupcleared`, `getAIGroupCount`, `getAIGroupAI` |
| Waiting | `waittill_dead`, `waittill_any`, `waittill_either` |
| Spawning | `spawn_failed` |
| Arrays | `array_thread`, `array_randomize`, `array_combine`, `random`, `getClosest`, `getFarthest` |
| AI | `magic_bullet_shield`, `stop_magic_bullet_shield`, `set_forcegoal`, `unset_forcegoal` |
| Sound | `playSoundinSpace`, `playSoundOnEntity`, `playLoopSoundOnEntity` |
| Misc | `keyHintPrint`, `battleChatterOff`, `missionFailedWrapper` |

`abs`, `random` and the flag functions already exist in `_utility`. Defining your own copy is a compile error.

## Spawning a zone
```c
sp = getentarray("zone_b", "targetname");
for (i = 0; i < sp.size; i++)
{
	sp[i].count = 1;
	g = sp[i] stalingradspawn();          // forced spawn, ignores player sight
	sp[i] delete();                        // otherwise the aigroup never clears
	if (spawn_failed(g))
		continue;
	g.goalradius = 256;
	g setgoalnode(cover[i]);
}
```
Spawner keys:
- `script_aigroup`, `script_health`, `script_accuracy`, `script_grenades`.
- `script_fightdist` sets `pathenemyfightdist`; `script_maxdist` sets `pathenemylookahead`.
- `script_playerseek`, `script_ignoreme`, `script_friendname`.

## Friendlies
- **Friendly chains:**
  - Set `level.friendlyMethod = "friendly chains";`.
  - Put the player on a chain with `level.player setfriendlychain(getnode("fc_start","targetname"));`.
  - The player must always be on a chain. Otherwise the game stops with the fatal "not on a friendly chain" error.
- **Reinforcements:** a trigger with targetname `friendly_wave` targets ally spawners. It respawns allies while `level.totalfriends < level.maxfriendlies`. Keep those spawners off-map.
- **Squad brain:** for anything complex, write your own squad thread with modes such as follow, assault, windows and circle. Build it from these fields and calls:
  - `setgoalpos`, `goalradius`
  - `pathenemyfightdist`
  - `ignoreall`
  - `orientmode("face angle", yaw)`
- **Bounding assault:** half the squad moves to cover 300–500 units ahead while the other half holds and fires. Then they swap.
- **Immortal hero:** `guy thread magic_bullet_shield();`.
- **No visible teleports:** never teleport AI where the player can see it. Re-path a stuck soldier or drop them from the event instead.
- **Weapon swaps:** set `anim.noWeaponToss = true;` after the first AI spawn. This stops AI switching to a dropped Luger.

## Objectives and flow
```c
objective_add(1, "active", &"MAP_OBJ_B", posB);
objective_add(2, "active", &"MAP_OBJ_C", posC);
objective_current(1, 2);                // two current at once
objective_state(1, "done");
autoSaveByName("b_clear");
```
- **Intro:** a black HUD element (`newHudElem`, `setshader("black",640,480)`, `alpha 1`) followed by `fadeOverTime(3)` and `alpha = 0`.
- **Outro:** the same element fades to `alpha 1` over 7 s, then `missionSuccess("credits", false)`.
- **Level chain:** the previous level ends with `missionSuccess("<next>", false)`.

## Music and dialogue
- **Music:** `musicplay(alias)` and `musicstop(fade)`. For looping music, set the alias's looping column.
- **Dialogue through `_anim`:** set `level.scrsound["leonov"]["line1"] = "alias";` and `guy.animname = "leonov";`, then call `guy anim_single_solo(guy, "line1");`.
- **Simple dialogue:** `guy playsound("alias", "done"); guy waittill("done");`.

## Hints that show key names
```c
t sethintstring(&"MAP_PLATFORM_BREAK_DOOR");   // the string lives in <map>_platform.str
```
In the platform file:
```
REFERENCE           BREAK_DOOR
LANG_ENGLISH        "Press [&&1] to break the door"
```

## Syntax and encoding traps
- Vectors take exactly 1 or 3 components. If the parser rejects a negative literal, write `(0, 0 - 5, 0)`.
- Two entities with the same targetname make `getent()` assert. Use `getentarray(name, "targetname")[0]`.
- In SP, `dodamage(amount, origin)` takes 2 arguments.
- GSC and str files must be ASCII or cp1252/latin-1, so transliterate letters like ş→s. Encode the text in memory first, then write a temp file and replace the target atomically.
