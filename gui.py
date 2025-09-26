import streamlit as st
from pdf_parser import extract_text_from_pdf, redact_sensitive
from openai_auditor import TicketAuditor
from claude_auditor import ClaudeAuditor
import os
import time
import tempfile
import io
from typing import List, Dict, Any
from dotenv import load_dotenv

# Import optimization utilities
from utils.config import get_config, validate_config
from utils.error_handling import setup_logging, get_performance_report


# Import batch processor
try:
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import zipfile
    BATCH_AVAILABLE = True
except ImportError:
    BATCH_AVAILABLE = False

# Load environment variables at startup
load_dotenv()

# Setup configuration and logging
config = get_config()
validation_result = validate_config()
setup_logging(level="INFO", log_file="logs/app.log" if not validation_result['issues'] else None)

st.set_page_config(page_title="PDF Redactor & Network Team Auditor", layout="wide")
st.title("📄 Incident PDF Redactor & Network Team AI Auditor")

# Configuration validation sidebar
with st.sidebar:
    st.header("🔧 System Status")
    
    if validation_result['valid']:
        st.success("✅ Configuration Valid")
    else:
        st.error("❌ Configuration Issues")
        for issue in validation_result['issues']:
            st.error(f"• {issue}")
    
    if validation_result['warnings']:
        st.warning("⚠️ Warnings")
        for warning in validation_result['warnings']:
            st.warning(f"• {warning}")
    
    # Performance monitoring
    if st.button("📊 Performance Report"):
        perf_report = get_performance_report()
        if perf_report:
            st.subheader("📊 Performance Metrics")
            for func_name, metrics in perf_report.items():
                with st.expander(f"🔧 {func_name}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Calls", metrics['total_calls'])
                        st.metric("Success Rate", f"{metrics['success_rate']:.1f}%")
                    with col2:
                        st.metric("Avg Duration", f"{metrics['avg_duration']:.2f}s")
                        st.metric("Max Duration", f"{metrics['max_duration']:.2f}s")
                    with col3:
                        st.metric("Min Duration", f"{metrics['min_duration']:.2f}s")
                        st.metric("Failed Calls", metrics['failed_calls'])
        else:
            st.info("💡 No performance data yet. Run an audit to see metrics!")
            st.markdown("**Performance monitoring tracks:**")
            st.markdown("• ⏱️ Function execution times")
            st.markdown("• ✅ Success/failure rates") 
            st.markdown("• 📊 Call frequency statistics")
            st.markdown("• 🔧 Bottleneck identification")

st.markdown("---")


st.header("🤖 Configuration")

# Check if API keys are available from .env or Streamlit secrets
def get_api_key(key_name):
    """Get API key from environment or Streamlit secrets"""
    # First try environment variables (local development)
    env_key = os.getenv(key_name, '')
    if env_key and env_key != f'your_{key_name.lower()}_here':
        return env_key
    
    # Then try Streamlit secrets (cloud deployment)
    try:
        if hasattr(st, 'secrets') and key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass
    
    return ''

env_openai_key = get_api_key('OPENAI_API_KEY')
env_anthropic_key = get_api_key('ANTHROPIC_API_KEY')

col1, col2 = st.columns([2, 1])

with col1:
    # AI Provider Selection
    provider_options = ["Claude (Anthropic) - Recommended", "OpenAI"]
    
    ai_provider = st.selectbox(
        "AI Provider", 
        provider_options,
        index=0,
        help="Claude 3.5 Sonnet provides superior compliance reasoning for Network Team audits"
    )
    
    # Initialize variables
    api_key_input = ""
    anthropic_key = ""
    
    # API Key handling based on provider
    if ai_provider == "OpenAI":
        if env_openai_key:
            st.success("✅ OpenAI API Key loaded from environment/secrets")
            api_key_input = env_openai_key
            # Optional override
            override_key = st.text_input("Override OpenAI API Key (optional)", type="password", 
                                       placeholder="Leave blank to use configured key")
            if override_key:
                api_key_input = override_key
        else:
            st.warning("⚠️ OpenAI API key not configured")
            api_key_input = st.text_input("OpenAI API Key", type="password", 
                                        help="Get your API key from OpenAI or configure in Streamlit secrets")
        
        if api_key_input:
            os.environ['OPENAI_API_KEY'] = api_key_input
            
    else:  # Claude (default)
        if env_anthropic_key and env_anthropic_key != 'your_anthropic_api_key_here':
            st.success("✅ Claude API Key loaded from environment/secrets")
            anthropic_key = env_anthropic_key
            # Optional override
            override_key = st.text_input("Override Claude API Key (optional)", type="password", 
                                       placeholder="Leave blank to use configured key")
            if override_key:
                anthropic_key = override_key
        else:
            st.warning("⚠️ Anthropic API key not configured")
            anthropic_key = st.text_input(
                "Claude API Key", 
                type="password",
                help="Get your API key from https://console.anthropic.com/ or configure in Streamlit secrets"
            )
        
        if anthropic_key:
            os.environ['ANTHROPIC_API_KEY'] = anthropic_key

with col2:
    if ai_provider == "OpenAI":
        # Use default model from environment or Streamlit secrets
        default_model = get_api_key('DEFAULT_MODEL') or 'gpt-4o-mini'
        model_options = ["gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"]
        
        # Set default index based on configured setting
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

# Processing mode selection
st.header("📄 Document Processing")

if BATCH_AVAILABLE:
    processing_mode = st.radio(
        "Processing Mode",
        ["Single File", "Batch Processing"],
        horizontal=True,
        help="Choose between processing one file or multiple files at once"
    )
else:
    processing_mode = "Single File"
    st.info("💡 Batch processing requires additional dependencies. Currently in single file mode.")

# Initialize session state
if 'redacted_text' not in st.session_state:
    st.session_state.redacted_text = None
if 'redaction_stats' not in st.session_state:
    st.session_state.redaction_stats = None
if 'audit_result' not in st.session_state:
    st.session_state.audit_result = None
if 'batch_results' not in st.session_state:
    st.session_state.batch_results = None

# File upload based on mode
if processing_mode == "Single File":
    uploaded_file = st.file_uploader("Upload an Incident PDF", type="pdf")
    
    # Store in session state for later processing
    if uploaded_file is not None:
        st.session_state.single_file = uploaded_file
        st.session_state.process_single = True
    else:
        st.session_state.process_single = False
        
else:  # Batch Processing
    uploaded_files = st.file_uploader(
        "Upload Multiple Incident PDFs", 
        type="pdf", 
        accept_multiple_files=True,
        help="Select multiple PDF files to process them all at once"
    )
    
    if uploaded_files:
        st.session_state.batch_files = uploaded_files
        st.session_state.process_batch = True
    else:
        st.info("👆 Select multiple PDF files to start batch processing")
        st.session_state.process_batch = False

def process_single_file(uploaded_file, ai_provider, api_key_input, anthropic_key, model_choice):
    """Process a single PDF file"""
    # Check if we need to reprocess (file changed)
    file_hash = hash(uploaded_file.getbuffer().tobytes())
    if 'file_hash' not in st.session_state or st.session_state.file_hash != file_hash:
        
        with st.spinner("Processing PDF and applying redaction..."):
            # Save uploaded file temporarily
            with open("temp_uploaded.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Extract and redact text
            redacted_text, redaction_stats = extract_text_from_pdf("temp_uploaded.pdf")
            
            # Store in session state
            st.session_state.redacted_text = redacted_text
            st.session_state.redaction_stats = redaction_stats
            st.session_state.file_hash = file_hash
            st.session_state.audit_result = None  # Reset audit when file changes
            
            # Clean up temp file
            os.remove("temp_uploaded.pdf")
    
    # Use cached results
    redacted_text = st.session_state.redacted_text
    redaction_stats = st.session_state.redaction_stats
    
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
    
    # Run audit
    run_single_audit(redacted_text, uploaded_file, ai_provider, api_key_input, anthropic_key, model_choice)

def process_batch_files(uploaded_files, ai_provider, api_key_input, anthropic_key, model_choice):
    """Process multiple PDF files in batch"""
    
    st.subheader(f"📁 Batch Processing ({len(uploaded_files)} files)")
    
    # Check API key
    has_api_key = False
    if ai_provider == "OpenAI":
        has_api_key = api_key_input != ""
    else:  # Claude
        has_api_key = anthropic_key != ""
    
    if not has_api_key:
        provider_name = "OpenAI" if ai_provider == "OpenAI" else "Claude"
        st.warning(f"⚠️ Please enter your {provider_name} API key to run batch processing.")
        return
    
    # Show file list
    st.write("**Files to process:**")
    for i, file in enumerate(uploaded_files, 1):
        file_size = len(file.getbuffer()) / (1024 * 1024)  # MB
        st.write(f"{i}. {file.name} ({file_size:.1f} MB)")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🚀 Start Batch Processing", type="primary", use_container_width=True):
            run_batch_processing(uploaded_files, ai_provider, api_key_input, anthropic_key, model_choice)
    
    with col2:
        max_workers = st.slider("Parallel Workers", 1, min(3, len(uploaded_files)), 2, 
                               help="Number of files to process simultaneously")
    
    # Display batch results if available
    if st.session_state.batch_results:
        display_batch_results(st.session_state.batch_results)

def run_batch_processing(uploaded_files, ai_provider, api_key_input, anthropic_key, model_choice):
    """Execute batch processing with progress tracking"""
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Results storage
    batch_results = {
        'files': [],
        'total_files': len(uploaded_files),
        'successful': 0,
        'failed': 0,
        'total_redactions': 0,
        'processing_time': 0
    }
    
    start_time = time.time()
    
    def process_single_batch_file(file_data):
        """Process a single file in the batch"""
        file, index = file_data
        try:
            # Save file temporarily
            temp_path = f"temp_batch_{index}.pdf"
            with open(temp_path, "wb") as f:
                f.write(file.getbuffer())
            
            # Extract and redact text
            redacted_text, redaction_stats = extract_text_from_pdf(temp_path)
            
            # Run audit
            if ai_provider == "OpenAI":
                auditor = TicketAuditor()
            else:
                auditor = ClaudeAuditor()
            
            audit_result = auditor.audit_ticket(redacted_text, model=model_choice)
            
            # Clean up
            os.remove(temp_path)
            
            return {
                'filename': file.name,
                'status': 'success',
                'redacted_text': redacted_text,
                'redaction_stats': redaction_stats,
                'audit_result': audit_result,
                'redaction_count': redaction_stats['total_redactions']
            }
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return {
                'filename': file.name,
                'status': 'error',
                'error': str(e),
                'redaction_count': 0
            }
    
    # Process files with threading
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Submit all jobs
        futures = {
            executor.submit(process_single_batch_file, (file, i)): i 
            for i, file in enumerate(uploaded_files)
        }
        
        completed = 0
        for future in as_completed(futures):
            result = future.result()
            batch_results['files'].append(result)
            
            if result['status'] == 'success':
                batch_results['successful'] += 1
                batch_results['total_redactions'] += result['redaction_count']
            else:
                batch_results['failed'] += 1
            
            completed += 1
            progress = completed / len(uploaded_files)
            progress_bar.progress(progress)
            status_text.text(f"Processing... {completed}/{len(uploaded_files)} files complete")
    
    batch_results['processing_time'] = time.time() - start_time
    st.session_state.batch_results = batch_results
    
    progress_bar.progress(1.0)
    status_text.text("✅ Batch processing complete!")

def display_batch_results(batch_results):
    """Display batch processing results with expandable cards"""
    
    st.divider()
    st.header("📊 Batch Processing Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Files", batch_results['total_files'])
    with col2:
        st.metric("Successful", batch_results['successful'])
    with col3:
        st.metric("Failed", batch_results['failed'])
    with col4:
        st.metric("Total Redactions", batch_results['total_redactions'])
    
    # Processing time and download options
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info(f"⏱️ Processing completed in {batch_results['processing_time']:.1f} seconds")
    
    with col2:
        if batch_results['successful'] > 0:
            zip_data = create_batch_zip(batch_results)
            st.download_button(
                "📥 Download All Results (ZIP)",
                data=zip_data,
                file_name=f"batch_results_{int(time.time())}.zip",
                mime="application/zip",
                use_container_width=True
            )
    
    st.divider()
    
    # Individual file results with expandable cards
    st.subheader("📋 Individual File Results")
    
    for i, file_result in enumerate(batch_results['files']):
        create_expandable_file_card(file_result, i)

def create_expandable_file_card(file_result, index):
    """Create an expandable card for a single file result"""
    
    # Card header with summary
    status_emoji = "✅" if file_result['status'] == 'success' else "❌"
    
    if file_result['status'] == 'success':
        # Extract audit score
        audit_score = extract_score_for_display(file_result['audit_result'])
        redaction_count = file_result['redaction_count']
        
        card_summary = f"{status_emoji} **{file_result['filename']}** | Score: {audit_score} | Redactions: {redaction_count}"
    else:
        card_summary = f"{status_emoji} **{file_result['filename']}** | Error: {file_result['error'][:50]}..."
    
    # Expandable section
    with st.expander(card_summary):
        if file_result['status'] == 'success':
            # Success - show full details
            
            # Redaction summary
            st.subheader("📊 Redaction Summary")
            stats = file_result['redaction_stats']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Redactions", stats['total_redactions'])
                st.metric("Names", stats['names_truncated'])
                st.metric("IP Addresses", stats['ip_addresses'])
            
            with col2:
                st.metric("Email Addresses", stats['email_addresses'])
                st.metric("Phone Numbers", stats['phone_numbers'])
                st.metric("URLs", stats['urls'])
            
            with col3:
                st.metric("MAC Addresses", stats['mac_addresses'])
                st.metric("Employee IDs", stats['employee_ids'])
                other = stats['account_numbers'] + stats['imei_numbers']
                st.metric("Other", other)
            
            st.divider()
            
            # Full audit report
            st.subheader("📋 Network Team Audit Report")
            
            # Show key findings first
            audit_lines = file_result['audit_result'].split('\n')
            key_findings = []
            
            # Look for specific failed questions with context
            for i, line in enumerate(audit_lines):
                line_clean = line.strip()
                if len(line_clean) > 10:
                    # Look for failed question sections
                    if '❌ FAIL' in line or 'STATUS**: ❌ FAIL' in line:
                        # Try to find the question title (usually a few lines before)
                        question_title = ""
                        for j in range(max(0, i-5), i):
                            prev_line = audit_lines[j].strip()
                            if prev_line.startswith('**QUESTION') and '**' in prev_line:
                                # Extract the question title
                                question_title = prev_line.replace('**QUESTION', '').replace('**', '').strip()
                                break
                        
                        # Look for the specific issue description (usually after WHAT YOU MISSED)
                        issue_description = ""
                        for j in range(i, min(len(audit_lines), i+10)):
                            next_line = audit_lines[j].strip()
                            if 'WHAT YOU MISSED' in next_line and j+1 < len(audit_lines):
                                issue_description = audit_lines[j+1].strip()
                                break
                            elif 'ANALYSIS' in next_line and 'not' in next_line.lower():
                                issue_description = next_line.replace('**ANALYSIS**:', '').replace('ANALYSIS:', '').strip()
                                break
                        
                        # Format the finding
                        if question_title and issue_description:
                            # Clean up markdown formatting
                            clean_title = question_title.replace('*', '').replace(':', '').strip()
                            clean_description = issue_description.replace('**', '').replace('*', '').strip()
                            key_findings.append(f"**{clean_title}**: {clean_description}")
                        elif question_title:
                            clean_title = question_title.replace('*', '').replace(':', '').strip()
                            key_findings.append(f"**{clean_title}**: Failed compliance check")
                        elif issue_description:
                            clean_description = issue_description.replace('**', '').replace('*', '').strip()
                            key_findings.append(clean_description)
                    
                    # Also look for direct negative answers
                    elif ('**ANSWER:** No' in line or '**ANSWER: No' in line) and '❌' not in line:
                        # Find the question for this answer
                        question_title = ""
                        for j in range(max(0, i-10), i):
                            prev_line = audit_lines[j].strip()
                            if prev_line.startswith('**QUESTION') and '**' in prev_line:
                                question_title = prev_line.replace('**QUESTION', '').replace('**', '').strip()
                                break
                        
                        if question_title:
                            clean_title = question_title.replace('*', '').replace(':', '').strip()
                            key_findings.append(f"**{clean_title}**: Answer was No")
            
            # Remove duplicates and limit
            key_findings = list(dict.fromkeys(key_findings))[:3]
            
            if key_findings:
                st.error("⚠️ **Issues Found:**")
                for finding in key_findings[:3]:  # Show top 3 issues
                    st.markdown(f"• {finding}")
            else:
                st.success("✅ No major issues found in audit")
            
            # Full audit report in expander
            with st.expander("View Complete Audit Report"):
                st.markdown(file_result['audit_result'])
            
            # Download buttons
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "📥 Download Redacted Text",
                    data=file_result['redacted_text'],
                    file_name=f"redacted_{file_result['filename']}.txt",
                    mime="text/plain",
                    key=f"redacted_{index}"
                )
            
            with col2:
                st.download_button(
                    "📥 Download Audit Report",
                    data=file_result['audit_result'],
                    file_name=f"audit_{file_result['filename']}.txt",
                    mime="text/plain",
                    key=f"audit_{index}"
                )
        
        else:
            # Error - show error details
            st.error(f"**Error processing file:** {file_result['error']}")
            st.info("💡 Check that the file is a valid PDF with extractable text")

# Score extraction is now handled by BaseAuditor.extract_audit_score_from_text()
# This avoids duplication and ensures consistency across all audit providers

def extract_score_for_display(audit_text):
    """Helper function to extract score using auditor instance"""
    # Create a temporary auditor instance for score extraction
    from base_auditor import BaseAuditor
    
    # Create a minimal concrete implementation just for score extraction
    class ScoreExtractor(BaseAuditor):
        def audit_ticket(self, text, model=None):
            pass  # Not needed for score extraction
    
    extractor = ScoreExtractor()
    return extractor.extract_audit_score_from_text(audit_text)

def create_batch_zip(batch_results):
    """Create ZIP file with all batch results"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_result in batch_results['files']:
            if file_result['status'] == 'success':
                # Add redacted text
                redacted_name = f"redacted_{file_result['filename'].replace('.pdf', '.txt')}"
                zip_file.writestr(redacted_name, file_result['redacted_text'])
                
                # Add audit report
                audit_name = f"audit_{file_result['filename'].replace('.pdf', '.txt')}"
                zip_file.writestr(audit_name, file_result['audit_result'])
        
        # Add summary
        summary = create_batch_summary(batch_results)
        zip_file.writestr("batch_summary.txt", summary)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def create_batch_summary(batch_results):
    """Create text summary of batch results"""
    summary = f"""BATCH PROCESSING SUMMARY
========================
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

OVERVIEW:
- Total Files: {batch_results['total_files']}
- Successful: {batch_results['successful']}
- Failed: {batch_results['failed']}
- Total Redactions: {batch_results['total_redactions']}
- Processing Time: {batch_results['processing_time']:.1f} seconds

FILE DETAILS:
=============
"""
    
    for file_result in batch_results['files']:
        summary += f"\nFile: {file_result['filename']}\n"
        summary += f"Status: {file_result['status'].upper()}\n"
        
        if file_result['status'] == 'success':
            summary += f"Redactions: {file_result['redaction_count']}\n"
            score = extract_score_for_display(file_result['audit_result'])
            summary += f"Audit Score: {score}\n"
        else:
            summary += f"Error: {file_result['error']}\n"
        
        summary += "-" * 30 + "\n"
    
    return summary

def run_single_audit(redacted_text, uploaded_file, ai_provider, api_key_input, anthropic_key, model_choice):
    """Run audit for single file"""
    
    st.header("🔍 Network Team Compliance Audit")
    
    # Show appropriate help text based on provider
    if ai_provider == "OpenAI":
        st.markdown("""
        **Professional Network Team Audit** using OpenAI's advanced models:
        - ✅ **15-Question Compliance Framework** based on official Network Team procedures
        - 🔍 **Evidence-Based Analysis** with specific quotes and citations
        - 📊 **Performance Scoring** (1-10 scale) with detailed justification
        - 📝 **Personal Audit Notes from Team Lead** - Direct manager feedback to engineers
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

                    # Attempt structured summary extraction (JSON first then fallback handled internally)
                    summary_dict = auditor.create_audit_summary(audit_result)
                    
                    # Store audit result only if not already stored or differs
                    if st.session_state.get('audit_result') != audit_result:
                        st.session_state.audit_result = audit_result
                    
                    # Save audit report with provider prefix
                    provider_prefix = "claude" if "Claude" in ai_provider else "openai"
                    report_file = auditor.save_audit_report(audit_result, f"{provider_prefix}_network_team_audit")
                    
                    st.success(f"✅ Audit completed! Report saved: {report_file}")
                    
                    # Display audit results
                    st.subheader("📊 Audit Results")

                    # If structured summary available show top-line metrics
                    if summary_dict:
                        cols = st.columns(5)
                        with cols[0]:
                            st.metric("PASS", summary_dict.get('pass_count', 0))
                        with cols[1]:
                            st.metric("FAIL", summary_dict.get('fail_count', 0))
                        with cols[2]:
                            st.metric("N/A", summary_dict.get('na_responses', 0))
                        with cols[3]:
                            comp = summary_dict.get('compliance_percentage')
                            st.metric("Compliance %", f"{comp:.1f}%" if comp is not None else "-")
                        with cols[4]:
                            st.metric("Scoreable", summary_dict.get('applicable_questions', summary_dict.get('scoreable_questions', '-')))

                        # Display raw JSON summary if used
                        if summary_dict.get('json_summary_used'):
                            with st.expander("Structured JSON Summary"):
                                st.code(str({k: v for k, v in summary_dict.items() if k not in ('json_summary_used', 'compliance_percentage')}), language="json")
                        else:
                            st.caption("Parsed via fallback pattern matching (JSON summary not present in model output).")
                    else:
                        st.caption("Summary extraction unavailable.")

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

# Process files after all functions are defined
if 'process_single' in st.session_state and st.session_state.process_single and 'single_file' in st.session_state:
    process_single_file(st.session_state.single_file, ai_provider, api_key_input, anthropic_key, model_choice)
elif 'process_batch' in st.session_state and st.session_state.process_batch and 'batch_files' in st.session_state:
    process_batch_files(st.session_state.batch_files, ai_provider, api_key_input, anthropic_key, model_choice)

# Footer
st.divider()
st.markdown("**Built for Network Team Compliance** | Automated redaction with AI-powered auditing")
