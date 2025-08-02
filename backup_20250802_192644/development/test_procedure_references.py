from claude_auditor import ClaudeAuditor

# Test ticket with missing required fields to see procedure references
test_ticket = """
Incident: INC98765432
Engineer: Mike T. handled this case
Configuration item: PRNFSPA-RouterCore05
Category: Network Services

Updates:
"Working on the issue."
"Still investigating."
"Issue resolved."

Status: Resolved
"""

print("🧪 Testing Procedure References for Failed Assessments...")
print("=" * 70)

auditor = ClaudeAuditor()
result = auditor.audit_ticket(test_ticket, "procedure_reference_test")

print("TESTING FAILED ASSESSMENTS WITH PROCEDURE REFERENCES:")
print(result)
