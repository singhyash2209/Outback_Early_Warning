import requests
from cachetools import TTLCache
from src.utils_cache import update_cache_time

# cache results for 15 minutes
_cache = TTLCache(maxsize=1, ttl=900)

def get_rfs_points():
    """Fetch NSW RFS incidents as point features for mapping."""
    if "points" in _cache:
        return _cache["points"]

    url = "https://www.rfs.nsw.gov.au/feeds/majorIncidents.json"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
    except Exception as e:
        print("Error fetching RFS incidents:", e)
        return []

    points = []
    for item in data.get("features", []):
        props = item.get("properties", {}) or {}
        geom = item.get("geometry", {}) or {}
        coords = geom.get("coordinates", [None, None])

        # --- smarter status derivation ---
        status = props.get("status") or props.get("statusText") or ""
        if not status:
            t = (props.get("type") or "").lower()
            if "burn" in t:
                status = "Planned burn"
            elif props.get("size"):
                status = f"Ongoing ({props.get('size')} ha)"
            else:
                status = "No official status published"

        if coords and len(coords) == 2:
            points.append({
                "lat": coords[1],
                "lon": coords[0],
                "title": props.get("title", "Unknown"),
                "status": status,
                "updated": props.get("updated", ""),
                "url": props.get("link", ""),
                "source": "NSW RFS"
            })

    # 🟢 Tell cache system that RFS feed is now updated
    update_cache_time("NSW RFS incidents")

    _cache["points"] = points
    return points


def get_rfs_feed():
    """Simplified feed list for sidebar/feed page."""
    points = get_rfs_points()
    feed = []
    for p in points:
        feed.append({
            "time": p["updated"],
            "title": p["title"],
            "summary": f"Status: {p['status']}",
            "url": p["url"]
        })
    return sorted(feed, key=lambda x: x["time"], reverse=True)