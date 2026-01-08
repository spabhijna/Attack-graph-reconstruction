# Temporal Constraints Implementation Summary

## Overview
The system now implements comprehensive temporal reasoning, transforming it from a simple rule engine into a causality-aware reasoning engine.

## Key Features Implemented

### 1. Causality Enforcement
- **Rule cannot fire if postcondition timestamp < precondition timestamp**
- Checks that all preconditions exist before postconditions can be inferred
- Rejects causally impossible sequences (e.g., lateral movement before credentials obtained)

**Code:** `check_temporal_causality()` in `inference.py`

### 2. Time Gap Penalties
- **Each rule has max_time_gap** (e.g., 30 min for privilege escalation, 1 hour for lateral movement)
- **Penalties applied:**
  - Within max gap: Linear decay (up to 30% penalty)
  - Exceeding max gap: Exponential decay (50% per excess interval)
  - Causality violation: Near-zero confidence (0.01)

**Code:** `calculate_time_gap_penalty()` in `inference.py`

### 3. Sliding Windows
- `get_sliding_window_states()` returns states within a time window (default 2 hours)
- Enables temporal relevance filtering for analysis

### 4. Time Decay
- Older states become less reliable over time
- Exponential decay with configurable half-life (default 1 hour)
- Floor at 0.3 to prevent complete confidence loss

**Code:** `calculate_time_decay()` in `inference.py`

## Rule Configuration Example

```python
{
    "name": "Lateral Movement A_to_B",
    "pre": {"credential_dumped:A", "network_access:A_to_B"},
    "post": {"user_access:B"},
    "confidence": 0.6,
    "tactic": "Lateral Movement",
    "max_time_gap": 3600  # 1 hour - NEW!
}
```

## Confidence Calculation Formula

```python
final_confidence = (
    base_confidence *        # min(rule_conf, min(parent_confs))
    time_gap_penalty *       # Based on time between pre/post
    absence_penalty *        # Missing expected evidence
    time_decay *             # Age of inference
    negative_penalty         # Contradicting evidence
)
```

## Example Output

```
=== State Confidence Scores ===

user_access:A: 1.00 (observed)
network_access:A_to_B: 1.00 (observed)
admin_access:A: 0.35 (inferred) [missing evidence: 0.50]
credential_dumped:A: 0.17 (inferred) [missing evidence: 0.50]
user_access:B: 0.17 (inferred)
admin_access:B: 0.09 (inferred) [missing evidence: 0.50]
```

## Critical Capabilities Achieved

✅ **"This lateral movement is unlikely because credentials appeared after the access"**
- System detects and rejects causality violations

✅ **"This privilege escalation is shaky - 2 hours passed since initial access"**
- Time gap penalties reflect temporal implausibility

✅ **"Credential dump inferred but no LSASS logs - confidence drops"**
- Absence-of-evidence reasoning

✅ **Timeline-aware reasoning, not just bookkeeping**
- True temporal causality, not just sorted IDs

## Files Modified

- `rules.py`: Added `max_time_gap` to all rules
- `inference.py`: Added temporal constraint functions and enforcement
- `output.py`: Display temporal penalties in confidence breakdown

## Testing

Run comprehensive demos:
```bash
python demo_comprehensive.py
```

This demonstrates:
- Good timing scenarios
- Time gap violations
- Missing evidence scenarios
- Causality checking
