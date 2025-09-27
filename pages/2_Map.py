import streamlit as st
import pydeck as pdk
import json

from src.fetch_rfs_nsw import get_rfs_points
from src.fetch_bom import get_bom_polygons
from src.fetch_firms import get_firms_points  # optional (only used if toggled)
from src.geo_utils import to_pydeck_layer_polygons

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
    # Only allow FIRMS if not in low-bandwidth mode
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

# Status line (quick data counts)
st.caption(f"Incidents: **{len(rfs_points)}** • BOM polygons: **{len(bom_polys)}**")

# ───────────────────────────────────────────────────────────────────────────────
# Prep layers
# ───────────────────────────────────────────────────────────────────────────────
layers = []

# Color incidents by status (red = Out of Control, orange = Being Controlled, green = other)
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
        r["radius_m"] = radius_value        # set from slider
        styled.append(r)
    return styled

# NSW RFS incident points (with slider-defined radius)
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

# BOM warning polygons
if show_bom and bom_polys:
    layers += to_pydeck_layer_polygons(bom_polys, name="BOM Warnings")

# FIRMS (optional heatmap)
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
# Map render (Carto basemap, no token needed) + rich tooltip incl. Updated time
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

# ───────────────────────────────────────────────────────────────────────────────
# Export incidents (GeoJSON-like) — handy for ArcGIS Online
# ───────────────────────────────────────────────────────────────────────────────
if rfs_points:
    geojson_like = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [p["lon"], p["lat"]]},
                "properties": {k: v for k, v in p.items() if k not in ("lat", "lon")}
            }
            for p in rfs_points
        ]
    }
    st.download_button(
        "⬇️ Download incidents (GeoJSON-like)",
        data=json.dumps(geojson_like),
        file_name="nsw_rfs_incidents.json",
        mime="application/json"
    )

# ───────────────────────────────────────────────────────────────────────────────
# Empty state (clear, human)
# ───────────────────────────────────────────────────────────────────────────────
if show_rfs and not rfs_points and show_bom and not bom_polys:
    st.info("No current major incidents reported by NSW RFS and no active BOM warnings for NSW at this moment.")