# Competing Narratives: Multiple Attack Explanations

## Overview
Step 5 transforms the system from showing **one story** to comparing **multiple possible stories**. This is where the project stops being a diagram and starts being a real analysis tool.

## What are Competing Narratives?

Instead of presenting a single attack chain, the system:
1. **Generates multiple candidate explanations**
2. **Ranks them by confidence and quality**
3. **Shows top-N for analyst comparison**
4. **Highlights differences between narratives**

This is how **real analysts work** - comparing multiple hypotheses.

## Implementation

### Narrative Types Generated

**Narrative #1: Full Inference Chain**
- All rules applied
- All states (observed + inferred + hypothetical)
- Most complete picture
- Highest speculation

**Narrative #2: Conservative (No Hypotheticals)**
- Excludes hypothetical steps
- Only observed + rule-based inferences
- Balanced view
- Moderate confidence

**Narrative #3: High-Confidence Only**
- States with confidence > 0.5
- Filters out weak inferences
- High certainty
- May miss parts of attack

**Narrative #4: Direct Inferences Only**
- Observed + one-level inferences
- Minimal speculation
- Quick assessment view

**Narrative #5: Minimal (Observed Only)**
- Pure evidence
- Zero speculation
- Highest confidence
- Least complete

### Scoring System

Each narrative is scored based on:

```python
score = (
    avg_confidence * 0.4 +      # Confidence levels
    coverage * 0.3 +             # How much evidence explained
    complexity_penalty * 0.2 +   # Prefer simpler explanations
    hypothetical_penalty * 0.1   # Penalize speculation
)
```

**Factors:**
- **Average Confidence**: Mean confidence across all states
- **Coverage**: Percentage of observed evidence explained
- **Complexity Penalty**: Parsimony - fewer steps preferred
- **Hypothetical Penalty**: Exponential penalty for speculation

## Example Output

### Narrative Comparison Matrix

```
State                         N5   N3   N4   N1   N2  
------------------------------------------------------
✓ admin_access:A              ██  ██  ██  ██  ██  
? admin_access:B                      ▒▒  ▒▒  ▒▒  
✓ credential_dumped:A         ██  ██  ██  ██  ██  
✓ network_access:A_to_B       ██  ██  ██  ██  ██  
✓ user_access:A               ██  ██  ██  ██  ██  
✓ user_access:B               ██  ██  ██  ██  ██  

Legend: ✓=Observed  ?=Inferred  ⚠=Hypothetical
        ██=High(0.7+) ▓▓=Med(0.5+) ▒▒=Low(0.3+) ░░=VeryLow
```

### Narrative Tradeoffs

```
Narrative  Score   States  Observed  Inferred  Hypothetical  Complexity
---------------------------------------------------------------------------
#5         1.000   5       5         0         0             0
#3         0.943   5       5         0         0             4
#4         0.923   6       5         1         0             2
#1         0.900   6       5         1         0             4
#2         0.900   6       5         1         0             4
```

## Use Cases

### Scenario 1: Incident Response (Active Threat)
**Use**: Most complete narrative (#1 or #4)
**Reason**: Need full attack scope to contain threat
**Trade-off**: Accept some speculation for completeness

### Scenario 2: Forensic Investigation (Post-Mortem)
**Use**: High-confidence narrative (#3 or #5)
**Reason**: Need defensible findings for report
**Trade-off**: May miss parts of attack, but high certainty

### Scenario 3: Threat Hunting (Proactive)
**Use**: Most complete narrative (#1)
**Reason**: Better to over-investigate than miss threats
**Trade-off**: Will investigate some false leads

### Scenario 4: Compliance Reporting
**Use**: Conservative narrative (#5)
**Reason**: Only report what you can prove
**Trade-off**: Underreports actual impact

## Key Features

### 1. Automatic Generation
- System generates 5 narrative variants automatically
- No manual configuration needed
- Different perspectives on same evidence

### 2. Transparent Scoring
- Clear scoring algorithm
- Each factor explained
- Analyst can understand rankings

### 3. Visual Comparison
- Matrix view shows state presence across narratives
- Confidence levels visualized with blocks
- Easy to spot differences

### 4. Shared vs. Unique States
```
States shared by all narratives (5):
  • admin_access:A
  • credential_dumped:A
  • network_access:A_to_B
  • user_access:A
  • user_access:B

Unique states per narrative:
  Narrative #1: admin_access:B
  Narrative #2: admin_access:B
  Narrative #3: (none)
  Narrative #4: admin_access:B
  Narrative #5: (none)
```

### 5. Recommendation System
```
RECOMMENDATION

Best narrative: #5
Score: 1.000
Rationale: Minimal (observed evidence only)

This narrative provides the best balance of:
  • Evidence coverage
  • Confidence levels
  • Explanation simplicity
  • Minimal speculation
```

## Files Implemented

- **`narratives.py`**: Core competing narratives engine
  - `AttackNarrative` class
  - `generate_narrative_variants()` function
  - `compare_narratives()` function
  - `explain_competing_narratives()` function

- **`main.py`**: Updated to generate and display narratives

- **Demo files**:
  - `demo_narratives.py`: Basic demonstration
  - `demo_narrative_comparison.py`: Enhanced visual comparison

## Critical Capability

**Before Step 5**: "Here's what happened"
**After Step 5**: "Here are 5 possible explanations, ranked by confidence"

### Example Analyst Dialogue:

> "We have 5 possible narratives. The most confident (#5, score=1.0) only includes observed evidence. The most complete (#1, score=0.9) includes an inferred admin_access:B that #5 doesn't have. If we're in active incident response, I recommend #1. If we're writing a compliance report, use #5."

## The Tool Moment

This is where the system becomes a **professional tool**:
- Analysts compare multiple hypotheses (standard practice)
- System shows trade-offs explicitly
- Recommendations based on use case
- Transparency in reasoning

**You're not showing a diagram. You're showing competing hypotheses with evidence-based rankings.**

That's what real analysts need. That's a tool.

## Testing

Run demonstrations:
```bash
# Basic demonstration
python demo_narratives.py

# Enhanced visual comparison
python demo_narrative_comparison.py

# Full system with competing narratives
python src/main.py
```

## Summary

With competing narratives, your attack graph reconstruction system:
✅ Generates multiple possible explanations
✅ Ranks them by quality scores
✅ Shows trade-offs explicitly
✅ Provides use-case specific recommendations
✅ Enables analyst decision-making
✅ Transforms from diagram to professional tool
