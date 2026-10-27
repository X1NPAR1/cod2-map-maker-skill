# cod2-map-maker — Claude Code skill for Call of Duty 2 single-player maps

A Claude Code skill that turns Claude into a working **Call of Duty 2 single-player level designer and scripter**. It covers the whole pipeline: generated `.map` geometry (iwmap 4), BSP/light compiles, AI path networks, GSC level scripting, vehicles, squads, sound, strings, testing and mission chaining.

Every rule in it was **measured in a real CoD2 1.3 + Mod Tools install**, not taken from documentation or memory.

> **Built with this skill:** [cod2-maps](https://github.com/X1NPAR1/cod2-maps), a released six-mission campaign of about 1 hour to 1 hour 15 minutes (3 Soviet + 3 British missions) with a one-click installer.
>
> Companion agent: [cod2-map-maker-agent](https://github.com/X1NPAR1/cod2-map-maker-agent)

---

## What it does

| Area | Coverage |
|---|---|
| **Geometry** | Python generators for terrain meshes, buildings, roads, sky box and border ridges; texture fitting; hidden approach roads and canyons |
| **Compile** | cod2map / cod2rad / `g_connectpaths`, log gates (LEAK, `in solid`, `no connections`) |
| **AI paths** | Lump 38 decoding, reachability BFS from the player start, stair/clip/closed-volume rules |
| **Scripting** | Level skeleton, objectives, autosaves, a custom squad brain, waves, hidden spawning, watchdogs, cinematic scenes |
| **Vehicles** | Convoys, riders, halftrack MGs, tanks (turret control, sticky bombs), Crusaders, Stukas, truck finales with stock animations |
| **Assets** | The sound-alias `loadspec` trap, vehicle engine sounds, `.str` / `_platform.str` hint keys, models, FX |
| **Stock quality** | Measured anatomy of IW's own `newvillers` source, a 370-prefab catalogue by nation (US/Normandy, British/North Africa, Germany), and the stock script systems |
| **Reverse engineering** | A CoD2 `.d3dbsp` decompiler: blueprint any stock map, or cut a bunker or street into a prefab for your own map |
| **QA** | Screenshot tours, a mandatory auto-player mission flow test, a playtest loop with the user |

## Workflow it enforces

1. **Plan:** a plan-mode interview with evidence gates.
2. **Generate:** geometry and entities from Python.
3. **Compile:** BSP and light, gate `LEAK 0`.
4. **Connect paths:** AI path network, gate 0 unreachable nodes.
5. **Script:** gate 0 script errors and 0 unknown aliases.
6. **Screenshot tour:** mandatory visual check.
7. **Flow test:** an auto-player plays the whole mission; gate `GOREV TAMAM`.
8. **Playtest:** the user plays and reports; every item gets fixed.

Each step ends with a **measurement**. "It compiled" is never accepted as proof.

## Contents

| File | Topic |
|---|---|
| `SKILL.md` | Workflow, hard rules, proven gameplay patterns |
| `references/planning-interview.md` | Plan-mode interview and plan template |
| `references/install-layout.md` | Tools, folders, iwd contents |
| `references/map-format.md` | `.map` format, generator design, materials, entities |
| `references/compile-pipeline.md` | cod2map, cod2rad, connectpaths, gates, launching |
| `references/terrain-borders-hidden-roads.md` | Sky box, outer ridge, canyon road valleys, hidden spawn roads |
| `references/ai-paths.md` | Lump 38 decoding, reachability audit, stairs and clip rules |
| `references/gsc-scripting.md` | Level skeleton, helpers, spawning, friendlies, objectives |
| `references/vehicles-mortars.md` | Vehicles, riders, godmode, mortar crews, flybys |
| `references/assets-sound-strings.md` | Alias loadspec trap, `.str` / `_platform.str`, models, FX |
| `references/visual-qa.md` | Screenshot tours and the visual checklist |
| `references/testing.md` | Load tests, the mission flow test (auto-player), log mining |
| `references/pitfalls.md` | 100+ entries: symptom → cause → fix |
| `references/stock-map-anatomy.md` | How Infinity Ward built `newvillers`, measured from the shipped source: geo/script split, prefab towns, terrain patches, road decals, dressing density, clips, portals, node density, trigger textures, lights |
| `references/prefab-catalog.md` | All 370 stock prefabs measured (size, floor, front side, doors/windows), themes by nation, placement rules verified in game |
| `references/stock-scripts-study.md` | How the 30 stock levels are scripted: `_load` trigger keys, call frequencies, level skeleton, start points, backdrops, ambience |
| `references/reverse-engineering.md` | The CoD2 `.d3dbsp` format and how to decompile a stock map into a blueprint or cut regions into placeable prefabs |
| `scripts/iwi_preview.py` | Export a material's texture to PNG |
| `scripts/screenshot_tour.ps1` | Drive an in-game screenshot tour (game window kept topmost) |
| `scripts/map_inspect.py` | Parse any `.map`: entity, key and material statistics; real brush corners; patch sizes |
| `scripts/prefab_catalog.py` | Regenerate the prefab catalogue (markdown + JSON) |
| `scripts/bsp_decompile.py` | Decompile a stock `.d3dbsp` (whole map or `--region ... --prefab`) |

## Install

```bash
git clone https://github.com/X1NPAR1/cod2-map-maker-skill ~/.claude/skills/cod2-map-maker
```

On Windows, clone it into `%USERPROFILE%\.claude\skills\cod2-map-maker`.

Claude loads the skill automatically for CoD2 mapping tasks. You can also invoke it with `/cod2-map-maker`. For long builds, install the companion agent as well.

## Requirements

- Call of Duty 2 with patch 1.3, and the CoD2 Mod Tools installed into the game folder.
- Python 3 for the generators and audits.
- Windows PowerShell for compiling, testing and screenshot tours.

## Disclaimer

Fan-made and unofficial. Call of Duty is a trademark of Activision. No game assets are included.
