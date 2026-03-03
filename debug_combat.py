#!/usr/bin/env python3

import requests
import json

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

# Manual test to debug battle system
session = requests.Session()

# Register user
import random
random_id = random.randint(100000, 999999)
user_data = {
    "username": f"debuguser{random_id}",
    "email": f"debuguser{random_id}@example.com", 
    "password": "testpassword123"
}

print("Testing Combat Level System manually...")

# 1. Register
response = session.post(f"{BASE_URL}/auth/register", json=user_data)
print(f"Register: {response.status_code}")
if response.status_code == 200:
    token = response.json()["token"]
    session.headers.update({"Authorization": f"Bearer {token}"})
    
    # 2. Create character
    char_data = {
        "nome_personaggio": "DebugPirate",
        "ruolo": "Pirata",
        "genere": "maschio",
        "eta": 20,
        "razza": "umano",
        "stile_combattimento": "corpo_misto",
        "sogno": "Test combat system",
        "storia_carattere": "Debug character",
        "mestiere": "guerriero",
        "mare_partenza": "east_blue"
    }
    
    char_response = session.post(f"{BASE_URL}/characters", json=char_data)
    print(f"Create character: {char_response.status_code}")
    
    if char_response.status_code == 200:
        char = char_response.json()
        print(f"Character created: {char['nome_personaggio']}")
        print(f"Combat level: {char.get('livello_combattimento', 'MISSING')}")
        
        # 3. Start battle
        battle_data = {
            "opponent_type": "npc",
            "opponent_id": "pirata_novizio"
        }
        
        battle_response = session.post(f"{BASE_URL}/battle/start", json=battle_data)
        print(f"Start battle: {battle_response.status_code}")
        
        if battle_response.status_code == 200:
            battle = battle_response.json()
            battle_id = battle.get("battle_id")
            print(f"Battle ID: {battle_id}")
            print(f"Initial log: {battle.get('log', [])}")
            
            # 4. Attack 
            attack_data = {
                "action_type": "attacco_base",
                "action_name": "Pugno"
            }
            
            attack_response = session.post(f"{BASE_URL}/battle/{battle_id}/action", json=attack_data)
            print(f"Attack: {attack_response.status_code}")
            
            if attack_response.status_code == 200:
                response_data = attack_response.json()
                result = response_data.get('result', {})
                battle_state = response_data.get('battle', {})
                
                print(f"Response structure: {list(response_data.keys())}")
                print(f"Battle log: {battle_state.get('log', [])}")
                print(f"Battle finished: {result.get('battaglia_finita', False)}")
                print(f"Player1 vita: {battle_state.get('player1', {}).get('vita', 'Unknown')}")
                print(f"Player2 vita: {battle_state.get('player2', {}).get('vita', 'Unknown')}")
                
                if result.get('battaglia_finita'):
                    rewards = battle_state.get('rewards', {})
                    print(f"Rewards: {rewards}")
            else:
                print(f"Attack failed: {attack_response.text}")
        else:
            print(f"Battle start failed: {battle_response.text}")
    else:
        print(f"Character creation failed: {char_response.text}")
else:
    print(f"Registration failed: {response.text}")