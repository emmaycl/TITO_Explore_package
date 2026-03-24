#define the TITO Object Data Structure
from __future__ import annotations
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

class TranslationInvariantTotalOrder:
    """
    Represents a Translation-Invariant Total Order over Z/nZ.
    Args:
        n:             Number of congruence classes (mod n).
        num_blocks:    Number of blocks in the order.
        vectors:       List of blocks; each block is a list of integers.
        waxing_waning: List of length num_blocks — 0 = waxing, 1 = waning.
    """
    def __init__(
        self,
        n: int,
        num_blocks: int,
        vectors: List[List[int]],
        waxing_waning: Optional[List[int]] = None,
    ) -> None:
        self.n = n
        self.num_blocks = num_blocks
        self.vectors = vectors
        self.waxing_waning = waxing_waning if waxing_waning is not None else []
    def __str__(self):
        return f"TranslationInvariantTotalOrder(n={self.n}, num_blocks={self.num_blocks}, vectors={self.vectors}, waxing_waning={self.waxing_waning})"
    def __repr__(self):
        return self.__str__()

