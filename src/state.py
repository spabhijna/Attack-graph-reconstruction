"""
Global state management for attack graph reconstruction.
"""
import networkx as nx
import time

# Graph structure
G = nx.DiGraph()

# State tracking
state_info = {}
state_confidence = {}  # Confidence score per state
current_states = set()

# Evidence tracking
observed_logs = []  # All logs for absence-of-evidence checking
negative_evidence = {}  # States with contradicting evidence

# Rule tracking
applied_rules = []

# Hypothetical inference tracking
hypothetical_states = {}  # States inferred without direct evidence

# Event counter
event_counter = 0


def now():
    """Return current Unix timestamp."""
    return int(time.time())


def reset_state():
    """Reset all global state (useful for testing)."""
    global G, state_info, state_confidence, current_states, applied_rules, event_counter
    global observed_logs, negative_evidence, hypothetical_states
    G = nx.DiGraph()
    state_info = {}
    state_confidence = {}
    current_states = set()
    applied_rules = []
    event_counter = 0
    observed_logs = []
    negative_evidence = {}
    hypothetical_states = {}
