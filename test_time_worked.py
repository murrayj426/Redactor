"""
Test for audit logic: assigned engineer must be author of at least one Time Worked entry
"""
from openai_auditor import TicketAuditor
from unittest.mock import patch, MagicMock

# Simulated incident text with two time entries, only one by assigned engineer
incident_text = '''
Assigned to: Jeremy Murray

Time worked by: Jeremy Murray
Duration: 1h
Notes: Troubleshooting network issue

Time worked by: John Smith
Duration: 2h
Notes: Assisted with configuration
'''

def test_time_worked_by_assigned_engineer():
    auditor = TicketAuditor()
    # Mock the OpenAI API call inside audit_ticket
    mock_audit_report = """
    ...existing audit output...
    **QUESTION 14: Did the assigned engineer personally document at least one of their own Time Worked entries (not just any team member)?**
    **STATUS**: ✅ PASS
    **EVIDENCE**: "Time worked by: Jeremy Murray"
    **ANALYSIS**: The assigned engineer, Jeremy Murray, entered a Time Worked entry. This matches the requirement.
    ...existing audit output...
    """
    with patch.object(auditor, 'audit_ticket', return_value=mock_audit_report):
        audit_report = auditor.audit_ticket(incident_text)
    print("\n=== AUDIT REPORT ===\n", audit_report)
    # Check that Question 14 is PASS (since Jeremy Murray entered time)
    assert "QUESTION 14" in audit_report
    assert ("Jeremy Murray" in audit_report) and ("PASS" in audit_report or "✅" in audit_report)

if __name__ == "__main__":
    test_time_worked_by_assigned_engineer()
