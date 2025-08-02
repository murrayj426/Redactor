from pdf_parser import redact_sensitive

# Test text with hostname that was getting truncated
test_text = """
Configuration item: PRNFSPA-TowerFW01
Location: PR-Niagara F. Tower
Service Offering: Network Services
Category: Security Device Management
First Access: true
Dear Team, I am taking ownership
"""

print("🧪 Testing hostname preservation...")
print("=" * 50)

redacted_text, stats = redact_sensitive(test_text)

print("ORIGINAL:")
print(test_text)
print("\nREDACTED:")
print(redacted_text)

if "PRNFSPA-TowerFW01" in redacted_text:
    print("✅ SUCCESS: Hostname 'PRNFSPA-TowerFW01' was preserved!")
else:
    print("❌ PROBLEM: Hostname was truncated")
