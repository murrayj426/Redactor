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
- Only use N/A for questions 12 and 15 when truly not applicable
- Questions 2-12, 14 should ALWAYS be answered PASS or FAIL
- Question 15: Can be N/A only if incident is still open/not resolved
- If you cannot find evidence, answer "FAIL" and explain what's missing
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
- **Questions 2-16**: For EACH question provide:

---

**QUESTION [NUMBER]: [REPEAT THE FULL QUESTION TEXT]**

**STATUS**: ✅ PASS or ❌ FAIL (or ⚠️ N/A only for questions 12 & 15 when appropriate)

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

**13. Activity & Change Task Deficiencies**
**Question**: Document any deficiencies found in Activity & Change task management
**Answer Required**: Text response (not scored - documentation only)
**Network Team Standard**: Provide detailed explanation of any task management issues identified

**14. Time Tracking Accuracy**
**Question**: Did the engineer accurately document their Time Worked entries?
**Answer Required**: ✅ PASS / ❌ FAIL (N/A not allowed)
**Network Team Standard**: Time Worked field must be populated accurately for cost evaluation

**15. Resolution Documentation**
**Question**: Do the 'Close Notes' accurately reflect the work that was done and provide evidence of resolution?
**Answer Required**: ✅ PASS / ❌ FAIL / ⚠️ N/A (N/A only if incident is still open/not resolved)
**Network Team Standard**: Close notes should include issue summary, steps taken, and resolution evidence

**16. Audit Notes**
**Question**: Share your thoughts on the overall performance of the audited engineer for this incident
**Answer Required**: Text response (not scored - documentation only)
**Network Team Standard**: Provide constructive feedback and identify areas for improvement or recognition

---

**SCORING RULES:**
- Question 1: Display INC number (not scored)
- Questions 2-12: MUST use ✅ PASS or ❌ FAIL based on Network Team standards (11 questions)
- Question 13: Text response only (not scored - documentation)
- Question 14: ✅ PASS / ❌ FAIL (Time Worked accuracy)
- Question 15: ✅ PASS / ❌ FAIL / ⚠️ N/A (Close Notes - N/A only if incident still open)
- Question 16: Text response only (not scored - audit notes)
- If evidence is missing, use ❌ FAIL and explain what should be there per Network Team procedures
- **Total scoreable questions: 13 maximum (Q2-12, Q14, Q15)**

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
            f.write(f"=== INCIDENT AUDIT REPORT (16-QUESTION FRAMEWORK) ===\n")
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
            # Count PASS/FAIL responses only - no more 1-10 scoring
            lines = audit_result.split('\n')
            pass_count = 0
            fail_count = 0
            na_count = 0
            
            for line in lines:
                if '⚠️' in line and 'N/A' in line:
                    # Check if this is Q12 (Task Management) or Q15 (Close Notes) - the only questions that can be N/A
                    if any(q in line for q in ['12', '15', 'Task Management', 'Close Notes', 'Resolution Documentation']):
                        na_count += 1
                elif '✅' in line and 'PASS' in line:
                    pass_count += 1
                elif '❌' in line and 'FAIL' in line:
                    fail_count += 1
            
            # Based on actual audit form: Q2-12 (11 questions), Q14, Q15 (2 questions) = 13 total scoreable
            # Q1, Q13, Q16 are not scored (identification/text fields)
            total_scoreable = 13  # Questions 2-12, 14, 15
            total_applicable = total_scoreable - na_count
            total_answered = pass_count + fail_count
            
            return {
                'pass_count': pass_count,
                'fail_count': fail_count,
                'total_answered': total_answered,
                'total_questions': 16,  # Total framework questions
                'scoreable_questions': total_scoreable,  # Questions 2-12, 14, 15
                'applicable_questions': total_applicable,  # Scoreable minus N/A
                'na_responses': na_count,
                'compliance_percentage': (pass_count / total_answered * 100) if total_answered > 0 else None
            }
        except:
            return None

    def extract_audit_score_from_text(self, audit_text):
        """Enhanced audit score extraction with PASS/FAIL counting and debug information"""
        import re
        
        # Patterns for modern audit format with emojis
        pass_patterns = [
            r'✅\s*PASS\s*\(Score:\s*(\d+)/(\d+)\)',  # "✅ PASS (Score: 9/10)"
            r'✅\s*PASS',
            r'STATUS.*?✅.*?PASS', 
            r'PASS.*?✅',
            r'✅.*?PASS'
        ]
        
        fail_patterns = [
            r'❌\s*FAIL\s*\(Score:\s*(\d+)/(\d+)\)',  # "❌ FAIL (Score: 2/10)"
            r'❌\s*FAIL',
            r'STATUS.*?❌.*?FAIL',
            r'FAIL.*?❌', 
            r'❌.*?FAIL'
        ]
        
        pass_count = 0
        fail_count = 0
        extracted_scores = []
        
        # Try multiple patterns to catch all variations
        for pattern in pass_patterns:
            matches = re.findall(pattern, audit_text, re.IGNORECASE | re.DOTALL)
            if matches:
                if isinstance(matches[0], tuple) and len(matches[0]) == 2:
                    # Pattern captured score (numerator, denominator)
                    for match in matches:
                        extracted_scores.append((int(match[0]), int(match[1])))
                    pass_count = len(matches)
                else:
                    # Simple PASS pattern
                    pass_count = max(pass_count, len(matches))
        
        for pattern in fail_patterns:
            matches = re.findall(pattern, audit_text, re.IGNORECASE | re.DOTALL)
            if matches:
                if isinstance(matches[0], tuple) and len(matches[0]) == 2:
                    # Pattern captured score (numerator, denominator)
                    for match in matches:
                        extracted_scores.append((int(match[0]), int(match[1])))
                    fail_count = len(matches)
                else:
                    # Simple FAIL pattern
                    fail_count = max(fail_count, len(matches))
        
        # Count total questions for verification (should be 16 total, Q2-12,14,15 are scored)
        question_count = len(re.findall(r'\*\*QUESTION\s+\d+', audit_text, re.IGNORECASE))
        
        # If we found PASS/FAIL counts, use them (this is the primary scoring method)
        if pass_count > 0 or fail_count > 0:
            total = pass_count + fail_count
            pct = round((pass_count/total) * 100) if total > 0 else 0
            
            # Note: Based on actual audit form structure:
            # Q1: INC# (not scored), Q2-12: Yes/No (11 questions), Q13: Text field (not scored)
            # Q14: Yes/No/N/A, Q15: Yes/No/N/A, Q16: Audit notes (not scored)  
            # Total scoreable: Q2-12, Q14, Q15 = 13 questions maximum
            max_scoreable = 13  # Questions 2-12, 14, 15
            
            if total == max_scoreable:
                debug_info = ""  # Clean display for full audit
            else:
                debug_info = f" ({total}/13)"
            
            return f"{pass_count}/{total} ({pct}%){debug_info}"
        
        # If we extracted individual scores from PASS/FAIL patterns, use them
        if extracted_scores:
            # Sum up all individual scores
            total_score = sum(score[0] for score in extracted_scores)
            total_possible = sum(score[1] for score in extracted_scores)
            pct = round((total_score/total_possible) * 100) if total_possible > 0 else 0
            return f"{total_score}/{total_possible} ({pct}%)"
        
        # Look for traditional score patterns as fallback
        score_patterns = [
            r'(\d+)/(\d+)\s*\((\d+)%\)',  # "11/12 (92%)"
            r'\(Score:\s*(\d+)/(\d+)\)',   # "(Score: 9/10)"
            r'Score:\s*(\d+)/(\d+)',      # "Score: 9/10"
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
        
        return "Score not available"
