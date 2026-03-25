from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass(frozen=True)
class _RowRec:
    src: int   # a mod n
    tgt: int   # value mod n
    star: bool # indicator == 1
    value: int # original values


class _DSU:
    def __init__(self, n: int) -> None:
        self.p = list(range(n))
        self.r = [0] * n

    def find(self, x: int) -> int:
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.r[ra] < self.r[rb]:
            ra, rb = rb, ra
        self.p[rb] = ra
        if self.r[ra] == self.r[rb]:
            self.r[ra] += 1


def _topo_sort(nodes: List[int], edges: Dict[int, Set[int]]) -> Optional[List[int]]:
    node_set = set(nodes)
    indeg = {x: 0 for x in nodes}

    for u in nodes:
        for v in edges.get(u, set()):
            if v in node_set:
                indeg[v] += 1

    queue = deque([x for x in nodes if indeg[x] == 0])
    out: List[int] = []

    while queue:
        x = queue.popleft()
        out.append(x)
        for y in edges.get(x, set()):
            if y in node_set:
                indeg[y] -= 1
                if indeg[y] == 0:
                    queue.append(y)

    return out if len(out) == len(nodes) else None


def _cycle_fallback_order(nodes: List[int], recs: List[_RowRec], n: int) -> List[int]:
    seen: Set[Tuple[int, int]] = {(r.src, r.tgt) for r in recs if r.src != r.tgt}

    def comes_before(x: int, y: int) -> bool:
        if x == y:
            return False
        i, j = (x, y) if x < y else (y, x)
        if (i, j) in seen:
            return x == j
        return x == i

    order: List[int] = []
    for value in sorted(nodes):
        placed = False
        for idx in range(len(order)):
            if comes_before(value, order[idx]):
                order.insert(idx, value)
                placed = True
                break
        if not placed:
            order.append(value)
    return order


def reflection_rows_to_blocks_and_order(
    rows: List[Tuple[int, int, int]],
    n: int,
) -> Tuple[List[List[int]], List[int], Optional[Dict[str, Any]]]:
    recs: List[_RowRec] = [
        _RowRec(src=a % n, tgt=v % n, star=(ind == 1), value=v)
        for a, v, ind in rows
    ]

    pair_evidence: Dict[Tuple[int, int], Set[Tuple[int, int, bool]]] = defaultdict(set)
    pair_rows: Dict[Tuple[int, int], List[_RowRec]] = defaultdict(list)
    diag_star: Set[int] = set()

    for r in recs:
        if r.src == r.tgt:
            if r.star:
                diag_star.add(r.src)
            continue
        a, b = sorted((r.src, r.tgt))
        pair_evidence[(a, b)].add((r.src, r.tgt, r.star))
        pair_rows[(a, b)].append(r)

    dsu = _DSU(n)
    pair_case: Dict[Tuple[int, int], str] = {}
    report: Dict[str, Any] = {"bad_pairs": [], "notes": []}

    for (a, b), evidence in pair_evidence.items():
        ev_list = list(evidence)
        star_count = sum(1 for (_, _, star) in ev_list if star)
        total = len(ev_list)

        if total == 1 and star_count == 1:
            pair_case[(a, b)] = "different_blocks"
        elif star_count == 0:
            pair_case[(a, b)] = "same_block_waxing"
            dsu.union(a, b)
        elif total == 2 and star_count == 2:
            pair_case[(a, b)] = "same_block_waning"
            dsu.union(a, b)
        else:
            pair_case[(a, b)] = "BAD"
            report["bad_pairs"].append(
                {
                    "pair": (a, b),
                    "distinct_directed_evidence": sorted(ev_list),
                    "raw_rows": [
                        (rr.src, rr.tgt, rr.star, rr.value)
                        for rr in pair_rows[(a, b)]
                    ],
                }
            )

    comp_to_nodes: Dict[int, List[int]] = defaultdict(list)
    for residue in range(n):
        comp_to_nodes[dsu.find(residue)].append(residue)

    blocks = [sorted(values) for values in comp_to_nodes.values()]

    block_waning: Dict[int, int] = {}
    for nodes in blocks:
        root = dsu.find(nodes[0])
        node_set = set(nodes)
        is_waning = any(node in diag_star for node in node_set)

        if not is_waning:
            for i in nodes:
                for j in nodes:
                    if i >= j:
                        continue
                    if pair_case.get((i, j)) == "same_block_waning":
                        is_waning = True
                        break
                if is_waning:
                    break
        block_waning[root] = 1 if is_waning else 0

    node_edges: Dict[int, Set[int]] = defaultdict(set)
    block_edges: Dict[int, Set[int]] = defaultdict(set)

    for r in recs:
        if r.src == r.tgt:
            continue
        u, v = r.tgt, r.src
        node_edges[u].add(v)
        cu, cv = dsu.find(u), dsu.find(v)
        if cu != cv:
            block_edges[cu].add(cv)

    block_roots = sorted({dsu.find(block[0]) for block in blocks})
    block_order = _topo_sort(block_roots, block_edges)
    if block_order is None:
        report["notes"].append(
            "Block-order constraints contain a cycle; falling back to sorted order."
        )
        block_order = sorted(block_roots, key=lambda r: min(comp_to_nodes[r]))

    ordered_blocks: List[List[int]] = []
    waxing_waning: List[int] = []

    for block_root in block_order:
        nodes = sorted(comp_to_nodes[block_root])
        waning_flag = block_waning[block_root]

        order = _topo_sort(nodes, node_edges)
        if order is None:
            if waning_flag == 0:
                report["notes"].append(
                    f"Waxing block {nodes} has cyclic constraints; using fallback order."
                )
            order = _cycle_fallback_order(nodes, recs, n)

        ordered_blocks.append(order)
        waxing_waning.append(waning_flag)

    final_report = report if (report["bad_pairs"] or report["notes"]) else None
    return ordered_blocks, waxing_waning, final_report
