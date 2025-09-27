from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from math import radians, sin, cos, asin, sqrt
from typing import List, Dict, Optional, Iterable
import requests

from src.fetch_rfs_nsw import get_rfs_points
from src.fetch_bom import get_bom_polygons
from src.fetch_firms import get_firms_points
from src.afdrs import get_today_rating_for_district  # optional weighting

@dataclass
class RiskResult:
    score: float                 # 0..1
    district: Optional[str]      # echoed back if provided
    tags: List[str]

# -----------------------
# Utilities
# -----------------------

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

@lru_cache(maxsize=128)
def _geocode_osm(query: str) -> Optional[Dict[str, float]]:
    if not (query or "").strip():
        return None
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "limit": 1, "countrycodes": "au"}
    headers = {"User-Agent": "Outback_Early_Warning/1.0 (demo)"}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        items = r.json()
        if not items:
            return None
        it = items[0]
        return {"lat": float(it["lat"]), "lon": float(it["lon"])}
    except Exception:
        return None

def _point_in_polygon(lon: float, lat: float, ring: Iterable[Iterable[float]]) -> bool:
    """
    Ray-casting point-in-polygon. Expects coordinates as [lon, lat].
    Returns True if (lon,lat) is inside the ring.
    """
    x, y = lon, lat
    inside = False
    pts = [tuple(p[:2]) for p in ring if isinstance(p, (list, tuple)) and len(p) >= 2]
    if len(pts) < 3:
        return False
    j = len(pts) - 1
    for i in range(len(pts)):
        xi, yi = pts[i]
        xj, yj = pts[j]
        # edge intersects horizontal ray?
        intersect = ((yi > y) != (yj > y)) and \
                    (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi)
        if intersect:
            inside = not inside
        j = i
    return inside

def _any_polygon_contains(lat: float, lon: float, polygons: List[Dict]) -> bool:
    """
    Accepts polygons from get_bom_polygons():
      - each item typically has 'polygon' key as a list of [lon, lat] points
      - sometimes a MultiPolygon-like structure; we handle a list/list case
    """
    if not polygons:
        return False
    for poly in polygons:
        coords = poly.get("polygon")
        if not coords:
            continue
        # If coords is a list of rings, test each; else treat as a single ring
        if isinstance(coords[0], list) and len(coords) >= 1 and isinstance(coords[0][0], (int, float, list)):
            # either [[lon,lat], ...] or [[[lon,lat],...], [hole], ...]
            if isinstance(coords[0][0], (int, float)):  # simple ring
                if _point_in_polygon(lon, lat, coords):
                    return True
            else:  # list of rings
                for ring in coords:
                    if _point_in_polygon(lon, lat, ring):
                        return True
        else:
            # Fallback: assume simple ring
            try:
                if _point_in_polygon(lon, lat, coords):
                    return True
            except Exception:
                continue
    return False

# -----------------------
# Main scoring
# -----------------------

_AFDRS_WEIGHT = {
    "No Rating": 1.00,
    "Moderate": 1.10,
    "High": 1.25,
    "Extreme": 1.50,
    "Catastrophic": 1.75,
    "Unknown": 1.00,
}

def compute_risk_for_query(q: str, district: Optional[str] = None) -> RiskResult:
    """
    Score is built from:
      - proximity to nearest RFS incident (0–50 km scale)
      - inside BOM warning polygon (adds 0.25)
      - nearby FIRMS hotspot within 20 km (adds up to 0.15)
    Then multiplied by an AFDRS weighting if a district is provided.
    """
    tags: List[str] = []

    # 1) Geocode
    loc = _geocode_osm(q or "")
    if not loc:
        return RiskResult(0.0, district, ["could not geocode location"])
    plat, plon = loc["lat"], loc["lon"]

    # 2) RFS proximity
    rfs = get_rfs_points() or []
    nearest_km = None
    for p in rfs:
        lat = p.get("lat")
        lon = p.get("lon")
        if lat is None or lon is None:
            continue
        try:
            d = _haversine_km(plat, plon, float(lat), float(lon))
        except Exception:
            continue
        nearest_km = d if nearest_km is None else min(nearest_km, d)

    base = 0.0
    if nearest_km is not None:
        # 0 at 50 km+, 1 near 0 km
        base = max(0.0, 1.0 - min(nearest_km, 50.0) / 50.0)
        if nearest_km <= 5:
            tags.append("very close to active incident (<5 km)")
        elif nearest_km <= 15:
            tags.append("near active incident (≤15 km)")
        elif nearest_km <= 30:
            tags.append("within 30 km of incident")

    # 3) BOM polygons (true point-in-polygon)
    bom = get_bom_polygons() or []
    if _any_polygon_contains(plat, plon, bom):
        base += 0.25
        tags.append("inside BOM warning area")

    # 4) FIRMS hotspots (optional)
    firms = get_firms_points() or []
    for f in firms[:500]:
        lat = f.get("lat")
        lon = f.get("lon")
        if lat is None or lon is None:
            continue
        try:
            d = _haversine_km(plat, plon, float(lat), float(lon))
        except Exception:
            continue
        if d <= 20:
            base = base + 0.15
            tags.append("near recent heat hotspot (≤20 km)")
            break

    # 5) AFDRS weighting (if district provided)
    weight = 1.0
    if (district or "").strip():
        lvl = get_today_rating_for_district(district).level
        weight = _AFDRS_WEIGHT.get(lvl, 1.0)
        tags.append(f"AFDRS today in {district}: {lvl}")

    score = max(0.0, min(1.0, base * weight))

    if score == 0.0 and not tags:
        tags.append("no nearby incidents or warnings")

    return RiskResult(score=round(score, 2), district=district, tags=tags)