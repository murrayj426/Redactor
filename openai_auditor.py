import openai
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

class TicketAuditor:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def load_incident_documentation(self):
        """Load incident handling documentation if available"""
        doc_paths = [
            "incident_handling_procedures.txt",
            "incident_documentation.md",
            "procedures/incident_handling.txt",
            "docs/incident_procedures.md"
        ]
        
        for path in doc_paths:
            try:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        return f.read()
            except:
                continue
        
        return None

    def create_audit_prompt(self, redacted_text, audit_type="general"):
        """Create audit prompt based on type with 15-question framework"""
        
        # Load incident documentation if available
        incident_docs = self.load_incident_documentation()
        doc_reference = ""
        if incident_docs:
            doc_reference = f"\n\nREFERENCE DOCUMENTATION:\n{incident_docs}\n\nUse the above documentation as your reference for best practices and procedures.\n"
        
    def create_audit_prompt(self, redacted_text, audit_type="general"):
        """Create audit prompt based on type with optimized 15-question framework"""
        
        # Load incident documentation if available (summarized version)
        incident_docs = self.load_incident_documentation()
        doc_reference = ""
        if incident_docs:
            # Summarize key points to reduce token usage
            key_points = """
KEY STANDARDS:
- First Access must be marked when logging into device/contacting client
- All heading fields (CI, Location, Service Offering/Category) must be populated
- Use proper Pending Codes: Client Action Required, Client Hold, RMA, Carrier, etc.
- P1/P2: Hourly updates, work with client on phone until resolution
- P3/P4: Updates every 2-3 days or per agreed event dates
- Time Worked entries are mandatory for cost tracking
- Use SNC email templates, copy to Additional Comments
- Close Notes must reflect all resolution steps
- Proper Close/Cause Codes required
"""

    def create_audit_prompt(self, redacted_text):
        """Create the audit prompt using Network Team procedures as the standard"""
        
        # Always use the Network Team procedures - no "focus" needed
        with open('incident_handling_procedures.txt', 'r') as f:
            procedures = f.read()
        
        audit_questions = f"""
**NETWORK TEAM INCIDENT AUDIT**

**COMPLIANCE STANDARD**: All questions are evaluated against Network Team Incident Management Documentation.

**NETWORK TEAM PROCEDURES (Reference):**
{procedures[:2000]}...

**CRITICAL INSTRUCTIONS**:
- Question 1: Simply identify and display the INC number (not a compliance check)
- Only use N/A for questions 12 and 14 when truly not applicable
- Questions 2-11, 13, and 15 should ALWAYS be answered Yes or No
- If you cannot find evidence, answer "No" and explain what's missing
- N/A should be rare - most questions apply to every incident
- **Accept common abbreviations**: "Client H." = "Client Hold", "CAR" = "Client Action Required", etc.
- **Be reasonable with formats**: Minor variations in wording/format should not automatically fail compliance

**RESPONSE FORMAT**: 
- **Question 1**: Simply display the INC number found
- **Questions 2-15**: For EACH question provide:

**QUESTION [NUMBER]: [REPEAT THE FULL QUESTION TEXT]**
1. **ANSWER**: Yes/No (or N/A only for questions 12 & 14 when appropriate)
2. **EVIDENCE**: Quote specific text from the ticket that supports your answer
3. **ANALYSIS**: Explain what you looked for and your reasoning based on Network Team standards

**EXAMPLE FORMAT:**
**QUESTION 2: Are CI/Location, State/Pending, Service Offering/Category properly populated?**
1. **ANSWER**: Yes
2. **EVIDENCE**: "CI: ROUTER-NYC-01, Location: New York Office, Service Offering: Network Infrastructure"
3. **ANALYSIS**: All required heading fields are properly populated per Network Team standards...

---

**1. Incident Number Identification**
**Question**: Identify and display the ServiceNow INC######## number from the ticket
**Answer Required**: Display the INC number found (or "Not Found" if missing)
**Network Team Standard**: Simply identify the incident number for reference

**2. Heading Fields Documentation**
**Question**: Are CI/Location, State/Pending, Service Offering/Category properly populated?
**Answer Required**: Yes/No (N/A not allowed)
**Network Team Standard**: Configuration Item, CI Location, Service Offering/Category must be verified for accuracy

**3. First Access Verification**
**Question**: Was First Access properly checked/marked when first accessing device or contacting client?
**Answer Required**: Yes/No (N/A not allowed)
**Network Team Standard**: First access should be checked when logging into device/contacting client

**4. Engineer Ownership Acknowledgment**
**Question**: Did engineer acknowledge ownership to customer with ticket summary?
**Answer Required**: Yes/No (N/A not allowed)
**Network Team Standard**: Engineer should acknowledge ownership with update to client including ticket summary

**5. Event Date Management**
**Question**: Are Event Dates used accurately for next follow-up scheduling?
**Answer Required**: Yes/No (N/A not allowed)
**Network Team Standard**: Event Date should accurately reflect the time for next follow up

**6. Pending Code Usage**
**Question**: Are Pending Codes used correctly per Network Team procedures?
**Answer Required**: Yes/No (N/A not allowed)
**Network Team Standard**: Correct usage of Pending Codes (Client Action Required, Client Hold, RMA, Carrier, etc.)
**Note**: Accept common abbreviations (e.g., "Client H." = "Client Hold", "CAR" = "Client Action Required")

**7. Status Field Updates**
**Question**: Are Current Status/Next Steps updated appropriately?
**Answer Required**: Yes/No (N/A not allowed)
**Network Team Standard**: Any change in current status or next steps requires documentation

**8. Client Communication Quality**
**Question**: Are detailed, professional updates provided to client?
**Answer Required**: Yes/No (N/A not allowed)
**Network Team Standard**: All client facing updates must be professional, detailed, and proofread

**9. Troubleshooting Documentation**
**Question**: Are troubleshooting steps documented thoroughly with evidence?
**Answer Required**: Yes/No (N/A not allowed)
**Network Team Standard**: Troubleshooting steps must be documented with evidence and explanations

**10. Timely Update Compliance**
**Question**: Were updates provided per Network Team priority standards?
**Answer Required**: Yes/No (N/A not allowed)
**Network Team Standard**: P1/P2: hourly updates, P3: every 2 days, P4: every 3 days

**11. Procedure Following**
**Question**: Were Network Team procedures and templates followed correctly?
**Answer Required**: Yes/No (N/A not allowed)
**Network Team Standard**: Must follow Ticket Acceptance/Update Templates and manual SNC email process

**12. Task Management**
**Question**: Were necessary Activity & Change tasks opened appropriately?
**Answer Required**: Yes/No/N/A (N/A only if no tasks/changes were needed for this incident type)
**Network Team Standard**: Proper Activity and Change task creation when required

**13. Time Tracking Accuracy**
**Question**: Is Time Worked accurately documented for cost tracking?
**Answer Required**: Yes/No (N/A not allowed)
**Network Team Standard**: Time Worked field must be populated accurately for cost evaluation

**14. Resolution Documentation**
**Question**: Do Close Notes reflect work done with evidence of resolution?
**Answer Required**: Yes/No/N/A (N/A only if incident is still open/not resolved)
**Network Team Standard**: Close notes should include issue summary, steps taken, and resolution evidence

**15. Overall Performance Assessment**
**Question**: Rate overall engineer performance on this incident (1-10 scale)
**Answer Required**: Yes with 1-10 score (N/A not allowed)
**Network Team Standard**: Overall compliance with Network Team incident management procedures

---

**SCORING RULES:**
- Question 1: Display INC number (not scored)
- Questions 2-11, 13, 15: MUST be answered Yes/No based on Network Team standards
- Question 12: N/A only if no Activity/Change tasks were required
- Question 14: N/A only if incident is still open
- If evidence is missing, answer "No" and explain what should be there per Network Team procedures
- Calculate score based on applicable Yes/No responses only (questions 2-15)

**AUDIT NOTES SECTION:**
📋 **PERSONAL AUDIT NOTES FROM YOUR TEAM LEAD**:
Write this section as if the team lead is personally reviewing the engineer's work and giving direct feedback. Use a conversational, supportive tone that shows you've carefully reviewed their work. Include:

- 👏 **What I Really Liked**: Specific things the engineer did that impressed you as their manager
- 💡 **Areas for Growth**: Friendly suggestions for improvement, written as coaching advice
- 🎯 **My Overall Take**: Personal assessment written directly to the engineer, acknowledging their effort and providing encouragement

Write in first person ("I noticed...", "Great job on...", "Next time, consider...") as if the team lead is speaking directly to the engineer. Be supportive but honest, like a good manager giving performance feedback.

**FOR FAILED ASSESSMENTS**: When marking any question as "No", always include these sections:

1. **📖 PROCEDURE REFERENCE** - Quote relevant procedure section from the documentation
2. **💡 TEAM LEAD GUIDANCE** - Technical context about the requirement
3. **❌ WHAT YOU MISSED** - 2-3 sentence plain-English explanation of the specific gap
4. **🎯 WHAT TO DO NEXT** - 1-2 sentence actionable next step

Use clear formatting, emojis, and a warm, professional tone throughout your audit. Make it feel personal and meaningful!

INCIDENT TEXT TO ANALYZE:
{{text}}
"""

        return audit_questions.format(text=redacted_text)
        
        audit_questions = f"""
**NETWORK TEAM DETAILED AUDIT - 15 QUESTIONS**
{doc_reference}

**CRITICAL INSTRUCTIONS**: 
- Only use N/A for questions 12 and 14 when truly not applicable
- Questions 1-11, 13, and 15 should ALWAYS be answered Yes or No
- If you cannot find evidence, answer "No" and explain what's missing
- N/A should be rare - most questions apply to every incident

**RESPONSE FORMAT**: For EACH question provide:

**QUESTION X: 🎯 [Question Title]**

**STATUS**: ✅ PASS or ❌ FAIL

**EVIDENCE**: Quote specific text from the ticket that supports your answer

**ANALYSIS**: Explain what you looked for and your reasoning

For failed assessments, also include:
**📖 PROCEDURE REFERENCE**: Quote from documentation
**💡 TEAM LEAD GUIDANCE**: Context about requirement  
**❌ WHAT YOU MISSED**: Plain English explanation
**🎯 WHAT TO DO NEXT**: Actionable next step

---

**1. Incident Number Identification**
**Question**: Identify and verify the ServiceNow INC######## number is present
**Answer Required**: Yes/No (N/A not allowed)
**What to look for**: ServiceNow incident number format (INC followed by digits)

**2. Heading Fields Documentation**
**Question**: Are CI/Location, State/Pending, Service Offering/Category properly populated?
**Answer Required**: Yes/No (N/A not allowed)
**What to look for**: Configuration Item names, device locations, incident states, service categories

**3. First Access Verification**
**Question**: Was First Access properly checked/marked when first accessing device or contacting client?
**Answer Required**: Yes/No (N/A not allowed)
**What to look for**: "First access" mentions, initial troubleshooting, device login, first client contact
**If missing**: Answer "No" - this is a compliance requirement for all incidents

**4. Engineer Ownership Acknowledgment**
**Question**: Did engineer acknowledge ownership to customer with ticket summary?
**Answer Required**: Yes/No (N/A not allowed)
**What to look for**: Initial client communication, ownership statements, ticket summary to client

**5. Event Date Management**
**Question**: Are Event Dates used accurately for next follow-up scheduling?
**Answer Required**: Yes/No (N/A not allowed)
**What to look for**: Event date entries, follow-up scheduling, future action dates

**6. Pending Code Usage**
**Question**: Are Pending Codes used correctly (Client Action Required, RMA, Carrier, etc.)?
**Answer Required**: Yes/No (N/A not allowed)
**What to look for**: Pending status, pending reasons, appropriate code selection

**7. Status Field Updates**
**Question**: Are Current Status/Next Steps updated appropriately?
**Answer Required**: Yes/No (N/A not allowed)
**What to look for**: Status entries, next steps documentation, action items

**8. Client Communication Quality**
**Question**: Are detailed, professional updates provided to client?
**Answer Required**: Yes/No (N/A not allowed)
**What to look for**: Client-facing updates, professional tone, detailed explanations

**9. Troubleshooting Documentation**
**Question**: Are troubleshooting steps documented thoroughly with evidence?
**Answer Required**: Yes/No (N/A not allowed)
**What to look for**: Technical steps, command outputs, screenshots, diagnostic work
**If missing**: Answer "No" - troubleshooting documentation is required

**10. Timely Update Compliance**
**Question**: Were updates provided per priority standards?
**Answer Required**: Yes/No (N/A not allowed)
**What to look for**: Update frequency based on priority level, timing compliance

**11. Procedure Following**
**Question**: Were Network Team procedures followed correctly?
**Answer Required**: Yes/No (N/A not allowed)
**What to look for**: Template usage, escalation processes, standard procedures

**12. Task Management**
**Question**: Were necessary Activity & Change tasks opened appropriately?
**Answer Required**: Yes/No/N/A (N/A only if no tasks/changes were needed for this incident type)
**What to look for**: Activity tasks, Change requests, task workflows

**13. Time Tracking Accuracy**
**Question**: Is Time Worked accurately documented for cost tracking?
**Answer Required**: Yes/No (N/A not allowed)
**What to look for**: Time entries, work duration, time logging accuracy

**14. Resolution Documentation**
**Question**: Do Close Notes reflect work done with evidence of resolution?
**Answer Required**: Yes/No/N/A (N/A only if incident is still open/not resolved)
**What to look for**: 
- "Close notes:" or "Resolution notes:" sections
- Issue description and summary of problem
- Technical observations and findings
- Evidence of resolution (screenshots, test results, confirmations)
- Steps taken to resolve (RMA, configuration changes, health checks)
- Final status confirmation
- Work summary with technical details

**15. Overall Performance Assessment**
**Question**: Rate overall engineer performance on this incident (1-10 scale)
**Answer Required**: Yes with 1-10 score (N/A not allowed)
**What to look for**: Overall compliance, professionalism, technical competence

---

**SCORING RULES:**
- Questions 1-11, 13, 15: MUST be answered Yes/No
- Question 12: N/A only if no Activity/Change tasks were required
- Question 14: N/A only if incident is still open
- If evidence is missing, answer "No" and explain what should be there
- Calculate score based on applicable Yes/No responses only

**AUDIT NOTES SECTION:**
Provide comprehensive audit notes as a single professional paragraph addressing the engineer directly.

INCIDENT TEXT TO ANALYZE:
{{text}}
"""

        return audit_questions.format(text=redacted_text)
    
    def audit_ticket(self, redacted_text, model="gpt-4o-mini", retry_delay=60):
        """Send redacted text to OpenAI for auditing using Network Team standards"""
        import time
        
        try:
            # Smart truncation - keep key sections for auditing
            original_length = len(redacted_text)
            if original_length > 25000:  # Even higher limit for very large documents
                # Try to preserve important sections for auditing
                lines = redacted_text.split('\n')
                
                # Look for key audit-relevant sections with better filtering
                important_lines = []
                current_section = []
                
                for line in lines:
                    line_lower = line.lower().strip()
                    # Enhanced keywords for better audit content detection
                    if any(keyword in line_lower for keyword in [
                        'incident', 'inc', 'ticket', 'assigned', 'priority', 'status',
                        'first access', 'pending', 'event date', 'time worked', 'close',
                        'resolution', 'customer', 'client', 'update', 'comment', 'work notes',
                        'troubleshoot', 'investigation', 'root cause', 'configuration', 'ci',
                        'service offering', 'category', 'sub-category', 'impact', 'urgency',
                        'template', 'acknowledgment', 'ownership', 'communication', 'email',
                        'phone', 'webex', 'change', 'activity', 'task', 'escalation',
                        'close notes', 'resolution notes', 'observations', 'issue description',
                        'rma', 'health check', 'vpn', 'dns', 'cpu', 'memory', 'screenshots',
                        'deployed', 'reachable', 'utilization', 'successfully', 'performed'
                    ]) or line.startswith(('•', '-', '*')) or ':' in line:
                        # Add some context lines before important content
                        important_lines.extend(current_section[-1:])  # Keep 1 line of context
                        important_lines.append(line)
                        current_section = []
                    else:
                        current_section.append(line)
                        if len(current_section) > 5:  # Don't keep too much irrelevant content
                            current_section = current_section[-2:]
                
                # If we got good content, use it; otherwise fall back to strategic truncation
                if len(important_lines) > 100:  # We found substantial relevant content
                    smart_text = '\n'.join(important_lines)
                    if len(smart_text) > 25000:
                        redacted_text = smart_text[:25000] + "\n\n[TRUNCATED - Showing audit-relevant sections]"
                    else:
                        redacted_text = smart_text + "\n\n[SMART EXTRACTION - Key audit sections preserved]"
                    print(f"🎯 Smart extraction: Reduced from {original_length:,} to {len(redacted_text):,} chars while preserving audit content")
                else:
                    # Strategic truncation: keep beginning, middle sample, and end
                    start_text = redacted_text[:10000]
                    middle_start = len(redacted_text) // 2 - 2500
                    middle_text = redacted_text[middle_start:middle_start + 5000]
                    end_text = redacted_text[-10000:]
                    redacted_text = (start_text + 
                                   f"\n\n[MIDDLE SECTION SAMPLE - {middle_start:,} to {middle_start+5000:,} chars]\n\n" + 
                                   middle_text +
                                   f"\n\n[FINAL SECTION - Last 10,000 chars]\n\n" + 
                                   end_text)
                    print(f"📄 Strategic truncation: Preserved beginning, middle sample, and end from {original_length:,} chars")
            else:
                print(f"📝 Document size OK: {original_length:,} characters, no truncation needed")
            
            prompt = self.create_audit_prompt(redacted_text)
            
            # Try the requested model first
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "You are a Network Team incident auditor. Provide concise, structured audit responses."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=1500,
                        temperature=0.3
                    )
                    return response.choices[0].message.content
                
                except Exception as e:
                    if "rate_limit_exceeded" in str(e) or "tokens" in str(e):
                        if attempt < max_retries - 1:
                            print(f"Rate limit hit, waiting {retry_delay} seconds before retry {attempt + 1}/{max_retries}...")
                            time.sleep(retry_delay)
                            continue
                        else:
                            # Final fallback to GPT-3.5-turbo
                            print("Max retries reached, falling back to GPT-3.5-turbo...")
                            response = self.client.chat.completions.create(
                                model="gpt-3.5-turbo",
                                messages=[
                                    {"role": "system", "content": "You are a Network Team incident auditor. Provide concise, structured audit responses."},
                                    {"role": "user", "content": prompt}
                                ],
                                max_tokens=1500,
                                temperature=0.3
                            )
                            return response.choices[0].message.content
                    else:
                        raise e
            
        except Exception as e:
            return f"Error during audit: {str(e)}"
    
    def save_audit_report(self, audit_result, filename_prefix="audit"):
        """Save audit report to file with structured format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/{filename_prefix}_{timestamp}.txt"
        
        with open(filename, "w") as f:
            f.write(f"=== INCIDENT AUDIT REPORT (15-QUESTION FRAMEWORK) ===\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Audit Type: {filename_prefix.replace('_audit', '').upper()}\n")
            f.write(f"{'='*60}\n\n")
            f.write(audit_result)
            f.write(f"\n\n{'='*60}\n")
            f.write(f"Report saved to: {filename}\n")
        
        return filename
    
    def create_audit_summary(self, audit_result):
        """Extract key metrics from audit result for dashboard with proper N/A handling"""
        try:
            # Simple parsing to extract scores (this could be enhanced)
            lines = audit_result.split('\n')
            scores = []
            na_count = 0
            overall_score = None
            
            for line in lines:
                # Count N/A responses (should not affect scoring)
                if 'N/A' in line and any(q in line for q in ['12.', '14.', 'Tasks', 'Close Notes']):
                    na_count += 1
                elif 'score' in line.lower() or '/10' in line:
                    # Extract numerical scores only for applicable questions
                    import re
                    score_match = re.search(r'(\d+(?:\.\d+)?)/10', line)
                    if score_match and 'N/A' not in line:
                        scores.append(float(score_match.group(1)))
                elif 'overall' in line.lower() and '/10' in line:
                    score_match = re.search(r'(\d+(?:\.\d+)?)/10', line)
                    if score_match:
                        overall_score = float(score_match.group(1))
            
            # Calculate percentage based on applicable questions only
            total_applicable = 15 - na_count
            
            return {
                'individual_scores': scores,
                'average_score': sum(scores)/len(scores) if scores else None,
                'overall_score': overall_score,
                'total_questions': 15,
                'applicable_questions': total_applicable,
                'na_responses': na_count,
                'compliance_percentage': (len([s for s in scores if s >= 7]) / len(scores) * 100) if scores else None
            }
        except:
            return None
    
    def get_available_models(self):
        """Get list of available OpenAI models"""
        try:
            models = self.client.models.list()
            return [model.id for model in models.data if 'gpt' in model.id]
        except:
            return ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"]
