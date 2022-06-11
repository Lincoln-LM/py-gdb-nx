"""An example of calling a function once a breakpoint is hit"""
# pylint: disable=import-error, wrong-import-position, unused-argument
import sys
# exit examples directory
sys.path.append("../")

from pygdbnx.gdbprocess import GdbProcess
from pygdbnx.breakpoint import Breakpoint

def on_tick_event(gdbprocess: GdbProcess, bkpt: Breakpoint):
    """Function to be called when the TickEvent breakpoint is hit"""
    print("Tick event!")

# IP of switch
gdb_process = GdbProcess("192.168.0.18")
# create breakpoint at address 71002BC2C70 (SmartPoint.AssetAssistant.Sequencer$$Update in BD)
gdb_process.add_breakpoint(Breakpoint(0x7102BC2C70, "TickEvent", on_break = on_tick_event))
# connecting with gdb automatically pauses execution, resume in order to wait for breakpoints
gdb_process.resume_execution()
# start loop of waiting for breaks
gdb_process.wait_for_break()
