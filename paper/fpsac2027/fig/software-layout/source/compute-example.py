"""Execute the corrected package; export the exact data used by the worked example.

The input is an explicitly constructed mathematical worked example, not an
empirical dataset or a pre-existing example claimed to come from the paper.
The package implementation is imported directly; its source hashes are recorded.
"""
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import hashlib
import importlib.util

HERE = Path(__file__).resolve().parent
REPO = Path(os.environ["TITO_SOURCE_ROOT"]).resolve() if os.environ.get("TITO_SOURCE_ROOT") else None
if REPO is not None:
    sys.path.insert(0, str(REPO / "src"))
from TITO_Explore.types import TranslationInvariantTotalOrder as TITO
from TITO_Explore.normalization import process_tito_blocks
from TITO_Explore.comparison import compare_titos_detailed, compare_titos_overall
from TITO_Explore.inversion_set import tito_to_inversion_set
from TITO_Explore.join import (
    inversion_matrix_to_edges, initialize_custom_matrix, compute_closure,
    update_indicators, compute_tito_join, compute_join_reflection_table,
)

A = TITO(6, 4, [[0, 13], [2, 9], [4], [5]], [0, 0, 0, 1])
B = TITO(6, 4, [[0, 1], [2, 4], [3], [5]], [0, 0, 0, 1])

def pack(t):
    return dict(n=t.n, blocks=t.vectors, waxing_waning=t.waxing_waning)

def reduce_matrix(matrix):
    """Sort bases; retain the smallest basis of each starred cell.

    All values in one cell are congruent modulo n, so their starred union is
    exactly the family from the minimum. No finite increments are discarded.
    """
    return [[dict(values=([min(c[0])] if c[1] else sorted(c[0])), star=bool(c[1]))
             if c and c[0] else dict(values=[], star=False) for c in row]
            for row in matrix]

def rank(x, t):
    # Independent order definition; no package inversion/comparison functions.
    for block, (window, waning) in enumerate(zip(t.vectors, t.waxing_waning)):
        for j, v in enumerate(window):
            if (x-v) % t.n == 0:
                return block, (1-2*waning)*((x-v)//t.n)*len(window)+j
    raise ValueError(x)

def direct_inversions(t, limit):
    return {(a,d) for a in range(t.n) for d in range(1, limit+1)
            if rank(a+d,t) < rank(a,t)}

def expand(matrix, n, limit):
    out = set()
    for a,row in enumerate(matrix):
        for c in row:
            for v in c['values']:
                out.update((a,d) for d in (range(v,limit+1,n) if c['star'] else [v])
                           if d <= limit)
    return out

log = io.StringIO()
with contextlib.redirect_stdout(log):
    inv_a = tito_to_inversion_set(A)
    inv_b = tito_to_inversion_set(B)
    edges = inversion_matrix_to_edges(inv_a,6) + inversion_matrix_to_edges(inv_b,6)
    union = initialize_custom_matrix(6,edges)
    closure = compute_closure(6,edges)
    final = update_indicators(copy.deepcopy(closure))
    blocks, flags, report = compute_tito_join(A,B)
    api_rows = compute_join_reflection_table(A,B)
    comparison = compare_titos_overall(A,B)
    detailed = compare_titos_detailed(A,B)
    J = TITO(6,len(blocks),blocks,flags)
    inv_j = tito_to_inversion_set(J)
    upper_bounds = [compare_titos_overall(t,J) for t in [A,B]]

assert report is None
assert comparison == 'incomparable'
assert blocks == [[0,13],[2,-2,-3],[5]] and flags == [0,1,1]
assert upper_bounds == ['tito1 < tito2']*2
assert process_tito_blocks(A) == A.vectors
assert process_tito_blocks(B) == B.vectors
assert process_tito_blocks(J) == J.vectors

limit = 240
direct_a, direct_b, direct_j = [direct_inversions(t,limit) for t in [A,B,J]]
for m,expected in [(inv_a,direct_a),(inv_b,direct_b),(inv_j,direct_j),(final,direct_j)]:
    assert expand(reduce_matrix(m),6,limit) == expected
assert direct_a | direct_b < direct_j
assert (2,1) in direct_a-direct_b  # reflection index (2,3)
assert (3,5) in direct_b-direct_a  # reflection index (3,8)

# Independent exact bounded transitive closure of integer inversions.
# Weights are positive, so every path with total <= limit stays in this range.
union_pairs = direct_a | direct_b
walks = set()
for a in range(6):
    reachable = {0}
    for offset in range(limit+1):
        if offset not in reachable:
            continue
        for d in range(1,limit-offset+1):
            if ((a+offset)%6,d) in union_pairs:
                reachable.add(offset+d)
    walks.update((a,d) for d in reachable if d)
assert walks == direct_j

u, j = reduce_matrix(union), reduce_matrix(final)
changed = [[a,b] for a in range(6) for b in range(6) if u[a][b] != j[a][b]]
assert changed == [[2,2],[2,3],[2,4],[3,3],[4,4]]
api_expansion = set()
for a,b,star in api_rows:
    api_expansion.update((a,d) for d in (range(b-a,limit+1,6) if star else [b-a])
                         if d <= limit)
assert api_expansion == direct_j

data = dict(
    provenance=dict(repository='https://github.com/emmaycl/TITO_Explore_package',
                    version=__import__('TITO_Explore').__version__,
                    source_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__import__('TITO_Explore').__file__).parent.glob('*.py'))},
                    example='Constructed worked input, executed with corrected version 0.1.1',
                    display_reduction='Starred cell bases reduced to their minimum; finite bases retained'),
    inputs=dict(A=pack(A),B=pack(B)), output=pack(J), comparison=comparison,
    comparisons=detailed, inversion_A=reduce_matrix(inv_a), inversion_B=reduce_matrix(inv_b),
    union=u, closure=j, changed_cells=changed,
    raw_closure=closure, raw_final=final, raw_reflection_rows=sorted(api_rows),
    witness_cycle=[dict(source=2,target=3,weight=1,star=False,operand='A'),
                   dict(source=3,target=4,weight=1,star=True,operand='B'),
                   dict(source=4,target=2,weight=4,star=True,operand='A')],
    checks=dict(status='PASS',increment_limit=limit,
                exact_bounded_walk_closure=True, window_rank_agrees=True,
                input_normalization=True, reconstruction_report=report,
                strict_upper_bounds=upper_bounds,
                unbounded_argument='All five changed cells are generated by paths through residues 2,3,4. '
                'The cycle 2->3->4->2 has weight 6; its starred edges supply every additional multiple of 6. '
                'No union edge leaves {0,1} for a later block, or leaves {2,3,4} for {5}; '
                'no path enlarges the finite (0,1) entry. The displayed table is therefore closed under '
                'positive weighted path concatenation, contains the union, and each displayed family '
                'has a union-path witness. It is the exact transitive closure, beyond the bounded check.')
)

# Verify the cycle against the unreduced input union.
for edge in data['witness_cycle']:
    cell=u[edge['source']][edge['target']]
    assert edge['weight'] in cell['values'] or (cell['star'] and edge['weight'] >= min(cell['values']) and (edge['weight']-min(cell['values'])) % 6 == 0)
    assert not edge['star'] or cell['star']
representation=TITO(4,2,[[0,5,6],[3]],[0,1])
data['representation']=dict(order=pack(representation), table=reduce_matrix(tito_to_inversion_set(representation)))
assert expand(data['representation']['table'],4,100)==direct_inversions(representation,100)

(HERE/'example-data.json').write_text(json.dumps(data,indent=2)+'\n')
(HERE.parent/'qa').mkdir(parents=True,exist_ok=True)
(HERE.parent/'qa/example-package.log').write_text(log.getvalue())
print(json.dumps(dict(version=data['provenance']['version'],output=data['output'],
                     changed_cells=changed,checks=data['checks']),indent=2))
