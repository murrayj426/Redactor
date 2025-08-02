"""
Test script to compare OpenAI vs Claude audit results
Run this with: python test_claude_comparison.py
"""

import os
from dotenv import load_dotenv
from openai_auditor import TicketAuditor
from claude_auditor import ClaudeAuditor

load_dotenv()

# Sample incident text for testing
sample_incident = """
ServiceNow INC11814999

Configuration item: PRNFSPA-TowerFW01
Location: PR-Niagara F. Tower  
Service Offering: Network Services
Category: Security D. Management
Priority: 3 - Moderate
First Access: true

Description: Alert for resource offline

Engineer: Kaushal S.
Time worked: 2 Hours 48 Minutes

Notes:
I am taking ownership of this case. I will review the ticket and update you shortly.

Dear Team, Kindly find below observations:
Issue description: Alert for resource offline
Device uptime is more than 2 hours
Cellular flap was observed

Current status: The RMA request has been raised: #6-555-0199
Next steps: Follow up is to be taken on the shipment process with the RMA team.

Pending reason: Client Hold
Follow up by: 3 days

Activity Task ACT3606715 created.
"""

def test_openai():
    print("🤖 Testing OpenAI GPT-4o-mini...")
    try:
        auditor = TicketAuditor()
        result = auditor.audit_ticket(sample_incident, model="gpt-4o-mini")
        return result
    except Exception as e:
        return f"OpenAI Error: {e}"

def test_claude():
    print("🧠 Testing Claude 3.5 Sonnet...")
    try:
        auditor = ClaudeAuditor()
        result = auditor.audit_ticket(sample_incident, model="claude-3-5-sonnet-20241022")
        return result
    except Exception as e:
        return f"Claude Error: {e}"

def main():
    print("=" * 80)
    print("🔍 COMPLIANCE AUDITING COMPARISON")
    print("OpenAI GPT-4o-mini vs Claude 3.5 Sonnet")
    print("=" * 80)
    
    # Check API keys
    openai_key = os.getenv('OPENAI_API_KEY')
    claude_key = os.getenv('ANTHROPIC_API_KEY')
    
    print(f"OpenAI API Key: {'✅ Found' if openai_key else '❌ Missing'}")
    print(f"Claude API Key: {'✅ Found' if claude_key and claude_key != 'your_anthropic_api_key_here' else '❌ Missing'}")
    print()
    
    if openai_key:
        openai_result = test_openai()
        print("📊 OPENAI AUDIT RESULTS:")
        print("-" * 50)
        print(openai_result[:1000] + "..." if len(openai_result) > 1000 else openai_result)
        print()
    
    if claude_key and claude_key != 'your_anthropic_api_key_here':
        claude_result = test_claude()
        print("📊 CLAUDE AUDIT RESULTS:")
        print("-" * 50)
        print(claude_result[:1000] + "..." if len(claude_result) > 1000 else claude_result)
        print()
    else:
        print("❌ Claude API key not configured. Add your key to .env file:")
        print("ANTHROPIC_API_KEY=your_actual_key_here")

if __name__ == "__main__":
    main()
