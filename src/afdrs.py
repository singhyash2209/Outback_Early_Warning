# AFDRS today + outlook (NSW) — real impl in Phase 4
class Rating:
    def __init__(self, level: str):
        self.level = level
def get_today_rating_for_district(district: str) -> Rating:
    return Rating("High")  # placeholder
