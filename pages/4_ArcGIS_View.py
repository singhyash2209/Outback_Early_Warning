import streamlit as st
st.header("🧭 ArcGIS View (Silver)")
st.write("When ready, this page embeds the ArcGIS Online Web Map or Dashboard.")
embed_url = st.text_input("Embed URL (paste from ArcGIS Online)", value="")
if embed_url:
    st.components.v1.iframe(embed_url, height=600)
else:
    st.info("We'll publish a Hosted Feature Layer + Web Map, then paste the embed URL here.")