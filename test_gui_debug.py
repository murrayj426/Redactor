#!/usr/bin/env python3
"""
Debug script to test GUI provider options
"""

import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.title("GUI Debug Test")

# Test the exact same selectbox code
st.header("Provider Selection Test")

ai_provider = st.selectbox(
    "AI Provider",
    ["Claude (Anthropic) - Recommended", "OpenAI"],
    help="Claude 3.5 Sonnet provides superior compliance reasoning for Network Team audits"
)

st.write(f"Selected provider: {ai_provider}")

# Check imports
st.header("Import Test")
try:
    from openai_auditor import TicketAuditor
    st.success("✅ OpenAI auditor imported successfully")
except Exception as e:
    st.error(f"❌ OpenAI import failed: {e}")

try:
    from claude_auditor import ClaudeAuditor
    st.success("✅ Claude auditor imported successfully")
except Exception as e:
    st.error(f"❌ Claude import failed: {e}")

# Check API keys
st.header("API Key Test")
env_openai_key = os.getenv('OPENAI_API_KEY', '')
env_anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')

if env_openai_key:
    st.success(f"✅ OpenAI API Key found (length: {len(env_openai_key)})")
else:
    st.warning("⚠️ No OpenAI API Key found")

if env_anthropic_key:
    st.success(f"✅ Anthropic API Key found (length: {len(env_anthropic_key)})")
else:
    st.warning("⚠️ No Anthropic API Key found")
