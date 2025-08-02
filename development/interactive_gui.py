"""
Enhanced Interactive GUI for PDF Redactor with Conversational AI Audit
"""

import streamlit as st
import sys
import os
from pdf_parser import extract_text_from_pdf, redact_pii
from openai_auditor import TicketAuditor
from interactive_auditor import InteractiveAuditor
import json
from datetime import datetime

def main():
    st.set_page_config(
        page_title="AI Incident Auditor - Interactive Mode",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 AI Incident Auditor - Interactive Mode")
    st.markdown("Upload incident PDFs for redaction and conversational AI audit analysis")
    
    # Initialize session state
    if 'interactive_auditor' not in st.session_state:
        st.session_state.interactive_auditor = InteractiveAuditor()
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'audit_completed' not in st.session_state:
        st.session_state.audit_completed = False
    if 'original_text' not in st.session_state:
        st.session_state.original_text = ""
    if 'redacted_text' not in st.session_state:
        st.session_state.redacted_text = ""
    
    # Sidebar controls
    with st.sidebar:
        st.header("🛠️ Controls")
        
        audit_mode = st.radio(
            "Audit Mode",
            ["Standard Audit", "Interactive Conversation"],
            help="Standard: Traditional audit report\nInteractive: Chat with AI about findings"
        )
        
        model_choice = st.selectbox(
            "AI Model",
            ["gpt-4o-mini (Recommended)", "gpt-4 (Premium)", "gpt-3.5-turbo (Budget)"],
            index=0,
            help="""
            • GPT-4o-mini: Best balance of cost/performance for audits
            • GPT-4: Most thorough analysis, higher cost
            • GPT-3.5-turbo: Budget option, basic compliance checks
            """
        )
        
        # Extract model name
        actual_model = model_choice.split(" ")[0]
        
        if st.button("🔄 Reset Session"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        if st.session_state.audit_completed:
            if st.button("💾 Export Conversation"):
                filename = st.session_state.interactive_auditor.export_conversation()
                st.success(f"Exported: {filename}")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📄 Document Processing")
        
        uploaded_file = st.file_uploader(
            "Upload Incident PDF",
            type=['pdf'],
            help="Upload a PDF incident ticket for analysis"
        )
        
        if uploaded_file is not None:
            with st.spinner("Processing PDF..."):
                # Save uploaded file temporarily
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                try:
                    # Extract and redact text
                    st.session_state.original_text = extract_text_from_pdf(temp_path)
                    st.session_state.redacted_text = redact_pii(st.session_state.original_text)
                    
                    # Display processing results
                    st.success(f"✅ Processed {len(st.session_state.original_text):,} characters")
                    
                    # Show redacted text preview
                    with st.expander("📝 Redacted Text Preview"):
                        st.text_area(
                            "Redacted Content",
                            st.session_state.redacted_text[:2000] + "..." if len(st.session_state.redacted_text) > 2000 else st.session_state.redacted_text,
                            height=200,
                            disabled=True
                        )
                    
                finally:
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
        
        # Audit trigger
        if st.session_state.redacted_text and not st.session_state.audit_completed:
            if st.button("🔍 Start Interactive Audit", type="primary"):
                with st.spinner("Performing comprehensive audit..."):
                    audit_result = st.session_state.interactive_auditor.perform_initial_audit(
                        st.session_state.redacted_text,
                        model=actual_model
                    )
                    st.session_state.conversation_history.append({
                        "role": "assistant",
                        "content": audit_result,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
                    st.session_state.audit_completed = True
                    st.rerun()
    
    with col2:
        st.header("🤖 AI Audit Analysis")
        
        if audit_mode == "Standard Audit" and st.session_state.redacted_text:
            # Traditional audit mode
            if st.button("📊 Generate Standard Report"):
                with st.spinner("Generating audit report..."):
                    auditor = TicketAuditor()
                    result = auditor.audit_ticket(st.session_state.redacted_text, model=actual_model)
                    
                    st.markdown("### 📋 Audit Report")
                    st.markdown(result)
                    
                    # Download report
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.download_button(
                        "💾 Download Report",
                        result,
                        f"audit_report_{timestamp}.txt",
                        "text/plain"
                    )
        
        elif audit_mode == "Interactive Conversation":
            # Interactive conversation mode
            if st.session_state.audit_completed:
                st.markdown("### 💬 Live Audit Discussion")
                
                # Chat container with auto-scroll
                chat_container = st.container()
                
                # Display conversation in chat format
                with chat_container:
                    for i, msg in enumerate(st.session_state.conversation_history):
                        if msg["role"] == "assistant":
                            with st.chat_message("assistant", avatar="🤖"):
                                st.markdown(msg["content"])
                                if "timestamp" in msg:
                                    st.caption(f"⏰ {msg['timestamp']}")
                        elif msg["role"] == "user":
                            with st.chat_message("user", avatar="👤"):
                                st.markdown(msg["content"])
                                if "timestamp" in msg:
                                    st.caption(f"⏰ {msg['timestamp']}")
                
                # Real-time chat input at bottom
                st.markdown("---")
                
                # Quick action buttons row
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button("❓ First Access Details", key="q3"):
                        prompt = "Can you provide more details about Question 3 (First Access)? What specific evidence did you find or expect to find?"
                        st.session_state.pending_message = prompt
                        
                with col2:
                    if st.button("🔍 Troubleshooting", key="q9"):
                        prompt = "Analyze the troubleshooting documentation in detail. What technical steps were documented and how thorough were they?"
                        st.session_state.pending_message = prompt
                        
                with col3:
                    if st.button("📊 Score Discussion", key="score"):
                        prompt = "Let's discuss the overall performance score. What were the key factors in your assessment and how could this engineer improve?"
                        st.session_state.pending_message = prompt
                        
                with col4:
                    if st.button("📝 Close Notes", key="q14"):
                        prompt = "Review the close notes in detail. Were they comprehensive enough according to Network Team standards?"
                        st.session_state.pending_message = prompt
                
                # Main chat input
                if prompt := st.chat_input("Ask about any aspect of the audit..."):
                    # Add user message
                    st.session_state.conversation_history.append({
                        "role": "user",
                        "content": prompt,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
                    
                    # Get AI response
                    with st.spinner("🤖 AI is thinking..."):
                        response = st.session_state.interactive_auditor.continue_conversation(prompt, actual_model)
                        st.session_state.conversation_history.append({
                            "role": "assistant",
                            "content": response,
                            "timestamp": datetime.now().strftime("%H:%M:%S")
                        })
                    
                    st.rerun()
                
                # Handle pending messages from quick buttons
                if hasattr(st.session_state, 'pending_message'):
                    prompt = st.session_state.pending_message
                    del st.session_state.pending_message
                    
                    # Add user message
                    st.session_state.conversation_history.append({
                        "role": "user",
                        "content": prompt,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
                    
                    # Get AI response
                    with st.spinner("🤖 AI is analyzing..."):
                        response = st.session_state.interactive_auditor.continue_conversation(prompt, actual_model)
                        st.session_state.conversation_history.append({
                            "role": "assistant",
                            "content": response,
                            "timestamp": datetime.now().strftime("%H:%M:%S")
                        })
                    
                    st.rerun()
                
                # Suggested questions section
                with st.expander("💡 Need inspiration? Get suggested questions"):
                    if st.button("Generate Question Suggestions"):
                        with st.spinner("Generating suggestions..."):
                            suggestions = st.session_state.interactive_auditor.get_suggested_questions()
                            st.markdown("### 🎯 Suggested Questions:")
                            for i, suggestion in enumerate(suggestions[:5], 1):
                                if suggestion.strip():
                                    suggestion_clean = suggestion.strip().replace('*', '').replace('-', '').strip()
                                    if st.button(f"{suggestion_clean}", key=f"sug_{i}"):
                                        st.session_state.pending_message = suggestion_clean
                                        st.rerun()
                
            else:
                st.info("📋 Upload a PDF and start the interactive audit to begin conversation")
                
                # Show example questions while waiting
                st.markdown("### 💭 Example Questions You Can Ask:")
                example_questions = [
                    "Why did Question 3 (First Access) receive a low score?",
                    "Can you explain the troubleshooting documentation findings?",
                    "What specific improvements would you recommend?",
                    "How does this compare to Network Team standards?",
                    "What evidence did you find for client communication?",
                    "Are the close notes compliant with procedures?"
                ]
                
                for q in example_questions:
                    st.markdown(f"• {q}")
    
    # Footer
    st.markdown("---")
    st.markdown("🔧 **Enhanced AI Auditor** - Interactive incident compliance analysis with conversational AI")

if __name__ == "__main__":
    main()
