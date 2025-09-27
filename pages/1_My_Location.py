import streamlit as st

from src.location import geocode_nominatim, detect_district, nsw_district_names
from src.afdrs import get_today_rating_for_district
from src.risk_model import compute_risk_for_query
from src.ui_text import actions_for_afdrs, explain_badges
from src.sidebar import render_sidebar
render_sidebar()

st.header("📍 My Location")

# --- Input ---
q = st.text_input("Enter town / postcode (NSW)", placeholder="e.g., Bathurst")

auto_latlon = None
auto_district = None

# --- Geocode + suggest district ---
if st.button("Check location"):
    if q.strip():
        geo = geocode_nominatim(q.strip())
        if geo:
            lat, lon, name = geo
            st.success(f"Found: **{name}** (lat {lat:.3f}, lon {lon:.3f})")
            auto_latlon = (lat, lon)
            auto_district = detect_district(lat, lon)
        else:
            st.error("Could not geocode your query. Try a different town/postcode in NSW.")

# --- AFDRS district chooser (with auto-detect preselection if available) ---
st.subheader("AFDRS District")
districts = ["(Select district)"] + nsw_district_names()
default_idx = 0
if auto_district and auto_district in nsw_district_names():
    default_idx = districts.index(auto_district) if auto_district in districts else 0

chosen = st.selectbox(
    "Choose your AFDRS district (auto-detection is approximate; override if needed)",
    districts,
    index=default_idx
)

st.caption("Auto-detection is approximate. If it looks off, choose your district manually.")

# --- Show today's AFDRS rating + actions ---
selected_district = None if chosen == "(Select district)" else chosen
if selected_district:
    rating = get_today_rating_for_district(selected_district)
    if rating.level and rating.level != "Unknown":
        st.success(f"AFDRS today in **{selected_district}**: **{rating.level}**")
        st.markdown(actions_for_afdrs(rating.level))
    else:
        st.info(f"AFDRS rating for **{selected_district}** is not available right now.")

# --- Risk prototype (uses AFDRS weighting when district is chosen) ---
st.subheader("Local Risk (prototype)")
if q.strip():
    res = compute_risk_for_query(q.strip(), district=selected_district)
    st.metric("Risk score (0–1)", f"{res.score:.2f}")
    for t in res.tags:
        st.write("•", t)
else:
    st.caption("Enter a town/postcode above to see a risk score prototype.")