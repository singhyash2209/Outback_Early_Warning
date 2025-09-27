import streamlit as st
import datetime

# placeholder for now
_last_update = {}

def update_cache_time(name: str):
    _last_update[name] = datetime.datetime.utcnow()

def cache_status_badge(name: str):
    ts = _last_update.get(name)
    if ts:
        age = (datetime.datetime.utcnow() - ts).seconds // 60
        st.markdown(f"✅ **{name}**: updated {age} min ago (UTC)")
    else:
        st.markdown(f"⚪ **{name}**: not fetched yet")