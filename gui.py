import streamlit as st
from pdf_parser import extract_text_from_pdf
from openai_auditor import TicketAuditor
from claude_auditor import ClaudeAuditor
import os
from dotenv import load_dotenv

# Load environment variables at startup
load_dotenv()

st.set_page_config(page_title="PDF Redactor & Network Team Auditor", layout="wide")
st.title("📄 Incident PDF Redactor & Network Team AI Auditor")

st.markdown("---")
st.header("🤖 Configuration")

# Check if API keys are already loaded from .env
env_openai_key = os.getenv('OPENAI_API_KEY', '')
env_anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')

col1, col2 = st.columns([2, 1])

with col1:
    # AI Provider Selection - Claude as default
    ai_provider = st.selectbox(
        "AI Provider",
        ["Claude (Anthropic) - Recommended", "OpenAI"],
        help="Claude 3.5 Sonnet provides superior compliance reasoning for Network Team audits"
    )
    
    # Initialize variables
    api_key_input = ""
    anthropic_key = ""
    
    # API Key handling based on provider
    if ai_provider == "OpenAI":
        if env_openai_key:
            st.success("✅ OpenAI API Key loaded from .env file")
            api_key_input = env_openai_key
            # Optional override
            override_key = st.text_input("Override OpenAI API Key (optional)", type="password", 
                                       placeholder="Leave blank to use .env key")
            if override_key:
                api_key_input = override_key
        else:
            api_key_input = st.text_input("OpenAI API Key", type="password", 
                                        help="Get your API key from OpenAI")
        
        if api_key_input:
            os.environ['OPENAI_API_KEY'] = api_key_input
            
    else:  # Claude (default)
        if env_anthropic_key and env_anthropic_key != 'your_anthropic_api_key_here':
            st.success("✅ Claude API Key loaded from .env file")
            anthropic_key = env_anthropic_key
            # Optional override
            override_key = st.text_input("Override Claude API Key (optional)", type="password", 
                                       placeholder="Leave blank to use .env key")
            if override_key:
                anthropic_key = override_key
        else:
            anthropic_key = st.text_input(
                "Claude API Key", 
                type="password",
                help="Get your API key from https://console.anthropic.com/"
            )
        
        if anthropic_key:
            os.environ['ANTHROPIC_API_KEY'] = anthropic_key

with col2:
    if ai_provider == "OpenAI":
        # Use default model from .env if available
        default_model = os.getenv('DEFAULT_MODEL', 'gpt-4o-mini')
        model_options = ["gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"]
        
        # Set default index based on .env setting
        try:
            default_index = model_options.index(default_model)
        except ValueError:
            default_index = 0
            
        model_choice = st.selectbox(
            "OpenAI Model",
            model_options,
            index=default_index,
            help="Select which model to use for auditing.",
            format_func=lambda x: {
                "gpt-3.5-turbo": "GPT-3.5-turbo (Faster, Higher Limits)",
                "gpt-4o-mini": "GPT-4o-mini (New, Efficient)",
                "gpt-4": "GPT-4 (Most Capable)"
            }[x]
        )
    else:  # Claude (default)
        model_choice = st.selectbox(
            "Claude Model",
            ["claude-3-5-sonnet-20241022"],
            help="Claude 3.5 Sonnet - Superior compliance reasoning and procedural analysis",
            format_func=lambda x: "Claude 3.5 Sonnet (Best for Compliance)"
        )

st.markdown("**Audit Standard**: Network Team Incident Management Documentation")
st.divider()

# File upload section
st.header("📄 Document Processing")
uploaded_file = st.file_uploader("Upload an Incident PDF", type="pdf")

if uploaded_file is not None:
    with st.spinner("Processing PDF and applying redaction..."):
        # Save uploaded file temporarily
        with open("temp_uploaded.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Extract and redact text
        redacted_text, redaction_stats = extract_text_from_pdf("temp_uploaded.pdf")
        
        # Clean up temp file
        os.remove("temp_uploaded.pdf")
    
    # Display redaction results
    st.success("✅ Document successfully redacted!")
    
    # Show redaction statistics in organized columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Redactions", redaction_stats['total_redactions'])
        st.metric("Names Truncated", redaction_stats['names_truncated'])
        st.metric("IP Addresses", redaction_stats['ip_addresses'])
    
    with col2:
        st.metric("Email Addresses", redaction_stats['email_addresses'])
        st.metric("Phone Numbers", redaction_stats['phone_numbers'])
        st.metric("URLs", redaction_stats['urls'])
    
    with col3:
        st.metric("MAC Addresses", redaction_stats['mac_addresses'])
        st.metric("Employee IDs", redaction_stats['employee_ids'])
        other_count = redaction_stats['account_numbers'] + redaction_stats['imei_numbers']
        st.metric("Other Sensitive Data", other_count)
    
    # Show preview of redacted text
    st.subheader("📋 Redacted Document Preview")
    with st.expander("View Redacted Text", expanded=False):
        st.text_area("Redacted Content", redacted_text, height=300)
    
    st.divider()
    
    # Audit section
    st.header("🔍 Network Team Compliance Audit")
    
    # Show appropriate help text based on provider
    if ai_provider == "OpenAI":
        st.markdown("""
        **Professional Network Team Audit** using OpenAI's advanced models:
        - ✅ **15-Question Compliance Framework** based on official Network Team procedures
        - 🔍 **Evidence-Based Analysis** with specific quotes and citations
        - 📊 **Performance Scoring** (1-10 scale) with detailed justification
        - 📝 **Personal Audit Notes from Jeremy** - Direct manager feedback to engineers
        """)
    else:  # Claude (default)
        st.markdown("""
        **🧠 Superior Compliance Reasoning** using Claude 3.5 Sonnet (Recommended):
        - ✅ **Constitutional AI** specialized in rule-following and compliance analysis
        - 🔍 **Enhanced Procedural Analysis** with balanced, reasonable standards
        - 📊 **Systematic Evaluation** with consistent scoring methodology
        - 📝 **Comprehensive Documentation** with detailed evidence review
        - 🎯 **Optimized for Network Team** standards and procedures
        """)
    
    # Check API key based on provider
    has_api_key = False
    if ai_provider == "OpenAI":
        has_api_key = api_key_input != ""
    else:  # Claude
        has_api_key = anthropic_key != ""
    
    if has_api_key:
        if st.button("🚀 Run Network Team Audit", type="primary", use_container_width=True):
            with st.spinner(f"Running Network Team compliance audit with {ai_provider}..."):
                try:
                    # Choose auditor based on provider
                    if ai_provider == "OpenAI":
                        auditor = TicketAuditor()
                    else:  # Claude
                        auditor = ClaudeAuditor()
                    
                    # Show processing info
                    text_length = len(redacted_text)
                    if text_length > 8000:
                        st.info(f"📏 Large document detected ({text_length:,} chars). Processing with optimization.")
                    
                    audit_result = auditor.audit_ticket(
                        redacted_text,
                        model=model_choice
                    )
                    
                    # Save audit report with provider prefix
                    provider_prefix = "claude" if "Claude" in ai_provider else "openai"
                    report_file = auditor.save_audit_report(audit_result, f"{provider_prefix}_network_team_audit")
                    
                    st.success(f"✅ Audit completed! Report saved: {report_file}")
                    
                    # Display audit results
                    st.subheader("📊 Audit Results")
                    with st.expander("View Full Audit Report", expanded=True):
                        st.markdown(audit_result)
                    
                    # Download button for audit report  
                    st.download_button(
                        "📥 Download Audit Report",
                        data=audit_result,
                        file_name=f"{provider_prefix}_audit_report_{uploaded_file.name}.txt",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Audit failed: {str(e)}")
                    st.info("💡 Please check your API key and try again.")
    else:
        provider_name = "OpenAI" if ai_provider == "OpenAI" else "Claude"
        st.warning(f"⚠️ Please enter your {provider_name} API key to run the audit.")
        
        if "Claude" in ai_provider:
            st.info("🔑 To get your Claude API key: Visit https://console.anthropic.com/")

# Footer
st.divider()
st.markdown("**Built for Network Team Compliance** | Automated redaction with AI-powered auditing")
