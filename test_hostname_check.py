from pdf_parser import redact_sensitive

# Test specifically for hostname preservation
test_text = """
Configuration item: PRNFSPA-TowerFW01
Device: PRNFSPA-ServerDB02
Network: PRNFSPA-RouterCore01
Firewall: PRNFSPA-FirewallEdge03
Location: PR-Niagara F. Tower

Engineer: John Smith worked on this case.
"""

print("🧪 Testing hostname preservation...")
print("=" * 50)

redacted_text, stats = redact_sensitive(test_text)

print("ORIGINAL:")
print(test_text)
print("\nREDACTED:")
print(redacted_text)

# Check hostname preservation
hostnames = ["PRNFSPA-TowerFW01", "PRNFSPA-ServerDB02", "PRNFSPA-RouterCore01", "PRNFSPA-FirewallEdge03"]

print("\n🔍 HOSTNAME CHECK:")
for hostname in hostnames:
    if hostname in redacted_text:
        print(f"✅ {hostname} - PRESERVED")
    else:
        print(f"❌ {hostname} - REDACTED")
