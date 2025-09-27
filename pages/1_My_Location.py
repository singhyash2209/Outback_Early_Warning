import streamlit as st
from src.risk_model import compute_risk_for_query
from src.afdrs import get_today_rating_for_district
from src.ui_text import actions_for_afdrs, explain_badges

st.header("📍 My Location")
q = st.text_input("Enter town / postcode (NSW)", placeholder="e.g., Bathurst")
if st.button("Check risk") and q.strip():
    risk = compute_risk_for_query(q.strip())
    st.metric("Risk score (0–1)", f"{risk.score:.2f}")
    st.write(explain_badges(risk))
    if risk.district:
        rating = get_today_rating_for_district(risk.district)
        st.success(f"AFDRS today in {risk.district}: **{rating.level}**")
        st.markdown(actions_for_afdrs(rating.level))
    else:
        st.info("Couldn’t resolve an AFDRS district for this location yet.")