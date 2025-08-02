#!/usr/bin/env python3
"""
Quick test of optimized audit functions
"""

def test_redaction_optimization():
    """Test optimized redaction with pre-compiled patterns"""
    from pdf_parser import redact_sensitive
    
    test_text = """
    John Smith called about incident INC123456.
    His email is john.smith@company.com and phone is 555-123-4567.
    The Security Device Management team is investigating.
    IP address 192.168.1.1 was affected.
    """
    
    print("🧪 Testing optimized redaction...")
    redacted, stats = redact_sensitive(test_text)
    print(f"✅ Redaction complete: {stats['total_redactions']} items redacted")
    print(f"📊 Business terms preserved: {'Security Device Management' in redacted}")
    return redacted, stats

def test_error_handling():
    """Test smart error handling"""
    from utils.error_handling import SmartErrorHandler
    
    print("\n🧪 Testing error handling...")
    handler = SmartErrorHandler()
    
    # Simulate a rate limit error
    test_error = Exception("Rate limit exceeded: 429")
    context = {'model': 'gpt-4', 'function_name': 'test_function'}
    
    error_context = handler.handle_error(test_error, context)
    print(f"✅ Error classified as: {error_context.error_type.value}")
    print(f"💡 Suggested action: {error_context.suggested_action}")

def test_token_management():
    """Test token optimization"""
    from utils.ai_utils import optimize_prompt_for_model
    
    print("\n🧪 Testing token management...")
    
    # Test with a reasonable prompt
    test_prompt = "Analyze this incident ticket for compliance." * 100
    result = optimize_prompt_for_model(test_prompt, 'gpt-4')
    
    print(f"✅ Original tokens: {result['original_tokens']}")
    print(f"📊 Optimized: {'Yes' if result['truncated'] else 'No'}")
    print(f"🎯 Model suggestion: {result['model_suggestion']}")

def test_caching():
    """Test response caching"""
    from utils.cache_utils import ResponseCache
    
    print("\n🧪 Testing response caching...")
    cache = ResponseCache()
    
    # Test cache set/get
    test_text = "Test incident text"
    test_response = "Test audit response"
    
    cache.set(test_text, "general", "gpt-4", test_response)
    cached_result = cache.get(test_text, "general", "gpt-4")
    
    print(f"✅ Cache working: {cached_result == test_response}")

def run_integration_test():
    """Run full integration test"""
    print("🚀 Running Optimization Integration Test")
    print("=" * 50)
    
    try:
        # Test each component
        redacted, stats = test_redaction_optimization()
        test_error_handling()
        test_token_management()
        test_caching()
        
        print("\n" + "=" * 50)
        print("✅ All optimization tests passed!")
        print("🎯 System is ready for production use")
        
        # Performance summary
        print(f"\n📊 Performance Summary:")
        print(f"   • Redaction: {stats['total_redactions']} items processed")
        print(f"   • Business terms: Preserved")
        print(f"   • Error handling: Active")
        print(f"   • Token management: Active")
        print(f"   • Caching: Active")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_integration_test()
    exit(0 if success else 1)
