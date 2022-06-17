"""Classes for gdb breakpoints"""

from dataclasses import dataclass, field
from typing import Callable

@dataclass
class Breakpoint:
    """Basic code breakpoint"""
    address: int
    name: str
    on_break: Callable = None
    active: bool = True
    bkpt_no: int = None
    stored_information: dict = field(default_factory=lambda : {})

@dataclass
class Watchpoint(Breakpoint):
    """Memory watchpoint"""
    watch_type: str = "awatch"
