import streamlit as st
from pdf_parser import extract_text_from_pdf

st.set_page_config(page_title="PDF Redactor", layout="centered")
st.title("📄 Incident PDF Redactor")

uploaded_file = st.file_uploader("Upload an Incident PDF", type="pdf")

if uploaded_file is not None:
    with st.spinner("Redacting..."):
        redacted_text = extract_text_from_pdf(uploaded_file)

    st.success("Redaction complete!")
    st.subheader("Redacted Output")
    st.text_area("Copy this and paste it into ChatGPT:", redacted_text, height=400)
