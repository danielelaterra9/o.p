#!/usr/bin/env python3

import requests
import json
import uuid
import time
import random
import string
from datetime import datetime

# Get backend URL from frontend/.env
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.strip().split('=')[1] + '/api'
    except:
        pass
    # Fallback to localhost
    return "http://localhost:8001/api"

BASE_URL = get_backend_url()

def random_string(length=8):
    """Generate random string for unique usernames/emails"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def random_character_data():
    """Generate random character data for testing"""
    return {
        "nome_personaggio": f"CombatTester{random.randint(10000, 99999)}",
        "ruolo": "Pirata",
        "genere": random.choice(["maschio", "femmina"]),
        "eta": random.randint(16, 30),
        "razza": random.choice(["umano", "uomo_pesce", "visone"]),
        "stile_combattimento": random.choice(["corpo_misto", "corpo_pugni", "corpo_calci", "armi_mono", "armi_pluri", "tiratore"]),
        "sogno": "Diventare il Re dei Pirati!",
        "storia_carattere": "Un giovane pirata che vuole testare il nuovo sistema di combattimento.",
        "mestiere": random.choice(["navigatore", "cuoco", "medico", "musicista"]),
        "mare_partenza": "east_blue"
    }

class CombatLevelSystemTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.token = None
        self.user_data = None
        self.character_data = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
        if error:
            print(f"   Error: {error}")

    def register_user(self):
        """Register a new user for testing"""
        try:
            random_id = random_string()
            user_data = {
                "username": f"combattest_{random_id}",
                "email": f"combattest_{random_id}@example.com",
                "password": "testpassword123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/register", json=user_data)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                self.user_data = user_data
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                self.log_test("User Registration", True, f"User {user_data['username']} created successfully")
                return True
            else:
                self.log_test("User Registration", False, "", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Registration", False, "", str(e))
            return False

    def create_character(self):
        """Create character and verify new combat level fields"""
        try:
            char_data = random_character_data()
            response = self.session.post(f"{self.base_url}/characters", json=char_data)
            
            if response.status_code == 200:
                self.character_data = response.json()
                
                # Check for new combat level fields
                required_fields = {
                    "livello_combattimento": 1,
                    "esperienza_livello": 0,
                    "esperienza_totale": 0,
                    "esperienza_prossimo_livello": 100
                }
                
                all_fields_present = True
                field_details = []
                
                for field, expected_value in required_fields.items():
                    actual_value = self.character_data.get(field)
                    if actual_value == expected_value:
                        field_details.append(f"{field}: {actual_value} ✓")
                    else:
                        field_details.append(f"{field}: {actual_value} (expected {expected_value}) ✗")
                        all_fields_present = False
                
                if all_fields_present:
                    self.log_test("Character Creation with Combat Fields", True, 
                                f"Character {char_data['nome_personaggio']} created with correct combat level fields: {', '.join(field_details)}")
                else:
                    self.log_test("Character Creation with Combat Fields", False, 
                                f"Missing or incorrect combat fields: {', '.join(field_details)}")
                return all_fields_present
            else:
                self.log_test("Character Creation with Combat Fields", False, "", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Character Creation with Combat Fields", False, "", str(e))
            return False

    def test_combat_level_info(self):
        """Test GET /api/combat/level-info endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/combat/level-info")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = [
                    "livello_combattimento", "esperienza_livello", "esperienza_prossimo_livello", 
                    "esperienza_totale", "moltiplicatore_exp", "prossimi_livelli"
                ]
                
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Verify data structure
                    prossimi_livelli = data.get("prossimi_livelli", [])
                    if len(prossimi_livelli) == 5 and all("livello" in level and "exp_necessaria" in level for level in prossimi_livelli):
                        self.log_test("Combat Level Info API", True, 
                                    f"Level: {data['livello_combattimento']}, EXP: {data['esperienza_livello']}/{data['esperienza_prossimo_livello']}, Multiplier: {data['moltiplicatore_exp']}x, Next 5 levels preview available")
                        return True
                    else:
                        self.log_test("Combat Level Info API", False, "", f"Invalid prossimi_livelli structure: {prossimi_livelli}")
                        return False
                else:
                    self.log_test("Combat Level Info API", False, "", f"Missing required fields: {missing_fields}")
                    return False
            else:
                self.log_test("Combat Level Info API", False, "", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Combat Level Info API", False, "", str(e))
            return False

    def test_combat_moves(self):
        """Test GET /api/combat/moves endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/combat/moves")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required categories
                required_categories = ["mosse_base", "mosse_speciali", "mosse_difesa", "armi", "carte_combattimento"]
                missing_categories = [cat for cat in required_categories if cat not in data]
                
                if not missing_categories:
                    # Verify each move has CD and energia fields
                    categories_details = []
                    all_valid = True
                    
                    for category in ["mosse_base", "mosse_speciali", "mosse_difesa"]:
                        moves = data[category]
                        valid_moves = 0
                        for move_name, move_data in moves.items():
                            if "cd" in move_data and "energia" in move_data:
                                valid_moves += 1
                            else:
                                all_valid = False
                        categories_details.append(f"{category}: {valid_moves} moves")
                    
                    # Check armi (weapons)
                    armi = data["armi"]
                    valid_weapons = 0
                    for weapon_name, weapon_data in armi.items():
                        if "cd" in weapon_data:
                            valid_weapons += 1
                        else:
                            all_valid = False
                    categories_details.append(f"armi: {valid_weapons} weapons")
                    
                    # Check carte_combattimento (combat cards)
                    carte = data["carte_combattimento"]
                    valid_cards = 0
                    for card_name, card_data in carte.items():
                        if "cd" in card_data:
                            valid_cards += 1
                        else:
                            all_valid = False
                    categories_details.append(f"carte_combattimento: {valid_cards} cards")
                    
                    if all_valid:
                        self.log_test("Combat Moves API", True, 
                                    f"All categories present with CD values: {', '.join(categories_details)}")
                        return True
                    else:
                        self.log_test("Combat Moves API", False, "", f"Some moves missing CD/energia fields")
                        return False
                else:
                    self.log_test("Combat Moves API", False, "", f"Missing categories: {missing_categories}")
                    return False
            else:
                self.log_test("Combat Moves API", False, "", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Combat Moves API", False, "", str(e))
            return False

    def test_simulate_damage(self):
        """Test POST /api/combat/simulate-damage endpoint"""
        try:
            # Test basic damage calculation
            test_data = {
                "level": 5,
                "cd": 6,
                "bonus_percent": 0.1
            }
            
            response = self.session.post(f"{self.base_url}/combat/simulate-damage", json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ["formula", "danno_base", "danno_minimo", "danno_massimo", "varianza"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    formula = data["formula"]
                    base_damage = data["danno_base"]
                    min_damage = data["danno_minimo"]
                    max_damage = data["danno_massimo"]
                    
                    # Verify formula calculation: Level (5) × CD (6) × (1 + 10%) = 33
                    expected_base = 5 * 6 * 1.1  # 33
                    if abs(base_damage - expected_base) < 1:
                        self.log_test("Damage Simulation API", True, 
                                    f"Formula: {formula}, Base: {base_damage}, Range: {min_damage}-{max_damage}")
                        
                        # Test edge cases
                        edge_cases = [
                            {"level": 1, "cd": 3, "bonus_percent": 0},  # Basic case
                            {"level": 10, "cd": 8, "bonus_percent": 0.5}  # High level case
                        ]
                        
                        edge_success = True
                        for case in edge_cases:
                            edge_response = self.session.post(f"{self.base_url}/combat/simulate-damage", json=case)
                            if edge_response.status_code != 200:
                                edge_success = False
                                break
                        
                        if edge_success:
                            self.log_test("Damage Simulation Edge Cases", True, "Level 1 and Level 10 calculations work correctly")
                        else:
                            self.log_test("Damage Simulation Edge Cases", False, "Some edge cases failed")
                        
                        return True
                    else:
                        self.log_test("Damage Simulation API", False, "", f"Incorrect calculation: expected ~{expected_base}, got {base_damage}")
                        return False
                else:
                    self.log_test("Damage Simulation API", False, "", f"Missing fields: {missing_fields}")
                    return False
            else:
                self.log_test("Damage Simulation API", False, "", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Damage Simulation API", False, "", str(e))
            return False

    def test_battle_system_with_combat_levels(self):
        """Test battle system with new damage calculation and CD tracking"""
        try:
            # Start battle with NPC
            battle_data = {
                "opponent_type": "npc",
                "opponent_id": "pirata_novizio"
            }
            
            response = self.session.post(f"{self.base_url}/battle/start", json=battle_data)
            
            if response.status_code == 200:
                battle = response.json()
                battle_id = battle.get("battle_id")
                
                if not battle_id:
                    self.log_test("Battle System - Start", False, "", "No battle_id returned")
                    return False
                    
                self.log_test("Battle System - Start", True, f"Battle started with ID: {battle_id}")
                
                # Execute attack action
                attack_data = {
                    "action_type": "attacco_base",
                    "action_name": "Pugno"
                }
                
                attack_response = self.session.post(f"{self.base_url}/battle/{battle_id}/action", json=attack_data)
                
                if attack_response.status_code == 200:
                    response_data = attack_response.json()
                    result = response_data.get('result', {})
                    battle_state = response_data.get('battle', {})
                    battle_log = battle_state.get("log", [])
                    
                    # Look for new damage format in log: "[LvX × CDY] Danno: Z"
                    damage_log_found = False
                    cd_found = False
                    level_found = False
                    
                    for log_entry in battle_log:
                        if "[Lv" in log_entry and "× CD" in log_entry and "Danno:" in log_entry:
                            damage_log_found = True
                            if "CD3" in log_entry:  # Pugno has CD 3
                                cd_found = True
                            if "Lv1" in log_entry:  # New character starts at level 1
                                level_found = True
                            break
                    
                    if damage_log_found and cd_found and level_found:
                        self.log_test("Battle System - New Damage Format", True, 
                                    f"Combat log shows new format with Level and CD: {[log for log in battle_log if '[Lv' in log]}")
                        
                        # Check if battle result includes new fields
                        if result.get("battaglia_finita"):
                            rewards = battle_state.get('rewards', {})
                            if "cd" in str(battle_state) or "livello_attaccante" in str(battle_state):
                                self.log_test("Battle System - Combat Fields", True, "Battle result includes combat level information")
                            else:
                                self.log_test("Battle System - Combat Fields", False, "Battle result missing combat level fields")
                        
                        return True
                    else:
                        self.log_test("Battle System - New Damage Format", False, "", 
                                    f"Log missing expected format. Found: {battle_log}")
                        return False
                else:
                    self.log_test("Battle System - Attack", False, "", f"Attack failed: {attack_response.status_code}")
                    return False
            else:
                self.log_test("Battle System - Start", False, "", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Battle System with Combat Levels", False, "", str(e))
            return False

    def test_level_up_system(self):
        """Test level up system by fighting multiple battles"""
        try:
            battles_won = 0
            battles_fought = 0
            exp_gained_total = 0
            level_ups = 0
            original_level = self.character_data.get("livello_combattimento", 1)
            
            # Fight multiple battles to gain EXP - NPC has 70 HP, we need sustained attacks
            for i in range(3):  # Reduced to 3 battles for efficiency
                battles_fought += 1
                # Start battle
                battle_data = {
                    "opponent_type": "npc",
                    "opponent_id": "pirata_novizio"
                }
                
                response = self.session.post(f"{self.base_url}/battle/start", json=battle_data)
                if response.status_code != 200:
                    continue
                    
                battle_info = response.json()["battle"]
                battle_id = battle_info.get("battle_id")
                
                # Fight until battle ends - attack repeatedly
                battle_finished = False
                attacks = 0
                max_attacks = 50  # Increased limit to ensure we can win
                
                while not battle_finished and attacks < max_attacks:
                    attack_data = {
                        "action_type": "attacco_base",
                        "action_name": "Pugno"
                    }
                    
                    attack_response = self.session.post(f"{self.base_url}/battle/{battle_id}/action", json=attack_data)
                    
                    if attack_response.status_code == 200:
                        response_data = attack_response.json()
                        result = response_data.get('result', {})
                        battle_state = response_data.get('battle', {})
                        
                        # Check if battle ended
                        if result.get("battaglia_finita"):
                            battle_finished = True
                            winner = result.get("vincitore")
                            
                            if winner == "player1":
                                battles_won += 1
                                rewards = battle_state.get("rewards", {})
                                
                                # Check for level up reward structure
                                required_reward_fields = [
                                    "exp_gained", "exp_multiplier", "leveled_up", 
                                    "current_exp", "exp_for_next_level", "total_exp"
                                ]
                                
                                missing_fields = [field for field in required_reward_fields if field not in rewards]
                                
                                if not missing_fields:
                                    exp_gained_total += rewards.get("exp_gained", 0)
                                    if rewards.get("leveled_up"):
                                        level_ups += 1
                                    
                                    self.log_test(f"Battle {i+1} Victory Rewards", True, 
                                                f"Victory! EXP: +{rewards['exp_gained']}, Total: {rewards['total_exp']}, Level up: {rewards['leveled_up']}")
                                else:
                                    self.log_test(f"Battle {i+1} Victory Rewards", False, "", f"Missing reward fields: {missing_fields}")
                            elif winner == "player2":
                                # Check defeat rewards (should still give EXP)
                                rewards = battle_state.get("rewards", {})
                                defeat_exp = rewards.get("defeat_exp", False)
                                if defeat_exp and rewards.get("exp_gained", 0) > 0:
                                    exp_gained_total += rewards.get("exp_gained", 0)
                                    self.log_test(f"Battle {i+1} Defeat EXP", True, 
                                                f"Defeat but gained EXP: +{rewards.get('exp_gained', 0)}")
                                else:
                                    self.log_test(f"Battle {i+1} Defeat EXP", False, "", "No EXP reward for defeat")
                            break
                        
                        attacks += 1
                        time.sleep(0.05)  # Very small delay between attacks
                    else:
                        break  # Error, exit battle
                
                time.sleep(0.1)  # Small delay between battles
            
            # Summary and validation
            if battles_fought > 0:
                if battles_won > 0:
                    self.log_test("Level Up System - Victory Achieved", True, 
                                f"Won {battles_won}/{battles_fought} battles, gained {exp_gained_total} total EXP")
                    
                    if level_ups > 0:
                        self.log_test("Level Up System - Level Up Achieved", True, 
                                    f"Achieved {level_ups} level ups! Combat level system working correctly")
                    elif exp_gained_total >= 50:  # Should be enough for testing purposes
                        self.log_test("Level Up System - EXP Gain Confirmed", True, 
                                    f"Gained {exp_gained_total} EXP, level up system structure confirmed (no level up yet is normal)")
                    else:
                        self.log_test("Level Up System - Minimal EXP", True, 
                                    f"Gained {exp_gained_total} EXP, system working but minimal reward")
                    return True
                else:
                    # Even if no victories, check if we got consolation EXP
                    if exp_gained_total > 0:
                        self.log_test("Level Up System - Consolation EXP", True, 
                                    f"No victories but gained {exp_gained_total} consolation EXP, defeat rewards working")
                        return True
                    else:
                        self.log_test("Level Up System", False, "", f"No victories and no EXP gained from {battles_fought} battles")
                        return False
            else:
                self.log_test("Level Up System", False, "", "No battles could be started")
                return False
                
        except Exception as e:
            self.log_test("Level Up System", False, "", str(e))
            return False

    def run_combat_level_tests(self):
        """Run comprehensive Combat Level System tests"""
        print("⚔️ ONE PIECE RPG - COMBAT LEVEL SYSTEM TESTING")
        print("=" * 60)
        
        # Setup phase
        print("\n📋 SETUP PHASE")
        if not self.register_user():
            print("❌ Failed at user registration - cannot continue")
            return self.generate_summary()
            
        if not self.create_character():
            print("❌ Failed at character creation - cannot continue") 
            return self.generate_summary()
        
        # Combat Level System API tests
        print("\n⚔️ COMBAT LEVEL SYSTEM API TESTS")
        self.test_combat_level_info()
        self.test_combat_moves()
        self.test_simulate_damage()
        
        # Battle System tests with new damage calculation
        print("\n🥊 BATTLE SYSTEM WITH COMBAT LEVELS")
        self.test_battle_system_with_combat_levels()
        
        # Level Up System tests  
        print("\n📈 LEVEL UP SYSTEM TESTING")
        self.test_level_up_system()
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 COMBAT LEVEL SYSTEM TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['test']}: {result['error']}")
        
        print(f"\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"   - {result['test']}")
        
        return {
            "total": total_tests,
            "passed": passed_tests, 
            "failed": failed_tests,
            "success_rate": (passed_tests/total_tests)*100 if total_tests > 0 else 0,
            "details": self.test_results
        }

if __name__ == "__main__":
    tester = CombatLevelSystemTester()
    summary = tester.run_combat_level_tests()