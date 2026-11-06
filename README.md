# TITO_Explore

TITO_Explore 0.1.1 is a standalone Python package for translation-invariant total orders (TITOs) of period n. It computes normalized windows, exact inversion sets, weak-order comparison and joins in the TITO lattice, including same-residue (imaginary) inversions. It has no runtime dependencies and requires Python 3.10 or later. Source code is licensed under [MIT](LICENSE).

## Installation

From a checkout of this revision:

```sh
python -m venv .venv
# macOS/Linux; on Windows use .venv\Scripts\activate
. .venv/bin/activate
python -m pip install .
```

Use the exact Git commit recorded in the paper's `REPRODUCIBILITY.txt` when reproducing its results. Do not substitute the older 0.1.0 code. Version 0.1.1 corrects propagation of infinite inversion families through cycles; see [the correction and its scope](docs/closure-correction.txt).

## Quick start

```python
from TITO_Explore import (TranslationInvariantTotalOrder as TITO,
                         compare_titos_overall, compute_tito_join_tito)
A = TITO(6, 4, [[0, 13], [2, 9], [4], [5]], [0, 0, 0, 1])
B = TITO(6, 4, [[0, 1], [2, 4], [3], [5]], [0, 0, 0, 1])
assert compare_titos_overall(A, B) == "incomparable"
J = compute_tito_join_tito(A, B)
assert all(compare_titos_overall(X, J) == "tito1 < tito2"
           for X in (A, B))
print(J.vectors, J.waxing_waning)
# [[0, 13], [2, -2, -3], [5]] [0, 1, 1]
```

This session is also [an executable file](examples/fpsac2027_join.py). Joining the two inputs creates a waning block on residues 2, 3, 4. The finite waxing block and the waning singleton are retained. The [notebook](examples/examples_demo.ipynb) covers further operations.

## Representation and functions

A TITO is a total order on the integers invariant under simultaneous translation by n. A block is a maximal order-convex subset with finite intervals and no endpoints. Its window lists consecutive elements, one per residue in that block. All blocks together contain each residue exactly once. Repeat a waxing window by adding n, or a waning window by subtracting n. Blocks are listed in order; flags are 0 for waxing and 1 for waning.

`TranslationInvariantTotalOrder(n, num_blocks, vectors, waxing_waning=None)` validates positive integer period, nonempty integer windows, residue coverage, block count and flags. Omitted flags mean all waxing. Invalid inputs raise `ValueError`. Do not mutate a constructed object's public fields into invalid data.

All functions below are exported from `TITO_Explore`:

| Function | Return value |
| --- | --- |
| `process_tito_blocks(A)` | Normalized list of windows; does not reorder blocks or change A. The least residue starts each window. |
| `tito_to_inversion_set(A)` | n by n matrix: `None` or `([increments], star)`. Cell `[a][r]` describes inversions `(a,a+d)` with `d>0` and `(a+d)%n == r`. Star 1 adds all nonnegative multiples of n to each listed increment. |
| `compare_titos_overall(A,B)` | Exactly `"tito1 < tito2"`, `"tito1 > tito2"`, `"tito1 = tito2"` or `"incomparable"`. |
| `compute_join_reflection_table(A,B)` | List of triples `(a,a+d,star)`. The second field is a target integer, not an increment. Redundant starred representatives may occur. |
| `compute_tito_join_tito(A,B)` | Join TITO. For comparable inputs it returns an original input object, possibly unnormalized. Otherwise it reconstructs windows and verifies their full symbolic table against the closure; inconsistency raises `ValueError`. |
| `compute_tito_join(A,B)` | Legacy interface: an original TITO for comparable inputs, otherwise `(windows, flags, diagnostic_report)`. Prefer the object-returning function. |

Binary operations require equal periods. Reflection indices include same-residue pairs, which record waning behavior. Forgetting these indices gives the extended weak order quotient; this package computes in the TITO lattice itself. It does not implement other affine types, Hasse diagrams, meets or a SageMath adapter.

Comparison performs O(n²) residue-component tests under unit-cost integer arithmetic. The weighted closure pass costs O(n³ W²), where W is the largest stored increment-list size, including redundant starred values; Boolean star propagation costs O(n³). These bounds describe closure stages, not the entire checked reconstruction. Large integer shifts can produce large lists and expensive joins.

## Validation and reproduction

```sh
python -m unittest discover -s tests -v
python examples/fpsac2027_join.py
python examples/benchmark_join.py
python paper/fpsac2027/fig/software-layout/source/compute-example.py
```

The tests use independent integer-order ranks and bounded positive-path enumeration. They check 333 ordered pairs in exhaustive small waxing-window families, 500 seeded mixed-block pairs, five reported period-4 regressions, and the period-6 example (839 pairs total). Exact rules and bounds are in [the tests](tests/test_orders.py). They check inversions, normalization, comparison, both join interfaces, commutativity, idempotence and upper bounds, plus invalid inputs. Bounded checks are evidence, not a proof for arbitrary inputs. GitHub Actions is configured for Python 3.10–3.13.

The [paper bundle](paper/fpsac2027/README.txt) contains the figure data, independent example verifier, editable HTML/SVG generator, embedded font and PDF exporter. No private manuscript files are needed. The benchmark reports measured local timings and environment, rather than a cross-machine performance guarantee.

## References and development

The companion preprint is Yifan Jing, Emma Yicheng Lou, Shaotian Sun and Yuxuan Wu, *Computing Tools for Translation-Invariant Total Orders*, arXiv:2607.11709 (2026). Its original Algorithm 3 needs the correction documented above. Mathematical definitions follow Grant Barkley's work on extended weak order for affine symmetric groups. See `CITATION.cff` for software citation metadata.

Report bugs, preferably with input windows and flags, through GitHub issues. Development uses pull requests and regression tests. Planned work includes reducing redundant starred increments and exploring SageMath interoperability. No dedicated SageMath integration is currently available.
