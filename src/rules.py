"""
Attack rules and tactics definitions.
"""

rules = [
    {
        "name": "Privilege Escalation on A",
        "pre": {"user_access:A"},
        "post": {"admin_access:A"},
        "confidence": 0.7,
        "tactic": "Privilege Escalation"
    },
    {
        "name": "Credential Dumping on A",
        "pre": {"admin_access:A"},
        "post": {"credential_dumped:A"},
        "confidence": 0.8,
        "tactic": "Credential Access"
    },
    {
        "name": "Lateral Movement A_to_B",
        "pre": {"credential_dumped:A", "network_access:A_to_B"},
        "post": {"user_access:B"},
        "confidence": 0.6,
        "tactic": "Lateral Movement"
    },
    {
        "name": "Privilege Escalation on B",
        "pre": {"user_access:B"},
        "post": {"admin_access:B"},
        "confidence": 0.7,
        "tactic": "Privilege Escalation"
    }
]
