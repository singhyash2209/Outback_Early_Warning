from dataclasses import dataclass
from math import radians, sin, cos, asin, sqrt
import requests
from typing import List, Dict, Optional

from src.fetch_rfs_nsw import get_rfs_points
from src.fetch_bom import get_bom_polygons
from src.fetch_firms import get_firms_points

@dataclass
class RiskResult:
    score: float                 # 0..1
    district: Optional[str]      # (UI may supply/override)
    tags: List[str]

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

def _geocode_osm(query: str) -> Optional[Dict[str, float]]:
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

def _point_in_polygon_bbox(lat: float, lon: float, poly_coords: List[List[float]]) -> bool:
    if not poly_coords:
        return False
    lons = [c[0] for c in poly_coords if isinstance(c, (list, tuple)) and len(c) >= 2]
    lats = [c[1] for c in poly_coords if isinstance(c, (list, tuple)) and len(c) >= 2]
    if not lons or not lats:
        return False
    return (min(lats) <= lat <= max(lats)) and (min(lons) <= lon <= max(lons))

def compute_risk_for_query(q: str) -> RiskResult:
    tags: List[str] = []
    loc = _geocode_osm(q)
    if not loc:
        return RiskResult(0.0, None, ["could not geocode location"])

    plat, plon = loc["lat"], loc["lon"]

    # RFS proximity (guard against missing coords)
    rfs = get_rfs_points() or []
    nearest_km = None
    for p in rfs:
        lat = p.get("lat")
        lon = p.get("lon")
        try:
            if lat is None or lon is None:
                continue
            d = _haversine_km(float(plat), float(plon), float(lat), float(lon))
        except Exception:
            continue
        nearest_km = d if nearest_km is None else min(nearest_km, d)

    base = 0.0
    if nearest_km is not None:
        base = max(0.0, 1.0 - min(nearest_km, 50.0) / 50.0)  # 0–50 km scale
        if nearest_km <= 5:
            tags.append("very close to active incident (<5 km)")
        elif nearest_km <= 15:
            tags.append("near active incident (≤15 km)")
        elif nearest_km <= 30:
            tags.append("within 30 km of incident")

    # BOM polygons (bbox gate)
    bom = get_bom_polygons() or []
    inside_bom = False
    for poly in bom:
        coords = poly.get("polygon")
        if isinstance(coords, list) and coords and isinstance(coords[0], list):
            if _point_in_polygon_bbox(plat, plon, coords):
                inside_bom = True
                break
    if inside_bom:
        base += 0.25
        tags.append("inside BOM warning area")

    # FIRMS hotspots (optional)
    boost_firms = 0.0
    firms = get_firms_points() or []
    for f in firms[:500]:
        lat = f.get("lat")
        lon = f.get("lon")
        try:
            if lat is None or lon is None:
                continue
            d = _haversine_km(plat, plon, float(lat), float(lon))
        except Exception:
            continue
        if d <= 20:
            boost_firms = max(boost_firms, 0.15)
            tags.append("near recent heat hotspot")
            break

    score = max(0.0, min(1.0, base + boost_firms))
    if score == 0.0 and not tags:
        tags.append("no nearby incidents or warnings")

    return RiskResult(score=round(score, 2), district=None, tags=tags)