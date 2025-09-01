#!/usr/bin/env python3
"""
Test script to verify authentication endpoints work correctly
"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:5000"  # Change this to your deployed URL for testing

def test_endpoints():
    """Test all authentication endpoints"""
    print("🧪 Testing Authentication Endpoints...")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Debug endpoint
    print("\n2. Testing /debug endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/debug")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Registration
    print("\n3. Testing /auth/register endpoint...")
    test_user = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Login
    print("\n4. Testing /auth/login endpoint...")
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            session_token = response.json()['user']['session_token']
            print(f"   Session token: {session_token[:20]}...")
        else:
            session_token = None
            
    except Exception as e:
        print(f"   Error: {e}")
        session_token = None
    
    # Test 5: Profile (if logged in)
    if session_token:
        print("\n5. Testing /auth/profile endpoint...")
        try:
            response = requests.get(
                f"{BASE_URL}/auth/profile",
                headers={"Authorization": f"Bearer {session_token}"}
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Testing completed!")

if __name__ == "__main__":
    test_endpoints()
