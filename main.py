"""main.py - GIVEN. Run every part in the terminal:   python main.py --demo
Parts that are not written yet are reported and skipped."""
import sys

import core
import glue
import theme as T


def demo():
    data = T.load()
    names = {n["id"]: n["name"] for n in data["nodes"]}
    root = data["root"]
    print(f"{T.TITLE} - {T.TAGLINE}\n" + "-" * 70)
    state = {"records": list(data["records"])}

    def part1():
        recs, index, dups = glue.clean_records(data["records"], T.LOOKUP_FIELD)
        state["records"] = recs
        first = recs[0][T.LOOKUP_FIELD]
        print(f"Part 1  Loaded {len(data['records'])} {T.RECORD}s; duplicates skipped: {dups or 'none'}")
        print(f"        Lookup {first}: {T.describe(index[first])}")

    def part2():
        ordered = core.merge_sort(state["records"], key=T.sort_value)
        i = core.lower_bound(ordered, T.to_minutes(T.SEARCH_DEFAULT), key=T.sort_value)
        print(f"Part 2  Sorted by {T.SORT_LABEL.lower()}; binary search for {T.SEARCH_DEFAULT}: "
              f"{len(ordered) - i} match (first at position {i})")

    def heap_of_records():
        h = core.MinHeap()
        for r in state["records"]:
            h.push(T.priority(r), r)
        return h

    def part3():
        h = heap_of_records()
        print(f"Part 3  {T.HEAP_TITLE}:")
        for k in range(3):
            r = h.pop()[1]
            print(f"        {k + 1}. {r[T.ID_FIELD]}  ({T.priority_reason(r)})")

    def part45():
        h = heap_of_records()
        items = T.plan_items([h.pop()[1] for _ in range(min(T.POOL_DEFAULT, len(state["records"])))])
        g = core.greedy_select(items, T.CAPACITY_DEFAULT)
        print(f"Part 4  Greedy {T.PLAN_TITLE.lower()} ({T.CAPACITY_DEFAULT} {T.CAPACITY_UNIT}): "
              f"{T.VALUE_LABEL.lower()} = {g[1]}")
        d = core.dp_select(items, T.CAPACITY_DEFAULT)
        print(f"Part 5  DP     {T.PLAN_TITLE.lower()} ({T.CAPACITY_DEFAULT} {T.CAPACITY_UNIT}): "
              f"{T.VALUE_LABEL.lower()} = {d[1]}  (DP gains {d[1] - g[1]})")

    def part6():
        roads = glue.road_graph(data)
        dist, prev = core.dijkstra(roads, root)
        far = max(dist, key=dist.get)
        print(f"Part 6  Dijkstra: farthest place {names[far]} = {dist[far]} min via "
              + " -> ".join(names[x] for x in core.path_to(prev, far)))
        tree, total, net = glue.network(data)
        print(f"        MST network: {len(tree)} links, total cost {total}")
        u, v, _ = tree[0]
        cut = [n for n in names if n not in core.bfs_reachable(net, root, (u, v))]
        print(f"        BFS: if {names[u]} - {names[v]} breaks, {len(cut)} place(s) are cut off")

    def part7():
        hits = [m["id"] for m in data["messages"]
                if any(core.kmp_search(m["text"].lower(), w.lower()) for w in data["keywords"])]
        print(f"Part 7  KMP scan for {data['keywords']}: {len(hits)} of {len(data['messages'])} flagged")

    def part8():
        roads = glue.road_graph(data)
        stops = []
        for r in state["records"]:
            if r["node"] not in stops and r["node"] != root:
                stops.append(r["node"])
            if len(stops) == 7:
                break
        dm = glue.distance_table(roads, [root] + stops)
        b = core.tour_brute_force(root, stops, dm)
        h = core.tour_heuristic(root, stops, dm)
        print(f"Part 8  Tour of 7 stops: brute force {b[1]} min (exact), heuristic {h[1]} min")

    def speed():
        rows = glue.doubling_test("merge_sort", [4000, 8000, 16000])
        print("Speed   merge_sort doubling test: " + ", ".join(f"n={r['n']}: {r['seconds']:.4f}s" for r in rows))

    for label, step in [("Part 1", part1), ("Part 2", part2), ("Part 3", part3), ("Parts 4-5", part45),
                        ("Part 6", part6), ("Part 7", part7), ("Part 8", part8), ("Speed", speed)]:
        try:
            step()
        except NotImplementedError as e:
            print(f"{label:<10}not implemented yet ({e})")
    print("-" * 70)


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    else:
        print("Usage:  python main.py --demo      (GUI:  streamlit run app.py)")
