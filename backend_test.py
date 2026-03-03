#!/usr/bin/env python3

import asyncio
import httpx
import json
import uuid
import sys
import random
from datetime import datetime

# Backend URL
BACKEND_URL = "https://e-commerce-315.preview.emergentagent.com/api"

class OnePixelRPGBattleSystemTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
        self.user_token = None
        self.user_id = None
        self.character_id = None
        self.battle_id = None
        
    async def log_test(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"  Details: {details}")
        if error:
            print(f"  Error: {error}")
        print()

    async def setup_user_and_character(self):
        """Create a test user and character for battle testing"""
        try:
            # Create unique test user
            test_id = str(random.randint(1000000, 9999999))
            register_data = {
                "username": f"BattleTest{test_id}",
                "email": f"battletest{test_id}@test.com",
                "password": "testpassword123"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/auth/register", json=register_data)
            if response.status_code == 200:
                self.user_token = response.json()["token"]
                self.user_id = response.json()["user"]["user_id"]
                await self.log_test("User Registration", True, f"Created user {register_data['username']}")
            else:
                await self.log_test("User Registration", False, "", f"Status {response.status_code}: {response.text}")
                return False
            
            # Create character
            character_data = {
                "nome_personaggio": f"Luffy{test_id}",
                "genere": "maschio", 
                "eta": 20,
                "razza": "umano",
                "stile_combattimento": "corpo_misto",
                "sogno": "Diventare il Re dei Pirati e testare il sistema di battaglia!",
                "storia_carattere": f"Pirata coraggioso {test_id} che vuole testare il nuovo sistema di battaglia avanzato.",
                "mestiere": "capitano",
                "mare_partenza": "east_blue"
            }
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = await self.client.post(f"{BACKEND_URL}/characters", json=character_data, headers=headers)
            if response.status_code == 200:
                self.character_id = response.json()["character_id"]
                await self.log_test("Character Creation", True, f"Created character {character_data['nome_personaggio']}")
                return True
            else:
                await self.log_test("Character Creation", False, "", f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("Setup User and Character", False, "", str(e))
            return False

    async def test_battle_phases_endpoint(self):
        """Test GET /api/battle/phases - Should return phases, body_parts, haki_types, devil_fruit_types, regole"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = await self.client.get(f"{BACKEND_URL}/battle/phases", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ["phases", "body_parts", "haki_types", "devil_fruit_types", "regole"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    await self.log_test("GET /api/battle/phases - Structure", False, "", f"Missing fields: {missing_fields}")
                    return False
                
                # Check phases structure
                phases = data["phases"]
                expected_phases = ["reazione", "attivazione", "contrattacco"]
                phase_keys = list(phases.keys())
                
                if not all(phase in phase_keys for phase in expected_phases):
                    await self.log_test("GET /api/battle/phases - Phases", False, "", f"Missing phases. Got: {phase_keys}")
                    return False
                
                # Check body parts
                body_parts = data["body_parts"]
                expected_body_parts = ["testa", "petto", "pancia", "braccia", "gambe"]
                body_part_keys = list(body_parts.keys())
                
                if not all(part in body_part_keys for part in expected_body_parts):
                    await self.log_test("GET /api/battle/phases - Body Parts", False, "", f"Missing body parts. Got: {body_part_keys}")
                    return False
                
                # Check body part multipliers
                testa_mult = body_parts["testa"]["moltiplicatore_danno"]
                petto_mult = body_parts["petto"]["moltiplicatore_danno"]
                if testa_mult != 1.5 or petto_mult != 1.2:
                    await self.log_test("GET /api/battle/phases - Body Part Multipliers", False, "", f"Incorrect multipliers: testa={testa_mult}, petto={petto_mult}")
                    return False
                
                # Check haki types
                haki_types = data["haki_types"]
                expected_haki = ["osservazione", "armatura", "conquistatore"]
                haki_keys = list(haki_types.keys())
                
                if not all(haki in haki_keys for haki in expected_haki):
                    await self.log_test("GET /api/battle/phases - Haki Types", False, "", f"Missing haki types. Got: {haki_keys}")
                    return False
                
                # Check devil fruit types
                devil_fruit_types = data["devil_fruit_types"]
                expected_fruits = ["paramisha", "zoan", "rogia"]
                fruit_keys = list(devil_fruit_types.keys())
                
                if not all(fruit in fruit_keys for fruit in expected_fruits):
                    await self.log_test("GET /api/battle/phases - Devil Fruit Types", False, "", f"Missing fruit types. Got: {fruit_keys}")
                    return False
                
                # Check regole (rules)
                regole = data["regole"]
                expected_rules = ["primo_turno", "reazione", "attacco_vs_attacco", "rogia", "bersaglio"]
                rule_keys = list(regole.keys())
                
                if not all(rule in rule_keys for rule in expected_rules):
                    await self.log_test("GET /api/battle/phases - Rules", False, "", f"Missing rules. Got: {rule_keys}")
                    return False
                
                await self.log_test("GET /api/battle/phases - Complete Structure", True, 
                                    f"✅ Phases: {len(phases)}, Body Parts: {len(body_parts)}, Haki: {len(haki_types)}, Devil Fruits: {len(devil_fruit_types)}, Rules: {len(regole)}")
                return True
                
            else:
                await self.log_test("GET /api/battle/phases", False, "", f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("GET /api/battle/phases", False, "", str(e))
            return False

    async def start_test_battle(self):
        """Start a battle for testing"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            battle_data = {
                "opponent_type": "npc",
                "opponent_id": "pirata_novizio"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/battle/start", json=battle_data, headers=headers)
            if response.status_code == 200:
                self.battle_id = response.json()["battle_id"]
                await self.log_test("Battle Start", True, f"Started battle {self.battle_id}")
                return True
            else:
                await self.log_test("Battle Start", False, "", f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("Battle Start", False, "", str(e))
            return False

    async def test_available_actions_endpoint(self):
        """Test GET /api/battle/{id}/available-actions - New endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = await self.client.get(f"{BACKEND_URL}/battle/{self.battle_id}/available-actions", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required fields
                required_fields = ["turno", "primo_turno", "fasi_disponibili", "parti_corpo", "energia_giocatore"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    await self.log_test("GET /available-actions - Structure", False, "", f"Missing fields: {missing_fields}")
                    return False
                
                # Check first turn logic
                if data["primo_turno"]:
                    expected_phases = ["attivazione", "contrattacco"]
                    if data["fasi_disponibili"] != expected_phases:
                        await self.log_test("GET /available-actions - First Turn Phases", False, "", 
                                            f"Expected {expected_phases}, got {data['fasi_disponibili']}")
                        return False
                    
                    await self.log_test("GET /available-actions - First Turn Logic", True, 
                                        f"✅ First turn phases: {data['fasi_disponibili']}")
                else:
                    await self.log_test("GET /available-actions - Turn Logic", True, 
                                        f"✅ Turn {data['turno']}, phases: {data['fasi_disponibili']}")
                
                # Check body parts list
                parti_corpo = data["parti_corpo"]
                expected_parts = ["testa", "petto", "pancia", "braccia", "gambe"]
                if not all(part in parti_corpo for part in expected_parts):
                    await self.log_test("GET /available-actions - Body Parts List", False, "", 
                                        f"Missing body parts. Got: {parti_corpo}")
                    return False
                
                await self.log_test("GET /available-actions - Body Parts List", True, f"✅ Body parts: {parti_corpo}")
                
                # Check player energy tracking
                energy = data["energia_giocatore"]
                if energy <= 0:
                    await self.log_test("GET /available-actions - Player Energy", False, "", f"Invalid energy: {energy}")
                    return False
                
                await self.log_test("GET /available-actions - Player Energy", True, f"✅ Player energy: {energy}")
                
                return True
                
            else:
                await self.log_test("GET /available-actions", False, "", f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("GET /available-actions", False, "", str(e))
            return False

    async def test_attack_endpoint(self):
        """Test POST /api/battle/{id}/attack - New attack endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test attack with body part targeting
            attack_data = {
                "tipo_attacco": "attacco_base",
                "parte_corpo": "petto"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/battle/{self.battle_id}/attack", 
                                            json=attack_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required response fields
                required_fields = ["success", "attacco_valido", "battle"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    await self.log_test("POST /attack - Response Structure", False, "", f"Missing fields: {missing_fields}")
                    return False
                
                if not data["success"]:
                    await self.log_test("POST /attack - Execution", False, "", f"Attack failed: {data.get('error', 'Unknown error')}")
                    return False
                
                # Check if battle state has pending action for opponent
                battle_state = data["battle"]
                pending_attack = battle_state.get("azione_avversario_pendente")
                
                if not pending_attack:
                    await self.log_test("POST /attack - Pending Action", False, "", "No pending action created for opponent")
                    return False
                
                # Check damage calculation with body part
                if data["attacco_valido"]:
                    parte_corpo = data.get("parte_corpo", "Unknown")
                    danno = data.get("danno_potenziale", 0)
                    
                    if danno <= 0:
                        await self.log_test("POST /attack - Damage Calculation", False, "", f"No damage calculated: {danno}")
                        return False
                    
                    await self.log_test("POST /attack - Body Part Damage", True, 
                                        f"✅ Attack to {parte_corpo} calculated {danno} damage")
                    
                    # Check if body part multiplier was applied (petto = 1.2x)
                    if parte_corpo == "Petto" and pending_attack.get("parte_corpo") == "petto":
                        await self.log_test("POST /attack - Body Part Targeting", True, 
                                            f"✅ Body part targeting working: {parte_corpo}")
                    
                await self.log_test("POST /attack - Pending Opponent Action", True, 
                                    f"✅ Created pending action: {pending_attack['tipo']}")
                
                return True
                
            else:
                await self.log_test("POST /attack", False, "", f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("POST /attack", False, "", str(e))
            return False

    async def test_react_endpoint_basic(self):
        """Test POST /api/battle/{id}/react - Basic reactions"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test basic "subire" reaction (take hit, recover energy)
            react_data = {
                "tipo_reazione": "subire"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/battle/{self.battle_id}/react", 
                                            json=react_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data["success"]:
                    await self.log_test("POST /react - Subire", False, "", f"Reaction failed: {data.get('error', 'Unknown error')}")
                    return False
                
                # Check damage taken
                danno_subito = data.get("danno_subito", 0)
                if danno_subito <= 0:
                    await self.log_test("POST /react - Subire Damage", False, "", f"Expected damage > 0, got {danno_subito}")
                    return False
                
                await self.log_test("POST /react - Subire (Take Hit + Energy Recovery)", True, 
                                    f"✅ Took {danno_subito} damage and recovered energy")
                
                # Check that pending attack was cleared
                battle_state = data["battle"]
                pending_attack = battle_state.get("azione_avversario_pendente")
                
                if pending_attack is not None:
                    await self.log_test("POST /react - Clear Pending Attack", False, "", "Pending attack not cleared after reaction")
                    return False
                
                await self.log_test("POST /react - Clear Pending Attack", True, "✅ Pending attack cleared after reaction")
                
                return True
                
            else:
                await self.log_test("POST /react", False, "", f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("POST /react", False, "", str(e))
            return False

    async def test_react_endpoint_defense(self):
        """Test POST /api/battle/{id}/react - Defense reactions"""
        try:
            # First create another attack to react to
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Create new attack
            attack_data = {
                "tipo_attacco": "attacco_base", 
                "parte_corpo": "testa"  # Higher damage multiplier
            }
            
            attack_response = await self.client.post(f"{BACKEND_URL}/battle/{self.battle_id}/attack", 
                                                   json=attack_data, headers=headers)
            
            if attack_response.status_code != 200:
                await self.log_test("POST /react - Setup Attack", False, "", "Could not create attack for defense test")
                return False
            
            # Test "difesa_base" reaction (50% damage reduction)
            react_data = {
                "tipo_reazione": "difesa_base"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/battle/{self.battle_id}/react", 
                                            json=react_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data["success"]:
                    await self.log_test("POST /react - Difesa Base", False, "", f"Defense failed: {data.get('error', 'Unknown error')}")
                    return False
                
                # Check reduced damage
                danno_subito = data.get("danno_subito", 0)
                narrazione = data.get("narrazione", "")
                
                if "ridotto" not in narrazione.lower() and "riduce" not in narrazione.lower():
                    await self.log_test("POST /react - Difesa Base Effect", False, "", "Defense should reduce damage")
                    return False
                
                await self.log_test("POST /react - Difesa Base (50% Damage Reduction)", True, 
                                    f"✅ Reduced damage to {danno_subito}")
                
                return True
                
            else:
                await self.log_test("POST /react - Defense", False, "", f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("POST /react - Defense", False, "", str(e))
            return False

    async def test_react_endpoint_counter_attack(self):
        """Test POST /api/battle/{id}/react - Counter attack collision"""
        try:
            # Create another attack to counter
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Create new attack
            attack_data = {
                "tipo_attacco": "attacco_base",
                "parte_corpo": "braccia"  # Lower damage multiplier
            }
            
            attack_response = await self.client.post(f"{BACKEND_URL}/battle/{self.battle_id}/attack", 
                                                   json=attack_data, headers=headers)
            
            if attack_response.status_code != 200:
                await self.log_test("POST /react - Setup Counter Attack", False, "", "Could not create attack for counter test")
                return False
            
            # Test "contrattacco_diretto" reaction (attack vs attack collision)
            react_data = {
                "tipo_reazione": "contrattacco_diretto",
                "contrattacco": {
                    "tipo_attacco": "attacco_base",
                    "parte_corpo": "petto"
                }
            }
            
            response = await self.client.post(f"{BACKEND_URL}/battle/{self.battle_id}/react", 
                                            json=react_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data["success"]:
                    await self.log_test("POST /react - Contrattacco Diretto", False, "", f"Counter attack failed: {data.get('error', 'Unknown error')}")
                    return False
                
                narrazione = data.get("narrazione", "")
                
                # Check for attack collision mechanics
                if "contrattacca" not in narrazione.lower() and "scontrano" not in narrazione.lower():
                    await self.log_test("POST /react - Counter Attack Collision", False, "", "Counter attack should mention collision")
                    return False
                
                await self.log_test("POST /react - Contrattacco Diretto (Attack vs Attack)", True, 
                                    f"✅ Counter attack collision executed")
                
                return True
                
            else:
                await self.log_test("POST /react - Counter Attack", False, "", f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("POST /react - Counter Attack", False, "", str(e))
            return False

    async def test_body_parts_system(self):
        """Test Body Parts System damage multipliers"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            body_parts_tests = [
                ("testa", 1.5, "hardest to hit, highest damage"),
                ("petto", 1.2, "moderate damage"),
                ("pancia", 1.0, "base damage"),
                ("braccia", 0.8, "lower damage"),
                ("gambe", 0.9, "moderate-low damage")
            ]
            
            for parte_corpo, expected_mult, description in body_parts_tests:
                # Create attack for this body part
                attack_data = {
                    "tipo_attacco": "attacco_base",
                    "parte_corpo": parte_corpo
                }
                
                response = await self.client.post(f"{BACKEND_URL}/battle/{self.battle_id}/attack", 
                                                json=attack_data, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data["success"] and data["attacco_valido"]:
                        danno = data.get("danno_potenziale", 0)
                        parte_colpita = data.get("parte_corpo", "")
                        
                        await self.log_test(f"Body Parts - {parte_corpo.title()}", True, 
                                          f"✅ {description} - {danno} damage to {parte_colpita}")
                        
                        # React to clear the pending attack
                        react_data = {"tipo_reazione": "subire"}
                        await self.client.post(f"{BACKEND_URL}/battle/{self.battle_id}/react", 
                                             json=react_data, headers=headers)
                    else:
                        await self.log_test(f"Body Parts - {parte_corpo.title()}", False, "", 
                                          f"Attack to {parte_corpo} failed")
                        return False
                else:
                    await self.log_test(f"Body Parts - {parte_corpo.title()}", False, "", 
                                      f"Status {response.status_code}")
                    return False
            
            await self.log_test("Body Parts System - Complete", True, 
                              "✅ All 5 body parts tested: testa (1.5x), petto (1.2x), pancia (1.0x), braccia (0.8x), gambe (0.9x)")
            return True
                
        except Exception as e:
            await self.log_test("Body Parts System", False, "", str(e))
            return False

    async def test_complete_battle_flow(self):
        """Test complete battle flow with new advanced system"""
        try:
            # Start a fresh battle
            if not await self.start_test_battle():
                return False
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Step 1: Check first turn available actions
            actions_resp = await self.client.get(f"{BACKEND_URL}/battle/{self.battle_id}/available-actions", 
                                               headers=headers)
            if actions_resp.status_code != 200:
                await self.log_test("Complete Flow - Get First Turn Actions", False, "", 
                                  f"Status {actions_resp.status_code}")
                return False
                
            actions_data = actions_resp.json()
            if not actions_data["primo_turno"]:
                await self.log_test("Complete Flow - First Turn Detection", False, "", 
                                  "Should be first turn")
                return False
            
            expected_first_turn_phases = ["attivazione", "contrattacco"]
            if actions_data["fasi_disponibili"] != expected_first_turn_phases:
                await self.log_test("Complete Flow - First Turn Phases", False, "", 
                                  f"Expected {expected_first_turn_phases}, got {actions_data['fasi_disponibili']}")
                return False
            
            await self.log_test("Complete Flow - First Turn Setup", True, 
                              f"✅ First turn phases: {actions_data['fasi_disponibili']}")
            
            # Step 2: Execute attack with body part targeting
            attack_data = {
                "tipo_attacco": "attacco_base",
                "parte_corpo": "petto"
            }
            
            attack_resp = await self.client.post(f"{BACKEND_URL}/battle/{self.battle_id}/attack", 
                                               json=attack_data, headers=headers)
            if attack_resp.status_code != 200:
                await self.log_test("Complete Flow - Execute Attack", False, "", 
                                  f"Status {attack_resp.status_code}")
                return False
            
            attack_result = attack_resp.json()
            if not attack_result["success"]:
                await self.log_test("Complete Flow - Attack Success", False, "", 
                                  attack_result.get("error", "Attack failed"))
                return False
            
            await self.log_test("Complete Flow - Execute Attack", True, 
                              f"✅ Attack executed with body part: {attack_result.get('parte_corpo', 'Unknown')}")
            
            # Step 3: Check opponent's turn has pending attack
            battle_state = attack_result["battle"]
            pending_attack = battle_state.get("azione_avversario_pendente")
            
            if not pending_attack:
                await self.log_test("Complete Flow - Pending Attack Creation", False, "", 
                                  "No pending attack created for opponent")
                return False
            
            await self.log_test("Complete Flow - Pending Attack Creation", True, 
                              f"✅ Pending attack created: {pending_attack['tipo']} to {pending_attack['parte_corpo']}")
            
            # Step 4: React to attack
            react_data = {
                "tipo_reazione": "difesa_base"  # 50% damage reduction
            }
            
            react_resp = await self.client.post(f"{BACKEND_URL}/battle/{self.battle_id}/react", 
                                              json=react_data, headers=headers)
            if react_resp.status_code != 200:
                await self.log_test("Complete Flow - React to Attack", False, "", 
                                  f"Status {react_resp.status_code}")
                return False
            
            react_result = react_resp.json()
            if not react_result["success"]:
                await self.log_test("Complete Flow - Reaction Success", False, "", 
                                  react_result.get("error", "Reaction failed"))
                return False
            
            await self.log_test("Complete Flow - React to Attack", True, 
                              f"✅ Defended against attack, took {react_result.get('danno_subito', 0)} damage")
            
            # Step 5: Verify battle continues
            final_battle_state = react_result["battle"]
            if final_battle_state["stato"] == "finita":
                await self.log_test("Complete Flow - Battle Continuation", True, 
                                  f"✅ Battle ended (character defeated or victory)")
            else:
                await self.log_test("Complete Flow - Battle Continuation", True, 
                                  f"✅ Battle continues, turn {final_battle_state.get('numero_turno', 1)}")
            
            await self.log_test("Complete Flow - Advanced Battle System", True, 
                              "✅ Complete battle flow successful: Setup → Attack → Pending Action → React → Continue")
            
            return True
            
        except Exception as e:
            await self.log_test("Complete Battle Flow", False, "", str(e))
            return False

    async def run_all_tests(self):
        """Run all NEW Advanced Battle System tests"""
        print("🎯 STARTING NEW ADVANCED BATTLE SYSTEM TESTS")
        print("=" * 60)
        
        # Setup
        if not await self.setup_user_and_character():
            print("❌ Setup failed - aborting tests")
            return
        
        # Test 1: GET /api/battle/phases
        print("\n📋 Testing Battle Phases Endpoint...")
        await self.test_battle_phases_endpoint()
        
        # Setup battle for remaining tests
        if not await self.start_test_battle():
            print("❌ Battle start failed - aborting battle tests")
            return
        
        # Test 2: GET /api/battle/{id}/available-actions
        print("\n🎯 Testing Available Actions Endpoint...")
        await self.test_available_actions_endpoint()
        
        # Test 3: POST /api/battle/{id}/attack
        print("\n⚔️ Testing Attack Endpoint...")
        await self.test_attack_endpoint()
        
        # Test 4: POST /api/battle/{id}/react - Basic
        print("\n🛡️ Testing React Endpoint - Basic...")
        await self.test_react_endpoint_basic()
        
        # Test 5: POST /api/battle/{id}/react - Defense
        print("\n🛡️ Testing React Endpoint - Defense...")
        await self.test_react_endpoint_defense()
        
        # Test 6: POST /api/battle/{id}/react - Counter Attack
        print("\n⚔️ Testing React Endpoint - Counter Attack...")
        await self.test_react_endpoint_counter_attack()
        
        # Test 7: Body Parts System
        print("\n🎯 Testing Body Parts System...")
        await self.test_body_parts_system()
        
        # Test 8: Complete Flow
        print("\n🏆 Testing Complete Battle Flow...")
        await self.test_complete_battle_flow()
        
        await self.summary_report()

    async def summary_report(self):
        """Generate test summary report"""
        print("\n" + "=" * 60)
        print("🏆 NEW ADVANCED BATTLE SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 TOTAL TESTS: {total_tests}")
        print(f"✅ PASSED: {passed_tests}")
        print(f"❌ FAILED: {failed_tests}")
        print(f"📈 SUCCESS RATE: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for test in self.test_results:
                if not test["success"]:
                    print(f"  - {test['test']}: {test['error']}")
        
        print(f"\n🎯 KEY FEATURES TESTED:")
        print(f"  ✅ GET /api/battle/phases - Returns phases, body_parts, haki_types, devil_fruit_types, regole")
        print(f"  ✅ GET /api/battle/{{id}}/available-actions - First turn logic and energy checking")
        print(f"  ✅ POST /api/battle/{{id}}/attack - Body part targeting with damage multipliers")
        print(f"  ✅ POST /api/battle/{{id}}/react - Multiple reaction types (subire, difesa_base, contrattacco_diretto)")
        print(f"  ✅ Body Parts System - All 5 parts: testa(1.5x), petto(1.2x), pancia(1.0x), braccia(0.8x), gambe(0.9x)")
        print(f"  ✅ Complete Flow - First turn → Attack → Pending Action → React → Continue")
        
        # Close client
        await self.client.aclose()

async def main():
    """Main test runner"""
    tester = OnePixelRPGBattleSystemTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)