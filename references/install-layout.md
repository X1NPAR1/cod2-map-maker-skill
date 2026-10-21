# Install layout (CoD2 1.3 + Mod Tools)

Root = game directory (e.g. `F:\Activision\Call of Duty 2`). Mod Tools must be installed into it.

## Executables
| File | Role |
|---|---|
| `CoD2SP_s.exe` | Single-player exe; use for `+devmap`, connectpaths, tests |
| `CoD2MP_s.exe` | Multiplayer exe |
| `bin/CoD2Radiant.exe` | Level editor. First run: load `bin/cod2.prj` |
| `bin/cod2map.exe` | BSP compiler (`-platform pc`, `-vis` unused in SP) |
| `bin/cod2rad.exe` / `cod2rad64.exe` | Light compiler |
| `bin/CoD2CompileTools.exe` | GUI that calls the `cod2compiletools_*.bat` files; point it at the root once |
| `bin/CoD2_EffectsEd.exe` | .efx editor |
| `bin/asset_manager.exe`, `bin/converter.exe` | GDT/asset conversion (xmodel, xanim, materials) |
| `bin/cod2.def` | Entity definitions shown in Radiant |

`bin/cod2.prj`: `basepath ".."`, `mapspath "..\map_source"`, `entitypath ".\cod2.def"`.

## Folders
- `map_source/` – `.map` sources and `prefabs/` (newvillers, matmata, eldaba, libyatown, lamps, interactable_objects...).
  Stock example: `newvillers.map` (gameplay layer, ~3000 entities) pulls geometry from
  `newvillers_geo.map` via one `misc_prefab`. Study it for real key usage.
- `main/` – game data. `iw_00..iw_15.iwd` are zip files:
  - iw_07: `maps/*.gsc` (all stock SP scripts), `animscripts/`, `animtrees/`, `fx/`, materials
  - iw_13: `xmodel/`, `xanim/`, materials; iw_08: `character/`, `aitype/`; iw_04-06: sound, soundaliases, ui
  - iw_15: patch overrides; `localized_english_iw*`: localized sound + `localizedstrings`
  Loose files in `main/maps`, `main/sound`, `main/soundaliases`, `main/localizedstrings`,
  `main/sun` override iwd contents.
- `deffiles/*.gdf` – asset schemas; `source_data/*.gdt` – weapon/turret settings;
  `collmaps/` – collision brushes for models; `aitype/*.gdt` – character aliases.
- `Docs/` – `CoD2_Tools_Documentation.htm`, `ScriptFunctions/` (engine function reference — check
  here before using any builtin), `compiletools/`, `lighting/`, `portals/`.
- `main/console.log` – written with `+set logfile 2`. Your primary runtime evidence.
- `main/players/<profile>/save/` – save games (`.svg`); delete stale ones after big changes.

## Extract stock scripts once
```
python -c "import zipfile;zipfile.ZipFile(r'main/iw_07.iwd').extractall(r'../cod2_ref')"
```
Grep the extracted `maps/` for any function before you call it.
