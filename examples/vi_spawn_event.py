"""An example of reading stack information when a breakpoint is hit"""
# pylint: disable=import-error, wrong-import-position, unused-argument
import sys
# exit examples directory
sys.path.append("../")

# TODO: update enums for SV
from examples.pokemonenums import Nature, Species, ITEMS
from pygdbnx.gdbprocess import GdbProcess
from pygdbnx.breakpoint import Breakpoint

def is_shiny(pid: int, sidtid: int):
    """Check if a given pid is shiny"""
    temp = pid ^ sidtid
    return ((temp & 0xFFFF) ^ (temp >> 16)) < 0x10

def overworld_spawn_event(gdbprocess: GdbProcess, bkpt: Breakpoint):
    """Function to be called when a pokemon is generated"""
    pokemon_addr = gdbprocess.read_register("sp") + 0x18
    ec = gdbprocess.read_int(pokemon_addr)
    pid = gdbprocess.read_int(pokemon_addr + 0x8)
    tidsid = gdbprocess.read_int(pokemon_addr + 0x10)
    species = gdbprocess.read_int(pokemon_addr + 0x18, "w")
    form = gdbprocess.read_int(pokemon_addr + 0x1a, "w")
    held_item = gdbprocess.read_int(pokemon_addr + 0x1c, "h")
    level = gdbprocess.read_int(pokemon_addr + 0x1e, "h")
    gender = gdbprocess.read_int(pokemon_addr + 0x20, "h")
    nature = Nature(gdbprocess.read_int(pokemon_addr + 0x22, "h"))
    stat_nature = Nature(gdbprocess.read_int(pokemon_addr + 0x24, "h"))
    ability = gdbprocess.read_int(pokemon_addr + 0x26, "b")
    shiny_rolls = gdbprocess.read_int(pokemon_addr + 0x27, "b")
    ivs = [gdbprocess.read_int(pokemon_addr + 0x28 + i * 2, "h") for i in range(6)]
    evs = [gdbprocess.read_int(pokemon_addr + 0x34 + i * 2, "h") for i in range(6)]
    friendship = gdbprocess.read_int(pokemon_addr + 0x40, "w")
    guaranteed_ivs = gdbprocess.read_int(pokemon_addr + 0x44, "b")
    size1_type = gdbprocess.read_int(pokemon_addr + 0x45, "b")
    size1 = gdbprocess.read_int(pokemon_addr + 0x46, "b")
    size0_type = gdbprocess.read_int(pokemon_addr + 0x47, "b")
    size0 = gdbprocess.read_int(pokemon_addr + 0x48, "b")
    size2_type = gdbprocess.read_int(pokemon_addr + 0x49, "b")
    size2 = gdbprocess.read_int(pokemon_addr + 0x4a, "b")
    favorite = gdbprocess.read_int(pokemon_addr + 0x4b, "b")
    fateful_encounter = gdbprocess.read_int(pokemon_addr + 0x4c, "b")
    print(
        f"{pokemon_addr=:X}",
        f"{species=} {form=} {level=} {shiny_rolls=}",
        f"{ec=:X} {tidsid=:X} {pid=:X} {is_shiny(pid, tidsid)=}",
        f"{nature=} {stat_nature=} {gender=} {ability=} {held_item=}",
        f"{guaranteed_ivs=} {ivs=} {evs=}",
        f"{size0_type=} {size1_type=} {size2_type=}",
        f"{size0=} {size1=} {size2=}",
        f"{favorite=} {fateful_encounter=} {friendship=}",
        sep="\n",
        end="\n\n",
    )

# IP of switch
gdb_process = GdbProcess("192.168.0.19")
# create breakpoint at address 7100D0AA60
# (near end of pokemon generation function in Violet)
gdb_process.add_breakpoint(Breakpoint(
    0x7100d0aa60,
    "Pokemon Generated",
    on_break = overworld_spawn_event
    ))
# connecting with gdb automatically pauses execution, resume in order to wait for breakpoints
gdb_process.resume_execution()
# start loop of waiting for breaks
gdb_process.wait_for_break()
