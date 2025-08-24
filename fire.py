import streamlit as st
from collections import defaultdict
import heapq
import datetime

# ---------------- Library Graph ----------------
ROOMS = [
    "Entrance",
    "ReadingHall",
    "StacksA",
    "StacksB",
    "StacksC",
    "ComputerLab",
    "ChildrenSection",
    "Restrooms",
    "Corridor1",
    "Corridor2",
    "Exit1",
    "Exit2",
]

EDGES = [
    ("Entrance", "Corridor1", 2),
    ("Corridor1", "ReadingHall", 2),
    ("ReadingHall", "StacksA", 1),
    ("StacksA", "StacksB", 1),
    ("StacksB", "StacksC", 1),
    ("Corridor1", "ComputerLab", 2),
    ("ComputerLab", "Corridor2", 1),
    ("Corridor2", "ChildrenSection", 1),
    ("Corridor2", "Restrooms", 1),
    ("Corridor1", "Corridor2", 2),
    ("Corridor1", "Exit1", 1),
    ("Corridor2", "Exit2", 1),
]

def build_graph(edges):
    g = defaultdict(list)
    for u, v, w in edges:
        g[u].append((v, w))
        g[v].append((u, w))
    return g

GRAPH = build_graph(EDGES)

# ---------------- Dijkstra ----------------
def dijkstra_nearest_exit(graph, start, exits, blocked_nodes=None, blocked_edges=None):
    if blocked_nodes is None: blocked_nodes = set()
    if blocked_edges is None: blocked_edges = set()

    if start in blocked_nodes:
        return None, float("inf")

    pq = [(0, start, None)]  # (distance, node, parent)
    dist = {start: 0}
    parent = {start: None}

    def edge_blocked(u, v):
        return (u, v) in blocked_edges or (v, u) in blocked_edges

    visited = set()
    while pq:
        d, u, _ = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)

        if u in exits:
            path = []
            cur = u
            while cur is not None:
                path.append(cur)
                cur = parent[cur]
            path.reverse()
            return path, d

        for v, w in graph.get(u, []):
            if v in blocked_nodes or u in blocked_nodes:
                continue
            if edge_blocked(u, v):
                continue
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                parent[v] = u
                heapq.heappush(pq, (nd, v, u))
    return None, float("inf")

# ---------------- Streamlit UI ----------------
st.title("AI-Driven Fire Safety Evacuation)")
st.write("Simulate a fire in a library and compute shortest evacuation paths using **Dijkstra’s Algorithm**.")

exits = {"Exit1", "Exit2"}

fire_location = st.selectbox("Select Fire Location", ROOMS)
start_room = st.selectbox("Select Your Current Room", ROOMS)

if st.button("Find Safe Path"):
    blocked_nodes = {fire_location}
    path, time_sec = dijkstra_nearest_exit(GRAPH, start_room, exits, blocked_nodes)
    
    if path:
        st.success(f"✅ Recommended Path: {' → '.join(path)}")
        st.info(f"Estimated Evacuation Time: {time_sec} seconds")
    else:
        st.error("❌ No Safe Path Found! Evacuation required by external rescue teams.")

    # Incident Report
    st.subheader("📄 Auto-Generated Fire Incident Report")
    report = f"""
    Fire Incident Report  
    ---------------------  
    🔥 Fire detected at: **{fire_location}**  
    🚶 Evacuation started from: **{start_room}**  
    🕒 Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
    ✅ Suggested Path: {' → '.join(path) if path else 'NO SAFE PATH'}  
    ⏱ Estimated Travel Time: {time_sec if time_sec != float('inf') else 'N/A'} seconds  
    """
    st.text_area("Generated Report", report, height=180)
