"""An example of calling a function once a memory address is accessed"""
# pylint: disable=import-error, wrong-import-position, unused-argument
import sys
# exit examples directory
sys.path.append("../")

from pygdbnx.gdbprocess import GdbProcess
from pygdbnx.breakpoint import Breakpoint, Watchpoint

def on_rng_accessed(gdbprocess: GdbProcess, bkpt: Breakpoint):
    """Function to be called when the global rng state is accessed"""
    seed0 = gdbprocess.read_int(0x4C2AAC18, size = "g", offset_heap=True)
    seed1 = gdbprocess.read_int(0x4C2AAC18 + 8, size = "g", offset_heap=True)
    print(f"{seed0=:X} {seed1=:X}")

# IP of switch
gdb_process = GdbProcess("192.168.0.18")
# create memory watchpoint at heap + 0x4C2AAC18 (global rng state in SWSH)
gdb_process.add_breakpoint(Watchpoint(
    gdb_process.heap_base + 0x4C2AAC18,
    "RNG state accessed",
    on_break=on_rng_accessed
    ))
# connecting with gdb automatically pauses execution, resume in order to wait for breakpoints
gdb_process.resume_execution()
# start loop of waiting for breaks
gdb_process.wait_for_break()
