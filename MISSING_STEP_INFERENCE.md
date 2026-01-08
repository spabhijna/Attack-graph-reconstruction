# Missing-Step Inference: Attack Reconstruction

## Overview
Step 4 transforms the system from **log replay** to **true attack reconstruction**. The system now infers steps that must have happened but were not observed in logs.

## What is Missing-Step Inference?

Instead of only working with observed events, the system:
1. **Detects gaps** in the attack chain
2. **Infers hypothetical steps** needed to explain evidence
3. **Marks them explicitly** as low-confidence hypotheses
4. **Explains the reasoning** behind each inference

This is **reconstruction, not replay**.

## Implementation

### Core Function: `infer_missing_steps()`

Located in `inference.py`, this function:

```python
def infer_missing_steps(rules):
    """
    Infer hypothetical steps to explain gaps in the attack chain.
    This is the "AI moment" - reconstructing what must have happened.
    """
```

### Detection Logic

**Scenario 1: Advanced Access Without Initial Access**
```
Observed: admin_access:A
Missing: user_access:A
Inference: "Required for observed admin_access:A"
Confidence: 0.30 (low - hypothetical)
```

**Scenario 2: Lateral Movement Gaps**
```
Observed: user_access:B
Missing: Clear lateral movement path (credentials + network access)
Inference: "lateral_movement:unknown_to_B"
Confidence: 0.25 (very low - complete hypothesis)
```

## Example Output

```
[Missing-Step Inference] Analyzing attack chain for gaps...
  [HYPOTHETICAL] user_access:A (conf=0.30)
    Reason: Required for observed admin_access:A
    Mechanism: unknown

=== State Confidence Scores ===

Observed (from logs):
  admin_access:A: 1.00
  network_access:A_to_B: 1.00
  user_access:B: 1.00

Inferred (via rules):
  credential_dumped:A: 0.40 [missing evidence: 0.50]
  admin_access:B: 0.35 [missing evidence: 0.50]

⚠ Hypothetical (missing-step inference):
  user_access:A: 0.30
    → Reason: Required for observed admin_access:A
    → Mechanism: unknown
    → Status: EXPLICITLY HYPOTHETICAL - LOW CONFIDENCE
```

## Key Features

### 1. Explicit Hypothetical Marking
- States marked with origin='hypothetical'
- Clearly labeled with ⚠ warning symbol
- "EXPLICITLY HYPOTHETICAL - LOW CONFIDENCE" status

### 2. Low Confidence Scores
- Hypothetical states: 0.25-0.30 confidence
- Much lower than observed (1.0) or inferred (0.35+)
- Reflects uncertainty of the hypothesis

### 3. Reasoning Explanation
- **Reason**: Why this step was inferred
- **Mechanism**: How it might have happened (often "unknown")
- Full transparency in the reasoning process

### 4. Gap Detection Algorithms

**Missing Prerequisites**:
```python
if state_type == 'admin_access':
    user_state = f"user_access:{host}"
    if user_state not in current_states:
        # Need to infer initial access
```

**Unexplained Lateral Movement**:
```python
if state_type == 'user_access' and host != 'A':
    if not (has_network_access and has_credentials):
        # Infer lateral movement via unknown mechanism
```

## Files Modified

- **`state.py`**: Added `hypothetical_states` tracking
- **`inference.py`**: Added `infer_missing_steps()` and gap detection logic
- **`main.py`**: Added missing-step inference step in pipeline
- **`output.py`**: Added hypothetical states display section

## Testing

Run the demonstration:
```bash
python demo_missing_steps.py
```

This shows:
1. Detecting missing user_access when admin_access is observed
2. Inferring lateral movement when path is unclear
3. Low confidence scoring
4. Explicit hypothetical labeling

## Critical Capability

**Before (Step 3)**: "We see these events in the logs"
**After (Step 4)**: "We see these events, and these other events must have happened"

### Example Statement:
> "Likely lateral movement via unknown mechanism (conf=0.25) - necessary to explain user_access:B"

This is **true intelligence** - not just processing logs, but **reasoning about what must have occurred** even without direct evidence.

## The AI Moment

This is where the system becomes intelligent:
- It doesn't just match patterns
- It **reasons about causality**
- It **fills in gaps** using domain knowledge
- It **admits uncertainty** with low confidence
- It **explains its reasoning**

The system can now say:
> "I don't have direct evidence, but based on what I see, this step (with low confidence) must have happened to explain the observations."

That's reconstruction, not replay. That's the AI moment.
