import requests

def geocode_nominatim(query: str):
    """Return (lat, lon, display_name) using OSM Nominatim."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query + ", NSW, Australia", "format": "json", "limit": 1}
    try:
        r = requests.get(url, params=params, headers={"User-Agent": "Outback_Early_Warning"}, timeout=10)
        r.raise_for_status()
        js = r.json()
        if not js:
            return None
        lat = float(js[0]["lat"]); lon = float(js[0]["lon"]); name = js[0]["display_name"]
        return lat, lon, name
    except Exception as e:
        print("Geocode error:", e)
        return None


# Very rough NSW AFDRS district bounding boxes for a demo-grade auto-detect.
# Each entry: name, lat_min, lat_max, lon_min, lon_max
AFDRS_BBOXES = [
    ("Greater Sydney",              -34.30, -32.80, 149.50, 151.50),
    ("Greater Hunter",              -33.50, -31.50, 150.00, 152.00),
    ("Illawarra Shoalhaven",       -35.50, -34.00, 149.80, 151.20),
    ("Far South Coast",            -37.50, -36.00, 149.00, 150.50),
    ("Monaro Alpine",              -37.00, -35.50, 147.00, 149.50),
    ("Southern Ranges",            -36.20, -34.20, 147.00, 150.00),
    ("Central Ranges",             -33.90, -31.90, 148.00, 150.50),
    ("New England and N. Tablelands", -31.60, -28.50, 149.50, 152.50),
    ("Northern Rivers",            -29.80, -28.00, 152.80, 153.60),
    ("Mid North Coast",            -32.30, -29.90, 151.50, 153.20),
    ("North Western",              -32.00, -28.00, 147.00, 150.00),
    ("Upper Central West Plains",  -33.00, -31.50, 146.00, 149.00),
    ("Lower Central West Plains",  -34.50, -33.00, 146.00, 149.00),
    ("Riverina",                   -36.50, -33.80, 144.00, 148.00),
    ("South Western",              -35.50, -33.00, 140.80, 144.80),
]

def detect_district(lat: float, lon: float) -> str | None:
    for name, la_min, la_max, lo_min, lo_max in AFDRS_BBOXES:
        if la_min <= lat <= la_max and lo_min <= lon <= lo_max:
            return name
    return None

def nsw_district_names() -> list[str]:
    return [x[0] for x in AFDRS_BBOXES]