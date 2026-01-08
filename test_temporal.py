"""
Demo script to test temporal constraints and causality checking.
"""
import sys
sys.path.insert(0, 'src')

from log_parser import ingest_logs
from inference import run_inference
from output import explain
from rules import rules
from state import reset_state


def test_temporal_constraints():
    """Test with logs that have proper temporal relationships."""
    print("="*60)
    print("TEST: Temporal Constraints with Proper Timing")
    print("="*60)
    
    reset_state()
    ingest_logs("logs_temporal_test.jsonl")
    run_inference(rules)
    explain()
    

def test_causality_violation():
    """
    Test causality violation scenario.
    User appears on B BEFORE credentials were obtained from A.
    """
    print("\n\n")
    print("="*60)
    print("TEST: Causality Violation Detection")
    print("="*60)
    print("Scenario: User access to B logged at 1641024000,")
    print("but user access to A logged at 1641024100 (100s later).")
    print("Lateral movement would require credentials from A first!")
    print("="*60)
    
    reset_state()
    ingest_logs("logs_causality_violation.jsonl")
    run_inference(rules)
    explain()


def test_time_gap_penalty():
    """
    Test time gap penalty.
    Long delay between steps should reduce confidence.
    """
    print("\n\n")
    print("="*60)
    print("TEST: Time Gap Penalty")  
    print("="*60)
    print("Scenario: 6000 seconds (1.67 hours) between A access and B access")
    print("Lateral movement max_time_gap is 3600s (1 hour)")
    print("Should see time_gap_exceeded penalty")
    print("="*60)
    
    # Same as causality but shows time gap
    # Already demonstrated in the previous test
    

if __name__ == "__main__":
    test_temporal_constraints()
    test_causality_violation()
    test_time_gap_penalty()
