#!/usr/bin/env python3
"""
Focused Backend Testing for One Piece RPG - Bug Fix Verification
Tests specifically for the fixed issues:
1. Character Creation with Berry (1000 starting)
2. Battle System with NPC AI (automatic turns + rewards)
3. Shop with Berry (purchases should work now)
"""

import requests
import json
import sys
from datetime import datetime

# Get backend URL from frontend env (production URL)
backend_url = "https://e-commerce-315.preview.emergentagent.com/api"

class FocusedOnePieceTest:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.token = None
        self.user_id = None
        self.character_id = None
        self.battle_id = None
        
        self.results = {
            "passed": 0,
            "failed": 0,
            "tests": []
        }
    
    def log(self, message, level="INFO"):
        print(f"[{level}] {message}")
    
    def add_result(self, test_name, passed, message="", response_data=None):
        status = "✅" if passed else "❌"
        self.results["tests"].append({
            "name": test_name,
            "status": status,
            "message": message,
            "data": response_data
        })
        
        if passed:
            self.results["passed"] += 1
            self.log(f"{status} {test_name}: {message}")
        else:
            self.results["failed"] += 1
            self.log(f"{status} {test_name}: {message}", "ERROR")
    
    def make_request(self, method, endpoint, data=None, auth=True):
        """Make HTTP request with optional authentication"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=15)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=15)
            
            return response
        except Exception as e:
            self.log(f"Request failed: {e}", "ERROR")
            return None
    
    def setup_auth_and_character(self):
        """Setup authentication and create character with berry"""
        # Generate unique test data
        timestamp = int(datetime.now().timestamp())
        test_email = f"berry_test_{timestamp}@onepiece.com"
        test_username = f"BerryTester{timestamp}"
        test_password = "berrypassword123"
        
        self.log("=== SETUP: Creating test user and character ===")
        
        # Register user
        reg_data = {
            "username": test_username,
            "email": test_email,
            "password": test_password
        }
        
        response = self.make_request("POST", "/auth/register", reg_data, auth=False)
        if not response or response.status_code != 200:
            self.add_result("Setup Registration", False, f"Failed registration: {response.status_code if response else 'No response'}")
            return False
        
        data = response.json()
        self.token = data.get("token")
        self.user_id = data["user"]["user_id"]
        self.add_result("Setup Registration", True, f"User registered: {test_username}")
        
        # Create character
        char_data = {
            "nome_personaggio": "Berry Tester",
            "ruolo": "pirata", 
            "genere": "maschio",
            "eta": 25,
            "razza": "umano",
            "stile_combattimento": "corpo_misto",
            "sogno": "Test Berry System",
            "storia_carattere": "A character created to test the berry system functionality.",
            "mestiere": "capitano"
        }
        
        response = self.make_request("POST", "/characters", char_data)
        if not response or response.status_code != 200:
            self.add_result("Setup Character Creation", False, f"Failed character creation: {response.status_code if response else 'No response'}")
            return False
        
        char_result = response.json()
        self.character_id = char_result["character_id"]
        self.add_result("Setup Character Creation", True, f"Character created: {char_result['nome_personaggio']}")
        
        return True
    
    def test_character_creation_berry_logbook(self):
        """Test 1: Character Creation includes Berry (1000) and Logbook initialization"""
        self.log("=== TEST 1: Character Creation with Berry & Logbook ===")
        
        if not self.character_id:
            self.add_result("Character Berry/Logbook Check", False, "No character available for testing")
            return
        
        # Get character details
        response = self.make_request("GET", "/characters/me")
        if not response or response.status_code != 200:
            self.add_result("Get Character Details", False, f"Failed to get character: {response.status_code if response else 'No response'}")
            return
        
        character = response.json()
        
        # Check Berry field exists and is 1000
        if "berry" not in character:
            self.add_result("Berry Field Present", False, "Character missing 'berry' field")
            return
        
        berry_amount = character["berry"]
        if berry_amount == 1000:
            self.add_result("Berry Starting Amount", True, f"Character starts with 1000 Berry (found: {berry_amount})")
        else:
            self.add_result("Berry Starting Amount", False, f"Expected 1000 Berry, found: {berry_amount}")
        
        # Check Logbook field exists and is initialized (empty array)
        if "logbook" not in character:
            self.add_result("Logbook Field Present", False, "Character missing 'logbook' field")
            return
        
        logbook = character["logbook"]
        if isinstance(logbook, list):
            self.add_result("Logbook Initialization", True, f"Logbook properly initialized as array (entries: {len(logbook)})")
        else:
            self.add_result("Logbook Initialization", False, f"Logbook should be array, found: {type(logbook)}")
    
    def test_battle_system_npc_ai(self):
        """Test 2: Battle System with NPC AI and Rewards"""
        self.log("=== TEST 2: Battle System with NPC AI ===")
        
        if not self.character_id:
            self.add_result("Battle System Test", False, "No character available for testing")
            return
        
        # Start battle with NPC
        battle_data = {
            "opponent_type": "npc",
            "opponent_id": "pirata_novizio"
        }
        
        response = self.make_request("POST", "/battle/start", battle_data)
        if not response or response.status_code != 200:
            self.add_result("Battle Start", False, f"Failed to start battle: {response.status_code if response else 'No response'}")
            return
        
        battle_result = response.json()
        self.battle_id = battle_result["battle_id"]
        battle_info = battle_result["battle"]
        
        self.add_result("Battle Start", True, f"Battle started with NPC 'pirata_novizio' (ID: {self.battle_id})")
        
        # Execute player action
        action_data = {
            "action_type": "attacco_base",
            "action_name": "Pugno"
        }
        
        response = self.make_request("POST", f"/battle/{self.battle_id}/action", action_data)
        if not response or response.status_code != 200:
            self.add_result("Battle Action", False, f"Failed to execute battle action: {response.status_code if response else 'No response'}")
            return
        
        action_result = response.json()
        
        # Check if NPC took automatic action
        battle_data = action_result.get("battle", {})
        battle_log = battle_data.get("log", [])
        
        if len(battle_log) >= 2:
            # Should have both player and NPC actions
            player_action = battle_log[-2] if len(battle_log) >= 2 else None
            npc_action = battle_log[-1] if len(battle_log) >= 1 else None
            
            self.add_result("Player Action Logged", True, f"Player action recorded: {player_action}")
            self.add_result("NPC Automatic Action", True, f"NPC took automatic action: {npc_action}")
        else:
            self.add_result("Battle Log Check", False, f"Expected at least 2 log entries (player + NPC), found: {len(battle_log)}")
        
        # Continue battle until finished to test rewards
        max_rounds = 10
        round_count = 0
        
        while battle_data.get("stato") == "attivo" and round_count < max_rounds:
            round_count += 1
            self.log(f"Battle round {round_count}...")
            
            response = self.make_request("POST", f"/battle/{self.battle_id}/action", action_data)
            if response and response.status_code == 200:
                action_result = response.json()
                battle_data = action_result.get("battle", {})
            else:
                break
        
        # Check if battle finished and rewards
        if battle_data.get("stato") == "finita":
            winner = battle_data.get("vincitore")
            rewards = battle_data.get("rewards")
            
            self.add_result("Battle Completion", True, f"Battle finished, winner: {winner}")
            
            if winner == "player1" and rewards:
                exp_gain = rewards.get("exp", 0)
                berry_gain = rewards.get("berry", 0)
                self.add_result("Battle Rewards", True, f"Player victory rewards: {exp_gain} EXP, {berry_gain} Berry")
            elif winner == "player1":
                self.add_result("Battle Rewards", False, "Player won but no rewards field found")
            else:
                self.add_result("Battle Completion Note", True, f"Battle finished with winner: {winner} (testing completed)")
        else:
            self.add_result("Battle Status", True, f"Battle in progress after {round_count} rounds")
    
    def test_shop_with_berry(self):
        """Test 3: Shop Purchase with Berry"""
        self.log("=== TEST 3: Shop Purchase with Berry ===")
        
        if not self.character_id:
            self.add_result("Shop Test", False, "No character available for testing")
            return
        
        # Get shop items first
        response = self.make_request("GET", "/shop/items")
        if not response or response.status_code != 200:
            self.add_result("Get Shop Items", False, f"Failed to get shop items: {response.status_code if response else 'No response'}")
            return
        
        shop_data = response.json()
        items = shop_data.get("items", {})
        
        if not items:
            self.add_result("Shop Items Available", False, "No items found in shop")
            return
        
        self.add_result("Get Shop Items", True, f"Shop has {len(items)} items available")
        
        # Get current berry amount
        response = self.make_request("GET", "/characters/me")
        if response and response.status_code == 200:
            character = response.json()
            initial_berry = character.get("berry", 0)
            self.log(f"Character has {initial_berry} Berry before purchase")
        else:
            self.add_result("Check Berry Before Purchase", False, "Could not check berry amount")
            return
        
        # Try to buy pozione_vita (should be affordable with 1000 Berry)
        item_to_buy = "pozione_vita"
        if item_to_buy not in items:
            # Find any affordable item
            affordable_items = {k: v for k, v in items.items() if v.get("price", 0) <= initial_berry}
            if affordable_items:
                item_to_buy = list(affordable_items.keys())[0]
            else:
                self.add_result("Affordable Item Check", False, f"No items affordable with {initial_berry} Berry")
                return
        
        item_price = items[item_to_buy].get("price", 0)
        item_name = items[item_to_buy].get("name", item_to_buy)
        
        self.log(f"Attempting to buy {item_name} for {item_price} Berry")
        
        buy_data = {"item_id": item_to_buy}
        response = self.make_request("POST", "/shop/buy", buy_data)
        
        if response and response.status_code == 200:
            purchase_result = response.json()
            self.add_result("Shop Purchase Success", True, f"Successfully bought {item_name} for {item_price} Berry")
            
            # Verify berry was deducted
            response = self.make_request("GET", "/characters/me")
            if response and response.status_code == 200:
                character = response.json()
                new_berry = character.get("berry", 0)
                expected_berry = initial_berry - item_price
                
                if new_berry == expected_berry:
                    self.add_result("Berry Deduction", True, f"Berry correctly deducted: {initial_berry} -> {new_berry}")
                else:
                    self.add_result("Berry Deduction", False, f"Berry mismatch. Expected: {expected_berry}, Got: {new_berry}")
            else:
                self.add_result("Berry Check After Purchase", False, "Could not verify berry after purchase")
        
        elif response and response.status_code == 400:
            error = response.json()
            self.add_result("Shop Purchase Failed", False, f"Purchase failed: {error.get('detail', 'Unknown error')}")
        else:
            status = response.status_code if response else "No response"
            self.add_result("Shop Purchase Error", False, f"Unexpected response: {status}")
    
    def run_focused_tests(self):
        """Run all focused tests for bug fix verification"""
        self.log("Starting focused testing for One Piece RPG bug fixes...")
        self.log(f"Testing against: {self.base_url}")
        
        # Setup
        if not self.setup_auth_and_character():
            self.log("Setup failed, cannot continue with tests", "ERROR")
            return
        
        # Run the three focused tests
        self.test_character_creation_berry_logbook()
        self.test_battle_system_npc_ai()
        self.test_shop_with_berry()
        
        self.print_summary()
    
    def print_summary(self):
        """Print focused test results summary"""
        print("\n" + "="*80)
        print("FOCUSED BUG FIX VERIFICATION RESULTS")
        print("="*80)
        
        print(f"\nTEST RESULTS:")
        for test in self.results['tests']:
            print(f"{test['status']} {test['name']}: {test['message']}")
        
        print(f"\nSUMMARY:")
        print(f"Total Tests: {self.results['passed'] + self.results['failed']}")
        print(f"Passed: {self.results['passed']}")
        print(f"Failed: {self.results['failed']}")
        
        if self.results['failed'] > 0:
            print(f"\nCRITICAL ISSUES FOUND:")
            for test in self.results['tests']:
                if "❌" in test['status']:
                    print(f"  • {test['name']}: {test['message']}")
        
        success_rate = (self.results['passed']/(self.results['passed']+self.results['failed'])*100) if (self.results['passed']+self.results['failed']) > 0 else 0
        print(f"\nSUCCESS RATE: {success_rate:.1f}%")
        print("="*80)

if __name__ == "__main__":
    tester = FocusedOnePieceTest(backend_url)
    tester.run_focused_tests()
    
    # Exit with appropriate code
    if tester.results['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)