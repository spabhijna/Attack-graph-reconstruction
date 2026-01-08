"""Inference engine for attack graph reconstruction with evidence reasoning."""
import time
import state
from state import (
    G, state_info, state_confidence, current_states, 
    applied_rules, now
)

# Expected evidence for each state type
EXPECTED_EVIDENCE = {
    "credential_dumped": ["lsass_access", "proc_dump"],
    "admin_access": ["sudo", "privilege_escalation"],
    "network_access": ["smb_session", "rdp_session"],
}

# Time decay parameters (seconds)
TIME_DECAY_HALF_LIFE = 3600  # 1 hour - confidence halves


def check_absence_of_evidence(state_name, state_time):
    """
    Check if expected evidence is missing for an inferred state.
    Returns confidence penalty (0.0 to 1.0).
    """
    # Extract state type (e.g., "credential_dumped" from "credential_dumped:A")
    state_type = state_name.split(":")[0]
    
    if state_type not in EXPECTED_EVIDENCE:
        return 1.0  # No penalty if we don't expect specific evidence
    
    # Extract host from state
    host = state_name.split(":")[1] if ":" in state_name else None
    
    # Check if any expected evidence type appears in logs
    expected_types = EXPECTED_EVIDENCE[state_type]
    found_evidence = False
    
    for log in state.observed_logs:
        if log["event_type"] in expected_types:
            # Check if it's for the same host
            if host and log.get("host") == host:
                found_evidence = True
                break
    
    if not found_evidence:
        # Absence of evidence: reduce confidence significantly
        return 0.5  # 50% penalty
    
    return 1.0  # No penalty


def calculate_time_decay(state_time):
    """
    Calculate time decay factor for state confidence.
    Older states are less reliable.
    """
    current_time = now()
    age = current_time - state_time
    
    # Exponential decay: confidence = 0.5^(age / half_life)
    decay_factor = 0.5 ** (age / TIME_DECAY_HALF_LIFE)
    
    # Floor at 0.3 to avoid complete loss of confidence
    return max(decay_factor, 0.3)


def apply_negative_evidence_penalty(state_name):
    """
    Apply penalty if negative evidence contradicts this state.
    """
    if state_name in state.negative_evidence:
        # Each negative evidence reduces confidence
        penalty = 0.8 ** len(state.negative_evidence[state_name])
        return penalty
    return 1.0


def check_temporal_causality(rule, precondition_states):
    """
    Verify temporal causality: all preconditions must exist before postcondition.
    Returns (is_valid, latest_precondition_time).
    """
    precondition_times = []
    
    for pre_state in precondition_states:
        if pre_state in state_info:
            precondition_times.append(state_info[pre_state]["time"])
        else:
            # Precondition doesn't exist - shouldn't happen but handle gracefully
            return False, 0
    
    if not precondition_times:
        return False, 0
    
    # Latest precondition time is the earliest this rule could fire
    latest_pre_time = max(precondition_times)
    
    return True, latest_pre_time


def calculate_time_gap_penalty(rule, precondition_time, current_time):
    """
    Calculate penalty based on time gap between preconditions and postcondition.
    Longer gaps reduce confidence based on tactic-specific max time gaps.
    """
    time_gap = current_time - precondition_time
    max_gap = rule.get("max_time_gap", float('inf'))
    
    if time_gap < 0:
        # Causality violation: effect before cause
        return 0.0, "causality_violation"
    
    if time_gap > max_gap:
        # Too much time passed - exponential decay beyond max
        excess_time = time_gap - max_gap
        penalty = 0.5 ** (excess_time / max_gap)
        return max(penalty, 0.1), "time_gap_exceeded"
    
    # Within acceptable range - linear decay
    penalty = 1.0 - (0.3 * time_gap / max_gap)
    return max(penalty, 0.7), None


def get_sliding_window_states(window_size=7200):
    """
    Get states within a sliding time window (default 2 hours).
    Returns states that are temporally relevant.
    """
    current_time = now()
    recent_states = set()
    
    for state_name, info in state_info.items():
        state_time = info["time"]
        if current_time - state_time <= window_size:
            recent_states.add(state_name)
    
    return recent_states


def run_inference(rules):
    """
    Run inference to derive new states from rules with temporal constraints.
    Enforces causality: effects cannot precede causes.
    Applies time gap penalties based on tactic-specific thresholds.
    """
    changed = True
    while changed:
        changed = False

        for rule in rules:
            if rule["name"] in [r["name"] for r in applied_rules]:
                continue

            if rule["pre"].issubset(current_states):
                # Check temporal causality
                is_valid, precondition_time = check_temporal_causality(rule, rule["pre"])
                
                if not is_valid:
                    continue  # Skip this rule - causality violated
                
                # Calculate when this rule could fire (after all preconditions)
                inferred_time = max(precondition_time, now())
                
                # Check if this would violate causality with existing evidence
                # (e.g., credentials appeared after access was already established)
                causality_violated = False
                for post in rule["post"]:
                    if post in state_info:
                        existing_time = state_info[post]["time"]
                        if existing_time < precondition_time:
                            # Evidence shows effect before cause - causality violation
                            causality_violated = True
                            break
                
                if causality_violated:
                    continue  # Skip this rule
                
                event_counter = state_info[list(state_info.keys())[-1]]["event_id"] + 1 if state_info else 1
                rule_node = f"[RULE] {rule['name']}"

                G.add_node(
                    rule_node,
                    type="rule",
                    confidence=rule["confidence"],
                    tactic=rule["tactic"],
                    event_id=event_counter
                )

                for pre in rule["pre"]:
                    G.add_edge(pre, rule_node)

                for post in rule["post"]:
                    if post not in current_states:
                        current_states.add(post)

                        # Base confidence: min of rule confidence and all parent confidences
                        parent_confidences = [state_confidence[p] for p in rule["pre"]]
                        base_confidence = min(rule["confidence"], min(parent_confidences))
                        
                        # Apply temporal constraint penalty
                        time_gap_penalty, violation_type = calculate_time_gap_penalty(
                            rule, precondition_time, inferred_time
                        )
                        
                        # If causality is violated, set confidence to near zero
                        if violation_type == "causality_violation":
                            calculated_confidence = 0.01
                            state_confidence[post] = calculated_confidence
                            # Don't add to graph if causally impossible
                            continue
                        
                        # Apply evidence reasoning penalties
                        absence_penalty = check_absence_of_evidence(post, inferred_time)
                        time_decay = calculate_time_decay(inferred_time)
                        negative_penalty = apply_negative_evidence_penalty(post)
                        
                        # Final confidence with all factors including temporal
                        calculated_confidence = (
                            base_confidence * 
                            time_gap_penalty * 
                            absence_penalty * 
                            time_decay * 
                            negative_penalty
                        )
                        state_confidence[post] = calculated_confidence

                        G.add_node(
                            post,
                            type="state",
                            origin="inferred",
                            confidence=calculated_confidence
                        )

                        G.add_edge(rule_node, post)

                        state_info[post] = {
                            "origin": "inferred",
                            "evidence": {
                                "derived_from_rule": rule["name"],
                                "time_gap_penalty": time_gap_penalty,
                                "time_gap_violation": violation_type,
                                "absence_penalty": absence_penalty,
                                "time_decay": time_decay,
                                "negative_penalty": negative_penalty
                            },
                            "event_id": event_counter,
                            "time": inferred_time,
                            "confidence": calculated_confidence
                        }

                        changed = True

                applied_rules.append({
                    "name": rule["name"],
                    "tactic": rule["tactic"],
                    "confidence": rule["confidence"],
                    "event_id": event_counter
                })


def detect_missing_steps(rules):
    """
    Detect states that exist but lack clear provenance.
    Returns list of gaps that need hypothetical inference.
    """
    from state import hypothetical_states
    
    gaps = []
    
    # Check each observed state to see if it has a clear path
    for state_name, info in state_info.items():
        if info['origin'] == 'log':
            # Check if this state could have been reached through known rules
            has_known_path = False
            
            # If it's an initial access point, it's fine
            if 'user_access' in state_name and state_name not in hypothetical_states:
                # Check if there's a logical predecessor
                state_type = state_name.split(':')[0]
                host = state_name.split(':')[1] if ':' in state_name else None
                
                # Advanced states without clear predecessors are suspicious
                if state_type in ['admin_access', 'credential_dumped']:
                    # Check if we have the prerequisite user_access
                    user_state = f"user_access:{host}"
                    if user_state not in state_info:
                        gaps.append({
                            'missing_state': user_state,
                            'observed_state': state_name,
                            'reason': 'Advanced access observed without initial access'
                        })
    
    return gaps


def infer_missing_steps(rules):
    """
    Infer hypothetical steps to explain gaps in the attack chain.
    This is the "AI moment" - reconstructing what must have happened.
    """
    from state import hypothetical_states
    
    print("\n[Missing-Step Inference] Analyzing attack chain for gaps...")
    
    # Look for observed states that appear without clear prerequisites
    hypothetical_inferences = []
    
    for state_name, info in state_info.items():
        if info['origin'] == 'log':
            state_type = state_name.split(':')[0]
            host = state_name.split(':')[1] if ':' in state_name else None
            
            # Check for privilege escalation evidence without initial access
            if state_type == 'admin_access':
                user_state = f"user_access:{host}"
                if user_state not in current_states:
                    # Need to infer initial access
                    hypothetical_inferences.append({
                        'state': user_state,
                        'reason': f'Required for observed {state_name}',
                        'confidence': 0.3,  # Low confidence - hypothetical
                        'mechanism': 'unknown'
                    })
            
            # Check for lateral movement gaps
            if state_type == 'user_access' and host != 'A':
                # Check if we have evidence of how they got here
                has_network_access = False
                has_credentials = False
                
                for existing_state in current_states:
                    if f'network_access:A_to_{host}' in existing_state:
                        has_network_access = True
                    if 'credential_dumped' in existing_state:
                        has_credentials = True
                
                if not (has_network_access and has_credentials):
                    # Infer lateral movement via unknown mechanism
                    hypothetical_inferences.append({
                        'state': f'lateral_movement:unknown_to_{host}',
                        'reason': f'Necessary to explain {state_name}',
                        'confidence': 0.25,  # Very low - complete hypothesis
                        'mechanism': 'unknown (no evidence found)'
                    })
    
    # Apply hypothetical inferences
    for hyp in hypothetical_inferences:
        state_name = hyp['state']
        
        # Add even if it exists, but mark as hypothetical if not already present
        if state_name not in current_states:
            current_states.add(state_name)
        
        # Always add to hypothetical tracking
        state_confidence[state_name] = hyp['confidence']
        hypothetical_states[state_name] = hyp
        
        state_info[state_name] = {
            'origin': 'hypothetical',
            'evidence': {
                'reason': hyp['reason'],
                'mechanism': hyp['mechanism']
            },
            'event_id': len(state_info) + 1,
            'time': now(),
            'confidence': hyp['confidence']
        }
        
        G.add_node(
            state_name,
            type='state',
            origin='hypothetical',
            confidence=hyp['confidence']
        )
        
        print(f"  [HYPOTHETICAL] {state_name} (conf={hyp['confidence']:.2f})")
        print(f"    Reason: {hyp['reason']}")
        print(f"    Mechanism: {hyp['mechanism']}")
    
    return len(hypothetical_inferences)
