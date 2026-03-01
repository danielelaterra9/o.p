#!/usr/bin/env python3
"""
Backend API Testing for One Piece RPG - The Grand Line Architect
Tests all backend endpoints according to the review request sequence
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
backend_url = "https://project-builder-127.preview.emergentagent.com/api"

class OnePointAPITester:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.token = None
        self.user_id = None
        self.character_id = None
        self.crew_id = None
        self.battle_id = None
        
        self.results = {
            "passed": 0,
            "failed": 0,
            "tests": []
        }
    
    def log(self, message, level="INFO"):
        print(f"[{level}] {message}")
    
    def add_result(self, test_name, passed, message="", response=None):
        status = "PASS" if passed else "FAIL" 
        self.results["tests"].append({
            "name": test_name,
            "status": status,
            "message": message,
            "response": response
        })
        
        if passed:
            self.results["passed"] += 1
            self.log(f"✅ {test_name} - {message}")
        else:
            self.results["failed"] += 1
            self.log(f"❌ {test_name} - {message}", "ERROR")
    
    def make_request(self, method, endpoint, data=None, auth=True):
        """Make HTTP request with optional authentication"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            
            return response
        except Exception as e:
            self.log(f"Request failed: {e}", "ERROR")
            return None
    
    def test_health_check(self):
        """Test 1: Health Check"""
        self.log("Testing health check endpoint...")
        
        response = self.make_request("GET", "/health", auth=False)
        if response and response.status_code == 200:
            data = response.json()
            if "status" in data and data["status"] == "healthy":
                self.add_result("Health Check", True, "API is healthy", data)
            else:
                self.add_result("Health Check", False, f"Unexpected response format: {data}")
        else:
            status = response.status_code if response else "No response"
            self.add_result("Health Check", False, f"Failed with status: {status}")
    
    def test_auth_flow(self):
        """Test 2: Authentication Flow"""
        # Generate unique test data
        timestamp = int(datetime.now().timestamp())
        test_email = f"test_pirate_{timestamp}@onepiece.com"
        test_username = f"TestPirate{timestamp}"
        test_password = "strongpassword123"
        
        # Test Registration
        self.log("Testing user registration...")
        reg_data = {
            "username": test_username,
            "email": test_email,
            "password": test_password
        }
        
        response = self.make_request("POST", "/auth/register", reg_data, auth=False)
        if response and response.status_code == 200:
            data = response.json()
            if "token" in data and "user" in data:
                self.token = data["token"]
                self.user_id = data["user"]["user_id"]
                self.add_result("User Registration", True, f"User created: {data['user']['username']}", data)
            else:
                self.add_result("User Registration", False, f"Missing token/user in response: {data}")
        else:
            status = response.status_code if response else "No response"
            error = response.json() if response else "No response"
            self.add_result("User Registration", False, f"Failed with status {status}: {error}")
            return
        
        # Test Login
        self.log("Testing user login...")
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        response = self.make_request("POST", "/auth/login", login_data, auth=False)
        if response and response.status_code == 200:
            data = response.json()
            if "token" in data:
                new_token = data["token"]
                self.add_result("User Login", True, f"Login successful, token received", data)
                # Use the new token
                self.token = new_token
            else:
                self.add_result("User Login", False, f"No token in login response: {data}")
        else:
            status = response.status_code if response else "No response"
            error = response.json() if response else "No response"
            self.add_result("User Login", False, f"Failed with status {status}: {error}")
        
        # Test Get Current User
        self.log("Testing get current user...")
        response = self.make_request("GET", "/auth/me")
        if response and response.status_code == 200:
            data = response.json()
            if "user_id" in data and data["user_id"] == self.user_id:
                self.add_result("Get Current User", True, f"User info retrieved: {data.get('username')}", data)
            else:
                self.add_result("Get Current User", False, f"User ID mismatch or missing: {data}")
        else:
            status = response.status_code if response else "No response"
            error = response.json() if response else "No response"
            self.add_result("Get Current User", False, f"Failed with status {status}: {error}")
    
    def test_game_data(self):
        """Test 3: Game Data Endpoints (requires auth)"""
        if not self.token:
            self.add_result("Game Data Endpoints", False, "No auth token available")
            return
        
        # Test Races
        self.log("Testing races endpoint...")
        response = self.make_request("GET", "/game/races")
        if response and response.status_code == 200:
            data = response.json()
            if "races" in data and len(data["races"]) >= 6:
                races = list(data["races"].keys())
                self.add_result("Get Races", True, f"Retrieved {len(races)} races: {races[:3]}...", data)
            else:
                self.add_result("Get Races", False, f"Expected at least 6 races, got: {data}")
        else:
            status = response.status_code if response else "No response"
            self.add_result("Get Races", False, f"Failed with status: {status}")
        
        # Test Fighting Styles
        self.log("Testing fighting styles endpoint...")
        response = self.make_request("GET", "/game/fighting-styles")
        if response and response.status_code == 200:
            data = response.json()
            if "styles" in data and len(data["styles"]) >= 6:
                styles = list(data["styles"].keys())
                self.add_result("Get Fighting Styles", True, f"Retrieved {len(styles)} styles: {styles[:3]}...", data)
            else:
                self.add_result("Get Fighting Styles", False, f"Expected at least 6 styles, got: {data}")
        else:
            status = response.status_code if response else "No response"
            self.add_result("Get Fighting Styles", False, f"Failed with status: {status}")
        
        # Test Mestieri
        self.log("Testing mestieri endpoint...")
        response = self.make_request("GET", "/game/mestieri")
        if response and response.status_code == 200:
            data = response.json()
            if "mestieri" in data and len(data["mestieri"]) >= 12:
                mestieri = list(data["mestieri"].keys())
                self.add_result("Get Mestieri", True, f"Retrieved {len(mestieri)} jobs: {mestieri[:3]}...", data)
            else:
                self.add_result("Get Mestieri", False, f"Expected at least 12 jobs, got: {data}")
        else:
            status = response.status_code if response else "No response"
            self.add_result("Get Mestieri", False, f"Failed with status: {status}")
    
    def test_character_name_validation(self):
        """Test 4: Character Name Validation"""
        if not self.token:
            self.add_result("Character Name Validation", False, "No auth token available")
            return
        
        # Test valid name
        self.log("Testing valid character name...")
        response = self.make_request("POST", "/characters/validate-name", {"nome": "Monkey Luffy"})
        if response and response.status_code == 200:
            data = response.json()
            if data.get("valid") == True:
                self.add_result("Valid Name Check", True, "Monkey Luffy is valid", data)
            else:
                self.add_result("Valid Name Check", False, f"Expected valid=True, got: {data}")
        else:
            status = response.status_code if response else "No response"
            self.add_result("Valid Name Check", False, f"Failed with status: {status}")
        
        # Test invalid name with "D."
        self.log("Testing invalid name with D....")
        response = self.make_request("POST", "/characters/validate-name", {"nome": "Monkey D. Luffy"})
        if response and response.status_code == 200:
            data = response.json()
            if data.get("valid") == False:
                self.add_result("Invalid Name D. Check", True, "Monkey D. Luffy correctly blocked", data)
            else:
                self.add_result("Invalid Name D. Check", False, f"Expected valid=False, got: {data}")
        else:
            status = response.status_code if response else "No response"
            self.add_result("Invalid Name D. Check", False, f"Failed with status: {status}")
        
        # Test invalid name with "D "
        self.log("Testing invalid name with D space...")
        response = self.make_request("POST", "/characters/validate-name", {"nome": "Monkey D Luffy"})
        if response and response.status_code == 200:
            data = response.json()
            if data.get("valid") == False:
                self.add_result("Invalid Name D Space Check", True, "Monkey D Luffy correctly blocked", data)
            else:
                self.add_result("Invalid Name D Space Check", False, f"Expected valid=False, got: {data}")
        else:
            status = response.status_code if response else "No response"
            self.add_result("Invalid Name D Space Check", False, f"Failed with status: {status}")
    
    def test_character_creation(self):
        """Test 5: Character Creation (requires auth, no existing character)"""
        if not self.token:
            self.add_result("Character Creation", False, "No auth token available")
            return
        
        # Create character
        self.log("Testing character creation...")
        char_data = {
            "nome_personaggio": "Test Pirate Captain",
            "ruolo": "pirata",
            "genere": "maschio",
            "eta": 20,
            "razza": "umano",
            "stile_combattimento": "corpo_misto",
            "sogno": "Diventare il Re dei Pirati",
            "storia_carattere": "Un giovane pirata determinato che ha sempre sognato di navigare i mari alla ricerca del One Piece",
            "mestiere": "capitano"
        }
        
        response = self.make_request("POST", "/characters", char_data)
        if response and response.status_code == 200:
            data = response.json()
            if "character_id" in data and "nome_personaggio" in data:
                self.character_id = data["character_id"]
                self.add_result("Character Creation", True, f"Character created: {data['nome_personaggio']}", data)
            else:
                self.add_result("Character Creation", False, f"Missing character data: {data}")
        else:
            status = response.status_code if response else "No response"
            error = response.json() if response else "No response"
            self.add_result("Character Creation", False, f"Failed with status {status}: {error}")
            return
        
        # Get character
        self.log("Testing get my character...")
        response = self.make_request("GET", "/characters/me")
        if response and response.status_code == 200:
            data = response.json()
            if "character_id" in data and data["character_id"] == self.character_id:
                self.add_result("Get My Character", True, f"Character retrieved: {data['nome_personaggio']}", data)
            else:
                self.add_result("Get My Character", False, f"Character ID mismatch: {data}")
        else:
            status = response.status_code if response else "No response"
            self.add_result("Get My Character", False, f"Failed with status: {status}")
    
    def test_battle_system(self):
        """Test 6: Battle System (requires auth + character)"""
        if not self.token or not self.character_id:
            self.add_result("Battle System", False, "No auth token or character available")
            return
        
        # Start battle
        self.log("Testing battle start...")
        battle_data = {
            "opponent_type": "npc",
            "opponent_id": "pirata_novizio"
        }
        
        response = self.make_request("POST", "/battle/start", battle_data)
        if response and response.status_code == 200:
            data = response.json()
            if "battle_id" in data and "battle" in data:
                self.battle_id = data["battle_id"]
                battle_info = data["battle"]
                self.add_result("Battle Start", True, f"Battle started with ID: {self.battle_id}", data)
                
                # Test battle action
                self.log("Testing battle action...")
                action_data = {
                    "action_type": "attacco_base",
                    "action_name": "Pugno"
                }
                
                action_response = self.make_request("POST", f"/battle/{self.battle_id}/action", action_data)
                if action_response and action_response.status_code == 200:
                    action_result = action_response.json()
                    if "result" in action_result and "battle" in action_result:
                        self.add_result("Battle Action", True, f"Battle action executed: {action_result['result']}", action_result)
                    else:
                        self.add_result("Battle Action", False, f"Missing result/battle in response: {action_result}")
                else:
                    status = action_response.status_code if action_response else "No response"
                    self.add_result("Battle Action", False, f"Failed with status: {status}")
            else:
                self.add_result("Battle Start", False, f"Missing battle data: {data}")
        else:
            status = response.status_code if response else "No response"
            error = response.json() if response else "No response"
            self.add_result("Battle Start", False, f"Failed with status {status}: {error}")
    
    def test_world_map(self):
        """Test 7: World Map (requires auth + character)"""
        if not self.token or not self.character_id:
            self.add_result("World Map", False, "No auth token or character available")
            return
        
        self.log("Testing world islands...")
        response = self.make_request("GET", "/world/islands")
        if response and response.status_code == 200:
            data = response.json()
            if "islands" in data and "isola_corrente" in data:
                islands = data["islands"]
                if len(islands) > 0:
                    unlocked = [i for i in islands if i.get("sbloccata")]
                    self.add_result("World Map", True, f"Retrieved {len(islands)} islands, {len(unlocked)} unlocked", data)
                else:
                    self.add_result("World Map", False, f"No islands returned: {data}")
            else:
                self.add_result("World Map", False, f"Missing islands/isola_corrente: {data}")
        else:
            status = response.status_code if response else "No response"
            error = response.json() if response else "No response"
            self.add_result("World Map", False, f"Failed with status {status}: {error}")
    
    def test_shop_system(self):
        """Test 8: Shop System (requires auth)"""
        if not self.token:
            self.add_result("Shop System", False, "No auth token available")
            return
        
        # Get shop items
        self.log("Testing shop items...")
        response = self.make_request("GET", "/shop/items")
        if response and response.status_code == 200:
            data = response.json()
            if "items" in data and len(data["items"]) > 0:
                items = list(data["items"].keys())
                self.add_result("Get Shop Items", True, f"Retrieved {len(items)} items: {items[:3]}...", data)
                
                # Try to buy an item (expected to fail due to no Berry)
                self.log("Testing shop purchase (expecting failure due to no Berry)...")
                buy_response = self.make_request("POST", "/shop/buy", {"item_id": "pozione_vita"})
                if buy_response and buy_response.status_code == 400:
                    error = buy_response.json()
                    if "Berry insufficienti" in error.get("detail", ""):
                        self.add_result("Shop Purchase (No Berry)", True, "Purchase correctly failed due to insufficient Berry", error)
                    else:
                        self.add_result("Shop Purchase (No Berry)", False, f"Unexpected error: {error}")
                else:
                    status = buy_response.status_code if buy_response else "No response"
                    self.add_result("Shop Purchase (No Berry)", False, f"Expected 400 error, got: {status}")
            else:
                self.add_result("Get Shop Items", False, f"No items returned: {data}")
        else:
            status = response.status_code if response else "No response"
            self.add_result("Get Shop Items", False, f"Failed with status: {status}")
    
    def test_crew_system(self):
        """Test 9: Crew System (requires auth + character)"""
        if not self.token or not self.character_id:
            self.add_result("Crew System", False, "No auth token or character available")
            return
        
        # Create crew
        self.log("Testing crew creation...")
        crew_data = {
            "nome": f"Test Pirates {int(datetime.now().timestamp())}"
        }
        
        response = self.make_request("POST", "/crew/create", crew_data)
        if response and response.status_code == 200:
            data = response.json()
            if "crew" in data and "crew_id" in data["crew"]:
                self.crew_id = data["crew"]["crew_id"]
                self.add_result("Crew Creation", True, f"Crew created: {data['crew']['nome']}", data)
                
                # Get my crew
                self.log("Testing get my crew...")
                crew_response = self.make_request("GET", "/crew/my")
                if crew_response and crew_response.status_code == 200:
                    crew_data = crew_response.json()
                    if "crew" in crew_data and crew_data["crew"]:
                        self.add_result("Get My Crew", True, f"Crew info retrieved: {crew_data['crew']['nome']}", crew_data)
                        
                        # Leave crew
                        self.log("Testing leave crew...")
                        leave_response = self.make_request("POST", "/crew/leave", {})
                        if leave_response and leave_response.status_code == 200:
                            leave_result = leave_response.json()
                            self.add_result("Leave Crew", True, "Successfully left crew", leave_result)
                        else:
                            status = leave_response.status_code if leave_response else "No response"
                            self.add_result("Leave Crew", False, f"Failed with status: {status}")
                    else:
                        self.add_result("Get My Crew", False, f"No crew info returned: {crew_data}")
                else:
                    status = crew_response.status_code if crew_response else "No response"
                    self.add_result("Get My Crew", False, f"Failed with status: {status}")
            else:
                self.add_result("Crew Creation", False, f"Missing crew data: {data}")
        else:
            status = response.status_code if response else "No response"
            error = response.json() if response else "No response"
            self.add_result("Crew Creation", False, f"Failed with status {status}: {error}")
    
    def test_logbook_system(self):
        """Test 10: Logbook (requires auth + character)"""
        if not self.token or not self.character_id:
            self.add_result("Logbook System", False, "No auth token or character available")
            return
        
        # Get logbook entries
        self.log("Testing get logbook...")
        response = self.make_request("GET", "/logbook")
        if response and response.status_code == 200:
            data = response.json()
            if "entries" in data:
                entries = data["entries"]
                self.add_result("Get Logbook", True, f"Retrieved {len(entries)} logbook entries", data)
                
                # Add manual entry
                self.log("Testing add logbook entry...")
                add_response = self.make_request("POST", "/logbook/add", {"descrizione": "Test logbook entry from API test"})
                if add_response and add_response.status_code == 200:
                    add_result = add_response.json()
                    if "entry" in add_result:
                        self.add_result("Add Logbook Entry", True, f"Entry added: {add_result['entry']['descrizione']}", add_result)
                    else:
                        self.add_result("Add Logbook Entry", False, f"Missing entry in response: {add_result}")
                else:
                    status = add_response.status_code if add_response else "No response"
                    self.add_result("Add Logbook Entry", False, f"Failed with status: {status}")
            else:
                self.add_result("Get Logbook", False, f"Missing entries in response: {data}")
        else:
            status = response.status_code if response else "No response"
            self.add_result("Get Logbook", False, f"Failed with status: {status}")

    def test_inventory_system(self):
        """Test 11: New Inventory System (requires auth + character with Berry)"""
        if not self.token or not self.character_id:
            self.add_result("Inventory System", False, "No auth token or character available")
            return
        
        # First ensure we have berry by winning a battle if needed
        self.log("Testing inventory system - ensuring we have Berry...")
        
        # Get current character to check Berry balance
        char_response = self.make_request("GET", "/characters/me")
        if not char_response or char_response.status_code != 200:
            self.add_result("Check Character Berry", False, "Cannot get character info")
            return
        
        char_data = char_response.json()
        current_berry = char_data.get("berry", 0)
        self.log(f"Current Berry balance: {current_berry}")
        
        # If we don't have enough Berry (need at least 1400 for all items), skip buying
        if current_berry < 1400:
            self.log(f"Insufficient Berry ({current_berry}), will test with whatever we can buy...")
        
        # Step 1: Buy items to populate inventory
        items_to_buy = [
            ("pozione_vita", 100),
            ("bevanda_energia", 80), 
            ("spada_base", 500),
            ("carta_vento_favorevole", 200)
        ]
        
        bought_items = []
        for item_id, price in items_to_buy:
            if current_berry >= price:
                self.log(f"Buying {item_id}...")
                buy_response = self.make_request("POST", "/shop/buy", {"item_id": item_id})
                if buy_response and buy_response.status_code == 200:
                    buy_data = buy_response.json()
                    bought_items.append(item_id)
                    current_berry -= price
                    self.add_result(f"Buy {item_id}", True, f"Successfully bought {buy_data.get('message', item_id)}")
                else:
                    status = buy_response.status_code if buy_response else "No response"
                    error = buy_response.json() if buy_response else "No response"
                    self.add_result(f"Buy {item_id}", False, f"Failed to buy {item_id}: {status} - {error}")
            else:
                self.log(f"Skipping {item_id} - insufficient Berry ({current_berry} < {price})")
        
        # Step 2: Test GET /api/inventory
        self.log("Testing GET /api/inventory...")
        inv_response = self.make_request("GET", "/inventory")
        if inv_response and inv_response.status_code == 200:
            inv_data = inv_response.json()
            if "oggetti" in inv_data and "armi" in inv_data and "carte" in inv_data:
                oggetti = inv_data["oggetti"]
                armi = inv_data["armi"] 
                carte = inv_data["carte"]
                berry = inv_data.get("berry", 0)
                
                self.add_result("Get Inventory", True, 
                    f"Inventory retrieved: {len(oggetti)} items, {len(armi)} weapons, "
                    f"{len(carte.get('storytelling', []))} cards, {berry} Berry", inv_data)
                
                # Verify bought items appear in correct categories
                if "pozione_vita" in bought_items or "bevanda_energia" in bought_items:
                    consumables_found = [item for item in oggetti if item.get("id") in ["pozione_vita", "bevanda_energia"]]
                    if consumables_found:
                        self.add_result("Items in Oggetti Category", True, 
                            f"Found {len(consumables_found)} consumable items in oggetti")
                    else:
                        self.add_result("Items in Oggetti Category", False, 
                            f"No consumable items found in oggetti, expected some")
                
                if "spada_base" in bought_items:
                    weapons_found = [weapon for weapon in armi if weapon.get("id") == "spada_base"]
                    if weapons_found:
                        self.add_result("Weapons in Armi Category", True, 
                            f"Found weapon in armi category: {weapons_found[0].get('name')}")
                    else:
                        self.add_result("Weapons in Armi Category", False, 
                            f"Spada Base not found in armi category")
                
                if "carta_vento_favorevole" in bought_items:
                    cards_found = [card for card in carte.get("storytelling", []) if card.get("id") == "carta_vento_favorevole"]
                    if cards_found:
                        self.add_result("Cards in Carte Category", True, 
                            f"Found card in storytelling category: {cards_found[0].get('name')}")
                    else:
                        self.add_result("Cards in Carte Category", False, 
                            f"Carta Vento Favorevole not found in storytelling cards")
                        
            else:
                self.add_result("Get Inventory", False, f"Missing inventory categories: {inv_data}")
        else:
            status = inv_response.status_code if inv_response else "No response"
            error = inv_response.json() if inv_response else "No response"
            self.add_result("Get Inventory", False, f"Failed with status {status}: {error}")
            return
        
        # Step 3: Test POST /api/inventory/use-item
        if "pozione_vita" in bought_items:
            self.log("Testing use-item endpoint with pozione_vita...")
            use_response = self.make_request("POST", "/inventory/use-item", {"item_id": "pozione_vita"})
            if use_response and use_response.status_code == 200:
                use_data = use_response.json()
                if "effects_applied" in use_data and "message" in use_data:
                    effects = use_data["effects_applied"]
                    self.add_result("Use Item (Pozione Vita)", True, 
                        f"Item used successfully: {use_data['message']}, Effects: {effects}", use_data)
                    
                    # Verify item was removed from inventory
                    self.log("Verifying item was removed from inventory...")
                    verify_response = self.make_request("GET", "/inventory")
                    if verify_response and verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        remaining_potions = [item for item in verify_data.get("oggetti", []) if item.get("id") == "pozione_vita"]
                        if len(remaining_potions) == 0:
                            self.add_result("Item Removed After Use", True, "Pozione Vita correctly removed from inventory")
                        else:
                            self.add_result("Item Removed After Use", False, f"Pozione Vita still in inventory: {remaining_potions}")
                else:
                    self.add_result("Use Item (Pozione Vita)", False, f"Missing effects/message in response: {use_data}")
            else:
                status = use_response.status_code if use_response else "No response"
                error = use_response.json() if use_response else "No response"
                self.add_result("Use Item (Pozione Vita)", False, f"Failed with status {status}: {error}")
        
        # Step 4: Test POST /api/inventory/equip-weapon
        if "spada_base" in bought_items:
            self.log("Testing equip-weapon endpoint with spada_base...")
            equip_response = self.make_request("POST", "/inventory/equip-weapon", {"weapon_id": "spada_base"})
            if equip_response and equip_response.status_code == 200:
                equip_data = equip_response.json()
                if "message" in equip_data:
                    self.add_result("Equip Weapon", True, f"Weapon equipped: {equip_data['message']}", equip_data)
                    
                    # Verify weapon is marked as equipped in inventory
                    self.log("Verifying weapon is marked as equipped...")
                    verify_response = self.make_request("GET", "/inventory")
                    if verify_response and verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        equipped_weapons = [weapon for weapon in verify_data.get("armi", []) 
                                          if weapon.get("id") == "spada_base" and weapon.get("equipped", False)]
                        if equipped_weapons:
                            self.add_result("Weapon Equipped Status", True, "Spada Base correctly marked as equipped")
                        else:
                            self.add_result("Weapon Equipped Status", False, "Spada Base not marked as equipped in inventory")
                else:
                    self.add_result("Equip Weapon", False, f"Missing message in response: {equip_data}")
            else:
                status = equip_response.status_code if equip_response else "No response"  
                error = equip_response.json() if equip_response else "No response"
                self.add_result("Equip Weapon", False, f"Failed with status {status}: {error}")
        
        # Step 5: Test POST /api/cards/use
        if "carta_vento_favorevole" in bought_items:
            self.log("Testing use card endpoint with carta_vento_favorevole...")
            card_response = self.make_request("POST", "/cards/use", {"card_id": "carta_vento_favorevole"})
            if card_response and card_response.status_code == 200:
                card_data = card_response.json()
                if "message" in card_data:
                    self.add_result("Use Card", True, f"Card used: {card_data['message']}", card_data)
                    
                    # Verify card was removed from inventory
                    self.log("Verifying card was removed from inventory...")
                    verify_response = self.make_request("GET", "/inventory")
                    if verify_response and verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        remaining_cards = [card for card in verify_data.get("carte", {}).get("storytelling", []) 
                                         if card.get("id") == "carta_vento_favorevole"]
                        if len(remaining_cards) == 0:
                            self.add_result("Card Removed After Use", True, "Carta Vento Favorevole correctly removed from inventory")
                        else:
                            self.add_result("Card Removed After Use", False, f"Carta Vento Favorevole still in inventory: {remaining_cards}")
                else:
                    self.add_result("Use Card", False, f"Missing message in response: {card_data}")
            else:
                status = card_response.status_code if card_response else "No response"
                error = card_response.json() if card_response else "No response"
                self.add_result("Use Card", False, f"Failed with status {status}: {error}")
    
    def run_all_tests(self):
        """Run all test sequences"""
        self.log("Starting comprehensive backend API testing...")
        self.log(f"Testing against: {self.base_url}")
        
        # Test sequence as per review request
        self.test_health_check()
        self.test_auth_flow()
        self.test_game_data()
        self.test_character_name_validation()
        self.test_character_creation()
        self.test_battle_system()
        self.test_world_map()
        self.test_shop_system()
        self.test_crew_system()
        self.test_logbook_system()
        
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*60)
        print("BACKEND API TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.results['passed'] + self.results['failed']}")
        print(f"Passed: {self.results['passed']}")
        print(f"Failed: {self.results['failed']}")
        
        if self.results['failed'] > 0:
            print(f"\nFAILED TESTS:")
            for test in self.results['tests']:
                if test['status'] == 'FAIL':
                    print(f"❌ {test['name']}: {test['message']}")
        
        print(f"\nSUCCESS RATE: {(self.results['passed']/(self.results['passed']+self.results['failed'])*100):.1f}%")
        print("="*60)

if __name__ == "__main__":
    tester = OnePointAPITester(backend_url)
    tester.run_all_tests()
    
    # Exit with error code if tests failed
    if tester.results['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)