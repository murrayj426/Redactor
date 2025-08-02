"""
Interactive AI Auditor - Conversational incident audit system
Allows back-and-forth discussion about audit findings
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
import json
from datetime import datetime

class InteractiveAuditor:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.conversation_history = []
        self.audit_context = None
        self.original_text = None
        
    def load_procedures(self):
        """Load the incident handling procedures"""
        try:
            with open('incident_handling_procedures.txt', 'r') as f:
                return f.read()
        except FileNotFoundError:
            return "Network Team procedures not found."
    
    def perform_initial_audit(self, redacted_text, model="gpt-4o-mini"):
        """Perform comprehensive initial audit using Network Team standards"""
        self.original_text = redacted_text
        procedures = self.load_procedures()
        
        # Smart model selection based on document complexity
        doc_length = len(redacted_text)
        if doc_length > 15000 and model == "gpt-4o-mini":
            print(f"📊 Large document ({doc_length:,} chars) - Using GPT-4 for better analysis")
            model = "gpt-4"
        elif doc_length < 5000 and model == "gpt-4":
            print(f"📄 Small document ({doc_length:,} chars) - GPT-4o-mini sufficient")
            model = "gpt-4o-mini"

        # Enhanced audit prompt - always uses Network Team procedures
        initial_prompt = f"""
You are an expert Network Team incident auditor with years of experience. You will be having a conversation with another auditor about this incident ticket. Provide a comprehensive initial audit using ONLY the Network Team procedures as your standard.

**NETWORK TEAM PROCEDURES (YOUR ONLY STANDARD):**
{procedures}

**COMPREHENSIVE AUDIT INSTRUCTIONS:**
Perform a thorough audit of this incident ticket against Network Team procedures ONLY. For each of the 15 questions below, provide:

1. **SCORE**: Yes/No/N/A with confidence level (High/Medium/Low)
2. **EVIDENCE**: Specific quotes from the ticket
3. **ANALYSIS**: Detailed reasoning based on Network Team procedures
4. **CONCERNS**: Any compliance gaps or risks
5. **FOLLOW-UP QUESTIONS**: What you'd like to explore further

**15-QUESTION NETWORK TEAM AUDIT FRAMEWORK:**

1. **Incident Identification**: ServiceNow INC number present and valid?
2. **Header Fields**: CI/Location, State/Pending, Service Offering populated per procedures?
3. **First Access**: Properly checked per Network Team requirements?
4. **Ownership Acknowledgment**: Engineer acknowledged ownership to customer per procedures?
5. **Event Date Management**: Accurate scheduling per Network Team standards?
6. **Pending Codes**: Correct usage per Network Team pending code procedures?
7. **Status Updates**: Current Status/Next Steps maintained per requirements?
8. **Client Communication**: Professional, detailed updates per Network Team standards?
9. **Troubleshooting**: Steps documented with evidence per procedures?
10. **Update Frequency**: Met Network Team priority-based communication standards?
11. **Procedure Compliance**: Network Team processes and templates followed?
12. **Task Management**: Activity/Change tasks handled per Network Team procedures?
13. **Time Tracking**: Work duration documented per Network Team requirements?
14. **Resolution Documentation**: Close notes meet Network Team standards?
15. **Overall Performance**: Rate 1-10 based on Network Team procedure compliance

**ADDITIONAL ANALYSIS:**
- **Strengths**: What Network Team procedures were followed well?
- **Improvement Areas**: Specific Network Team compliance gaps
- **Risk Assessment**: Any client satisfaction or compliance risks?
- **Training Needs**: Which Network Team procedures need reinforcement?
- **Audit Confidence**: How confident are you in this Network Team standards assessment?

**CONVERSATION SETUP:**
End your audit with: "I'm ready to discuss any of these Network Team compliance findings in detail. What would you like to explore further?"

**INCIDENT TEXT:**
{redacted_text}
"""

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert Network Team incident auditor. Provide thorough, evidence-based audits and be ready for detailed discussions."},
                    {"role": "user", "content": initial_prompt}
                ],
                max_tokens=2500 if model == "gpt-4" else 2000,
                temperature=0.3
            )
            
            audit_result = response.choices[0].message.content
            print(f"🤖 Audit completed using {model}")
            
            # Store context for conversation
            self.audit_context = audit_result
            self.current_model = model
            self.conversation_history = [
                {"role": "system", "content": "You are an expert Network Team incident auditor discussing an audit with a colleague."},
                {"role": "assistant", "content": audit_result}
            ]
            
            return audit_result
            
        except Exception as e:
            # Fallback to cheaper model if rate limited
            if "rate_limit" in str(e).lower() and model == "gpt-4":
                print("⚠️ GPT-4 rate limited, falling back to GPT-4o-mini...")
                return self.perform_initial_audit(redacted_text, "gpt-4o-mini")
            elif "rate_limit" in str(e).lower() and model == "gpt-4o-mini":
                print("⚠️ GPT-4o-mini rate limited, falling back to GPT-3.5-turbo...")
                return self.perform_initial_audit(redacted_text, "gpt-3.5-turbo")
            else:
                return f"Error during initial audit: {str(e)}"
    
    def continue_conversation(self, user_message, model=None):
        """Continue the audit conversation with smart model selection"""
        if not self.audit_context:
            return "Please perform an initial audit first."
        
        # Use same model as initial audit unless specified
        if model is None:
            model = getattr(self, 'current_model', 'gpt-4o-mini')
        
        # Add user message to conversation
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Create context-aware response
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=self.conversation_history + [
                    {"role": "system", "content": f"""
                    Continue the audit discussion. You have access to:
                    - The original incident text
                    - Your initial audit findings
                    - Network Team procedures
                    
                    Provide specific, evidence-based responses. If asked about specific questions or findings:
                    - Quote exact text from the incident
                    - Reference specific compliance requirements
                    - Suggest concrete improvements
                    - Offer alternative interpretations if valid
                    
                    Original incident text for reference:
                    {self.original_text[:5000]}...
                    """}
                ],
                max_tokens=1500 if model == "gpt-4" else 1200,
                temperature=0.4
            )
            
            ai_response = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            return ai_response
            
        except Exception as e:
            # Fallback for rate limits
            if "rate_limit" in str(e).lower() and model == "gpt-4":
                print("⚠️ Falling back to GPT-4o-mini for conversation...")
                return self.continue_conversation(user_message, "gpt-4o-mini")
            return f"Error in conversation: {str(e)}"
    
    def get_suggested_questions(self):
        """Generate suggested follow-up questions based on the audit"""
        if not self.audit_context:
            return []
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Generate 5 insightful follow-up questions about this audit."},
                    {"role": "user", "content": f"Based on this audit: {self.audit_context[:1000]}... what questions should we explore?"}
                ],
                max_tokens=300,
                temperature=0.5
            )
            
            suggestions = response.choices[0].message.content
            return suggestions.split('\n')
            
        except Exception as e:
            return [f"Error generating suggestions: {str(e)}"]
    
    def export_conversation(self):
        """Export the full audit conversation"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audit_conversation_{timestamp}.json"
        
        export_data = {
            "timestamp": timestamp,
            "audit_context": self.audit_context,
            "conversation": self.conversation_history,
            "original_text_length": len(self.original_text) if self.original_text else 0
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filename
    
    def reset_conversation(self):
        """Reset the conversation for a new audit"""
        self.conversation_history = []
        self.audit_context = None
        self.original_text = None

if __name__ == "__main__":
    # Command line interface for testing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python interactive_auditor.py <pdf_file>")
        sys.exit(1)
    
    # Import PDF parser
    from pdf_parser import extract_text_from_pdf, redact_pii
    
    pdf_file = sys.argv[1]
    print(f"Loading and processing {pdf_file}...")
    
    # Extract and redact text
    text = extract_text_from_pdf(pdf_file)
    redacted = redact_pii(text)
    
    # Start interactive audit
    auditor = InteractiveAuditor()
    print("\n=== PERFORMING INITIAL AUDIT ===")
    initial_audit = auditor.perform_initial_audit(redacted)
    print(initial_audit)
    
    print("\n=== INTERACTIVE MODE ===")
    print("You can now ask questions about the audit. Type 'quit' to exit, 'export' to save conversation.")
    
    while True:
        user_input = input("\nYour question: ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            break
        elif user_input.lower() == 'export':
            filename = auditor.export_conversation()
            print(f"Conversation exported to {filename}")
            continue
        elif user_input.lower() == 'suggestions':
            suggestions = auditor.get_suggested_questions()
            print("\nSuggested questions:")
            for i, suggestion in enumerate(suggestions[:5], 1):
                print(f"{i}. {suggestion.strip()}")
            continue
        
        response = auditor.continue_conversation(user_input)
        print(f"\nAI Auditor: {response}")
