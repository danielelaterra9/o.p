#!/usr/bin/env python3
"""
Extended Character Persistence Testing with Navigation Changes
Tests character persistence with actual travel between islands
"""

import requests
import json
import random
import string
import time

# Configuration
BASE_URL = "https://project-builder-127.preview.emergentagent.com/api"

class ExtendedPersistenceTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_credentials = None
        self.initial_token = None
        self.character_data = None
        self.test_results = []

    def log_test(self, test_name, success, message):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} | {test_name}: {message}"
        print(result)
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
        return success

    def setup_rich_character(self):
        """Setup character with enough resources to test navigation"""
        try:
            # Generate unique user credentials
            random_suffix = ''.join(random.choices(string.digits, k=8))
            username = f"RichPirate{random_suffix}"
            email = f"richpirate{random_suffix}@test.com"
            password = "SecureTestPass123!"

            self.user_credentials = {
                "username": username,
                "email": email,
                "password": password
            }

            # Register user
            register_data = {
                "username": username,
                "email": email,
                "password": password
            }

            response = self.session.post(f"{BASE_URL}/auth/register", json=register_data)
            if response.status_code != 200:
                return self.log_test("Setup: User Registration", False, f"Registration failed: {response.text}")
            
            self.initial_token = response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {self.initial_token}"})

            # Create character
            character_data = {
                "nome_personaggio": "Nami Navigator",
                "ruolo": "pirata",
                "genere": "femmina",
                "eta": 18,
                "razza": "umano",
                "stile_combattimento": "tiratore",
                "sogno": "Disegnare una mappa del mondo",
                "storia_carattere": "Una navigatrice esperta che conosce tutti i segreti del mare. Ama i soldi e le mappe.",
                "mestiere": "navigatore",
                "mare_partenza": "east_blue"
            }

            char_response = self.session.post(f"{BASE_URL}/characters", json=character_data)
            if char_response.status_code != 200:
                return self.log_test("Setup: Character Creation", False, f"Character creation failed: {char_response.text}")
            
            self.character_data = char_response.json()

            # Give character enough Berry through battles (simulate earning money)
            # First, let's try some battles to earn Berry
            battle_response = self.session.post(f"{BASE_URL}/battle/start", 
                                              json={"opponent_type": "npc", "opponent_id": "pirata_novizio"})
            
            if battle_response.status_code == 200:
                battle_data = battle_response.json()
                battle_id = battle_data.get("battle_id")
                
                # Execute attack to win battle
                attack_response = self.session.post(f"{BASE_URL}/battle/{battle_id}/action",
                                                  json={"action_type": "attacco_base", "action_name": "Pugno"})
                
                if attack_response.status_code == 200:
                    # Check if we won and got rewards
                    battle_result = attack_response.json()
                    battle_state = battle_result.get("battle", {})
                    
                    if battle_state.get("stato") == "finita" and battle_state.get("vincitore") == "player1":
                        rewards = battle_state.get("rewards", {})
                        berry_gained = rewards.get("berry", 0)
                        self.log_test("Setup: Battle Rewards", True, f"Won battle, gained {berry_gained} Berry")

            return self.log_test("Setup: Rich Character", True, f"Character {self.character_data['character_id']} created and ready for testing")
            
        except Exception as e:
            return self.log_test("Setup: Rich Character", False, f"Setup error: {str(e)}")

    def test_buy_ship_and_travel(self):
        """Buy a ship and travel to next island"""
        try:
            # Get current character Berry amount
            char_response = self.session.get(f"{BASE_URL}/characters/me")
            if char_response.status_code != 200:
                return self.log_test("Ship & Travel: Get Character", False, "Failed to get character")
            
            character = char_response.json()
            current_berry = character.get("berry", 0)
            current_island = character.get("isola_corrente")
            
            self.log_test("Ship & Travel: Status", True, f"Character has {current_berry} Berry at {current_island}")

            # Try to buy the cheapest ship (5000 Berry)
            ship_response = self.session.post(f"{BASE_URL}/shop/buy", json={"item_id": "barca_piccola"})
            
            if ship_response.status_code != 200:
                # Not enough Berry - let's check what we can afford
                shop_response = self.session.get(f"{BASE_URL}/shop/items")
                if shop_response.status_code == 200:
                    items = shop_response.json().get("items", {})
                    ship_price = items.get("barca_piccola", {}).get("price", 5000)
                    return self.log_test("Ship & Travel: Buy Ship", False, 
                                       f"Cannot afford ship: need {ship_price} Berry, have {current_berry}")
                
                return self.log_test("Ship & Travel: Buy Ship", False, f"Ship purchase failed: {ship_response.text}")
            
            # Ship purchased successfully
            self.log_test("Ship & Travel: Buy Ship", True, "Successfully bought ship")

            # Get islands to find next available island
            islands_response = self.session.get(f"{BASE_URL}/world/islands")
            if islands_response.status_code != 200:
                return self.log_test("Ship & Travel: Get Islands", False, "Failed to get islands")
            
            islands_data = islands_response.json()
            islands = islands_data.get("islands", [])
            
            # Find next available island
            next_island = None
            for island in islands:
                if island.get("can_travel_forward"):
                    next_island = island["id"]
                    break
            
            if not next_island:
                return self.log_test("Ship & Travel: Find Next Island", False, "No forward travel available")

            # Travel to next island
            travel_response = self.session.post(f"{BASE_URL}/world/travel", 
                                              json={"island_id": next_island})
            
            if travel_response.status_code != 200:
                return self.log_test("Ship & Travel: Travel", False, f"Travel failed: {travel_response.text}")
            
            travel_result = travel_response.json()
            return self.log_test("Ship & Travel: Travel", True, 
                               f"Successfully traveled to {travel_result.get('island', {}).get('name', next_island)}")
            
        except Exception as e:
            return self.log_test("Ship & Travel: Navigation", False, f"Navigation error: {str(e)}")

    def test_persistence_after_travel(self):
        """Test persistence after traveling to a different island"""
        try:
            # Get current position before logout
            char_response = self.session.get(f"{BASE_URL}/characters/me")
            if char_response.status_code != 200:
                return self.log_test("Persistence: Pre-logout Check", False, "Failed to get character before logout")
            
            pre_logout_char = char_response.json()
            pre_logout_island = pre_logout_char.get("isola_corrente")
            pre_logout_berry = pre_logout_char.get("berry")
            pre_logout_ship = pre_logout_char.get("nave")
            
            self.log_test("Persistence: Pre-logout State", True, 
                         f"Before logout: at {pre_logout_island}, {pre_logout_berry} Berry, ship: {pre_logout_ship}")

            # Simulate logout by clearing token
            self.session.headers.pop("Authorization", None)
            
            # Login again with same credentials
            login_data = {
                "email": self.user_credentials["email"],
                "password": self.user_credentials["password"]
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            if login_response.status_code != 200:
                return self.log_test("Persistence: Re-login", False, f"Login failed: {login_response.text}")
            
            new_token = login_response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {new_token}"})
            
            # Get character data after login
            post_login_response = self.session.get(f"{BASE_URL}/characters/me")
            if post_login_response.status_code != 200:
                return self.log_test("Persistence: Post-login Check", False, "Failed to get character after login")
            
            post_login_char = post_login_response.json()
            post_login_island = post_login_char.get("isola_corrente")
            post_login_berry = post_login_char.get("berry")
            post_login_ship = post_login_char.get("nave")
            
            # Verify all data persisted correctly
            if post_login_island != pre_logout_island:
                return self.log_test("Persistence: Island State", False, 
                                   f"Island position not persisted: {pre_logout_island} → {post_login_island}")
            
            if post_login_berry != pre_logout_berry:
                return self.log_test("Persistence: Berry State", False, 
                                   f"Berry amount not persisted: {pre_logout_berry} → {post_login_berry}")
            
            if post_login_ship != pre_logout_ship:
                return self.log_test("Persistence: Ship State", False, 
                                   f"Ship not persisted: {pre_logout_ship} → {post_login_ship}")
            
            return self.log_test("Persistence: Complete State", True, 
                               f"All data persisted correctly: at {post_login_island}, {post_login_berry} Berry, ship: {post_login_ship}")
            
        except Exception as e:
            return self.log_test("Persistence: After Travel", False, f"Persistence test error: {str(e)}")

    def run_extended_test(self):
        """Run extended character persistence test with navigation"""
        print("=" * 80)
        print("EXTENDED CHARACTER PERSISTENCE TESTING")
        print("Testing persistence with navigation changes and purchases")
        print("=" * 80)
        
        tests_passed = 0
        total_tests = 0
        
        test_functions = [
            ("Setup: Create Rich Character", self.setup_rich_character),
            ("Test: Ship Purchase & Travel", self.test_buy_ship_and_travel),
            ("Test: Persistence After Travel", self.test_persistence_after_travel),
        ]
        
        for test_name, test_func in test_functions:
            print(f"\n[RUNNING] {test_name}")
            result = test_func()
            if result:
                tests_passed += 1
            total_tests += 1
            
            # Stop if critical steps fail
            if not result and "Setup" in test_name:
                print(f"❌ Setup failed: {test_name}. Stopping test.")
                break
        
        print("\n" + "=" * 80)
        print("EXTENDED PERSISTENCE TESTING SUMMARY")
        print("=" * 80)
        
        success_rate = (tests_passed / total_tests) * 100 if total_tests > 0 else 0
        print(f"Tests Passed: {tests_passed}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("✅ EXTENDED PERSISTENCE WORKING!")
        else:
            print("❌ EXTENDED PERSISTENCE ISSUES!")
            
        return success_rate >= 80

if __name__ == "__main__":
    tester = ExtendedPersistenceTester()
    success = tester.run_extended_test()
    exit(0 if success else 1)