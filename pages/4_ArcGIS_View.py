import json
import re
import datetime as dt
import streamlit as st
from streamlit.components.v1 import html as st_html

from src.sidebar import render_sidebar
from src.fetch_rfs_nsw import get_rfs_points

render_sidebar()

st.header("🧭 ArcGIS View")
st.caption("Export incidents for ArcGIS Online and embed a live ArcGIS map. Paste a Web Map ID/URL or a Hosted Feature Layer / GeoJSON URL.")

# Build ArcGIS-ready GeoJSON (skip null coords + timestamp)
rfs_points = get_rfs_points() or []
features = []
for p in rfs_points:
    lat, lon = p.get("lat"), p.get("lon")
    if lat is None or lon is None:
        continue
    features.append({
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [float(lon), float(lat)]},
        "properties": {
            "title": p.get("title"),
            "status": p.get("status") or "No official status published",
            "updated": p.get("updated") or "",
            "url": p.get("url"),
            "source": p.get("source") or "NSW RFS"
        }
    })

payload = {
    "type": "FeatureCollection",
    "generated_at_utc": dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
    "features": features
}

left, right = st.columns([2, 1], vertical_alignment="center")
with left:
    st.subheader("Export incidents (GeoJSON)")
    st.caption("Upload this file to ArcGIS Online and add it to a Web Map.")
    st.write(f"Features ready: **{len(features)}**")
    st.download_button(
        "⬇️ Download incidents (GeoJSON-like)",
        data=json.dumps(payload, indent=2),
        file_name="nsw_rfs_incidents.json",
        mime="application/json",
        use_container_width=True
    )

with right:
    st.subheader("Color key")
    st.caption("Red = Out of control\n\nOrange = Being controlled\n\nGreen = Other/Advice")

st.divider()
st.subheader("Embed an ArcGIS map (live)")
st.caption("Option A: paste a Web Map ID or a Map Viewer URL with ?webmap=…  •  Option B: paste a Hosted Feature Layer / GeoJSON URL.")

colA, colB = st.columns(2)

def _extract_webmap_id(text: str) -> str | None:
    if not text:
        return None
    text = text.strip()
    if re.fullmatch(r"[A-Za-z0-9]{32}", text):
        return text
    m = re.search(r"[?&]webmap=([A-Za-z0-9]{32})", text)
    if m:
        return m.group(1)
    return None

with colA:
    wm_input = st.text_input(
        "Web Map ID or Map Viewer URL",
        placeholder="e.g. 1234567890abcdef1234567890abcdef or https://www.arcgis.com/apps/mapviewer/index.html?webmap=<ID>&embed=true"
    )
    webmap_id = _extract_webmap_id(wm_input)

with colB:
    layer_url = st.text_input(
        "Hosted Feature Layer / GeoJSON URL",
        placeholder="e.g. https://services.arcgis.com/.../FeatureServer/0  or  https://.../your.geojson"
    ).strip()
    if layer_url:
        viewer_link = f"https://www.arcgis.com/apps/mapviewer/index.html?layers={layer_url}"
        st.link_button("Open in ArcGIS Map Viewer", viewer_link, use_container_width=True)

def _webmap_html(item_id: str) -> str:
    return f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="initial-scale=1,maximum-scale=1,user-scalable=no"/>
  <link rel="stylesheet" href="https://js.arcgis.com/4.29/esri/themes/dark/main.css"/>
  <script src="https://js.arcgis.com/4.29/"></script>
  <style>html,body,#viewDiv{{height:100%;margin:0;padding:0;}}</style>
</head>
<body>
<div id="viewDiv"></div>
<script>
require(["esri/WebMap","esri/views/MapView"], (WebMap, MapView) => {{
  const webmap = new WebMap({{ portalItem: {{ id: "{item_id}" }} }});
  new MapView({{ container: "viewDiv", map: webmap }});
}});
</script>
</body>
</html>
""".strip()

def _layer_html(url: str) -> str:
    js_layer_block = (
        f'const lyr = new GeoJSONLayer({{ url: "{url}" }});'
        if url.lower().endswith(".geojson") or "geojson" in url.lower()
        else f'const lyr = new FeatureLayer({{ url: "{url}" }});'
    )
    return f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="initial-scale=1,maximum-scale=1,user-scalable=no"/>
  <link rel="stylesheet" href="https://js.arcgis.com/4.29/esri/themes/dark/main.css"/>
  <script src="https://js.arcgis.com/4.29/"></script>
  <style>html,body,#viewDiv{{height:100%;margin:0;padding:0;}}</style>
</head>
<body>
<div id="viewDiv"></div>
<script>
require(["esri/Map","esri/views/MapView","esri/layers/FeatureLayer","esri/layers/GeoJSONLayer"], (Map, MapView, FeatureLayer, GeoJSONLayer) => {{
  const map = new Map({{ basemap: "gray-vector" }});
  const view = new MapView({{ container: "viewDiv", map, center: [147, -32.5], zoom: 5 }});
  {js_layer_block}
  map.add(lyr);
}});
</script>
</body>
</html>
""".strip()

viewer_rendered = False
if webmap_id:
    st.success("Web Map detected — loading viewer ⤵")
    st_html(_webmap_html(webmap_id), height=750)
    viewer_rendered = True
elif layer_url:
    st.success("Layer URL detected — loading viewer ⤵")
    st_html(_layer_html(layer_url), height=750)
    viewer_rendered = True

if not viewer_rendered:
    with st.expander("How to publish & embed in ArcGIS (quick steps)"):
        st.markdown(
            """
**Web Map**
1. In ArcGIS Online → Content → New Item → Your device → upload `nsw_rfs_incidents.json`.
2. Open in Map Viewer, style, Save, Share (public).
3. Paste the Web Map ID or Map Viewer URL above.

**Layer URL**
Paste a public FeatureServer/0 or MapServer/0 layer URL, or a .geojson URL; it will load directly here.
            """
        )