# Compile pipeline

```bat
set R=F:\Activision\Call of Duty 2
copy "%R%\map_source\<map>.map" "%R%\main\maps\<map>.map"
"%R%\bin\cod2map.exe" -platform pc "%R%\main\maps\<map>"
"%R%\bin\cod2rad.exe" -platform pc "%R%\main\maps\<map>"
del "%R%\main\maps\<map>.map"
"%R%\CoD2SP_s.exe" +set developer 1 +set logfile 2 +set g_connectpaths 2 +set thereisacow 1337 +set com_introplayed 1 +devmap <map>
```
- SP: no vis step. Full compile of a ~8000×6400 terrain map: 10–12 min (light dominates).
  If only GSC changed, skip compile; a load test takes ~30 s.
- `g_connectpaths 2` computes links, writes them into the bsp and quits. Value 1 continues
  into the map. Do it after EVERY BSP compile — the bsp otherwise has no links.
- `.lin` (leak line) moves back to `map_source`; load it in Radiant (File ▸ Pointfile).

## Gates (read logs, don't trust exit codes)
1. cod2map output: no `LEAK`, no `MAX_MAP_*`, no `brush with no sides`.
2. cod2rad finished; `.d3dbsp` mtime newer than `.map`.
3. console.log after connectpaths: no `in solid` lines (each = spawner/node inside geometry),
   no `no connections`, paths saved message present.
4. Lump audit: decode lump 38 (see ai-paths.md) – node count matches entity count; BFS 0 unreachable.
5. Load test (`+devmap <map>` with `developer 1`, quit after N s): grep console.log for
   `script runtime error`, `script compile error`, `unknown sound alias`, `missing`, `couldn't find`.

## Launch for the user (playtest)
```
CoD2SP_s.exe +set r_fullscreen 1 +set r_mode 1920x1080 +set r_aaSamples 1 +set thereisacow 1337 +set com_introplayed 1 +devmap <map>
```
No `developer 1` for user tests (dev asserts in stock animscripts can stop the game).
Kill leftover `CoD2SP_s` processes before every compile — they lock the bsp.
