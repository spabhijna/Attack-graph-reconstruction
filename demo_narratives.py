"""
Demonstrate competing narratives with rich attack scenarios.
"""
import sys
sys.path.insert(0, 'src')

from log_parser import ingest_logs
from inference import run_inference, infer_missing_steps
from narratives import generate_narrative_variants, explain_competing_narratives
from rules import rules
from state import reset_state


def demo_competing_narratives():
    """
    Demonstrate competing narratives with richer log data.
    """
    print("="*70)
    print("COMPETING NARRATIVES DEMONSTRATION")
    print("="*70)
    print("\nShowing how the system generates and ranks multiple")
    print("possible attack explanations from the same evidence.\n")
    
    reset_state()
    ingest_logs("logs_temporal_test.jsonl")
    run_inference(rules)
    infer_missing_steps(rules)
    
    # Generate competing narratives
    narratives = generate_narrative_variants(rules, max_variants=5)
    
    # Explain them
    explain_competing_narratives(narratives, top_n=5)
    
    print("\n" + "="*70)
    print("KEY INSIGHTS")
    print("="*70)
    print("\n1. Multiple valid explanations exist for the same evidence")
    print("2. Narratives are ranked by:")
    print("   - Confidence levels")
    print("   - Evidence coverage")
    print("   - Simplicity (parsimony)")
    print("   - Amount of speculation")
    print("\n3. Conservative vs. speculative narratives:")
    print("   - Conservative: Observed evidence only")
    print("   - Moderate: Direct inferences")
    print("   - Speculative: Full inference chain + hypotheticals")
    print("\n4. Analysts can compare narratives and choose based on:")
    print("   - Risk tolerance")
    print("   - Investigation goals")
    print("   - Need for certainty vs. completeness")
    print("="*70)


if __name__ == "__main__":
    demo_competing_narratives()
