#!/usr/bin/env python3
"""
Dice Navigation with Ship Test - One Piece RPG
Tests dice navigation system when character has enough money to buy a ship
"""

import requests
import json
import random
import string
import time

# Configuration
BASE_URL = "https://e-commerce-315.preview.emergentagent.com/api"

class NavigationWithShipTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None

    def log_test(self, test_name, success, message):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} | {test_name}: {message}"
        print(result)
        return success

    def setup_character_with_money(self):
        """Create character and give them enough money through battles"""
        try:
            # Generate unique credentials
            random_suffix = ''.join(random.choices(string.digits, k=8))
            username = f"RichPirate{random_suffix}"
            email = f"rich{random_suffix}@test.com"
            password = "TestPass123!"

            # Register user
            register_data = {"username": username, "email": email, "password": password}
            response = self.session.post(f"{BASE_URL}/auth/register", json=register_data)
            
            if response.status_code != 200:
                return self.log_test("Setup Rich Character", False, f"Registration failed: {response.text}")
            
            self.token = response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})

            # Create character
            character_data = {
                "nome_personaggio": "Rich Monkey Luffy",
                "ruolo": "pirata",
                "genere": "maschio",
                "eta": 17,
                "razza": "umano",
                "stile_combattimento": "corpo_misto",
                "sogno": "Diventare il Re dei Pirati e comprare una nave",
                "storia_carattere": "Un giovane pirata determinato a navigare i mari.",
                "mestiere": "capitano",
                "mare_partenza": "east_blue"
            }

            char_response = self.session.post(f"{BASE_URL}/characters", json=character_data)
            if char_response.status_code != 200:
                return self.log_test("Setup Rich Character", False, f"Character creation failed: {char_response.text}")

            # Fight battles to earn money
            battles_won = 0
            for i in range(50):  # Fight up to 50 battles to earn money
                # Start battle
                battle_response = self.session.post(f"{BASE_URL}/battle/start")
                if battle_response.status_code != 200:
                    continue
                
                battle_data = battle_response.json()
                battle_id = battle_data.get("battle_id")
                
                if not battle_id:
                    continue
                
                # Execute attack
                action_data = {"action": "attacco_base", "tecnica": "Pugno"}
                action_response = self.session.post(f"{BASE_URL}/battle/{battle_id}/action", json=action_data)
                
                if action_response.status_code == 200:
                    action_result = action_response.json()
                    if action_result.get("battaglia_terminata") and action_result.get("vincitore") == "giocatore":
                        battles_won += 1
                
                # Small delay between battles
                time.sleep(0.1)
                
                # Check money periodically
                if i % 10 == 0:
                    char_check = self.session.get(f"{BASE_URL}/characters/me")
                    if char_check.status_code == 200:
                        current_berry = char_check.json().get("berry", 0)
                        if current_berry >= 5000:  # Enough for ship
                            break

            # Check final money
            final_char = self.session.get(f"{BASE_URL}/characters/me")
            if final_char.status_code != 200:
                return self.log_test("Setup Rich Character", False, "Failed to get final character state")
            
            final_berry = final_char.json().get("berry", 0)
            
            return self.log_test("Setup Rich Character", True, 
                               f"Character created with {final_berry} Berry after {battles_won} battles won")
            
        except Exception as e:
            return self.log_test("Setup Rich Character", False, f"Setup error: {str(e)}")

    def buy_ship_test(self):
        """Buy a ship and test the purchase"""
        try:
            # Get shop items to find ship
            shop_response = self.session.get(f"{BASE_URL}/shop/items")
            if shop_response.status_code != 200:
                return self.log_test("Buy Ship", False, f"Failed to get shop items: {shop_response.text}")

            items = shop_response.json().get("items", [])
            ship_item = None
            
            # Find a ship (barca_piccola)
            for item in items:
                if item.get("id") == "barca_piccola" or "barca" in item.get("name", "").lower():
                    ship_item = item
                    break
            
            if not ship_item:
                return self.log_test("Buy Ship", False, "No ship found in shop")

            # Try to buy ship
            purchase_data = {"item_id": ship_item["id"]}
            purchase_response = self.session.post(f"{BASE_URL}/shop/buy", json=purchase_data)
            
            if purchase_response.status_code != 200:
                error_detail = purchase_response.json().get("detail", "Unknown error")
                return self.log_test("Buy Ship", False, f"Ship purchase failed: {error_detail}")
            
            purchase_result = purchase_response.json()
            
            return self.log_test("Buy Ship", True, 
                               f"Successfully purchased {ship_item['name']} for {ship_item['prezzo']} Berry")
            
        except Exception as e:
            return self.log_test("Buy Ship", False, f"Ship purchase error: {str(e)}")

    def test_navigation_with_ship(self):
        """Test navigation dice rolling with ship"""
        try:
            rolls_tested = 0
            successful_navigation = False
            outcomes = []
            
            for i in range(5):  # Try up to 5 dice rolls
                response = self.session.post(f"{BASE_URL}/navigation/roll-dice")
                
                if response.status_code != 200:
                    return self.log_test("Navigation With Ship", False, f"Dice roll failed: {response.text}")
                
                dice_data = response.json()
                rolls_tested += 1
                
                # Verify structure
                required_fields = ["dice_result", "bonuses", "total", "outcome", "message", "arrived"]
                for field in required_fields:
                    if field not in dice_data:
                        return self.log_test("Navigation With Ship", False, f"Missing field: {field}")
                
                dice_result = dice_data.get("dice_result")
                outcome = dice_data.get("outcome")
                arrived = dice_data.get("arrived")
                
                outcomes.append(outcome)
                
                # Log the roll result
                print(f"  Roll {i+1}: Dice={dice_result}, Outcome={outcome}, Arrived={arrived}")
                
                if arrived:
                    successful_navigation = True
                    break
                
                time.sleep(0.5)
            
            if successful_navigation:
                return self.log_test("Navigation With Ship", True, 
                                   f"Navigation successful after {rolls_tested} rolls. Outcomes: {outcomes}")
            else:
                return self.log_test("Navigation With Ship", True, 
                                   f"Navigation tested with {rolls_tested} rolls. Outcomes: {outcomes} (no arrival but system working)")
            
        except Exception as e:
            return self.log_test("Navigation With Ship", False, f"Navigation error: {str(e)}")

    def run_test(self):
        """Run the complete navigation with ship test"""
        print("=" * 70)
        print("DICE NAVIGATION WITH SHIP TEST")
        print("=" * 70)
        
        tests = [
            ("Setup Rich Character", self.setup_character_with_money),
            ("Buy Ship", self.buy_ship_test),
            ("Navigation With Ship", self.test_navigation_with_ship),
        ]
        
        passed = 0
        total = 0
        
        for test_name, test_func in tests:
            print(f"\n[RUNNING] {test_name}")
            result = test_func()
            if result:
                passed += 1
            total += 1
            
            if not result and test_name in ["Setup Rich Character", "Buy Ship"]:
                print(f"Critical step failed: {test_name}. Stopping.")
                break
        
        print("\n" + "=" * 70)
        print(f"NAVIGATION WITH SHIP TEST RESULTS: {passed}/{total} passed")
        return passed == total

if __name__ == "__main__":
    tester = NavigationWithShipTester()
    success = tester.run_test()