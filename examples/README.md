## pygdbnx examples
* ``bd_tick_event`` An example of calling a function once a breakpoint is hit. This will print out "Tick event!" each time an in-game tick happens in Pokemon: Brilliant Diamond.
* ``sh_rng_watch`` An example of calling a function once a memory address is accessed. This will print out the global rng state any time it is accessed by the game in Pokemon: Sword and Shield.
* ``sh_spawn_event`` An example of reading advanced information when a breakpoint is hit. This will break whenever an overworld pokemon is spawned in Pokemon: Shield, and print out all of its information, which is stored at a register's address.

## helper scripts
* ``pokemonenums`` This is used to convert the numbers accessed by ``sh_spawn_event`` to their human-readable equivalents.