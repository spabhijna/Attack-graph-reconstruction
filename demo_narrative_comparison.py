"""
Enhanced narrative comparison and visualization.
"""
import sys
sys.path.insert(0, 'src')

from log_parser import ingest_logs
from inference import run_inference, infer_missing_steps
from narratives import generate_narrative_variants, compare_narratives
from rules import rules
from state import reset_state, state_info, state_confidence


def visualize_narrative_comparison(narratives):
    """
    Create a visual comparison of narratives.
    """
    print("\n" + "="*70)
    print("NARRATIVE COMPARISON MATRIX")
    print("="*70)
    
    # Get all unique states
    all_states = set()
    for n in narratives:
        all_states.update(n.states)
    
    # Create header
    print(f"\n{'State':<30}", end="")
    for n in narratives[:5]:
        print(f"N{n.id:<4}", end="")
    print()
    print("-" * 70)
    
    # Show each state
    for state in sorted(all_states):
        origin = state_info.get(state, {}).get('origin', '?')
        origin_marker = {
            'log': '✓',
            'inferred': '?',
            'hypothetical': '⚠'
        }.get(origin, '?')
        
        state_display = f"{origin_marker} {state}"[:29]
        print(f"{state_display:<30}", end="")
        
        for n in narratives[:5]:
            if state in n.states:
                conf = n.confidences.get(state, 0)
                if conf >= 0.7:
                    marker = "██"  # High confidence
                elif conf >= 0.5:
                    marker = "▓▓"  # Medium confidence
                elif conf >= 0.3:
                    marker = "▒▒"  # Low confidence
                else:
                    marker = "░░"  # Very low confidence
            else:
                marker = "  "  # Not in narrative
            print(f"{marker:<4}", end="")
        print()
    
    print("\n" + "-" * 70)
    print("Legend: ✓=Observed  ?=Inferred  ⚠=Hypothetical")
    print("        ██=High(0.7+) ▓▓=Med(0.5+) ▒▒=Low(0.3+) ░░=VeryLow")


def show_narrative_tradeoffs(narratives):
    """
    Show the tradeoffs between different narratives.
    """
    print("\n" + "="*70)
    print("NARRATIVE TRADEOFFS")
    print("="*70)
    
    print(f"\n{'Narrative':<15} {'Score':<8} {'States':<8} {'Observed':<10} {'Inferred':<10} {'Hypothetical':<12} {'Complexity':<12}")
    print("-" * 70)
    
    for n in narratives:
        observed = sum(1 for s in n.states if state_info.get(s, {}).get('origin') == 'log')
        inferred = sum(1 for s in n.states if state_info.get(s, {}).get('origin') == 'inferred')
        hypothetical = sum(1 for s in n.states if state_info.get(s, {}).get('origin') == 'hypothetical')
        
        print(f"#{n.id:<14} {n.score:<8.3f} {len(n.states):<8} {observed:<10} {inferred:<10} {hypothetical:<12} {len(n.rules_applied):<12}")
    
    print("\n" + "="*70)
    print("INTERPRETATION")
    print("="*70)
    
    # Find extremes
    max_score_n = max(narratives, key=lambda n: n.score)
    most_complete_n = max(narratives, key=lambda n: len(n.states))
    most_conservative_n = min(narratives, key=lambda n: sum(1 for s in n.states if state_info.get(s, {}).get('origin') != 'log'))
    
    print(f"\n• Highest confidence: Narrative #{max_score_n.id} (score={max_score_n.score:.3f})")
    print(f"  → Best when: You need high certainty")
    
    print(f"\n• Most complete: Narrative #{most_complete_n.id} ({len(most_complete_n.states)} states)")
    print(f"  → Best when: You need full attack picture")
    
    print(f"\n• Most conservative: Narrative #{most_conservative_n.id}")
    print(f"  → Best when: You can't afford false positives")
    
    print("\n" + "="*70)
    print("ANALYST DECISION GUIDE")
    print("="*70)
    print("\nChoose narrative based on your scenario:")
    print("\n1. Incident Response (Active Threat)")
    print("   → Use: Most complete narrative")
    print("   → Reason: Need full attack scope to contain threat")
    
    print("\n2. Forensic Investigation (Post-Mortem)")
    print("   → Use: High-confidence narrative")
    print("   → Reason: Need defensible findings")
    
    print("\n3. Threat Hunting (Proactive)")
    print("   → Use: Most complete narrative")
    print("   → Reason: Better to over-investigate than miss threats")
    
    print("\n4. Compliance Reporting")
    print("   → Use: Conservative narrative")
    print("   → Reason: Only report what you can prove")


def demo_enhanced_narratives():
    """
    Enhanced demonstration of competing narratives.
    """
    print("="*70)
    print("ENHANCED COMPETING NARRATIVES ANALYSIS")
    print("="*70)
    
    reset_state()
    ingest_logs("logs_temporal_test.jsonl")
    run_inference(rules)
    infer_missing_steps(rules)
    
    narratives = generate_narrative_variants(rules, max_variants=5)
    
    # Show visual comparison
    visualize_narrative_comparison(narratives)
    
    # Show tradeoffs
    show_narrative_tradeoffs(narratives)


if __name__ == "__main__":
    demo_enhanced_narratives()
