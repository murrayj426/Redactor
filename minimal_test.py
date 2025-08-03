#!/usr/bin/env python3
"""
Minimal test to reproduce the provider dropdown issue
"""

import streamlit as st

st.title("Minimal Provider Test")

# Test with exact same structure as main GUI
col1, col2 = st.columns([2, 1])

with col1:
    st.write("Testing provider dropdown...")
    
    # Exact same selectbox code
    ai_provider = st.selectbox(
        "AI Provider",
        ["Claude (Anthropic) - Recommended", "OpenAI"],
        help="Claude 3.5 Sonnet provides superior compliance reasoning for Network Team audits"
    )
    
    st.write(f"Selected: {ai_provider}")
    st.write("Available options:", ["Claude (Anthropic) - Recommended", "OpenAI"])

with col2:
    st.write("Column 2 test")
