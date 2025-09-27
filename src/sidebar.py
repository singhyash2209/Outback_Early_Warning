import streamlit as st
from datetime import datetime

def render_sidebar():
    st.sidebar.header("Navigation")
    st.sidebar.page_link("Home.py", label="🏠 Home")
    st.sidebar.page_link("pages/1_My_Location.py", label="📍 My Location")
    st.sidebar.page_link("pages/2_Map.py", label="🗺️ Map")
    st.sidebar.page_link("pages/3_Feed.py", label="📰 Feed")
    st.sidebar.page_link("pages/4_ArcGIS_View.py", label="🧭 ArcGIS View (Silver)")
    st.sidebar.page_link("pages/5_Offline_Pack.py", label="📦 Offline Safety Pack")

    st.sidebar.divider()
    st.sidebar.caption("v0.1 • Last updated: " + datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"))