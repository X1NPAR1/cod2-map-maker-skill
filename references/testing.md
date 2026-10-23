# Testing

## Load test
1. Start `CoD2SP_s.exe +set developer 1 +set logfile 2 +devmap <map>`.
2. Wait 30–40 s, then kill the process.
3. Grep `main/console.log` for `error`, `unknown sound alias`, `in solid`, `couldn't`, `missing` and `WARNING`.

## In-script test modes
```c
if (getcvar("kr_test") == "1")
	level thread auto_test();             // started with +set kr_test 1
test_log(msg) { setcvar("kr_log", msg); } // shows in console.log as "dvar set kr_log ..."
```
- **Auto test:**
  - Give the player godmode.
  - Kill each zone's AI with `g dodamage(g.health + 1, g.origin)` and wait for the zone flags.
  - Log timings, and check the objectives and the final sequence.
- **Measurement mode:** log ally positions every second to find stuck AI.
- **Log mode:** run without `developer_script 1` so stock dev asserts don't stop the run.

## Screenshots
- Cheats are on with `thereisacow 1337` plus devmap. Then use `noclip`, `setviewpos x y z yaw pitch` and `screenshotJpeg`.
- Bird's-eye shots catch layout errors, floating objects and visible skybox edges.

## The user test is final
- Launch fullscreen without developer mode.
- Collect the user's list of problems and fix every item.
- Re-measure every gate after the fixes.

## Full mission flow test (kr_tur 2) -- mandatory before handing over
- Add a test mode to the level script: when cvar `kr_tur` is `2`, run the normal mission plus an auto-player thread.
  - The auto-player is god-mode (health loop). It stays prone during stealth, teleports to each objective, kills the targets with `dodamage`, and fires the use triggers with `notify("trigger", level.player)`.
- Log with `setcvar("kr_log", msg)`. Every `dvar set kr_log ...` line lands in `console.log` (`logfile 2`); `println` does NOT.
- Also log a status line every 15 s: phase, AI counts, remaining enemies, key vehicle position. This turns a silent hang into a diagnosis.
- Start the game windowed with sound off (`snd_volume 0`, `mus_volume 0`), click once after `Load time` (the loadscreen waits for input), and watch the log with a Monitor.
- Test-script traps:
  - Never teleport the auto-player into a vehicle spawn valley; the vehicles crush it and the autosave reload loops.
  - Fire a trigger only after the script has re-enabled it, or the notify is lost.
- This run found five real bugs in one map: spawner field read after delete, turret delete, turret notsolid, visible-spawner stall, and a vehicle blocked by clip_player.
