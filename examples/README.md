## pygdbnx examples
* ``bd_tick_event`` An example of calling a function once a breakpoint is hit. This will print out "Tick event!" each time an in-game tick happens in Pokemon: Brilliant Diamond.
* ``sh_rng_watch`` An example of calling a function once a memory address is accessed. This will print out the global rng state any time it is accessed by the game in Pokemon: Sword and Shield.
* ``sh_spawn_event`` An example of reading advanced information when a breakpoint is hit. This will break whenever an overworld pokemon is spawned in Pokemon: Shield, and print out all of its information, which is stored at a register's address.
* ``vi_spawn_event`` An example of reading stack information when a breakpoint is hit. This will break whenever a pokemon is generated in Pokemon: Violet, and print out all of its information, which is stored in stack.
* ``quest_cook_prediction`` An example of waiting for input after breaking, along with storing information in breakpoints. This will break any time the global rng is accessed in Pokemon Quest, and print out how many advances until a shiny will appear.

## helper scripts
* ``pokemonenums`` This is used to convert the numbers accessed to their human-readable equivalents.
* ``pokemonrng`` Pseudo-random number generators present in the pokemon games.

## helper data
* ``cooking_weights`` Information for pokemon quest cooking spawns.