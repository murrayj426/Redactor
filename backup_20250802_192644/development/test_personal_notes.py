from claude_auditor import ClaudeAuditor

# Sample ticket text to test personal audit notes
sample_ticket = """
Incident: INC12345678
Engineer: Sarah M. worked on this case
Configuration item: PRNFSPA-TowerFW01
Category: Security Device Management
Status: Resolved

Updates:
"Dear Team,
I am taking ownership of this case and will review the configuration.
Best regards,
Sarah M."

Resolution:
"Issue resolved by replacing faulty component. Customer notified."
Time worked: 2 hours
"""

print("🧪 Testing Personal Audit Notes...")
print("=" * 60)

auditor = ClaudeAuditor()
result = auditor.audit_ticket(sample_ticket, "personal_feedback")

print("SAMPLE PERSONAL AUDIT NOTES:")
print(result)
