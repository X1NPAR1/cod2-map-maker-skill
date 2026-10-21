# cod2-map-maker skill (Claude Code)

A Claude Code skill that teaches Claude to build Call of Duty 2 single-player maps end to end:
`.map` (iwmap 4) generation, compiling, AI path networks, GSC level scripting, sound aliases,
localized strings, vehicles, mortar crews, squad AI, objectives, intro/outro and mission chaining.

Every rule was measured on a real CoD2 1.3 + Mod Tools install while shipping complete maps.

Companion agent: **https://github.com/X1NPAR1/cod2-map-maker-agent**

## Contents
| File | Topic |
|---|---|
| `SKILL.md` | Workflow, hard rules, proven patterns |
| `references/planning-interview.md` | Plan-mode interview and plan template |
| `references/visual-qa.md` | Screenshot tours and visual checklist |
| `scripts/iwi_preview.py` | Export a material's texture to PNG |
| `scripts/screenshot_tour.ps1` | Drive an in-game screenshot tour |
| `references/install-layout.md` | Tools, folders, iwd contents |
| `references/map-format.md` | .map format, generator design, materials, entities |
| `references/compile-pipeline.md` | cod2map, cod2rad, connectpaths, gates, launching |
| `references/terrain-borders-hidden-roads.md` | Sky box, outer ring, hidden spawn roads |
| `references/ai-paths.md` | Lump 38 decoding, reachability audit, stairs/clip rules |
| `references/gsc-scripting.md` | Level skeleton, helpers, spawning, friendlies, objectives |
| `references/vehicles-mortars.md` | Vehicles, riders, godmode, mortar crews, flybys |
| `references/assets-sound-strings.md` | Alias loadspec trap, .str/_platform.str, models, FX |
| `references/pitfalls.md` | Symptom → cause → fix catalogue |
| `references/testing.md` | Load tests, in-script test modes, screenshots |

## Install
```bash
git clone https://github.com/X1NPAR1/cod2-map-maker-skill ~/.claude/skills/cod2-map-maker
```
Windows: clone it into `%USERPROFILE%\.claude\skills\cod2-map-maker`.

Claude loads the skill automatically for CoD2 mapping tasks. You can also invoke it with `/cod2-map-maker`.

## Disclaimer
Fan-made and unofficial. Call of Duty is a trademark of Activision. No game assets are included.
