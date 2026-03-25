from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Union

from TITO_Explore.inversion_set import tito_to_inversion_set
from TITO_Explore.reflection import reflection_rows_to_blocks_and_order
from TITO_Explore.types import TranslationInvariantTotalOrder

Edge = Tuple[int, int, List[int]]
MatrixCell = Tuple[List[int], int]


def inversion_matrix_to_edges(
    matrix: List[List[MatrixCell | None]],
    n: int,
) -> List[Edge]:
    """
    Converts an inversion matrix entry ([vals], star) at matrix[i][j]
    into edge tuples (i, (i + v) % n, [v]).
    """
    edges: List[Edge] = []
    for i in range(n):
        for j in range(n):
            cell = matrix[i][j]
            if cell is None:
                continue
            values, _ = cell
            for value in values:
                edges.append((i, (i + value) % n, [value]))
    return edges


def _cell_subset(cell_a: MatrixCell | None, cell_b: MatrixCell | None) -> bool:
    """Returns True iff inversion cell A is a subset of cell B."""
    if cell_a is None:
        return True
    if cell_b is None:
        return False

    vals_a, star_a = cell_a
    vals_b, star_b = cell_b

    set_a = set(vals_a)
    set_b = set(vals_b)

    if star_a and not star_b:
        return False

    if not star_a and star_b:
        return set_a.issubset(set_b)

    # star_a == star_b (both True or both False)
    return set_a.issubset(set_b)


def _matrix_subset(matrix_a: List[List[MatrixCell | None]], matrix_b: List[List[MatrixCell | None]]) -> bool:
    """Elementwise subset check between two inversion matrices of the same size."""
    if len(matrix_a) != len(matrix_b):
        return False

    n = len(matrix_a)
    for i in range(n):
        for j in range(n):
            if not _cell_subset(matrix_a[i][j], matrix_b[i][j]):
                return False
    return True


def _tito_to_window(
    tito: TranslationInvariantTotalOrder,
    inv_matrix: List[List[MatrixCell | None]] | None = None,
) -> Tuple[List[List[int]], List[int], Optional[Dict[str, Any]]]:
    """
    Converts a single TITO into the same window/flag/report triple that
    compute_tito_join returns. Accepts an optional precomputed inversion
    matrix to avoid recomputation when available.
    """
    inv = inv_matrix if inv_matrix is not None else tito_to_inversion_set(tito)
    edges = inversion_matrix_to_edges(inv, tito.n)
    closure = compute_closure(tito.n, edges)
    final_matrix = update_indicators(closure)
    table_rows = generate_reflection_table(final_matrix)
    return reflection_rows_to_blocks_and_order(table_rows, tito.n)


def initialize_custom_matrix(n: int, initial_edges: List[Edge]) -> List[List[MatrixCell]]:
    """Initializes an n by n matrix with edge values and a 0 indicator."""
    matrix: List[List[MatrixCell]] = [[([], 0) for _ in range(n)] for _ in range(n)]
    for u, v, values in initial_edges:
        matrix[u][v] = (list(set(values)), 0)
    return matrix


def update_path(matrix: List[List[MatrixCell]], i: int, k: int, j: int) -> bool:
    """
    Extends path i->k->j if k is strictly intermediate.
    This guard prevents self-loop compounding.
    """
    if i == k or j == k:
        return False

    list_ik = matrix[i][k][0]
    list_kj = matrix[k][j][0]

    if list_ik and list_kj:
        generated = {a + b for a in list_ik for b in list_kj}
        current = set(matrix[i][j][0])
        combined = current | generated
        if combined != current:
            matrix[i][j] = (list(combined), 0)
            return True
    return False


def compute_closure(n: int, initial_edges: List[Edge]) -> List[List[MatrixCell]]:
    """Runs Floyd-Warshall-style closure over the edge matrix."""
    matrix = initialize_custom_matrix(n, initial_edges)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                update_path(matrix, i, k, j)
    return matrix


def update_indicators(matrix: List[List[MatrixCell]]) -> List[List[MatrixCell]]:
    """
    Marks diagonal entries with non-empty value lists as indicator=1,
    then propagates indicator=1 to edges whose start or end node has a loop.
    """
    n = len(matrix)
    for i in range(n):
        if matrix[i][i][0]:
            matrix[i][i] = (matrix[i][i][0], 1)

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            values, _ = matrix[i][j]
            if values and (matrix[i][i][1] == 1 or matrix[j][j][1] == 1):
                matrix[i][j] = (values, 1)
    return matrix


def generate_reflection_table(matrix: List[List[MatrixCell]]) -> List[Tuple[int, int, int]]:
    """
    Converts the closure matrix into reflection table rows:
    (start_node, start_node + value, indicator)
    """
    n = len(matrix)
    table_rows: List[Tuple[int, int, int]] = []
    for a in range(n):
        for b in range(n):
            values, indicator = matrix[a][b]
            for c in values:
                table_rows.append((a, a + c, indicator))
    return table_rows


def compute_join_reflection_table(
    tito1: TranslationInvariantTotalOrder,
    tito2: TranslationInvariantTotalOrder,
) -> List[Tuple[int, int, int]]:
    """
    Takes two TITO objects, converts them to inversion matrices,
    converts the matrices to edge lists, runs the closure + indicator logic,
    and returns the resulting reflection table rows.
    """
    if tito1.n != tito2.n:
        raise ValueError("Both TITOs must have the same modulus n.")

    n = tito1.n
    inv1 = tito_to_inversion_set(tito1)
    inv2 = tito_to_inversion_set(tito2)

    edges = inversion_matrix_to_edges(inv1, n) + inversion_matrix_to_edges(inv2, n)
    closure = compute_closure(n, edges)
    final_matrix = update_indicators(closure)
    return generate_reflection_table(final_matrix)


def compute_tito_join(
    tito1: TranslationInvariantTotalOrder,
    tito2: TranslationInvariantTotalOrder,
) -> Union[TranslationInvariantTotalOrder, Tuple[List[List[int]], List[int], Optional[Dict[str, Any]]]]:
    """
    Computes the join of two TITOs. If the two TITOs are already comparable
    in the lattice (one inversion set contained in the other), the larger
    original TITO object is returned directly; otherwise the join is computed
    via reflection-table closure and returned in window/flag/report form.
    """
    if tito1.n != tito2.n:
        raise ValueError("Both TITOs must have the same modulus n.")

    inv1 = tito_to_inversion_set(tito1)
    inv2 = tito_to_inversion_set(tito2)

    subset_1_in_2 = _matrix_subset(inv1, inv2)
    subset_2_in_1 = _matrix_subset(inv2, inv1)

    if subset_1_in_2:
        return tito2

    if subset_2_in_1:
        return tito1

    edges = inversion_matrix_to_edges(inv1, tito1.n) + inversion_matrix_to_edges(inv2, tito1.n)
    closure = compute_closure(tito1.n, edges)
    final_matrix = update_indicators(closure)
    table_rows = generate_reflection_table(final_matrix)
    return reflection_rows_to_blocks_and_order(table_rows, tito1.n)
