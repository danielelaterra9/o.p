#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Four Seas Navigation System
Tests the updated structure with new islands and zones
"""

import requests
import json
import random
import string
import time

# Configuration
BASE_URL = "https://project-builder-127.preview.emergentagent.com/api"

class FourSeasNavigationTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.test_character_id = None
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

    def register_and_login(self):
        """Setup: Register and login a test user"""
        # Generate unique user credentials
        random_suffix = ''.join(random.choices(string.digits, k=8))
        username = f"FourSeasTester{random_suffix}"
        email = f"fourseas{random_suffix}@test.com"
        password = "SecureTestPass123!"

        # Register user
        register_data = {
            "username": username,
            "email": email,
            "password": password
        }

        try:
            response = self.session.post(f"{BASE_URL}/auth/register", json=register_data)
            if response.status_code != 200:
                return self.log_test("User Registration", False, f"Registration failed: {response.text}")
            
            register_result = response.json()
            self.user_token = register_result.get("token")
            
            if not self.user_token:
                return self.log_test("User Registration", False, "No token received")
            
            # Set authorization header for future requests
            self.session.headers.update({"Authorization": f"Bearer {self.user_token}"})
            
            return self.log_test("User Registration", True, f"User {username} registered successfully with token")
            
        except Exception as e:
            return self.log_test("User Registration", False, f"Registration error: {str(e)}")

    def test_get_all_seas(self):
        """Test GET /api/world/seas - should return 4 seas"""
        try:
            response = self.session.get(f"{BASE_URL}/world/seas")
            
            if response.status_code != 200:
                return self.log_test("Get All Seas", False, f"HTTP {response.status_code}: {response.text}")
            
            data = response.json()
            seas = data.get("seas", {})
            
            # Verify 4 seas exist
            expected_seas = ["east_blue", "west_blue", "north_blue", "south_blue"]
            
            if len(seas) != 4:
                return self.log_test("Get All Seas", False, f"Expected 4 seas, got {len(seas)}")
            
            for sea_id in expected_seas:
                if sea_id not in seas:
                    return self.log_test("Get All Seas", False, f"Missing sea: {sea_id}")
                
                sea_data = seas[sea_id]
                if not all(key in sea_data for key in ["name", "description", "color"]):
                    return self.log_test("Get All Seas", False, f"Incomplete data for sea: {sea_id}")
            
            return self.log_test("Get All Seas", True, f"All 4 seas returned with complete data: {list(seas.keys())}")
            
        except Exception as e:
            return self.log_test("Get All Seas", False, f"Exception: {str(e)}")

    def test_east_blue_islands(self):
        """Test GET /api/world/seas/east_blue/islands - should return 9 islands with Dawn Island zones"""
        try:
            response = self.session.get(f"{BASE_URL}/world/seas/east_blue/islands")
            
            if response.status_code != 200:
                return self.log_test("East Blue Islands", False, f"HTTP {response.status_code}: {response.text}")
            
            data = response.json()
            islands = data.get("islands", [])
            sea_info = data.get("sea_info", {})
            
            # Check island count
            if len(islands) != 9:
                return self.log_test("East Blue Islands", False, f"Expected 9 islands, got {len(islands)}")
            
            # Verify expected islands exist
            expected_islands = [
                "dawn_island", "shells_town", "shimotsuki_village", "organ_islands",
                "island_rare_animals", "gecko_islands", "baratie", "conomi_islands", "loguetown"
            ]
            
            island_ids = [island["id"] for island in islands]
            
            for expected_id in expected_islands:
                if expected_id not in island_ids:
                    return self.log_test("East Blue Islands", False, f"Missing expected island: {expected_id}")
            
            # Find Dawn Island and check zones
            dawn_island = None
            for island in islands:
                if island["id"] == "dawn_island":
                    dawn_island = island
                    break
            
            if not dawn_island:
                return self.log_test("East Blue Islands", False, "Dawn Island not found")
            
            zones = dawn_island.get("zone", [])
            if len(zones) != 5:
                return self.log_test("East Blue Islands", False, f"Dawn Island should have 5 zones, got {len(zones)}")
            
            # Verify zone names
            expected_zones = ["foosha", "mt_colubo", "gray_terminal", "midway_forest", "goa_kingdom"]
            zone_ids = [zone["id"] for zone in zones]
            
            for expected_zone in expected_zones:
                if expected_zone not in zone_ids:
                    return self.log_test("East Blue Islands", False, f"Missing Dawn Island zone: {expected_zone}")
            
            # Verify sea info
            if sea_info.get("name") != "East Blue":
                return self.log_test("East Blue Islands", False, f"Incorrect sea name: {sea_info.get('name')}")
            
            return self.log_test("East Blue Islands", True, f"9 East Blue islands returned with Dawn Island containing 5 zones: {zone_ids}")
            
        except Exception as e:
            return self.log_test("East Blue Islands", False, f"Exception: {str(e)}")

    def test_west_blue_islands(self):
        """Test GET /api/world/seas/west_blue/islands - should return 7 islands starting with Ohara"""
        try:
            response = self.session.get(f"{BASE_URL}/world/seas/west_blue/islands")
            
            if response.status_code != 200:
                return self.log_test("West Blue Islands", False, f"HTTP {response.status_code}: {response.text}")
            
            data = response.json()
            islands = data.get("islands", [])
            
            # Check island count
            if len(islands) != 7:
                return self.log_test("West Blue Islands", False, f"Expected 7 islands, got {len(islands)}")
            
            # Check first island is Ohara
            if not islands or islands[0]["id"] != "ohara":
                first_island = islands[0]["id"] if islands else "none"
                return self.log_test("West Blue Islands", False, f"First island should be 'ohara', got '{first_island}'")
            
            # Verify all islands belong to west_blue
            for island in islands:
                if island["sea"] != "west_blue":
                    return self.log_test("West Blue Islands", False, f"Island {island['id']} has wrong sea: {island['sea']}")
            
            island_names = [island["name"] for island in islands]
            return self.log_test("West Blue Islands", True, f"7 West Blue islands starting with Ohara: {island_names}")
            
        except Exception as e:
            return self.log_test("West Blue Islands", False, f"Exception: {str(e)}")

    def test_north_blue_islands(self):
        """Test GET /api/world/seas/north_blue/islands - should return 11 islands starting with Downs"""
        try:
            response = self.session.get(f"{BASE_URL}/world/seas/north_blue/islands")
            
            if response.status_code != 200:
                return self.log_test("North Blue Islands", False, f"HTTP {response.status_code}: {response.text}")
            
            data = response.json()
            islands = data.get("islands", [])
            
            # Check island count
            if len(islands) != 11:
                return self.log_test("North Blue Islands", False, f"Expected 11 islands, got {len(islands)}")
            
            # Check first island is Downs
            if not islands or islands[0]["id"] != "downs":
                first_island = islands[0]["id"] if islands else "none"
                return self.log_test("North Blue Islands", False, f"First island should be 'downs', got '{first_island}'")
            
            # Verify all islands belong to north_blue
            for island in islands:
                if island["sea"] != "north_blue":
                    return self.log_test("North Blue Islands", False, f"Island {island['id']} has wrong sea: {island['sea']}")
            
            island_names = [island["name"] for island in islands]
            return self.log_test("North Blue Islands", True, f"11 North Blue islands starting with Downs: {island_names}")
            
        except Exception as e:
            return self.log_test("North Blue Islands", False, f"Exception: {str(e)}")

    def test_south_blue_islands(self):
        """Test GET /api/world/seas/south_blue/islands - should return 10 islands starting with Baterilla"""
        try:
            response = self.session.get(f"{BASE_URL}/world/seas/south_blue/islands")
            
            if response.status_code != 200:
                return self.log_test("South Blue Islands", False, f"HTTP {response.status_code}: {response.text}")
            
            data = response.json()
            islands = data.get("islands", [])
            
            # Check island count
            if len(islands) != 10:
                return self.log_test("South Blue Islands", False, f"Expected 10 islands, got {len(islands)}")
            
            # Check first island is Baterilla
            if not islands or islands[0]["id"] != "baterilla":
                first_island = islands[0]["id"] if islands else "none"
                return self.log_test("South Blue Islands", False, f"First island should be 'baterilla', got '{first_island}'")
            
            # Verify all islands belong to south_blue
            for island in islands:
                if island["sea"] != "south_blue":
                    return self.log_test("South Blue Islands", False, f"Island {island['id']} has wrong sea: {island['sea']}")
            
            island_names = [island["name"] for island in islands]
            return self.log_test("South Blue Islands", True, f"10 South Blue islands starting with Baterilla: {island_names}")
            
        except Exception as e:
            return self.log_test("South Blue Islands", False, f"Exception: {str(e)}")

    def test_character_creation_east_blue(self):
        """Test character creation with mare_partenza: east_blue - should set isola_corrente to dawn_island"""
        try:
            character_data = {
                "nome_personaggio": "Monkey Luffy",
                "ruolo": "capitano",
                "genere": "maschio",
                "eta": 17,
                "razza": "umano",
                "stile_combattimento": "corpo_pugni",
                "sogno": "Diventare il Re dei Pirati",
                "storia_carattere": "Un giovane pirata con il sogno di trovare il One Piece e diventare il Re dei Pirati. Ha mangiato il frutto del diavolo Gomu Gomu.",
                "mestiere": "pirata",
                "mare_partenza": "east_blue"
            }

            response = self.session.post(f"{BASE_URL}/characters", json=character_data)
            
            if response.status_code != 200:
                return self.log_test("Character Creation East Blue", False, f"HTTP {response.status_code}: {response.text}")
            
            character = response.json()
            self.test_character_id = character.get("character_id")
            
            # Verify starting location
            mare_corrente = character.get("mare_corrente")
            isola_corrente = character.get("isola_corrente")
            
            if mare_corrente != "east_blue":
                return self.log_test("Character Creation East Blue", False, f"Expected mare_corrente 'east_blue', got '{mare_corrente}'")
            
            if isola_corrente != "dawn_island":
                return self.log_test("Character Creation East Blue", False, f"Expected isola_corrente 'dawn_island', got '{isola_corrente}'")
            
            return self.log_test("Character Creation East Blue", True, f"Character created in east_blue starting at dawn_island")
            
        except Exception as e:
            return self.log_test("Character Creation East Blue", False, f"Exception: {str(e)}")

    def test_character_islands_view(self):
        """Test GET /world/islands after character creation - should show Dawn Island with zones"""
        try:
            response = self.session.get(f"{BASE_URL}/world/islands")
            
            if response.status_code != 200:
                return self.log_test("Character Islands View", False, f"HTTP {response.status_code}: {response.text}")
            
            data = response.json()
            islands = data.get("islands", [])
            isola_corrente = data.get("isola_corrente")
            mare_corrente = data.get("mare_corrente")
            
            if mare_corrente != "east_blue":
                return self.log_test("Character Islands View", False, f"Expected mare_corrente 'east_blue', got '{mare_corrente}'")
            
            if isola_corrente != "dawn_island":
                return self.log_test("Character Islands View", False, f"Expected isola_corrente 'dawn_island', got '{isola_corrente}'")
            
            # Find Dawn Island in response
            dawn_island = None
            for island in islands:
                if island["id"] == "dawn_island":
                    dawn_island = island
                    break
            
            if not dawn_island:
                return self.log_test("Character Islands View", False, "Dawn Island not found in character's islands")
            
            # Verify zones are present
            zones = dawn_island.get("zone", [])
            if len(zones) != 5:
                return self.log_test("Character Islands View", False, f"Dawn Island should have 5 zones, got {len(zones)}")
            
            # Verify current island is marked correctly
            if not dawn_island.get("corrente"):
                return self.log_test("Character Islands View", False, "Dawn Island not marked as current")
            
            return self.log_test("Character Islands View", True, f"Character islands view correct: {len(islands)} East Blue islands with Dawn Island as current, containing 5 zones")
            
        except Exception as e:
            return self.log_test("Character Islands View", False, f"Exception: {str(e)}")

    def test_character_creation_other_seas(self):
        """Test character creation with different starting seas"""
        seas_to_test = [
            ("west_blue", "ohara"),
            ("north_blue", "downs"), 
            ("south_blue", "baterilla")
        ]
        
        all_tests_passed = True
        
        for sea_id, expected_island in seas_to_test:
            try:
                # Create new user for each sea test
                random_suffix = ''.join(random.choices(string.digits, k=6))
                username = f"SeaTester{sea_id}{random_suffix}"
                email = f"seatest{sea_id}{random_suffix}@test.com"
                password = "TestPass123!"

                # Register
                register_data = {
                    "username": username,
                    "email": email,
                    "password": password
                }
                
                register_response = self.session.post(f"{BASE_URL}/auth/register", json=register_data)
                if register_response.status_code != 200:
                    all_tests_passed = False
                    continue
                
                token = register_response.json().get("token")
                headers = {"Authorization": f"Bearer {token}"}
                
                # Create character in specific sea
                character_data = {
                    "nome_personaggio": f"TestPirate{sea_id.title()}",
                    "ruolo": "capitano",
                    "genere": "maschio",
                    "eta": 20,
                    "razza": "umano",
                    "stile_combattimento": "armi_mono",
                    "sogno": "Esplorare il mare",
                    "storia_carattere": f"Un pirata del {sea_id.replace('_', ' ').title()}",
                    "mestiere": "pirata",
                    "mare_partenza": sea_id
                }

                char_response = requests.post(f"{BASE_URL}/characters", json=character_data, headers=headers)
                
                if char_response.status_code != 200:
                    all_tests_passed = False
                    self.log_test(f"Character Creation {sea_id.title()}", False, f"Failed to create character: {char_response.text}")
                    continue
                
                character = char_response.json()
                mare_corrente = character.get("mare_corrente")
                isola_corrente = character.get("isola_corrente")
                
                if mare_corrente != sea_id:
                    all_tests_passed = False
                    self.log_test(f"Character Creation {sea_id.title()}", False, f"Expected mare_corrente '{sea_id}', got '{mare_corrente}'")
                    continue
                
                if isola_corrente != expected_island:
                    all_tests_passed = False
                    self.log_test(f"Character Creation {sea_id.title()}", False, f"Expected isola_corrente '{expected_island}', got '{isola_corrente}'")
                    continue
                
                self.log_test(f"Character Creation {sea_id.title()}", True, f"Character created in {sea_id} starting at {expected_island}")
                
            except Exception as e:
                all_tests_passed = False
                self.log_test(f"Character Creation {sea_id.title()}", False, f"Exception: {str(e)}")
        
        return all_tests_passed

    def run_all_tests(self):
        """Run all Four Seas navigation tests"""
        print("=" * 80)
        print("FOUR SEAS NAVIGATION SYSTEM - COMPREHENSIVE TESTING")
        print("=" * 80)
        
        tests_passed = 0
        total_tests = 0
        
        # Test sequence
        test_functions = [
            ("Setup: User Registration & Login", self.register_and_login),
            ("Test 1: Get All Seas", self.test_get_all_seas),
            ("Test 2: East Blue Islands (9 islands + zones)", self.test_east_blue_islands),
            ("Test 3: West Blue Islands (7 islands)", self.test_west_blue_islands),
            ("Test 4: North Blue Islands (11 islands)", self.test_north_blue_islands),
            ("Test 5: South Blue Islands (10 islands)", self.test_south_blue_islands),
            ("Test 6: Character Creation East Blue", self.test_character_creation_east_blue),
            ("Test 7: Character Islands View", self.test_character_islands_view),
            ("Test 8: Character Creation Other Seas", self.test_character_creation_other_seas),
        ]
        
        for test_name, test_func in test_functions:
            print(f"\n[RUNNING] {test_name}")
            result = test_func()
            if result:
                tests_passed += 1
            total_tests += 1
            
        print("\n" + "=" * 80)
        print("FOUR SEAS NAVIGATION TESTING SUMMARY")
        print("=" * 80)
        
        success_rate = (tests_passed / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Tests Passed: {tests_passed}/{total_tests} ({success_rate:.1f}%)")
        
        if tests_passed == total_tests:
            print("🎉 ALL TESTS PASSED! Four Seas Navigation System is fully functional.")
        else:
            print("⚠️  Some tests failed. Review the failures above.")
            
        return success_rate >= 95

if __name__ == "__main__":
    tester = FourSeasNavigationTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)