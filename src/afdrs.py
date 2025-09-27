from dataclasses import dataclass
from typing import Optional, Dict
import os
import csv
from io import StringIO

import requests
from cachetools import TTLCache

from src.utils_cache import update_cache_time


# --- Public API --------------------------------------------------------------

@dataclass
class Rating:
    level: str  # "No Rating", "Moderate", "High", "Extreme", "Catastrophic", "Unknown"


def get_today_ratings() -> Dict[str, str]:
    """
    Returns a mapping: { district_name -> normalized_rating }.
    Order of attempts:
      1) Custom CSV/JSON if AFDRS_CUSTOM_URL is set
      2) NSW RFS JSON (fdrToban.json)
      3) empty dict
    Always updates the cache timestamp so your Home badge shows freshness.
    """
    if "ratings" in _CACHE:
        return _CACHE["ratings"]

    ratings: Dict[str, str] = {}
    try:
        # 1) Try custom source (CSV or JSON) if configured
        ratings = _try_fetch_custom_source()
        if not ratings:
            # 2) Try NSW RFS JSON
            ratings = _try_fetch_rfs_json()
    except Exception as e:
        print("AFDRS fetch error:", e)
        ratings = {}

    _CACHE["ratings"] = ratings
    update_cache_time("AFDRS ratings")
    return ratings


def get_today_rating_for_district(district: str) -> Rating:
    """
    Fuzzy matches the provided district string against the loaded ratings.
    Returns a Rating("Unknown") if no match is found.
    """
    ratings = get_today_ratings()
    if not district:
        return Rating("Unknown")

    dl = district.lower().strip()
    best = None
    for name, lvl in ratings.items():
        nl = name.lower()
        if dl in nl or nl in dl:
            best = lvl
            break

    return Rating(best or "Unknown")


# --- Internal helpers --------------------------------------------------------

# TTL: cache one object (the dict) for 60 minutes
_CACHE = TTLCache(maxsize=1, ttl=3600)

# Normalize to Title Case used in UI
_RATING_NORMALIZE = {
    "no rating": "No Rating",
    "no-rating": "No Rating",
    "none": "No Rating",
    "moderate": "Moderate",
    "low-moderate": "Moderate",
    "low to moderate": "Moderate",
    "high": "High",
    "extreme": "Extreme",
    "catastrophic": "Catastrophic",
}


def _normalize_level(level: Optional[str]) -> str:
    lvl = (level or "").strip().lower()
    return _RATING_NORMALIZE.get(lvl, (level or "Unknown").strip().title() or "Unknown")


def _try_fetch_custom_source() -> Dict[str, str]:
    """
    Optional: read AFDRS from a custom endpoint (CSV or JSON).
    Configure with environment variable AFDRS_CUSTOM_URL.

    JSON shapes accepted:
      - {"data":[{"district":"Far South Coast","rating":"High"}, ...]}
      - [{"district":"...","rating":"..."}, ...]   # bare list is OK

    CSV columns accepted (case-insensitive):
      - district, rating   (name/level also accepted as synonyms)
    """
    url = os.getenv("AFDRS_CUSTOM_URL", "").strip()
    if not url:
        return {}

    headers = {"User-Agent": "Outback_Early_Warning"}
    r = requests.get(url, timeout=10, headers=headers)
    r.raise_for_status()

    ctype = (r.headers.get("Content-Type") or "").lower()
    text = r.text

    # Prefer JSON if declared
    if "json" in ctype or text.strip().startswith(("{", "[")):
        try:
            js = r.json()
        except Exception:
            js = None

        out: Dict[str, str] = {}
        rows = None

        if isinstance(js, dict) and "data" in js and isinstance(js["data"], list):
            rows = js["data"]
        elif isinstance(js, list):
            rows = js

        if isinstance(rows, list):
            for row in rows:
                if not isinstance(row, dict):
                    continue
                name = (row.get("district") or row.get("name") or "").strip()
                rating = _normalize_level(row.get("rating") or row.get("level"))
                if name and rating:
                    out[name] = rating
        return out

    # Fallback: parse CSV
    out: Dict[str, str] = {}
    try:
        # robust CSV sniffing
        first = text.splitlines()[0] if text else ""
        try:
            dialect = csv.Sniffer().sniff(first) if first else csv.excel
        except Exception:
            dialect = csv.excel
        reader = csv.DictReader(StringIO(text), dialect=dialect)
        for row in reader:
            # Accept flexible column names
            name = (row.get("district") or row.get("name") or "").strip()
            rating = _normalize_level(row.get("rating") or row.get("level"))
            if name and rating:
                out[name] = rating
    except Exception as e:
        print("AFDRS CSV parse error:", e)
        return {}

    return out


def _try_fetch_rfs_json() -> Dict[str, str]:
    """
    NSW RFS feed (where available). Shape:
      {"districts":[{"name":"Far South Coast","todays_fire_danger_rating":"High"}, ...]}
    """
    url = "https://www.rfs.nsw.gov.au/feeds/fdrToban.json"
    headers = {"User-Agent": "Outback_Early_Warning"}
    r = requests.get(url, timeout=10, headers=headers)
    r.raise_for_status()
    js = r.json()

    out: Dict[str, str] = {}
    for d in js.get("districts", []):
        name = (d.get("name") or "").strip()
        rating_raw = (d.get("todays_fire_danger_rating") or "").strip()
        if name and rating_raw:
            out[name] = _normalize_level(rating_raw)
    return out