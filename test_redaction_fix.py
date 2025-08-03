#!/usr/bin/env python3

from pdf_parser import redact_sensitive

# Test with some problematic text from your sample
test_text = """
Report T.: Incident Details
Company: Delaware North Companies, Inc. 
Caller: Caleb F. 
Location: Wheeling D. - Gaming
Service Offering: Network Services
Configuration item: GEWIGGAFW01 
Category: Network Management and Monitoring
CI Not A.: false Service Offering: Network Services
Configuration item: Category: Security D. Management
Location: Wheeling Downs - Gaming
Impact: 1 - High R. party: Presidio
Assignment group: MSC Network Engineer
Assigned to: Kaushal S.
Additional assignee list:
Jeremy M. worked on this ticket
Eastern Daylight Time
Run By: Jeremy M. 08-03-2025 09:29:30 Eastern Daylight Time
"""

print("Testing redaction patterns...")
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
print("REDACTION STATS:")
print("="*50)
for key, value in stats.items():
    print(f"{key}: {value}")
