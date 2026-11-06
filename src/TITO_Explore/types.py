from __future__ import annotations
from numbers import Integral

class TranslationInvariantTotalOrder:
    def __init__(self, n, num_blocks, vectors, waxing_waning=None):
        """
        Initializes the TranslationInvariantTotalOrder.
        Args:
            n (int): The number of congruence classes.
            num_blocks (int): The number of blocks.
            vectors (list): A list of vectors.
            waxing_waning (list, optional): A list indicating if each block is waxing (0) or waning (1).
        """
        if isinstance(n, bool) or not isinstance(n, Integral) or n < 1:
            raise ValueError("n must be a positive integer.")
        if isinstance(num_blocks, bool) or not isinstance(num_blocks, Integral) or num_blocks < 1:
            raise ValueError("num_blocks must be a positive integer.")
        if not isinstance(vectors, (list, tuple)) or len(vectors) != num_blocks:
            raise ValueError("num_blocks must equal the number of windows.")
        if any(not isinstance(v, (list, tuple)) or not v for v in vectors):
            raise ValueError("Every window must be a nonempty list or tuple.")
        values = [x for v in vectors for x in v]
        if any(isinstance(x, bool) or not isinstance(x, Integral) for x in values):
            raise ValueError("Window entries must be integers.")
        if len(values) != n or {x % n for x in values} != set(range(n)):
            raise ValueError("Windows must contain every residue modulo n exactly once.")
        flags = [0] * num_blocks if waxing_waning is None else waxing_waning
        if not isinstance(flags, (list, tuple)) or len(flags) != num_blocks:
            raise ValueError("waxing_waning must have one flag per window.")
        if any(not isinstance(flag, Integral) or flag not in (0, 1) for flag in flags):
            raise ValueError("waxing_waning flags must be 0 (waxing) or 1 (waning).")
        self.n = n
        self.num_blocks = num_blocks
        self.vectors = [list(v) for v in vectors]
        self.waxing_waning = list(flags)

    def __str__(self):
        return f"TranslationInvariantTotalOrder(n={self.n}, num_blocks={self.num_blocks}, vectors={self.vectors}, waxing_waning={self.waxing_waning})"

    def __repr__(self):
        return self.__str__()
