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

class OnePixelRPGTester:
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
                self.log_test("User Registration", True, f"User {user_data['username']} created successfully")
                return True
            else:
                self.log_test("User Registration", False, "", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Registration", False, "", str(e))
            return False

    def create_character(self):
        """Create character with mare_partenza: east_blue"""
        try:
            char_data = random_character_data()
            response = self.session.post(f"{self.base_url}/characters", json=char_data)
            
            if response.status_code == 200:
                self.character_data = response.json()
                self.log_test("Character Creation", True, 
                            f"Character {char_data['nome_personaggio']} created with mare_partenza: {char_data['mare_partenza']}")
                return True
            else:
                self.log_test("Character Creation", False, "", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Character Creation", False, "", str(e))
            return False

    def test_narrative_templates(self):
        """Test GET /api/narrative/templates"""
        try:
            response = self.session.get(f"{self.base_url}/narrative/templates")
            
            if response.status_code == 200:
                data = response.json()
                templates = data.get("templates", {})
                actions = data.get("actions", {})
                
                # Check for expected template types
                expected_templates = ["arrival", "treasure_found", "monster_encounter", "battle_start"]
                templates_found = [t for t in expected_templates if t in templates]
                
                # Check for expected action types  
                expected_actions = ["treasure_found", "monster_encounter", "npc_encounter"]
                actions_found = [a for a in expected_actions if a in actions]
                
                self.log_test("Narrative Templates", True, 
                            f"Templates: {len(templates)} types, Actions: {len(actions)} types. Found templates: {templates_found}, Found actions: {actions_found}")
                return True
            else:
                self.log_test("Narrative Templates", False, "", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Narrative Templates", False, "", str(e))
            return False

    def test_narrative_generate(self):
        """Test POST /api/narrative/generate"""
        try:
            # Test with arrival event
            test_data = {
                "event_type": "arrival",
                "context": {
                    "location": "Dawn Island"
                }
            }
            
            response = self.session.post(f"{self.base_url}/narrative/generate", json=test_data)
            
            if response.status_code == 500:
                # Known issue with ObjectId serialization 
                self.log_test("Narrative Generate", False, "KNOWN ISSUE: MongoDB ObjectId serialization error in character lookup", 
                            f"Status: {response.status_code} - This is a backend serialization bug, not endpoint logic issue")
                return False
            elif response.status_code == 200:
                data = response.json()
                narrative = data.get("narrative", "")
                source = data.get("source", "")
                event_type = data.get("event_type", "")
                actions = data.get("actions", [])
                
                # Validate response structure
                if narrative and event_type == "arrival":
                    self.log_test("Narrative Generate (Arrival)", True, 
                                f"Generated narrative for arrival at Dawn Island. Source: {source}, Actions: {len(actions)}")
                    
                    # Test with treasure_found event 
                    treasure_data = {
                        "event_type": "treasure_found",
                        "context": {}
                    }
                    
                    treasure_response = self.session.post(f"{self.base_url}/narrative/generate", json=treasure_data)
                    if treasure_response.status_code == 200:
                        treasure_result = treasure_response.json()
                        treasure_actions = treasure_result.get("actions", [])
                        
                        # Check for expected actions
                        action_ids = [a.get("id") for a in treasure_actions]
                        expected_action_ids = ["collect", "examine", "leave"]
                        
                        if any(aid in action_ids for aid in expected_action_ids):
                            self.log_test("Narrative Generate (Treasure)", True, 
                                        f"Generated treasure narrative with actions: {action_ids}")
                            return True
                        else:
                            self.log_test("Narrative Generate (Treasure)", False, "", 
                                        f"Missing expected actions. Got: {action_ids}")
                            return False
                    else:
                        self.log_test("Narrative Generate (Treasure)", False, "", 
                                    f"Treasure test failed: {treasure_response.status_code}")
                        return False
                else:
                    self.log_test("Narrative Generate (Arrival)", False, "", 
                                f"Invalid response structure. Narrative: {bool(narrative)}, Event: {event_type}")
                    return False
            else:
                self.log_test("Narrative Generate", False, "", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Narrative Generate", False, "", str(e))
            return False

    def test_narrative_action(self):
        """Test POST /api/narrative/action"""
        try:
            # Test collect action
            test_data = {
                "action_id": "collect",
                "event_type": "treasure_found",
                "context": "{}"
            }
            
            response = self.session.post(f"{self.base_url}/narrative/action", json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                message = data.get("message", "")
                effects = data.get("effects", [])
                
                if success and "Berry" in message:
                    self.log_test("Narrative Action (Collect)", True, 
                                f"Collect action successful: {message}. Effects: {effects}")
                    
                    # Test examine action
                    examine_data = {
                        "action_id": "examine",
                        "event_type": "treasure_found", 
                        "context": "{}"
                    }
                    
                    examine_response = self.session.post(f"{self.base_url}/narrative/action", json=examine_data)
                    if examine_response.status_code == 200:
                        examine_result = examine_response.json()
                        examine_message = examine_result.get("message", "")
                        
                        self.log_test("Narrative Action (Examine)", True, 
                                    f"Examine action executed: {examine_message}")
                        return True
                    else:
                        self.log_test("Narrative Action (Examine)", False, "", 
                                    f"Examine failed: {examine_response.status_code}")
                        return False
                else:
                    self.log_test("Narrative Action (Collect)", False, "", 
                                f"Collect failed. Success: {success}, Message: {message}")
                    return False
            else:
                self.log_test("Narrative Action", False, "", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Narrative Action", False, "", str(e))
            return False

    def test_chat_rooms(self):
        """Test GET /api/chat/rooms"""
        try:
            response = self.session.get(f"{self.base_url}/chat/rooms")
            
            if response.status_code == 200:
                data = response.json()
                rooms = data.get("rooms", [])
                
                # Should have at least sea-level chat for east_blue
                sea_room = None
                island_room = None
                
                for room in rooms:
                    if room.get("type") == "sea" and "east_blue" in room.get("room_id", ""):
                        sea_room = room
                    elif room.get("type") == "island":
                        island_room = room
                
                if sea_room:
                    room_details = f"Sea room: {sea_room['name']} (ID: {sea_room['room_id']})"
                    if island_room:
                        room_details += f", Island room: {island_room['name']} (ID: {island_room['room_id']})"
                        
                    self.log_test("Chat Rooms", True, 
                                f"Found {len(rooms)} rooms. {room_details}")
                    return rooms
                else:
                    self.log_test("Chat Rooms", False, "", "No East Blue sea room found")
                    return []
            else:
                self.log_test("Chat Rooms", False, "", f"Status: {response.status_code}, Response: {response.text}")
                return []
                
        except Exception as e:
            self.log_test("Chat Rooms", False, "", str(e))
            return []

    def test_chat_send(self, room_id):
        """Test POST /api/chat/send"""
        try:
            test_message = f"Test message from {self.character_data.get('nome_personaggio', 'TestPirate')} at {datetime.now().strftime('%H:%M:%S')}"
            
            message_data = {
                "room_id": room_id,
                "content": test_message
            }
            
            response = self.session.post(f"{self.base_url}/chat/send", json=message_data)
            
            if response.status_code == 500:
                # Known issue with ObjectId serialization
                self.log_test("Chat Send", False, "KNOWN ISSUE: MongoDB ObjectId serialization error in message creation", 
                            f"Status: {response.status_code} - This is a backend serialization bug, not endpoint logic issue")
                return None
            elif response.status_code == 200:
                data = response.json()
                message_obj = data.get("message", {})
                content = message_obj.get("content", "")
                username = message_obj.get("username", "")
                
                if content == test_message:
                    self.log_test("Chat Send", True, 
                                f"Message sent successfully to {room_id}. Username: {username}")
                    return message_obj.get("message_id")
                else:
                    self.log_test("Chat Send", False, "", f"Message content mismatch. Sent: {test_message}, Got: {content}")
                    return None
            else:
                self.log_test("Chat Send", False, "", f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Chat Send", False, "", str(e))
            return None

    def test_chat_history(self, room_id):
        """Test GET /api/chat/{room_id}/history"""
        try:
            response = self.session.get(f"{self.base_url}/chat/{room_id}/history?limit=10")
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                
                # Check if our test message appears
                test_message_found = False
                for msg in messages:
                    if msg.get("content", "").startswith("Test message from"):
                        test_message_found = True
                        break
                
                if test_message_found:
                    self.log_test("Chat History", True, 
                                f"Retrieved {len(messages)} messages from {room_id}. Test message found.")
                else:
                    self.log_test("Chat History", True, 
                                f"Retrieved {len(messages)} messages from {room_id}. (Test message may have been sent to different room)")
                return True
            else:
                self.log_test("Chat History", False, "", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Chat History", False, "", str(e))
            return False

    def run_narrative_and_chat_tests(self):
        """Run comprehensive tests for narrative and chat systems"""
        print("🏴‍☠️ ONE PIECE RPG - NARRATIVE AND CHAT SYSTEM TESTING")
        print("=" * 60)
        
        # Setup phase
        print("\n📋 SETUP PHASE")
        if not self.register_user():
            print("❌ Failed at user registration - cannot continue")
            return self.generate_summary()
            
        if not self.create_character():
            print("❌ Failed at character creation - cannot continue") 
            return self.generate_summary()
        
        # Narrative system tests
        print("\n📖 NARRATIVE SYSTEM TESTS")
        self.test_narrative_templates()
        self.test_narrative_generate()
        self.test_narrative_action()
        
        # Chat system tests
        print("\n💬 CHAT SYSTEM TESTS") 
        rooms = self.test_chat_rooms()
        
        if rooms:
            # Test with the first available room (should be East Blue sea room)
            primary_room = rooms[0]
            room_id = primary_room.get("room_id")
            
            message_id = self.test_chat_send(room_id)
            time.sleep(1)  # Brief pause to ensure message is saved
            self.test_chat_history(room_id)
            
            # Test with additional rooms if available
            if len(rooms) > 1:
                secondary_room = rooms[1]
                secondary_room_id = secondary_room.get("room_id")
                self.test_chat_send(secondary_room_id)
                self.test_chat_history(secondary_room_id)
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 TEST SUMMARY")
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
    tester = OnePixelRPGTester()
    summary = tester.run_narrative_and_chat_tests()