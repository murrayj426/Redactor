from claude_auditor import ClaudeAuditor

# Test ticket with multiple issues to see personal explanations
test_ticket = """
Incident: INC11223344
Engineer: Alex R. worked on this case
Configuration item: PRNFSPA-RouterCore10
Category: Network Services
Status: Resolved

Updates:
"Looking into this issue."
"Problem fixed."
"""

print("🧪 Testing Personal Explanations for Failed Assessments...")
print("=" * 70)

auditor = ClaudeAuditor()
result = auditor.audit_ticket(test_ticket, "personal_explanations_test")

print("TESTING PERSONAL EXPLANATIONS FOR EACH MISS:")
print(result)
