import streamlit as st
from datetime import datetime

from src.fetch_rfs_nsw import get_rfs_feed
from src.fetch_bom import get_bom_feed

st.header("📰 Unified Feed")

# Fetch
rfs_feed = get_rfs_feed()      # Bushfire incidents
bom_feed = get_bom_feed()      # BOM warnings

combined = rfs_feed + bom_feed

def _key_time(item):
    return item.get("time") or ""

def _fmt(ts: str):
    # Accepts ISO like 2025-09-27T12:34:00Z, returns 'YYYY-MM-DD HH:MM UTC'
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return ts or ""

combined = sorted(combined, key=_key_time, reverse=True)

filter_opt = st.selectbox("Filter", ["All", "Bushfire", "Flood", "Severe Weather"], index=0)

def _passes_filter(item, f):
    if f == "All":
        return True
    title = (item.get("title") or "").lower()
    summary = (item.get("summary") or "").lower()
    txt = f"{title} {summary}"
    if f == "Bushfire":
        return ("fire" in txt) or ("bushfire" in txt) or ("nsw rfs" in txt)
    if f == "Flood":
        return "flood" in txt
    if f == "Severe Weather":
        return ("storm" in txt) or ("severe" in txt) or ("wind" in txt) or ("weather" in txt)
    return True

visible = [x for x in combined if _passes_filter(x, filter_opt)]

if not visible:
    st.info("No items match this filter yet.")
else:
    for item in visible[:200]:
        title = item.get("title", "Untitled")
        time_str = _fmt(item.get("time", ""))
        summary = item.get("summary", "")
        url = item.get("url")

        with st.expander(f"{time_str} • {title}"):
            if summary:
                st.write(summary)
            if url:
                st.markdown(f"[Official link]({url})")