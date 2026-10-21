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
