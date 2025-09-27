import streamlit as st
import pydeck as pdk
from src.fetch_rfs_nsw import get_rfs_points
from src.fetch_bom import get_bom_polygons
from src.fetch_firms import get_firms_points  # optional
from src.geo_utils import to_pydeck_layer_points, to_pydeck_layer_polygons

st.header("🗺️ Map")

rfs = get_rfs_points()
bom = get_bom_polygons()
firms = None if st.session_state.get("low_bw") else get_firms_points()

initial_view = pdk.ViewState(latitude=-33.8688, longitude=151.2093, zoom=5)

layers = []
layers += to_pydeck_layer_points(rfs, name="NSW RFS Incidents")
layers += to_pydeck_layer_polygons(bom, name="BOM Warnings")
if firms is not None:
    layers += to_pydeck_layer_points(firms, name="NASA FIRMS Hotspots", heat=True)

st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=initial_view,
    layers=layers,
    tooltip={"text": "{title}\n{status}\n{source}"}
))