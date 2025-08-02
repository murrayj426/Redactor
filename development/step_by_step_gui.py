"""
Step-by-Step Audit Interface
Interactive Streamlit interface for going through audit questions one by one
"""

import streamlit as st
from pdf_parser import extract_text_from_pdf
from step_by_step_auditor import StepByStepAuditor
import tempfile
import os
from dotenv import load_dotenv

# Load environment variables at startup
load_dotenv()

def main():
    st.set_page_config(
        page_title="Step-by-Step Audit",
        page_icon="📋",
        layout="wide"
    )
    
    st.title("📋 Step-by-Step Network Team Audit")
    st.markdown("*Interactive audit - go through each question with AI discussion*")
    
    # Initialize session state
    if 'auditor' not in st.session_state:
        st.session_state.auditor = None
    if 'audit_started' not in st.session_state:
        st.session_state.audit_started = False
    if 'current_response' not in st.session_state:
        st.session_state.current_response = ""
    
    # Configuration
    st.header("🤖 Configuration")
    
    # Check if API key is already loaded from .env
    env_api_key = os.getenv('OPENAI_API_KEY', '')
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if env_api_key:
            st.success("✅ OpenAI API Key loaded from .env file")
            api_key = env_api_key
            # Optional override
            override_key = st.text_input("Override API Key (optional)", type="password", 
                                       placeholder="Leave blank to use .env key")
            if override_key:
                api_key = override_key
        else:
            api_key = st.text_input("OpenAI API Key", type="password", 
                                   help="Enter your OpenAI API key or add it to .env file")
    
    with col2:
        # Use default model from .env if available
        default_model = os.getenv('DEFAULT_MODEL', 'gpt-4o-mini')
        model_options = ["gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"]
        
        # Set default index based on .env setting
        try:
            default_index = model_options.index(default_model)
        except ValueError:
            default_index = 0
            
        model = st.selectbox("Model", model_options, index=default_index)
    
    if api_key:
        os.environ['OPENAI_API_KEY'] = api_key
    
    st.divider()
    
    # File Upload
    if not st.session_state.audit_started:
        st.header("📁 Upload Incident")
        uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])
        
        if uploaded_file and api_key:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("🚀 Start Step-by-Step Audit", type="primary", use_container_width=True):
                    with st.spinner("Processing PDF and starting audit..."):
                        # Process PDF
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                            tmp.write(uploaded_file.getbuffer())
                            tmp_path = tmp.name
                        
                        try:
                            # Extract text
                            redacted_text, redaction_stats = extract_text_from_pdf(tmp_path)
                            
                            # Show redaction statistics
                            st.subheader("🔒 Redaction Summary")
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Total Redactions", redaction_stats['total_redactions'])
                                st.metric("Names Truncated", redaction_stats['names_truncated'])
                            
                            with col2:
                                st.metric("IP Addresses", redaction_stats['ip_addresses'])
                                st.metric("Email Addresses", redaction_stats['email_addresses'])
                            
                            with col3:
                                st.metric("Phone Numbers", redaction_stats['phone_numbers'])
                                st.metric("URLs", redaction_stats['urls'])
                            
                            if redaction_stats['total_redactions'] == 0:
                                st.info("ℹ️ No sensitive data found requiring redaction")
                            else:
                                st.success(f"✅ Successfully redacted {redaction_stats['total_redactions']} sensitive items")
                            
                            # Start audit
                            st.session_state.auditor = StepByStepAuditor()
                            response = st.session_state.auditor.start_audit(redacted_text, model)
                            st.session_state.current_response = response
                            st.session_state.audit_started = True
                            
                            os.unlink(tmp_path)  # Clean up temp file
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                            os.unlink(tmp_path)
            
            with col2:
                st.info("📄 **Preview Mode Available**\n\nClick 'Start Audit' to begin the interactive 15-question process.")
        
        elif uploaded_file and not api_key:
            st.warning("⚠️ Please enter your OpenAI API key to start the audit.")
        
        # Show preview of audit questions
        if not uploaded_file:
            st.header("📋 Audit Questions Preview")
            with st.expander("15-Question Network Team Framework", expanded=True):
                st.markdown("""
                **Step-by-Step Interactive Audit Process:**
                
                1. **Incident Number Identification** - Display ServiceNow INC number
                2. **Heading Fields Documentation** - CI/Location, State/Pending, Service Offering
                3. **First Access Verification** - Proper marking when accessing device/client
                4. **Engineer Ownership Acknowledgment** - Customer ownership acknowledgment
                5. **Event Date Management** - Accurate follow-up scheduling
                6. **Pending Code Usage** - Correct pending codes (Client Action, RMA, etc.)
                7. **Status Field Updates** - Current Status/Next Steps documentation
                8. **Client Communication Quality** - Professional, detailed updates
                9. **Troubleshooting Documentation** - Thorough steps with evidence
                10. **Timely Update Compliance** - Priority-based update frequency
                11. **Procedure Following** - Network Team procedures and templates
                12. **Task Management** - Activity & Change tasks (when applicable)
                13. **Time Tracking Accuracy** - Cost tracking documentation
                14. **Resolution Documentation** - Close notes quality (when applicable)
                15. **Overall Performance Assessment** - 1-10 scale rating
                
                **Interactive Features:**
                - ✅ Go through each question individually
                - 💬 Discuss findings with AI for each question
                - ⏮️ Go back to previous questions
                - 📊 See progress as you go
                - 📄 Generate comprehensive final report
                """)
    
    # Audit Interface
    else:
        auditor = st.session_state.auditor
        
        # Progress bar
        progress = (auditor.current_question - 1) / 15
        st.progress(progress, text=auditor.get_progress())
        
        # Current question info
        with st.expander("📋 Current Question Info", expanded=False):
            st.markdown(auditor.get_current_question_info())
        
        # Navigation buttons
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        with col1:
            if st.button("⏮️ Previous", disabled=(auditor.current_question <= 1)):
                response = auditor.previous_question()
                st.session_state.current_response = response
                st.rerun()
        
        with col2:
            if st.button("⏭️ Next Question", disabled=(auditor.current_question > 15)):
                response = auditor.next_question(model)
                st.session_state.current_response = response
                st.rerun()
        
        with col3:
            if st.button("📊 Final Report", disabled=(len(auditor.audit_results) == 0)):
                report = auditor.generate_final_report()
                st.session_state.final_report = report
                st.success("Final report generated!")
        
        with col4:
            if st.button("🔄 New Audit"):
                st.session_state.auditor = None
                st.session_state.audit_started = False
                st.session_state.current_response = ""
                st.rerun()
        
        st.divider()
        
        # Current question and response
        if auditor.current_question <= 15:
            st.header(f"Question {auditor.current_question} of 15")
            
            # Show AI response
            if st.session_state.current_response:
                st.markdown("### 🤖 AI Analysis")
                st.markdown(st.session_state.current_response)
            
            # Discussion area
            st.markdown("### 💬 Discussion")
            discussion_input = st.text_area(
                "Ask for clarification or discuss this question further:",
                placeholder="e.g., 'Can you explain why this is a compliance issue?' or 'What specific evidence should I look for?'",
                height=100
            )
            
            if st.button("💬 Discuss", type="secondary") and discussion_input:
                with st.spinner("Getting AI response..."):
                    response = auditor.continue_discussion(discussion_input, model)
                    st.markdown("**AI Response:**")
                    st.markdown(response)
        
        else:
            st.header("✅ Audit Complete!")
            st.success("All 15 questions have been completed.")
            
            if st.button("📊 Generate Final Report", type="primary"):
                report = auditor.generate_final_report()
                st.session_state.final_report = report
        
        # Show final report if generated
        if hasattr(st.session_state, 'final_report'):
            st.divider()
            st.header("📄 Final Audit Report")
            st.text_area("Complete Audit Report:", st.session_state.final_report, height=400)
            
            st.download_button(
                label="📥 Download Report",
                data=st.session_state.final_report,
                file_name=f"step_by_step_audit_{auditor.current_question-1}_questions.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()
