#!/usr/bin/env python
"""
Simple newsletter subscription test
"""

import requests
import json

def test_newsletter_subscription():
    """Test newsletter subscription functionality."""
    
    # Test data
    test_email = "test@example.com"
    base_url = "http://127.0.0.1:8000"
    
    print("Testing Newsletter Subscription API...")
    print("=" * 50)
    
    # Test 1: API endpoint
    try:
        print("1. Testing API endpoint...")
        response = requests.post(
            f"{base_url}/api/newsletter/subscribe/",
            json={"email": test_email},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            print("   ✅ API endpoint working!")
        else:
            print("   ❌ API endpoint failed")
            
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
    
    # Test 2: Form endpoint with CSRF
    try:
        print("\n2. Testing form endpoint...")
        
        # First get CSRF token
        session = requests.Session()
        csrf_response = session.get(f"{base_url}/")
        
        if 'csrftoken' in session.cookies:
            csrf_token = session.cookies['csrftoken']
            
            # Now submit form
            form_data = {
                'email': 'test2@example.com',
                'csrfmiddlewaretoken': csrf_token
            }
            
            response = session.post(
                f"{base_url}/newsletter-login/",
                data=form_data,
                headers={'Referer': f"{base_url}/"}
            )
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Redirected to: {response.url}")
            
            if response.status_code == 200 or response.status_code == 302:
                print("   ✅ Form submission working!")
            else:
                print("   ❌ Form submission failed")
        else:
            print("   ❌ Could not get CSRF token")
            
    except Exception as e:
        print(f"   ❌ Form test failed: {e}")
    
    # Test 3: Admin access
    try:
        print("\n3. Testing admin access...")
        response = requests.get(f"{base_url}/admin/")
        
        if response.status_code == 200:
            print("   ✅ Admin interface accessible!")
        else:
            print("   ❌ Admin interface failed")
            
    except Exception as e:
        print(f"   ❌ Admin test failed: {e}")
    
    print("\n" + "=" * 50)
    print("Newsletter backend test completed!")
    print("\nTo test manually:")
    print("1. Open http://127.0.0.1:8000/ in your browser")
    print("2. Scroll down to the newsletter form")
    print("3. Enter an email and click 'Sign Up'")
    print("4. Check http://127.0.0.1:8000/admin/ for subscriptions")

if __name__ == "__main__":
    test_newsletter_subscription()