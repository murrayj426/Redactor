#!/usr/bin/env python3

from pdf_parser import redact_sensitive

# Test with business terms that should be preserved AND personal names that should be redacted
test_text = """
Report T.: Incident Details
Company: Delaware North Companies, Inc. 
Caller: John Smith (should be redacted)
Contact E.: john.smith@example.com
Location: Wheeling Downs - Gaming
Service Offering: Network Services
Configuration item: GEWIGGAFW01 
Category: Security Device Management (should be preserved)
Location: Wheeling Downs - Gaming (should be preserved)
Assignment group: MSC Network Engineer
Assigned to: Kaushal Singh (should be redacted)
Resolved by: Delaware North Integration User (should be preserved)
Updated by: Sarah Johnson (should be redacted)
Eastern Daylight Time (should be preserved)
Network Management and Monitoring (should be preserved)
Run By: Jeremy Murray 08-03-2025 09:29:30 Eastern Daylight Time
IP Address: 192.168.1.100
Phone: 555-123-4567
Case #6-555-123-4567 (should not be redacted - it's a case number)
"""

print("Testing comprehensive redaction patterns...")
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
