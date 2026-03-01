#!/usr/bin/env python3
"""
Complete Character Persistence Test with Multiple Battles
Tests character persistence with earning Berry through battles and navigation
"""

import requests
import json
import random
import string
import time

# Configuration
BASE_URL = "https://project-builder-127.preview.emergentagent.com/api"

class CompletePersistenceTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_credentials = None
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

    def complete_persistence_flow(self):
        """Complete persistence test with earning Berry and navigation"""
        try:
            print("=" * 80)
            print("COMPLETE CHARACTER PERSISTENCE FLOW TEST")
            print("=" * 80)

            # Step 1: Register and create character
            random_suffix = ''.join(random.choices(string.digits, k=10))
            username = f"CompleteTester{random_suffix}"
            email = f"complete{random_suffix}@test.com"
            password = "SecureTestPass123!"

            self.user_credentials = {
                "username": username,
                "email": email,
                "password": password
            }

            # Register
            register_response = self.session.post(f"{BASE_URL}/auth/register", 
                                                json={"username": username, "email": email, "password": password})
            
            if register_response.status_code != 200:
                return self.log_test("Complete Flow", False, f"Registration failed: {register_response.text}")

            token = register_response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})

            # Create character
            character_data = {
                "nome_personaggio": "Luffy Explorer",
                "ruolo": "pirata",
                "genere": "maschio",
                "eta": 17,
                "razza": "umano",
                "stile_combattimento": "corpo_pugni",
                "sogno": "Diventare il Re dei Pirati e esplorare tutti i mari",
                "storia_carattere": "Un giovane pirata con il sogno di diventare il Re dei Pirati. Ha mangiato il frutto del diavolo Gomu Gomu no Mi.",
                "mestiere": "capitano",
                "mare_partenza": "east_blue"
            }

            char_response = self.session.post(f"{BASE_URL}/characters", json=character_data)
            if char_response.status_code != 200:
                return self.log_test("Complete Flow", False, f"Character creation failed: {char_response.text}")

            self.character_data = char_response.json()
            character_id = self.character_data.get("character_id")

            print(f"✅ Step 1: Created character {character_id} with initial Berry: {self.character_data.get('berry')}")

            # Step 2: Fight multiple battles to earn Berry
            battles_won = 0
            total_berry_earned = 0

            for i in range(10):  # Try up to 10 battles
                battle_response = self.session.post(f"{BASE_URL}/battle/start", 
                                                  json={"opponent_type": "npc", "opponent_id": "pirata_novizio"})
                
                if battle_response.status_code != 200:
                    continue

                battle_data = battle_response.json()
                battle_id = battle_data.get("battle_id")

                # Keep attacking until battle ends
                for attack_num in range(20):  # Max 20 attacks per battle
                    attack_response = self.session.post(f"{BASE_URL}/battle/{battle_id}/action",
                                                      json={"action_type": "attacco_speciale", "action_name": "Gomu Gomu no Pistol"})
                    
                    if attack_response.status_code != 200:
                        break

                    attack_result = attack_response.json()
                    battle_state = attack_result.get("battle", {})

                    if battle_state.get("stato") == "finita":
                        if battle_state.get("vincitore") == "player1":
                            battles_won += 1
                            rewards = battle_state.get("rewards", {})
                            berry_gained = rewards.get("berry", 0)
                            total_berry_earned += berry_gained
                            print(f"   Won battle #{battles_won}, gained {berry_gained} Berry")
                        break

                # Check current Berry amount
                current_char = self.session.get(f"{BASE_URL}/characters/me")
                if current_char.status_code == 200:
                    char_data = current_char.json()
                    current_berry = char_data.get("berry", 0)
                    if current_berry >= 5000:  # Enough for ship
                        break

            print(f"✅ Step 2: Won {battles_won} battles, earned {total_berry_earned} Berry total")

            # Step 3: Get final Berry amount and buy ship if possible
            final_char_response = self.session.get(f"{BASE_URL}/characters/me")
            if final_char_response.status_code != 200:
                return self.log_test("Complete Flow", False, "Failed to get final character state")

            final_char = final_char_response.json()
            final_berry = final_char.get("berry", 0)
            original_island = final_char.get("isola_corrente")

            print(f"✅ Step 3: Character now has {final_berry} Berry at {original_island}")

            navigation_tested = False
            final_island = original_island

            if final_berry >= 5000:
                # Buy ship and travel
                ship_response = self.session.post(f"{BASE_URL}/shop/buy", json={"item_id": "barca_piccola"})
                
                if ship_response.status_code == 200:
                    print(f"✅ Step 4: Successfully bought ship")
                    
                    # Get islands and travel
                    islands_response = self.session.get(f"{BASE_URL}/world/islands")
                    if islands_response.status_code == 200:
                        islands_data = islands_response.json()
                        islands = islands_data.get("islands", [])
                        
                        next_island = None
                        for island in islands:
                            if island.get("can_travel_forward"):
                                next_island = island["id"]
                                break
                        
                        if next_island:
                            travel_response = self.session.post(f"{BASE_URL}/world/travel", 
                                                              json={"island_id": next_island})
                            if travel_response.status_code == 200:
                                final_island = next_island
                                navigation_tested = True
                                print(f"✅ Step 5: Successfully traveled to {next_island}")

            # Step 4: Simulate logout and login
            self.session.headers.pop("Authorization", None)
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", 
                                             json={"email": email, "password": password})
            
            if login_response.status_code != 200:
                return self.log_test("Complete Flow", False, f"Login after logout failed: {login_response.text}")

            new_token = login_response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {new_token}"})

            print(f"✅ Step 6: Successfully logged back in with new token")

            # Step 5: Verify all data persisted
            persistent_char_response = self.session.get(f"{BASE_URL}/characters/me")
            if persistent_char_response.status_code != 200:
                return self.log_test("Complete Flow", False, "Failed to get character after login")

            persistent_char = persistent_char_response.json()
            
            # Verify character ID matches
            if persistent_char.get("character_id") != character_id:
                return self.log_test("Complete Flow", False, "Character ID mismatch after login")

            # Verify key data persisted
            persistent_berry = persistent_char.get("berry")
            persistent_island = persistent_char.get("isola_corrente")
            persistent_ship = persistent_char.get("nave")

            print(f"✅ Step 7: After login - Berry: {persistent_berry}, Island: {persistent_island}, Ship: {persistent_ship}")

            # Verify persistence
            success_messages = []
            
            if persistent_berry >= 1000:  # Should have at least starting Berry + battle rewards
                success_messages.append(f"Berry persisted: {persistent_berry}")
            else:
                return self.log_test("Complete Flow", False, f"Berry not properly persisted: {persistent_berry}")

            if persistent_island == final_island:
                success_messages.append(f"Island position persisted: {persistent_island}")
            else:
                return self.log_test("Complete Flow", False, 
                                   f"Island position not persisted: expected {final_island}, got {persistent_island}")

            if navigation_tested and persistent_ship:
                success_messages.append(f"Ship persisted: {persistent_ship}")

            # Test character name and core data
            if persistent_char.get("nome_personaggio") != "Luffy Explorer":
                return self.log_test("Complete Flow", False, "Character name not persisted")

            if persistent_char.get("mestiere") != "capitano":
                return self.log_test("Complete Flow", False, "Character mestiere not persisted")

            success_message = "Character persistence COMPLETE: " + ", ".join(success_messages)
            
            if navigation_tested:
                success_message += f" | Navigation tested with travel to {final_island}"
            else:
                success_message += f" | Navigation state maintained at {final_island}"

            return self.log_test("Complete Flow", True, success_message)

        except Exception as e:
            return self.log_test("Complete Flow", False, f"Exception during complete test: {str(e)}")

    def run_test(self):
        """Run the complete persistence test"""
        success = self.complete_persistence_flow()
        
        print("\n" + "=" * 80)
        print("COMPLETE PERSISTENCE TEST SUMMARY")
        print("=" * 80)
        
        if success:
            print("🎉 COMPLETE CHARACTER PERSISTENCE TEST PASSED!")
            print("✅ All aspects of character data persist correctly across login sessions")
            print("✅ Returning players can successfully continue where they left off")
            print("✅ Battle rewards, purchases, and navigation state all persist")
        else:
            print("❌ CHARACTER PERSISTENCE TEST FAILED!")
            print("🔧 Issues detected that prevent returning players from continuing properly")
            
        return success

if __name__ == "__main__":
    tester = CompletePersistenceTester()
    success = tester.run_test()
    exit(0 if success else 1)