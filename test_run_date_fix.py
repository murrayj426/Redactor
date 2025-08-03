#!/usr/bin/env python3

from pdf_parser import redact_sensitive

def test_specific_terms():
    """Test the specific terms that were being over-redacted"""
    
    test_cases = [
        # Test case, expected result
        ("Run Date and Time: 08-03-2025 09:29:30 Eastern Daylight Time", "Run Date and Time: 08-03-2025 09:29:30 Eastern Daylight Time"),
        ("Run By: Jeremy Murray", "Run By: Jeremy M."),  # Names should still be redacted
        ("Opened by: Delaware North Integration User", "Opened by: Delaware North Integration User"),
        ("Caller: Caleb Franklin", "Caller: Caleb F."),  # Names should be redacted
        ("Assigned to: Kaushal Smith", "Assigned to: Kaushal S."),  # Names should be redacted
        ("Contact Type: Ticket Integration", "Contact Type: Ticket Integration"),
        ("Business Service: Network Services", "Business Service: Network Services"),
        ("Service Offering: Network Management and Monitoring", "Service Offering: Network Management and Monitoring"),
        ("Configuration Item: GEWIGGAFW01", "Configuration Item: GEWIGGAFW01"),
        ("Assignment Group: MSC Network Engineer", "Assignment Group: MSC Network Engineer"),
        ("Responsible Party: Presidio", "Responsible Party: Presidio"),
        ("Short Description: Wheeling itrak and Everi floor monitor were unavailable", "Short Description: Wheeling itrak and Everi floor monitor were unavailable"),
        ("Current Status: Resolved", "Current Status: Resolved"),
        ("Next Steps: Investigation continues", "Next Steps: Investigation continues"),
        ("Work Notes: Additional information provided", "Work Notes: Additional information provided"),
        ("Time Worked: 10 Minutes", "Time Worked: 10 Minutes"),
        ("Customer Ticket #: INC0444083", "Customer Ticket #: INC0444083"),
        ("Additional Comments: System restored", "Additional Comments: System restored"),
        ("Primary Agreement: Standard SLA", "Primary Agreement: Standard SLA")
    ]
    
    print("Testing specific redaction cases...")
    print("=" * 60)
    
    failed_tests = []
    
    for i, (test_input, expected) in enumerate(test_cases, 1):
        result, _ = redact_sensitive(test_input)
        
        if result.strip() == expected.strip():
            print(f"✅ Test {i}: PASSED")
            print(f"   Input: {test_input}")
            print(f"   Output: {result}")
        else:
            print(f"❌ Test {i}: FAILED")
            print(f"   Input: {test_input}")
            print(f"   Expected: {expected}")
            print(f"   Got: {result}")
            failed_tests.append(i)
        print()
    
    print("=" * 60)
    if failed_tests:
        print(f"❌ {len(failed_tests)} test(s) failed: {failed_tests}")
        return False
    else:
        print("✅ All tests passed!")
        return True

if __name__ == "__main__":
    success = test_specific_terms()
    exit(0 if success else 1)
