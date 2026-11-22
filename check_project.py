"""check_project.py - GIVEN. Self-check for core.py.   Run:  python check_project.py

Shows which of the 8 parts pass and whether core.py follows the rules.
Take a screenshot of the final summary for your report.
Your instructor runs more tests than these, so also test your own cases."""
import ast
import os
import random
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core  # noqa: E402

R = random.Random(335)


def part1():
    recs = [{"id": "A", "v": 1}, {"id": "B", "v": 2}, {"id": "A", "v": 3}, {"id": "C"}, {"id": "B"}]
    idx, dups = core.build_index(recs, "id")
    assert set(idx) == {"A", "B", "C"}, "index should hold each key once"
    assert idx["A"]["v"] == 1, "keep the FIRST record for a duplicate key"
    assert dups == ["A", "B"], "duplicates should be listed in the order found"
    assert core.build_index([], "id") == ({}, []), "empty input"


def part2():
    for n in (0, 1, 2, 7, 300):
        data = [R.randint(0, 40) for _ in range(n)]
        copy = list(data)
        assert core.merge_sort(data) == sorted(data), f"merge_sort wrong for n={n}"
        assert data == copy, "merge_sort must not change the input list"
    pairs = [(2, "a"), (1, "b"), (2, "c"), (1, "d")]
    assert core.merge_sort(pairs, key=lambda p: p[0]) == [(1, "b"), (1, "d"), (2, "a"), (2, "c")], "must be stable"
    a = [1, 3, 3, 5, 9]
    assert [core.lower_bound(a, t) for t in (0, 1, 3, 4, 9, 10)] == [0, 0, 1, 3, 4, 5], "lower_bound"
    assert core.lower_bound([], 5) == 0, "lower_bound on an empty list"
    words = [{"t": t} for t in (2, 4, 4, 8)]
    assert core.lower_bound(words, 4, key=lambda w: w["t"]) == 1, "lower_bound with key"


def part3():
    h = core.MinHeap()
    vals = [R.randint(0, 99) for _ in range(200)]
    for v in vals:
        h.push(v, f"x{v}")
    assert len(h) == 200
    assert h.peek()[0] == min(vals)
    assert [h.pop()[0] for _ in range(200)] == sorted(vals), "pop order"
    h.push((1, 2), "first"); h.push((1, 2), "second"); h.push((0, 9), "zero")
    assert [h.pop()[1] for _ in range(3)] == ["zero", "first", "second"], "ties: first pushed, first popped"
    for op in (h.pop, h.peek):
        try:
            op()
            raise AssertionError("empty heap must raise IndexError")
        except IndexError:
            pass


ITEMS = [{"id": "a", "weight": 1, "value": 2}, {"id": "b", "weight": 3, "value": 4},
         {"id": "c", "weight": 3, "value": 4}]


def part4():
    ids, val, w = core.greedy_select(ITEMS, 6)
    assert (ids, val, w) == (["a", "b"], 6, 4), f"greedy got {(ids, val, w)}"
    assert core.greedy_select(ITEMS, 0) == ([], 0, 0)
    assert core.greedy_select([], 10) == ([], 0, 0)


def _best(items, cap):
    best = 0
    for mask in range(1 << len(items)):
        w = sum(items[i]["weight"] for i in range(len(items)) if mask >> i & 1)
        if w <= cap:
            best = max(best, sum(items[i]["value"] for i in range(len(items)) if mask >> i & 1))
    return best


def part5():
    ids, val, w = core.dp_select(ITEMS, 6)
    assert val == 8 and sorted(ids) == ["b", "c"] and w == 6, f"dp got {(ids, val, w)}"
    for _ in range(25):
        items = [{"id": i, "weight": R.randint(1, 9), "value": R.randint(1, 30)} for i in range(R.randint(1, 10))]
        cap = R.randint(0, 25)
        ids, val, w = core.dp_select(items, cap)
        assert val == _best(items, cap), "dp_select is not optimal"
        chosen = [it for it in items if it["id"] in set(ids)]
        assert sum(it["value"] for it in chosen) == val and sum(it["weight"] for it in chosen) == w <= cap


G = {"A": [("B", 1), ("C", 5)], "B": [("A", 1), ("C", 1), ("D", 7)], "C": [("A", 5), ("B", 1), ("D", 2)],
     "D": [("B", 7), ("C", 2)], "E": []}


def part6():
    assert core.bfs_reachable(G, "A") == {"A": 0, "B": 1, "C": 1, "D": 2}, "bfs hops"
    assert core.bfs_reachable(G, "A", blocked_edge=("C", "A")) == {"A": 0, "B": 1, "C": 2, "D": 2}, "blocked edge"
    dist, prev = core.dijkstra(G, "A")
    assert dist == {"A": 0, "B": 1, "C": 2, "D": 4}, f"dijkstra distances {dist}"
    assert core.path_to(prev, "D") == ["A", "B", "C", "D"], "dijkstra prev / path"
    tree, total = core.mst_kruskal(["A", "B", "C", "D"],
                                   [("A", "B", 4), ("B", "C", 1), ("A", "C", 3), ("C", "D", 2), ("B", "D", 5)])
    assert total == 6 and len(tree) == 3, f"mst got {tree}, {total}"
    _, total2 = core.mst_kruskal(["A", "B", "X"], [("A", "B", 2)])
    assert total2 == 2, "mst of a disconnected graph = a forest"


def part7():
    assert core.kmp_search("aaaa", "aa") == [0, 1, 2], "overlapping matches"
    assert core.kmp_search("line down, line down", "line down") == [0, 11]
    assert core.kmp_search("abc", "") == [] and core.kmp_search("", "a") == []
    for _ in range(50):
        t = "".join(R.choice("ab") for _ in range(60))
        p = "".join(R.choice("ab") for _ in range(R.randint(1, 4)))
        expect = [i for i in range(len(t) - len(p) + 1) if t[i:i + len(p)] == p]
        assert core.kmp_search(t, p) == expect, "kmp_search positions"


def part8():
    pts = {i: (R.random() * 10, R.random() * 10) for i in range(8)}
    d = {a: {b: round(((pts[a][0] - pts[b][0]) ** 2 + (pts[a][1] - pts[b][1]) ** 2) ** 0.5, 3) for b in pts} for a in pts}
    order, cost = core.tour_brute_force(0, list(range(1, 7)), d)
    assert order[0] == 0 and sorted(order) == list(range(7)), "tour must start at start and visit each stop once"
    assert abs(cost - core.tour_cost(order, d)) < 1e-6
    best = min(core.tour_cost([0, *p], d) for p in __import__("itertools").permutations(range(1, 7)))
    assert abs(cost - best) < 1e-6, "brute force is not optimal"
    h_order, h_cost = core.tour_heuristic(0, list(range(1, 7)), d)
    assert h_order[0] == 0 and sorted(h_order) == list(range(7)) and h_cost >= best - 1e-6
    assert h_cost <= best * 1.25, "heuristic tour is far from optimal - check 2-opt"
    assert core.tour_brute_force(0, [], d) == ([0], 0)


BANNED_CALLS = {"sorted"}
BANNED_METHODS = {"sort", "find", "index", "count", "rfind"}
BANNED_MODULES = {"heapq", "bisect", "re"}


def rules():
    tree = ast.parse(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "core.py")).read())
    found = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mods = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            found += [f"import {m} (line {node.lineno})" for m in mods if m.split(".")[0] in BANNED_MODULES]
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name) and f.id in BANNED_CALLS:
                found.append(f"{f.id}() (line {node.lineno})")
            if isinstance(f, ast.Attribute) and f.attr in BANNED_METHODS:
                found.append(f".{f.attr}() (line {node.lineno})")
    return found


if __name__ == "__main__":
    print("CPSC 335 Final Project - self-check of core.py\n" + "-" * 60)
    parts = [("Part 1  build_index", part1), ("Part 2  merge_sort, lower_bound", part2),
             ("Part 3  MinHeap", part3), ("Part 4  greedy_select", part4), ("Part 5  dp_select", part5),
             ("Part 6  bfs_reachable, dijkstra, mst_kruskal", part6), ("Part 7  kmp_search", part7),
             ("Part 8  tour_brute_force, tour_heuristic", part8)]
    passed = 0
    for name, fn in parts:
        try:
            fn()
            print(f"PASS          {name}")
            passed += 1
        except NotImplementedError as e:
            print(f"NOT STARTED   {name}  ({e})")
        except Exception as e:
            msg = str(e) or type(e).__name__
            line = traceback.extract_tb(e.__traceback__)[-1].lineno
            print(f"FAIL          {name}  ->  {msg}  (check_project.py line {line})")
    bad = rules()
    print("-" * 60)
    print("Rules check:  " + ("OK - no built-in shortcuts found" if not bad else "PROBLEM - remove: " + ", ".join(bad)))
    print(f"Summary:      {passed} of 8 parts pass the self-check")
