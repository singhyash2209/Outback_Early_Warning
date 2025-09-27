import streamlit as st
import datetime

_last_update = {}  # name -> datetime.utcnow()

def update_cache_time(name: str):
    _last_update[name] = datetime.datetime.utcnow()

def _fmt_utc(dt: datetime.datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M UTC")

def cache_status_badge(name: str):
    ts = _last_update.get(name)
    if ts:
        age_min = int((datetime.datetime.utcnow() - ts).total_seconds() // 60)
        when = _fmt_utc(ts)
        st.markdown(f"✅ **{name}**: updated {age_min} min ago • _{when}_")
    else:
        st.markdown(f"⚪ **{name}**: not fetched yet")