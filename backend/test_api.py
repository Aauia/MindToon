#!/usr/bin/env python3
"""
Test script for MindToon API endpoints
Run this to verify your backend is working correctly
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_ios_config():
    """Test iOS config endpoint"""
    print("\n🔍 Testing iOS config endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/ios/config")
        if response.status_code == 200:
            print("✅ iOS config endpoint working")
            config = response.json()
            print(f"   API Version: {config.get('api_version')}")
            print(f"   Base URL: {config.get('base_url')}")
            print(f"   Features: {config.get('features')}")
            return True
        else:
            print(f"❌ iOS config failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ iOS config error: {e}")
        return False

def test_register():
    """Test user registration"""
    print("\n🔍 Testing user registration...")
    try:
        user_data = {
            "username": "testuser123",
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "testpassword123"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ User registration successful")
            user = response.json()
            print(f"   User ID: {user.get('id')}")
            print(f"   Username: {user.get('username')}")
            return user_data
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

def test_login(username, password):
    """Test user login"""
    print("\n🔍 Testing user login...")
    try:
        login_data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("✅ Login successful")
            token_data = response.json()
            print(f"   Token type: {token_data.get('token_type')}")
            print(f"   Access token: {token_data.get('access_token')[:20]}...")
            return token_data.get('access_token')
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_comic_generation(token):
    """Test comic generation"""
    print("\n🔍 Testing comic generation...")
    try:
        comic_data = {
            "message": "A superhero saves a cat from a tree",
            "genre": "superhero",
            "art_style": "comic book"
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/chats/scenario/comic/sheet/",
            json=comic_data,
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Comic generation successful")
            comic = response.json()
            print(f"   Comic ID: {comic.get('id')}")
            print(f"   Genre: {comic.get('genre')}")
            print(f"   Art Style: {comic.get('art_style')}")
            print(f"   Panels: {len(comic.get('panels', []))}")
            print(f"   Sheet URL: {comic.get('sheet_url')}")
            return True
        else:
            print(f"❌ Comic generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Comic generation error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting MindToon API Tests")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Backend is not running or not accessible")
        print("   Make sure to start your FastAPI server with: uvicorn src.main:app --reload")
        sys.exit(1)
    
    # Test 2: iOS config
    if not test_ios_config():
        print("\n❌ iOS config endpoint not working")
        sys.exit(1)
    
    # Test 3: Registration
    user_data = test_register()
    if not user_data:
        print("\n⚠️  Registration failed (user might already exist)")
        # Try with existing user
        user_data = {
            "username": "admin",
            "password": "ad123"
        }
    
    # Test 4: Login
    token = test_login(user_data["username"], user_data["password"])
    if not token:
        print("\n❌ Login failed")
        sys.exit(1)
    
    # Test 5: Comic generation
    if not test_comic_generation(token):
        print("\n❌ Comic generation failed")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Your backend is ready for iOS integration!")
    print("\n📱 Next steps:")
    print("   1. Start your iOS app development")
    print("   2. Use the provided Swift code examples")
    print("   3. Test with the iOS simulator")
    print("   4. Deploy to production when ready")

if __name__ == "__main__":
    main() 