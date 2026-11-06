"""Reproduce a local microbenchmark of the exact period-6 demonstration."""
import json
import platform
import statistics
import timeit
from TITO_Explore import TranslationInvariantTotalOrder as TITO, compute_tito_join_tito, tito_to_inversion_set
from TITO_Explore.join import inversion_matrix_to_edges, initialize_custom_matrix, compute_closure

A=TITO(6,4,[[0,13],[2,9],[4],[5]],[0,0,0,1])
B=TITO(6,4,[[0,1],[2,4],[3],[5]],[0,0,0,1])
edges=inversion_matrix_to_edges(tito_to_inversion_set(A),6)+inversion_matrix_to_edges(tito_to_inversion_set(B),6)
# compute_closure only adds increments, so its final maximum is also the
# largest list size reached during the weighted pass.
W=max(len(c[0]) for row in compute_closure(6,edges) for c in row)
repeats,number=7,100
samples=[t/number for t in timeit.repeat(lambda:compute_tito_join_tito(A,B),repeat=repeats,number=number)]
print(json.dumps(dict(python=platform.python_version(),platform=platform.platform(),processor=platform.machine(),period=6,W=W,repeats=repeats,joins_per_repeat=number,median_seconds=statistics.median(samples),min_seconds=min(samples),max_seconds=max(samples),samples_seconds=samples,scope='Full object-returning join, including reconstruction and symbolic table verification; input construction excluded.'),indent=2))
