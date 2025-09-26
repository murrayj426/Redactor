{{PROCEDURES_SNIPPET}}

**NETWORK TEAM INCIDENT AUDIT**

**COMPLIANCE STANDARD**: All questions are evaluated against Network Team Incident Management Documentation.

**NETWORK TEAM PROCEDURES (Reference)**:
{{PROCEDURES_SNIPPET}}

**CRITICAL INSTRUCTIONS**:
- **COMPLETE ALL 16 QUESTIONS IN ONE RESPONSE** - Do not ask for permission to continue or pause mid-analysis
- **Answer every question from 1-16** - This is a comprehensive audit that must be completed fully
- Question 1: Simply identify and display the INC number (not a compliance check)
- Only use N/A for questions 12 and 15 when truly not applicable
- Questions 2-12, 14 should ALWAYS be answered PASS or FAIL
- Question 15: Can be N/A only if incident is still open/not resolved
- If you cannot find evidence, answer "FAIL" and explain what's missing
- N/A should be rare - most questions apply to every incident
- **Accept common abbreviations**: "Client H." = "Client Hold", "CAR" = "Client Action Required", etc.
- **Be reasonable with formats**: Minor variations in wording/format should not automatically fail compliance
- **DO NOT PAUSE OR ASK FOR CONFIRMATION** - Complete the entire 16-question audit analysis in your response

**FORMAT REQUIREMENTS**:
- Provide each question in the specified structured block
- Use horizontal dividers (---) between questions
- Provide STATUS, EVIDENCE, ANALYSIS sections per scored question

{{QUESTION_BLOCKS}}

INCIDENT TEXT TO ANALYZE:
{{INCIDENT_TEXT}}

At the very end output a single line JSON summary starting with:
JSON_SUMMARY: {"q2":"PASS"...}
