import pdfplumber
import re
import pyperclip
import streamlit as st

def redact_sensitive(text):
    text = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "[REDACTED IP]", text)
    text = re.sub(r"(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}", "[REDACTED MAC]", text)
    text = re.sub(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", "[REDACTED PHONE]", text)
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[REDACTED EMAIL]", text)
    text = re.sub(r"EVE\d{8}", "[REDACTED EMPLOYEE ID]", text)
    text = re.sub(r"IMEI[#\s]*\d+", "IMEI#[REDACTED]", text)
    text = re.sub(r"Account\s+\d{8,}(-\d+)?", "Account [REDACTED]", text)
    text = re.sub(r"https?://\S+", "[REDACTED URL]", text)
    # Redact last names but preserve first initial (e.g., "Robert Barraclough" → "Robert B.")
    text = re.sub(r"\b([A-Z][a-z]+)\s+([A-Z])[a-z]+\b", r"\1 \2.", text)
    return text

def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        full_text = "\n".join(
            page.extract_text() for page in pdf.pages if page.extract_text()
        )
    redacted = redact_sensitive(full_text)
    pyperclip.copy(redacted)
    return redacted

def run_redactor_gui():
    st.title("📄 PDF Redactor")
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file is not None:
        with pdfplumber.open(uploaded_file) as pdf:
            full_text = "\n".join(
                page.extract_text() for page in pdf.pages if page.extract_text()
            )
        redacted = redact_sensitive(full_text)
        st.text_area("🔒 Redacted Content", redacted, height=400)

        if st.button("📋 Copy to Clipboard"):
            pyperclip.copy(redacted)
            st.success("Redacted content copied to clipboard!")

