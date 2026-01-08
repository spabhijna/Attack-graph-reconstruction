"""
Log parsing and signal extraction.
"""
import json
from state import G, state_info, state_confidence, current_states, event_counter


def read_logs(path):
    """Generator to read logs from JSONL file."""
    with open(path) as f:
        for line in f:
            yield json.loads(line)


def extract_signals(log):
    """Extract security signals from a log entry."""
    signals = []

    if log["event_type"] == "login" and log.get("privilege") == "user":
        signals.append(f"user_access:{log['host']}")

    if log["event_type"] == "sudo":
        signals.append(f"admin_access:{log['host']}")

    if log["event_type"] == "lsass_access":
        signals.append(f"credential_dumped:{log['host']}")

    if log["event_type"] == "smb_session":
        signals.append(f"network_access:{log['src']}_to_{log['dst']}")

    return signals


def extract_negative_signals(log):
    """Extract negative signals that contradict attack hypotheses."""
    negative = []

    # Failed login contradicts access
    if log["event_type"] == "login_failed":
        negative.append(f"user_access:{log.get('host')}")

    # Logout/session end contradicts continued access
    if log["event_type"] == "logout":
        negative.append(f"user_access:{log.get('host')}")
        negative.append(f"admin_access:{log.get('host')}")

    # Security tools detecting/blocking
    if log["event_type"] == "edr_block":
        negative.append(f"credential_dumped:{log.get('host')}")

    # Network isolation
    if log["event_type"] == "firewall_block":
        src = log.get('src')
        dst = log.get('dst')
        if src and dst:
            negative.append(f"network_access:{src}_to_{dst}")

    return negative


def ingest_logs(path):
    """
    Ingest logs and populate initial states.
    Observed states have full confidence (1.0).
    Tracks negative evidence and all logs for reasoning.
    """
    import state
    global event_counter

    for log in read_logs(path):
        # Track all logs for absence-of-evidence checking
        state.observed_logs.append(log)

        # Extract positive and negative signals
        signals = extract_signals(log)
        negative = extract_negative_signals(log)

        # Record negative evidence
        for neg_state in negative:
            if neg_state not in state.negative_evidence:
                state.negative_evidence[neg_state] = []
            state.negative_evidence[neg_state].append(log)

        for s in signals:
            if s not in state_info:
                event_counter += 1

                state_info[s] = {
                    "origin": "log",
                    "evidence": [log],
                    "event_id": event_counter,
                    "time": log["timestamp"]
                }

                # Observed states have full confidence
                state_confidence[s] = 1.0

                current_states.add(s)

                G.add_node(s, type="state", origin="log", confidence=1.0)
