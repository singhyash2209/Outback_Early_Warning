import streamlit as st

from datetime import datetime
from src.utils_cache import cache_status_badge

st.set_page_config(page_title="AI in the Outback – Early Warning (NSW)",
                   page_icon="🔥",
                   layout="wide")

# Disclaimer
st.warning("This prototype aggregates official sources (NSW Rural Fire Service, Bureau of Meteorology). "
           "Always follow directions on official channels. This is NOT an official warning service.")

st.title("AI in the Outback — Early Warning (NSW)")

st.caption("NSW-first unified view: **My Location** risk score + **Map** layers + **Feed** of official alerts. "
           "Includes AFDRS (Australian Fire Danger Rating System) badge and plain-English actions.")

# Data freshness (wired later)
with st.container():
    st.markdown("**Data freshness**")
    cols = st.columns(3)
    with cols[0]:
        cache_status_badge("NSW RFS incidents")
    with cols[1]:
        cache_status_badge("BOM warnings (CAP)")
    with cols[2]:
        cache_status_badge("AFDRS ratings")

st.divider()

st.subheader("Get started")
st.markdown("Use the sidebar to switch between **My Location**, **Map**, and **Feed** pages. "
            "Low-bandwidth mode available in the sidebar.")

st.sidebar.header("Navigation")
st.sidebar.page_link("pages/1_My_Location.py", label="📍 My Location")
st.sidebar.page_link("pages/2_Map.py", label="🗺️ Map")
st.sidebar.page_link("pages/3_Feed.py", label="📰 Feed")
st.sidebar.toggle("Low-bandwidth mode", key="low_bw", help="Disable heavy layers for slow internet.")

st.sidebar.header("Extras")
st.sidebar.page_link("pages/4_ArcGIS_View.py", label="🧭 ArcGIS View (Silver)")
st.sidebar.page_link("pages/5_Offline_Pack.py", label="📦 Offline Safety Pack")

st.sidebar.caption("v0.1 • Last updated: " + datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"))