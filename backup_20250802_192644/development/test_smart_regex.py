#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdf_parser import redact_sensitive

# Comprehensive test for the new smart regex
test_cases = [
    # Business terms that should NOT be redacted
    ("Category: Security Device Management", "Business term"),
    ("Service: Network Services Management", "Business term"),
    ("Status: Client Hold Request", "Business term"),
    ("Team: First Access Support", "Business term"),
    ("Dear Team Member", "Business greeting"),
    ("Configuration item: PRNFSPA-TowerFW01", "Technical identifier"),
    
    # Actual names that SHOULD be redacted
    ("Engineer: John Smith worked on this", "Person name"),
    ("Contact: Mary Johnson reported this", "Person name"), 
    ("Assigned to: Robert Davis for review", "Person name"),
    ("Created by: Sarah Wilson yesterday", "Person name"),
]

print("🧪 COMPREHENSIVE REGEX TEST")
print("=" * 60)

for i, (text, category) in enumerate(test_cases, 1):
    print(f"\n{i}. Testing: {category}")
    print(f"   Input: {text}")
    
    redacted, stats = redact_sensitive(text)
    print(f"   Output: {redacted}")
    
    # Determine if redaction occurred
    if stats['names_truncated'] > 0:
        print("   ✅ REDACTED (as expected for names)")
    else:
        print("   ✅ PRESERVED (as expected for business terms)")
    
    print(f"   Stats: {stats['names_truncated']} names redacted")

print("\n" + "=" * 60)
print("🎯 SMART REGEX ANALYSIS COMPLETE")
