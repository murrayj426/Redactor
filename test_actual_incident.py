#!/usr/bin/env python3

from pdf_parser import redact_sensitive

# Test with actual problematic text from your incident
test_text = """
Report T.: Incident Details
Company: Delaware North Companies, Inc. Opened by: Delaware North Integration User
Caller: Caleb F. Contact type: Ticket Integration
Service offering: Event date:
Configuration item: GEWIGGAFW01 First Access: true
CI Not A.: false Service Offering: Network Services
Configuration item: Category: Network Management and Monitoring
Location: Wheeling D. - Gaming Subcategory:
Impact: 1 - High R. party: Presidio
Assignment group: MSC Network Engineer
Customer Assignment Group: undefined Assigned to: Kaushal S.
Run B. : Jeremy M. 08-03-2025 09:29:30 Eastern Daylight Time
"""

print("Testing with actual incident text...")
redacted, stats = redact_sensitive(test_text)
print("\n" + "="*50)
print("ORIGINAL:")
print("="*50)
print(test_text)
print("\n" + "="*50)
print("REDACTED:")
print("="*50)
print(redacted)
print("\n" + "="*50)
print("CHANGES MADE:")
print("="*50)
lines_orig = test_text.strip().split('\n')
lines_redacted = redacted.strip().split('\n')
for i, (orig, red) in enumerate(zip(lines_orig, lines_redacted)):
    if orig != red:
        print(f"Line {i+1}:")
        print(f"  BEFORE: {orig}")
        print(f"  AFTER:  {red}")
        print()
