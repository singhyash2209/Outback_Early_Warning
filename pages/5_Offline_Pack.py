import streamlit as st
from pathlib import Path
import json

from src.offline_pack import generate_pdf_and_csv
from src.sidebar import render_sidebar
render_sidebar()

st.header("📦 Offline Safety Pack")

st.write(
    "Download a printable checklist and key contacts for NSW (for low-connectivity situations). "
    "You can also quickly copy numbers or add a vCard."
)

# Quick-copy contacts
contacts = [
    {"name": "Emergency (Fire/Police/Ambulance)", "phone": "000", "url": "tel:000"},
    {"name": "NSW RFS Bush Fire Information Line", "phone": "1800679377", "url": "tel:1800679377"},
    {"name": "SES (Flood/Storm)", "phone": "132500", "url": "tel:132500"},
    {"name": "Bureau of Meteorology", "phone": "", "url": "https://www.bom.gov.au"},
]

st.subheader("☏ Quick contacts")
for c in contacts:
    cols = st.columns([3,2,2,2])
    with cols[0]:
        st.write(f"**{c['name']}**")
    with cols[1]:
        if c["phone"]:
            st.code(c["phone"])  # gives a copy button
        else:
            st.write("-")
    with cols[2]:
        link = c["url"] or ""
        if link.startswith("tel:"):
            st.markdown(f"[Call]({link})")
        elif link:
            st.markdown(f"[Open site]({link})")
        else:
            st.write("-")
    with cols[3]:
        # Simple vCard download for phone contacts
        if c["phone"]:
            vcf = (
                "BEGIN:VCARD\nVERSION:3.0\n"
                f"N:{c['name']};;;;\nFN:{c['name']}\n"
                f"TEL;TYPE=voice,home,pref:{c['phone']}\n"
                "END:VCARD\n"
            ).encode("utf-8")
            st.download_button(
                "Add to phone (vCard)",
                data=vcf,
                file_name=f"{c['name'].replace(' ','_')}.vcf",
                mime="text/vcard"
            )

st.divider()

if st.button("📄 Generate printable pack"):
    pdf_path, csv_path = generate_pdf_and_csv()
    st.success("Pack generated.")
    st.download_button("Download Checklist (PDF)", open(pdf_path, "rb"), file_name="nsw_offline_checklist.pdf")
    st.download_button("Download Contacts (CSV)", open(csv_path, "rb"), file_name="nsw_contacts.csv")