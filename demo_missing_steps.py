"""
Demonstrate missing-step inference.
Shows how the system reconstructs steps that must have happened.
"""
import sys
sys.path.insert(0, 'src')

from log_parser import ingest_logs
from inference import run_inference, infer_missing_steps
from output import explain
from rules import rules
from state import reset_state


def demo_missing_step_inference():
    """
    Demonstrate missing-step inference.
    Logs show admin access on A without user access first.
    System should infer that user access must have happened.
    """
    print("="*70)
    print("MISSING-STEP INFERENCE DEMONSTRATION")
    print("="*70)
    print("\nScenario: Logs show admin_access:A but no user_access:A")
    print("Expected: System infers hypothetical user_access:A")
    print("-"*70)
    
    reset_state()
    ingest_logs("logs_missing_steps.jsonl")
    run_inference(rules)
    
    print("\n--- After rule-based inference ---")
    infer_missing_steps(rules)
    
    explain()


def demo_lateral_movement_gap():
    """
    Demonstrate lateral movement gap detection.
    User appears on B without clear lateral movement evidence.
    """
    print("\n\n")
    print("="*70)
    print("LATERAL MOVEMENT GAP DETECTION")
    print("="*70)
    print("\nScenario: user_access:B observed but unclear how attacker got there")
    print("Expected: System infers hypothetical lateral movement")
    print("-"*70)
    
    reset_state()
    # Use original logs - only has user_access:A and network, but infers user_access:B
    ingest_logs("logs.jsonl")
    run_inference(rules)
    infer_missing_steps(rules)
    explain()


if __name__ == "__main__":
    demo_missing_step_inference()
    demo_lateral_movement_gap()
    
    print("\n" + "="*70)
    print("MISSING-STEP INFERENCE: RECONSTRUCTION, NOT REPLAY")
    print("="*70)
    print("\n✓ System detects gaps in attack chain")
    print("✓ Infers hypothetical steps needed to explain evidence")
    print("✓ Marks hypothetical states with low confidence")
    print("✓ Explicitly labels them as HYPOTHETICAL")
    print("\nThis is true attack reconstruction - inferring what must have")
    print("happened even without direct evidence.")
    print("="*70)
