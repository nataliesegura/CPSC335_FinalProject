"""app.py - Streamlit GUI (GIVEN). Run:  streamlit run app.py
Each tab calls your functions in core.py. A tab shows "Not implemented yet"
until the function it needs works. You may improve the look of this app."""
import html

import altair as alt
import pandas as pd
import streamlit as st

import core
import glue
import theme as T

st.set_page_config(page_title=T.TITLE, layout="wide")


@st.cache_data
def load():
    return T.load()


data = load()
names = {n["id"]: n["name"] for n in data["nodes"]}
pos = {n["id"]: (n["x"], n["y"]) for n in data["nodes"]}


def todo(err):
    """Shown in a tab until the core.py function it needs is written."""
    st.info(f"Not implemented yet: **{err}** in core.py. Write it, save the file, "
            "and this tab updates (press R in the browser if it does not).")


part1_ready = True
try:
    records, index, dups = glue.clean_records(data["records"], T.LOOKUP_FIELD)
except NotImplementedError:
    part1_ready = False          # Part 1 not written yet: show raw records
    records, dups = list(data["records"]), []
    index = {}
    for r in records:
        index.setdefault(r[T.LOOKUP_FIELD], r)
roads = glue.road_graph(data)
root = data["root"]

st.title(T.TITLE)
st.caption(T.TAGLINE + " · CPSC 335 Algorithm Engineering · simulated data")
c1, c2, c3, c4 = st.columns(4)
c1.metric(f"{T.RECORD.capitalize()}s loaded", len(data["records"]))
c2.metric("Duplicates removed", len(dups))
c3.metric("Places on the map", len(data["nodes"]))
c4.metric("Road links", len(data["edges"]))


def map_chart(path_nodes=(), path_edges=(), dim_nodes=(), title=""):
    """Draw the city: grey links, highlighted links in orange, the root as a square."""
    hi = {tuple(sorted(e)) for e in path_edges}
    rows = []
    for k, e in enumerate(data["edges"]):
        on = tuple(sorted((e["u"], e["v"]))) in hi
        for end in (e["u"], e["v"]):
            rows.append({"edge": k, "x": pos[end][0], "y": pos[end][1], "on": on})
    edf = pd.DataFrame(rows)
    ndf = pd.DataFrame([{"id": n, "name": names[n], "x": pos[n][0], "y": pos[n][1],
                         "status": ("root" if n == root else "cut off" if n in dim_nodes
                                    else "on route" if n in path_nodes else "place")}
                        for n in names])
    base = alt.Chart(edf).mark_line(strokeWidth=1.5, color="#c9ced6").encode(
        x=alt.X("x:Q", axis=None), y=alt.Y("y:Q", axis=None), detail="edge:N")
    lit = alt.Chart(edf[edf["on"]]).mark_line(strokeWidth=4, color="#f08c00").encode(
        x="x:Q", y="y:Q", detail="edge:N")
    pts = alt.Chart(ndf).mark_point(filled=True, size=140).encode(
        x="x:Q", y="y:Q", tooltip=["name", "status"],
        shape=alt.Shape("status:N", legend=None,
                        scale=alt.Scale(domain=["root", "on route", "place", "cut off"],
                                        range=["square", "circle", "circle", "cross"])),
        color=alt.Color("status:N", legend=alt.Legend(orient="bottom", title=None),
                        scale=alt.Scale(domain=["root", "on route", "place", "cut off"],
                                        range=["#1c3d6e", "#f08c00", "#5c7cfa", "#e03131"])))
    labels = alt.Chart(ndf).mark_text(dy=-11, fontSize=10, color="#495057").encode(
        x="x:Q", y="y:Q", text="name:N")
    return (base + lit + pts + labels).properties(height=430, title=title)


tabs = st.tabs(["1 · Records & lookup", "2 · Sort & search", "3 · Priority queue",
                "4–5 · Greedy vs DP", "6 · Routes & network", "7 · Text scan",
                "8 · Route optimizer", "Speed report"])

# ---------------------------------------------------------------- Part 1
with tabs[0]:
    try:
        if not part1_ready:
            raise NotImplementedError("Part 1: build_index")
        st.subheader(f"Part 1 · Hash-table lookup by {T.LOOKUP_LABEL}")
        st.write(f"`build_index` stores every {T.RECORD} in a dictionary keyed by **{T.LOOKUP_LABEL}**, "
                 "so a lookup takes expected O(1) time instead of scanning the whole list.")
        if dups:
            st.warning(f"Duplicate {T.LOOKUP_LABEL} found and skipped: {', '.join(dups)}")
        key = st.selectbox(T.LOOKUP_LABEL, list(index.keys()))
        st.success(T.describe(index[key]))
        st.dataframe(pd.DataFrame(records)[T.COLUMNS], width="stretch", hide_index=True)
    except NotImplementedError as e:
        todo(e)

# ---------------------------------------------------------------- Part 2
with tabs[1]:
    try:
        st.subheader(f"Part 2 · Merge sort by {T.SORT_LABEL.lower()}, then binary search")
        ordered = core.merge_sort(records, key=T.sort_value)
        q = st.text_input(T.SEARCH_PROMPT, T.SEARCH_DEFAULT)
        try:
            target = T.to_minutes(q)
            i = core.lower_bound(ordered, target, key=T.sort_value)
            st.info(f"Binary search: the first match is at position **{i}** of {len(ordered)} "
                    f"(about {max(1, len(ordered)).bit_length()} comparisons instead of {len(ordered)}). "
                    f"**{len(ordered) - i}** {T.RECORD}s match.")
            df = pd.DataFrame(ordered)[T.COLUMNS]
            df.insert(0, "match", ["" if k < i else "yes" for k in range(len(df))])
            st.dataframe(df, width="stretch", hide_index=True)
        except ValueError:
            st.error("Please type the value in the format shown.")
    except NotImplementedError as e:
        todo(e)

# ---------------------------------------------------------------- Part 3
with tabs[2]:
    try:
        st.subheader("Part 3 · " + T.HEAP_TITLE)
        st.caption(T.HEAP_RULE)
        k = st.slider("How many to pop from the heap", 1, len(records), 8)
        heap = core.MinHeap()
        for r in records:
            heap.push(T.priority(r), r)
        popped = []
        for rank in range(1, k + 1):
            _p, r = heap.pop()
            popped.append({"order": rank, T.ID_FIELD: r[T.ID_FIELD], "why": T.priority_reason(r)})
        st.dataframe(pd.DataFrame(popped), width="stretch", hide_index=True)
        st.caption(f"Each push and pop is O(log n). Still waiting in the heap: {len(heap)}.")
    except NotImplementedError as e:
        todo(e)

# ---------------------------------------------------------------- Parts 4-5
with tabs[3]:
    try:
        st.subheader("Parts 4–5 · " + T.PLAN_TITLE + ": greedy vs dynamic programming")
        cap = st.slider(f"{T.CAPACITY_LABEL} ({T.CAPACITY_UNIT})", T.CAPACITY_MIN, T.CAPACITY_MAX, T.CAPACITY_DEFAULT)
        pool_size = st.slider(f"Candidates to consider (top of the priority list)", 5, len(records), min(T.POOL_DEFAULT, len(records)))
        heap = core.MinHeap()
        for r in records:
            heap.push(T.priority(r), r)
        pool = [heap.pop()[1] for _ in range(pool_size)]
        items = T.plan_items(pool)
        g_ids, g_val, g_w = core.greedy_select(items, cap)
        d_ids, d_val, d_w = core.dp_select(items, cap)
        a, b = st.columns(2)
        a.metric(f"Greedy · {T.VALUE_LABEL.lower()}", g_val, help=f"uses {g_w} of {cap} {T.CAPACITY_UNIT}")
        b.metric(f"DP (optimal) · {T.VALUE_LABEL.lower()}", d_val, delta=d_val - g_val,
                 help=f"uses {d_w} of {cap} {T.CAPACITY_UNIT}")
        if d_val > g_val:
            st.warning(f"Greedy (best value per {T.CAPACITY_UNIT[:-1] if T.CAPACITY_UNIT.endswith('s') else T.CAPACITY_UNIT} first) "
                       f"misses {d_val - g_val} {T.VALUE_LABEL.lower()}. Dynamic programming checks every capacity and finds the best mix.")
        else:
            st.success("Here greedy happens to match the optimal answer. Move the sliders to find a case where it does not.")
        df = pd.DataFrame(items).rename(columns={"weight": T.WEIGHT_LABEL, "value": T.VALUE_LABEL})
        df["greedy"] = ["yes" if i in set(g_ids) else "" for i in df["id"]]
        df["DP"] = ["yes" if i in set(d_ids) else "" for i in df["id"]]
        st.dataframe(df, width="stretch", hide_index=True)
    except NotImplementedError as e:
        todo(e)

# ---------------------------------------------------------------- Part 6
with tabs[4]:
    try:
        st.subheader("Part 6 · Graphs: shortest routes, the network, and failures")
        mode = st.radio("Show", ["Shortest route (Dijkstra)", f"{T.NETWORK_TITLE} (MST)", "Failure check (BFS)"],
                        horizontal=True)
        if mode.startswith("Shortest"):
            dest = st.selectbox("Destination", [n for n in names if n != root], format_func=lambda n: names[n])
            dist, prev = core.dijkstra(roads, root)
            p = core.path_to(prev, dest)
            st.info(f"Fastest route from {names[root]} to {names[dest]}: **{dist[dest]} min** "
                    f"({T.ROAD_LABEL}) via {' → '.join(names[x] for x in p)}")
            st.altair_chart(map_chart(p, list(zip(p, p[1:]))), width="stretch")
        else:
            tree, total, net = glue.network(data)
            if "MST" in mode:
                st.info(f"{T.MST_TEXT} Total: **{total}** using {len(tree)} of {len(data['edges'])} links.")
                st.altair_chart(map_chart([u for u, _, _ in tree], [(u, v) for u, v, _ in tree]),
                                width="stretch")
            else:
                st.write(T.BREAK_TEXT)
                label = {f"{names[u]} — {names[v]}": (u, v) for u, v, _ in tree}
                pick = st.selectbox("Broken link", list(label))
                reach = core.bfs_reachable(net, root, blocked_edge=label[pick])
                cut = [n for n in names if n not in reach]
                st.error(f"BFS from {names[root]}: **{len(cut)}** place(s) cut off: "
                         + ", ".join(names[n] for n in cut))
                st.altair_chart(map_chart([], [(u, v) for u, v, _ in tree if (u, v) != label[pick]], cut),
                                width="stretch")
    except NotImplementedError as e:
        todo(e)

# ---------------------------------------------------------------- Part 7
with tabs[5]:
    try:
        st.subheader("Part 7 · " + T.TEXT_TITLE + " (KMP)")
        st.caption(T.TEXT_HELP)
        kws = st.multiselect("Words to look for", data["keywords"], default=data["keywords"])
        extra = st.text_input("Add another word or phrase (optional)")
        if extra.strip():
            kws = kws + [extra.strip()]
        flagged = 0
        for m in data["messages"]:
            text, low = m["text"], m["text"].lower()
            marks = [False] * len(text)
            found = []
            for w in kws:
                hits = core.kmp_search(low, w.lower())
                if hits:
                    found.append(w)
                for h in hits:
                    for j in range(h, h + len(w)):
                        marks[j] = True
            out, j = [], 0
            while j < len(text):
                k2 = j
                while k2 < len(text) and marks[k2] == marks[j]:
                    k2 += 1
                seg = html.escape(text[j:k2])
                out.append(f"<mark style='background:#ffd8a8'>{seg}</mark>" if marks[j] else seg)
                j = k2
            flagged += bool(found)
            tag = f"<b style='color:#c92a2a'>FLAG</b> " if found else ""
            st.markdown(f"{tag}<code>{m['id']}</code> {''.join(out)}", unsafe_allow_html=True)
        st.caption(f"{flagged} of {len(data['messages'])} flagged. KMP never re-reads a character of the text, so each scan is O(n + m).")
    except NotImplementedError as e:
        todo(e)

# ---------------------------------------------------------------- Part 8
with tabs[6]:
    try:
        st.subheader("Part 8 · " + T.TOUR_TITLE)
        st.caption(T.TOUR_TEXT)
        heap = core.MinHeap()
        for r in records:
            heap.push(T.priority(r), r)
        default = []
        while len(heap) and len(default) < 7:
            n = heap.pop()[1]["node"]
            if n not in default and n != root:
                default.append(n)
        stops = st.multiselect("Stops (exact brute force runs only up to 9 stops)", [n for n in names if n != root],
                               default=default, format_func=lambda n: names[n])
        if stops:
            dist = glue.distance_table(roads, [root] + stops)
            h_order, h_cost = core.tour_heuristic(root, stops, dist)
            a, b = st.columns(2)
            a.metric("Heuristic: nearest neighbor + 2-opt", f"{h_cost} min")
            if len(stops) <= 9:
                t = core.time_it(core.tour_brute_force, root, stops, dist, repeat=1)
                b_order, b_cost = core.tour_brute_force(root, stops, dist)
                b.metric(f"Brute force: all {len(stops)}! orders", f"{b_cost} min",
                         delta=f"{h_cost - b_cost} min better than heuristic" if h_cost > b_cost else "heuristic found the optimum",
                         delta_color="off", help=f"took {t:.3f} s")
            else:
                b.metric("Brute force", "too slow", help="10! = 3.6 million orders, and it grows fast")
            legs = []
            for x, y in zip(h_order, h_order[1:] + h_order[:1]):
                legs += list(zip(core.path_to(core.dijkstra(roads, x)[1], y), core.path_to(core.dijkstra(roads, x)[1], y)[1:]))
            st.write("Heuristic route: " + " → ".join(names[x] for x in h_order + h_order[:1]))
            st.altair_chart(map_chart(h_order, legs), width="stretch")
    except NotImplementedError as e:
        todo(e)

# ---------------------------------------------------------------- Speed report
with tabs[7]:
    try:
        st.subheader("Speed report · the doubling test")
        st.write("Double the input size and watch the time. Ratio about 2 → linear (or n log n); "
                 "about 4 → quadratic. For DP the size is the capacity, so the time grows linearly in it.")
        kind = st.selectbox("Function", ["merge_sort", "dp_select", "kmp_search"])
        sizes = {"merge_sort": [2000, 4000, 8000, 16000, 32000],
                 "dp_select": [250, 500, 1000, 2000, 4000],
                 "kmp_search": [20000, 40000, 80000, 160000, 320000]}[kind]
        if st.button("Run doubling test"):
            rows = glue.doubling_test(kind, sizes)
            df = pd.DataFrame(rows)
            st.dataframe(df, width="stretch", hide_index=True)
            st.altair_chart(alt.Chart(df).mark_line(point=True, color="#f08c00").encode(
                x=alt.X("n:Q", title="input size n"), y=alt.Y("seconds:Q", title="seconds")).properties(height=300),
                width="stretch")
    except NotImplementedError as e:
        todo(e)
