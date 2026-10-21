# Assets, sounds, strings

## Sound aliases
- **File:** `soundaliases/<map>.csv`. Copy the header from a stock csv in iw_06; its columns include `name, sequence, file, ... loadspec, subtitle`.
- **The loadspec trap:** stock aliases are restricted to their own level through the loadspec column.
  - Copy every alias you use and set its loadspec to `<map>`.
  - If a row has a `secondaryaliasname`, copy that alias too.
- **Check the wav files:** confirm that each `file` exists in an iwd or in loose `main/sound/`.
- **Check the script:** collect every string your GSC passes to `playsound`, `musicplay`, `playloopsound` and `playSoundinSpace`, and diff the list against the csv. A single missing alias stops the game the first time it plays.
- **Custom audio:** 16-bit PCM wav, mono for 3D sounds, stored under `main/sound/<map>/`.

## Localized strings
```
VERSION             "1"
CONFIG              "C:\trees\cod2\bin\StringEd.cfg"
FILENOTES           ""

REFERENCE           OBJ_A
LANG_ENGLISH        "Take the outpost."

ENDMARKER
```
- **Referencing:** use `&"<MAP>_OBJ_A"`, i.e. the file name in uppercase plus `_` plus the reference.
- **Precache:** precache every string with `precacheString`.
- **Key-binding text:** put it in `<map>_platform.str` and reference it as `&"<MAP>_PLATFORM_KEY"`.
- **Encoding:** cp1252 or ASCII.

## Models
- `_obj` models such as `weapon_*_obj` glow. Use them only on pickups that should be highlighted.
- Multi-bone models cannot be static `misc_model`s; make them `script_model`s.
- Confirm every model exists in the `xmodel/` folder of iw_13, and precache each one you spawn from script.
- **Crate tops:** stock `prop_crate*` are 26 units tall.

## FX
Register effects in `<map>_fx.gsc` as `level._effect["name"] = loadfx("fx/...efx");`.

Effects we confirmed:
- `fx/dust/dust_door_ambush.efx`
- `fx/impacts/large_woodhit.efx`
- `fx/muzzleflashes/mortar_flash.efx`

## Level csv (`main/maps/<map>.csv`)
```
levelBriefing,loadscreen_tankhunt
victoryBackdrop,victory_russian
defeatBackdrop,defeat_russian
```
