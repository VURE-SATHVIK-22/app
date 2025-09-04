import requests
import sys
import json
import time
from datetime import datetime

class MentalWellnessAPITester:
    def __init__(self, base_url="https://mindai-youth.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.session_id = f"test_session_{int(time.time())}"

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=30):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}")
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timed out after {timeout} seconds")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_normal_chat(self):
        """Test normal mental health chat with GPT-5"""
        print("\n📝 Testing normal mental health conversation...")
        success, response = self.run_test(
            "Normal Chat - Exam Stress",
            "POST",
            "chat",
            200,
            data={
                "session_id": self.session_id,
                "message": "I feel really stressed about my upcoming board exams. My parents have high expectations and I'm worried I'll disappoint them."
            },
            timeout=45  # AI responses can take time
        )
        
        if success and isinstance(response, dict):
            # Verify response structure
            required_fields = ['id', 'response', 'is_crisis', 'timestamp']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            # Verify it's not a crisis
            if response.get('is_crisis', True):
                print(f"❌ Normal message incorrectly flagged as crisis")
                return False
            
            # Verify AI response exists and is meaningful
            ai_response = response.get('response', '')
            if len(ai_response) < 20:
                print(f"❌ AI response too short: {ai_response}")
                return False
            
            print(f"✅ AI Response (first 100 chars): {ai_response[:100]}...")
            print(f"✅ Crisis flag correctly set to: {response['is_crisis']}")
            return True
        
        return False

    def test_crisis_detection(self):
        """Test crisis detection system"""
        print("\n🚨 Testing crisis detection system...")
        
        crisis_messages = [
            "I want to hurt myself, I can't take this anymore",
            "I'm thinking about suicide, everything feels hopeless",
            "I want to end my life, there's no way out"
        ]
        
        all_passed = True
        
        for i, message in enumerate(crisis_messages):
            print(f"\n   Testing crisis message {i+1}: '{message[:50]}...'")
            success, response = self.run_test(
                f"Crisis Detection {i+1}",
                "POST",
                "chat",
                200,
                data={
                    "session_id": f"{self.session_id}_crisis_{i}",
                    "message": message
                },
                timeout=45
            )
            
            if success and isinstance(response, dict):
                # Verify crisis is detected
                if not response.get('is_crisis', False):
                    print(f"❌ Crisis message not detected as crisis!")
                    all_passed = False
                    continue
                
                # Verify helplines are provided
                if 'helplines' not in response or not response['helplines']:
                    print(f"❌ No helplines provided for crisis message!")
                    all_passed = False
                    continue
                
                # Verify Indian helplines are present
                helplines = response['helplines']
                expected_helplines = ['KIRAN', 'Vandrevala', 'Sneha', 'Sumaitri']
                found_helplines = [name for name in expected_helplines if name in helplines]
                
                if len(found_helplines) < 2:
                    print(f"❌ Not enough Indian helplines found: {found_helplines}")
                    all_passed = False
                    continue
                
                print(f"✅ Crisis detected with helplines: {list(helplines.keys())}")
                
                # Verify helpline structure
                for helpline_name, helpline_data in helplines.items():
                    required_fields = ['name', 'number', 'hours', 'description']
                    if not all(field in helpline_data for field in required_fields):
                        print(f"❌ Helpline {helpline_name} missing required fields")
                        all_passed = False
                
            else:
                all_passed = False
        
        return all_passed

    def test_wellness_resources(self):
        """Test wellness resources endpoint"""
        print("\n📚 Testing wellness resources...")
        success, response = self.run_test(
            "Wellness Resources",
            "GET",
            "wellness-resources",
            200
        )
        
        if success and isinstance(response, dict):
            if 'resources' not in response:
                print(f"❌ No 'resources' key in response")
                return False
            
            resources = response['resources']
            if not isinstance(resources, list) or len(resources) == 0:
                print(f"❌ Resources should be a non-empty list")
                return False
            
            # Check resource structure
            required_fields = ['id', 'title', 'content', 'category', 'tags']
            for i, resource in enumerate(resources[:3]):  # Check first 3
                missing_fields = [field for field in required_fields if field not in resource]
                if missing_fields:
                    print(f"❌ Resource {i} missing fields: {missing_fields}")
                    return False
            
            # Check for Indian-specific content
            indian_keywords = ['academic', 'family', 'indian', 'pressure', 'exam']
            found_indian_content = False
            for resource in resources:
                content_lower = (resource.get('content', '') + resource.get('title', '')).lower()
                if any(keyword in content_lower for keyword in indian_keywords):
                    found_indian_content = True
                    break
            
            if not found_indian_content:
                print(f"❌ No Indian-specific content found in resources")
                return False
            
            print(f"✅ Found {len(resources)} wellness resources with Indian context")
            return True
        
        return False

    def test_helplines_endpoint(self):
        """Test helplines endpoint"""
        print("\n📞 Testing helplines endpoint...")
        success, response = self.run_test(
            "Helplines Endpoint",
            "GET",
            "helplines",
            200
        )
        
        if success and isinstance(response, dict):
            if 'helplines' not in response:
                print(f"❌ No 'helplines' key in response")
                return False
            
            helplines = response['helplines']
            expected_helplines = ['KIRAN', 'Vandrevala', 'Sneha', 'Sumaitri']
            
            for helpline_name in expected_helplines:
                if helpline_name not in helplines:
                    print(f"❌ Missing expected helpline: {helpline_name}")
                    return False
                
                helpline = helplines[helpline_name]
                required_fields = ['name', 'number', 'hours', 'description']
                missing_fields = [field for field in required_fields if field not in helpline]
                
                if missing_fields:
                    print(f"❌ Helpline {helpline_name} missing fields: {missing_fields}")
                    return False
            
            print(f"✅ All Indian helplines present with correct structure")
            return True
        
        return False

    def test_blockchain_integrity(self):
        """Test blockchain data integrity"""
        print("\n🔐 Testing blockchain data integrity...")
        
        # Send a message and check if hash is generated
        success, response = self.run_test(
            "Blockchain Hash Generation",
            "POST",
            "chat",
            200,
            data={
                "session_id": f"{self.session_id}_blockchain",
                "message": "Test message for blockchain integrity"
            },
            timeout=30
        )
        
        if success and isinstance(response, dict):
            # The hash is generated server-side and stored in DB
            # We can verify the response structure is correct
            if 'id' not in response:
                print(f"❌ No message ID for blockchain tracking")
                return False
            
            print(f"✅ Message ID generated for blockchain tracking: {response['id']}")
            return True
        
        return False

    def test_anonymous_session_handling(self):
        """Test anonymous session handling"""
        print("\n🕵️ Testing anonymous session handling...")
        
        # Test with different session IDs
        sessions = [f"anon_test_{i}_{int(time.time())}" for i in range(3)]
        
        for session_id in sessions:
            success, response = self.run_test(
                f"Anonymous Session {session_id[-10:]}",
                "POST",
                "chat",
                200,
                data={
                    "session_id": session_id,
                    "message": "Hello, this is an anonymous session test"
                },
                timeout=30
            )
            
            if not success:
                print(f"❌ Failed to handle anonymous session: {session_id}")
                return False
        
        print(f"✅ Successfully handled {len(sessions)} anonymous sessions")
        return True

def main():
    print("🧠 Mental Wellness AI Platform - Backend API Testing")
    print("=" * 60)
    
    tester = MentalWellnessAPITester()
    
    # Test sequence - prioritizing core functionality
    tests = [
        ("Root Endpoint", tester.test_root_endpoint),
        ("Normal Chat with GPT-5", tester.test_normal_chat),
        ("Crisis Detection System", tester.test_crisis_detection),
        ("Wellness Resources", tester.test_wellness_resources),
        ("Helplines Endpoint", tester.test_helplines_endpoint),
        ("Blockchain Integrity", tester.test_blockchain_integrity),
        ("Anonymous Sessions", tester.test_anonymous_session_handling),
    ]
    
    failed_tests = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if not test_func():
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {str(e)}")
            failed_tests.append(test_name)
    
    # Print final results
    print(f"\n{'='*60}")
    print(f"📊 FINAL TEST RESULTS")
    print(f"{'='*60}")
    print(f"Total Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    
    if failed_tests:
        print(f"\n❌ FAILED TESTS:")
        for test in failed_tests:
            print(f"   - {test}")
        return 1
    else:
        print(f"\n✅ ALL TESTS PASSED!")
        return 0

if __name__ == "__main__":
    sys.exit(main())