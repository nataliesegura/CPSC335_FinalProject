"""glue.py - small helpers that connect the theme data to core.py (same in every theme)."""
import random
import core


def clean_records(records, key):
    """Part 1: index the records by key, report duplicates, keep the first copy."""
    index, dups = core.build_index(records, key)
    return list(index.values()), index, dups


def road_graph(data):
    """Undirected graph: node -> [(neighbor, drive minutes)]."""
    g = {n["id"]: [] for n in data["nodes"]}
    for e in data["edges"]:
        g[e["u"]].append((e["v"], e["minutes"]))
        g[e["v"]].append((e["u"], e["minutes"]))
    return g


def network(data):
    """Part 6: the minimum spanning tree of the link costs = the network we build."""
    nodes = [n["id"] for n in data["nodes"]]
    edges = [(e["u"], e["v"], e["cost"]) for e in data["edges"]]
    tree, total = core.mst_kruskal(nodes, edges)
    g = {n: [] for n in nodes}
    for u, v, c in tree:
        g[u].append((v, c))
        g[v].append((u, c))
    return tree, total, g


def distance_table(graph, places):
    """Shortest drive time between every pair of places (one Dijkstra per place)."""
    return {p: core.dijkstra(graph, p)[0] for p in places}


def doubling_test(kind, sizes, seed=7):
    """Speed report: time one core function while the input size doubles."""
    rng = random.Random(seed)
    rows = []
    for n in sizes:
        if kind == "merge_sort":
            data = [rng.random() for _ in range(n)]
            t = core.time_it(core.merge_sort, data)
        elif kind == "dp_select":
            items = [{"id": i, "weight": rng.randint(1, 20), "value": rng.randint(1, 50)} for i in range(40)]
            t = core.time_it(core.dp_select, items, n)
        elif kind == "kmp_search":
            text = "".join(rng.choice("ab") for _ in range(n))
            t = core.time_it(core.kmp_search, text, "abbab")
        else:
            raise ValueError(kind)
        rows.append({"n": n, "seconds": t})
    for i in range(1, len(rows)):
        rows[i]["ratio vs previous"] = round(rows[i]["seconds"] / rows[i - 1]["seconds"], 2)
    return rows
