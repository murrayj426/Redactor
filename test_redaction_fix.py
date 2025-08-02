from pdf_parser import redact_sensitive

# Test text with business terms that should NOT be redacted
test_text = """
Configuration item: PRNFSPA-TowerFW01
Location: PR-Niagara F. Tower
Service Offering: Network Services
Category: Security Device Management
Pending reason: Client Hold

Engineer: John Smith worked on this case.
Customer: Mary Johnson reported the issue.
"""

print("🧪 Testing redaction with business terms...")
print("=" * 50)

redacted_text, stats = redact_sensitive(test_text)

print("ORIGINAL:")
print(test_text)
print("\nREDACTED:")
print(redacted_text)
print(f"\nSTATISTICS:")
print(f"Names truncated: {stats['names_truncated']}")
print(f"Total redactions: {stats['total_redactions']}")

# Check if business terms were preserved
if "Device Management" in redacted_text:
    print("\n✅ SUCCESS: 'Device Management' was preserved!")
else:
    print("\n❌ PROBLEM: 'Device Management' was redacted")

if "Client Hold" in redacted_text:
    print("✅ SUCCESS: 'Client Hold' was preserved!")
else:
    print("❌ PROBLEM: 'Client Hold' was redacted")
