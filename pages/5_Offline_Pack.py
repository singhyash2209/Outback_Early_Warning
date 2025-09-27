import streamlit as st
from src.offline_pack import generate_pdf_and_csv

st.header("📦 Offline Safety Pack")
st.write("Download a printable checklist and key contacts for NSW (for low-connectivity situations).")
if st.button("Generate pack"):
    pdf_path, csv_path = generate_pdf_and_csv()
    st.success("Pack generated.")
    st.download_button("Download Checklist (PDF)", open(pdf_path, "rb"), file_name="nsw_offline_checklist.pdf")
    st.download_button("Download Contacts (CSV)", open(csv_path, "rb"), file_name="nsw_contacts.csv")