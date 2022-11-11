"""Example of waiting for input after breaking, along with storing information in breakpoints"""
# pylint: disable=import-error, wrong-import-position, unused-argument
import sys
import json
import numpy as np
# exit examples directory
sys.path.append("../")

from examples.pokemonrng import Xorshift
from examples.pokemonenums import Species
from pygdbnx.gdbprocess import GdbProcess
from pygdbnx.breakpoint import Breakpoint

with open("./cooking_weights.json", encoding="utf-8") as file:
    COOKING_WEIGHTS = json.load(file)
COOKING_RARITY = input("Cooking Rarity: ")
COOKING_TYPE = input("Cooking Type: ")
COOKING_TYPE_2 = input("Cooking Type 2 (enter for None): ")
if COOKING_TYPE_2 == "":
    COOKING_TYPE_2 = None
SPECIES = int(input("Target Species ID: "))

def is_shiny(sidtid, pid):
    """Check if a pid is shiny"""
    return ((sidtid ^ pid ^ ((sidtid ^ pid) >> 16)) & 0xFFFF) < 16

def pokemon_slot(
    _rng: Xorshift,
    cooking_rarity: str,
    cooking_type: str,
    cooking_type_2: str = None
):
    """Generate random pokemon"""
    weights: dict = COOKING_WEIGHTS[cooking_rarity][cooking_type]
    if cooking_type_2 is not None:
        weights = weights[cooking_type_2]
    weight_total = sum(weights.values())
    rand_weight = _rng.rand(maximum=weight_total)
    weight_count = 0
    for species, weight in weights.items():
        species = int(species)
        if rand_weight < weight_count + weight:
            return Species(species)
        weight_count += weight
    return Species(0)

def generate_voxel(rng: Xorshift):
    """Generate pokemon information and return shininess"""
    _rng = Xorshift(*rng.state)
    _rng.next() # delay of 1
    _rng.rand(maximum=210) # multiple pokemon check
    species = pokemon_slot(_rng, COOKING_RARITY, COOKING_TYPE, COOKING_TYPE_2)
    _rng.next() # level range
    sidtid = _rng.alt_rand()
    _rng.rand(maximum=25) # seikaku
    for _ in range(81):
        pid = np.uint32(_rng.rand_float(maximum=0x100000000)) # why is this float
        if is_shiny(sidtid, pid):
            break
    return is_shiny(sidtid, pid), pid, sidtid, species

def on_rng_accessed(gdbprocess: GdbProcess, bkpt: Breakpoint):
    """Function to be run whenever the global rng is accessed"""
    seed0 = gdbprocess.read_int(0x2c8ef30,size="w",offset_main=True)
    seed1 = gdbprocess.read_int(0x2c8ef34,size="w",offset_main=True)
    seed2 = gdbprocess.read_int(0x2c8ef38,size="w",offset_main=True)
    seed3 = gdbprocess.read_int(0x2c8ef3c,size="w",offset_main=True)
    rng: Xorshift = bkpt.stored_information.get('rng_tracker', None)
    if rng is None:
        rng = Xorshift(seed0,seed1,seed2,seed3)
        bkpt.stored_information['rng_tracker'] = rng
        bkpt.stored_information['rng_advances'] = 0
    else:
        test = Xorshift(seed0,seed1,seed2,seed3)
        while rng.state != test.state:
            rng.next()
            bkpt.stored_information['rng_advances'] += 1
    advances: int = bkpt.stored_information['rng_advances']

    test = Xorshift(seed0,seed1,seed2,seed3)
    advances_until_shiny = 0
    # can only hit even/odd
    if not advances & 1:
        test.next()
        advances_until_shiny += 1
    while not (generate_voxel(test)[0] and generate_voxel(test)[-1] == Species(SPECIES)):
        test.next()
        test.next()
        advances_until_shiny += 2

    print(f"{advances=}")
    print(f"{advances_until_shiny=}")
    print(f"{generate_voxel(test)}")
    print(f"{seed0=:08X} {seed1=:08X} {seed2=:08X} {seed3=:08X}")
    input()

# IP of switch
gdb_process = GdbProcess("192.168.0.19")
# create breakpoint when rng is accessed
gdb_process.add_breakpoint(Breakpoint(
    0x710101d960,
    "RNG accessed",
    on_break=on_rng_accessed
))
# connecting with gdb automatically pauses execution, resume in order to wait for breakpoints
gdb_process.resume_execution()
# start loop of waiting for breaks
gdb_process.wait_for_break()
