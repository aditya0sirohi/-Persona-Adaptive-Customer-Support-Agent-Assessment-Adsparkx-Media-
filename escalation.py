import re

ESCALATION_KEYWORDS = [
    "refund", "lawsuit", "legal", "cancel subscription", "complaint", "speak to human", "talk to human", "representative", "attorney", "court"
]
NEGATIVE_WORDS = [
    "useless", "angry", "tired", "hate", "worst", "never works", "not working", "disappointed", "frustrated", "broken", "issue", "problem", "fail", "error", "unresolved", "poor service"
]

def check_escalation(query: str, response: str, persona: str = None) -> tuple[bool, str]:
    q_lower = query.lower()
    # 1) Immediate escalation for explicit keywords
    for kw in ESCALATION_KEYWORDS:
        if kw in q_lower:
            return True, f"Immediate escalation: keyword '{kw}' detected in query."
    # 2) Conditional escalation for frustrated persona with multiple negative indicators
    if persona == "Frustrated User":
        negative_count = sum(1 for word in NEGATIVE_WORDS if word in q_lower)
        word_count = len(re.findall(r'\w+', query))
        if negative_count >= 2 and word_count > 10:
            return True, (
                f"Conditional escalation: persona is 'Frustrated User', "
                f"{negative_count} negative indicators found, query length is {word_count} words."
            )
        # 3) Failure-aware escalation: low knowledge confidence in response
        failure_phrases = [
            "no relevant documentation found",
            "information is not available",
            "not found in context"
        ]
        for phrase in failure_phrases:
            if phrase in response.lower():
                return True, (
                    "Escalation due to frustrated persona + low knowledge confidence."
                )
    # 4) Otherwise, do not escalate
    return False, "No escalation: criteria not met."

def create_handoff_packet(query: str, persona: str, context: list[str], reason: str) -> dict:
    return {
        "persona": persona,
        "reason": reason,
        "user_query": query,
        "retrieved_context": context,
        "summary": " ".join(context)
    }
