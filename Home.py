import streamlit as st
from datetime import datetime

from src.utils_cache import cache_status_badge
from src.afdrs import get_today_ratings
from src.sidebar import render_sidebar   

st.set_page_config(
    page_title="AI in the Outback – Early Warning (NSW)",
    page_icon="🔥",
    layout="wide"
)

# --- Sidebar ---
render_sidebar()

# --- Disclaimer ---
st.warning(
    "This prototype aggregates official sources (NSW Rural Fire Service, Bureau of Meteorology). "
    "Always follow directions on official channels. This is NOT an official warning service."
)

st.title("AI in the Outback — Early Warning (NSW)")

st.caption(
    "NSW-first unified view: **My Location** risk score + **Map** layers + **Feed** of official alerts. "
    "Includes AFDRS (Australian Fire Danger Rating System) badge and plain-English actions."
)

# --- Data freshness badges ---
st.markdown("**Data freshness**")
cols = st.columns(3)

with cols[0]:
    cache_status_badge("NSW RFS incidents")

with cols[1]:
    cache_status_badge("BOM warnings (CAP)")

with cols[2]:
    try:
        ratings = get_today_ratings()  # prefetch
        if not ratings:
            st.markdown("⚪ **AFDRS ratings**: Data not available (official feed didn’t publish today)")
        else:
            cache_status_badge("AFDRS ratings")
    except Exception:
        st.markdown("⚪ **AFDRS ratings**: Error fetching feed")

st.divider()

# --- Intro text ---
st.subheader("Get started")
st.write("Use the sidebar to explore **My Location**, **Map**, and **Feed**. Low-bandwidth mode is available if needed.")