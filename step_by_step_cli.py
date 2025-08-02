#!/usr/bin/env python3
"""
Step-by-Step Audit CLI
Command-line interface for interactive step-by-step auditing
"""

import sys
import os
from pdf_parser import extract_text_from_pdf
from step_by_step_auditor import StepByStepAuditor

def print_separator():
    print("=" * 60)

def print_header(text):
    print_separator()
    print(f" {text}")
    print_separator()

def main():
    print_header("🤖 STEP-BY-STEP NETWORK TEAM AUDIT")
    
    if len(sys.argv) < 2:
        print("Usage: python step_by_step_cli.py <pdf_file>")
        print("Example: python step_by_step_cli.py incident_123.pdf")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    
    if not os.path.exists(pdf_file):
        print(f"❌ Error: File '{pdf_file}' not found")
        sys.exit(1)
    
    print(f"📄 Processing: {pdf_file}")
    print("⏳ Extracting and redacting text...")
    
    try:
        # Extract and redact text
        redacted_text = extract_text_from_pdf(pdf_file)
        print(f"✅ Processed {len(redacted_text):,} characters")
        
        # Start step-by-step audit
        auditor = StepByStepAuditor()
        
        print("\n🔍 STARTING STEP-BY-STEP AUDIT")
        print("Commands: 'n' = next, 'p' = previous, 'd' = discuss, 'q' = quit, 'r' = report")
        print_separator()
        
        # Start audit
        response = auditor.start_audit(redacted_text)
        
        while True:
            # Show current question and response
            print(f"\n{auditor.get_progress()}")
            print(f"\n{response}")
            
            if auditor.current_question > 15:
                print("\n✅ AUDIT COMPLETE!")
                print("Use 'r' to generate the final report or 'q' to quit.")
            
            # Get user input
            print("\nOptions:")
            if auditor.current_question > 1:
                print("  p - Previous question")
            if auditor.current_question <= 15:
                print("  n - Next question")
                print("  d - Discuss current question")
            print("  r - Generate final report")
            print("  q - Quit")
            
            choice = input("\nEnter command: ").lower().strip()
            
            if choice == 'q':
                print("👋 Goodbye!")
                break
            
            elif choice == 'n' and auditor.current_question <= 15:
                print("\n⏭️  Moving to next question...")
                response = auditor.next_question()
            
            elif choice == 'p' and auditor.current_question > 1:
                print("\n⏮️  Going back to previous question...")
                response = auditor.previous_question()
            
            elif choice == 'd' and auditor.current_question <= 15:
                discussion = input("\n💬 Enter your question or comment: ")
                if discussion.strip():
                    print("\n🤖 AI Response:")
                    response = auditor.continue_discussion(discussion)
                    print(response)
                    print("\n" + "="*40)
                    response = ""  # Don't repeat the response in next loop
                else:
                    print("No input provided.")
                    response = ""
            
            elif choice == 'r':
                print("\n📊 GENERATING FINAL REPORT...")
                report = auditor.generate_final_report()
                print(report)
                
                save_choice = input("\n💾 Save report to file? (y/n): ").lower().strip()
                if save_choice == 'y':
                    print("Report saved to reports/ directory")
                
                break
            
            else:
                print("❌ Invalid command or not available at this time.")
                response = ""
        
    except KeyboardInterrupt:
        print("\n\n👋 Audit interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
