"""
Base Auditor Class - Shared audit logic for Network Team compliance
Contains all shared functionality between OpenAI and Claude auditors
"""

import os
from datetime import datetime
from abc import ABC, abstractmethod

# Import optimization utilities
from utils.error_handling import smart_error_handler, monitor_performance
from utils.cache_utils import load_network_procedures
from utils.ai_utils import optimize_prompt_for_model, RateLimiter

class BaseAuditor(ABC):
    def __init__(self):
        self.rate_limiter = RateLimiter()
        # Load incident documentation with caching
        self.incident_documentation = load_network_procedures()
    
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

**FORMATTING REQUIREMENTS**:
- Use proper spacing and line breaks for readability
- Add blank lines between STATUS, EVIDENCE, and ANALYSIS sections
- Separate each question with horizontal dividers (---)
- Keep consistent bold formatting throughout
- Make the output clean and professional

**RESPONSE FORMAT**: 
- **Question 1**: Simply display the INC number found
- **Questions 2-15**: For EACH question provide:

---

**QUESTION [NUMBER]: [REPEAT THE FULL QUESTION TEXT]**

**STATUS**: ✅ PASS or ❌ FAIL (or ⚠️ N/A only for questions 12 & 14 when appropriate)

**EVIDENCE**: Quote specific text from the ticket that supports your answer

**ANALYSIS**: Explain what you looked for and your reasoning based on Network Team standards

---

**EXAMPLE FORMAT:**

**QUESTION 2: Are CI/Location, State/Pending, Service Offering/Category properly populated?**

**STATUS**: ✅ PASS

**EVIDENCE**: "CI: ROUTER-NYC-01, Location: New York Office, Service Offering: Network Infrastructure"

**ANALYSIS**: All required heading fields are properly populated per Network Team standards...

CRITICAL: Use proper line breaks and spacing. Add a blank line after each section (STATUS, EVIDENCE, ANALYSIS) and separate each question with horizontal rules (---) for clean formatting.

---

**1. Incident Number Identification**
**Question**: Identify and display the ServiceNow INC######## number from the ticket
**Answer Required**: Display the INC number found (or "Not Found" if missing)
**Network Team Standard**: Simply identify the incident number for reference

**2. Heading Fields Documentation**
**Question**: Are CI/Location, State/Pending, Service Offering/Category properly populated?
**Answer Required**: ✅ PASS / ❌ FAIL (N/A not allowed)
**Network Team Standard**: Configuration Item, CI Location, Service Offering/Category must be verified for accuracy

**3. First Access Verification**
**Question**: Was First Access properly checked/marked when first accessing device or contacting client?
**Answer Required**: ✅ PASS / ❌ FAIL (N/A not allowed)
**Network Team Standard**: First access should be checked when logging into device/contacting client

**4. Engineer Ownership Acknowledgment**
**Question**: Did engineer acknowledge ownership to customer with ticket summary?
**Answer Required**: ✅ PASS / ❌ FAIL (N/A not allowed)
**Network Team Standard**: Engineer should acknowledge ownership with update to client including ticket summary

**5. Event Date Management**
**Question**: Are Event Dates used accurately for next follow-up scheduling?
**Answer Required**: ✅ PASS / ❌ FAIL (N/A not allowed)
**Network Team Standard**: Event Date should accurately reflect the time for next follow up

**6. Pending Code Usage**
**Question**: Are Pending Codes used correctly per Network Team procedures?
**Answer Required**: ✅ PASS / ❌ FAIL (N/A not allowed)
**Network Team Standard**: Correct usage of Pending Codes (Client Action Required, Client Hold, RMA, Carrier, etc.)
**Note**: Accept common abbreviations (e.g., "Client H." = "Client Hold", "CAR" = "Client Action Required")

**7. Status Field Updates**
**Question**: Are Current Status/Next Steps updated appropriately?
**Answer Required**: ✅ PASS / ❌ FAIL (N/A not allowed)
**Network Team Standard**: Any change in current status or next steps requires documentation

**8. Client Communication Quality**
**Question**: Are detailed, professional updates provided to client?
**Answer Required**: ✅ PASS / ❌ FAIL (N/A not allowed)
**Network Team Standard**: All client facing updates must be professional, detailed, and proofread

**9. Troubleshooting Documentation**
**Question**: Are troubleshooting steps documented thoroughly with evidence?
**Answer Required**: ✅ PASS / ❌ FAIL (N/A not allowed)
**Network Team Standard**: Troubleshooting steps must be documented with evidence and explanations

**10. Timely Update Compliance**
**Question**: Were updates provided per Network Team priority standards?
**Answer Required**: ✅ PASS / ❌ FAIL (N/A not allowed)
**Network Team Standard**: P1/P2: hourly updates, P3: every 2 days, P4: every 3 days

**11. Procedure Following**
**Question**: Were Network Team procedures and templates followed correctly?
**Answer Required**: ✅ PASS / ❌ FAIL (N/A not allowed)
**Network Team Standard**: Must follow Ticket Acceptance/Update Templates and manual SNC email process

**12. Task Management**
**Question**: Were necessary Activity & Change tasks opened appropriately?
**Answer Required**: ✅ PASS / ❌ FAIL / ⚠️ N/A (N/A only if no tasks/changes were needed for this incident type)
**Network Team Standard**: Proper Activity and Change task creation when required

**13. Time Tracking Accuracy**
**Question**: Is Time Worked accurately documented for cost tracking?
**Answer Required**: ✅ PASS / ❌ FAIL (N/A not allowed)
**Network Team Standard**: Time Worked field must be populated accurately for cost evaluation

**14. Resolution Documentation**
**Question**: Do Close Notes reflect work done with evidence of resolution?
**Answer Required**: ✅ PASS / ❌ FAIL / ⚠️ N/A (N/A only if incident is still open/not resolved)
**Network Team Standard**: Close notes should include issue summary, steps taken, and resolution evidence

**15. Overall Performance Assessment**
**Question**: Rate overall engineer performance on this incident (1-10 scale)
**Answer Required**: ✅ PASS with 1-10 score (N/A not allowed)
**Network Team Standard**: Overall compliance with Network Team incident management procedures

---

**SCORING RULES:**
- Question 1: Display INC number (not scored)
- Questions 2-11, 13, 15: MUST use ✅ PASS or ❌ FAIL based on Network Team standards
- Question 12: ⚠️ N/A only if no Activity/Change tasks were required
- Question 14: ⚠️ N/A only if incident is still open
- If evidence is missing, use ❌ FAIL and explain what should be there per Network Team procedures
- Calculate score based on applicable PASS/FAIL responses only (questions 2-15)

**AUDIT NOTES SECTION:**

---

📋 **PERSONAL AUDIT NOTES FROM YOUR TEAM LEAD**:

Write a concise 2-3 sentence audit note using **Markdown formatting** with the following structure:

**[Engineer Name],** your handling of incident [INC#] shows **[key strength - reference specific Network Team procedure compliance]**. **[One area for improvement or continued excellence, referencing Network Team standards]**. **[Encouraging conclusion about overall performance]**.

**EXAMPLE:**

**Kaushal S.,** your handling of incident INC11814999 shows **excellent adherence to our Ticket Acceptance Templates and professional client communication standards**. **Continue this level of thorough troubleshooting documentation - it's exactly what our Network Team procedures require**. **Great work maintaining procedural compliance throughout the incident lifecycle**.

Use this **bold formatting**, keep it personal and supportive, and make it feel like authentic manager feedback that directly references Network Team procedures and standards.

---

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
    
    @abstractmethod
    def audit_ticket(self, redacted_text, model=None):
        """Abstract method - must be implemented by provider-specific classes"""
        pass
    
    def save_audit_report(self, audit_result, filename_prefix="audit"):
        """Save audit report to file with structured format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/{filename_prefix}_{timestamp}.txt"
        
        # Ensure reports directory exists
        os.makedirs("reports", exist_ok=True)
        
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

    def extract_audit_score_from_text(self, audit_text):
        """Enhanced audit score extraction with PASS/FAIL counting and debug information"""
        import re
        
        # Patterns for modern audit format with emojis
        pass_patterns = [
            r'✅\s*PASS',
            r'STATUS.*?✅.*?PASS', 
            r'PASS.*?✅',
            r'✅.*?PASS'
        ]
        
        fail_patterns = [
            r'❌\s*FAIL',
            r'STATUS.*?❌.*?FAIL',
            r'FAIL.*?❌', 
            r'❌.*?FAIL'
        ]
        
        pass_count = 0
        fail_count = 0
        
        # Try multiple patterns to catch all variations
        for pattern in pass_patterns:
            matches = re.findall(pattern, audit_text, re.IGNORECASE | re.DOTALL)
            if matches:
                pass_count = max(pass_count, len(matches))
        
        for pattern in fail_patterns:
            matches = re.findall(pattern, audit_text, re.IGNORECASE | re.DOTALL)
            if matches:
                fail_count = max(fail_count, len(matches))
        
        # Count total questions for verification
        question_count = len(re.findall(r'\*\*QUESTION\s+\d+', audit_text, re.IGNORECASE))
        
        # Look for traditional score patterns first
        score_patterns = [
            r'(\d+)/(\d+)\s*\((\d+)%\)',  # "11/12 (92%)"
            r'TOTAL.*?(\d+)/(\d+)',       # "TOTAL: 11/12"
            r'SCORE.*?(\d+)/(\d+)',       # "SCORE: 11/12"
            r'(\d+)\s*out\s*of\s*(\d+)',  # "11 out of 15"
        ]
        
        for pattern in score_patterns:
            matches = re.findall(pattern, audit_text, re.IGNORECASE)
            if matches:
                match = matches[-1]  # Get last match
                if len(match) == 3:  # Full pattern with percentage
                    return f"{match[0]}/{match[1]} ({match[2]}%)"
                elif len(match) == 2:
                    try:
                        num, den = int(match[0]), int(match[1])
                        pct = round((num/den) * 100)
                        return f"{num}/{den} ({pct}%)"
                    except (ValueError, ZeroDivisionError):
                        return f"{match[0]}/{match[1]}"
        
        # If we found PASS/FAIL counts, use them
        if pass_count > 0 or fail_count > 0:
            total = pass_count + fail_count
            pct = round((pass_count/total) * 100) if total > 0 else 0
            
            # Debug info - shows question count if different from total
            debug_info = f" (Found {question_count} questions)" if question_count != total else ""
            
            return f"{pass_count}/{total} ({pct}%){debug_info}"
        
        return "Score not available"
