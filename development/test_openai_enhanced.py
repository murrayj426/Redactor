from openai_auditor import TicketAuditor

# Test OpenAI auditor with same functionality as Claude
test_ticket = """
Incident: INC99887766
Engineer: Sarah T. handled this case
Configuration item: PRNFSPA-ServerDB05
Category: Network Services
Status: Resolved

Updates:
"Working on the issue."
"Issue resolved."
"""

print("🧪 Testing OpenAI Auditor with Enhanced Features...")
print("=" * 70)

# Check if OpenAI API key is available
import os
from dotenv import load_dotenv
load_dotenv()

if not os.getenv('OPENAI_API_KEY'):
    print("⚠️  OpenAI API key not found. Please add OPENAI_API_KEY to your .env file to test.")
    print("The functionality has been added and will work when the API key is available.")
else:
    auditor = TicketAuditor()
    result = auditor.audit_ticket(test_ticket)  # Use default model
    print("OPENAI ENHANCED AUDIT RESULT:")
    print(result)
