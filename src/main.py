"""
Attack Graph Reconstruction - Main Entry Point

This system reconstructs attack graphs from security logs using:
- Log parsing and signal extraction
- Rule-based inference with confidence propagation
- Missing-step inference for gap filling
- Competing narratives (multiple explanations)
- Graph visualization
"""
from log_parser import ingest_logs
from inference import run_inference, infer_missing_steps
from output import explain, visualize
from narratives import generate_narrative_variants, explain_competing_narratives
from rules import rules


def main():
    """Main execution flow."""
    # Step 1: Ingest logs and extract initial states
    ingest_logs("logs.jsonl")
    
    # Step 2: Run inference to derive attack chain
    run_inference(rules)
    
    # Step 3: Infer missing steps (hypothetical reconstruction)
    infer_missing_steps(rules)
    
    # Step 4: Generate competing narratives
    narratives = generate_narrative_variants(rules, max_variants=5)
    
    # Step 5: Explain competing narratives (top 3)
    explain_competing_narratives(narratives, top_n=3)
    
    # Step 6: Show detailed view of best narrative
    print("\n" + "="*70)
    print("DETAILED VIEW OF BEST NARRATIVE")
    print("="*70)
    explain()
    
    # Step 7: Visualize the attack graph
    visualize()


if __name__ == "__main__":
    main()
    visualize()


if __name__ == "__main__":
    main()
