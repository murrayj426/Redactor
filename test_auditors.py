#!/usr/bin/env python3
"""
Test script for both OpenAI and Claude auditors
"""

import sys
import os

def test_openai_auditor():
    """Test OpenAI auditor if OpenAI key is available"""
    try:
        from openai_auditor import TicketAuditor
        from dotenv import load_dotenv
        
        load_dotenv()
        
        if not os.getenv('OPENAI_API_KEY'):
            print("❌ OpenAI API key not found")
            return False
        
        print("🔥 Testing OpenAI Auditor...")
        auditor = TicketAuditor()
        
        with open('test_incident.txt', 'r') as f:
            ticket_text = f.read()
        
        result = auditor.audit_ticket(ticket_text, model="gpt-4o-mini")
        print("✅ OpenAI Auditor working!")
        print("📊 Sample result:", result[:200] + "..." if len(result) > 200 else result)
        return True
        
    except Exception as e:
        print(f"❌ OpenAI Auditor failed: {e}")
        return False

def test_claude_auditor():
    """Test Claude auditor if Claude key is available"""
    try:
        from claude_auditor import ClaudeAuditor
        from dotenv import load_dotenv
        
        load_dotenv()
        
        if not os.getenv('ANTHROPIC_API_KEY'):
            print("❌ Claude API key not found")
            return False
        
        print("🧠 Testing Claude Auditor...")
        auditor = ClaudeAuditor()
        
        with open('test_incident.txt', 'r') as f:
            ticket_text = f.read()
        
        result = auditor.audit_ticket(ticket_text)
        print("✅ Claude Auditor working!")
        print("📊 Sample result:", result[:200] + "..." if len(result) > 200 else result)
        return True
        
    except Exception as e:
        print(f"❌ Claude Auditor failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Redactor Auditors...")
    print("=" * 50)
    
    # Test both auditors
    openai_works = test_openai_auditor()
    print()
    claude_works = test_claude_auditor()
    
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print(f"OpenAI Auditor: {'✅ Working' if openai_works else '❌ Failed'}")
    print(f"Claude Auditor: {'✅ Working' if claude_works else '❌ Failed'}")
    
    if openai_works or claude_works:
        print("\n🎉 At least one auditor is working! Your app is ready to go.")
    else:
        print("\n⚠️ Neither auditor working. Check your API keys in .env file.")
