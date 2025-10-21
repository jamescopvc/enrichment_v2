#!/usr/bin/env python3
"""
Test the actual API endpoints with real data
"""

import json
import sys
import os

# Add current directory to path for imports
sys.path.append('.')

def test_health_endpoint():
    """Test the health endpoint"""
    print("🏥 Testing Health Endpoint")
    print("-" * 40)
    
    try:
        from api import handler
        
        # Simulate health check request
        request = {
            "method": "GET",
            "path": "/health",
            "body": "{}"
        }
        
        response = handler(request)
        
        print(f"Status Code: {response['statusCode']}")
        print(f"Headers: {response['headers']}")
        
        body = json.loads(response['body'])
        print(f"Response Body: {json.dumps(body, indent=2)}")
        
        if response['statusCode'] == 200 and body.get('status') == 'healthy':
            print("✅ Health endpoint working correctly")
            return True
        else:
            print("❌ Health endpoint failed")
            return False
            
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_enrich_endpoint():
    """Test the enrich endpoint with real data"""
    print("\n🔍 Testing Enrich Endpoint")
    print("-" * 40)
    
    try:
        from api import handler
        
        # Test with exactrx.ai (known working domain)
        request = {
            "method": "POST",
            "path": "/enrich",
            "body": json.dumps({
                "domain": "exactrx.ai",
                "list_source": "james-test"
            })
        }
        
        print("Request payload:")
        print(json.dumps(json.loads(request['body']), indent=2))
        
        response = handler(request)
        
        print(f"\nStatus Code: {response['statusCode']}")
        print(f"Headers: {response['headers']}")
        
        body = json.loads(response['body'])
        print(f"Response Body: {json.dumps(body, indent=2)}")
        
        if response['statusCode'] == 200:
            print("✅ Enrich endpoint working correctly")
            return True
        else:
            print("❌ Enrich endpoint failed")
            return False
            
    except Exception as e:
        print(f"❌ Enrich endpoint error: {e}")
        return False

def test_webhook_endpoint():
    """Test the webhook endpoint with real data"""
    print("\n🔗 Testing Webhook Endpoint")
    print("-" * 40)
    
    try:
        from api import handler
        
        # Test with amperefinancial.com (known working domain)
        request = {
            "method": "POST",
            "path": "/webhook",
            "body": json.dumps({
                "domain": "amperefinancial.com",
                "list_source": "zi-test"
            })
        }
        
        print("Request payload:")
        print(json.dumps(json.loads(request['body']), indent=2))
        
        response = handler(request)
        
        print(f"\nStatus Code: {response['statusCode']}")
        print(f"Headers: {response['headers']}")
        
        body = json.loads(response['body'])
        print(f"Response Body: {json.dumps(body, indent=2)}")
        
        if response['statusCode'] == 200:
            print("✅ Webhook endpoint working correctly")
            return True
        else:
            print("❌ Webhook endpoint failed")
            return False
            
    except Exception as e:
        print(f"❌ Webhook endpoint error: {e}")
        return False

def test_error_handling():
    """Test error handling with invalid requests"""
    print("\n🚨 Testing Error Handling")
    print("-" * 40)
    
    try:
        from api import handler
        
        # Test 1: Missing domain
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
            print("✅ Missing domain error handled correctly")
        else:
            print("❌ Missing domain error not handled")
        
        # Test 2: Missing list_source
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
            print("✅ Missing list_source error handled correctly")
        else:
            print("❌ Missing list_source error not handled")
        
        # Test 3: Invalid endpoint
        request = {
            "method": "GET",
            "path": "/invalid",
            "body": "{}"
        }
        
        response = handler(request)
        print(f"Invalid endpoint - Status: {response['statusCode']}")
        
        if response['statusCode'] == 404:
            print("✅ Invalid endpoint error handled correctly")
        else:
            print("❌ Invalid endpoint error not handled")
            
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_list_source_validation():
    """Test list source validation logic"""
    print("\n🔐 Testing List Source Validation")
    print("-" * 40)
    
    try:
        from api import handler
        
        # Test valid james source
        request = {
            "method": "POST",
            "path": "/enrich",
            "body": json.dumps({
                "domain": "test.com",
                "list_source": "james-sales-team"
            })
        }
        
        response = handler(request)
        print(f"James source - Status: {response['statusCode']}")
        
        # Test valid zi source
        request = {
            "method": "POST",
            "path": "/enrich",
            "body": json.dumps({
                "domain": "test.com",
                "list_source": "zi-venture-capital"
            })
        }
        
        response = handler(request)
        print(f"Zi source - Status: {response['statusCode']}")
        
        # Test invalid source
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
    """Run all endpoint tests"""
    print("🧪 TESTING ACTUAL API ENDPOINTS")
    print("=" * 60)
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Enrich Endpoint", test_enrich_endpoint),
        ("Webhook Endpoint", test_webhook_endpoint),
        ("Error Handling", test_error_handling),
        ("List Source Validation", test_list_source_validation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 {test_name.upper()}")
        print(f"{'='*60}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST RESULTS SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! API is ready for deployment!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
