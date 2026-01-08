"""
Comprehensive temporal constraint demonstration.
Creates scenarios that show causality violations and time gap penalties.
"""
import sys
sys.path.insert(0, 'src')

import json
import os


# Scenario 1: Short time gaps - everything works well
scenario_1 = [
    {"timestamp": 1641024000, "event_type": "login", "privilege": "user", "host": "A"},
    {"timestamp": 1641024300, "event_type": "smb_session", "src": "A", "dst": "B"},
    {"timestamp": 1641024600, "event_type": "sudo", "host": "A"},
    {"timestamp": 1641024900, "event_type": "lsass_access", "host": "A"},
]

# Scenario 2: Excessive time gaps - should trigger time_gap_exceeded penalty
scenario_2 = [
    {"timestamp": 1641024000, "event_type": "login", "privilege": "user", "host": "A"},
    {"timestamp": 1641024300, "event_type": "smb_session", "src": "A", "dst": "B"},
    {"timestamp": 1641030000, "event_type": "sudo", "host": "A"},  # 1.5 hours later!
]

# Scenario 3: Missing evidence - no lsass_access for credential dump inference
scenario_3 = [
    {"timestamp": 1641024000, "event_type": "login", "privilege": "user", "host": "A"},
    {"timestamp": 1641024300, "event_type": "smb_session", "src": "A", "dst": "B"},
    # No sudo, no lsass_access - system will infer but with low confidence
]


def write_scenario(filename, logs):
    """Write scenario logs to file."""
    with open(filename, 'w') as f:
        for log in logs:
            f.write(json.dumps(log) + '\n')


def run_scenario(name, log_file):
    """Run a scenario and display results."""
    from log_parser import ingest_logs
    from inference import run_inference
    from output import explain
    from rules import rules
    from state import reset_state, state_info
    
    print("\n" + "="*70)
    print(f"SCENARIO: {name}")
    print("="*70)
    
    reset_state()
    ingest_logs(log_file)
    run_inference(rules)
    
    # Show timeline
    print("\n--- Timeline ---")
    events = []
    for state_name, info in state_info.items():
        events.append({
            'time': info['time'],
            'state': state_name,
            'origin': info['origin']
        })
    
    events.sort(key=lambda x: x['time'])
    
    if events:
        start_time = events[0]['time']
        for event in events:
            elapsed = event['time'] - start_time
            marker = "✓ OBS" if event['origin'] == 'log' else "? INF"
            print(f"  T+{elapsed:5d}s [{marker}] {event['state']}")
    
    explain()


if __name__ == "__main__":
    # Write scenarios
    write_scenario("scenario_1_good.jsonl", scenario_1)
    write_scenario("scenario_2_timegap.jsonl", scenario_2)
    write_scenario("scenario_3_missing.jsonl", scenario_3)
    
    # Run demonstrations
    run_scenario("Good Timing - All constraints satisfied", "scenario_1_good.jsonl")
    run_scenario("Excessive Time Gaps - Penalties applied", "scenario_2_timegap.jsonl")
    run_scenario("Missing Evidence - Low confidence", "scenario_3_missing.jsonl")
    
    print("\n" + "="*70)
    print("TEMPORAL REASONING SUMMARY:")
    print("="*70)
    print("✓ Causality Enforcement: Rules cannot fire if timestamps violate causality")
    print("✓ Time Gap Penalties: Excessive delays between steps reduce confidence")
    print("✓ Absence Penalties: Missing expected evidence (e.g., lsass_access) = lower confidence")
    print("✓ Time Decay: Older inferred states become less reliable")
    print("\nThe system now reasons about TIME, not just rule matching.")
    print("="*70)
