"""
Real-time Interactive Chat Auditor
Simple chat interface for immediate testing
"""

import streamlit as st
from interactive_auditor import InteractiveAuditor
from pdf_parser import extract_text_from_pdf
import tempfile
import os
from datetime import datetime

def main():
    st.set_page_config(
        page_title="Chat Auditor",
        page_icon="💬",
        layout="wide"
    )
    
    st.title("💬 Real-Time Audit Chat")
    
    # Initialize
    if 'auditor' not in st.session_state:
        st.session_state.auditor = InteractiveAuditor()
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'audit_ready' not in st.session_state:
        st.session_state.audit_ready = False
    
    # Sidebar for PDF upload
    with st.sidebar:
        st.header("📄 Load Incident")
        
        uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])
        
        if uploaded_file and not st.session_state.audit_ready:
            with st.spinner("Processing..."):
                # Process PDF
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    tmp.write(uploaded_file.getbuffer())
                    tmp_path = tmp.name
                
                try:
                    # extract_text_from_pdf already returns redacted text
                    redacted_text = extract_text_from_pdf(tmp_path)
                    
                    # Perform initial audit
                    result = st.session_state.auditor.perform_initial_audit(redacted_text)
                    
                    # Add to messages
                    st.session_state.messages = [
                        {"role": "assistant", "content": f"📊 **AUDIT COMPLETE**\n\n{result}\n\n---\n\n💬 **Ready for questions!** Ask me anything about this audit."}
                    ]
                    st.session_state.audit_ready = True
                    
                finally:
                    os.unlink(tmp_path)
                    
                st.success("✅ Audit ready!")
                st.rerun()
        
        if st.session_state.audit_ready:
            st.success("🤖 Chat active")
            if st.button("🔄 New Audit"):
                st.session_state.messages = []
                st.session_state.audit_ready = False
                st.session_state.auditor.reset_conversation()
                st.rerun()
    
    # Main chat area
    if st.session_state.audit_ready:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Quick action buttons
        st.markdown("**Quick Questions:**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("❓ First Access", key="fa"):
                question = "Tell me about the First Access findings. What evidence did you see?"
                st.session_state.messages.append({"role": "user", "content": question})
                with st.spinner("🤖"):
                    response = st.session_state.auditor.continue_conversation(question)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col2:
            if st.button("🔧 Troubleshooting", key="ts"):
                question = "How was the troubleshooting documentation? Show me specific examples."
                st.session_state.messages.append({"role": "user", "content": question})
                with st.spinner("🤖"):
                    response = st.session_state.auditor.continue_conversation(question)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col3:
            if st.button("📝 Close Notes", key="cn"):
                question = "Review the close notes quality. Were they comprehensive?"
                st.session_state.messages.append({"role": "user", "content": question})
                with st.spinner("🤖"):
                    response = st.session_state.auditor.continue_conversation(question)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col4:
            if st.button("📊 Overall Score", key="os"):
                question = "Explain the overall score. What drove the assessment?"
                st.session_state.messages.append({"role": "user", "content": question})
                with st.spinner("🤖"):
                    response = st.session_state.auditor.continue_conversation(question)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        # Chat input
        if prompt := st.chat_input("Ask anything about the audit..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Get AI response
            with st.spinner("🤖 Thinking..."):
                response = st.session_state.auditor.continue_conversation(prompt)
                st.session_state.messages.append({"role": "assistant", "content": response})
            
            st.rerun()
    
    else:
        st.info("👈 Upload a PDF in the sidebar to start chatting about the audit!")
        
        st.markdown("""
        ### 💬 How This Works:
        1. **Upload** your incident PDF in the sidebar
        2. **Wait** for the initial audit to complete  
        3. **Chat** with the AI about any findings
        4. **Ask** specific questions about compliance issues
        5. **Get** detailed explanations with evidence
        
        ### 🎯 Example Questions:
        - "Why did Question 3 score poorly?"
        - "Show me the troubleshooting evidence you found"
        - "How can this engineer improve?"
        - "Are the close notes compliant?"
        """)

if __name__ == "__main__":
    main()
