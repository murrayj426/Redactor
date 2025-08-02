"""
Claude 3.5 Sonnet-powered Network Team Audit System
Specialized for superior compliance reasoning and procedural analysis
"""

import os
import re
from datetime import datetime
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()

class ClaudeAuditor:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        
        # Load Network Team procedures
        try:
            with open('incident_handling_procedures.txt', 'r') as f:
                self.procedures = f.read()
        except FileNotFoundError:
            self.procedures = "Network Team procedures file not found."
    
    def create_audit_prompt(self, ticket_text, audit_type="general"):
        """Create structured audit prompt optimized for Claude's reasoning capabilities"""
        
        prompt = f"""You are a senior Network Team compliance auditor with expertise in systematic procedural analysis. Your task is to conduct a thorough compliance audit of this incident ticket against Network Team standards.

IMPORTANT: Apply reasonable standards - for ownership acknowledgment (Question 4), basic ownership statements are sufficient and should be marked as compliant.

FORMATTING EXAMPLE:
**QUESTION 2: 📋 CI/Location/Service Fields**

**STATUS**: ✅ PASS

**EVIDENCE**: 
- "Configuration item: PRNFSPA-TowerFW01"
- "Location: PR-Niagara F. Tower" 
- "Service Offering: Network Services"
- "Category: Security Device Management"

**ANALYSIS**: All required fields are populated with appropriate values! 🎯

---

NETWORK TEAM PROCEDURES:
{self.procedures}

INCIDENT TICKET TO AUDIT:
{ticket_text}

AUDIT INSTRUCTIONS:
Perform a comprehensive step-by-step analysis for each of the 15 compliance questions below. 

FORMAT REQUIREMENTS:
- Use ✅ for passing questions and ❌ for failing questions
- Add blank lines between sections for better readability
- Use clear headers and emoji for better readability
- Focus on compliance, not formatting - abbreviated fields are acceptable if meaningful
- Make the output engaging and easy to scan with proper spacing

For each question, provide:
1. **STATUS**: ✅ PASS / ❌ FAIL / ⚠️ N/A with clear visual indicator
2. **EVIDENCE**: Complete, untruncated quotes from the ticket (on separate lines)
3. **ANALYSIS**: Brief, clear explanation in friendly language
4. Add a separator line (---) between questions for better readability

COMPLIANCE QUESTIONS:

**QUESTION 1: 🎯 Identify and display the ServiceNow INC######## number from the ticket**
(This is identification only - display the INC number without compliance assessment)

**QUESTION 2: 📋 Are CI/Location, State/Pending, Service Offering/Category properly populated?**
Verify all required fields contain appropriate values per Network Team standards. Focus on whether fields are populated with valid values, not formatting or truncation issues.

**QUESTION 3: 🔐 Was First Access properly checked/marked when first accessing device or contacting client?**
Check for proper First Access verification and documentation.

**QUESTION 4: 👤 Did engineer acknowledge ownership to customer with ticket summary?**
Look for clear ownership acknowledgment. Basic ownership statement is sufficient per Network Team standards.

**QUESTION 5: 📅 Are Event Dates used accurately for next follow-up scheduling?**
Verify follow-up dates are set appropriately per priority and procedures.

**QUESTION 6: ⏸️ Are Pending Codes used correctly per Network Team procedures?**
Check for proper use of pending codes (Client, Vendor, Internal, etc.) with clear reasoning.

**QUESTION 7: 📊 Are Current Status/Next Steps updated appropriately?**
Verify status updates are clear, actionable, and follow proper format.

**QUESTION 8: 💬 Are detailed, professional updates provided to client?**
Assess quality, professionalism, and completeness of client communications.

**QUESTION 9: 🔧 Are troubleshooting steps documented thoroughly with evidence?**
Check for comprehensive documentation of all troubleshooting actions and results.

**QUESTION 10: ⏰ Were updates provided per Network Team priority standards?**
Verify update frequency matches incident priority and escalation requirements.

**QUESTION 11: 📝 Were Network Team procedures and templates followed correctly?**
Check adherence to standard procedures, templates, and documentation formats.

**QUESTION 12: 📋 Were necessary Activity & Change tasks opened appropriately?**
Verify proper task creation and linkage per Network Team procedures.

**QUESTION 13: ⏱️ Is Time Worked accurately documented for cost tracking?**
Check for accurate time tracking and appropriate billing documentation.

**QUESTION 14: ✅ Do Close Notes reflect work done with evidence of resolution?**
Assess closure documentation quality and resolution evidence (if applicable).

**QUESTION 15: 🎯 Rate overall engineer performance on this incident (1-10 scale)**
Provide numerical rating with detailed justification based on compliance and execution quality.

📋 **PERSONAL AUDIT NOTES FROM JEREMY**:
Write this section as if Jeremy (the team lead) is personally reviewing the engineer's work and giving direct feedback. Use a conversational, supportive tone that shows you've carefully reviewed their work. Include:

- 👏 **What I Really Liked**: Specific things the engineer did that impressed you as their manager
- � **Areas for Growth**: Friendly suggestions for improvement, written as coaching advice
- 🎯 **My Overall Take**: Personal assessment written directly to the engineer, acknowledging their effort and providing encouragement

Write in first person ("I noticed...", "Great job on...", "Next time, consider...") as if Jeremy is speaking directly to the engineer. Be supportive but honest, like a good manager giving performance feedback.

Use clear formatting, emojis, and a warm, professional tone throughout your audit. Make it feel personal and meaningful!"""

        return prompt
    
    def audit_ticket(self, ticket_text, audit_type="general", model="claude-3-5-sonnet-20241022"):
        """Conduct audit using Claude 3.5 Sonnet's superior reasoning capabilities"""
        
        try:
            prompt = self.create_audit_prompt(ticket_text, audit_type)
            
            response = self.client.messages.create(
                model=model,
                max_tokens=4000,
                temperature=0.1,  # Low temperature for consistent compliance analysis
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Error during Claude audit: {str(e)}\n\nPlease check your ANTHROPIC_API_KEY in the .env file."
    
    def save_audit_report(self, audit_result, audit_type="general"):
        """Save audit report with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/claude_{audit_type}_audit_{timestamp}.txt"
        
        # Ensure reports directory exists
        os.makedirs('reports', exist_ok=True)
        
        with open(filename, 'w') as f:
            f.write("="*80)
            f.write(f"\nCLAUDE 3.5 SONNET NETWORK TEAM AUDIT REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Audit Type: {audit_type.upper()}\n")
            f.write("="*80)
            f.write("\n\n")
            f.write(audit_result)
        
        return filename

# Test function for command line usage
def main():
    if len(sys.argv) != 2:
        print("Usage: python claude_auditor.py <path_to_text_file>")
        return
    
    auditor = ClaudeAuditor()
    
    with open(sys.argv[1], 'r') as f:
        ticket_text = f.read()
    
    result = auditor.audit_ticket(ticket_text)
    print(result)

if __name__ == "__main__":
    import sys
    main()
