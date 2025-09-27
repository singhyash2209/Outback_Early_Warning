from pathlib import Path

def generate_pdf_and_csv():
    out_pdf = Path("data") / "nsw_offline_checklist.pdf"
    out_csv = Path("data") / "nsw_contacts.csv"
    out_pdf.write_bytes(b"%PDF-1.4 placeholder checklist")
    out_csv.write_text("name,phone,url\nNSW RFS,000,https://www.rfs.nsw.gov.au\nBOM,NA,https://www.bom.gov.au\n")
    return str(out_pdf), str(out_csv)