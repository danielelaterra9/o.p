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
session = requests.Session()

# Register and setup
import random
random_id = random.randint(100000, 999999)
user_data = {
    "username": f"quicktest{random_id}",
    "email": f"quicktest{random_id}@example.com", 
    "password": "testpassword123"
}

response = session.post(f"{BASE_URL}/auth/register", json=user_data)
token = response.json()["token"]
session.headers.update({"Authorization": f"Bearer {token}"})

# Create character
char_data = {
    "nome_personaggio": "QuickTester",
    "ruolo": "Pirata", "genere": "maschio", "eta": 20,
    "razza": "umano", "stile_combattimento": "corpo_misto",
    "sogno": "Quick test", "storia_carattere": "Quick test",
    "mestiere": "guerriero", "mare_partenza": "east_blue"
}
char_response = session.post(f"{BASE_URL}/characters", json=char_data)
character = char_response.json()

print(f"Character: {character['nome_personaggio']}")
print(f"Combat level: {character['livello_combattimento']}")

# Start battle
battle_data = {"opponent_type": "npc", "opponent_id": "pirata_novizio"}
battle_response = session.post(f"{BASE_URL}/battle/start", json=battle_data)
battle_info = battle_response.json()["battle"]
battle_id = battle_info["battle_id"]

print(f"Battle ID: {battle_id}")
print(f"Turn: {battle_info['turno_corrente']}")
print(f"Player1 is: {battle_info['player1']['nome']}")
print(f"Player2 is: {battle_info['player2']['nome']}")

# Test single attack
print("\n=== Testing single attack ===")
attack_data = {"action_type": "attacco_base", "action_name": "Pugno"}
attack_response = session.post(f"{BASE_URL}/battle/{battle_id}/action", json=attack_data)

print(f"Attack response status: {attack_response.status_code}")

if attack_response.status_code == 200:
    response_data = attack_response.json()
    print(f"Response keys: {list(response_data.keys())}")
    
    result = response_data.get('result', {})
    battle_state = response_data.get('battle', {})
    
    print(f"Result keys: {list(result.keys())}")
    print(f"Battle state keys: {list(battle_state.keys())}")
    
    log = battle_state.get('log', [])
    print(f"Log entries: {len(log)}")
    for i, entry in enumerate(log):
        print(f"  {i+1}: {entry}")
        
    print(f"Current turn: {battle_state.get('turno_corrente')}")
    print(f"Player1 HP: {battle_state.get('player1', {}).get('vita')}")
    print(f"Player2 HP: {battle_state.get('player2', {}).get('vita')}")
    
elif attack_response.status_code == 400:
    error_detail = attack_response.json().get('detail', 'Unknown error')
    print(f"Error: {error_detail}")
else:
    print(f"Error: {attack_response.text}")