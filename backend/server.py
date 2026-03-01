from fastapi import FastAPI, APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.security import HTTPBearer
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import httpx
from jose import jwt, JWTError
from passlib.context import CryptContext
import random
import asyncio
import base64

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Config
JWT_SECRET = os.environ.get('JWT_SECRET', 'default_secret')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 168  # 7 days

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
security = HTTPBearer(auto_error=False)

app = FastAPI(title="One Piece RPG - The Grand Line Architect")
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============ PYDANTIC MODELS ============

class UserCreate(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    created_at: datetime

class CharacterCreate(BaseModel):
    name: str
    title: str = "Aspirante Pirata"
    body_type: str = "normal"
    hair_color: str = "#3E2723"
    outfit: str = "pirate"
    race: str = "human"
    fighting_style: str = "brawler"
    devil_fruit: Optional[str] = None

class CharacterResponse(BaseModel):
    character_id: str
    user_id: str
    name: str
    title: str
    level: int = 1
    experience: int = 0
    bounty: int = 10000000
    stats: Dict[str, int]
    appearance: Dict[str, str]
    devil_fruit: Optional[str] = None
    haki_unlocked: bool = False
    special_moves: List[str] = []
    inventory: List[Dict] = []
    cards: Dict[str, List[str]] = {"storytelling": [], "events": [], "duel": [], "resources": []}
    current_island: str = "foosha"
    ship: Optional[str] = None
    crew_id: Optional[str] = None
    hp: int = 100
    max_hp: int = 100
    energy: int = 100
    max_energy: int = 100
    avatar_url: Optional[str] = None

class BattleAction(BaseModel):
    action_type: str  # movement, basic_attack, haki, special_move, duel_card, item, pass
    action_name: str
    target: Optional[str] = None

class NavigationAction(BaseModel):
    destination: str  # island_id or "open_sea"
    use_storytelling_card: Optional[str] = None

class ChatMessage(BaseModel):
    content: str
    recipient_id: Optional[str] = None

# ============ AUTH HELPERS ============

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

async def get_current_user(request: Request) -> dict:
    # Check cookie first
    session_token = request.cookies.get("session_token")
    
    # Then check Authorization header
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ")[1]
    
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if it's a JWT token
    try:
        payload = jwt.decode(session_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        pass
    
    # Check if it's a session token (Google OAuth)
    session = await db.user_sessions.find_one({"session_token": session_token}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    expires_at = session.get("expires_at")
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")
    
    user = await db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# ============ AUTH ENDPOINTS ============

@api_router.post("/auth/register")
async def register(user_data: UserCreate):
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    user_doc = {
        "user_id": user_id,
        "email": user_data.email,
        "password_hash": hash_password(user_data.password),
        "name": user_data.name,
        "picture": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(user_doc)
    
    token = create_access_token({"user_id": user_id})
    return {"token": token, "user": {"user_id": user_id, "email": user_data.email, "name": user_data.name}}

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if "password_hash" in user and not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"user_id": user["user_id"]})
    return {"token": token, "user": {"user_id": user["user_id"], "email": user["email"], "name": user["name"]}}

@api_router.get("/auth/session")
async def process_session(session_id: str, response: Response):
    """Process Google OAuth session_id from Emergent Auth"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": session_id}
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        data = resp.json()
    
    # Check if user exists
    user = await db.users.find_one({"email": data["email"]}, {"_id": 0})
    
    if not user:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        user = {
            "user_id": user_id,
            "email": data["email"],
            "name": data["name"],
            "picture": data.get("picture"),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(user)
    else:
        user_id = user["user_id"]
        await db.users.update_one({"user_id": user_id}, {"$set": {"name": data["name"], "picture": data.get("picture")}})
    
    # Store session
    session_token = data["session_token"]
    await db.user_sessions.insert_one({
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7*24*60*60,
        path="/"
    )
    
    return {"user_id": user_id, "email": data["email"], "name": data["name"], "picture": data.get("picture")}

@api_router.get("/auth/me")
async def get_me(request: Request):
    user = await get_current_user(request)
    return {k: v for k, v in user.items() if k != "password_hash"}

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_one({"session_token": session_token})
    response.delete_cookie("session_token", path="/")
    return {"message": "Logged out"}

# ============ CHARACTER ENDPOINTS ============

@api_router.post("/characters", response_model=CharacterResponse)
async def create_character(char_data: CharacterCreate, request: Request):
    user = await get_current_user(request)
    
    # Check if user already has a character
    existing = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Character already exists")
    
    # Calculate base stats based on choices
    base_stats = {"attack": 50, "defense": 40, "speed": 45, "luck": 30}
    
    if char_data.body_type == "slim":
        base_stats["attack"] += 10
        base_stats["speed"] += 15
        base_stats["defense"] -= 5
    elif char_data.body_type == "muscular":
        base_stats["attack"] += 5
        base_stats["defense"] += 10
    elif char_data.body_type == "giant":
        base_stats["attack"] += 15
        base_stats["defense"] += 15
        base_stats["speed"] -= 10
    
    # Devil fruit bonuses
    bounty = 10000000
    if char_data.devil_fruit:
        base_stats["attack"] += 20
        bounty = 50000000
    
    character_id = f"char_{uuid.uuid4().hex[:12]}"
    character = {
        "character_id": character_id,
        "user_id": user["user_id"],
        "name": char_data.name,
        "title": char_data.title,
        "level": 1,
        "experience": 0,
        "bounty": bounty,
        "stats": base_stats,
        "appearance": {
            "body_type": char_data.body_type,
            "hair_color": char_data.hair_color,
            "outfit": char_data.outfit,
            "race": char_data.race
        },
        "fighting_style": char_data.fighting_style,
        "devil_fruit": char_data.devil_fruit,
        "haki_unlocked": False,
        "special_moves": get_base_moves(char_data.fighting_style),
        "inventory": [],
        "cards": {"storytelling": [], "events": [], "duel": [], "resources": []},
        "current_island": "foosha",
        "ship": None,
        "crew_id": None,
        "hp": 100,
        "max_hp": 100,
        "energy": 100,
        "max_energy": 100,
        "avatar_url": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.characters.insert_one(character)
    character.pop("_id", None)
    return character

def get_base_moves(fighting_style: str) -> List[str]:
    moves = {
        "brawler": ["Pugno Potente", "Calcio Rotante", "Testata"],
        "swordsman": ["Fendente", "Affondo", "Parata Offensiva"],
        "shooter": ["Colpo Mirato", "Raffica", "Tiro di Sbarramento"],
        "martial_artist": ["Colpo di Palmo", "Calcio Volante", "Presa Mortale"]
    }
    return moves.get(fighting_style, ["Pugno", "Calcio", "Schivata"])

@api_router.get("/characters/me", response_model=CharacterResponse)
async def get_my_character(request: Request):
    user = await get_current_user(request)
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character

@api_router.put("/characters/me")
async def update_character(updates: Dict[str, Any], request: Request):
    user = await get_current_user(request)
    
    # Only allow certain fields to be updated
    allowed_fields = ["name", "title", "current_island", "hp", "energy", "inventory", "cards"]
    filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
    
    if filtered_updates:
        await db.characters.update_one({"user_id": user["user_id"]}, {"$set": filtered_updates})
    
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    return character

@api_router.delete("/characters/me")
async def delete_character(request: Request):
    """Delete the current user's character to allow recreation"""
    user = await get_current_user(request)
    
    result = await db.characters.delete_one({"user_id": user["user_id"]})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return {"message": "Character deleted successfully"}

# ============ NAVIGATION & WORLD MAP ============

ISLANDS = {
    "foosha": {"name": "Foosha Village", "saga": "East Blue", "x": 10, "y": 70, "events_required": 0},
    "shells_town": {"name": "Shells Town", "saga": "East Blue", "x": 18, "y": 55, "events_required": 1},
    "orange_town": {"name": "Orange Town", "saga": "East Blue", "x": 25, "y": 60, "events_required": 2},
    "baratie": {"name": "Baratie", "saga": "East Blue", "x": 35, "y": 50, "events_required": 3},
    "arlong_park": {"name": "Arlong Park", "saga": "East Blue", "x": 42, "y": 45, "events_required": 4},
    "loguetown": {"name": "Loguetown", "saga": "East Blue", "x": 50, "y": 55, "events_required": 5},
    "alabasta": {"name": "Alabasta", "saga": "Grand Line", "x": 60, "y": 40, "events_required": 8},
    "skypiea": {"name": "Skypiea", "saga": "Grand Line", "x": 65, "y": 20, "events_required": 12},
    "water_seven": {"name": "Water 7", "saga": "Grand Line", "x": 72, "y": 45, "events_required": 15},
    "thriller_bark": {"name": "Thriller Bark", "saga": "Grand Line", "x": 78, "y": 35, "events_required": 18},
    "sabaody": {"name": "Sabaody", "saga": "Grand Line", "x": 85, "y": 50, "events_required": 22},
    "wano": {"name": "Wano", "saga": "New World", "x": 92, "y": 30, "events_required": 30}
}

@api_router.get("/world/islands")
async def get_islands(request: Request):
    user = await get_current_user(request)
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    completed_events = len(character.get("cards", {}).get("events", []))
    
    islands_list = []
    for island_id, data in ISLANDS.items():
        islands_list.append({
            "id": island_id,
            **data,
            "unlocked": completed_events >= data["events_required"],
            "current": character.get("current_island") == island_id
        })
    
    return {"islands": islands_list, "current_island": character.get("current_island")}

@api_router.post("/world/roll-dice")
async def roll_dice(navigation: NavigationAction, request: Request):
    user = await get_current_user(request)
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    if not character.get("ship"):
        raise HTTPException(status_code=400, detail="You need a ship to navigate!")
    
    # Roll dice (1-6)
    dice_result = random.randint(1, 6)
    
    # Apply storytelling card bonus if used
    bonus = 0
    if navigation.use_storytelling_card:
        # Check if player has the card and apply effect
        bonus = random.randint(1, 3)
    
    total_movement = dice_result + bonus
    
    # Generate random event based on destination
    event = None
    if navigation.destination == "open_sea" or random.random() < 0.7:
        event = generate_sea_event(total_movement)
    
    # Update position
    await db.characters.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"navigation_progress": total_movement}}
    )
    
    return {
        "dice_result": dice_result,
        "bonus": bonus,
        "total_movement": total_movement,
        "event": event
    }

def generate_sea_event(movement: int) -> Dict:
    events = [
        {"type": "battle", "name": "Pirati Nemici!", "description": "Una nave pirata vi attacca!", "difficulty": "easy"},
        {"type": "treasure", "name": "Forziere alla Deriva", "description": "Trovate un forziere galleggiante!", "reward": "random_card"},
        {"type": "storm", "name": "Tempesta!", "description": "Una tempesta colpisce la nave!", "damage": 10},
        {"type": "merchant", "name": "Mercante Viaggiatore", "description": "Incontrate un mercante in mare.", "shop": True},
        {"type": "sea_king", "name": "Re del Mare!", "description": "Un gigantesco Re del Mare emerge!", "difficulty": "hard"},
        {"type": "marine", "name": "Nave della Marina!", "description": "La Marina vi ha avvistato!", "difficulty": "medium"},
        {"type": "calm", "name": "Mare Calmo", "description": "Navigazione tranquilla.", "bonus_energy": 10},
        {"type": "island_sighting", "name": "Isola all'Orizzonte", "description": "Avvistate un'isola misteriosa!", "optional_stop": True}
    ]
    return random.choice(events)

@api_router.post("/world/arrive-island")
async def arrive_at_island(data: Dict[str, str], request: Request):
    user = await get_current_user(request)
    island_id = data.get("island_id")
    
    if island_id not in ISLANDS:
        raise HTTPException(status_code=400, detail="Island not found")
    
    await db.characters.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"current_island": island_id, "navigation_progress": 0}}
    )
    
    return {"message": f"Arrived at {ISLANDS[island_id]['name']}", "island": ISLANDS[island_id]}

# ============ ISLAND ZONES & EVENTS ============

ISLAND_ZONES = {
    "dock": {"name": "Molo", "description": "Il porto della città", "npcs": ["harbor_master", "fisherman"]},
    "tavern": {"name": "Taverna", "description": "Un luogo per riposare e raccogliere informazioni", "npcs": ["bartender", "drunk_pirate"]},
    "market": {"name": "Mercato", "description": "Compra e vendi oggetti", "npcs": ["merchant", "blacksmith"]},
    "plaza": {"name": "Piazza", "description": "Il centro della città", "npcs": ["townsfolk", "marine_patrol"]},
    "hospital": {"name": "Ospedale", "description": "Cura le tue ferite", "npcs": ["doctor"]},
    "beach": {"name": "Spiaggia", "description": "Una spiaggia tranquilla", "npcs": ["hermit", "sunbather"]},
    "forest": {"name": "Foresta", "description": "Una foresta misteriosa", "npcs": ["bandit", "mysterious_figure"]},
    "mansion": {"name": "Villa", "description": "La residenza del governatore", "npcs": ["noble", "butler"]}
}

@api_router.get("/island/zones")
async def get_island_zones(request: Request):
    user = await get_current_user(request)
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    current_island = character.get("current_island", "foosha")
    
    return {
        "island": ISLANDS.get(current_island, {}),
        "zones": ISLAND_ZONES
    }

@api_router.post("/island/interact-npc")
async def interact_with_npc(data: Dict[str, str], request: Request):
    user = await get_current_user(request)
    npc_id = data.get("npc_id")
    zone = data.get("zone")
    
    # NPC interactions with rewards
    npc_interactions = {
        "bartender": {
            "dialogue": "Benvenuto, straniero! Vuoi sapere le ultime notizie?",
            "action": "get_info",
            "reward": {"type": "info", "value": "Rumors about treasure"}
        },
        "merchant": {
            "dialogue": "Ho ottimi affari per te oggi!",
            "action": "shop",
            "items": ["health_potion", "energy_drink", "basic_weapon"]
        },
        "doctor": {
            "dialogue": "Hai bisogno di cure?",
            "action": "heal",
            "cost": 100,
            "heal_amount": 50
        },
        "harbor_master": {
            "dialogue": "Cerchi una nave? Posso aiutarti.",
            "action": "ship_shop",
            "ships": ["small_boat", "caravel", "brigantine"]
        },
        "mysterious_figure": {
            "dialogue": "Vedo grande potenziale in te... Vuoi imparare l'Haki?",
            "action": "quest",
            "quest_type": "haki_training"
        }
    }
    
    interaction = npc_interactions.get(npc_id, {
        "dialogue": "Non ho nulla da dirti.",
        "action": "none"
    })
    
    return {"npc_id": npc_id, "interaction": interaction}

# ============ BATTLE SYSTEM ============

active_battles: Dict[str, Dict] = {}

@api_router.post("/battle/start")
async def start_battle(data: Dict[str, str], request: Request):
    user = await get_current_user(request)
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    opponent_type = data.get("opponent_type", "npc")  # npc or player
    opponent_id = data.get("opponent_id")
    
    battle_id = f"battle_{uuid.uuid4().hex[:12]}"
    
    # Generate NPC opponent stats
    if opponent_type == "npc":
        opponent = generate_npc_opponent(opponent_id)
    else:
        opponent = await db.characters.find_one({"character_id": opponent_id}, {"_id": 0})
        if not opponent:
            raise HTTPException(status_code=404, detail="Opponent not found")
    
    battle = {
        "battle_id": battle_id,
        "player1": {
            "character_id": character["character_id"],
            "user_id": user["user_id"],
            "name": character["name"],
            "hp": character["hp"],
            "max_hp": character["max_hp"],
            "energy": character["energy"],
            "max_energy": character["max_energy"],
            "stats": character["stats"],
            "special_moves": character.get("special_moves", []),
            "devil_fruit": character.get("devil_fruit"),
            "haki_unlocked": character.get("haki_unlocked", False)
        },
        "player2": opponent,
        "current_turn": "player1",
        "turn_number": 1,
        "turn_start_time": datetime.now(timezone.utc).isoformat(),
        "max_turn_time": 180,  # 3 minutes
        "max_battle_time": 1200,  # 20 minutes
        "battle_start": datetime.now(timezone.utc).isoformat(),
        "battle_log": [],
        "status": "active"
    }
    
    active_battles[battle_id] = battle
    # Store battle without MongoDB _id issues
    battle_doc = battle.copy()
    await db.battles.insert_one(battle_doc)
    
    return {"battle_id": battle_id, "battle": battle}

def generate_npc_opponent(opponent_id: Optional[str]) -> Dict:
    npcs = {
        "marine_grunt": {"name": "Marine Soldato", "hp": 80, "max_hp": 80, "energy": 60, "max_energy": 60, 
                        "stats": {"attack": 35, "defense": 30, "speed": 40}, "special_moves": ["Colpo di Spada"], "bounty": 0},
        "marine_captain": {"name": "Marine Capitano", "hp": 120, "max_hp": 120, "energy": 80, "max_energy": 80,
                          "stats": {"attack": 55, "defense": 50, "speed": 45}, "special_moves": ["Giustizia Assoluta", "Raffica"], "bounty": 0},
        "pirate_rookie": {"name": "Pirata Novizio", "hp": 70, "max_hp": 70, "energy": 50, "max_energy": 50,
                         "stats": {"attack": 40, "defense": 25, "speed": 45}, "special_moves": ["Taglio Disperato"], "bounty": 5000000},
        "pirate_captain": {"name": "Capitano Pirata", "hp": 150, "max_hp": 150, "energy": 100, "max_energy": 100,
                          "stats": {"attack": 65, "defense": 55, "speed": 50}, "special_moves": ["Assalto Pirata", "Grido di Guerra"], "bounty": 30000000},
        "sea_king": {"name": "Re del Mare", "hp": 200, "max_hp": 200, "energy": 150, "max_energy": 150,
                    "stats": {"attack": 80, "defense": 70, "speed": 30}, "special_moves": ["Morso Devastante", "Onda d'Urto"], "bounty": 0}
    }
    
    npc = npcs.get(opponent_id, npcs["pirate_rookie"])
    npc["character_id"] = f"npc_{opponent_id}"
    npc["is_npc"] = True
    return npc

@api_router.post("/battle/{battle_id}/action")
async def battle_action(battle_id: str, action: BattleAction, request: Request):
    user = await get_current_user(request)
    
    battle = active_battles.get(battle_id)
    if not battle:
        battle_doc = await db.battles.find_one({"battle_id": battle_id}, {"_id": 0})
        if not battle_doc:
            raise HTTPException(status_code=404, detail="Battle not found")
        battle = battle_doc
        active_battles[battle_id] = battle
    
    # Determine which player is acting
    is_player1 = battle["player1"]["user_id"] == user["user_id"]
    current_player = "player1" if is_player1 else "player2"
    opponent = "player2" if is_player1 else "player1"
    
    if battle["current_turn"] != current_player:
        raise HTTPException(status_code=400, detail="Not your turn!")
    
    # Process action
    result = process_battle_action(battle, current_player, opponent, action)
    
    # Update battle state
    battle["current_turn"] = opponent if not result.get("battle_ended") else None
    battle["turn_number"] += 1
    battle["turn_start_time"] = datetime.now(timezone.utc).isoformat()
    battle["battle_log"].append(result["log_entry"])
    
    if result.get("battle_ended"):
        battle["status"] = "finished"
        battle["winner"] = result.get("winner")
    
    active_battles[battle_id] = battle
    await db.battles.update_one({"battle_id": battle_id}, {"$set": battle})
    
    return {"result": result, "battle": battle}

def process_battle_action(battle: Dict, attacker: str, defender: str, action: BattleAction) -> Dict:
    attacker_data = battle[attacker]
    defender_data = battle[defender]
    
    damage = 0
    energy_cost = 0
    effect = None
    log_entry = ""
    
    if action.action_type == "basic_attack":
        damage = calculate_damage(attacker_data["stats"]["attack"], defender_data["stats"]["defense"], 1.0)
        energy_cost = 5
        log_entry = f"{attacker_data['name']} usa {action.action_name}! Infligge {damage} danni!"
        
    elif action.action_type == "special_move":
        if action.action_name not in attacker_data.get("special_moves", []):
            raise HTTPException(status_code=400, detail="Move not available")
        damage = calculate_damage(attacker_data["stats"]["attack"], defender_data["stats"]["defense"], 1.5)
        energy_cost = 20
        log_entry = f"{attacker_data['name']} usa {action.action_name}! Infligge {damage} danni!"
        
    elif action.action_type == "haki":
        if not attacker_data.get("haki_unlocked"):
            raise HTTPException(status_code=400, detail="Haki not unlocked")
        damage = calculate_damage(attacker_data["stats"]["attack"], defender_data["stats"]["defense"], 2.0)
        damage = int(damage * 1.3)  # Haki ignores 30% defense
        energy_cost = 30
        log_entry = f"{attacker_data['name']} attiva l'Haki! {action.action_name}! {damage} danni devastanti!"
        
    elif action.action_type == "movement":
        effect = {"type": "movement", "value": action.action_name}
        energy_cost = 3
        log_entry = f"{attacker_data['name']} si muove: {action.action_name}"
        
    elif action.action_type == "item":
        effect = {"type": "item", "value": action.action_name}
        log_entry = f"{attacker_data['name']} usa oggetto: {action.action_name}"
        
    elif action.action_type == "pass":
        attacker_data["energy"] = min(attacker_data["max_energy"], attacker_data["energy"] + 15)
        log_entry = f"{attacker_data['name']} recupera energia! (+15)"
    
    # Apply damage and energy
    if damage > 0:
        defender_data["hp"] = max(0, defender_data["hp"] - damage)
    
    if energy_cost > 0:
        attacker_data["energy"] = max(0, attacker_data["energy"] - energy_cost)
    
    # Check for battle end
    battle_ended = defender_data["hp"] <= 0
    winner = attacker if battle_ended else None
    
    return {
        "damage": damage,
        "energy_cost": energy_cost,
        "effect": effect,
        "log_entry": log_entry,
        "battle_ended": battle_ended,
        "winner": winner
    }

def calculate_damage(attack: int, defense: int, multiplier: float) -> int:
    base_damage = int((attack * multiplier) - (defense * 0.5))
    variance = random.randint(-5, 5)
    return max(1, base_damage + variance)

@api_router.get("/battle/{battle_id}")
async def get_battle(battle_id: str, request: Request):
    await get_current_user(request)
    
    battle = active_battles.get(battle_id)
    if not battle:
        battle = await db.battles.find_one({"battle_id": battle_id}, {"_id": 0})
    
    if not battle:
        raise HTTPException(status_code=404, detail="Battle not found")
    
    return battle

# ============ AI NARRATION ============

@api_router.post("/ai/narrate-battle")
async def narrate_battle(data: Dict[str, Any], request: Request):
    """Generate AI narration for battle events using Gemini 3 Flash"""
    await get_current_user(request)
    
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        api_key = os.getenv("EMERGENT_LLM_KEY")
        session_id = f"narration_{uuid.uuid4().hex[:8]}"
        
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message="""Sei un narratore epico di combattimenti in stile One Piece. 
Descrivi le azioni di combattimento in modo drammatico e coinvolgente, in italiano.
Usa descrizioni vivide, onomatopee giapponesi occasionali (BOOM!, CRASH!), e riferimenti allo stile dell'anime.
Mantieni le descrizioni brevi ma impattanti (2-3 frasi max)."""
        )
        chat.with_model("gemini", "gemini-3-flash-preview")
        
        battle_context = data.get("context", "")
        action = data.get("action", "")
        
        message = UserMessage(text=f"Contesto battaglia: {battle_context}\n\nAzione da narrare: {action}")
        
        response = await chat.send_message(message)
        
        return {"narration": response}
    except Exception as e:
        logger.error(f"AI narration error: {e}")
        return {"narration": data.get("action", "L'azione è stata eseguita!")}

# ============ IMAGE GENERATION ============

@api_router.post("/ai/generate-avatar")
async def generate_avatar(data: Dict[str, str], request: Request):
    """Generate character avatar using Gemini Nano Banana"""
    await get_current_user(request)
    
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        api_key = os.getenv("EMERGENT_LLM_KEY")
        session_id = f"avatar_{uuid.uuid4().hex[:8]}"
        
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message="You are an anime character designer specializing in One Piece style art."
        )
        chat.with_model("gemini", "gemini-3-pro-image-preview").with_params(modalities=["image", "text"])
        
        character_desc = data.get("description", "a pirate character")
        prompt = f"""Create an anime-style portrait of {character_desc} in One Piece art style.
The character should look like they belong in the One Piece universe.
High quality, vibrant colors, dynamic pose, detailed anime features.
Portrait format, character facing slightly to the side, dramatic lighting."""
        
        message = UserMessage(text=prompt)
        text, images = await chat.send_message_multimodal_response(message)
        
        if images and len(images) > 0:
            # Return base64 image data (first 50 chars for logging)
            image_data = images[0].get("data", "")
            logger.info(f"Generated avatar image: {image_data[:50]}...")
            return {"image_data": image_data, "mime_type": images[0].get("mime_type", "image/png")}
        
        return {"error": "No image generated"}
    except Exception as e:
        logger.error(f"Avatar generation error: {e}")
        return {"error": str(e)}

# ============ CARDS SYSTEM ============

@api_router.get("/cards/collection")
async def get_card_collection(request: Request):
    user = await get_current_user(request)
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return {"cards": character.get("cards", {})}

@api_router.post("/cards/use")
async def use_card(data: Dict[str, str], request: Request):
    user = await get_current_user(request)
    card_type = data.get("card_type")
    card_id = data.get("card_id")
    
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    if card_id not in character.get("cards", {}).get(card_type, []):
        raise HTTPException(status_code=400, detail="Card not found in collection")
    
    # Apply card effect based on type
    effect = apply_card_effect(card_type, card_id, character)
    
    # Remove card from collection
    await db.characters.update_one(
        {"user_id": user["user_id"]},
        {"$pull": {f"cards.{card_type}": card_id}}
    )
    
    return {"effect": effect, "message": f"Card {card_id} used successfully"}

def apply_card_effect(card_type: str, card_id: str, character: Dict) -> Dict:
    effects = {
        "storytelling": {"bonus_dice": 2, "description": "Bonus al tiro del dado"},
        "events": {"skip_event": True, "description": "Salta un evento negativo"},
        "duel": {"damage_bonus": 20, "description": "Bonus danni nel prossimo attacco"},
        "resources": {"heal": 30, "description": "Recupera HP"}
    }
    return effects.get(card_type, {"description": "Effetto sconosciuto"})

# ============ CHAT SYSTEM ============

chat_connections: Dict[str, WebSocket] = {}

@api_router.websocket("/ws/chat/{room_id}")
async def chat_websocket(websocket: WebSocket, room_id: str):
    await websocket.accept()
    
    # Get user from query params or cookie
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001)
        return
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
    except JWTError:
        await websocket.close(code=4001)
        return
    
    connection_id = f"{room_id}_{user_id}"
    chat_connections[connection_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_json()
            message = {
                "user_id": user_id,
                "room_id": room_id,
                "content": data.get("content"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Save to DB
            await db.chat_messages.insert_one(message)
            
            # Broadcast to all in room
            for conn_id, ws in chat_connections.items():
                if conn_id.startswith(room_id):
                    try:
                        await ws.send_json(message)
                    except:
                        pass
    except WebSocketDisconnect:
        del chat_connections[connection_id]

@api_router.get("/chat/{room_id}/history")
async def get_chat_history(room_id: str, request: Request):
    await get_current_user(request)
    
    messages = await db.chat_messages.find(
        {"room_id": room_id},
        {"_id": 0}
    ).sort("timestamp", -1).limit(50).to_list(50)
    
    return {"messages": list(reversed(messages))}

# ============ SHOP SYSTEM ============

SHOP_ITEMS = {
    "health_potion": {"name": "Pozione Salute", "price": 100, "effect": {"heal": 30}},
    "energy_drink": {"name": "Bevanda Energetica", "price": 80, "effect": {"energy": 25}},
    "basic_sword": {"name": "Spada Base", "price": 500, "effect": {"attack_bonus": 5}},
    "small_boat": {"name": "Barca Piccola", "price": 5000, "type": "ship", "speed": 1},
    "caravel": {"name": "Caravella", "price": 20000, "type": "ship", "speed": 2},
    "brigantine": {"name": "Brigantino", "price": 50000, "type": "ship", "speed": 3}
}

@api_router.get("/shop/items")
async def get_shop_items(request: Request):
    await get_current_user(request)
    return {"items": SHOP_ITEMS}

@api_router.post("/shop/buy")
async def buy_item(data: Dict[str, str], request: Request):
    user = await get_current_user(request)
    item_id = data.get("item_id")
    
    if item_id not in SHOP_ITEMS:
        raise HTTPException(status_code=400, detail="Item not found")
    
    item = SHOP_ITEMS[item_id]
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    # Check if enough berry (we'd need to add a berry field)
    # For now, just add the item
    
    if item.get("type") == "ship":
        await db.characters.update_one(
            {"user_id": user["user_id"]},
            {"$set": {"ship": item_id}}
        )
    else:
        await db.characters.update_one(
            {"user_id": user["user_id"]},
            {"$push": {"inventory": {"item_id": item_id, **item}}}
        )
    
    return {"message": f"Purchased {item['name']}", "item": item}

# ============ ROOT & HEALTH ============

@api_router.get("/")
async def root():
    return {"message": "One Piece RPG - The Grand Line Architect API", "version": "1.0.0"}

@api_router.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Include router and middleware
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
