#!/usr/bin/env python3

import requests
import sys
import json
import time
from datetime import datetime

class OnePieceRPGAPITester:
    def __init__(self, base_url="https://nakama-combat.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.character_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        
        # Test data
        self.test_email = f"test_pirate_{int(time.time())}@grandline.com"
        self.test_password = "StrawHat123!"
        self.test_name = "Test Monkey D. Luffy"

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, skip_auth=False):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        
        # Default headers
        test_headers = {'Content-Type': 'application/json'}
        if self.token and not skip_auth:
            test_headers['Authorization'] = f'Bearer {self.token}'
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            print(f"   Response Status: {response.status_code}")
            print(f"   Expected Status: {expected_status}")

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - {name}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                print(f"❌ FAILED - {name}: {error_msg}")
                try:
                    error_data = response.json()
                    print(f"   Error Response: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Raw Response: {response.text[:200]}")
                
                self.failed_tests.append({
                    "test": name,
                    "endpoint": endpoint,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "error": error_msg
                })
                return False, {}

        except Exception as e:
            error_msg = f"Request failed: {str(e)}"
            print(f"❌ FAILED - {name}: {error_msg}")
            self.failed_tests.append({
                "test": name,
                "endpoint": endpoint,
                "error": error_msg
            })
            return False, {}

    def test_root_endpoints(self):
        """Test basic endpoints"""
        print("\n" + "="*50)
        print("TESTING ROOT ENDPOINTS")
        print("="*50)
        
        # Test root endpoint
        self.run_test("Root API", "GET", "", 200, skip_auth=True)
        
        # Test health endpoint
        self.run_test("Health Check", "GET", "health", 200, skip_auth=True)

    def test_authentication(self):
        """Test authentication flows"""
        print("\n" + "="*50)
        print("TESTING AUTHENTICATION")
        print("="*50)
        
        # Test registration
        register_data = {
            "name": self.test_name,
            "email": self.test_email,
            "password": self.test_password
        }
        
        success, response = self.run_test(
            "User Registration", 
            "POST", 
            "auth/register", 
            200, 
            register_data,
            skip_auth=True
        )
        
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response.get('user', {}).get('user_id')
            print(f"✅ Registration successful, token acquired")
        else:
            print(f"❌ Registration failed, cannot continue with auth tests")
            return False
        
        # Test login with same credentials
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        success, response = self.run_test(
            "User Login", 
            "POST", 
            "auth/login", 
            200, 
            login_data,
            skip_auth=True
        )
        
        # Test /auth/me endpoint
        self.run_test("Get Current User", "GET", "auth/me", 200)
        
        return True

    def test_character_system(self):
        """Test character creation and management"""
        print("\n" + "="*50)
        print("TESTING CHARACTER SYSTEM")
        print("="*50)
        
        if not self.token:
            print("❌ No auth token, skipping character tests")
            return False
        
        # Test character creation
        character_data = {
            "name": "Monkey D. Test Luffy",
            "title": "Test Pirate King",
            "body_type": "normal",
            "hair_color": "#000000",
            "outfit": "pirate",
            "race": "human", 
            "fighting_style": "brawler",
            "devil_fruit": "gomu_gomu"
        }
        
        success, response = self.run_test(
            "Create Character",
            "POST",
            "characters",
            200,
            character_data
        )
        
        if success and 'character_id' in response:
            self.character_id = response['character_id']
            print(f"✅ Character created with ID: {self.character_id}")
        
        # Test get my character
        self.run_test("Get My Character", "GET", "characters/me", 200)
        
        # Test character update
        update_data = {
            "title": "Updated Test Pirate",
            "hp": 95
        }
        self.run_test(
            "Update Character",
            "PUT", 
            "characters/me",
            200,
            update_data
        )
        
        return True

    def test_world_system(self):
        """Test world navigation and islands"""
        print("\n" + "="*50)
        print("TESTING WORLD SYSTEM")
        print("="*50)
        
        if not self.token:
            print("❌ No auth token, skipping world tests")
            return False
        
        # Test get islands
        success, response = self.run_test("Get World Islands", "GET", "world/islands", 200)
        
        if success and 'islands' in response:
            print(f"✅ Found {len(response['islands'])} islands")
        
        # Test dice rolling (this might fail if no ship)
        dice_data = {
            "destination": "open_sea"
        }
        self.run_test(
            "Roll Navigation Dice", 
            "POST", 
            "world/roll-dice", 
            400,  # Expecting 400 because character has no ship initially
            dice_data
        )
        
        return True

    def test_battle_system(self):
        """Test battle system"""
        print("\n" + "="*50)
        print("TESTING BATTLE SYSTEM")
        print("="*50)
        
        if not self.token:
            print("❌ No auth token, skipping battle tests")
            return False
        
        # Test start battle
        battle_data = {
            "opponent_type": "npc",
            "opponent_id": "marine_grunt"
        }
        
        success, response = self.run_test(
            "Start Battle",
            "POST",
            "battle/start",
            200,
            battle_data
        )
        
        battle_id = None
        if success and 'battle_id' in response:
            battle_id = response['battle_id']
            print(f"✅ Battle started with ID: {battle_id}")
            
            # Test battle action
            action_data = {
                "action_type": "basic_attack",
                "action_name": "Pugno"
            }
            
            self.run_test(
                "Execute Battle Action",
                "POST",
                f"battle/{battle_id}/action",
                200,
                action_data
            )
            
            # Test get battle status
            self.run_test(
                "Get Battle Status",
                "GET",
                f"battle/{battle_id}",
                200
            )
        
        return True

    def test_ai_features(self):
        """Test AI integration features"""
        print("\n" + "="*50)
        print("TESTING AI FEATURES")
        print("="*50)
        
        if not self.token:
            print("❌ No auth token, skipping AI tests")
            return False
        
        # Test battle narration
        narration_data = {
            "context": "Test battle context",
            "action": "Test pirate throws a punch!"
        }
        
        self.run_test(
            "AI Battle Narration",
            "POST",
            "ai/narrate-battle", 
            200,
            narration_data
        )
        
        # Test avatar generation
        avatar_data = {
            "description": "a brave pirate captain with a straw hat"
        }
        
        self.run_test(
            "AI Avatar Generation",
            "POST",
            "ai/generate-avatar",
            200, 
            avatar_data
        )
        
        return True

    def test_shop_system(self):
        """Test shop functionality"""
        print("\n" + "="*50)
        print("TESTING SHOP SYSTEM")
        print("="*50)
        
        if not self.token:
            print("❌ No auth token, skipping shop tests")
            return False
        
        # Test get shop items
        success, response = self.run_test("Get Shop Items", "GET", "shop/items", 200)
        
        if success and 'items' in response:
            print(f"✅ Found {len(response['items'])} shop items")
            
            # Test buy item (might fail due to insufficient funds)
            if response['items']:
                first_item = list(response['items'].keys())[0]
                buy_data = {
                    "item_id": first_item
                }
                self.run_test(
                    "Buy Shop Item",
                    "POST",
                    "shop/buy",
                    200,
                    buy_data
                )
        
        return True

    def test_cards_system(self):
        """Test card collection system"""
        print("\n" + "="*50)
        print("TESTING CARDS SYSTEM")
        print("="*50)
        
        if not self.token:
            print("❌ No auth token, skipping cards tests")
            return False
        
        # Test get card collection
        self.run_test("Get Card Collection", "GET", "cards/collection", 200)
        
        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {len(self.failed_tests)}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%" if self.tests_run > 0 else "No tests run")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for failure in self.failed_tests:
                print(f"  - {failure['test']}: {failure.get('error', 'Status code mismatch')}")
        
        return len(self.failed_tests) == 0

def main():
    print("🏴‍☠️ ONE PIECE RPG API TESTING")
    print("=" * 60)
    
    tester = OnePieceRPGAPITester()
    
    # Run all test suites
    tester.test_root_endpoints()
    tester.test_authentication()
    tester.test_character_system()
    tester.test_world_system()
    tester.test_battle_system()
    tester.test_ai_features()
    tester.test_shop_system()
    tester.test_cards_system()
    
    # Print summary and return appropriate exit code
    success = tester.print_summary()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())