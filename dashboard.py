import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import json
import os
import time

st.set_page_config(layout="wide")
st.title("AI-Driven Digital Twin Smart Grid")

# --------------------------
# PATHS
# --------------------------
DATA_DIR = os.path.abspath("data")
FAULT_FILE = os.path.join(DATA_DIR, "fault.json")
MSG_FILE = os.path.join(DATA_DIR, "messages.json")

os.makedirs(DATA_DIR, exist_ok=True)

# --------------------------
# SIDEBAR
# --------------------------
st.sidebar.header("Control Panel")

refresh_rate = st.sidebar.slider("Refresh rate (seconds)", 1, 5, 1)

selected_node = st.sidebar.selectbox(
    "Select Node to Inject Fault",
    list(range(1, 11))
)

if st.sidebar.button("⚡ Trigger Fault"):
    with open(FAULT_FILE, "w") as f:
        json.dump({"node": int(selected_node)}, f)
    st.sidebar.success(f"Fault triggered at Node {selected_node}")

# --------------------------
# GRAPH STRUCTURE
# --------------------------
edges = [
    (1,2),(1,3),(2,4),(3,5),
    (4,6),(5,7),(6,8),
    (7,9),(8,10)
]

G = nx.Graph()
G.add_edges_from(edges)

# stable layout
pos = nx.spring_layout(G, seed=42)

colors = []
labels = {}

# --------------------------
# LOAD NODE DATA
# --------------------------
for node in range(1, 11):

    file = os.path.join(DATA_DIR, f"node_{node}.json")

    if os.path.exists(file):
        try:
            with open(file) as f:
                d = json.load(f)
        except:
            d = {}

        load = d.get("load", 0)
        cap = d.get("capacity", 0)

        # label
        labels[node] = (
            f"N{node}\n"
            f"L:{int(load)}\n"
            f"C:{cap}\n"
            f"{'OVERLOAD' if load > cap else ''}"
        )

        # color logic (STATE-based)
        if load > cap:
            colors.append("red")
        elif load > 0.8 * cap:
            colors.append("orange")
        else:
            colors.append("green")

    else:
        labels[node] = str(node)
        colors.append("gray")

# --------------------------
# LOAD MESSAGE LOG
# --------------------------
log_lines = []

if os.path.exists(MSG_FILE):
    try:
        with open(MSG_FILE) as f:
            log_lines = f.readlines()
    except:
        log_lines = []

# --------------------------
# DRAW GRAPH
# --------------------------
fig, ax = plt.subplots(figsize=(10,6))

nx.draw(
    G,
    pos,
    labels=labels,
    node_color=colors,
    node_size=2000,
    font_size=9,
    ax=ax
)

# --------------------------
# MULTIPLE P2P PACKETS
# --------------------------
recent_msgs = log_lines[-5:]  # last 5 messages

for line in recent_msgs:
    try:
        m = json.loads(line)

        src = m.get("from")
        dst = m.get("to")

        if src in pos and dst in pos:

            x1, y1 = pos[src]
            x2, y2 = pos[dst]

            t = (time.time() % 1)

            xm = x1 + (x2 - x1) * t
            ym = y1 + (y2 - y1) * t

            ax.scatter(xm, ym, s=150)

    except:
        continue

st.pyplot(fig)

# --------------------------
# COMMUNICATION LOG
# --------------------------
st.subheader("P2P Communication Log")

for line in log_lines[-10:][::-1]:
    try:
        m = json.loads(line)

        st.write(
            f"Node {m.get('from')} → Node {m.get('to')} | "
            f"{m.get('action','sync')} | "
            f"Load Sent: {round(m.get('amount',0),2)}"
        )
    except:
        continue

# --------------------------
# DEBUG (helps you confirm refresh)
# --------------------------
st.caption(f"Last refresh: {time.time()}")

# --------------------------
# REFRESH LOOP
# --------------------------
time.sleep(refresh_rate)
st.rerun()