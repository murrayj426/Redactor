import sys
import argparse
from pdf_parser import extract_text_from_pdf, run_redactor_gui
from openai_auditor import TicketAuditor

def redact_pdf_to_text(file_path):
    redacted_text, redaction_stats = extract_text_from_pdf(file_path)
    
    with open("reports/redacted_output.txt", "w") as f:
        f.write("=== REDACTION SUMMARY ===\n")
        f.write(f"Total Redactions: {redaction_stats['total_redactions']}\n")
        f.write(f"Names Truncated: {redaction_stats['names_truncated']}\n")
        f.write(f"IP Addresses: {redaction_stats['ip_addresses']}\n")
        f.write(f"Email Addresses: {redaction_stats['email_addresses']}\n")
        f.write(f"Phone Numbers: {redaction_stats['phone_numbers']}\n")
        f.write(f"URLs: {redaction_stats['urls']}\n")
        f.write(f"MAC Addresses: {redaction_stats['mac_addresses']}\n")
        f.write(f"Employee IDs: {redaction_stats['employee_ids']}\n")
        f.write(f"Account Numbers: {redaction_stats['account_numbers']}\n")
        f.write(f"IMEI Numbers: {redaction_stats['imei_numbers']}\n")
        f.write("="*50 + "\n\n")
        f.write(redacted_text)
    
    print(f"\n🔒 REDACTION SUMMARY:")
    print(f"Total Redactions: {redaction_stats['total_redactions']}")
    print(f"Names Truncated: {redaction_stats['names_truncated']}")
    print(f"IP Addresses: {redaction_stats['ip_addresses']}")
    print(f"Email Addresses: {redaction_stats['email_addresses']}")
    print(f"Phone Numbers: {redaction_stats['phone_numbers']}")
    print(f"URLs: {redaction_stats['urls']}")
    print(f"Other: {redaction_stats['mac_addresses'] + redaction_stats['employee_ids'] + redaction_stats['account_numbers'] + redaction_stats['imei_numbers']}")
    print("\nRedacted PDF text saved to: reports/redacted_output.txt")
    
    return redacted_text

def audit_pdf(file_path, audit_type="general", model="gpt-4"):
    """Redact PDF and run AI audit"""
    print(f"Processing {file_path}...")
    
    # Redact the PDF
    redacted_text = redact_pdf_to_text(file_path)
    
    # Run AI audit
    print(f"Running {audit_type} audit with {model}...")
    auditor = TicketAuditor()
    audit_result = auditor.audit_ticket(redacted_text, audit_type, model)
    
    # Save audit report
    report_file = auditor.save_audit_report(audit_result, f"{audit_type}_audit")
    
    print(f"\n✅ Audit complete!")
    print(f"📄 Redacted text: reports/redacted_output.txt")
    print(f"📊 Audit report: {report_file}")
    
    return audit_result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF Redactor and AI Auditor")
    parser.add_argument("pdf_path", nargs="?", help="Path to PDF file")
    parser.add_argument("--audit", action="store_true", help="Run AI audit after redaction")
    parser.add_argument("--audit-type", choices=["general", "security", "performance"], 
                       default="general", help="Type of audit to perform")
    parser.add_argument("--model", default="gpt-4", help="OpenAI model to use")
    parser.add_argument("--gui", action="store_true", help="Launch GUI")
    
    args = parser.parse_args()
    
    if args.gui or not args.pdf_path:
        run_redactor_gui()
    elif args.audit:
        audit_pdf(args.pdf_path, args.audit_type, args.model)
    else:
        redact_pdf_to_text(args.pdf_path)
