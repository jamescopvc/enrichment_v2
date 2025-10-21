#!/usr/bin/env python3
"""
Test script to verify Vercel deployment compatibility
"""

import json

def test_vercel_handler():
    """Test the Vercel handler function"""
    print("🧪 Testing Vercel Handler Function")
    print("=" * 50)
    
    # Import the handler
    try:
        from api import handler
        print("✅ Successfully imported handler function")
    except ImportError as e:
        print(f"❌ Failed to import handler: {e}")
        return
    
    # Test health endpoint
    print("\n1. Testing Health Endpoint:")
    health_request = {
        "method": "GET",
        "path": "/health",
        "body": "{}"
    }
    
    try:
        response = handler(health_request)
        print(f"   Status Code: {response['statusCode']}")
        print(f"   Response: {response['body']}")
        if response['statusCode'] == 200:
            print("   ✅ Health endpoint working")
        else:
            print("   ❌ Health endpoint failed")
    except Exception as e:
        print(f"   ❌ Health endpoint error: {e}")
    
    # Test enrich endpoint
    print("\n2. Testing Enrich Endpoint:")
    enrich_request = {
        "method": "POST",
        "path": "/enrich",
        "body": json.dumps({
            "domain": "exactrx.ai",
            "list_source": "james-test"
        })
    }
    
    try:
        response = handler(enrich_request)
        print(f"   Status Code: {response['statusCode']}")
        if response['statusCode'] == 200:
            print("   ✅ Enrich endpoint working")
        else:
            print(f"   ❌ Enrich endpoint failed: {response['body']}")
    except Exception as e:
        print(f"   ❌ Enrich endpoint error: {e}")
    
    # Test webhook endpoint
    print("\n3. Testing Webhook Endpoint:")
    webhook_request = {
        "method": "POST",
        "path": "/webhook",
        "body": json.dumps({
            "domain": "amperefinancial.com",
            "list_source": "zi-test"
        })
    }
    
    try:
        response = handler(webhook_request)
        print(f"   Status Code: {response['statusCode']}")
        if response['statusCode'] == 200:
            print("   ✅ Webhook endpoint working")
        else:
            print(f"   ❌ Webhook endpoint failed: {response['body']}")
    except Exception as e:
        print(f"   ❌ Webhook endpoint error: {e}")
    
    # Test invalid endpoint
    print("\n4. Testing Invalid Endpoint:")
    invalid_request = {
        "method": "GET",
        "path": "/invalid",
        "body": "{}"
    }
    
    try:
        response = handler(invalid_request)
        print(f"   Status Code: {response['statusCode']}")
        if response['statusCode'] == 404:
            print("   ✅ Invalid endpoint correctly returns 404")
        else:
            print(f"   ❌ Invalid endpoint should return 404: {response['body']}")
    except Exception as e:
        print(f"   ❌ Invalid endpoint error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Vercel Deployment Test Complete!")

if __name__ == "__main__":
    test_vercel_handler()
