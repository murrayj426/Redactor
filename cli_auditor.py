#!/usr/bin/env python3
"""
Command-line Interactive Auditor
Quick way to test the interactive audit system
"""

import sys
import os
from pdf_parser import extract_text_from_pdf, redact_pii
from interactive_auditor import InteractiveAuditor

def main():
    print("🤖 Interactive AI Auditor - Command Line")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage: python cli_auditor.py <pdf_file>")
        print("Example: python cli_auditor.py incident_123.pdf")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    
    if not os.path.exists(pdf_file):
        print(f"❌ Error: File '{pdf_file}' not found")
        sys.exit(1)
    
    print(f"📄 Processing: {pdf_file}")
    print("⏳ Extracting and redacting text...")
    
    try:
        # Extract and redact text
        text = extract_text_from_pdf(pdf_file)
        redacted = redact_pii(text)
        
        print(f"✅ Processed {len(text):,} characters")
        print(f"📝 Redacted to {len(redacted):,} characters")
        
        # Start interactive audit
        auditor = InteractiveAuditor()
        
        print("\n🔍 PERFORMING COMPREHENSIVE AUDIT")
        print("=" * 50)
        
        initial_audit = auditor.perform_initial_audit(redacted)
        print(initial_audit)
        
        print("\n💬 INTERACTIVE DISCUSSION MODE")
        print("=" * 50)
        print("Commands:")
        print("  • Ask any question about the audit")
        print("  • 'suggestions' - Get suggested follow-up questions")
        print("  • 'export' - Save conversation to file")
        print("  • 'quit' - Exit")
        print()
        
        while True:
            try:
                user_input = input("🤔 Your question: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                elif user_input.lower() == 'export':
                    filename = auditor.export_conversation()
                    print(f"💾 Conversation saved to: {filename}")
                    continue
                
                elif user_input.lower() in ['suggestions', 'suggest', 'help']:
                    print("\n💡 Suggested Questions:")
                    suggestions = auditor.get_suggested_questions()
                    for i, suggestion in enumerate(suggestions[:5], 1):
                        if suggestion.strip():
                            print(f"   {i}. {suggestion.strip()}")
                    print()
                    continue
                
                elif not user_input:
                    continue
                
                print("\n🤖 AI Auditor Response:")
                print("-" * 30)
                response = auditor.continue_conversation(user_input)
                print(response)
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
    
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
