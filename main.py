import sys
from pdf_parser import extract_text_from_pdf, run_redactor_gui

def redact_pdf_to_text(file_path):
    text = extract_text_from_pdf(file_path)
    with open("reports/redacted_output.txt", "w") as f:
        f.write(text)
    print("\nRedacted PDF text saved to: reports/redacted_output.txt")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        redact_pdf_to_text(pdf_path)
    else:
        run_redactor_gui()
