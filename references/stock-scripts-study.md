# How the stock SP levels are scripted (measured on all 30 campaign `.gsc`)

Extract the scripts with:

```
unzip -o "main/iw_*.iwd" "maps/*.gsc" -d <scratch>
```

There are 204 files: 30 levels × (`<map>.gsc`, `_anim.gsc`, `_fx.gsc`, `_amb.gsc`) plus the stock
`_*.gsc` systems.

## 1. IW relies on map-driven stock systems

`maps\_load::main()` scans every trigger (`trigger_multiple/once/use/radius/lookat/damage`). It
starts a stock behaviour for each key it finds, so **most of the gameplay is in the map, not in
the level script** (`_load.gsc`, lines 330–425).

| trigger key / targetname | stock handler | effect |
|---|---|---|
| `target` → spawner(s) | `_spawner::trigger_spawn` | spawns the targeted spawners when touched |
| `script_killspawner N` | `_spawner::kill_spawner` | deletes all spawners with the same N (stops reinforcements behind the player) |
| `script_emptyspawner` | `_spawner::empty_spawner` | sets counts to 0 |
| `script_autosave` / `script_autosavename` | `_autosave` | checkpoint on touch |
| `script_fallback` | `_spawner::fallback_think` | AI fall back to the next node group |
| `script_mg42auto` | `_mg42::mg42_auto` | MG42 auto mode |
| `script_exploder N` | `_load::exploder_load` | fires exploder N (destruction set-pieces) |
| `ambient "<track>"` | `_load::ambient_thread` | switches the ambience track |
| `script_fxstart` / `script_fxstop` | | starts or stops looped FX |
| `script_triggered_playerseek` | | AI hunt the player |
| `targetname flood_spawner` | `_spawner::flood_trigger` | endless respawn until a `stopspawn` or `kill` trigger |
| `targetname friendly_wave` / `friendly_wave_off` | `_spawner::friendly_wave` | friendly reinforcements |
| `targetname friendly_chat`, `axis_touching`, `axis_dead`, `dead_autosave`, `friendly_mg42`, `hopelesslylost` | `_load` / `_spawner` | small stock helpers |
| `script_noteworthy triggeronce`, `targetname ambient_volume` | `_load` | |

In newvillers, the trigger texture names what the trigger does, which keeps the editor readable:
`aitrig` 84, `escort` 55, `spawner_trigger` 53, `kill` 43, `stopspawn` 22, `ambient` 20
(see `stock-map-anatomy.md` §7).

**Rule for us:**
- Use these keys before writing custom loops. A `spawner_trigger` that targets a group, plus a
  `kill` trigger with the same `script_killspawner` at the next street, is how IW paces waves.
- Our own loops (squad brain, watchdogs) are still right for set-pieces the stock systems do not
  cover.

## 2. Frequency of the main calls (30 levels)

| call | uses | levels |
|---|---|---|
| `level.player` | 1 642 | 32 |
| `getentarray` | 830 | 33 |
| `anim_single` / `anim_reach` / `anim_loop` | 629 | 26 |
| `setgoalnode` | 363 | 27 (vs `setgoalpos` 41 in 15) |
| `flag_wait` / `flag_set` | 354 / 318 | 25 / 24 |
| `setBattleChatter` | 324 | 25 |
| `objective_add` | 299 | 29 |
| `autosavebyname` | 227 | 23 |
| friendly chains (`friendlyChain*`, `setFriendlyChainWrapper`) | 188 + 94 | 24 + 20 |
| `doSpawn` | 184 | 23 (vs `stalingradspawn` 56 in 15) |
| `magic_bullet_shield` | 179 | 27 |
| `trigger_on` / `trigger_off` | 154 | 26 |
| `exploder(` | 129 | 25 |
| `musicplay` | 51 | 23 |
| `setCullFog` / `setExpFog` | 32 / 28 | 16 / 22 |
| `waittill_aigroupcleared` | 10 | 3 |

**Lessons:**
- **`setgoalnode` is the norm.** IW sends AI to path nodes, not points. This matches our measured
  freeze bug, where an AI given an unreachable point stood still.
- **Cinematics are `_anim` calls with scene animations** (`anim_reach` → `anim_single` →
  `anim_loop`) on tags of vehicles or nodes. Example: beltot's truck scene in `vehicles-mortars.md`.
- **Destruction is exploders.** Geometry and FX entities carry `script_exploder N`, and
  `exploder(N)` swaps them. That is cheaper and more reliable than moving brushmodels by hand.

## 3. Level skeleton IW uses (newvillers / matmata / toujane)

```c
main()
{
    setCullFog(300, 3500, r, g, b, 0.1);         // or setExpFog(density, r, g, b, 0) + setCullDist(N)
    precache...();                                // shaders, models, strings
    level.campaign = "british";                   // drives friendly names / voices
    maps\_<vehicle>::main("xmodel/...");          // every vehicle type BEFORE _load
    maps\<map>_fx::main();
    maps\_load::main();
    level thread maps\<map>_amb::main();          // ambience
    maps\<map>_anim::main();
    flag_init(...);                               // one flag per beat
    level.price = getent("price","script_linkname"); level.price thread magic_bullet_shield();
    level.player setFriendlyChainWrapper(getnode(...));
    array_thread(getentarray("...","targetname"), ::handler);   // data-driven per-entity threads
    objective_add(...);  // all objectives added up front, later set active/done
    if (getcvar("start") == "...") ...            // dev start points (skip to a section)
}
```

- **Start points:** `getcvar("start")` (newvillers, toujane, matmata) or `getcvar("jumpto")`
  (eldaba). These are developer cvars that jump to a section: the player and friendlies are
  teleported and earlier triggers are turned off. Use the same for long missions; it is much
  faster than a full flow test for checking a late section.
- **Data-driven threads:** `array_thread(getentarray("grenade","script_noteworthy"), ::grenadeTossGuy)`.
  Behaviour is attached by `targetname` / `script_noteworthy` set in the map, never by hard-coded
  coordinates.

## 4. Environment from script

- **Backdrops** close the horizon with xmodel cards spawned in script:
  `backdrop_toujane_card`, `backdrop_toujane_frntmntn`, `backdrop_toujane_frnthill`,
  `backdrop_newvillers_card`, `backdrop_newvillers_trees`, `backdrop_rhine_card`,
  `backdrop_silotown_trees` and `backdrop_british_destroyer`.
  For example: `backdrop = spawn("script_model", (0,0,185)); backdrop setmodel("xmodel/backdrop_toujane_card");`
- **Fog and draw distance:**
  - desert: `setExpFog(0.00015, 131/255, 116/255, 116/255, 0); setCullDist(4000);`
  - Normandy night: `setCullFog(300, 3500, ...)`
  - measured `setCullDist` values: 2 800–18 000; most often 4 000–6 000.
- **Ambience (`_amb.gsc`)** uses the stock `_ambient` package:
  - tracks: `level.ambient_track["exterior"|"interior"|...]` = `"ambient_<map>_ext"`;
  - `set_ambient("exterior")`;
  - `ambientDelay(track, min, max)`;
  - `ambientEvent(track, "elm_windgust1", weight)` for random one-shots (wind gusts, distant
    explosions);
  - interior/exterior switches through `ambient` triggers in the map.
- **FX (`_fx.gsc`):** `loadfx` table plus `maps\_fx::loopfx` / `oneshotfx` for fires, smoke and
  dust (newvillers 7 calls, eldaba 34, matmata 26).

## 5. Checklist for a stock-quality level script

- [ ] All vehicles `main()`'d before `_load`; `_fx` before `_load`; `_amb` and `_anim` after.
- [ ] Waves paced with spawner triggers plus `kill` / `stopspawn` triggers (map keys).
- [ ] AI moves with `setgoalnode`; friendlies use chains or our squad brain.
- [ ] Every beat is a `flag`; objectives added up front; `autosavebyname` at each beat.
- [ ] Destruction through `script_exploder` groups.
- [ ] Ambience package with interior and exterior tracks; backdrops plus fog plus cull distance.
- [ ] `start` / `jumpto` dev cvar for every major section.
