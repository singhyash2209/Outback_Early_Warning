import requests
from bs4 import BeautifulSoup
from src.utils_cache import update_cache_time

def get_bom_polygons():
    """Fetch BOM warnings polygons for map display."""
    url = "http://www.bom.gov.au/fwo/IDZ00059.warnings_nsw.xml"
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.content, "xml")
    except Exception as e:
        print("Error fetching BOM warnings:", e)
        return []

    polys = []
    for area in soup.find_all("area"):
        polygon_text = area.find("polygon")
        if not polygon_text:
            continue
        coords = []
        for pair in polygon_text.text.split(" "):
            try:
                lat, lon = pair.split(",")
                coords.append([float(lon), float(lat)])
            except:
                continue
        if coords:
            polys.append({
                "polygon": coords,
                "fill_r": 255, "fill_g": 165, "fill_b": 0,  # orange
                "title": area.find("areaDesc").text if area.find("areaDesc") else "BOM Area"
            })

    update_cache_time("BOM warnings (CAP)")
    return polys


def get_bom_feed():
    """Fetch BOM warning feed items for list display."""
    url = "http://www.bom.gov.au/fwo/IDZ00059.warnings_nsw.xml"
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.content, "xml")
    except Exception as e:
        print("Error fetching BOM warnings feed:", e)
        return []

    feed = []
    for info in soup.find_all("info"):
        headline = info.find("headline").text if info.find("headline") else "BOM Warning"
        effective = info.find("effective").text if info.find("effective") else ""
        link = soup.find("identifier").text if soup.find("identifier") else ""

        feed.append({
            "time": effective,
            "title": headline,
            "summary": "Issued by Bureau of Meteorology",
            "url": "http://www.bom.gov.au/nsw/warnings/"
        })

    update_cache_time("BOM warnings (CAP)")
    return feed