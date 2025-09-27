import streamlit as st
from src.location import geocode_nominatim, detect_district, nsw_district_names
from src.afdrs import get_today_rating_for_district
from src.risk_model import compute_risk_for_query
from src.ui_text import actions_for_afdrs, explain_badges

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

# 👇 tiny, human hint (as requested)
st.caption("Auto-detection is approximate. If it looks off, choose your district manually.")

# --- Show today's AFDRS rating + actions ---
if chosen != "(Select district)":
    rating = get_today_rating_for_district(chosen)
    if rating.level and rating.level != "Unknown":
        st.success(f"AFDRS today in **{chosen}**: **{rating.level}**")
        st.markdown(actions_for_afdrs(rating.level))
    else:
        st.info(f"AFDRS rating for **{chosen}** is not available right now.")

# --- Risk prototype (will be upgraded in Phase 5) ---
st.subheader("Local Risk (prototype)")
if q.strip():
    risk = compute_risk_for_query(q.strip())
    st.metric("Risk score (0–1)", f"{risk.score:.2f}")
    st.write(explain_badges(risk))
else:
    st.caption("Enter a town/postcode above to see a risk score prototype.")