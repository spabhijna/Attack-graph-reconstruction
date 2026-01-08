"""
Competing narratives: Generate and rank multiple attack explanations.
"""
import copy
from state import (
    state_info, state_confidence, applied_rules, 
    hypothetical_states, G
)


class AttackNarrative:
    """Represents a single candidate attack explanation."""
    
    def __init__(self, narrative_id, rules_applied, states, confidences):
        self.id = narrative_id
        self.rules_applied = rules_applied
        self.states = states
        self.confidences = confidences
        self.score = 0.0
        self.explanation = ""
        self.calculate_score()
    
    def calculate_score(self):
        """
        Calculate narrative quality score based on:
        - Total confidence of inferred states
        - Number of steps (prefer simpler explanations)
        - Coverage of observed states
        - Hypothetical step penalty
        """
        if not self.states:
            self.score = 0.0
            return
        
        # Average confidence across all states
        avg_confidence = sum(self.confidences.values()) / len(self.confidences)
        
        # Count observed vs inferred vs hypothetical
        observed = sum(1 for s in self.states if state_info.get(s, {}).get('origin') == 'log')
        inferred = sum(1 for s in self.states if state_info.get(s, {}).get('origin') == 'inferred')
        hypothetical = sum(1 for s in self.states if state_info.get(s, {}).get('origin') == 'hypothetical')
        
        # Parsimony: prefer fewer steps
        complexity_penalty = 1.0 / (1.0 + len(self.rules_applied) * 0.1)
        
        # Hypothetical penalty
        hypothetical_penalty = 0.8 ** hypothetical
        
        # Coverage bonus: how much of the observed evidence is explained
        coverage = observed / max(len([s for s, i in state_info.items() if i.get('origin') == 'log']), 1)
        
        # Final score
        self.score = (
            avg_confidence * 0.4 +
            coverage * 0.3 +
            complexity_penalty * 0.2 +
            hypothetical_penalty * 0.1
        )
        
        # Generate explanation
        self.explanation = (
            f"{len(self.rules_applied)} steps, "
            f"{observed} observed, {inferred} inferred, {hypothetical} hypothetical, "
            f"avg_conf={avg_confidence:.2f}"
        )
    
    def __lt__(self, other):
        return self.score > other.score  # Higher score is better


def generate_narrative_variants(rules, max_variants=5):
    """
    Generate multiple competing narratives by exploring different rule application orders
    and optional rule paths.
    """
    narratives = []
    
    # Narrative 1: Current state (all rules applied)
    narrative_1 = AttackNarrative(
        narrative_id=1,
        rules_applied=copy.deepcopy(applied_rules),
        states=set(state_info.keys()),
        confidences=copy.deepcopy(state_confidence)
    )
    narrative_1.explanation = "Full inference chain (all rules applied)"
    narratives.append(narrative_1)
    
    # Narrative 2: Without hypothetical steps (skeptical view)
    non_hypothetical_states = {
        s for s in state_info.keys()
        if state_info[s].get('origin') != 'hypothetical'
    }
    non_hypothetical_confidences = {
        s: c for s, c in state_confidence.items()
        if s in non_hypothetical_states
    }
    narrative_2 = AttackNarrative(
        narrative_id=2,
        rules_applied=[r for r in applied_rules],
        states=non_hypothetical_states,
        confidences=non_hypothetical_confidences
    )
    narrative_2.explanation = "Conservative (no hypothetical steps)"
    narratives.append(narrative_2)
    
    # Narrative 3: High-confidence only (confidence > 0.5)
    high_conf_states = {
        s for s, c in state_confidence.items() if c > 0.5
    }
    high_conf_confidences = {
        s: c for s, c in state_confidence.items() if c > 0.5
    }
    narrative_3 = AttackNarrative(
        narrative_id=3,
        rules_applied=[r for r in applied_rules if r['confidence'] > 0.5],
        states=high_conf_states,
        confidences=high_conf_confidences
    )
    narrative_3.explanation = "High-confidence only (conf > 0.5)"
    narratives.append(narrative_3)
    
    # Narrative 4: Observed + direct inferences only (one level deep)
    direct_states = set()
    for s, info in state_info.items():
        if info.get('origin') == 'log':
            direct_states.add(s)
        elif info.get('origin') == 'inferred':
            # Check if all prerequisites are observed
            derived_from = info.get('evidence', {}).get('derived_from_rule')
            if derived_from:
                # Simple heuristic: if high confidence, likely direct
                if state_confidence.get(s, 0) > 0.3:
                    direct_states.add(s)
    
    narrative_4 = AttackNarrative(
        narrative_id=4,
        rules_applied=[r for r in applied_rules[:2]] if len(applied_rules) >= 2 else applied_rules,
        states=direct_states,
        confidences={s: state_confidence[s] for s in direct_states if s in state_confidence}
    )
    narrative_4.explanation = "Observed + direct inferences only"
    narratives.append(narrative_4)
    
    # Narrative 5: Minimal explanation (observed states only)
    observed_only = {
        s for s, info in state_info.items()
        if info.get('origin') == 'log'
    }
    narrative_5 = AttackNarrative(
        narrative_id=5,
        rules_applied=[],
        states=observed_only,
        confidences={s: state_confidence[s] for s in observed_only if s in state_confidence}
    )
    narrative_5.explanation = "Minimal (observed evidence only)"
    narratives.append(narrative_5)
    
    return sorted(narratives)[:max_variants]


def compare_narratives(narratives):
    """
    Compare narratives and highlight differences.
    Returns comparison data structure.
    """
    comparison = {
        'all_states': set(),
        'narrative_states': {},
        'unique_to_narrative': {},
        'shared_states': set()
    }
    
    # Collect all states across narratives
    for n in narratives:
        comparison['all_states'].update(n.states)
        comparison['narrative_states'][n.id] = n.states
    
    # Find shared states (in all narratives)
    if narratives:
        comparison['shared_states'] = set(narratives[0].states)
        for n in narratives[1:]:
            comparison['shared_states'].intersection_update(n.states)
    
    # Find unique states per narrative
    for n in narratives:
        unique = n.states - comparison['shared_states']
        comparison['unique_to_narrative'][n.id] = unique
    
    return comparison


def explain_competing_narratives(narratives, top_n=3):
    """
    Display competing narratives ranked by score.
    """
    print("\n" + "="*70)
    print("COMPETING ATTACK NARRATIVES")
    print("="*70)
    print("\nMultiple possible explanations ranked by confidence:\n")
    
    for i, narrative in enumerate(narratives[:top_n], 1):
        print(f"{'='*70}")
        print(f"NARRATIVE #{narrative.id} - Score: {narrative.score:.3f}")
        print(f"{'='*70}")
        print(f"Description: {narrative.explanation}")
        print(f"\nStates in this narrative: {len(narrative.states)}")
        
        # Group by origin
        observed = [s for s in narrative.states if state_info.get(s, {}).get('origin') == 'log']
        inferred = [s for s in narrative.states if state_info.get(s, {}).get('origin') == 'inferred']
        hypothetical = [s for s in narrative.states if state_info.get(s, {}).get('origin') == 'hypothetical']
        
        if observed:
            print(f"\n  Observed ({len(observed)}):")
            for s in sorted(observed):
                print(f"    • {s}: {narrative.confidences.get(s, 0):.2f}")
        
        if inferred:
            print(f"\n  Inferred ({len(inferred)}):")
            for s in sorted(inferred, key=lambda x: narrative.confidences.get(x, 0), reverse=True):
                print(f"    • {s}: {narrative.confidences.get(s, 0):.2f}")
        
        if hypothetical:
            print(f"\n  Hypothetical ({len(hypothetical)}):")
            for s in sorted(hypothetical):
                print(f"    • {s}: {narrative.confidences.get(s, 0):.2f}")
        
        print(f"\n  Rules applied: {len(narrative.rules_applied)}")
        for rule in narrative.rules_applied:
            print(f"    → {rule['name']} (tactic: {rule['tactic']})")
        
        print()
    
    # Show comparison
    if len(narratives) > 1:
        comparison = compare_narratives(narratives[:top_n])
        
        print(f"{'='*70}")
        print("NARRATIVE COMPARISON")
        print(f"{'='*70}")
        
        print(f"\nStates shared by all narratives ({len(comparison['shared_states'])}):")
        for s in sorted(comparison['shared_states']):
            print(f"  • {s}")
        
        print(f"\nUnique states per narrative:")
        for nid in sorted(comparison['unique_to_narrative'].keys()):
            unique = comparison['unique_to_narrative'][nid]
            if unique:
                print(f"  Narrative #{nid}: {', '.join(sorted(unique))}")
            else:
                print(f"  Narrative #{nid}: (none)")
        
        print(f"\n{'='*70}")
        print("RECOMMENDATION")
        print(f"{'='*70}")
        best = narratives[0]
        print(f"\nBest narrative: #{best.id}")
        print(f"Score: {best.score:.3f}")
        print(f"Rationale: {best.explanation}")
        print(f"\nThis narrative provides the best balance of:")
        print(f"  • Evidence coverage")
        print(f"  • Confidence levels")
        print(f"  • Explanation simplicity")
        print(f"  • Minimal speculation")
