#!/usr/bin/env python3

import requests
import json
import uuid
import random
import string

# Base URL for backend
BASE_URL = "https://saved-check.preview.emergentagent.com/api"

def random_string(length=8):
    """Generate random string for unique usernames/emails"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def random_character_data():
    """Generate random character data for testing"""
    return {
        "nome_personaggio": f"TestPirate{random.randint(10000, 99999)}",
        "ruolo": "Pirata",
        "genere": random.choice(["maschio", "femmina"]),
        "eta": random.randint(16, 30),
        "razza": random.choice(["umano", "uomo_pesce", "visone"]),
        "stile_combattimento": random.choice(["corpo_misto", "corpo_pugni", "corpo_calci", "armi_mono", "armi_pluri", "tiratore"]),
        "sogno": "Diventare il Re dei Pirati!",
        "storia_carattere": "Un giovane pirata con grandi ambizioni di esplorare il Grand Line.",
        "mestiere": random.choice(["navigatore", "cuoco", "medico", "musicista"]),
        "mare_partenza": "east_blue"
    }

class SimpleAbilityPointsTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.token = None
        self.user_data = None
        self.character_data = None
        
    def register_and_create_character(self):
        """Setup: register user and create character"""
        try:
            # Register
            random_id = random_string()
            user_data = {
                "username": f"testuser_{random_id}",
                "email": f"test_{random_id}@example.com",
                "password": "testpassword123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/register", json=user_data)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                self.user_data = user_data
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                print(f"✅ User {user_data['username']} registered successfully")
            else:
                print(f"❌ Registration failed: {response.status_code}, {response.text}")
                return False
            
            # Create character
            char_data = random_character_data()
            char_response = self.session.post(f"{self.base_url}/characters", json=char_data)
            
            if char_response.status_code == 200:
                self.character_data = char_response.json()
                print(f"✅ Character {char_data['nome_personaggio']} created successfully")
                
                # Check new ability fields
                punti_disponibili = self.character_data.get("punti_abilita_disponibili", "NOT_FOUND")
                punti_totali = self.character_data.get("punti_abilita_totali", "NOT_FOUND")
                attacco = self.character_data.get("attacco", 0)
                difesa = self.character_data.get("difesa", 0)
                forza = self.character_data.get("forza", 0)
                velocita = self.character_data.get("velocita", 0)
                resistenza = self.character_data.get("resistenza", 0)
                agilita = self.character_data.get("agilita", 0)
                
                print(f"📊 Character Stats:")
                print(f"   punti_abilita_disponibili: {punti_disponibili}")
                print(f"   punti_abilita_totali: {punti_totali}")
                print(f"   Attacco: {attacco} (should be Forza {forza} + Velocità {velocita} = {forza + velocita})")
                print(f"   Difesa: {difesa} (should be Resistenza {resistenza} + Agilità {agilita} = {resistenza + agilita})")
                
                # Verify calculations
                if attacco == forza + velocita and difesa == resistenza + agilita:
                    print("✅ Attack/Defense calculations correct (SUM not multiplication)")
                else:
                    print("❌ Attack/Defense calculations wrong")
                
                return True
            else:
                print(f"❌ Character creation failed: {char_response.status_code}, {char_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False

    def test_ability_points_status(self):
        """Test GET /api/ability-points/status endpoint"""
        try:
            print("\n🔍 Testing GET /api/ability-points/status")
            response = self.session.get(f"{self.base_url}/ability-points/status")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Status endpoint works!")
                
                # Print the full response for analysis
                print(f"📊 Full Response:")
                print(json.dumps(data, indent=2))
                
                # Check structure
                required_fields = ["punti_disponibili", "punti_totali", "abilita_attuali", "stats_derivati", "formula_info"]
                missing = [f for f in required_fields if f not in data]
                
                if missing:
                    print(f"❌ Missing fields: {missing}")
                    return False
                else:
                    print("✅ All required fields present")
                    
                    # Verify formulas
                    formulas = data.get("formula_info", {})
                    attacco_formula = formulas.get("attacco", "")
                    difesa_formula = formulas.get("difesa", "")
                    
                    if attacco_formula == "Forza + Velocità" and difesa_formula == "Resistenza + Agilità":
                        print("✅ Formulas correct")
                        
                        # Verify calculations
                        abilita = data.get("abilita_attuali", {})
                        stats = data.get("stats_derivati", {})
                        
                        expected_attacco = abilita.get("forza", 0) + abilita.get("velocita", 0)
                        expected_difesa = abilita.get("resistenza", 0) + abilita.get("agilita", 0)
                        
                        if (stats.get("attacco") == expected_attacco and 
                            stats.get("difesa") == expected_difesa):
                            print("✅ Calculations verified")
                            return True
                        else:
                            print(f"❌ Calculation mismatch: Expected A:{expected_attacco}, D:{expected_difesa}, Got A:{stats.get('attacco')}, D:{stats.get('difesa')}")
                            return False
                    else:
                        print(f"❌ Wrong formulas: Attacco='{attacco_formula}', Difesa='{difesa_formula}'")
                        return False
                        
            else:
                print(f"❌ Status endpoint failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Status test failed: {e}")
            return False

    def test_ability_points_distribute(self):
        """Test POST /api/ability-points/distribute endpoint"""
        try:
            print("\n🎯 Testing POST /api/ability-points/distribute")
            
            # Test with no points (should work)
            zero_distribution = {"forza": 0, "velocita": 0, "resistenza": 0, "agilita": 0}
            response = self.session.post(f"{self.base_url}/ability-points/distribute", json=zero_distribution)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Zero distribution works!")
                print(f"Response: {data.get('message', '')}")
                
                # Test with excessive points (should fail)
                excessive_distribution = {"forza": 999, "velocita": 999, "resistenza": 0, "agilita": 0}
                excessive_response = self.session.post(f"{self.base_url}/ability-points/distribute", json=excessive_distribution)
                
                if excessive_response.status_code == 400:
                    print("✅ Excessive distribution correctly rejected")
                    error_data = excessive_response.json()
                    print(f"Error message: {error_data.get('detail', '')}")
                    return True
                else:
                    print(f"❌ Excessive distribution should fail but got {excessive_response.status_code}")
                    return False
            else:
                print(f"❌ Distribution endpoint failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Distribution test failed: {e}")
            return False

    def test_single_battle(self):
        """Test a single battle to see if ability points are awarded"""
        try:
            print("\n⚔️ Testing Battle for Ability Points")
            
            # Start battle
            battle_data = {"opponent_type": "npc", "opponent_id": "pirata_novizio"}
            response = self.session.post(f"{self.base_url}/battle/start", json=battle_data)
            
            if response.status_code == 200:
                battle_info = response.json()
                battle_id = battle_info.get("battle_id")
                battle = battle_info.get("battle", {})
                
                print(f"✅ Battle started: {battle_id}")
                
                # Show initial state
                player = battle.get("player1", {})
                enemy = battle.get("player2", {})
                
                print(f"   Player: {player.get('nome', '')} (Lv{player.get('livello_combattimento', 1)}, HP:{player.get('vita', 0)})")
                print(f"   Enemy: {enemy.get('nome', '')} (Lv{enemy.get('livello_combattimento', 1)}, HP:{enemy.get('vita', 0)})")
                
                # Execute powerful attacks to finish quickly
                for attempt in range(20):  # More attempts
                    action_data = {"action_type": "attacco_speciale", "action_name": "Combo Devastante"}
                    
                    action_response = self.session.post(f"{self.base_url}/battle/{battle_id}/action", json=action_data)
                    
                    if action_response.status_code == 200:
                        action_result = action_response.json()
                        battle = action_result.get("battle", {})
                        
                        if battle.get("stato") == "finita":
                            # Battle finished!
                            rewards = battle.get("rewards", {})
                            vincitore = battle.get("vincitore")
                            ability_points = rewards.get("ability_points_earned", 0)
                            formula = rewards.get("ability_points_formula", "")
                            
                            print(f"✅ Battle finished! Winner: {vincitore}")
                            print(f"   Ability Points Earned: {ability_points}")
                            print(f"   Formula: {formula}")
                            print(f"   All Rewards: {json.dumps(rewards, indent=2)}")
                            
                            if ability_points > 0:
                                return True
                            elif vincitore == "player2":
                                print("ℹ️  Lost battle - consolation points may be 0")
                                return True
                            else:
                                print("❌ Won battle but no ability points awarded")
                                return False
                        else:
                            # Battle continues
                            current_player_hp = battle.get("player1", {}).get("vita", 0)
                            current_enemy_hp = battle.get("player2", {}).get("vita", 0)
                            
                            if attempt < 3:  # Only show first few
                                print(f"   Round {attempt+1}: Player HP {current_player_hp}, Enemy HP {current_enemy_hp}")
                    else:
                        print(f"❌ Battle action failed: {action_response.status_code}")
                        return False
                
                print("❌ Battle didn't finish in 20 rounds")
                return False
                
            else:
                print(f"❌ Battle start failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Battle test failed: {e}")
            return False

    def run_tests(self):
        """Run all ability points tests"""
        print("💪 SIMPLE ABILITY POINTS SYSTEM TEST")
        print("=" * 50)
        
        success_count = 0
        total_tests = 4
        
        # Test 1: Setup
        print("1. Setup (Register + Create Character)")
        if self.register_and_create_character():
            success_count += 1
        
        # Test 2: Status endpoint
        print("\n2. Ability Points Status Endpoint")
        if self.test_ability_points_status():
            success_count += 1
        
        # Test 3: Distribution endpoint
        print("\n3. Ability Points Distribution Endpoint")
        if self.test_ability_points_distribute():
            success_count += 1
        
        # Test 4: Battle for points
        print("\n4. Battle System with Ability Points")
        if self.test_single_battle():
            success_count += 1
        
        # Final status check
        print("\n5. Final Status Check")
        final_status = self.test_ability_points_status()
        
        print(f"\n📊 SUMMARY")
        print("=" * 50)
        print(f"Tests Passed: {success_count}/{total_tests}")
        print(f"Success Rate: {(success_count/total_tests)*100:.1f}%")

if __name__ == "__main__":
    tester = SimpleAbilityPointsTester()
    tester.run_tests()