import streamlit as st 
import pydeck as pdk
import json
import datetime as dt

from src.fetch_rfs_nsw import get_rfs_points
from src.fetch_bom import get_bom_polygons
from src.fetch_firms import get_firms_points
from src.geo_utils import to_pydeck_layer_polygons
from src.sidebar import render_sidebar
render_sidebar()

st.header("🗺️ Map")

# ───────────────────────────────────────────────────────────────────────────────
# Controls (now with a marker-size slider)
# ───────────────────────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 2, 1])

with col1:
    show_rfs = st.checkbox("NSW RFS incidents", True)

with col2:
    show_bom = st.checkbox("BOM warnings", True)

with col3:
    show_firms = False if st.session_state.get("low_bw") else st.checkbox("NASA FIRMS hotspots", False)

with col4:
    if st.button("🔄 Refresh data"):
        st.rerun()

with col5:
    radius_m = st.slider("Marker size", min_value=2000, max_value=8000, value=4500, step=500)

# ───────────────────────────────────────────────────────────────────────────────
# Fetch data
# ───────────────────────────────────────────────────────────────────────────────
rfs_points = get_rfs_points()
bom_polys = get_bom_polygons()
firms_points = get_firms_points() if show_firms else None

st.caption(f"Incidents: **{len(rfs_points)}** • BOM polygons: **{len(bom_polys)}**")

# ───────────────────────────────────────────────────────────────────────────────
# Prep layers
# ───────────────────────────────────────────────────────────────────────────────
layers = []

def _apply_point_styles(records, radius_value):
    styled = []
    for r in records:
        s = (r.get("status") or "").lower()
        if "out of control" in s:
            r["color"] = [230, 57, 70]       # red
        elif "being controlled" in s:
            r["color"] = [255, 165, 0]       # orange
        else:
            r["color"] = [34, 139, 34]       # green
        r["radius_m"] = radius_value
        # Normalize status label
        r["status"] = r.get("status") or "No official status published"
        styled.append(r)
    return styled

# NSW RFS incidents
if show_rfs and rfs_points:
    styled_points = _apply_point_styles(list(rfs_points), radius_m)
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=styled_points,
            get_position='[lon, lat]',
            get_radius='radius_m',
            filled=True,
            pickable=True,
            get_fill_color='color',
            get_line_color=[30, 30, 30],
            line_width_min_pixels=1,
        )
    )

# BOM polygons
if show_bom and bom_polys:
    layers += to_pydeck_layer_polygons(bom_polys, name="BOM Warnings")

# FIRMS hotspots
if show_firms and firms_points:
    layers.append(
        pdk.Layer(
            "HeatmapLayer",
            data=firms_points,
            get_position='[lon, lat]',
            get_weight='weight',
            aggregation='MEAN',
            opacity=0.4
        )
    )

# ───────────────────────────────────────────────────────────────────────────────
# Map render
# ───────────────────────────────────────────────────────────────────────────────
initial_view = pdk.ViewState(latitude=-32.5, longitude=147.0, zoom=5)

deck = pdk.Deck(
    map_provider="carto",
    map_style="light",
    initial_view_state=initial_view,
    layers=layers,
    tooltip={
        "html": "<b>{title}</b><br>Status: {status}<br>Updated: {updated}<br>Source: {source}",
        "style": {"backgroundColor": "white", "color": "black"}
    }
)

st.pydeck_chart(deck)
st.caption("Color key: red = Out of control • orange = Being Controlled • green = Other/Advice")

# ───────────────────────────────────────────────────────────────────────────────
# Export incidents (GeoJSON-like)
# ───────────────────────────────────────────────────────────────────────────────
if rfs_points:
    features = []
    for p in rfs_points:
        lat, lon = p.get("lat"), p.get("lon")
        if lat is None or lon is None:
            continue
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                "title": p.get("title"),
                "status": p.get("status") or "No official status published",
                "updated": p.get("updated") or "",
                "url": p.get("url"),
                "source": "NSW RFS",
                "color": p.get("color"),
                "radius": p.get("radius_m", radius_m)
            }
        })

    payload = {
        "type": "FeatureCollection",
        "generated_at_utc": dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "features": features
    }

    st.download_button(
        "⬇️ Download incidents (GeoJSON-like)",
        data=json.dumps(payload, indent=2),
        file_name="nsw_rfs_incidents.json",
        mime="application/json"
    )

# ───────────────────────────────────────────────────────────────────────────────
# Empty state
# ───────────────────────────────────────────────────────────────────────────────
if show_rfs and not rfs_points and show_bom and not bom_polys:
    st.info("No current major incidents reported by NSW RFS and no active BOM warnings for NSW at this moment.")