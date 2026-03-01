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
        
        # Test data for v2 system
        timestamp = int(time.time())
        self.test_email = f"test_pirate_{timestamp}@grandline.com"
        self.test_password = "StrawHat123!"
        self.test_username = f"testuser_{timestamp}"
        self.test_character_name = "Monkey Luffy"  # Valid name without D.
        self.invalid_character_name = "Monkey D. Luffy"  # Should be blocked

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
        """Test authentication flows for v2 system"""
        print("\n" + "="*50)
        print("TESTING AUTHENTICATION V2")
        print("="*50)
        
        # Test registration with username field (separate from character name)
        register_data = {
            "username": self.test_username,  # New: separate username field
            "email": self.test_email,
            "password": self.test_password
        }
        
        success, response = self.run_test(
            "User Registration with Username", 
            "POST", 
            "auth/register", 
            200, 
            register_data,
            skip_auth=True
        )
        
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response.get('user', {}).get('user_id')
            print(f"✅ Registration successful with username: {response.get('user', {}).get('username')}")
            print(f"✅ Token acquired: {self.token[:20]}...")
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
        
        if success and 'token' in response:
            # Update token from login response
            self.token = response['token']
            print(f"✅ Login successful, new token acquired")
        
        # Test /auth/me endpoint
        self.run_test("Get Current User", "GET", "auth/me", 200)
        
        return True

    def test_game_data_endpoints(self):
        """Test game data endpoints (races, fighting styles, mestieri)"""
        print("\n" + "="*50)
        print("TESTING GAME DATA ENDPOINTS")
        print("="*50)
        
        if not self.token:
            print("❌ No auth token, skipping game data tests")
            return False
        
        # Test get races (should return 6 races)
        success, response = self.run_test("Get Races", "GET", "game/races", 200)
        if success and 'races' in response:
            races_count = len(response['races'])
            print(f"✅ Found {races_count} races")
            if races_count == 6:
                print("✅ Correct number of races (6)")
            else:
                print(f"⚠️  Expected 6 races, found {races_count}")
                
            # Validate race structure
            for race_id, race_data in response['races'].items():
                if 'name' in race_data and 'bonus' in race_data:
                    print(f"   ✅ Race {race_id}: {race_data['name']} - valid structure")
                else:
                    print(f"   ❌ Race {race_id}: missing required fields")
        
        # Test get fighting styles
        success, response = self.run_test("Get Fighting Styles", "GET", "game/fighting-styles", 200)
        if success and 'styles' in response:
            styles_count = len(response['styles'])
            print(f"✅ Found {styles_count} fighting styles")
            
            # Validate fighting style structure
            for style_id, style_data in response['styles'].items():
                if 'name' in style_data and 'bonus' in style_data:
                    print(f"   ✅ Style {style_id}: {style_data['name']} - valid structure")
        
        # Test get mestieri (should return 12 mestieri)
        success, response = self.run_test("Get Mestieri", "GET", "game/mestieri", 200)
        if success and 'mestieri' in response:
            mestieri_count = len(response['mestieri'])
            print(f"✅ Found {mestieri_count} mestieri")
            if mestieri_count == 12:
                print("✅ Correct number of mestieri (12)")
            else:
                print(f"⚠️  Expected 12 mestieri, found {mestieri_count}")
                
            # Validate mestiere structure
            for mestiere_id, mestiere_data in response['mestieri'].items():
                if 'name' in mestiere_data and 'description' in mestiere_data:
                    print(f"   ✅ Mestiere {mestiere_id}: {mestiere_data['name']} - valid structure")
        
        return True

    def test_character_name_validation(self):
        """Test character name validation blocking D. pattern"""
        print("\n" + "="*50)
        print("TESTING CHARACTER NAME VALIDATION")
        print("="*50)
        
        if not self.token:
            print("❌ No auth token, skipping name validation tests")
            return False
        
        # Test invalid name with D. pattern (should be rejected)
        invalid_name_data = {"nome": self.invalid_character_name}
        success, response = self.run_test(
            "Validate Invalid Name (with D.)",
            "POST",
            "characters/validate-name", 
            200,
            invalid_name_data
        )
        
        if success and 'valid' in response:
            if response['valid'] == False and 'D.' in response.get('message', ''):
                print(f"✅ Name validation correctly blocked D. pattern")
                print(f"   Message: {response.get('message', '')}")
            else:
                print(f"❌ Name validation failed to block D. pattern")
                print(f"   Response: {response}")
        
        # Test valid name (should be accepted)
        valid_name_data = {"nome": self.test_character_name}
        success, response = self.run_test(
            "Validate Valid Name",
            "POST", 
            "characters/validate-name",
            200,
            valid_name_data
        )
        
        if success and 'valid' in response:
            if response['valid'] == True:
                print(f"✅ Name validation correctly accepted valid name")
            else:
                print(f"❌ Name validation incorrectly rejected valid name: {response.get('message', '')}")
        
        return True

    def test_character_system(self):
        """Test v2 character creation and management system"""
        print("\n" + "="*50)
        print("TESTING CHARACTER SYSTEM V2")
        print("="*50)
        
        if not self.token:
            print("❌ No auth token, skipping character tests")
            return False
        
        # Test AI trait extraction first
        traits_data = {
            "storia_carattere": "Un giovane pirata coraggioso che sogna di diventare il Re dei Pirati. È molto determinato ma a volte impulsivo nelle sue decisioni. Ama aiutare i suoi amici e non sopporta le ingiustizie."
        }
        
        success, response = self.run_test(
            "AI Trait Extraction",
            "POST",
            "characters/extract-traits",
            200,
            traits_data
        )
        
        extracted_traits = []
        if success and 'traits' in response:
            extracted_traits = response['traits']
            print(f"✅ AI extracted {len(extracted_traits)} traits: {', '.join(extracted_traits)}")
        
        # Test full character creation with v2 system
        character_data = {
            "nome_personaggio": self.test_character_name,
            "ruolo": "pirata",
            "genere": "maschio",
            "eta": 17,
            "razza": "umano",  # Using race from the races endpoint
            "stile_combattimento": "corpo_misto",  # Using fighting style from styles endpoint
            "sogno": "Diventare il Re dei Pirati!",
            "storia_carattere": "Un giovane pirata coraggioso che sogna di diventare il Re dei Pirati. È molto determinato ma a volte impulsivo nelle sue decisioni.",
            "mestiere": "capitano",  # Using mestiere from mestieri endpoint
            "colore_capelli": "Nero",
            "colore_occhi": "Marroni", 
            "particolarita": "Cicatrice sotto l'occhio sinistro"
        }
        
        success, response = self.run_test(
            "Create Character V2",
            "POST",
            "characters",
            200,
            character_data
        )
        
        if success and 'character_id' in response:
            self.character_id = response['character_id']
            print(f"✅ Character created with ID: {self.character_id}")
            
            # Verify character has expected v2 fields
            expected_fields = ['nome_personaggio', 'razza', 'stile_combattimento', 'mestiere', 'sogno', 'aspetto']
            for field in expected_fields:
                if field in response:
                    print(f"   ✅ Character has {field}: {response.get(field)}")
                else:
                    print(f"   ❌ Character missing {field}")
        
        # Test update character traits (if we have extracted traits)
        if extracted_traits:
            traits_update_data = {"traits": extracted_traits}
            success, response = self.run_test(
                "Update Character Traits",
                "PUT",
                "characters/me/traits", 
                200,
                traits_update_data
            )
            
            if success:
                print(f"✅ Character traits updated successfully")
        
        # Test get my character
        success, response = self.run_test("Get My Character", "GET", "characters/me", 200)
        
        if success and self.character_id:
            # Test get character public info
            self.run_test(
                "Get Character Public Info",
                "GET", 
                f"characters/{self.character_id}/public",
                200
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
        
        # Test start battle with updated opponent types
        battle_data = {
            "opponent_type": "npc",
            "opponent_id": "marine_soldato"  # Updated to match backend NPC types
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
            
            # Test battle action with updated action types
            action_data = {
                "action_type": "attacco_base",  # Updated to match v2 system
                "action_name": "Pugno"
            }
            
            self.run_test(
                "Execute Battle Action",
                "POST",
                f"battle/{battle_id}/action",
                200,
                action_data
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
        
        # Test simplified AI narration (updated for v2)
        narration_data = {
            "attacker": "Test Pirate",
            "action": "pugno potente",
            "damage": 15,
            "effect": "Il nemico barcolla!"
        }
        
        self.run_test(
            "AI Action Narration",
            "POST",
            "ai/narrate-action", 
            200,
            narration_data
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