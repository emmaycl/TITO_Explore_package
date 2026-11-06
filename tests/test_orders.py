"""Independent bounded integer-order oracles and permanent join regressions."""
import contextlib
import io
import itertools
import random
import unittest

from TITO_Explore import (
    TranslationInvariantTotalOrder as TITO, compare_titos_overall,
    compute_tito_join_tito, process_tito_blocks, tito_to_inversion_set,
)
from TITO_Explore.join import compute_join_reflection_table


def rank(order, x):
    for block, (window, waning) in enumerate(zip(order.vectors, order.waxing_waning)):
        for position, value in enumerate(window):
            if (x - value) % order.n == 0:
                return block, (1 - 2 * waning) * ((x - value) // order.n) * len(window) + position
    raise AssertionError("Missing residue")


def inversions(order, limit):
    return {(a, d) for a in range(order.n) for d in range(1, limit + 1)
            if rank(order, a + d) < rank(order, a)}


def expand(matrix, n, limit):
    result = set()
    for a, row in enumerate(matrix):
        for cell in row:
            if cell:
                values, star = cell
                for value in values:
                    result.update((a, d) for d in (range(value, limit + 1, n) if star else [value])
                                  if 0 < d <= limit)
    return result


def closure(pairs, n, limit):
    # Positive increments ensure every path of weight <= limit stays in range.
    outgoing = {a: sorted(d for x, d in pairs if x == a) for a in range(n)}
    result = set()
    for a in range(n):
        reachable = {0}
        for offset in range(limit + 1):
            if offset not in reachable:
                continue
            for d in outgoing[(a + offset) % n]:
                if offset + d > limit:
                    break
                reachable.add(offset + d)
        result.update((a, d) for d in reachable if d)
    return result


REGRESSIONS = [
    ([0, 1, -2, -1], [0, 2, 1, -1], [[0], [1, -2], [3]]),
    ([0, 1, -2, -1], [0, -1, 2, 1], [[0], [1, -2], [3]]),
    ([0, 1, -1, 2], [0, 3, 1, 2], [[0], [1, -1], [2]]),
    ([0, 9, -5, 6], [0, -6, -5, 1], [[1], [0, -2], [3]]),
    ([0, -3, 2, -1], [0, 3, -2, -3], [[0], [2, -1], [1]]),
]


class OrderTests(unittest.TestCase):
    def check_pair(self, a, b, limit=120):
        ia, ib = inversions(a, limit), inversions(b, limit)
        self.assertEqual(expand(tito_to_inversion_set(a), a.n, limit), ia)
        self.assertEqual(expand(tito_to_inversion_set(b), b.n, limit), ib)
        expected = ('tito1 = tito2' if ia == ib else 'tito1 < tito2' if ia < ib else
                    'tito1 > tito2' if ia > ib else 'incomparable')
        self.assertEqual(compare_titos_overall(a, b), expected)
        j = compute_tito_join_tito(a, b)
        target = closure(ia | ib, a.n, limit)
        self.assertEqual(inversions(j, limit), target)
        self.assertEqual(expand(tito_to_inversion_set(j), a.n, limit), target)
        rows = compute_join_reflection_table(a, b)
        row_pairs = {(x, d) for x, y, star in rows
                     for d in (range(y - x, limit + 1, a.n) if star else [y - x]) if d <= limit}
        self.assertEqual(row_pairs, target)
        self.assertLessEqual(ia | ib, target)
        self.assertEqual(inversions(compute_tito_join_tito(b, a), limit), target)
        self.assertEqual(inversions(compute_tito_join_tito(a, a), limit), ia)
        normalized = TITO(a.n, a.num_blocks, process_tito_blocks(a), a.waxing_waning)
        self.assertEqual(inversions(normalized, limit), ia)
        return j

    def test_reported_regressions(self):
        for a, b, expected in REGRESSIONS:
            with self.subTest(a=a, b=b):
                j = self.check_pair(TITO(4, 1, [a], [0]), TITO(4, 1, [b], [0]), 240)
                self.assertEqual(j.vectors, expected)
                self.assertEqual(j.waxing_waning, [0, 1, 0])

    def test_seeded_mixed_orders(self):
        rng = random.Random(20261106)
        for case in range(500):
            n = rng.randint(2, 6)
            def make():
                residues = list(range(n)); rng.shuffle(residues)
                cuts = [0] + [i for i in range(1, n) if rng.random() < 0.35] + [n]
                blocks = [[r + n * rng.randint(-3, 3) for r in residues[a:b]]
                          for a, b in zip(cuts, cuts[1:])]
                return TITO(n, len(blocks), blocks, [rng.randint(0, 1) for _ in blocks])
            a, b = make(), make()
            with self.subTest(case=case, a=a, b=b): self.check_pair(a, b)

    def test_exhaustive_small_families(self):
        for n in (2, 3):
            orders = [TITO(n, 1, [[0] + [r + n * t for r, t in zip(p, shifts)]], [0])
                      for p in itertools.permutations(range(1, n))
                      for shifts in itertools.product((-1, 0, 1), repeat=n - 1)]
            for a, b in itertools.product(orders, repeat=2):
                with self.subTest(n=n, a=a, b=b): self.check_pair(a, b, 60)

    def test_demonstration_and_quiet_api(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            j = self.check_pair(TITO(6, 4, [[0, 13], [2, 9], [4], [5]], [0, 0, 0, 1]),
                                TITO(6, 4, [[0, 1], [2, 4], [3], [5]], [0, 0, 0, 1]), 240)
        self.assertEqual(j.vectors, [[0, 13], [2, -2, -3], [5]])
        self.assertEqual(j.waxing_waning, [0, 1, 1])
        self.assertEqual(out.getvalue(), '')
        self.assertEqual(process_tito_blocks(TITO(3, 2, [[4, 3], [5]], [0, 0])), [[0, 4], [2]])

    def test_invalid_inputs(self):
        invalid = [(0, 1, [[0]], [0]), (2, 2, [[0, 1]], [0]), (2, 1, [[0, 2]], [0]),
                   (3, 1, [[0, 1]], [0]), (2, 2, [[0], [1]], [0]), (2, 1, [[0, 1]], [2]),
                   (2, 2, [[], [0, 1]], [0, 0]), (2, 1, [[0.0, 1]], [0])]
        for args in invalid:
            with self.subTest(args=args), self.assertRaises(ValueError): TITO(*args)
        self.assertEqual(TITO(2, 1, [[0, 1]]).waxing_waning, [0])
        with self.assertRaises(ValueError):
            compute_tito_join_tito(TITO(2, 1, [[0, 1]]), TITO(3, 1, [[0, 1, 2]]))


if __name__ == '__main__': unittest.main()
