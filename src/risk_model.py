# Transparent scorer — real impl in Phase 5
class RiskResult:
    def __init__(self, score: float, district: str | None, tags: list[str]):
        self.score = score
        self.district = district
        self.tags = tags

def compute_risk_for_query(q: str) -> RiskResult:
    return RiskResult(0.42, "Greater Sydney", ["hotspots", "official warning"])