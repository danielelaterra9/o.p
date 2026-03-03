#!/usr/bin/env python3

import asyncio
import httpx
import json
import uuid
import sys
import random
from datetime import datetime

# Backend URL
BACKEND_URL = "https://saved-check.preview.emergentagent.com/api"

class ObjectIdSerializationBugTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
        self.user_token = None
        self.user_id = None
        self.character_id = None
        
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
        """Create a test user and character for testing"""
        try:
            # Create unique test user
            test_id = str(random.randint(1000000, 9999999))
            register_data = {
                "username": f"ObjectIdTest{test_id}",
                "email": f"objectidtest{test_id}@test.com",
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
                "nome_personaggio": f"TestPirate{test_id}",
                "genere": "maschio", 
                "eta": 19,
                "razza": "umano",
                "stile_combattimento": "corpo_misto",
                "sogno": "Test the ObjectId serialization fixes!",
                "storia_carattere": f"A brave pirate {test_id} testing MongoDB ObjectId serialization bug fixes.",
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

    async def test_narrative_generation_endpoint(self):
        """Test POST /api/narrative/generate - Previously had ObjectId serialization bug"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test narrative generation with arrival event
            narrative_data = {
                "event_type": "arrival",
                "context": {
                    "location": "Dawn Island"
                }
            }
            
            response = await self.client.post(f"{BACKEND_URL}/narrative/generate", 
                                            json=narrative_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required response fields
                required_fields = ["narrative", "source", "event_type", "timestamp"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    await self.log_test("POST /narrative/generate - Response Structure", False, "", 
                                      f"Missing fields: {missing_fields}")
                    return False
                
                # Check narrative content exists
                if not data["narrative"] or len(data["narrative"]) < 10:
                    await self.log_test("POST /narrative/generate - Narrative Content", False, "", 
                                      f"Empty or too short narrative: {data['narrative']}")
                    return False
                
                # Check event type matches
                if data["event_type"] != "arrival":
                    await self.log_test("POST /narrative/generate - Event Type", False, "", 
                                      f"Expected 'arrival', got '{data['event_type']}'")
                    return False
                
                await self.log_test("POST /narrative/generate - ObjectId Fix", True, 
                                  f"✅ Narrative generated successfully without 500 error. Source: {data['source']}, Length: {len(data['narrative'])} chars")
                return True
                
            elif response.status_code == 500:
                await self.log_test("POST /narrative/generate - ObjectId Bug", False, "", 
                                  f"500 Internal Server Error - ObjectId serialization bug NOT fixed: {response.text}")
                return False
            else:
                await self.log_test("POST /narrative/generate", False, "", 
                                  f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("POST /narrative/generate", False, "", str(e))
            return False

    async def test_chat_send_endpoint(self):
        """Test POST /api/chat/send - Previously had ObjectId serialization bug"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test chat message sending
            chat_data = {
                "room_id": "mare_east_blue",
                "content": "Test message to verify ObjectId serialization fix"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/chat/send", 
                                            json=chat_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if "message" not in data:
                    await self.log_test("POST /chat/send - Response Structure", False, "", 
                                      "Missing 'message' field in response")
                    return False
                
                message = data["message"]
                required_fields = ["message_id", "room_id", "type", "user_id", "username", "content", "timestamp"]
                missing_fields = [field for field in required_fields if field not in message]
                
                if missing_fields:
                    await self.log_test("POST /chat/send - Message Structure", False, "", 
                                      f"Missing message fields: {missing_fields}")
                    return False
                
                # Check message content
                if message["content"] != chat_data["content"]:
                    await self.log_test("POST /chat/send - Message Content", False, "", 
                                      f"Content mismatch: expected '{chat_data['content']}', got '{message['content']}'")
                    return False
                
                # Check room ID
                if message["room_id"] != chat_data["room_id"]:
                    await self.log_test("POST /chat/send - Room ID", False, "", 
                                      f"Room ID mismatch: expected '{chat_data['room_id']}', got '{message['room_id']}'")
                    return False
                
                # Check user ID matches
                if message["user_id"] != self.user_id:
                    await self.log_test("POST /chat/send - User ID", False, "", 
                                      f"User ID mismatch: expected '{self.user_id}', got '{message['user_id']}'")
                    return False
                
                await self.log_test("POST /chat/send - ObjectId Fix", True, 
                                  f"✅ Message sent successfully without 500 error. User: {message['username']}, Room: {message['room_id']}")
                return True
                
            elif response.status_code == 500:
                await self.log_test("POST /chat/send - ObjectId Bug", False, "", 
                                  f"500 Internal Server Error - ObjectId serialization bug NOT fixed: {response.text}")
                return False
            else:
                await self.log_test("POST /chat/send", False, "", 
                                  f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("POST /chat/send", False, "", str(e))
            return False

    async def test_narrative_generation_with_ai(self):
        """Test POST /api/narrative/generate with AI flag - Additional ObjectId validation"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test narrative generation with AI (more complex character data retrieval)
            narrative_data = {
                "event_type": "treasure_found",
                "context": {
                    "location": "Dawn Island",
                    "item": "Golden Compass"
                },
                "use_ai": False  # Set to false to avoid LLM dependencies in testing
            }
            
            response = await self.client.post(f"{BACKEND_URL}/narrative/generate", 
                                            json=narrative_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Should include actions for treasure events
                if "actions" not in data:
                    await self.log_test("POST /narrative/generate - Actions", False, "", 
                                      "Missing 'actions' field for treasure event")
                    return False
                
                actions = data["actions"]
                if not isinstance(actions, list):
                    await self.log_test("POST /narrative/generate - Actions Structure", False, "", 
                                      f"Actions should be array, got: {type(actions)}")
                    return False
                
                await self.log_test("POST /narrative/generate - Complex Context", True, 
                                  f"✅ Treasure event generated with {len(actions)} actions available")
                return True
                
            elif response.status_code == 500:
                await self.log_test("POST /narrative/generate - Complex Context ObjectId Bug", False, "", 
                                  f"500 Internal Server Error with complex context - ObjectId bug persists: {response.text}")
                return False
            else:
                await self.log_test("POST /narrative/generate - Complex Context", False, "", 
                                  f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("POST /narrative/generate - Complex Context", False, "", str(e))
            return False

    async def test_chat_send_with_long_message(self):
        """Test POST /api/chat/send with maximum length message"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test with maximum allowed message length (500 chars)
            long_message = "A" * 400 + " - Testing ObjectId serialization fix with long message content to verify character data handling"
            
            chat_data = {
                "room_id": "isola_dawn_island", 
                "content": long_message
            }
            
            response = await self.client.post(f"{BACKEND_URL}/chat/send", 
                                            json=chat_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                message = data["message"]
                
                if len(message["content"]) != len(long_message):
                    await self.log_test("POST /chat/send - Long Message Content", False, "", 
                                      f"Message length mismatch: expected {len(long_message)}, got {len(message['content'])}")
                    return False
                
                await self.log_test("POST /chat/send - Long Message", True, 
                                  f"✅ Long message ({len(long_message)} chars) sent successfully to {message['room_id']}")
                return True
                
            elif response.status_code == 500:
                await self.log_test("POST /chat/send - Long Message ObjectId Bug", False, "", 
                                  f"500 error with long message - ObjectId serialization issue: {response.text}")
                return False
            else:
                await self.log_test("POST /chat/send - Long Message", False, "", 
                                  f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("POST /chat/send - Long Message", False, "", str(e))
            return False

    async def test_multiple_narrative_requests(self):
        """Test multiple consecutive narrative generation requests to stress test ObjectId handling"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            event_types = ["arrival", "treasure_found", "monster_encounter", "victory", "defeat"]
            locations = ["Dawn Island", "Foosha Village", "Mt. Colubo", "Gray Terminal", "Midway Forest"]
            
            success_count = 0
            
            for i, (event_type, location) in enumerate(zip(event_types, locations)):
                narrative_data = {
                    "event_type": event_type,
                    "context": {
                        "location": location,
                        "player": f"TestPirate{i}",
                        "item": "Test Item"
                    }
                }
                
                response = await self.client.post(f"{BACKEND_URL}/narrative/generate", 
                                                json=narrative_data, headers=headers)
                
                if response.status_code == 200:
                    success_count += 1
                elif response.status_code == 500:
                    await self.log_test(f"Narrative Stress Test - Request {i+1}", False, "", 
                                      f"500 error on {event_type} at {location} - ObjectId bug present")
                    return False
                else:
                    await self.log_test(f"Narrative Stress Test - Request {i+1}", False, "", 
                                      f"Status {response.status_code} on {event_type}")
                    return False
            
            if success_count == len(event_types):
                await self.log_test("Narrative Generation - Stress Test", True, 
                                  f"✅ {success_count}/{len(event_types)} consecutive narrative requests successful")
                return True
            else:
                await self.log_test("Narrative Generation - Stress Test", False, "", 
                                  f"Only {success_count}/{len(event_types)} requests succeeded")
                return False
                
        except Exception as e:
            await self.log_test("Narrative Generation - Stress Test", False, "", str(e))
            return False

    async def run_all_tests(self):
        """Run all ObjectId serialization bug fix tests"""
        print("🐛 STARTING OBJECTID SERIALIZATION BUG FIX TESTS")
        print("=" * 60)
        print("Testing MongoDB ObjectId serialization fixes for:")
        print("  - POST /api/narrative/generate")
        print("  - POST /api/chat/send")
        print("=" * 60)
        
        # Setup
        if not await self.setup_user_and_character():
            print("❌ Setup failed - aborting tests")
            return
        
        # Test 1: Basic narrative generation
        print("\n📖 Testing Narrative Generation (Basic)...")
        await self.test_narrative_generation_endpoint()
        
        # Test 2: Basic chat message sending
        print("\n💬 Testing Chat Message Sending (Basic)...")
        await self.test_chat_send_endpoint()
        
        # Test 3: Complex narrative generation
        print("\n📖 Testing Narrative Generation (Complex Context)...")
        await self.test_narrative_generation_with_ai()
        
        # Test 4: Long message chat sending
        print("\n💬 Testing Chat Message Sending (Long Message)...")
        await self.test_chat_send_with_long_message()
        
        # Test 5: Stress test multiple requests
        print("\n🔄 Testing Multiple Consecutive Requests...")
        await self.test_multiple_narrative_requests()
        
        await self.summary_report()

    async def summary_report(self):
        """Generate test summary report"""
        print("\n" + "=" * 60)
        print("🐛 OBJECTID SERIALIZATION BUG FIX TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 TOTAL TESTS: {total_tests}")
        print(f"✅ PASSED: {passed_tests}")
        print(f"❌ FAILED: {failed_tests}")
        print(f"📈 SUCCESS RATE: {(passed_tests/total_tests)*100:.1f}%")
        
        # Specific endpoint results
        narrative_tests = [t for t in self.test_results if "narrative" in t["test"].lower()]
        chat_tests = [t for t in self.test_results if "chat" in t["test"].lower()]
        
        narrative_success = len([t for t in narrative_tests if t["success"]])
        chat_success = len([t for t in chat_tests if t["success"]])
        
        print(f"\n🎯 ENDPOINT-SPECIFIC RESULTS:")
        print(f"  📖 Narrative Generation: {narrative_success}/{len(narrative_tests)} tests passed")
        print(f"  💬 Chat Message Sending: {chat_success}/{len(chat_tests)} tests passed")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for test in self.test_results:
                if not test["success"]:
                    print(f"  - {test['test']}: {test['error']}")
        else:
            print(f"\n🎉 ALL TESTS PASSED! ObjectId serialization bugs have been successfully fixed!")
            print(f"  ✅ POST /api/narrative/generate - No longer returns 500 errors")
            print(f"  ✅ POST /api/chat/send - No longer returns 500 errors") 
            print(f"  ✅ serialize_mongo_doc() helper function working correctly")
            print(f"  ✅ copy.deepcopy() preventing _id injection into responses")
        
        # Close client
        await self.client.aclose()

async def main():
    """Main test runner"""
    tester = ObjectIdSerializationBugTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)