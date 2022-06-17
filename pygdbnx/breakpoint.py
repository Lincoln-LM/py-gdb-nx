"""Classes for gdb breakpoints"""

from dataclasses import dataclass
from typing import Callable

@dataclass
class Breakpoint:
    """Basic code breakpoint"""
    address: int
    name: str
    on_break: Callable = None
    active: bool = True
    bkpt_no: int = None

@dataclass
class Watchpoint(Breakpoint):
    """Memory watchpoint"""
    watch_type: str = "awatch"
