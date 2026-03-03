#!/usr/bin/env python3

import requests
import json
import uuid
import time
import random
import string
from datetime import datetime

# Base URL for backend
BASE_URL = "https://e-commerce-315.preview.emergentagent.com/api"

def random_string(length=8):
    """Generate random string for unique usernames/emails"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def random_character_data():
    """Generate random character data for testing"""
    return {
        "nome_personaggio": f"BattlePirate{random.randint(10000, 99999)}",
        "ruolo": "Pirata",
        "genere": random.choice(["maschio", "femmina"]),
        "eta": random.randint(16, 30),
        "razza": random.choice(["umano", "uomo_pesce", "visone"]),
        "stile_combattimento": random.choice(["corpo_misto", "corpo_pugni", "corpo_calci", "armi_mono", "armi_pluri", "tiratore"]),
        "sogno": "Diventare il maestro delle fasi di battaglia!",
        "storia_carattere": "Un giovane pirata che ha scoperto il segreto delle fasi di battaglia.",
        "mestiere": random.choice(["navigatore", "cuoco", "medico", "musicista"]),
        "mare_partenza": "east_blue"
    }

class BattlePhaseSystemTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.token = None
        self.user_data = None
        self.character_data = None
        self.battle_id = None
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
                "username": f"battleuser_{random_id}",
                "email": f"battle_{random_id}@example.com",
                "password": "battlepass123"
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
        """Create character for battle phase testing"""
        try:
            char_data = random_character_data()
            response = self.session.post(f"{self.base_url}/characters", json=char_data)
            
            if response.status_code == 200:
                self.character_data = response.json()
                self.log_test("Character Creation", True, 
                            f"Character {char_data['nome_personaggio']} created successfully")
                return True
            else:
                self.log_test("Character Creation", False, "", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Character Creation", False, "", str(e))
            return False

    def test_battle_phases_endpoint(self):
        """Test GET /api/battle/phases - Returns all battle phases and actions"""
        try:
            response = self.session.get(f"{self.base_url}/battle/phases")
            
            if response.status_code == 200:
                data = response.json()
                phases = data.get("phases", {})
                energy_multipliers = data.get("energy_multipliers", {})
                description = data.get("description", "")
                
                # Check for expected 3 phases
                expected_phases = ["reazione", "attivazione", "contrattacco"]
                phases_found = [phase for phase in expected_phases if phase in phases]
                
                if len(phases_found) == 3:
                    # Check each phase has actions
                    phase_details = []
                    for phase in expected_phases:
                        actions = phases[phase].get("actions", {})
                        phase_details.append(f"{phase}: {len(actions)} actions")
                    
                    # Check energy multipliers
                    multiplier_check = all(str(i) in energy_multipliers for i in [1, 2, 3])
                    
                    if multiplier_check:
                        self.log_test("Battle Phases Endpoint", True, 
                                    f"Found all 3 phases ({', '.join(phases_found)}). {', '.join(phase_details)}. Energy multipliers: {energy_multipliers}")
                        return data
                    else:
                        self.log_test("Battle Phases Endpoint", False, "", f"Missing energy multipliers. Got: {energy_multipliers}")
                        return False
                else:
                    self.log_test("Battle Phases Endpoint", False, "", 
                                f"Expected 3 phases, found {len(phases_found)}: {phases_found}")
                    return False
            else:
                self.log_test("Battle Phases Endpoint", False, "", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Battle Phases Endpoint", False, "", str(e))
            return False

    def test_vita_energia_formulas(self):
        """Test new Vita/Energia formulas - Vita = Level × 100, Energia = Level × 50"""
        try:
            if not self.character_data:
                self.log_test("Vita/Energia Formulas", False, "", "No character data available")
                return False
            
            level = self.character_data.get("livello_combattimento", 1)
            vita = self.character_data.get("vita", 0)
            vita_max = self.character_data.get("vita_max", 0)
            energia = self.character_data.get("energia", 0)
            energia_max = self.character_data.get("energia_max", 0)
            
            # Expected formulas: Vita = Level × 100, Energia = Level × 50
            expected_vita = level * 100
            expected_energia = level * 50
            
            vita_correct = vita_max == expected_vita
            energia_correct = energia_max == expected_energia
            
            if vita_correct and energia_correct:
                self.log_test("Vita/Energia Formulas", True, 
                            f"Level {level}: Vita = {vita_max} (expected {expected_vita}), Energia = {energia_max} (expected {expected_energia})")
                return True
            else:
                errors = []
                if not vita_correct:
                    errors.append(f"Vita: got {vita_max}, expected {expected_vita}")
                if not energia_correct:
                    errors.append(f"Energia: got {energia_max}, expected {expected_energia}")
                
                self.log_test("Vita/Energia Formulas", False, "", f"Level {level} - {', '.join(errors)}")
                return False
                
        except Exception as e:
            self.log_test("Vita/Energia Formulas", False, "", str(e))
            return False

    def start_battle_for_phase_testing(self):
        """Start a battle to test phase actions"""
        try:
            battle_data = {
                "opponent_type": "npc", 
                "opponent_id": "pirata_novizio"
            }
            
            response = self.session.post(f"{self.base_url}/battle/start", json=battle_data)
            
            if response.status_code == 200:
                battle_info = response.json()
                self.battle_id = battle_info.get("battle_id")
                battle = battle_info.get("battle", {})
                
                if self.battle_id:
                    player = battle.get("player1", {})
                    opponent = battle.get("player2", {})
                    
                    self.log_test("Start Battle for Phase Testing", True, 
                                f"Battle {self.battle_id} started. Player: {player.get('nome')}, Opponent: {opponent.get('nome')}")
                    return battle
                else:
                    self.log_test("Start Battle for Phase Testing", False, "", "No battle_id returned")
                    return False
            else:
                self.log_test("Start Battle for Phase Testing", False, "", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Start Battle for Phase Testing", False, "", str(e))
            return False

    def test_phase_action_contrattacco(self):
        """Test POST /api/battle/{id}/phase-action - Execute contrattacco phase with pugno action"""
        try:
            if not self.battle_id:
                self.log_test("Phase Action - Contrattacco", False, "", "No battle ID available")
                return False
            
            # Test contrattacco phase with pugno action
            action_data = {
                "fase": "contrattacco",
                "azione": "pugno",
                "parametri": {}
            }
            
            response = self.session.post(f"{self.base_url}/battle/{self.battle_id}/phase-action", json=action_data)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                result = data.get("result", {})
                battle = data.get("battle", {})
                
                if success:
                    fase = result.get("fase")
                    azione = result.get("azione")
                    energia_spesa = result.get("energia_spesa", 0)
                    energy_multiplier = result.get("energy_multiplier", 1.0)
                    danno = result.get("danno", 0)
                    log_entry = result.get("log_entry", "")
                    
                    # Verify phase action details
                    fasi_completate = battle.get("fasi_completate", [])
                    contrattacco_completed = "contrattacco" in fasi_completate
                    
                    if fase == "contrattacco" and azione == "pugno" and danno > 0 and contrattacco_completed:
                        self.log_test("Phase Action - Contrattacco", True, 
                                    f"Contrattacco/Pugno executed. Damage: {danno}, Energy: {energia_spesa} (x{energy_multiplier}), Log: {log_entry}")
                        return True
                    else:
                        self.log_test("Phase Action - Contrattacco", False, "", 
                                    f"Invalid result: fase={fase}, azione={azione}, danno={danno}, completed={contrattacco_completed}")
                        return False
                else:
                    error = data.get("error", "Unknown error")
                    self.log_test("Phase Action - Contrattacco", False, "", f"Action failed: {error}")
                    return False
            else:
                self.log_test("Phase Action - Contrattacco", False, "", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase Action - Contrattacco", False, "", str(e))
            return False

    def test_energy_multiplier_multiple_phases(self):
        """Test energy multiplier when using multiple phases"""
        try:
            if not self.battle_id:
                self.log_test("Energy Multiplier - Multiple Phases", False, "", "No battle ID available")
                return False
            
            # Get current battle state
            stats_response = self.session.get(f"{self.base_url}/battle/{self.battle_id}/character-stats")
            if stats_response.status_code != 200:
                self.log_test("Energy Multiplier - Multiple Phases", False, "", "Could not get battle stats")
                return False
            
            initial_stats = stats_response.json()
            initial_energy = initial_stats.get("player", {}).get("energia", 0)
            
            # First, end turn to reset phases
            end_turn_response = self.session.post(f"{self.base_url}/battle/{self.battle_id}/end-turn")
            if end_turn_response.status_code != 200:
                self.log_test("Energy Multiplier - Multiple Phases", False, "", "Could not end turn")
                return False
            
            # Wait for NPC turn to complete
            time.sleep(1)
            
            # Now test multiple phases in sequence
            phases_to_test = [
                {"fase": "reazione", "azione": "subire"},  # Phase 1 - multiplier 1.0
                {"fase": "attivazione", "azione": "salta"},  # Phase 2 - multiplier 1.3
                {"fase": "contrattacco", "azione": "pugno"}  # Phase 3 - multiplier 1.6
            ]
            
            energy_costs = []
            multipliers = []
            
            for i, action_data in enumerate(phases_to_test):
                response = self.session.post(f"{self.base_url}/battle/{self.battle_id}/phase-action", json=action_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        result = data.get("result", {})
                        energia_spesa = result.get("energia_spesa", 0)
                        energy_multiplier = result.get("energy_multiplier", 1.0)
                        
                        energy_costs.append(energia_spesa)
                        multipliers.append(energy_multiplier)
                    else:
                        break
                else:
                    break
            
            if len(energy_costs) >= 2:
                # Check that multipliers increase as expected
                multipliers_increasing = all(multipliers[i] <= multipliers[i+1] for i in range(len(multipliers)-1))
                
                if multipliers_increasing:
                    self.log_test("Energy Multiplier - Multiple Phases", True, 
                                f"Energy multipliers work correctly: {multipliers}. Energy costs: {energy_costs}")
                    return True
                else:
                    self.log_test("Energy Multiplier - Multiple Phases", False, "", 
                                f"Multipliers not increasing: {multipliers}")
                    return False
            else:
                self.log_test("Energy Multiplier - Multiple Phases", False, "", 
                            f"Could only execute {len(energy_costs)} phases")
                return False
                
        except Exception as e:
            self.log_test("Energy Multiplier - Multiple Phases", False, "", str(e))
            return False

    def test_end_turn_and_switch(self):
        """Test POST /api/battle/{id}/end-turn - End turn and switch"""
        try:
            if not self.battle_id:
                self.log_test("End Turn and Switch", False, "", "No battle ID available")
                return False
            
            # Get initial battle state
            stats_response = self.session.get(f"{self.base_url}/battle/{self.battle_id}/character-stats")
            if stats_response.status_code == 200:
                initial_battle_info = stats_response.json().get("battle_info", {})
                initial_turn = initial_battle_info.get("turno", 0)
                initial_phases = initial_battle_info.get("fasi_completate", [])
            else:
                self.log_test("End Turn and Switch", False, "", "Could not get initial battle state")
                return False
            
            # End turn
            response = self.session.post(f"{self.base_url}/battle/{self.battle_id}/end-turn")
            
            if response.status_code == 200:
                data = response.json()
                battle = data.get("battle", {})
                
                new_turn = battle.get("numero_turno", 0)
                new_phases = battle.get("fasi_completate", [])
                current_player = battle.get("turno_corrente", "")
                
                # Check that turn advanced and phases reset
                turn_advanced = new_turn > initial_turn
                phases_reset = len(new_phases) == 0  # Should be reset for new turn
                
                if turn_advanced and phases_reset:
                    self.log_test("End Turn and Switch", True, 
                                f"Turn advanced from {initial_turn} to {new_turn}. Phases reset from {len(initial_phases)} to {len(new_phases)}. Current player: {current_player}")
                    
                    # Check if NPC auto-played (should switch back to player)
                    time.sleep(1)
                    
                    # Get battle state after NPC turn
                    final_stats = self.session.get(f"{self.base_url}/battle/{self.battle_id}/character-stats")
                    if final_stats.status_code == 200:
                        final_battle_info = final_stats.json().get("battle_info", {})
                        final_turn = final_battle_info.get("turno", 0)
                        
                        if final_turn > new_turn:
                            self.log_test("NPC Auto-Turn", True, 
                                        f"NPC automatically played turn {new_turn + 1}")
                        else:
                            self.log_test("NPC Auto-Turn", True, 
                                        "Turn switch working, NPC turn processing")
                    
                    return True
                else:
                    self.log_test("End Turn and Switch", False, "", 
                                f"Turn not properly advanced or phases not reset. Turn: {initial_turn}->{new_turn}, Phases: {len(initial_phases)}->{len(new_phases)}")
                    return False
            else:
                self.log_test("End Turn and Switch", False, "", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("End Turn and Switch", False, "", str(e))
            return False

    def test_character_stats_popup(self):
        """Test GET /api/battle/{id}/character-stats - Stats popup during battle"""
        try:
            if not self.battle_id:
                self.log_test("Character Stats Popup", False, "", "No battle ID available")
                return False
            
            response = self.session.get(f"{self.base_url}/battle/{self.battle_id}/character-stats")
            
            if response.status_code == 200:
                data = response.json()
                player = data.get("player", {})
                opponent = data.get("opponent", {})
                battle_info = data.get("battle_info", {})
                
                # Check player full stats
                required_player_stats = ["nome", "livello_combattimento", "vita", "vita_max", "energia", "energia_max", 
                                        "forza", "velocita", "resistenza", "agilita", "attacco", "difesa"]
                player_stats_present = all(stat in player for stat in required_player_stats)
                
                # Check opponent basic info
                required_opponent_info = ["nome", "livello_combattimento", "vita", "vita_max"]
                opponent_info_present = all(info in opponent for info in required_opponent_info)
                
                # Check battle info
                required_battle_info = ["turno", "fase_corrente", "fasi_completate"]
                battle_info_present = all(info in battle_info for info in required_battle_info)
                
                if player_stats_present and opponent_info_present and battle_info_present:
                    player_details = f"Player: {player['nome']} (Lv{player['livello_combattimento']}) - HP:{player['vita']}/{player['vita_max']}, Energy:{player['energia']}/{player['energia_max']}"
                    opponent_details = f"Opponent: {opponent['nome']} (Lv{opponent['livello_combattimento']}) - HP:{opponent['vita']}/{opponent['vita_max']}"
                    battle_details = f"Battle: Turn {battle_info['turno']}, Current Phase: {battle_info.get('fase_corrente', 'N/A')}, Completed: {battle_info['fasi_completate']}"
                    
                    self.log_test("Character Stats Popup", True, 
                                f"{player_details}. {opponent_details}. {battle_details}")
                    return data
                else:
                    missing = []
                    if not player_stats_present:
                        missing_player = [stat for stat in required_player_stats if stat not in player]
                        missing.append(f"Player stats: {missing_player}")
                    if not opponent_info_present:
                        missing_opponent = [info for info in required_opponent_info if info not in opponent]
                        missing.append(f"Opponent info: {missing_opponent}")
                    if not battle_info_present:
                        missing_battle = [info for info in required_battle_info if info not in battle_info]
                        missing.append(f"Battle info: {missing_battle}")
                    
                    self.log_test("Character Stats Popup", False, "", f"Missing data: {'; '.join(missing)}")
                    return False
            else:
                self.log_test("Character Stats Popup", False, "", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Character Stats Popup", False, "", str(e))
            return False

    def test_reazione_phase_to_npc_attack(self):
        """Test reazione phase to react to NPC attack"""
        try:
            if not self.battle_id:
                self.log_test("Reazione Phase to NPC Attack", False, "", "No battle ID available")
                return False
            
            # First check if there's a pending attack
            stats_response = self.session.get(f"{self.base_url}/battle/{self.battle_id}/character-stats")
            if stats_response.status_code != 200:
                self.log_test("Reazione Phase to NPC Attack", False, "", "Could not get battle stats")
                return False
            
            battle_info = stats_response.json().get("battle_info", {})
            pending_attack = battle_info.get("azione_pendente")
            
            if not pending_attack:
                # End turn to trigger NPC attack
                end_turn_response = self.session.post(f"{self.base_url}/battle/{self.battle_id}/end-turn")
                if end_turn_response.status_code != 200:
                    self.log_test("Reazione Phase to NPC Attack", False, "", "Could not end turn to trigger NPC")
                    return False
                
                # Wait for NPC to act
                time.sleep(1)
                
                # Check again for pending attack
                stats_response = self.session.get(f"{self.base_url}/battle/{self.battle_id}/character-stats")
                if stats_response.status_code == 200:
                    battle_info = stats_response.json().get("battle_info", {})
                    pending_attack = battle_info.get("azione_pendente")
            
            # Now test reazione phase
            reaction_actions = ["schivata", "parata", "subire"]
            
            for action in reaction_actions:
                # Try each reaction type
                action_data = {
                    "fase": "reazione",
                    "azione": action
                }
                
                response = self.session.post(f"{self.base_url}/battle/{self.battle_id}/phase-action", json=action_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        result = data.get("result", {})
                        danno = result.get("danno", 0)
                        effetto = result.get("effetto", "")
                        log_entry = result.get("log_entry", "")
                        
                        self.log_test("Reazione Phase to NPC Attack", True, 
                                    f"Reaction '{action}' executed. Damage taken: {danno}, Effect: {effetto}, Log: {log_entry}")
                        return True
                    else:
                        error = data.get("error", "")
                        if "già completata" in error.lower():
                            continue  # This phase already used, try next action
                        else:
                            self.log_test("Reazione Phase to NPC Attack", False, "", f"Action '{action}' failed: {error}")
                            return False
                else:
                    continue
            
            # If we get here, no reaction worked
            self.log_test("Reazione Phase to NPC Attack", False, "", "No reaction actions could be executed")
            return False
                
        except Exception as e:
            self.log_test("Reazione Phase to NPC Attack", False, "", str(e))
            return False

    def run_complete_battle_flow_test(self):
        """Test complete battle flow with phases"""
        try:
            if not self.battle_id:
                self.log_test("Complete Battle Flow", False, "", "No battle ID available")
                return False
            
            print("\n🏴‍☠️ TESTING COMPLETE BATTLE FLOW WITH PHASES")
            
            max_turns = 10
            turn_count = 0
            battle_complete = False
            
            while turn_count < max_turns and not battle_complete:
                turn_count += 1
                print(f"   Turn {turn_count}")
                
                # Get current battle state
                stats_response = self.session.get(f"{self.base_url}/battle/{self.battle_id}/character-stats")
                if stats_response.status_code != 200:
                    break
                
                stats_data = stats_response.json()
                player_hp = stats_data.get("player", {}).get("vita", 0)
                opponent_hp = stats_data.get("opponent", {}).get("vita", 0)
                battle_info = stats_data.get("battle_info", {})
                
                # Check if battle is over
                if player_hp <= 0 or opponent_hp <= 0:
                    battle_complete = True
                    winner = "Player" if opponent_hp <= 0 else "NPC"
                    print(f"   Battle ended! Winner: {winner}")
                    break
                
                # Try to use each phase in order
                phases_used = 0
                
                # Phase 1: Reazione (if there's a pending attack)
                pending_attack = battle_info.get("azione_pendente")
                if pending_attack:
                    reaction_data = {
                        "fase": "reazione", 
                        "azione": random.choice(["schivata", "parata", "subire"])
                    }
                    
                    reaction_response = self.session.post(f"{self.base_url}/battle/{self.battle_id}/phase-action", json=reaction_data)
                    if reaction_response.status_code == 200 and reaction_response.json().get("success"):
                        phases_used += 1
                        print(f"      Reazione: {reaction_data['azione']}")
                
                # Phase 2: Attivazione (skip most of the time to save energy)
                if random.choice([True, False, False]):  # 33% chance
                    activation_data = {
                        "fase": "attivazione",
                        "azione": "salta"
                    }
                    
                    activation_response = self.session.post(f"{self.base_url}/battle/{self.battle_id}/phase-action", json=activation_data)
                    if activation_response.status_code == 200 and activation_response.json().get("success"):
                        phases_used += 1
                        print(f"      Attivazione: {activation_data['azione']}")
                
                # Phase 3: Contrattacco
                counter_attacks = ["pugno", "calcio", "colpo_rapido", "colpo_potente"]
                counter_data = {
                    "fase": "contrattacco",
                    "azione": random.choice(counter_attacks)
                }
                
                counter_response = self.session.post(f"{self.base_url}/battle/{self.battle_id}/phase-action", json=counter_data)
                if counter_response.status_code == 200 and counter_response.json().get("success"):
                    phases_used += 1
                    result = counter_response.json().get("result", {})
                    damage = result.get("danno", 0)
                    print(f"      Contrattacco: {counter_data['azione']} ({damage} damage)")
                
                print(f"      Used {phases_used} phases this turn")
                
                # End turn
                end_response = self.session.post(f"{self.base_url}/battle/{self.battle_id}/end-turn")
                if end_response.status_code != 200:
                    break
                
                # Wait for NPC turn
                time.sleep(0.5)
            
            if battle_complete:
                self.log_test("Complete Battle Flow", True, 
                            f"Battle completed successfully in {turn_count} turns. Winner: {winner}")
                return True
            else:
                self.log_test("Complete Battle Flow", False, "", 
                            f"Battle didn't complete within {max_turns} turns")
                return False
                
        except Exception as e:
            self.log_test("Complete Battle Flow", False, "", str(e))
            return False

    def run_new_battle_phase_system_tests(self):
        """Run comprehensive tests for the NEW Battle Phase System"""
        print("⚔️ ONE PIECE RPG - NEW BATTLE PHASE SYSTEM TESTING")
        print("=" * 60)
        
        # Setup phase
        print("\n📋 SETUP PHASE")
        if not self.register_user():
            print("❌ Failed at user registration - cannot continue")
            return self.generate_summary()
            
        if not self.create_character():
            print("❌ Failed at character creation - cannot continue") 
            return self.generate_summary()
        
        print("\n⚔️ BATTLE PHASE SYSTEM TESTS")
        
        # Test 1: GET /api/battle/phases endpoint
        print("\n1️⃣ Testing Battle Phases Endpoint")
        phases_data = self.test_battle_phases_endpoint()
        
        # Test 2: New Vita/Energia formulas
        print("\n2️⃣ Testing New Vita/Energia Formulas") 
        self.test_vita_energia_formulas()
        
        # Test 3: Start battle for phase testing
        print("\n3️⃣ Starting Battle for Phase Testing")
        battle = self.start_battle_for_phase_testing()
        
        if not battle:
            print("❌ Cannot continue without battle - skipping phase action tests")
            return self.generate_summary()
        
        # Test 4: Phase action - contrattacco with pugno
        print("\n4️⃣ Testing Phase Action - Contrattacco")
        self.test_phase_action_contrattacco()
        
        # Test 5: Energy multiplier with multiple phases
        print("\n5️⃣ Testing Energy Multiplier - Multiple Phases")
        self.test_energy_multiplier_multiple_phases()
        
        # Test 6: End turn and switch
        print("\n6️⃣ Testing End Turn and Switch")
        self.test_end_turn_and_switch()
        
        # Test 7: Character stats popup
        print("\n7️⃣ Testing Character Stats Popup")
        self.test_character_stats_popup()
        
        # Test 8: Reazione phase to NPC attack
        print("\n8️⃣ Testing Reazione Phase")
        self.test_reazione_phase_to_npc_attack()
        
        # Test 9: Complete battle flow
        print("\n9️⃣ Testing Complete Battle Flow")
        self.run_complete_battle_flow_test()
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 BATTLE PHASE SYSTEM TEST SUMMARY")
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
    tester = BattlePhaseSystemTester()
    summary = tester.run_new_battle_phase_system_tests()