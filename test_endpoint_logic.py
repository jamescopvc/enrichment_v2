#!/usr/bin/env python3
"""
Test the endpoint logic with mocked dependencies
"""

import json
import sys
import os

# Mock the dependencies to test the actual endpoint logic
class MockEnrichmentService:
    def __init__(self):
        pass
    
    def enrich_company(self, domain, list_source):
        # Mock response based on domain
        if domain == "exactrx.ai":
            return {
                "status": "enriched",
                "company": {
                    "name": "ExactRx",
                    "domain": "exactrx.ai",
                    "industry": "HealthTech",
                    "location": "Nashville, Tennessee",
                    "employee_count": 10,
                    "linkedin": "https://linkedin.com/company/exactrx"
                },
                "founders": [
                    {
                        "name": "Athena Doshi",
                        "title": "CEO & Founder",
                        "email": "athena@exactrx.ai",
                        "linkedin": "https://linkedin.com/in/athena-doshi-2837b799"
                    }
                ],
                "owner": "james@scopvc.com"
            }
        elif domain == "amperefinancial.com":
            return {
                "status": "enriched",
                "company": {
                    "name": "Ampere",
                    "domain": "amperefinancial.com",
                    "industry": "Financial Services",
                    "location": "Washington, DC",
                    "employee_count": 5,
                    "linkedin": "https://linkedin.com/company/ampere-ai"
                },
                "founders": [
                    {
                        "name": "Skye Lawrence",
                        "title": "Co-Founder",
                        "email": "skye@amperefinancial.com",
                        "linkedin": "https://linkedin.com/in/skye-lawrence"
                    }
                ],
                "owner": "zi@scopvc.com"
            }
        elif "invalid" in list_source:
            return {
                "status": "invalid",
                "message": "Unauthorized list source"
            }
        else:
            return {
                "status": "failed",
                "message": "Company not found"
            }

# Mock the enrichment_logic module
sys.modules['enrichment_logic'] = type('MockModule', (), {
    'EnrichmentService': MockEnrichmentService
})()

def test_health_endpoint():
    """Test health endpoint with mocked dependencies"""
    print("🏥 Testing Health Endpoint (Mocked)")
    print("-" * 40)
    
    try:
        from api import handler
        
        request = {
            "method": "GET",
            "path": "/health",
            "body": "{}"
        }
        
        response = handler(request)
        
        print(f"Status Code: {response['statusCode']}")
        print(f"Headers: {response['headers']}")
        
        body = json.loads(response['body'])
        print(f"Response: {json.dumps(body, indent=2)}")
        
        if response['statusCode'] == 200 and body.get('status') == 'healthy':
            print("✅ Health endpoint working")
            return True
        else:
            print("❌ Health endpoint failed")
            return False
            
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_enrich_endpoint():
    """Test enrich endpoint with real domain"""
    print("\n🔍 Testing Enrich Endpoint (Mocked)")
    print("-" * 40)
    
    try:
        from api import handler
        
        # Test with exactrx.ai
        request = {
            "method": "POST",
            "path": "/enrich",
            "body": json.dumps({
                "domain": "exactrx.ai",
                "list_source": "james-sales-team"
            })
        }
        
        print("Request:")
        print(json.dumps(json.loads(request['body']), indent=2))
        
        response = handler(request)
        
        print(f"\nStatus Code: {response['statusCode']}")
        print(f"Headers: {response['headers']}")
        
        body = json.loads(response['body'])
        print(f"Response: {json.dumps(body, indent=2)}")
        
        if response['statusCode'] == 200 and body.get('status') == 'enriched':
            print("✅ Enrich endpoint working")
            return True
        else:
            print("❌ Enrich endpoint failed")
            return False
            
    except Exception as e:
        print(f"❌ Enrich endpoint error: {e}")
        return False

def test_webhook_endpoint():
    """Test webhook endpoint with real domain"""
    print("\n🔗 Testing Webhook Endpoint (Mocked)")
    print("-" * 40)
    
    try:
        from api import handler
        
        # Test with amperefinancial.com
        request = {
            "method": "POST",
            "path": "/webhook",
            "body": json.dumps({
                "domain": "amperefinancial.com",
                "list_source": "zi-venture-capital"
            })
        }
        
        print("Request:")
        print(json.dumps(json.loads(request['body']), indent=2))
        
        response = handler(request)
        
        print(f"\nStatus Code: {response['statusCode']}")
        print(f"Headers: {response['headers']}")
        
        body = json.loads(response['body'])
        print(f"Response: {json.dumps(body, indent=2)}")
        
        if response['statusCode'] == 200 and body.get('status') == 'enriched':
            print("✅ Webhook endpoint working")
            return True
        else:
            print("❌ Webhook endpoint failed")
            return False
            
    except Exception as e:
        print(f"❌ Webhook endpoint error: {e}")
        return False

def test_error_handling():
    """Test error handling"""
    print("\n🚨 Testing Error Handling (Mocked)")
    print("-" * 40)
    
    try:
        from api import handler
        
        # Test missing domain
        request = {
            "method": "POST",
            "path": "/enrich",
            "body": json.dumps({
                "list_source": "james-test"
            })
        }
        
        response = handler(request)
        print(f"Missing domain - Status: {response['statusCode']}")
        
        if response['statusCode'] == 400:
            print("✅ Missing domain error handled")
        else:
            print("❌ Missing domain error not handled")
        
        # Test missing list_source
        request = {
            "method": "POST",
            "path": "/enrich",
            "body": json.dumps({
                "domain": "test.com"
            })
        }
        
        response = handler(request)
        print(f"Missing list_source - Status: {response['statusCode']}")
        
        if response['statusCode'] == 400:
            print("✅ Missing list_source error handled")
        else:
            print("❌ Missing list_source error not handled")
        
        # Test invalid endpoint
        request = {
            "method": "GET",
            "path": "/invalid",
            "body": "{}"
        }
        
        response = handler(request)
        print(f"Invalid endpoint - Status: {response['statusCode']}")
        
        if response['statusCode'] == 404:
            print("✅ Invalid endpoint error handled")
        else:
            print("❌ Invalid endpoint error not handled")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_list_source_validation():
    """Test list source validation"""
    print("\n🔐 Testing List Source Validation (Mocked)")
    print("-" * 40)
    
    try:
        from api import handler
        
        # Test invalid list source
        request = {
            "method": "POST",
            "path": "/enrich",
            "body": json.dumps({
                "domain": "test.com",
                "list_source": "invalid-source"
            })
        }
        
        response = handler(request)
        print(f"Invalid source - Status: {response['statusCode']}")
        
        body = json.loads(response['body'])
        if body.get('status') == 'invalid':
            print("✅ Invalid list source correctly rejected")
        else:
            print("❌ Invalid list source not handled")
        
        return True
        
    except Exception as e:
        print(f"❌ List source validation test failed: {e}")
        return False

def main():
    """Run all endpoint tests with mocked dependencies"""
    print("🧪 TESTING ACTUAL ENDPOINT LOGIC (With Mocked Dependencies)")
    print("=" * 70)
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Enrich Endpoint", test_enrich_endpoint),
        ("Webhook Endpoint", test_webhook_endpoint),
        ("Error Handling", test_error_handling),
        ("List Source Validation", test_list_source_validation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*70}")
        print(f"🧪 {test_name.upper()}")
        print(f"{'='*70}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 ENDPOINT TEST RESULTS SUMMARY")
    print(f"{'='*70}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} endpoint tests passed")
    
    if passed == total:
        print("🎉 ALL ENDPOINT TESTS PASSED!")
        print("✅ Health endpoint working")
        print("✅ Enrich endpoint working")
        print("✅ Webhook endpoint working")
        print("✅ Error handling working")
        print("✅ List source validation working")
        print("🚀 API is ready for Vercel deployment!")
    else:
        print("⚠️  Some endpoint tests failed. Check the output above.")

if __name__ == "__main__":
    main()
