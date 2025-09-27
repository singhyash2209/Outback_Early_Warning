from dataclasses import dataclass
import requests
from cachetools import TTLCache
from src.utils_cache import update_cache_time

@dataclass
class Rating:
    level: str  # e.g., "Moderate", "High", "Extreme", "Catastrophic"

# cache the latest dict for 60 minutes
_cache = TTLCache(maxsize=1, ttl=3600)

RATING_NORMALIZE = {
    "no rating": "No Rating",
    "moderate": "Moderate",
    "high": "High",
    "extreme": "Extreme",
    "catastrophic": "Catastrophic",
    "low-moderate": "Moderate",
    "low to moderate": "Moderate",
}

def _try_fetch_rfs_json():
    """
    Try NSW RFS FDR/TOBAN style JSON (some regions still publish daily ratings here).
    Example historical endpoint: https://www.rfs.nsw.gov.au/feeds/fdrToban.json
    Returns: dict[str, str] => {district_name: rating}
    """
    url = "https://www.rfs.nsw.gov.au/feeds/fdrToban.json"
    r = requests.get(url, timeout=10, headers={"User-Agent": "Outback_Early_Warning"})
    r.raise_for_status()
    js = r.json()
    out = {}
    for d in js.get("districts", []):
        name = (d.get("name") or "").strip()
        rating = (d.get("todays_fire_danger_rating") or "").strip()
        if name and rating:
            out[name] = rating
    return out

def _normalize(level: str) -> str:
    lvl = (level or "").strip().lower()
    return RATING_NORMALIZE.get(lvl, level or "Unknown")

def get_today_ratings() -> dict[str, str]:
    """Return mapping district -> rating. Cached, graceful fallback to empty dict."""
    if "ratings" in _cache:
        return _cache["ratings"]
    try:
        ratings = _try_fetch_rfs_json()
        # normalize
        ratings = {k: _normalize(v) for k, v in ratings.items()}
        _cache["ratings"] = ratings
        update_cache_time("AFDRS ratings")
        return ratings
    except Exception as e:
        print("AFDRS fetch error:", e)
        _cache["ratings"] = {}
        return {}

def get_today_rating_for_district(district: str) -> Rating:
    ratings = get_today_ratings()
    # fuzzy match by lowercase containment
    dl = district.lower()
    best = None
    for name, lvl in ratings.items():
        if dl in name.lower() or name.lower() in dl:
            best = lvl
            break
    return Rating(best or "Unknown")