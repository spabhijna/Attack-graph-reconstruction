"""
Enhanced temporal demonstration.
Shows causality checking, time gaps, and sliding windows.
"""
import sys
sys.path.insert(0, 'src')

from log_parser import ingest_logs
from inference import run_inference
from output import explain
from rules import rules
from state import reset_state, state_info
import time


def show_timeline():
    """Display temporal timeline of attack states."""
    print("\n=== Temporal Timeline ===\n")
    
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
            marker = "✓" if event['origin'] == 'log' else "?"
            print(f"T+{elapsed:5d}s [{marker}] {event['state']}")


def demo_good_timeline():
    """Demonstrate attack with good temporal causality."""
    print("\n" + "="*70)
    print("DEMO 1: Proper Temporal Sequence")
    print("="*70)
    print("All preconditions happen BEFORE postconditions")
    print("Reasonable time gaps between steps")
    print("-"*70)
    
    reset_state()
    ingest_logs("logs_temporal_test.jsonl")
    run_inference(rules)
    show_timeline()
    explain()


def demo_missing_evidence():
    """Demonstrate absence-of-evidence with temporal context."""
    print("\n" + "="*70)
    print("DEMO 2: Missing Expected Evidence")
    print("="*70)
    print("System infers credential_dumped:A but no lsass_access observed")
    print("Confidence should be low due to missing evidence")
    print("-"*70)
    
    reset_state()
    ingest_logs("logs.jsonl")  # Only basic logs, no lsass_access
    run_inference(rules)
    show_timeline()
    explain()


if __name__ == "__main__":
    demo_good_timeline()
    demo_missing_evidence()
    
    print("\n" + "="*70)
    print("KEY TEMPORAL FEATURES DEMONSTRATED:")
    print("="*70)
    print("✓ Causality checking: Effects cannot precede causes")
    print("✓ Time gap penalties: Max time between related events")
    print("✓ Absence-of-evidence: Missing expected logs reduce confidence")
    print("✓ Time decay: Older states become less certain")
    print("✓ Timeline visualization: Shows attack progression")
    print("="*70)
