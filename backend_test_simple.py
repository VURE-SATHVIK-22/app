import requests
import sys
import json
import time

def test_backend_apis():
    """Simple backend API tests"""
    base_url = "https://mindai-youth.preview.emergentagent.com/api"
    session_id = f"test_{int(time.time())}"
    
    print("🧠 Mental Wellness AI - Backend API Tests")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Root endpoint
    tests_total += 1
    print("\n1. Testing Root API Endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "Mental Wellness AI" in data.get("message", ""):
                print("✅ Root endpoint working")
                tests_passed += 1
            else:
                print(f"❌ Unexpected response: {data}")
        else:
            print(f"❌ Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 2: Helplines endpoint
    tests_total += 1
    print("\n2. Testing Helplines Endpoint...")
    try:
        response = requests.get(f"{base_url}/helplines", timeout=10)
        if response.status_code == 200:
            data = response.json()
            helplines = data.get("helplines", {})
            expected = ["KIRAN", "Vandrevala", "Sneha", "Sumaitri"]
            found = [name for name in expected if name in helplines]
            if len(found) >= 3:
                print(f"✅ Helplines endpoint working - Found: {found}")
                tests_passed += 1
            else:
                print(f"❌ Missing helplines. Found: {found}")
        else:
            print(f"❌ Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 3: Wellness resources
    tests_total += 1
    print("\n3. Testing Wellness Resources...")
    try:
        response = requests.get(f"{base_url}/wellness-resources", timeout=10)
        if response.status_code == 200:
            data = response.json()
            resources = data.get("resources", [])
            if len(resources) >= 3:
                print(f"✅ Wellness resources working - Found {len(resources)} resources")
                tests_passed += 1
            else:
                print(f"❌ Not enough resources: {len(resources)}")
        else:
            print(f"❌ Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 4: Normal chat
    tests_total += 1
    print("\n4. Testing Normal Chat...")
    try:
        chat_data = {
            "session_id": session_id,
            "message": "I feel stressed about my exams"
        }
        response = requests.post(f"{base_url}/chat", json=chat_data, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get("response") and len(data["response"]) > 20:
                is_crisis = data.get("is_crisis", True)
                print(f"✅ Normal chat working - Crisis flag: {is_crisis}")
                if not is_crisis:
                    tests_passed += 1
                else:
                    print("❌ Normal message flagged as crisis")
            else:
                print(f"❌ Invalid response: {data}")
        else:
            print(f"❌ Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 5: Crisis detection
    tests_total += 1
    print("\n5. Testing Crisis Detection...")
    try:
        crisis_data = {
            "session_id": f"{session_id}_crisis",
            "message": "I want to hurt myself, I can't take this anymore"
        }
        response = requests.post(f"{base_url}/chat", json=crisis_data, timeout=30)
        if response.status_code == 200:
            data = response.json()
            is_crisis = data.get("is_crisis", False)
            helplines = data.get("helplines", {})
            if is_crisis and helplines:
                print(f"✅ Crisis detection working - Found {len(helplines)} helplines")
                tests_passed += 1
            else:
                print(f"❌ Crisis not detected properly - Crisis: {is_crisis}, Helplines: {bool(helplines)}")
        else:
            print(f"❌ Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Results
    print(f"\n{'='*50}")
    print(f"📊 RESULTS: {tests_passed}/{tests_total} tests passed")
    
    if tests_passed == tests_total:
        print("✅ ALL BACKEND TESTS PASSED!")
        return True
    else:
        print(f"❌ {tests_total - tests_passed} tests failed")
        return False

if __name__ == "__main__":
    success = test_backend_apis()
    sys.exit(0 if success else 1)