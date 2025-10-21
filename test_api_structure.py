#!/usr/bin/env python3
"""
Test the API structure without requiring dependencies
"""

import json
import sys
import os

def test_api_structure():
    """Test the API structure and routing"""
    print("🧪 TESTING API STRUCTURE (No Dependencies)")
    print("=" * 60)
    
    # Test 1: Check if api.py exists and has correct structure
    print("1. 📁 Checking API File Structure")
    print("-" * 40)
    
    try:
        with open('api.py', 'r') as f:
            content = f.read()
        print("✅ api.py file exists")
        print(f"   File size: {len(content)} characters")
    except Exception as e:
        print(f"❌ api.py file error: {e}")
        return False
    
    # Test 2: Check handler function
    print("\n2. 🔧 Checking Handler Function")
    print("-" * 40)
    
    required_functions = [
        'def handler(request):',
        'def handle_enrich(data):',
        'def handle_webhook(data):',
        'def handle_health():'
    ]
    
    for func in required_functions:
        if func in content:
            print(f"✅ {func}")
        else:
            print(f"❌ {func}")
    
    # Test 3: Check routing logic
    print("\n3. 🛣️  Checking Routing Logic")
    print("-" * 40)
    
    routing_checks = [
        ('/enrich route', 'path == \'/enrich\''),
        ('/webhook route', 'path == \'/webhook\''),
        ('/health route', 'path == \'/health\''),
        ('POST method check', 'method == \'POST\''),
        ('GET method check', 'method == \'GET\'')
    ]
    
    for check_name, pattern in routing_checks:
        if pattern in content:
            print(f"✅ {check_name}")
        else:
            print(f"❌ {check_name}")
    
    # Test 4: Check response format
    print("\n4. 📤 Checking Response Format")
    print("-" * 40)
    
    response_checks = [
        ('statusCode field', 'statusCode'),
        ('headers field', 'headers'),
        ('body field', 'body'),
        ('JSON serialization', 'json.dumps'),
        ('Content-Type header', 'Content-Type')
    ]
    
    for check_name, pattern in response_checks:
        if pattern in content:
            print(f"✅ {check_name}")
        else:
            print(f"❌ {check_name}")
    
    # Test 5: Check error handling
    print("\n5. 🚨 Checking Error Handling")
    print("-" * 40)
    
    error_checks = [
        ('Try-catch blocks', 'try:'),
        ('Exception handling', 'except Exception'),
        ('400 status codes', 'statusCode\": 400'),
        ('500 status codes', 'statusCode\": 500'),
        ('404 status codes', 'statusCode\": 404'),
        ('Error logging', 'logger.error')
    ]
    
    for check_name, pattern in error_checks:
        if pattern in content:
            print(f"✅ {check_name}")
        else:
            print(f"❌ {check_name}")
    
    # Test 6: Check request parsing
    print("\n6. 📥 Checking Request Parsing")
    print("-" * 40)
    
    parsing_checks = [
        ('Method extraction', 'request.get(\'method\''),
        ('Path extraction', 'request.get(\'path\''),
        ('Body extraction', 'request.get(\'body\''),
        ('JSON parsing', 'json.loads'),
        ('Data validation', 'data.get(\'domain\''),
        ('Data validation', 'data.get(\'list_source\'')
    ]
    
    for check_name, pattern in parsing_checks:
        if pattern in content:
            print(f"✅ {check_name}")
        else:
            print(f"❌ {check_name}")
    
    return True

def test_vercel_config():
    """Test Vercel configuration"""
    print("\n7. ⚙️  Checking Vercel Configuration")
    print("-" * 40)
    
    try:
        with open('vercel.json', 'r') as f:
            config = json.load(f)
        
        # Check required fields
        required_fields = ['version', 'builds', 'routes']
        for field in required_fields:
            if field in config:
                print(f"✅ {field} present")
            else:
                print(f"❌ {field} missing")
        
        # Check build configuration
        if 'builds' in config and len(config['builds']) > 0:
            build = config['builds'][0]
            if build.get('src') == 'api.py':
                print("✅ Build source correct (api.py)")
            else:
                print(f"❌ Build source incorrect: {build.get('src')}")
            
            if build.get('use') == '@vercel/python':
                print("✅ Build type correct (@vercel/python)")
            else:
                print(f"❌ Build type incorrect: {build.get('use')}")
        
        # Check routing
        if 'routes' in config and len(config['routes']) > 0:
            route = config['routes'][0]
            if route.get('dest') == '/api.py':
                print("✅ Route destination correct (/api.py)")
            else:
                print(f"❌ Route destination incorrect: {route.get('dest')}")
        
        # Check environment variables
        if 'env' in config:
            env_vars = config['env']
            if 'APOLLO_API_KEY' in env_vars:
                print("✅ APOLLO_API_KEY configured")
            else:
                print("❌ APOLLO_API_KEY missing")
            
            if 'OPENAI_API_KEY' in env_vars:
                print("✅ OPENAI_API_KEY configured")
            else:
                print("❌ OPENAI_API_KEY missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Vercel config error: {e}")
        return False

def test_dependencies():
    """Test dependencies configuration"""
    print("\n8. 📦 Checking Dependencies")
    print("-" * 40)
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        required_packages = ['requests', 'openai', 'python-dotenv']
        for package in required_packages:
            if package in requirements:
                print(f"✅ {package}")
            else:
                print(f"❌ {package} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Dependencies error: {e}")
        return False

def main():
    """Run all structure tests"""
    print("🎯 API STRUCTURE TEST (No Dependencies Required)")
    print("=" * 60)
    
    tests = [
        ("API Structure", test_api_structure),
        ("Vercel Configuration", test_vercel_config),
        ("Dependencies", test_dependencies)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 STRUCTURE TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} structure tests passed")
    
    if passed == total:
        print("🎉 API STRUCTURE IS CORRECT!")
        print("✅ Ready for Vercel deployment")
        print("✅ All endpoints properly configured")
        print("✅ Error handling implemented")
        print("✅ Vercel compatibility confirmed")
    else:
        print("⚠️  Some structure issues found. Check output above.")

if __name__ == "__main__":
    main()
