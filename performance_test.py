import requests
import time
import sys

class PerformanceTest:
    def __init__(self, base_url="https://mindai-youth.preview.emergentagent.com"):
        self.api_url = f"{base_url}/api"
        self.session_id = f"perf_test_{int(time.time())}"

    def test_normal_chat_performance(self):
        """Test normal chat response time - should be under 15 seconds"""
        print("🚀 Testing Normal Chat Performance...")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.api_url}/chat",
                json={
                    "session_id": self.session_id,
                    "message": "I feel stressed about exams"
                },
                timeout=20
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            print(f"   Response time: {response_time:.2f} seconds")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {response.status_code}")
                print(f"   ✅ Crisis flag: {data.get('is_crisis', 'N/A')}")
                print(f"   ✅ Response length: {len(data.get('response', ''))}")
                
                if response_time <= 15:
                    print(f"   ✅ PASS: Response time {response_time:.2f}s <= 15s target")
                    return True
                else:
                    print(f"   ❌ FAIL: Response time {response_time:.2f}s > 15s target")
                    return False
            else:
                print(f"   ❌ FAIL: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            end_time = time.time()
            response_time = end_time - start_time
            print(f"   ❌ FAIL: Request timed out after {response_time:.2f} seconds")
            return False
        except Exception as e:
            print(f"   ❌ FAIL: Error - {str(e)}")
            return False

    def test_crisis_chat_performance(self):
        """Test crisis chat response time - should be under 20 seconds"""
        print("\n🚨 Testing Crisis Chat Performance...")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.api_url}/chat",
                json={
                    "session_id": f"{self.session_id}_crisis",
                    "message": "I want to hurt myself"
                },
                timeout=25
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            print(f"   Response time: {response_time:.2f} seconds")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {response.status_code}")
                print(f"   ✅ Crisis flag: {data.get('is_crisis', 'N/A')}")
                print(f"   ✅ Helplines provided: {bool(data.get('helplines'))}")
                
                # Verify crisis detection
                if not data.get('is_crisis', False):
                    print(f"   ❌ FAIL: Crisis not detected")
                    return False
                
                # Verify helplines
                helplines = data.get('helplines', {})
                expected_helplines = ['KIRAN', 'Vandrevala', 'Sneha', 'Sumaitri']
                found_helplines = [name for name in expected_helplines if name in helplines]
                
                if len(found_helplines) < 4:
                    print(f"   ❌ FAIL: Missing helplines. Found: {found_helplines}")
                    return False
                
                print(f"   ✅ All Indian helplines present: {found_helplines}")
                
                if response_time <= 20:
                    print(f"   ✅ PASS: Response time {response_time:.2f}s <= 20s target")
                    return True
                else:
                    print(f"   ❌ FAIL: Response time {response_time:.2f}s > 20s target")
                    return False
            else:
                print(f"   ❌ FAIL: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            end_time = time.time()
            response_time = end_time - start_time
            print(f"   ❌ FAIL: Request timed out after {response_time:.2f} seconds")
            return False
        except Exception as e:
            print(f"   ❌ FAIL: Error - {str(e)}")
            return False

    def test_helplines_endpoint_performance(self):
        """Test helplines endpoint performance"""
        print("\n📞 Testing Helplines Endpoint Performance...")
        
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.api_url}/helplines", timeout=5)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            print(f"   Response time: {response_time:.2f} seconds")
            
            if response.status_code == 200:
                data = response.json()
                helplines = data.get('helplines', {})
                expected_helplines = ['KIRAN', 'Vandrevala', 'Sneha', 'Sumaitri']
                
                print(f"   ✅ Status: {response.status_code}")
                print(f"   ✅ Helplines count: {len(helplines)}")
                
                # Verify all expected helplines
                for helpline_name in expected_helplines:
                    if helpline_name not in helplines:
                        print(f"   ❌ FAIL: Missing helpline {helpline_name}")
                        return False
                    
                    helpline = helplines[helpline_name]
                    required_fields = ['name', 'number', 'hours', 'description']
                    
                    for field in required_fields:
                        if field not in helpline:
                            print(f"   ❌ FAIL: Helpline {helpline_name} missing field {field}")
                            return False
                
                print(f"   ✅ All helplines verified: {list(helplines.keys())}")
                print(f"   ✅ PASS: Helplines endpoint working correctly")
                return True
            else:
                print(f"   ❌ FAIL: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ FAIL: Error - {str(e)}")
            return False

def main():
    print("⚡ Mental Wellness AI - Performance Testing")
    print("=" * 50)
    
    tester = PerformanceTest()
    
    tests = [
        ("Normal Chat Performance (≤15s)", tester.test_normal_chat_performance),
        ("Crisis Chat Performance (≤20s)", tester.test_crisis_chat_performance),
        ("Helplines Endpoint", tester.test_helplines_endpoint_performance),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test crashed: {str(e)}")
    
    print(f"\n{'='*50}")
    print(f"📊 PERFORMANCE TEST RESULTS")
    print(f"{'='*50}")
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ ALL PERFORMANCE TESTS PASSED!")
        return 0
    else:
        print("❌ SOME PERFORMANCE TESTS FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())