"""PyGDBNX specific Exceptions"""

class GDBNotFoundException(Exception):
    """Raised when the GDB executable is not found"""

class WaitApplicationException(Exception):
    """Raised when `monitor wait application` fails"""
