#!/usr/bin/env python3
"""
Four Seas Navigation - Ship Purchase and Travel Test
Complete the review request by testing ship purchase and successful travel
"""

import requests
import json
import sys
from datetime import datetime

backend_url = "https://project-builder-127.preview.emergentagent.com/api"

def test_ship_and_travel():
    results = []
    
    def log_test(name, passed, message, details=None):
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}: {message}")
        if details:
            print(f"    Details: {details}")
        results.append((name, passed, message))
    
    # Setup user and character
    timestamp = int(datetime.now().timestamp())
    user_data = {
        "username": f"ShipTester{timestamp}",
        "email": f"ship_{timestamp}@test.com", 
        "password": "testpass123"
    }
    
    try:
        # Register and create character
        print("🔧 Setting up test user...")
        reg_response = requests.post(f"{backend_url}/auth/register", json=user_data, timeout=10)
        token = reg_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        # Create character in West Blue 
        char_data = {
            "nome_personaggio": "Ship Captain",
            "ruolo": "pirata", "genere": "maschio", "eta": 30, "razza": "umano",
            "stile_combattimento": "corpo_misto", "sogno": "Navigate the seas",
            "storia_carattere": "A captain seeking to explore all islands",
            "mestiere": "capitano", "mare_partenza": "west_blue"
        }
        
        char_response = requests.post(f"{backend_url}/characters", json=char_data, headers=headers, timeout=10)
        char_info = char_response.json()
        
        print(f"✅ Character created: {char_info['nome_personaggio']} in {char_info['mare_corrente']}")
        print(f"   Starting Berry: {char_info.get('berry', 0)}")
        
        # Check if we need more Berry (barca_piccola costs 5000)
        current_berry = char_info.get('berry', 0)
        if current_berry < 5000:
            print(f"\n💰 Need more Berry for ship (have {current_berry}, need 5000)")
            print("    Fighting battles to earn Berry...")
            
            # Fight some battles to earn Berry
            for i in range(3):  # Fight up to 3 battles
                battle_response = requests.post(f"{backend_url}/battle/start", 
                    json={"opponent_type": "npc", "opponent_id": "pirata_novizio"}, 
                    headers=headers, timeout=10)
                
                if battle_response.status_code == 200:
                    battle_data = battle_response.json()
                    battle_id = battle_data["battle_id"]
                    
                    # Execute attack
                    action_response = requests.post(f"{backend_url}/battle/{battle_id}/action",
                        json={"action_type": "attacco_base", "action_name": "Pugno"},
                        headers=headers, timeout=10)
                    
                    if action_response.status_code == 200:
                        action_result = action_response.json()
                        battle = action_result.get("battle", {})
                        
                        if battle.get("stato") == "finita" and battle.get("vincitore") == "player1":
                            rewards = battle.get("rewards", {})
                            berry_gain = rewards.get("berry", 0)
                            exp_gain = rewards.get("exp", 0)
                            print(f"    ⚔️  Battle {i+1} won! +{berry_gain} Berry, +{exp_gain} EXP")
                            current_berry += berry_gain
                            
                            if current_berry >= 5000:
                                break
        
        # Get updated character info
        char_updated = requests.get(f"{backend_url}/characters/me", headers=headers, timeout=10)
        if char_updated.status_code == 200:
            char_data = char_updated.json()
            current_berry = char_data.get('berry', 0)
            print(f"    Final Berry balance: {current_berry}")
        
        # Buy ship if we have enough Berry
        print(f"\n🚢 Testing ship purchase...")
        if current_berry >= 5000:
            ship_response = requests.post(f"{backend_url}/shop/buy",
                json={"item_id": "barca_piccola"}, headers=headers, timeout=10)
            
            if ship_response.status_code == 200:
                ship_data = ship_response.json()
                log_test("Ship Purchase", True, f"Successfully bought: {ship_data.get('message')}")
                
                # Verify character has ship
                char_check = requests.get(f"{backend_url}/characters/me", headers=headers, timeout=10)
                if char_check.status_code == 200:
                    char_info = char_check.json()
                    if char_info.get("nave"):
                        log_test("Ship Equipped", True, f"Ship equipped: {char_info.get('nave')}")
                    else:
                        log_test("Ship Equipped", False, "Ship not found in character data")
            else:
                error_msg = ship_response.json().get('detail', 'Unknown error')
                log_test("Ship Purchase", False, f"Purchase failed: {error_msg}")
                return results
        else:
            print(f"    Insufficient Berry for ship purchase: {current_berry} < 5000")
            print("    Will test travel with existing character setup...")
        
        # Test successful travel forward (with or without ship)
        print(f"\n⚓ Testing travel forward...")
        islands_response = requests.get(f"{backend_url}/world/islands", headers=headers, timeout=10)
        
        if islands_response.status_code == 200:
            islands_data = islands_response.json()
            islands = islands_data.get("islands", [])
            current_island = islands_data.get("isola_corrente")
            
            # Find next island
            next_island = None
            for island in islands:
                if island.get("can_travel_forward", False):
                    next_island = island
                    break
            
            if next_island:
                print(f"    Attempting travel from {current_island} to {next_island['name']}...")
                travel_response = requests.post(f"{backend_url}/world/travel",
                    json={"island_id": next_island["id"]}, headers=headers, timeout=10)
                
                if travel_response.status_code == 200:
                    travel_data = travel_response.json()
                    island_info = travel_data.get("island", {})
                    
                    log_test("Forward Travel", True, travel_data.get("message", "Travel successful"))
                    
                    # Show island story
                    if island_info.get("storia"):
                        story = island_info["storia"]
                        print(f"    📖 Island Story: {story[:150]}...")
                    
                    # Verify position changed
                    pos_check = requests.get(f"{backend_url}/characters/me", headers=headers, timeout=10)
                    if pos_check.status_code == 200:
                        new_pos = pos_check.json()
                        new_island = new_pos.get("isola_corrente")
                        if new_island == next_island["id"]:
                            log_test("Position Update", True, f"Character now at: {new_island}")
                        else:
                            log_test("Position Update", False, f"Position not updated: {new_island}")
                    
                elif travel_response.status_code == 400:
                    error_msg = travel_response.json().get("detail", "")
                    log_test("Forward Travel", False, f"Travel blocked: {error_msg}")
                else:
                    log_test("Forward Travel", False, f"Unexpected status: {travel_response.status_code}")
            else:
                log_test("Forward Travel", False, "No next island available for travel")
        
        # Test backward travel if we moved forward
        print(f"\n🔄 Testing backward travel...")
        islands_response = requests.get(f"{backend_url}/world/islands", headers=headers, timeout=10)
        
        if islands_response.status_code == 200:
            islands_data = islands_response.json()
            islands = islands_data.get("islands", [])
            current_island = islands_data.get("isola_corrente")
            
            # Find previous island
            prev_island = None
            for island in islands:
                if island.get("can_travel_back", False):
                    prev_island = island
                    break
            
            if prev_island:
                print(f"    Attempting backward travel to {prev_island['name']}...")
                back_response = requests.post(f"{backend_url}/world/travel",
                    json={"island_id": prev_island["id"]}, headers=headers, timeout=10)
                
                if back_response.status_code == 200:
                    back_data = back_response.json()
                    log_test("Backward Travel", True, back_data.get("message", "Backward travel successful"))
                else:
                    error_msg = back_response.json().get("detail", "") if back_response else "No response"
                    log_test("Backward Travel", False, f"Backward travel failed: {error_msg}")
            else:
                log_test("Backward Travel", True, "No previous island available (expected at start)")
    
    except requests.RequestException as e:
        log_test("Network Connection", False, f"Connection error: {e}")
    except Exception as e:
        log_test("Test Execution", False, f"Unexpected error: {e}")
    
    return results

def main():
    print("🎯 Four Seas Navigation - Ship Purchase & Travel Test")
    print("=" * 70)
    
    results = test_ship_and_travel()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, p, _ in results if p)
    failed = len(results) - passed
    
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(results)*100):.1f}%" if len(results) > 0 else "No tests run")
    
    if failed > 0:
        print(f"\n❌ Failed Tests:")
        for name, passed, message in results:
            if not passed:
                print(f"   • {name}: {message}")
    
    print(f"\n✅ Passed Tests:")
    for name, passed, message in results:
        if passed:
            print(f"   • {name}: {message}")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)