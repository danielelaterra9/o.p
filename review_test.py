#!/usr/bin/env python3

import asyncio
import httpx
import json
import random

# Test the specific endpoints mentioned in the review request
async def test_specific_endpoints():
    client = httpx.AsyncClient(timeout=30.0)
    backend_url = "https://saved-check.preview.emergentagent.com/api"
    
    try:
        print("🎯 TESTING SPECIFIC REVIEW REQUEST ENDPOINTS")
        print("=" * 50)
        
        # 1. Create test user
        test_id = str(random.randint(1000000, 9999999))
        register_data = {
            "username": f"ReviewTest{test_id}",
            "email": f"reviewtest{test_id}@test.com", 
            "password": "testpassword123"
        }
        
        response = await client.post(f"{backend_url}/auth/register", json=register_data)
        if response.status_code != 200:
            print(f"❌ User registration failed: {response.text}")
            return
        
        user_token = response.json()["token"]
        print("✅ User created successfully")
        
        # 2. Create character
        character_data = {
            "nome_personaggio": f"ReviewPirate{test_id}",
            "genere": "maschio",
            "eta": 19,
            "razza": "umano", 
            "stile_combattimento": "corpo_misto",
            "sogno": "Test the specific endpoints",
            "storia_carattere": "A pirate testing the review request endpoints",
            "mestiere": "capitano",
            "mare_partenza": "east_blue"
        }
        
        headers = {"Authorization": f"Bearer {user_token}"}
        response = await client.post(f"{backend_url}/characters", json=character_data, headers=headers)
        if response.status_code != 200:
            print(f"❌ Character creation failed: {response.text}")
            return
        
        print("✅ Character created successfully")
        
        # 3. Test POST /api/narrative/generate with exact data from review
        print("\n📖 Testing POST /api/narrative/generate")
        narrative_data = {
            "event_type": "arrival",
            "context": {"location": "Dawn Island"}
        }
        
        response = await client.post(f"{backend_url}/narrative/generate", json=narrative_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Narrative generation successful!")
            print(f"   - Source: {result.get('source', 'unknown')}")
            print(f"   - Length: {len(result.get('narrative', ''))} chars")
            print(f"   - Narrative: {result.get('narrative', '')[:100]}...")
        else:
            print(f"❌ Narrative generation failed: Status {response.status_code}")
            if response.status_code == 500:
                print("   🐛 Still has ObjectId serialization bug!")
            return
        
        # 4. Test POST /api/chat/send with exact data from review  
        print("\n💬 Testing POST /api/chat/send")
        chat_data = {
            "room_id": "mare_east_blue",
            "content": "Test message"
        }
        
        response = await client.post(f"{backend_url}/chat/send", json=chat_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            message = result["message"]
            print(f"✅ Chat message sending successful!")
            print(f"   - Room: {message.get('room_id')}")
            print(f"   - User: {message.get('username')}")
            print(f"   - Content: {message.get('content')}")
            print(f"   - Message ID: {message.get('message_id')}")
        else:
            print(f"❌ Chat message sending failed: Status {response.status_code}")
            if response.status_code == 500:
                print("   🐛 Still has ObjectId serialization bug!")
            return
        
        print("\n🎉 ALL REVIEW REQUEST ENDPOINTS WORKING CORRECTLY!")
        print("✅ Both endpoints now work without 500 ObjectId serialization errors")
        
    except Exception as e:
        print(f"💥 Test error: {e}")
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(test_specific_endpoints())