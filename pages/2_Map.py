import streamlit as st
import pydeck as pdk

from src.fetch_rfs_nsw import get_rfs_points
from src.fetch_bom import get_bom_polygons
from src.fetch_firms import get_firms_points  # optional later
from src.geo_utils import to_pydeck_layer_points, to_pydeck_layer_polygons

st.header("🗺️ Map")

# Fetch data
rfs_points = get_rfs_points()
bom_polys = get_bom_polygons()
firms_points = None if st.session_state.get("low_bw") else get_firms_points()

# Quick status
st.caption(f"Incidents loaded: **{len(rfs_points)}** • BOM polygons: **{len(bom_polys)}**")

# NSW viewport
initial_view = pdk.ViewState(latitude=-32.5, longitude=147.0, zoom=5)

# Build layers
layers = []
layers += to_pydeck_layer_points(rfs_points, name="NSW RFS Incidents")
if bom_polys:
    layers += to_pydeck_layer_polygons(bom_polys, name="BOM Warnings")
if firms_points:
    layers += to_pydeck_layer_points(firms_points, name="NASA FIRMS Hotspots", heat=True)

# Render deck with CARTO basemap (no token needed)
deck = pdk.Deck(
    map_provider="carto",
    map_style="light",
    initial_view_state=initial_view,
    layers=layers,
    tooltip={"text": "{title}\nStatus: {status}\nSource: {source}"}
)

st.pydeck_chart(deck)

# Empty state messages
if not rfs_points and not bom_polys:
    st.info("No NSW RFS incidents or BOM warnings available right now. This will populate automatically when data is available.")