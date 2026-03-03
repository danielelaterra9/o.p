#!/usr/bin/env python3
"""
Additional Navigation Flow Test for Four Seas System
"""

import requests
import json
import random
import string

# Configuration
BASE_URL = "https://saved-check.preview.emergentagent.com/api"

def test_navigation_flow():
    """Test the complete navigation flow"""
    print("\n🚢 TESTING NAVIGATION FLOW")
    print("-" * 50)
    
    # Setup - Register and login
    random_suffix = ''.join(random.choices(string.digits, k=6))
    username = f"NavTester{random_suffix}"
    email = f"navtest{random_suffix}@test.com"
    password = "NavTestPass123!"

    session = requests.Session()

    # Register
    register_data = {
        "username": username,
        "email": email,
        "password": password
    }
    
    register_response = session.post(f"{BASE_URL}/auth/register", json=register_data)
    if register_response.status_code != 200:
        print(f"❌ Registration failed: {register_response.text}")
        return False
    
    token = register_response.json().get("token")
    session.headers.update({"Authorization": f"Bearer {token}"})
    
    # Create character
    character_data = {
        "nome_personaggio": "Test Navigator",
        "ruolo": "capitano",
        "genere": "maschio",
        "eta": 25,
        "razza": "umano",
        "stile_combattimento": "corpo_pugni",
        "sogno": "Navigare tutti i mari",
        "storia_carattere": "Un esperto navigatore che vuole esplorare tutti e quattro i mari.",
        "mestiere": "navigatore",
        "mare_partenza": "east_blue"
    }

    char_response = session.post(f"{BASE_URL}/characters", json=character_data)
    if char_response.status_code != 200:
        print(f"❌ Character creation failed: {char_response.text}")
        return False
    
    character = char_response.json()
    print(f"✅ Character created at {character.get('isola_corrente')} in {character.get('mare_corrente')}")
    
    # Test travel attempt without ship (should fail)
    try:
        travel_data = {"island_id": "shells_town"}
        travel_response = session.post(f"{BASE_URL}/world/travel", json=travel_data)
        
        if travel_response.status_code == 400:
            error_msg = travel_response.json().get("detail", "")
            if "nave" in error_msg.lower():
                print("✅ Navigation correctly blocked without ship")
                return True
            else:
                print(f"✅ Navigation blocked with message: {error_msg}")
                return True
        else:
            print(f"❌ Travel should have failed but got: {travel_response.status_code} - {travel_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Navigation test error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_navigation_flow()
    print(f"\n🏁 Navigation Flow Test: {'PASSED' if success else 'FAILED'}")