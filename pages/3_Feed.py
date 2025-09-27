import streamlit as st
from src.fetch_bom import get_bom_feed
from src.fetch_rfs_nsw import get_rfs_feed

st.header("📰 Unified Feed")

filter_opt = st.selectbox("Filter", ["All", "Bushfire", "Flood", "Severe Weather"])
feed = get_bom_feed() + get_rfs_feed()
# TODO: sort by datetime, apply filter
for item in feed[:200]:
    with st.expander(f"{item['time']} • {item['title']}"):
        st.write(item['summary'])
        if 'url' in item: st.markdown(f"[Official link]({item['url']})")