# utils.py
# Responsibility: Helper functions used by app.py
# No ML code, no Streamlit code belongs here

from typing import List, Tuple


# Keywords commonly found in phishing and spam messages
# Organized by category for readability and easy expansion
SUSPICIOUS_KEYWORDS = {
    "urgency": [
        "urgent", "immediately", "act now", "limited time",
        "expires today", "last chance", "don't wait", "hurry"
    ],
    "financial": [
        "free", "win", "winner", "cash", "prize", "reward",
        "money", "pounds", "dollars", "credit", "loan",
        "investment", "profit", "earn"
    ],
    "action": [
        "click", "call now", "txt", "text", "reply",
        "subscribe", "claim", "apply now", "verify"
    ],
    "personal_info": [
        "password", "account", "login", "confirm",
        "social security", "bank details", "card number"
    ],
    "suspicious_phrases": [
        "you have been selected", "congratulations",
        "you are a winner", "claim your", "guaranteed",
        "no obligation", "risk free"
    ],
}


def get_risk_level(confidence: float, label: str) -> Tuple[str, str]:
    """
    Convert a confidence score into a human-readable risk level.
    
    Returns:
        risk_label  - string description
        color       - hex color for UI display
    """
    if label == "Ham":
        if confidence >= 0.90:
            return "Safe", "#28a745"           # green
        elif confidence >= 0.70:
            return "Probably Safe", "#5cb85c"  # lighter green
        else:
            return "Uncertain", "#ffc107"      # amber

    else:  # Spam
        if confidence >= 0.90:
            return "High Risk", "#dc3545"      # red
        elif confidence >= 0.70:
            return "Medium Risk", "#fd7e14"    # orange
        else:
            return "Low Risk / Uncertain", "#ffc107"  # amber


def find_suspicious_keywords(message: str) -> List[Tuple[str, str]]:
    """
    Scan a message for known suspicious keywords.
    
    Returns a list of (keyword, category) tuples for every match found.
    Example: [("free", "financial"), ("click", "action")]
    """
    message_lower = message.lower()
    found = []

    for category, keywords in SUSPICIOUS_KEYWORDS.items():
        for keyword in keywords:
            if keyword in message_lower:
                found.append((keyword, category))

    return found


def format_confidence_percentage(confidence: float) -> str:
    """
    Convert a float confidence score to a display-friendly percentage.
    
    Example: 0.9732 -> "97.32%"
    """
    return f"{confidence * 100:.2f}%"


def summarize_keywords(found_keywords: List[Tuple[str, str]]) -> str:
    """
    Convert a list of (keyword, category) tuples into a readable summary.
    
    Example output:
        "free (financial), click (action), urgent (urgency)"
    """
    if not found_keywords:
        return "None detected"

    return ", ".join(
        f"{keyword} ({category})"
        for keyword, category in found_keywords
    )