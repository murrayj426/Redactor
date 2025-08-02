from pdf_parser import redact_sensitive

# Test text with the specific truncations observed
test_text = """
First Access: true
Dear Team, Kindly find below observations
State: Pending Client
Pending reason: Client Hold
Category: Security Device Management
Service Offering: Network Services
Configuration item: PRNFSPA-TowerFW01
"""

print("🔍 Testing for specific truncation issues...")
print("=" * 60)

redacted_text, stats = redact_sensitive(test_text)

print("ORIGINAL:")
print(test_text)
print("\nREDACTED:")
print(redacted_text)

# Check for problematic truncations
issues = []

if "First A.:" in redacted_text:
    issues.append("❌ 'First Access' was truncated to 'First A.:'")
elif "First Access:" in redacted_text:
    print("✅ 'First Access:' preserved correctly")

if "Dear T.," in redacted_text:
    issues.append("❌ 'Dear Team' was truncated to 'Dear T.,'")
elif "Dear Team," in redacted_text:
    print("✅ 'Dear Team,' preserved correctly")

if "Pending C." in redacted_text:
    issues.append("❌ 'Pending Client' was truncated to 'Pending C.'")
elif "Pending Client" in redacted_text:
    print("✅ 'Pending Client' preserved correctly")

if issues:
    print("\n🚨 TRUNCATION ISSUES FOUND:")
    for issue in issues:
        print(issue)
else:
    print("\n🎉 NO TRUNCATION ISSUES - ALL BUSINESS TERMS PRESERVED!")
