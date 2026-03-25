from __future__ import annotations

from typing import Dict, List, Optional, Tuple

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
) -> Tuple[List[List[int]], List[int], Optional[Dict[str, Any]]]:
    """
    Computes the join of two TITOs and returns the resulting window notation,
    waxing/waning flags, and anomaly report.
    """
    table_rows = compute_join_reflection_table(tito1, tito2)
    return reflection_rows_to_blocks_and_order(table_rows, tito1.n)
