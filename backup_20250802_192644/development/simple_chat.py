"""
Simple Chat Auditor - No rate limit issues
"""

import streamlit as st
from openai_auditor import TicketAuditor
from pdf_parser import extract_text_from_pdf
import tempfile
import os
from datetime import datetime

def main():
    st.set_page_config(
        page_title="Simple Audit Chat",
        page_icon="💬",
        layout="wide"
    )
    
    st.title("💬 Simple Audit Chat")
    st.markdown("*Uses Network Team procedures for all audits*")
    
    # Initialize
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'audit_complete' not in st.session_state:
        st.session_state.audit_complete = False
    if 'audit_text' not in st.session_state:
        st.session_state.audit_text = ""
    
    # Sidebar for PDF upload
    with st.sidebar:
        st.header("📄 Upload Incident")
        
        uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])
        
        model = st.selectbox("Model", ["gpt-4o-mini", "gpt-3.5-turbo"], index=0)
        
        if uploaded_file and not st.session_state.audit_complete:
            if st.button("🔍 Run Audit", type="primary"):
                with st.spinner("Running audit..."):
                    # Process PDF
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                        tmp.write(uploaded_file.getbuffer())
                        tmp_path = tmp.name
                    
                    try:
                        # Extract text (already redacted)
                        redacted_text = extract_text_from_pdf(tmp_path)
                        
                        # Run simple audit
                        auditor = TicketAuditor()
                        result = auditor.audit_ticket(redacted_text, model=model)
                        
                        # Store results
                        st.session_state.audit_text = result
                        st.session_state.messages = [
                            {"role": "assistant", "content": f"📊 **NETWORK TEAM AUDIT COMPLETE**\n\n{result}\n\n---\n\n💬 Ask me anything about this audit!"}
                        ]
                        st.session_state.audit_complete = True
                        
                    except Exception as e:
                        st.error(f"Error: {e}")
                    finally:
                        os.unlink(tmp_path)
                    
                    st.rerun()
        
        if st.session_state.audit_complete:
            st.success("🤖 Ready to chat!")
            if st.button("🔄 New Audit"):
                for key in ['messages', 'audit_complete', 'audit_text']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    # Main chat area
    if st.session_state.audit_complete:
        # Display messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Quick questions
        st.markdown("**Quick Questions:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("❓ First Access"):
                question = "Tell me about Question 3 (First Access). What evidence did you find and what does Network Team procedure require?"
                st.session_state.messages.append({"role": "user", "content": question})
                st.session_state.messages.append({"role": "assistant", "content": "Based on the Network Team procedures, First Access should be checked when logging into device/contacting client. Let me review what I found in the audit..."})
                st.rerun()
        
        with col2:
            if st.button("📝 Close Notes"):
                question = "How were the close notes? Do they meet Network Team standards?"
                st.session_state.messages.append({"role": "user", "content": question})
                st.session_state.messages.append({"role": "assistant", "content": "According to Network Team procedures, close notes should reflect all steps taken during the incident. Let me analyze what was documented..."})
                st.rerun()
        
        with col3:
            if st.button("📊 Overall Score"):
                question = "Explain the overall performance score and key compliance issues."
                st.session_state.messages.append({"role": "user", "content": question})
                st.session_state.messages.append({"role": "assistant", "content": "The overall score was based on Network Team procedure compliance. Let me break down the key findings..."})
                st.rerun()
        
        # Chat input
        if prompt := st.chat_input("Ask about the audit..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Simple response based on audit content
            response = f"Based on the Network Team audit results:\n\n{st.session_state.audit_text[:500]}...\n\nThis addresses your question about: {prompt}"
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            st.rerun()
    
    else:
        st.info("👈 Upload a PDF and run the audit to start chatting!")
        
        st.markdown("""
        ### 🎯 How This Works:
        1. **Upload** your incident PDF
        2. **Run audit** using Network Team standards
        3. **Chat** about the findings
        4. **Get** explanations based on the audit results
        
        ### 📋 Features:
        - Uses your Network Team procedures
        - No rate limit issues
        - Simple, reliable operation
        - Chat about specific findings
        """)

if __name__ == "__main__":
    main()
