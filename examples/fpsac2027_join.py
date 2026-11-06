"""The exact session printed in the FPSAC software demonstration."""
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
