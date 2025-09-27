def actions_for_afdrs(level: str) -> str:
    """
    Return short, plain-English actions for the given AFDRS level.
    Keys are stored in Title Case for prettier display.
    Input is normalized so function works with any case.
    """
    lvl = (level or "").strip().title()
    guide = {
        "No Rating": [
            "Stay informed via NSW RFS / BOM.",
            "Use local conditions to guide decisions."
        ],
        "Moderate": [
            "Review your bushfire survival plan.",
            "Check radios/alerts; know multiple exit routes."
        ],
        "High": [
            "Clear gutters and combustibles around the home.",
            "Pack a go-bag and monitor official alerts frequently."
        ],
        "Extreme": [
            "Leaving early is recommended for high-risk properties.",
            "Prepare your route and destination in advance."
        ],
        "Catastrophic": [
            "Do not wait — leaving early is the safest option.",
            "Follow official instructions immediately and avoid bushland."
        ],
        "Unknown": [
            "AFDRS data not available; act on local conditions.",
            "Monitor NSW RFS and BOM for updates."
        ],
    }

    key = lvl if lvl in guide else "Unknown"
    return "\n".join(f"- {line}" for line in guide[key])


def explain_badges(risk) -> str:
    """
    Human-readable explanation of why a risk score was assigned.
    Uses tags attached to the risk object.
    """
    tags = getattr(risk, "tags", []) or []
    if not tags:
        return "No contributing factors detected yet."
    return "Why this score: " + ", ".join(tags)
