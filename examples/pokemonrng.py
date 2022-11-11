"""Pseudorandom number generators used in pokemon"""
from typing import List
import numpy as np

class Xorshift:
    """UnityEngine.Random's Xorshift128 PRNG"""

    # Ignore over/underflow
    np.seterr(over='ignore', under='ignore')

    # Constants
    SHIFT_8 = np.uint32(8)
    SHIFT_16 = np.uint32(16)
    SHIFT_11 = np.uint32(11)
    SHIFT_22 = np.uint32(22)
    SHIFT_19 = np.uint32(19)
    ALT_MIN = np.uint32(-0x80000000)
    ALT_MAX = np.uint32(0x7FFFFFFF)
    FLOAT_MAX = np.uint32(0x7FFFFF)
    (FLOAT_1,) = np.frombuffer(b'\x00\x00\x80\x3F', dtype=np.float32)
    (FLOAT_MUL,) = np.frombuffer(b'\x01\x00\x00\x34', dtype=np.float32)

    def __init__(
        self,
        seed0: np.uint32,
        seed1: np.uint32,
        seed2: np.uint32,
        seed3: np.uint32,
    ):
        """Create Xorshift from seeds

        Args:
            seed0 (np.uint32): Seed at index 0
            seed1 (np.uint32): Seed at index 1
            seed2 (np.uint32): Seed at index 2
            seed3 (np.uint32): Seed at index 3
        """
        self.state: List[np.uint32] = [
            np.uint32(seed0),
            np.uint32(seed1),
            np.uint32(seed2),
            np.uint32(seed3),
        ]

    def next(self) -> np.uint32:
        """Generate next random u32

        Returns:
            np.uint32: 32 bit random number
        """
        seed0 = self.state[0]
        seed3 = self.state[3]

        seed0 ^= seed0 << self.SHIFT_11
        seed0 ^= seed0 >> self.SHIFT_8
        seed0 ^= seed3 ^ (seed3 >> self.SHIFT_19)

        self.state = self.state[1:4] + [seed0]

        return seed0

    def previous(self) -> np.uint32:
        """Reverse next to get the previous random number

        Returns:
            np.uint32: Previous 32 bit random number
        """
        # Undo seed1 ^ (seed1 >> self.SHIFT_19)
        seed0 = self.state[2] >> self.SHIFT_19 ^ self.state[2] ^ self.state[3]
        # Undo seed0 ^= seed0 >> self.SHIFT_8
        seed0 ^= seed0 >> self.SHIFT_8
        seed0 ^= seed0 >> self.SHIFT_16
        # Undo seed0 ^= seed0 << self.SHIFT_11
        seed0 ^= seed0 << self.SHIFT_11
        seed0 ^= seed0 << self.SHIFT_22

        self.state = [seed0] + self.state[0:3]

        return seed0

    def rand(
        self,
        minimum: np.uint32 = 0,
        maximum: np.uint32 = 0x100000000,
    ) -> np.uint32:
        """Generate random int in range [minimum,maximum)

        Args:
            minimum (np.uint32): Minimum random number. Defaults to 0
            maximum (np.uint32): Maximum random number. Defaults to 0x100000000

        Returns:
            np.uint32: Random int in range
        """
        minimum = np.uint32(minimum)
        maximum = np.uint32(maximum) if maximum < 0x100000000 else 0x100000000

        return (self.next() % (maximum - minimum)) + minimum

    def alt_rand(
        self,
        minimum: np.uint32 = 0,
        maximum: np.uint32 = 0x100000000,
    ) -> np.uint32:
        """Generate random int in range[minimum,maximum) based on rand(-0x80000000,0x7FFFFFFF)

        Args:
            maximum (np.uint32): Maximum random number. Defaults to 0
            minimum (np.uint32): Minimum random number. Defaults to 0x100000000

        Returns:
            np.uint32: Random int in range
        """
        minimum = np.uint32(minimum)
        maximum = np.uint32(maximum) if maximum < 0x100000000 else 0x100000000

        return (self.rand(self.ALT_MIN,self.ALT_MAX) % maximum) + minimum

    def rand_float(
        self,
        minimum: np.float32 = 0.0,
        maximum: np.float32 = 1.0,
    ):
        """Generate random float in range[minimum,maximum)

        Args:
            minimum (np.float32): Minimum random float. Defaults to 0.0
            maximum (np.float32): Maximum random float. Defaults to 1.0
        """
        minimum = np.float32(minimum)
        maximum = np.float32(maximum)

        rand = np.float32(np.uint64(self.next() & self.FLOAT_MAX)) * self.FLOAT_MUL
        return rand * minimum + (self.FLOAT_1 - rand) * maximum
