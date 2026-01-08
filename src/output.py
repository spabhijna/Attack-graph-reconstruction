"""
Output generation: explanations and visualizations.
"""
import networkx as nx
import matplotlib.pyplot as plt
import state
from state import G, state_info, state_confidence, applied_rules


def explain():
    """Print human-readable attack narrative with confidence scores."""
    print("\n=== Reconstructed Attack Narrative ===\n")
    for step in applied_rules:
        print(
            f"[{step['event_id']}] {step['name']} "
            f"(Tactic: {step['tactic']}, Confidence: {step['confidence']})"
        )
    
    print("\n=== State Confidence Scores ===\n")
    
    # Separate states by origin type
    observed = []
    inferred = []
    hypothetical = []
    
    for state_name, conf in state_confidence.items():
        origin = state_info[state_name].get('origin', 'unknown')
        if origin == 'log':
            observed.append((state_name, conf))
        elif origin == 'hypothetical':
            hypothetical.append((state_name, conf))
        else:
            inferred.append((state_name, conf))
    
    # Display observed states
    if observed:
        print("Observed (from logs):")
        for state_name, conf in sorted(observed, key=lambda x: x[1], reverse=True):
            print(f"  {state_name}: {conf:.2f}")
    
    # Display inferred states
    if inferred:
        print("\nInferred (via rules):")
        for state_name, conf in sorted(inferred, key=lambda x: x[1], reverse=True):
            evidence = state_info[state_name].get('evidence', {})
            time_gap = evidence.get('time_gap_penalty', 1.0)
            time_gap_violation = evidence.get('time_gap_violation')
            absence = evidence.get('absence_penalty', 1.0)
            decay = evidence.get('time_decay', 1.0)
            negative = evidence.get('negative_penalty', 1.0)
            
            factors = []
            if time_gap_violation == "causality_violation":
                factors.append("CAUSALITY VIOLATION")
            elif time_gap_violation == "time_gap_exceeded":
                factors.append(f"time gap exceeded: {time_gap:.2f}")
            elif time_gap < 1.0:
                factors.append(f"temporal penalty: {time_gap:.2f}")
            
            if absence < 1.0:
                factors.append(f"missing evidence: {absence:.2f}")
            if decay < 1.0:
                factors.append(f"time decay: {decay:.2f}")
            if negative < 1.0:
                factors.append(f"contradicted: {negative:.2f}")
            
            factor_str = f" [{', '.join(factors)}]" if factors else ""
            print(f"  {state_name}: {conf:.2f}{factor_str}")
    
    # Display hypothetical states
    if hypothetical:
        print("\n⚠ Hypothetical (missing-step inference):")
        for state_name, conf in sorted(hypothetical, key=lambda x: x[1], reverse=True):
            if state_name in state.hypothetical_states:
                hyp_info = state.hypothetical_states[state_name]
                print(f"  {state_name}: {conf:.2f}")
                print(f"    → Reason: {hyp_info['reason']}")
                print(f"    → Mechanism: {hyp_info['mechanism']}")
                print(f"    → Status: EXPLICITLY HYPOTHETICAL - LOW CONFIDENCE")
            else:
                # Fallback if not in hypothetical_states dict
                print(f"  {state_name}: {conf:.2f}")
                print(f"    → Status: HYPOTHETICAL (details not available)")
    elif len(state.hypothetical_states) > 0:
        # Debug: hypothetical_states has items but not showing
        print("\n⚠ Hypothetical (missing-step inference):")
        for state_name, hyp_info in state.hypothetical_states.items():
            conf = state_confidence.get(state_name, 0.0)
            print(f"  {state_name}: {conf:.2f}")
            print(f"    → Reason: {hyp_info['reason']}")
            print(f"    → Mechanism: {hyp_info['mechanism']}")
            print(f"    → Status: EXPLICITLY HYPOTHETICAL - LOW CONFIDENCE")


def visualize():
    """Generate and display attack graph visualization."""
    pos = nx.spring_layout(G, seed=42)

    state_nodes_log = [
        n for n, d in G.nodes(data=True)
        if d.get("type") == "state" and d.get("origin") == "log"
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
        nodelist=state_nodes_log,
        node_color="#A3D5FF",
        node_size=2600,
        label="Observed (Logs)"
    )

    nx.draw_networkx_nodes(
        G, pos,
        nodelist=state_nodes_inferred,
        node_color="#7FC97F",
        node_size=2600,
        label="Inferred"
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

    plt.title("Attack Graph: Kill Chain Reconstruction from Logs")
    plt.legend(scatterpoints=1)
    plt.axis("off")
    plt.show()
