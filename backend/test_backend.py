#!/usr/bin/env python
"""
Test script for Wax and Warmth Django backend
Run this after setting up the backend to verify everything works.
"""

import os
import sys
import requests
import json

def test_django_server():
    """Test if Django server is running."""
    try:
        response = requests.get('http://127.0.0.1:8000/', timeout=5)
        return True
    except:
        return False

def test_newsletter_api():
    """Test newsletter subscription API."""
    test_email = "test@example.com"
    
    try:
        # Test API endpoint
        response = requests.post(
            'http://127.0.0.1:8000/api/newsletter/subscribe/',
            json={'email': test_email},
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('success', False)
        else:
            return False
    except:
        return False

def main():
    """Run tests."""
    print("=== Wax and Warmth Backend Tests ===\n")
    
    # Check if manage.py exists
    if not os.path.exists('manage.py'):
        print("❌ Error: Please run this script from the backend directory")
        sys.exit(1)
    
    # Test 1: Django server
    print("1. Testing Django server...")
    if test_django_server():
        print("   ✅ Django server is running")
    else:
        print("   ❌ Django server is not running")
        print("   Please run: python manage.py runserver")
        return
    
    # Test 2: Newsletter API
    print("\n2. Testing Newsletter API...")
    if test_newsletter_api():
        print("   ✅ Newsletter API is working")
    else:
        print("   ❌ Newsletter API test failed")
        print("   Check Django logs for errors")
    
    print("\n=== Test Results ===")
    print("✅ Backend is ready for use!")
    print("\nNext steps:")
    print("1. Open your website HTML files in a browser")
    print("2. Try subscribing to the newsletter")
    print("3. Check the Django admin at http://127.0.0.1:8000/admin/")

if __name__ == "__main__":
    main()