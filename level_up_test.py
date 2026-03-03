#!/usr/bin/env python3

import requests
import json
import time

# Get backend URL
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.strip().split('=')[1] + '/api'
    except:
        pass
    return "http://localhost:8001/api"

BASE_URL = get_backend_url()

def test_single_battle():
    """Test a complete battle to verify level up system works"""
    session = requests.Session()
    
    # Register user
    import random
    random_id = random.randint(100000, 999999)
    user_data = {
        "username": f"leveltest{random_id}",
        "email": f"leveltest{random_id}@example.com", 
        "password": "testpassword123"
    }
    
    print("🎯 Testing Level Up System with Single Battle")
    
    # 1. Register
    response = session.post(f"{BASE_URL}/auth/register", json=user_data)
    if response.status_code != 200:
        print("❌ Registration failed")
        return
        
    token = response.json()["token"]
    session.headers.update({"Authorization": f"Bearer {token}"})
    print("✅ User registered")
    
    # 2. Create character with stronger race for better chance
    char_data = {
        "nome_personaggio": "LevelTester",
        "ruolo": "Pirata",
        "genere": "maschio",
        "eta": 20,
        "razza": "semi_gigante",  # Stronger race
        "stile_combattimento": "corpo_pugni",  # Stronger style
        "sogno": "Test level system",
        "storia_carattere": "Strong fighter for testing",
        "mestiere": "guerriero",
        "mare_partenza": "east_blue"
    }
    
    char_response = session.post(f"{BASE_URL}/characters", json=char_data)
    if char_response.status_code != 200:
        print("❌ Character creation failed")
        return
        
    character = char_response.json()
    print(f"✅ Character created: {character['nome_personaggio']}")
    print(f"   Level: {character['livello_combattimento']}, EXP: {character['esperienza_totale']}")
    print(f"   Vita: {character['vita']}, Attacco: {character['attacco']}")
    
    # 3. Fight until we win or max attempts
    attempts = 0
    max_attempts = 20
    
    while attempts < max_attempts:
        attempts += 1
        print(f"\n🥊 Battle Attempt {attempts}")
        
        # Start battle
        battle_data = {"opponent_type": "npc", "opponent_id": "pirata_novizio"}
        battle_response = session.post(f"{BASE_URL}/battle/start", json=battle_data)
        
        if battle_response.status_code != 200:
            print("❌ Battle start failed")
            continue
            
        battle = battle_response.json()["battle"]
        battle_id = battle["battle_id"]
        
        print(f"   Battle ID: {battle_id}")
        print(f"   Player HP: {battle['player1']['vita']}, Enemy HP: {battle['player2']['vita']}")
        
        # Fight until battle ends
        fight_turns = 0
        max_turns = 15
        
        while fight_turns < max_turns:
            fight_turns += 1
            
            attack_data = {"action_type": "attacco_base", "action_name": "Pugno"}
            attack_response = session.post(f"{BASE_URL}/battle/{battle_id}/action", json=attack_data)
            
            if attack_response.status_code != 200:
                print(f"   ❌ Attack {fight_turns} failed")
                break
                
            response_data = attack_response.json()
            result = response_data.get('result', {})
            battle_state = response_data.get('battle', {})
            
            # Show last log entry
            log = battle_state.get('log', [])
            if log:
                print(f"   Turn {fight_turns}: {log[-1]}")
            
            if result.get('battaglia_finita'):
                print(f"\n🏁 Battle finished after {fight_turns} turns")
                winner = result.get('vincitore')
                print(f"   Winner: {winner}")
                
                if winner == "player1":
                    print("🎉 VICTORY! Checking rewards...")
                    rewards = battle_state.get('rewards', {})
                    
                    print("📊 Reward Structure:")
                    for key, value in rewards.items():
                        print(f"   {key}: {value}")
                    
                    # Verify required fields
                    required_fields = [
                        "exp_gained", "exp_multiplier", "leveled_up", 
                        "current_exp", "exp_for_next_level", "total_exp"
                    ]
                    
                    missing_fields = [f for f in required_fields if f not in rewards]
                    if missing_fields:
                        print(f"❌ Missing reward fields: {missing_fields}")
                    else:
                        print("✅ All required reward fields present")
                        
                        if rewards.get('leveled_up'):
                            print(f"🎉 LEVEL UP! From {rewards.get('old_level')} to {rewards.get('new_level')}")
                        else:
                            print(f"📈 EXP gained: {rewards['exp_gained']} (x{rewards['exp_multiplier']} multiplier)")
                        
                        print(f"📊 Progress: {rewards['current_exp']}/{rewards['exp_for_next_level']} EXP to next level")
                    
                    return True  # Success!
                    
                elif winner == "player2":
                    print("💀 Defeat... Checking consolation EXP...")
                    rewards = battle_state.get('rewards', {})
                    
                    if rewards.get('defeat_exp'):
                        print(f"📈 Consolation EXP: +{rewards.get('exp_gained', 0)}")
                    else:
                        print("❌ No consolation EXP found")
                break
            
            time.sleep(0.1)  # Small delay
            
        if fight_turns >= max_turns:
            print(f"   ⏰ Battle timed out after {max_turns} turns")
    
    print(f"\n❌ Failed to win battle after {attempts} attempts")
    return False

if __name__ == "__main__":
    test_single_battle()