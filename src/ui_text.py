def actions_for_afdrs(level: str) -> str:
    tips = {
        "Moderate": "- Stay informed.\n- Review your bushfire survival plan.",
        "High": "- Clear gutters/combustibles.\n- Be ready to leave early if advised.",
        "Extreme": "- Do not wait to the last minute.\n- Consider leaving early.",
        "Catastrophic": "- Leaving early is the safest option.\n- Follow official advice immediately."
    }
    return tips.get(level, "Stay informed and follow official advice.")

def explain_badges(risk):
    return f"**Why:** {', '.join(risk.tags)}"