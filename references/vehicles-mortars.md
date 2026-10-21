# Vehicles, riders, mortars, flybys

## Spawn and drive
```c
v = maps\_vehicle::scripted_spawn(4)[0];        // vehicle has script_vehiclespawngroup 4
level thread maps\_vehicle::gopath(v);
```
- **Path:** an `info_vehicle_node` chain linked through `target`. The last node ends the path.
- **No loops:** a looping chain makes `vehicle_paths_setup` hang. Do loops in script instead.
- **Node events:** set `script_noteworthy` to `godon`, `godoff`, `unload_continue` or a custom notify.
- **Speeds we used:**

  | Vehicle | Speed |
  |---|---|
  | Arriving friendly truck | 20 |
  | Fast enemy truck | 60 |
  | Halftrack | 16 |

## Riders
- **Spawner keys:** `script_vehicleride` is the vehicle's ride group; `script_startingposition` is the seat.
- **Seats:**
  - Truck: 0..8, where 0 is the driver.
  - Halftrack: 1 is the MG gunner (an mg42 on `tag_turret`).
- **Placement:** put rider spawners beside the vehicle start, ±110 units lateral and 20 + k*60 units along the body.
  - Too far ahead: riders slide along the ground or never board.
  - Too far sideways in a valley: they end up in solid.
- **AI budget:** riders only spawn while there is room in the AI budget. Keep live AI under about 26 before a vehicle spawns.
- **Unloading:** to tell when riders are off, poll `distance(rider.origin, vehicle.origin) > 150`, then give them orders.

## Invulnerable vehicle
```c
godmode()
{
	self endon("death");
	for (;;)
	{
		self.health = 100000;
		self waittill("damage");
	}
}
```

## Incoming mortar barrage
- **Call:** `maps\_mortar::generic_style("mortar", delay, barrage, barrageDelay, minRange, maxRange);`.
- **Setup:** it asserts unless `level._effect["mortar"]` exists. `generic_style_init()` must run before `_load`.
- **Start/stop:** use the `explosion_startNotify` / `explosion_stopNotify` level notifies.

## AI mortar crew (trainyard pattern)
1. Call `maps\_mortarteam::main()` after `_load`, then set `level.mortar = level._effect["mortar"]`.
2. Place the crew spawners and a `script_model` for `prop_mortar`.
3. On the crew, set `self.mortarEnt`, `self.mortar` and `self.mortar_targets` (an array of script_origins).
4. Keep the crew on `ignoreall` until one of them is damaged, then let them fight. This also avoids `tag_flash` errors.

## Plane flyby
```c
u = spawn("script_model", start);
u setmodel("xmodel/vehicle_stuka_flying");
u.angles = vectortoangles(end - start);
u moveto(end, 14);
u playsound("matmata_stuka_flyby1");
```
Both the start and end points must be inside the skybox, or the plane is invisible.
