"""An example of reading advanced information when a breakpoint is hit"""
# pylint: disable=import-error, wrong-import-position, unused-argument
import sys
# exit examples directory
sys.path.append("../")

from examples.pokemonenums import Shininess, OverworldGender, Nature, Species, Move, Mark, ITEMS
from pygdbnx.gdbprocess import GdbProcess
from pygdbnx.breakpoint import Breakpoint

def overworld_spawn_event(gdbprocess: GdbProcess, bkpt: Breakpoint):
    """Function to be called when an overworld pokemon is generated"""
    pokemon_addr = gdbprocess.read_register("x20")
    species = Species(gdbprocess.read_int(pokemon_addr, size = "w"))
    shininess = Shininess(gdbprocess.read_int(pokemon_addr + 8, size = "w"))
    nature = Nature(gdbprocess.read_int(pokemon_addr + 12, size = "h"))
    gender = OverworldGender(gdbprocess.read_int(pokemon_addr + 16, size = "w"))
    ability = gdbprocess.read_int(pokemon_addr + 20, size = "w")
    held_item = ITEMS[gdbprocess.read_int(pokemon_addr + 28, size = "h")]
    egg_move = Move(gdbprocess.read_int(pokemon_addr + 32, size = "w"))
    guaranteed_ivs = gdbprocess.read_int(pokemon_addr + 53, size = "b")
    mark = Mark(gdbprocess.read_int(pokemon_addr + 72, size = "h"))
    brilliant_value = gdbprocess.read_int(pokemon_addr + 74, size = "b")
    fixed_seed = gdbprocess.read_int(pokemon_addr + 80, size = "g")
    print(
        f"{pokemon_addr=:X}",
        f"{species=} {shininess=}",
        f"{nature=} {gender=} {ability=} {held_item=}",
        f"{brilliant_value=} {egg_move=} {guaranteed_ivs=}",
        f"{mark=} {fixed_seed=:X}",
        sep="\n",
        end="\n\n",
        )

# IP of switch
gdb_process = GdbProcess("192.168.0.19")
# create breakpoint at address 7100D317BC
# (near end of overworld pokemon generation function in Shield)
gdb_process.add_breakpoint(Breakpoint(
    0x7100D317BC,
    "Overworld Pokemon Generated",
    on_break = overworld_spawn_event
    ))
# connecting with gdb automatically pauses execution, resume in order to wait for breakpoints
gdb_process.resume_execution()
# start loop of waiting for breaks
gdb_process.wait_for_break()
