import networkx as nx
import matplotlib.pyplot as plt
import time

# -------------------------
# Utility
# -------------------------
def now():
    return int(time.time())

# -------------------------
# Initial States
# -------------------------
initial_states = {
    "user_access:A",
    "network_access:A_to_B",
    "vuln_privesc:A",
    "vuln_privesc:B",
    "vuln_lateral:B"
}

state_info = {}

for s in initial_states:
    state_info[s] = {
        "origin": "assumed",
        "evidence": [],
        "event_id": 0,
        "time": now()
    }

# -------------------------
# Rules
# -------------------------
rules = [
    {
        "name": "Privilege Escalation on A",
        "pre": {"user_access:A", "vuln_privesc:A"},
        "post": {"admin_access:A"},
        "confidence": 0.7,
        "tactic": "Privilege Escalation"
    },
    {
        "name": "Credential Dumping on A",
        "pre": {"admin_access:A"},
        "post": {"credential_dumped:A"},
        "confidence": 0.8,
        "tactic": "Credential Access"
    },
    {
        "name": "Lateral Movement A_to_B",
        "pre": {"credential_dumped:A", "network_access:A_to_B", "vuln_lateral:B"},
        "post": {"user_access:B"},
        "confidence": 0.6,
        "tactic": "Lateral Movement"
    },
    {
        "name": "Privilege Escalation on B",
        "pre": {"user_access:B", "vuln_privesc:B"},
        "post": {"admin_access:B"},
        "confidence": 0.7,
        "tactic": "Privilege Escalation"
    }
]

# -------------------------
# Inference Engine
# -------------------------
current_states = set(initial_states)
applied_rules = []          # ORDER MATTERS
event_counter = 0

G = nx.DiGraph()

# add initial state nodes
for s in initial_states:
    G.add_node(s, type="state", origin="assumed")

changed = True
while changed:
    changed = False

    for rule in rules:
        if rule["name"] in [r["name"] for r in applied_rules]:
            continue

        if rule["pre"].issubset(current_states):
            event_counter += 1
            rule_node = f"[RULE] {rule['name']}"

            # add rule node
            G.add_node(
                rule_node,
                type="rule",
                confidence=rule["confidence"],
                tactic=rule["tactic"],
                event_id=event_counter
            )

            # connect preconditions
            for pre in rule["pre"]:
                G.add_edge(pre, rule_node)

            # apply postconditions
            for post in rule["post"]:
                if post not in current_states:
                    current_states.add(post)

                    G.add_node(
                        post,
                        type="state",
                        origin="inferred"
                    )

                    G.add_edge(rule_node, post)

                    state_info[post] = {
                        "origin": "inferred",
                        "evidence": {
                            "derived_from_rule": rule["name"],
                            "supporting_logs": [f"log_{event_counter}"]
                        },
                        "event_id": event_counter,
                        "time": now()
                    }

                    changed = True

            applied_rules.append({
                "name": rule["name"],
                "tactic": rule["tactic"],
                "confidence": rule["confidence"],
                "event_id": event_counter
            })

# -------------------------
# Timeline Construction
# -------------------------
timeline = []

for state, meta in state_info.items():
    timeline.append({
        "state": state,
        "origin": meta["origin"],
        "event_id": meta["event_id"],
        "evidence": meta["evidence"]
    })

timeline = sorted(timeline, key=lambda x: x["event_id"])

# -------------------------
# Explanation
# -------------------------
def explain():
    print("\n=== Reconstructed Attack Narrative ===\n")
    for step in applied_rules:
        print(
            f"[{step['event_id']}] "
            f"{step['name']} "
            f"(Tactic: {step['tactic']}, Confidence: {step['confidence']})"
        )

# -------------------------
# Visualization
# -------------------------
pos = nx.spring_layout(G, seed=42)

state_nodes_assumed = [
    n for n, d in G.nodes(data=True)
    if d.get("type") == "state" and d.get("origin") == "assumed"
]

state_nodes_inferred = [
    n for n, d in G.nodes(data=True)
    if d.get("type") == "state" and d.get("origin") == "inferred"
]

rule_nodes = [
    n for n, d in G.nodes(data=True)
    if d.get("type") == "rule"
]

plt.figure(figsize=(16, 11))

nx.draw_networkx_nodes(
    G, pos,
    nodelist=state_nodes_assumed,
    node_color="#A3D5FF",
    node_shape="o",
    node_size=2600,
    label="Assumed State"
)

nx.draw_networkx_nodes(
    G, pos,
    nodelist=state_nodes_inferred,
    node_color="#7FC97F",
    node_shape="o",
    node_size=2600,
    label="Inferred State"
)

nx.draw_networkx_nodes(
    G, pos,
    nodelist=rule_nodes,
    node_color="#FB8072",
    node_shape="s",
    node_size=3000,
    label="Attack Action"
)

nx.draw_networkx_edges(G, pos, arrows=True)
nx.draw_networkx_labels(G, pos, font_size=9)

plt.title("Attack Graph: Kill Chain Reconstruction")
plt.legend(scatterpoints=1)
plt.axis("off")
plt.show()

# -------------------------
# Run Explanation
# -------------------------
explain()
