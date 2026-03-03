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
import re

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

# ============ GAME CONSTANTS ============

# Race bonuses: {forza, velocita, resistenza, agilita, vita_base, energia_base, aspettativa_vita}
RACE_STATS = {
    "umano": {
        "name": "Umano",
        "description": "Razza equilibrata, versatile in ogni situazione.",
        "bonus": {"forza": 10, "velocita": 10, "resistenza": 10, "agilita": 10},
        "vita_base": 100,
        "energia_base": 100,
        "aspettativa_vita": 80,
        "vantaggi": ["Versatilità in tutti i ruoli", "Apprendimento rapido"],
        "svantaggi": ["Nessun bonus particolare"]
    },
    "uomo_pesce": {
        "name": "Uomo Pesce",
        "description": "Creature marine con forza 10 volte superiore agli umani in acqua.",
        "bonus": {"forza": 20, "velocita": 8, "resistenza": 15, "agilita": 12},
        "vita_base": 120,
        "energia_base": 90,
        "aspettativa_vita": 100,
        "vantaggi": ["Forza 10x in acqua", "Può respirare sott'acqua", "Bonus nuoto"],
        "svantaggi": ["Meno agile sulla terraferma"]
    },
    "visone": {
        "name": "Visone",
        "description": "Creature antropomorfe con abilità elettriche innate (Electro).",
        "bonus": {"forza": 12, "velocita": 15, "resistenza": 8, "agilita": 18},
        "vita_base": 90,
        "energia_base": 110,
        "aspettativa_vita": 70,
        "vantaggi": ["Electro innato", "Agilità superiore", "Sensi potenziati"],
        "svantaggi": ["Resistenza minore", "Vita più bassa"]
    },
    "semi_gigante": {
        "name": "Semi-Gigante",
        "description": "Ibridi con sangue di gigante, più forti e resistenti della media.",
        "bonus": {"forza": 18, "velocita": 6, "resistenza": 18, "agilita": 5},
        "vita_base": 150,
        "energia_base": 80,
        "aspettativa_vita": 120,
        "vantaggi": ["Forza e resistenza elevate", "Vita molto alta"],
        "svantaggi": ["Lenti", "Poca agilità", "Bersaglio facile"]
    },
    "gigante": {
        "name": "Gigante",
        "description": "Creature enormi con forza devastante ma lente.",
        "bonus": {"forza": 25, "velocita": 3, "resistenza": 22, "agilita": 2},
        "vita_base": 200,
        "energia_base": 70,
        "aspettativa_vita": 300,
        "vantaggi": ["Forza devastante", "Vita altissima", "Lunga vita"],
        "svantaggi": ["Molto lenti", "Agilità quasi nulla", "Difficoltà in spazi stretti"]
    },
    "cyborg": {
        "name": "Cyborg",
        "description": "Umani potenziati con parti meccaniche.",
        "bonus": {"forza": 15, "velocita": 10, "resistenza": 20, "agilita": 8},
        "vita_base": 130,
        "energia_base": 120,
        "aspettativa_vita": 60,
        "vantaggi": ["Alta resistenza", "Può usare armi integrate", "Bonus con scienziato"],
        "svantaggi": ["Vulnerabile all'acqua", "Necessita manutenzione", "Vita più breve"]
    }
}

# Fighting style bonuses
FIGHTING_STYLES = {
    "corpo_misto": {
        "name": "Corpo a Corpo - Misto",
        "description": "Combina pugni e calci per un approccio versatile.",
        "bonus": {"forza": 5, "velocita": 5, "agilita": 5},
        "vantaggi": ["Versatilità nelle mosse", "Nessuna debolezza evidente"],
        "svantaggi": ["Non eccelle in nulla di specifico"]
    },
    "corpo_pugni": {
        "name": "Corpo a Corpo - Pugile",
        "description": "Specializzato in pugni potenti e devastanti.",
        "bonus": {"forza": 10, "velocita": 3, "resistenza": 5},
        "vantaggi": ["Pugni molto potenti", "Buona difesa ravvicinata"],
        "svantaggi": ["Portata limitata", "Calci deboli"]
    },
    "corpo_calci": {
        "name": "Corpo a Corpo - Solo Calci",
        "description": "Maestro delle tecniche di calcio, maggiore portata.",
        "bonus": {"velocita": 8, "agilita": 8, "forza": 3},
        "vantaggi": ["Maggiore portata", "Alta velocità", "Mani libere per altro"],
        "svantaggi": ["Pugni deboli", "Vulnerabile a distanza ravvicinata"]
    },
    "armi_mono": {
        "name": "Armi Bianche - Mono Arma",
        "description": "Padronanza di una singola arma (spada, ascia, lancia...).",
        "bonus": {"forza": 7, "velocita": 5, "agilita": 5},
        "vantaggi": ["Maestria con un'arma", "Tecniche specializzate", "Bonus precisione"],
        "svantaggi": ["Dipendente dall'arma", "Senza arma è debole"]
    },
    "armi_pluri": {
        "name": "Armi Bianche - Pluri Arma",
        "description": "Utilizza più armi contemporaneamente o in sequenza.",
        "bonus": {"velocita": 6, "agilita": 7, "forza": 4},
        "vantaggi": ["Imprevedibile", "Molte opzioni d'attacco"],
        "svantaggi": ["Meno danni per singolo colpo", "Difficile da padroneggiare"]
    },
    "tiratore": {
        "name": "Tiratore",
        "description": "Specialista in armi a distanza: pistole, fucili, fionde.",
        "bonus": {"velocita": 3, "agilita": 10, "resistenza": -3},
        "vantaggi": ["Attacchi a distanza", "Alta precisione", "Evita corpo a corpo"],
        "svantaggi": ["Debole in mischia", "Dipendente da munizioni"]
    }
}

# Gender life expectancy modifiers
GENDER_LIFE_MODIFIER = {
    "maschio": 0,
    "femmina": 5,  # +5 years
    "non_definito": 0
}

# Mestieri/Jobs
MESTIERI = {
    "capitano": {
        "name": "Capitano",
        "description": "Leader della ciurma. +20% Liv. combattimento e energia a tutta la ciurma.",
        "bonus_ciurma": {"combattimento": 0.2, "energia": 0.2},
        "abilita": "Può muovere la nave per conto della ciurma"
    },
    "guerriero": {
        "name": "Guerriero",
        "description": "Combattente esperto. Risolve situazioni di pericolo durante eventi.",
        "bonus_ciurma": {},
        "abilita": "Può comandare la nave in assenza del capitano"
    },
    "navigatore": {
        "name": "Navigatore",
        "description": "Esperto di rotte e mappe. Evita eventi naturali negativi.",
        "bonus_ciurma": {},
        "abilita": "Può decidere la rotta in assenza del capitano"
    },
    "cecchino": {
        "name": "Cecchino",
        "description": "Occhio infallibile. Vede più lontano sulla mappa.",
        "bonus_ciurma": {},
        "abilita": "Bonus danni con cannoni nelle battaglie navali"
    },
    "cuoco": {
        "name": "Cuoco",
        "description": "Maestro della cucina. Funge da ristorante ovunque.",
        "bonus_ciurma": {"energia_recovery": 1.0},
        "abilita": "Recupera energia al 100% per tutta la ciurma"
    },
    "medico": {
        "name": "Medico",
        "description": "Dottore di bordo. Come un ospedale portatile.",
        "bonus_ciurma": {"vita_recovery": 1.0},
        "abilita": "Recupera vita al 100% e cura condizioni speciali"
    },
    "archeologo": {
        "name": "Archeologo",
        "description": "Studioso di storia antica. Traduce Poneglyph.",
        "bonus_ciurma": {},
        "abilita": "Trova tesori, oggetti, armi e frutti del diavolo più facilmente"
    },
    "carpentiere": {
        "name": "Carpentiere",
        "description": "Costruttore e riparatore di navi.",
        "bonus_ciurma": {},
        "abilita": "Installa armi sulla nave e la ripara"
    },
    "musicista": {
        "name": "Musicista",
        "description": "Artista che solleva il morale. +20% EXP per la ciurma.",
        "bonus_ciurma": {"exp": 0.2},
        "abilita": "Bonus su alcune carte evento e combattimento"
    },
    "timoniere": {
        "name": "Timoniere",
        "description": "Esperto nel governare la nave.",
        "bonus_ciurma": {},
        "abilita": "Permette di usare navi avanzate e viaggiare più velocemente"
    },
    "scienziato": {
        "name": "Scienziato",
        "description": "Inventore e studioso. Crea armi speciali.",
        "bonus_ciurma": {},
        "abilita": "Ottiene armi speciali più facilmente. +20% Liv. ai Cyborg"
    },
    "ipnotista": {
        "name": "Ipnotista",
        "description": "Manipolatore mentale. Potenzia la ciurma in battaglia.",
        "bonus_ciurma": {},
        "abilita": "Amplifica tutti i valori di combattimento del 30% per 3 turni"
    }
}

MESTIERE_LEVELS = ["principiante", "intermedio", "avanzato", "esperto"]

# ============ PYDANTIC MODELS ============

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class CharacterCreate(BaseModel):
    nome_personaggio: str
    ruolo: str = "pirata"
    genere: str  # maschio, femmina, non_definito
    eta: int = Field(ge=16)
    razza: str
    stile_combattimento: str
    sogno: str = Field(max_length=100)
    storia_carattere: str = Field(max_length=1000)
    mestiere: str
    mare_partenza: str = "east_blue"  # east_blue, west_blue, north_blue, south_blue
    # Aspetto fisico (opzionale per avatar)
    colore_capelli: Optional[str] = None
    colore_occhi: Optional[str] = None
    particolarita: Optional[str] = None

class CharacterTraitsRequest(BaseModel):
    storia_carattere: str

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

def validate_character_name(name: str) -> tuple[bool, str]:
    """Check if name contains forbidden 'D.' pattern"""
    # Check for "D." or "D " patterns
    if re.search(r'\bD\.', name, re.IGNORECASE) or re.search(r'\bD\s', name, re.IGNORECASE):
        return False, "La volontà della D. puoi sbloccarla solo durante la storia. Per il momento non può essere inserita nel tuo nome personaggio."
    return True, ""

async def get_current_user(request: Request) -> dict:
    session_token = request.cookies.get("session_token")
    
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ")[1]
    
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
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
    # Check if email exists
    existing_email = await db.users.find_one({"email": user_data.email})
    if existing_email:
        raise HTTPException(status_code=400, detail="Email già registrata")
    
    # Check if username exists
    existing_username = await db.users.find_one({"username": user_data.username.lower()})
    if existing_username:
        raise HTTPException(status_code=400, detail="Username già in uso")
    
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    user_doc = {
        "user_id": user_id,
        "username": user_data.username.lower(),
        "display_username": user_data.username,
        "email": user_data.email,
        "password_hash": hash_password(user_data.password),
        "picture": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(user_doc)
    
    token = create_access_token({"user_id": user_id})
    return {
        "token": token, 
        "user": {
            "user_id": user_id, 
            "username": user_data.username,
            "email": user_data.email
        }
    }

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Credenziali non valide")
    
    if "password_hash" in user and not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenziali non valide")
    
    token = create_access_token({"user_id": user["user_id"]})
    return {
        "token": token, 
        "user": {
            "user_id": user["user_id"], 
            "username": user.get("display_username", user.get("username")),
            "email": user["email"]
        }
    }

@api_router.get("/auth/session")
async def process_session(session_id: str, response: Response):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": session_id}
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        data = resp.json()
    
    user = await db.users.find_one({"email": data["email"]}, {"_id": 0})
    
    if not user:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        # Generate username from email
        base_username = data["email"].split("@")[0].lower()
        username = base_username
        counter = 1
        while await db.users.find_one({"username": username}):
            username = f"{base_username}{counter}"
            counter += 1
        
        user = {
            "user_id": user_id,
            "username": username,
            "display_username": data["name"],
            "email": data["email"],
            "picture": data.get("picture"),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(user)
    else:
        user_id = user["user_id"]
        await db.users.update_one({"user_id": user_id}, {"$set": {"picture": data.get("picture")}})
    
    session_token = data["session_token"]
    await db.user_sessions.insert_one({
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7*24*60*60,
        path="/"
    )
    
    return {
        "user_id": user_id, 
        "username": user.get("display_username", user.get("username")),
        "email": data["email"], 
        "picture": data.get("picture")
    }

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
    return {"message": "Logout effettuato"}

# ============ GAME DATA ENDPOINTS ============

@api_router.get("/game/races")
async def get_races():
    """Get all available races with their bonuses"""
    return {"races": RACE_STATS}

@api_router.get("/game/fighting-styles")
async def get_fighting_styles():
    """Get all available fighting styles"""
    return {"styles": FIGHTING_STYLES}

@api_router.get("/game/mestieri")
async def get_mestieri():
    """Get all available jobs/mestieri"""
    return {"mestieri": MESTIERI, "levels": MESTIERE_LEVELS}

# ============ CHARACTER ENDPOINTS ============

@api_router.post("/characters/validate-name")
async def validate_name(data: Dict[str, str]):
    """Validate character name for forbidden patterns"""
    name = data.get("nome", "")
    is_valid, message = validate_character_name(name)
    return {"valid": is_valid, "message": message}

@api_router.post("/characters/extract-traits")
async def extract_character_traits(data: CharacterTraitsRequest, request: Request):
    """Use AI to extract character traits from story/character description"""
    await get_current_user(request)
    
    storia = data.storia_carattere
    
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        api_key = os.getenv("EMERGENT_LLM_KEY")
        session_id = f"traits_{uuid.uuid4().hex[:8]}"
        
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message="""Sei un analista di personalità per un gioco RPG di One Piece.
Analizza la storia/descrizione del personaggio e estrai da 3 a 5 tratti caratteriali distintivi.
I tratti devono essere:
- Brevi (2-4 parole)
- Possono essere positivi o negativi
- Devono poter influenzare gameplay (es: "pessimo senso dell'orientamento", "testardo", "coraggioso", "bugiardo compulsivo", "generoso", "vendicativo")

Rispondi SOLO con un JSON array di stringhe, nient'altro. Esempio:
["coraggioso", "pessimo senso dell'orientamento", "leale fino alla morte"]"""
        )
        chat.with_model("gemini", "gemini-3-flash-preview")
        
        message = UserMessage(text=f"Analizza questa descrizione del personaggio e estrai i tratti caratteriali:\n\n{storia}")
        
        response = await chat.send_message(message)
        
        # Parse JSON response
        import json
        # Clean response - extract JSON array
        response_clean = response.strip()
        if response_clean.startswith("```"):
            response_clean = response_clean.split("```")[1]
            if response_clean.startswith("json"):
                response_clean = response_clean[4:]
        
        traits = json.loads(response_clean)
        return {"traits": traits, "source": "ai"}
        
    except Exception as e:
        logger.error(f"Trait extraction error: {e}")
        # Fallback: suggest random traits
        default_traits = [
            "determinato", "impulsivo", "leale", "misterioso", "ottimista",
            "pessimo senso dell'orientamento", "goloso", "pigro", "coraggioso",
            "solitario", "chiacchierone", "testardo", "gentile", "vendicativo"
        ]
        suggested = random.sample(default_traits, 3)
        return {"traits": suggested, "source": "suggested"}

@api_router.post("/characters")
async def create_character(char_data: CharacterCreate, request: Request):
    user = await get_current_user(request)
    
    # Check if user already has a character
    existing = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Personaggio già esistente")
    
    # Validate character name
    is_valid, error_msg = validate_character_name(char_data.nome_personaggio)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Validate race
    if char_data.razza not in RACE_STATS:
        raise HTTPException(status_code=400, detail="Razza non valida")
    
    # Validate fighting style
    if char_data.stile_combattimento not in FIGHTING_STYLES:
        raise HTTPException(status_code=400, detail="Stile di combattimento non valido")
    
    # Validate mestiere
    if char_data.mestiere not in MESTIERI:
        raise HTTPException(status_code=400, detail="Mestiere non valido")
    
    # Validate gender
    if char_data.genere not in ["maschio", "femmina", "non_definito"]:
        raise HTTPException(status_code=400, detail="Genere non valido")
    
    # Calculate base stats from race
    race_data = RACE_STATS[char_data.razza]
    style_data = FIGHTING_STYLES[char_data.stile_combattimento]
    
    # Base stats
    forza = race_data["bonus"]["forza"] + style_data["bonus"].get("forza", 0)
    velocita = race_data["bonus"]["velocita"] + style_data["bonus"].get("velocita", 0)
    resistenza = race_data["bonus"]["resistenza"] + style_data["bonus"].get("resistenza", 0)
    agilita = race_data["bonus"]["agilita"] + style_data["bonus"].get("agilita", 0)
    
    # Calculated stats
    attacco = forza * velocita
    difesa = resistenza * agilita
    
    # Life expectancy with gender modifier
    aspettativa_vita = race_data["aspettativa_vita"] + GENDER_LIFE_MODIFIER.get(char_data.genere, 0)
    
    character_id = f"char_{uuid.uuid4().hex[:12]}"
    character = {
        "character_id": character_id,
        "user_id": user["user_id"],
        "owner_username": user.get("display_username", user.get("username")),
        
        # Basic info
        "nome_personaggio": char_data.nome_personaggio,
        "ruolo": char_data.ruolo,
        "genere": char_data.genere,
        "eta": char_data.eta,
        "razza": char_data.razza,
        "stile_combattimento": char_data.stile_combattimento,
        "sogno": char_data.sogno,
        "storia_carattere": char_data.storia_carattere,
        "tratti_carattere": [],  # Will be filled by AI extraction
        
        # Mestiere
        "mestiere": char_data.mestiere,
        "mestiere_livello": "principiante",
        
        # PUBLIC STATS (visible to others)
        "livello": 1,
        "esperienza": 0,
        "taglia": 0,  # Bounty in Berry
        "ciurma_id": None,
        "ciurma_ruolo": None,  # "fondatore" or "membro"
        
        # Combat abilities (PUBLIC)
        "vita": race_data["vita_base"],
        "vita_max": race_data["vita_base"],
        "energia": race_data["energia_base"],
        "energia_max": race_data["energia_base"],
        "attacco": attacco,
        "difesa": difesa,
        
        # Base stats (can grow with experience)
        "forza": forza,
        "velocita": velocita,
        "resistenza": resistenza,
        "agilita": agilita,
        
        # Life expectancy
        "aspettativa_vita": aspettativa_vita,
        "aspettativa_vita_max": aspettativa_vita,
        
        # Altre capacità (PUBLIC - empty at start)
        "frutto_diavolo": None,
        "haki": {
            "osservazione": False,
            "armatura": False,
            "conquistatore": False
        },
        "poteri_speciali": [],
        
        # Equipment (PUBLIC)
        "armi": [],
        "oggetti": [],
        "carte": {
            "storytelling": [],
            "eventi": [],
            "duello": [],
            "risorse": []
        },
        
        # PRIVATE STATS (only owner can see)
        "abilita_base": {
            "forza_raw": forza,
            "velocita_raw": velocita,
            "resistenza_raw": resistenza,
            "agilita_raw": agilita,
            "danno_subibile": race_data["vita_base"]
        },
        "armi_speciali": [],
        "poteri_segreti": [],
        "missioni_attive": [],
        "missioni_completate": [],
        
        # Appearance for avatar
        "aspetto": {
            "colore_capelli": char_data.colore_capelli,
            "colore_occhi": char_data.colore_occhi,
            "particolarita": char_data.particolarita
        },
        
        # Location - based on chosen sea
        "mare_corrente": char_data.mare_partenza,
        "isola_corrente": get_starting_island(char_data.mare_partenza),
        "nave": None,
        "navigazione_progresso": 0,
        
        # Economy
        "berry": 1000,  # Starting money
        
        # Logbook
        "logbook": [],
        
        # Metadata
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_active": datetime.now(timezone.utc).isoformat()
    }
    
    await db.characters.insert_one(character)
    character.pop("_id", None)
    return character

@api_router.get("/characters/me")
async def get_my_character(request: Request):
    user = await get_current_user(request)
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    return character

@api_router.get("/characters/{character_id}/public")
async def get_character_public(character_id: str, request: Request):
    """Get public info of any character (what others can see)"""
    await get_current_user(request)
    
    character = await db.characters.find_one({"character_id": character_id}, {"_id": 0})
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    
    # Return only public fields
    public_fields = [
        "character_id", "nome_personaggio", "ruolo", "genere", "razza",
        "stile_combattimento", "sogno", "tratti_carattere",
        "mestiere", "mestiere_livello",
        "livello", "esperienza", "taglia", "ciurma_id", "ciurma_ruolo",
        "vita", "vita_max", "energia", "energia_max", "attacco", "difesa",
        "forza", "velocita", "resistenza", "agilita",
        "aspettativa_vita", "frutto_diavolo", "haki", "poteri_speciali",
        "armi", "oggetti", "carte", "aspetto"
    ]
    
    return {k: character.get(k) for k in public_fields if k in character}

@api_router.put("/characters/me/traits")
async def update_character_traits(data: Dict[str, List[str]], request: Request):
    """Update character traits after AI extraction"""
    user = await get_current_user(request)
    
    traits = data.get("traits", [])
    if len(traits) < 3:
        raise HTTPException(status_code=400, detail="Servono almeno 3 tratti caratteriali")
    
    await db.characters.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"tratti_carattere": traits}}
    )
    
    return {"message": "Tratti aggiornati", "traits": traits}

@api_router.delete("/characters/me")
async def delete_character(request: Request):
    user = await get_current_user(request)
    result = await db.characters.delete_one({"user_id": user["user_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    return {"message": "Personaggio eliminato"}

# ============ BATTLE SYSTEM ============

active_battles: Dict[str, Dict] = {}

@api_router.post("/battle/start")
async def start_battle(data: Dict[str, str], request: Request):
    user = await get_current_user(request)
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    
    opponent_type = data.get("opponent_type", "npc")
    opponent_id = data.get("opponent_id")
    
    battle_id = f"battle_{uuid.uuid4().hex[:12]}"
    
    if opponent_type == "npc":
        opponent = generate_npc_opponent(opponent_id)
    else:
        opponent = await db.characters.find_one({"character_id": opponent_id}, {"_id": 0})
        if not opponent:
            raise HTTPException(status_code=404, detail="Avversario non trovato")
    
    battle = {
        "battle_id": battle_id,
        "player1": {
            "character_id": character["character_id"],
            "user_id": user["user_id"],
            "nome": character["nome_personaggio"],
            "vita": character["vita"],
            "vita_max": character["vita_max"],
            "energia": character["energia"],
            "energia_max": character["energia_max"],
            "attacco": character["attacco"],
            "difesa": character["difesa"],
            "forza": character["forza"],
            "velocita": character["velocita"],
            "resistenza": character["resistenza"],
            "agilita": character["agilita"],
            "stile_combattimento": character["stile_combattimento"],
            "armi": character.get("armi", []),
            "haki": character.get("haki", {}),
            "frutto_diavolo": character.get("frutto_diavolo")
        },
        "player2": opponent,
        "turno_corrente": "player1",
        "numero_turno": 1,
        "inizio_turno": datetime.now(timezone.utc).isoformat(),
        "tempo_max_turno": 180,
        "tempo_max_battaglia": 1200,
        "inizio_battaglia": datetime.now(timezone.utc).isoformat(),
        "log": [],
        "stato": "attivo"
    }
    
    active_battles[battle_id] = battle
    battle_doc = battle.copy()
    await db.battles.insert_one(battle_doc)
    
    return {"battle_id": battle_id, "battle": battle}

def generate_npc_opponent(opponent_id: Optional[str]) -> Dict:
    npcs = {
        "marine_soldato": {
            "nome": "Marine Soldato", 
            "vita": 80, "vita_max": 80, 
            "energia": 60, "energia_max": 60,
            "attacco": 100, "difesa": 80,
            "forza": 10, "velocita": 10, "resistenza": 10, "agilita": 8,
            "stile_combattimento": "corpo_misto",
            "taglia": 0, "is_npc": True
        },
        "pirata_novizio": {
            "nome": "Pirata Novizio",
            "vita": 70, "vita_max": 70,
            "energia": 50, "energia_max": 50,
            "attacco": 90, "difesa": 60,
            "forza": 12, "velocita": 8, "resistenza": 8, "agilita": 8,
            "stile_combattimento": "corpo_pugni",
            "taglia": 5000000, "is_npc": True
        },
        "marine_capitano": {
            "nome": "Marine Capitano",
            "vita": 120, "vita_max": 120,
            "energia": 80, "energia_max": 80,
            "attacco": 200, "difesa": 150,
            "forza": 15, "velocita": 12, "resistenza": 15, "agilita": 10,
            "stile_combattimento": "armi_mono",
            "taglia": 0, "is_npc": True
        },
        "capitano_pirata": {
            "nome": "Capitano Pirata",
            "vita": 150, "vita_max": 150,
            "energia": 100, "energia_max": 100,
            "attacco": 250, "difesa": 180,
            "forza": 18, "velocita": 14, "resistenza": 16, "agilita": 12,
            "stile_combattimento": "armi_pluri",
            "taglia": 30000000, "is_npc": True
        }
    }
    
    npc = npcs.get(opponent_id, npcs["pirata_novizio"])
    npc["character_id"] = f"npc_{opponent_id}"
    return npc

@api_router.post("/battle/{battle_id}/action")
async def battle_action(battle_id: str, data: Dict[str, Any], request: Request):
    user = await get_current_user(request)
    
    battle = active_battles.get(battle_id)
    if not battle:
        battle_doc = await db.battles.find_one({"battle_id": battle_id}, {"_id": 0})
        if not battle_doc:
            raise HTTPException(status_code=404, detail="Battaglia non trovata")
        battle = battle_doc
        active_battles[battle_id] = battle
    
    if battle["stato"] == "finita":
        raise HTTPException(status_code=400, detail="Battaglia già terminata")
    
    is_player1 = battle["player1"]["user_id"] == user["user_id"]
    current_player = "player1" if is_player1 else "player2"
    opponent = "player2" if is_player1 else "player1"
    
    if battle["turno_corrente"] != current_player:
        raise HTTPException(status_code=400, detail="Non è il tuo turno!")
    
    action_type = data.get("action_type")
    action_name = data.get("action_name")
    
    # Player action
    result = process_battle_action(battle, current_player, opponent, action_type, action_name)
    battle["log"].append(result["log_entry"])
    
    # Check if battle ended after player action
    if result.get("battaglia_finita"):
        battle["stato"] = "finita"
        battle["vincitore"] = result.get("vincitore")
        battle["turno_corrente"] = None
        
        # Award experience and berry if player won
        if result.get("vincitore") == "player1":
            exp_gain = 50 + battle["player2"].get("taglia", 0) // 100000
            berry_gain = 100 + random.randint(0, 200)
            await db.characters.update_one(
                {"user_id": user["user_id"]},
                {"$inc": {"esperienza": exp_gain, "berry": berry_gain}}
            )
            battle["rewards"] = {"exp": exp_gain, "berry": berry_gain}
    else:
        # NPC Turn (automatic)
        if battle["player2"].get("is_npc"):
            npc_result = process_npc_turn(battle, "player2", "player1")
            battle["log"].append(npc_result["log_entry"])
            battle["numero_turno"] += 1
            
            # Check if NPC won
            if npc_result.get("battaglia_finita"):
                battle["stato"] = "finita"
                battle["vincitore"] = "player2"
                battle["turno_corrente"] = None
            else:
                battle["turno_corrente"] = "player1"
                battle["inizio_turno"] = datetime.now(timezone.utc).isoformat()
        else:
            # PvP - switch turn
            battle["turno_corrente"] = opponent
            battle["numero_turno"] += 1
            battle["inizio_turno"] = datetime.now(timezone.utc).isoformat()
    
    active_battles[battle_id] = battle
    await db.battles.update_one({"battle_id": battle_id}, {"$set": battle})
    
    return {"result": result, "battle": battle}

def process_npc_turn(battle: Dict, attacker: str, defender: str) -> Dict:
    """Process NPC automatic turn"""
    attacker_data = battle[attacker]
    
    # NPC AI: choose action based on energy and health
    if attacker_data["energia"] < 10:
        # Low energy - rest
        recovery = 15
        attacker_data["energia"] = min(attacker_data["energia_max"], attacker_data["energia"] + recovery)
        log_entry = f"{attacker_data['nome']} recupera energia. +{recovery}"
        return {"danno": 0, "log_entry": log_entry, "battaglia_finita": False}
    
    # Choose attack type based on probability
    attack_roll = random.random()
    
    if attack_roll < 0.3 and attacker_data["energia"] >= 20:
        # 30% chance special attack
        action_type = "attacco_speciale"
        action_name = random.choice(["Colpo Potente", "Tecnica Segreta", "Assalto Furioso"])
    elif attack_roll < 0.9:
        # 60% chance basic attack
        action_type = "attacco_base"
        action_name = random.choice(["Pugno", "Calcio", "Colpo Rapido"])
    else:
        # 10% chance defend
        action_type = "difesa"
        action_name = "Difende"
    
    return process_battle_action(battle, attacker, defender, action_type, action_name)

def process_battle_action(battle: Dict, attacker: str, defender: str, action_type: str, action_name: str) -> Dict:
    attacker_data = battle[attacker]
    defender_data = battle[defender]
    
    danno = 0
    costo_energia = 0
    log_entry = ""
    
    if action_type == "attacco_base":
        # Danno = Attacco - (Difesa * 0.3) + varianza
        danno = max(1, int(attacker_data["attacco"] * 0.1 - defender_data["difesa"] * 0.03))
        danno += random.randint(-3, 5)
        costo_energia = 5
        log_entry = f"{attacker_data['nome']} usa {action_name}. Danno: {danno}"
        
    elif action_type == "attacco_speciale":
        danno = max(1, int(attacker_data["attacco"] * 0.2 - defender_data["difesa"] * 0.02))
        danno += random.randint(0, 10)
        costo_energia = 20
        log_entry = f"{attacker_data['nome']} usa {action_name}! Danno: {danno}"
        
    elif action_type == "movimento":
        costo_energia = 3
        log_entry = f"{attacker_data['nome']} si muove: {action_name}"
        
    elif action_type == "difesa":
        # Increase defense temporarily
        costo_energia = 5
        log_entry = f"{attacker_data['nome']} si difende. +50% difesa questo turno"
        
    elif action_type == "passa":
        # Recover energy
        recovery = 15
        attacker_data["energia"] = min(attacker_data["energia_max"], attacker_data["energia"] + recovery)
        log_entry = f"{attacker_data['nome']} recupera energia. +{recovery}"
    
    # Apply damage
    if danno > 0:
        defender_data["vita"] = max(0, defender_data["vita"] - danno)
    
    # Apply energy cost
    if costo_energia > 0:
        attacker_data["energia"] = max(0, attacker_data["energia"] - costo_energia)
    
    # Check battle end
    battaglia_finita = defender_data["vita"] <= 0
    vincitore = attacker if battaglia_finita else None
    
    return {
        "danno": danno,
        "costo_energia": costo_energia,
        "log_entry": log_entry,
        "battaglia_finita": battaglia_finita,
        "vincitore": vincitore
    }

# ============ AI NARRATION (SIMPLIFIED) ============

@api_router.post("/ai/narrate-action")
async def narrate_action(data: Dict[str, Any], request: Request):
    """Simple narration: who did what and the effects"""
    await get_current_user(request)
    
    attacker = data.get("attacker", "Giocatore")
    action = data.get("action", "attacco")
    damage = data.get("damage", 0)
    effect = data.get("effect", "")
    
    # Simple template narration (no AI needed for basic)
    if damage > 0:
        narration = f"{attacker} esegue {action}. Infligge {damage} danni."
    else:
        narration = f"{attacker} esegue {action}. {effect}"
    
    return {"narration": narration}

# ============ WORLD & NAVIGATION ============

# ============ FOUR SEAS MAPS ============

SEAS = {
    "east_blue": {
        "name": "East Blue",
        "description": "Il mare più debole dei quattro, ma patria di grandi pirati come Gol D. Roger e Monkey D. Luffy.",
        "color": "#3B82F6"
    },
    "west_blue": {
        "name": "West Blue",
        "description": "Mare occidentale, patria degli studiosi di Ohara e del potente regno di Kano.",
        "color": "#10B981"
    },
    "north_blue": {
        "name": "North Blue",
        "description": "Mare settentrionale, freddo e misterioso. Patria del Supernova Trafalgar Law.",
        "color": "#8B5CF6"
    },
    "south_blue": {
        "name": "South Blue",
        "description": "Mare meridionale, noto per le arti marziali e come luogo di nascita di Portgas D. Ace.",
        "color": "#F59E0B"
    }
}

ISLANDS = {
    # ============ EAST BLUE ============
    "dawn_island": {
        "name": "Dawn Island",
        "sea": "east_blue",
        "order": 1,
        "x": 10, "y": 70,
        "storia": "L'isola dove tutto ha avuto inizio. Patria di Monkey D. Luffy, Portgas D. Ace e Sabo. Qui il leggendario pirata Shanks il Rosso salvò un giovane Luffy da un Re del Mare, perdendo il braccio sinistro e affidandogli il suo prezioso cappello di paglia.",
        "zone": [
            {"id": "foosha", "name": "Foosha Village", "descrizione": "Tranquillo villaggio di pescatori dove Luffy è cresciuto. Qui si trova la taverna di Makino."},
            {"id": "mt_colubo", "name": "Mt. Colubo", "descrizione": "Montagna selvaggia dove vivono i banditi di montagna guidati da Curly Dadan, che ha cresciuto Ace e Luffy."},
            {"id": "gray_terminal", "name": "Gray Terminal", "descrizione": "Enorme discarica ai confini del regno di Goa, dove vivevano i reietti della società. Fu bruciata per ordine dei nobili."},
            {"id": "midway_forest", "name": "Midway Forest", "descrizione": "Foresta tra il Gray Terminal e il regno di Goa. Qui Ace, Sabo e Luffy costruirono la loro base segreta."},
            {"id": "goa_kingdom", "name": "Goa Kingdom", "descrizione": "Il regno più ricco dell'East Blue, governato da nobili corrotti che disprezzano i poveri."}
        ],
        "pericolo": 2
    },
    "shells_town": {
        "name": "Shells Town",
        "sea": "east_blue",
        "order": 2,
        "x": 20, "y": 60,
        "storia": "Città portuale nella regione di Yotsuba Island con una base della Marina comandata dal Capitano Morgan. Qui Roronoa Zoro era tenuto prigioniero dopo aver salvato una bambina. Luffy lo liberò e Zoro divenne il primo membro della ciurma.",
        "zone": [],
        "pericolo": 3
    },
    "shimotsuki_village": {
        "name": "Shimotsuki Village",
        "sea": "east_blue",
        "order": 3,
        "x": 28, "y": 55,
        "storia": "Villaggio fondato da samurai fuggiti da Wano 50 anni fa. Qui si trova il dojo del maestro Koshiro dove Roronoa Zoro si allenò fin da bambino insieme a Kuina, giurando di diventare il più grande spadaccino del mondo.",
        "zone": [],
        "pericolo": 2
    },
    "organ_islands": {
        "name": "Organ Islands",
        "sea": "east_blue",
        "order": 4,
        "x": 36, "y": 50,
        "storia": "Arcipelago un tempo prospero, devastato dalla ciurma di Buggy il Clown. Qui Luffy sconfisse Buggy, il pirata che aveva mangiato il frutto Bara Bara.",
        "zone": [
            {"id": "orange_town", "name": "Orange Town", "descrizione": "Città principale dell'arcipelago, attaccata da Buggy il Clown. Il sindaco Boodle difese la città con coraggio."}
        ],
        "pericolo": 4
    },
    "island_rare_animals": {
        "name": "Island of Rare Animals",
        "sea": "east_blue",
        "order": 5,
        "x": 44, "y": 45,
        "storia": "Isola misteriosa abitata da creature ibride uniche al mondo. Qui vive Gaimon, un uomo intrappolato in un forziere per 20 anni mentre cercava un tesoro.",
        "zone": [],
        "pericolo": 2
    },
    "gecko_islands": {
        "name": "Gecko Islands",
        "sea": "east_blue",
        "order": 6,
        "x": 52, "y": 48,
        "storia": "Arcipelago pacifico, casa di Usopp e della sua amica d'infanzia Kaya. Il Capitano Kuro tentò di assassinare Kaya per la sua eredità, ma fu fermato da Luffy. Qui i Mugiwara ottennero la Going Merry.",
        "zone": [
            {"id": "syrup_village", "name": "Syrup Village", "descrizione": "Tranquillo villaggio dove Usopp raccontava le sue bugie quotidiane. Qui si trova la villa di Kaya."}
        ],
        "pericolo": 3
    },
    "baratie": {
        "name": "Baratie",
        "sea": "east_blue",
        "order": 7,
        "x": 60, "y": 42,
        "storia": "Il famoso ristorante galleggiante nella regione di Sambas, gestito dallo chef Zeff 'Gamba Rossa'. Qui Sanji lavorava come sous-chef finché Luffy non lo convinse a unirsi alla ciurma. Il Baratie fu attaccato da Don Krieg.",
        "zone": [],
        "pericolo": 5
    },
    "conomi_islands": {
        "name": "Conomi Islands",
        "sea": "east_blue",
        "order": 8,
        "x": 70, "y": 38,
        "storia": "Arcipelago terrorizzato per otto anni dal tritone Arlong. Nami fu costretta a disegnare mappe per lui. Luffy distrusse Arlong Park e liberò Nami dalla sua prigionia.",
        "zone": [
            {"id": "gosa_village", "name": "Gosa Village", "descrizione": "Villaggio distrutto da Arlong come monito per chi osava ribellarsi."},
            {"id": "cocoyasi_village", "name": "Cocoyasi Village", "descrizione": "Villaggio natale di Nami, dove visse con Bellemere e Nojiko."},
            {"id": "ex_arlong_park", "name": "Ex Arlong Park", "descrizione": "Le rovine della fortezza di Arlong, ora simbolo della liberazione dell'arcipelago."}
        ],
        "pericolo": 6
    },
    "loguetown": {
        "name": "Loguetown",
        "sea": "east_blue",
        "order": 9,
        "x": 85, "y": 50,
        "storia": "La 'Città dell'Inizio e della Fine' nelle Polestar Islands, dove Gol D. Roger nacque e fu giustiziato 22 anni fa. Le sue ultime parole diedero inizio alla Grande Era della Pirateria. Qui Luffy sfuggì all'esecuzione grazie a un fulmine.",
        "zone": [],
        "pericolo": 5
    },
    
    # ============ WEST BLUE ============
    "ohara": {
        "name": "Ohara",
        "sea": "west_blue",
        "order": 1,
        "x": 10, "y": 70,
        "storia": "L'isola degli studiosi, un tempo sede della più grande biblioteca del mondo e dell'Albero della Conoscenza. Gli archeologi di Ohara studiavano i Ponegliff. 20 anni fa, il Buster Call distrusse l'intera isola. L'unica sopravvissuta fu Nico Robin.",
        "zone": [],
        "pericolo": 2
    },
    "ilisia_kingdom": {
        "name": "Ilisia Kingdom",
        "sea": "west_blue",
        "order": 2,
        "x": 22, "y": 62,
        "storia": "Un pacifico regno del West Blue, affiliato al Governo Mondiale. Importante centro commerciale e diplomatico della regione.",
        "zone": [],
        "pericolo": 1
    },
    "thriller_bark_origin": {
        "name": "Thriller Bark (Origine)",
        "sea": "west_blue",
        "order": 3,
        "x": 34, "y": 55,
        "storia": "Il luogo d'origine della gigantesca nave-isola Thriller Bark, creata da Gecko Moria. Prima di essere portata nel Florian Triangle, questa nave fantasma fu costruita qui nel West Blue.",
        "zone": [],
        "pericolo": 4
    },
    "toroa": {
        "name": "Toroa",
        "sea": "west_blue",
        "order": 4,
        "x": 46, "y": 48,
        "storia": "Isola nota per i suoi abili artigiani di spade. Molte lame famose del mondo provengono da qui. I fabbri di Toroa sono rispettati in tutto il West Blue.",
        "zone": [],
        "pericolo": 3
    },
    "las_camp": {
        "name": "Las Camp",
        "sea": "west_blue",
        "order": 5,
        "x": 58, "y": 42,
        "storia": "Isola con un clima arido. Nonostante le difficili condizioni, è un importante punto commerciale per i viaggiatori del West Blue.",
        "zone": [],
        "pericolo": 3
    },
    "kano_country": {
        "name": "Kano Country",
        "sea": "west_blue",
        "order": 6,
        "x": 70, "y": 38,
        "storia": "Potente nazione del West Blue, patria della famiglia Chinjao e dell'Armata Happo. Don Chinjao era un temuto pirata con una taglia di 500 milioni. Sai, suo nipote, è ora il 13° comandante della Flotta dei Cappelli di Paglia.",
        "zone": [],
        "pericolo": 5
    },
    "god_valley": {
        "name": "God Valley",
        "sea": "west_blue",
        "order": 7,
        "x": 85, "y": 50,
        "storia": "Isola misteriosa dove 38 anni fa si svolse l'epica battaglia tra i Rocks Pirates e l'alleanza tra Monkey D. Garp e Gol D. Roger. Dopo la battaglia, l'isola scomparve dalle mappe. I suoi segreti sono ancora avvolti nel mistero.",
        "zone": [],
        "pericolo": 10
    },
    
    # ============ NORTH BLUE ============
    "downs": {
        "name": "Downs",
        "sea": "north_blue",
        "order": 1,
        "x": 10, "y": 70,
        "storia": "Isola fredda del North Blue, punto di partenza per molti avventurieri che vogliono esplorare questo mare gelido e misterioso.",
        "zone": [],
        "pericolo": 2
    },
    "lvneel_kingdom": {
        "name": "Lvneel Kingdom",
        "sea": "north_blue",
        "order": 2,
        "x": 20, "y": 62,
        "storia": "Antico e prospero regno del North Blue. 400 anni fa, l'esploratore Montblanc Noland partì da qui per scoprire la Città d'Oro di Shandora. Tornato senza prove, fu giustiziato come bugiardo.",
        "zone": [],
        "pericolo": 1
    },
    "spider_miles": {
        "name": "Spider Miles",
        "sea": "north_blue",
        "order": 3,
        "x": 30, "y": 55,
        "storia": "Un'isola portuale senza legge, rifugio di pirati e criminali. Qui il giovane Donquixote Doflamingo assassinò suo padre dopo essere stato cacciato da Mary Geoise.",
        "zone": [],
        "pericolo": 6
    },
    "flevance": {
        "name": "Flevance",
        "sea": "north_blue",
        "order": 4,
        "x": 40, "y": 48,
        "storia": "La 'Città Bianca', splendente per il piombo ambrato che la ricopriva. Ma il minerale era velenoso. Quando la popolazione si ammalò, il Governo insabbiò la verità. L'isola fu sterminata. L'unico sopravvissuto fu Trafalgar Law.",
        "zone": [],
        "pericolo": 3
    },
    "rubeck_island": {
        "name": "Rubeck Island",
        "sea": "north_blue",
        "order": 5,
        "x": 50, "y": 42,
        "storia": "Isola del North Blue dove la ciurma di Donquixote Rosinante cercò una cura per Law. Un'isola con risorse mediche limitate.",
        "zone": [],
        "pericolo": 2
    },
    "swallow_island": {
        "name": "Swallow Island",
        "sea": "north_blue",
        "order": 6,
        "x": 58, "y": 38,
        "storia": "Isola pacifica del North Blue nota per i suoi medici competenti. Qui Corazon portò Law nella speranza di trovare una cura per il Morbo del Piombo Ambrato.",
        "zone": [],
        "pericolo": 2
    },
    "minion_island": {
        "name": "Minion Island",
        "sea": "north_blue",
        "order": 7,
        "x": 66, "y": 45,
        "storia": "Isola innevata dove si svolse una delle tragedie più grandi. Qui Doflamingo attaccò per rubare l'Ope Ope no Mi, ma Corazon lo diede a Law, sacrificando la sua vita.",
        "zone": [],
        "pericolo": 5
    },
    "rakesh": {
        "name": "Rakesh",
        "sea": "north_blue",
        "order": 8,
        "x": 74, "y": 52,
        "storia": "Isola commerciale del North Blue, nota per i suoi mercati e scambi tra viaggiatori di diverse regioni.",
        "zone": [],
        "pericolo": 2
    },
    "notice": {
        "name": "Notice",
        "sea": "north_blue",
        "order": 9,
        "x": 82, "y": 40,
        "storia": "Isola del North Blue nota come punto di ritrovo per mercanti e viaggiatori. Un luogo dove le informazioni viaggiano veloci.",
        "zone": [],
        "pericolo": 2
    },
    "kuen_village": {
        "name": "Kuen Village",
        "sea": "north_blue",
        "order": 10,
        "x": 88, "y": 48,
        "storia": "Piccolo villaggio di pescatori del North Blue, dove la vita scorre tranquilla lontano dai grandi conflitti.",
        "zone": [],
        "pericolo": 1
    },
    "deul_kingdom": {
        "name": "Deul Kingdom",
        "sea": "north_blue",
        "order": 11,
        "x": 92, "y": 55,
        "storia": "Regno del North Blue affiliato al Governo Mondiale. Mantiene relazioni diplomatiche con le altre nazioni della regione.",
        "zone": [],
        "pericolo": 2
    },
    
    # ============ SOUTH BLUE ============
    "baterilla": {
        "name": "Baterilla",
        "sea": "south_blue",
        "order": 1,
        "x": 10, "y": 70,
        "storia": "L'isola dove nacque Portgas D. Ace, figlio di Gol D. Roger. Sua madre, Portgas D. Rouge, tenne Ace nel grembo per 20 mesi per proteggerlo dalla Marina, morendo dopo il parto.",
        "zone": [],
        "pericolo": 2
    },
    "torino_kingdom": {
        "name": "Torino Kingdom",
        "sea": "south_blue",
        "order": 2,
        "x": 20, "y": 62,
        "storia": "Isola primitiva abitata da una tribù di umani e giganteschi uccelli. Qui Tony Tony Chopper fu mandato da Kuma e studiò le erbe medicinali avanzate per due anni.",
        "zone": [],
        "pericolo": 3
    },
    "evil_black_drum": {
        "name": "Evil Black Drum Kingdom",
        "sea": "south_blue",
        "order": 3,
        "x": 30, "y": 55,
        "storia": "Regno oscuro del South Blue con una reputazione sinistra. Il suo nome evoca paura tra i viaggiatori della regione.",
        "zone": [],
        "pericolo": 5
    },
    "sorbet_kingdom": {
        "name": "Sorbet Kingdom",
        "sea": "south_blue",
        "order": 4,
        "x": 40, "y": 48,
        "storia": "Piccolo regno povero del South Blue, patria di Bartholomew Kuma e Jewelry Bonney. Kuma era il re amato del popolo prima di diventare uno Shichibukai.",
        "zone": [],
        "pericolo": 2
    },
    "samba_kingdom": {
        "name": "Samba Kingdom",
        "sea": "south_blue",
        "order": 5,
        "x": 50, "y": 42,
        "storia": "Regno vivace del South Blue, noto per la sua cultura festosa e le sue tradizioni musicali.",
        "zone": [],
        "pericolo": 2
    },
    "tumi": {
        "name": "Tumi",
        "sea": "south_blue",
        "order": 6,
        "x": 60, "y": 38,
        "storia": "Isola del South Blue con antiche rovine e misteri ancora da scoprire.",
        "zone": [],
        "pericolo": 3
    },
    "kutsukku_island": {
        "name": "Kutsukku Island",
        "sea": "south_blue",
        "order": 7,
        "x": 70, "y": 45,
        "storia": "Isola del South Blue nota per le sue risorse naturali e i suoi artigiani.",
        "zone": [],
        "pericolo": 2
    },
    "taya_kingdom": {
        "name": "Taya Kingdom",
        "sea": "south_blue",
        "order": 8,
        "x": 78, "y": 52,
        "storia": "Regno pacifico del South Blue, affiliato al Governo Mondiale.",
        "zone": [],
        "pericolo": 1
    },
    "vespa_kingdom": {
        "name": "Vespa Kingdom",
        "sea": "south_blue",
        "order": 9,
        "x": 86, "y": 40,
        "storia": "Regno del South Blue con una forte tradizione militare e guerriera.",
        "zone": [],
        "pericolo": 3
    },
    "samuwanai_island": {
        "name": "Samuwanai Island",
        "sea": "south_blue",
        "order": 10,
        "x": 92, "y": 48,
        "storia": "Isola remota del South Blue, ultima tappa prima delle acque della Calm Belt.",
        "zone": [],
        "pericolo": 4
    }
}

# Helper to get islands by sea
def get_islands_by_sea(sea_id: str) -> list:
    """Get all islands from a specific sea, ordered"""
    islands = [(k, v) for k, v in ISLANDS.items() if v["sea"] == sea_id]
    return sorted(islands, key=lambda x: x[1]["order"])

def get_starting_island(sea_id: str) -> str:
    """Get the first island of a sea"""
    starting_islands = {
        "east_blue": "dawn_island",
        "west_blue": "ohara",
        "north_blue": "downs",
        "south_blue": "baterilla"
    }
    return starting_islands.get(sea_id, "dawn_island")

@api_router.get("/world/seas")
async def get_seas(request: Request):
    """Get list of all four seas"""
    await get_current_user(request)
    return {"seas": SEAS}

@api_router.get("/world/seas/{sea_id}/islands")
async def get_sea_islands_view(sea_id: str, request: Request):
    """Get islands of any sea for viewing (not navigation)"""
    await get_current_user(request)
    
    if sea_id not in SEAS:
        raise HTTPException(status_code=400, detail="Mare non trovato")
    
    sea_islands = get_islands_by_sea(sea_id)
    
    islands_list = []
    for island_id, data in sea_islands:
        islands_list.append({
            "id": island_id,
            "name": data["name"],
            "sea": data["sea"],
            "order": data["order"],
            "x": data["x"],
            "y": data["y"],
            "storia": data["storia"],
            "zone": data.get("zone", []),
            "pericolo": data["pericolo"]
        })
    
    return {
        "sea_id": sea_id,
        "sea_info": SEAS[sea_id],
        "islands": islands_list
    }

@api_router.get("/world/islands")
async def get_islands(request: Request):
    user = await get_current_user(request)
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    
    current_sea = character.get("mare_corrente", "east_blue")
    current_island = character.get("isola_corrente", "dawn_island")
    
    # Get islands for current sea
    sea_islands = get_islands_by_sea(current_sea)
    
    # Find current island index
    current_index = 0
    for i, (island_id, _) in enumerate(sea_islands):
        if island_id == current_island:
            current_index = i
            break
    
    islands_list = []
    for i, (island_id, data) in enumerate(sea_islands):
        # Islands are unlocked if they are current, previous, or next
        is_accessible = i <= current_index + 1
        islands_list.append({
            "id": island_id,
            "name": data["name"],
            "sea": data["sea"],
            "order": data["order"],
            "x": data["x"],
            "y": data["y"],
            "storia": data["storia"],
            "zone": data.get("zone", []),
            "pericolo": data["pericolo"],
            "sbloccata": is_accessible,
            "corrente": island_id == current_island,
            "can_travel_back": i < current_index,
            "can_travel_forward": i == current_index + 1 and is_accessible
        })
    
    return {
        "islands": islands_list,
        "isola_corrente": current_island,
        "mare_corrente": current_sea,
        "sea_info": SEAS.get(current_sea, {})
    }

@api_router.post("/world/travel")
async def travel_to_island(data: Dict[str, str], request: Request):
    """Travel to an adjacent island (forward or backward)"""
    user = await get_current_user(request)
    target_island_id = data.get("island_id")
    
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    
    current_sea = character.get("mare_corrente", "east_blue")
    current_island = character.get("isola_corrente", "dawn_island")
    
    # Validate target island exists in current sea
    if target_island_id not in ISLANDS:
        raise HTTPException(status_code=400, detail="Isola non trovata")
    
    target_island = ISLANDS[target_island_id]
    if target_island["sea"] != current_sea:
        raise HTTPException(status_code=400, detail="Puoi viaggiare solo tra isole dello stesso mare")
    
    # Get ordered islands for this sea
    sea_islands = get_islands_by_sea(current_sea)
    island_ids = [iid for iid, _ in sea_islands]
    
    current_index = island_ids.index(current_island) if current_island in island_ids else 0
    target_index = island_ids.index(target_island_id) if target_island_id in island_ids else -1
    
    if target_index == -1:
        raise HTTPException(status_code=400, detail="Isola non trovata in questo mare")
    
    # Can only travel to adjacent islands (one forward or any backward)
    if target_index > current_index + 1:
        raise HTTPException(status_code=400, detail="Non puoi saltare isole! Devi navigare una alla volta.")
    
    # Check if player has a ship for forward travel
    if target_index > current_index:
        if not character.get("nave"):
            raise HTTPException(status_code=400, detail="Hai bisogno di una nave per viaggiare verso nuove isole!")
    
    # Update character location
    await db.characters.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"isola_corrente": target_island_id}}
    )
    
    # Add to logbook
    direction = "⬅️ Ritorno" if target_index < current_index else "➡️ Avanzamento"
    await add_logbook_entry(
        user["user_id"],
        "navigazione",
        f"{direction} verso {target_island['name']}"
    )
    
    return {
        "message": f"Sei arrivato a {target_island['name']}!",
        "island": {
            "id": target_island_id,
            **target_island
        }
    }

# ============ ZONE EXPLORATION & EVENTS ============

# Eventi casuali che possono accadere nelle zone
ZONE_EVENTS = {
    "combattimento": [
        {"tipo": "nemico", "nome": "Bandito di strada", "descrizione": "Un bandito ti attacca per rubarti i Berry!", "ricompensa_berry": 50, "ricompensa_exp": 20, "difficolta": 2},
        {"tipo": "nemico", "nome": "Pirata solitario", "descrizione": "Un pirata sbandato cerca di derubarti.", "ricompensa_berry": 100, "ricompensa_exp": 35, "difficolta": 3},
        {"tipo": "nemico", "nome": "Cacciatore di taglie", "descrizione": "Un cacciatore di taglie ti ha riconosciuto!", "ricompensa_berry": 200, "ricompensa_exp": 50, "difficolta": 4},
        {"tipo": "nemico", "nome": "Soldato della Marina", "descrizione": "Una pattuglia della Marina ti ferma!", "ricompensa_berry": 150, "ricompensa_exp": 40, "difficolta": 4},
    ],
    "scoperta": [
        {"tipo": "tesoro", "nome": "Forziere abbandonato", "descrizione": "Trovi un vecchio forziere nascosto!", "ricompensa_berry": 100},
        {"tipo": "tesoro", "nome": "Sacca di Berry", "descrizione": "Qualcuno ha perso una sacca piena di Berry!", "ricompensa_berry": 75},
        {"tipo": "oggetto", "nome": "Pozione dimenticata", "descrizione": "Trovi una pozione di vita abbandonata.", "oggetto": {"id": "pozione_vita", "name": "Pozione Vita", "effect": {"vita": 30}}},
        {"tipo": "carta", "nome": "Mappa misteriosa", "descrizione": "Trovi una vecchia mappa che potrebbe essere utile.", "carta": {"id": f"carta_mappa_{random.randint(1000,9999)}", "name": "Mappa Misteriosa", "effect": {"bonus_navigazione": 1}}},
    ],
    "sociale": [
        {"tipo": "npc", "nome": "Mercante viaggiatore", "descrizione": "Un mercante ti offre uno sconto speciale.", "effetto": "sconto_shop"},
        {"tipo": "npc", "nome": "Anziano del villaggio", "descrizione": "Un anziano ti racconta storie del passato.", "ricompensa_exp": 25},
        {"tipo": "npc", "nome": "Pirata amichevole", "descrizione": "Un pirata ti offre informazioni utili.", "ricompensa_exp": 30},
        {"tipo": "npc", "nome": "Bambino smarrito", "descrizione": "Aiuti un bambino a tornare a casa.", "ricompensa_exp": 20, "bonus_fortuna": 5},
    ],
    "pericolo": [
        {"tipo": "trappola", "nome": "Tagliola nascosta", "descrizione": "Calpesti una trappola! Ti fai male.", "danno_vita": 15},
        {"tipo": "veleno", "nome": "Fungo velenoso", "descrizione": "Mangi per sbaglio un fungo velenoso.", "danno_vita": 20},
        {"tipo": "furto", "nome": "Borseggiatore", "descrizione": "Un ladro ti ruba alcuni Berry!", "perdita_berry": 50},
    ],
    "riposo": [
        {"tipo": "riposo", "nome": "Locanda accogliente", "descrizione": "Trovi una locanda dove riposarti.", "recupero_vita": 50, "recupero_energia": 30},
        {"tipo": "riposo", "nome": "Sorgente termale", "descrizione": "Scopri una sorgente termale nascosta!", "recupero_vita": 100, "recupero_energia": 50},
        {"tipo": "riposo", "nome": "Campo tranquillo", "descrizione": "Trovi un posto tranquillo per riposare.", "recupero_vita": 30, "recupero_energia": 20},
    ]
}

@api_router.get("/exploration/current-island")
async def get_current_island_info(request: Request):
    """Get detailed info about current island and its zones"""
    user = await get_current_user(request)
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    
    current_island_id = character.get("isola_corrente", "dawn_island")
    
    if current_island_id not in ISLANDS:
        raise HTTPException(status_code=404, detail="Isola non trovata")
    
    island = ISLANDS[current_island_id]
    
    # Get visited zones for this island
    visited_zones = character.get("zone_visitate", {}).get(current_island_id, [])
    
    return {
        "island_id": current_island_id,
        "island": {
            "name": island["name"],
            "storia": island["storia"],
            "pericolo": island["pericolo"],
            "zone": island.get("zone", [])
        },
        "visited_zones": visited_zones,
        "character_stats": {
            "vita": character["vita"],
            "vita_max": character["vita_max"],
            "energia": character["energia"],
            "energia_max": character["energia_max"],
            "berry": character.get("berry", 0)
        }
    }

@api_router.post("/exploration/visit-zone")
async def visit_zone(data: Dict[str, str], request: Request):
    """Visit a specific zone on the current island"""
    user = await get_current_user(request)
    zone_id = data.get("zone_id")
    
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    
    current_island_id = character.get("isola_corrente", "dawn_island")
    island = ISLANDS.get(current_island_id)
    
    if not island:
        raise HTTPException(status_code=404, detail="Isola non trovata")
    
    # Find the zone
    zone = None
    for z in island.get("zone", []):
        if z["id"] == zone_id:
            zone = z
            break
    
    if not zone:
        raise HTTPException(status_code=400, detail="Zona non trovata su questa isola")
    
    # Mark zone as visited
    await db.characters.update_one(
        {"user_id": user["user_id"]},
        {"$addToSet": {f"zone_visitate.{current_island_id}": zone_id}}
    )
    
    # Add to logbook
    await add_logbook_entry(
        user["user_id"],
        "esplorazione",
        f"Hai visitato {zone['name']} su {island['name']}"
    )
    
    return {
        "message": f"Sei arrivato a {zone['name']}!",
        "zone": zone,
        "island": island["name"]
    }

@api_router.post("/exploration/random-event")
async def trigger_random_event(request: Request):
    """Trigger a random event on the current island"""
    user = await get_current_user(request)
    
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    
    current_island_id = character.get("isola_corrente", "dawn_island")
    island = ISLANDS.get(current_island_id)
    
    if not island:
        raise HTTPException(status_code=404, detail="Isola non trovata")
    
    # Choose event category based on island danger level and luck
    pericolo = island.get("pericolo", 1)
    fortuna = character.get("fortuna", 10)
    
    # Weight event categories based on danger and luck
    weights = {
        "scoperta": 30 + fortuna,
        "sociale": 25,
        "riposo": 20 + (fortuna // 2),
        "combattimento": 15 + (pericolo * 3),
        "pericolo": 10 + (pericolo * 2) - (fortuna // 3)
    }
    
    # Normalize weights
    total = sum(weights.values())
    roll = random.randint(1, total)
    
    cumulative = 0
    selected_category = "scoperta"
    for cat, weight in weights.items():
        cumulative += weight
        if roll <= cumulative:
            selected_category = cat
            break
    
    # Select random event from category
    events = ZONE_EVENTS[selected_category]
    event = random.choice(events)
    
    # Apply event effects
    effects_applied = []
    updates = {}
    
    if event.get("ricompensa_berry"):
        updates["$inc"] = updates.get("$inc", {})
        updates["$inc"]["berry"] = event["ricompensa_berry"]
        effects_applied.append(f"+{event['ricompensa_berry']} Berry")
    
    if event.get("ricompensa_exp"):
        updates["$inc"] = updates.get("$inc", {})
        updates["$inc"]["esperienza"] = event["ricompensa_exp"]
        effects_applied.append(f"+{event['ricompensa_exp']} EXP")
    
    if event.get("perdita_berry"):
        current_berry = character.get("berry", 0)
        loss = min(event["perdita_berry"], current_berry)
        updates["$inc"] = updates.get("$inc", {})
        updates["$inc"]["berry"] = -loss
        effects_applied.append(f"-{loss} Berry")
    
    if event.get("danno_vita"):
        current_vita = character.get("vita", 100)
        new_vita = max(1, current_vita - event["danno_vita"])
        updates["$set"] = updates.get("$set", {})
        updates["$set"]["vita"] = new_vita
        effects_applied.append(f"-{event['danno_vita']} Vita")
    
    if event.get("recupero_vita"):
        current_vita = character.get("vita", 100)
        max_vita = character.get("vita_max", 100)
        recovery = min(event["recupero_vita"], max_vita - current_vita)
        if recovery > 0:
            updates["$inc"] = updates.get("$inc", {})
            updates["$inc"]["vita"] = recovery
            effects_applied.append(f"+{recovery} Vita")
    
    if event.get("recupero_energia"):
        current_energia = character.get("energia", 100)
        max_energia = character.get("energia_max", 100)
        recovery = min(event["recupero_energia"], max_energia - current_energia)
        if recovery > 0:
            updates["$inc"] = updates.get("$inc", {})
            updates["$inc"]["energia"] = recovery
            effects_applied.append(f"+{recovery} Energia")
    
    if event.get("oggetto"):
        updates["$push"] = updates.get("$push", {})
        updates["$push"]["oggetti"] = event["oggetto"]
        effects_applied.append(f"Ottenuto: {event['oggetto']['name']}")
    
    if event.get("carta"):
        updates["$push"] = updates.get("$push", {})
        updates["$push"]["carte.storytelling"] = event["carta"]
        effects_applied.append(f"Ottenuta carta: {event['carta']['name']}")
    
    if event.get("bonus_fortuna"):
        updates["$inc"] = updates.get("$inc", {})
        updates["$inc"]["fortuna"] = event["bonus_fortuna"]
        effects_applied.append(f"+{event['bonus_fortuna']} Fortuna")
    
    # Apply updates
    if updates:
        await db.characters.update_one({"user_id": user["user_id"]}, updates)
    
    # Add to logbook
    await add_logbook_entry(
        user["user_id"],
        "evento",
        f"{event['nome']}: {event['descrizione']}"
    )
    
    return {
        "event": {
            "categoria": selected_category,
            "tipo": event["tipo"],
            "nome": event["nome"],
            "descrizione": event["descrizione"]
        },
        "effects_applied": effects_applied,
        "island": island["name"]
    }

# ============ DICE ROLL NAVIGATION (3 STAGES) ============

# Eventi di navigazione in base al dado
NAVIGATION_EVENTS = {
    "facile": [  # Dado 5-6
        {"nome": "Mare Calmo", "descrizione": "La navigazione procede senza intoppi.", "tipo": "positivo", "effetti": []},
        {"nome": "Vento Favorevole", "descrizione": "Un vento favorevole ti spinge avanti!", "tipo": "positivo", "effetti": [{"tipo": "energia", "valore": 10}]},
        {"nome": "Banco di Pesci", "descrizione": "Trovi un banco di pesci e fai scorta di cibo.", "tipo": "positivo", "effetti": [{"tipo": "berry", "valore": 30}]},
    ],
    "medio": [  # Dado 3-4
        {"nome": "Corrente Contraria", "descrizione": "Una corrente rallenta il viaggio.", "tipo": "neutro", "effetti": [{"tipo": "energia", "valore": -10}]},
        {"nome": "Nebbia Fitta", "descrizione": "La nebbia rende la navigazione difficile.", "tipo": "neutro", "effetti": [{"tipo": "energia", "valore": -15}]},
        {"nome": "Uccelli Marini", "descrizione": "Degli uccelli marini indicano la rotta giusta.", "tipo": "positivo", "effetti": []},
    ],
    "difficile": [  # Dado 1-2
        {"nome": "Tempesta!", "descrizione": "Una tempesta si abbatte sulla nave!", "tipo": "sfida", "difficolta": 3, "stat": "difesa", "successo": {"berry": 50, "exp": 20}, "fallimento": {"vita": -25}},
        {"nome": "Pirati Nemici!", "descrizione": "Una nave pirata vi attacca!", "tipo": "sfida", "difficolta": 4, "stat": "attacco", "successo": {"berry": 100, "exp": 30}, "fallimento": {"vita": -30, "berry": -50}},
        {"nome": "Mostro Marino!", "descrizione": "Un mostro marino emerge dalle profondità!", "tipo": "sfida", "difficolta": 5, "stat": "attacco", "successo": {"berry": 150, "exp": 50}, "fallimento": {"vita": -40}},
        {"nome": "Pattuglia Marina!", "descrizione": "Una nave della Marina vi intercetta!", "tipo": "sfida", "difficolta": 4, "stat": "velocita", "successo": {"exp": 40}, "fallimento": {"berry": -100}},
    ]
}

@api_router.get("/navigation/status")
async def get_navigation_status(request: Request):
    """Get current navigation progress"""
    user = await get_current_user(request)
    
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    
    current_sea = character.get("mare_corrente", "east_blue")
    current_island = character.get("isola_corrente", "dawn_island")
    nav_progress = character.get("navigazione_progresso", 0)
    
    # Get islands info
    sea_islands = get_islands_by_sea(current_sea)
    island_ids = [iid for iid, _ in sea_islands]
    current_index = island_ids.index(current_island) if current_island in island_ids else 0
    
    # Get next and previous islands
    next_island = None
    prev_island = None
    
    if current_index < len(island_ids) - 1:
        next_island_id = island_ids[current_index + 1]
        next_island = {"id": next_island_id, **ISLANDS[next_island_id]}
    
    if current_index > 0:
        prev_island_id = island_ids[current_index - 1]
        prev_island = {"id": prev_island_id, **ISLANDS[prev_island_id]}
    
    return {
        "current_island": {"id": current_island, **ISLANDS.get(current_island, {})},
        "next_island": next_island,
        "prev_island": prev_island,
        "progress": nav_progress,
        "progress_required": 3,
        "has_ship": bool(character.get("nave")),
        "ship_type": character.get("nave"),
        "can_advance": nav_progress >= 3 and next_island is not None,
        "can_go_back": prev_island is not None,
        "character_stats": {
            "vita": character.get("vita", 100),
            "vita_max": character.get("vita_max", 100),
            "energia": character.get("energia", 100),
            "energia_max": character.get("energia_max", 100),
            "berry": character.get("berry", 0),
            "attacco": character.get("attacco", 10),
            "difesa": character.get("difesa", 10),
            "velocita": character.get("velocita", 10)
        }
    }

@api_router.post("/navigation/roll-dice")
async def roll_navigation_dice(request: Request):
    """Roll dice for navigation - each roll is a stage with an event"""
    user = await get_current_user(request)
    
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    
    if not character.get("nave"):
        raise HTTPException(status_code=400, detail="Hai bisogno di una nave per navigare!")
    
    current_sea = character.get("mare_corrente", "east_blue")
    current_island = character.get("isola_corrente", "dawn_island")
    nav_progress = character.get("navigazione_progresso", 0)
    
    # Check if already at max progress
    if nav_progress >= 3:
        raise HTTPException(status_code=400, detail="Hai già completato la navigazione! Usa 'Avanza' per raggiungere l'isola.")
    
    # Get next island
    sea_islands = get_islands_by_sea(current_sea)
    island_ids = [iid for iid, _ in sea_islands]
    current_index = island_ids.index(current_island) if current_island in island_ids else 0
    
    if current_index >= len(island_ids) - 1:
        raise HTTPException(status_code=400, detail="Sei già all'ultima isola di questo mare!")
    
    next_island_id = island_ids[current_index + 1]
    next_island = ISLANDS[next_island_id]
    
    # Roll the dice (1-6)
    dice_result = random.randint(1, 6)
    
    # Calculate bonuses
    nave_tipo = character.get("nave", "barca_piccola")
    nave_bonus = {"barca_piccola": 0, "caravella": 1, "brigantino": 2}.get(nave_tipo, 0)
    fortuna = character.get("fortuna", 10)
    fortuna_bonus = fortuna // 20
    
    total_roll = dice_result + nave_bonus + fortuna_bonus
    
    # Determine event difficulty based on roll
    if total_roll >= 5:
        difficulty = "facile"
    elif total_roll >= 3:
        difficulty = "medio"
    else:
        difficulty = "difficile"
    
    # Select random event from category
    event = random.choice(NAVIGATION_EVENTS[difficulty])
    
    # Process event
    effects_applied = []
    event_passed = True
    challenge_result = None
    
    if event["tipo"] == "sfida":
        # This is a challenge - check if character can pass
        stat_name = event["stat"]
        stat_value = character.get(stat_name, 10)
        difficulty_value = event["difficolta"] * 10  # Convert to comparable value
        
        # Roll for challenge (stat + random vs difficulty)
        challenge_roll = stat_value + random.randint(1, 20)
        challenge_result = {
            "stat_used": stat_name,
            "stat_value": stat_value,
            "roll": challenge_roll - stat_value,
            "total": challenge_roll,
            "needed": difficulty_value,
            "passed": challenge_roll >= difficulty_value
        }
        
        if challenge_roll >= difficulty_value:
            # Success!
            event_passed = True
            for key, value in event.get("successo", {}).items():
                if key == "berry":
                    effects_applied.append(f"+{value} Berry")
                    await db.characters.update_one({"user_id": user["user_id"]}, {"$inc": {"berry": value}})
                elif key == "exp":
                    effects_applied.append(f"+{value} EXP")
                    await db.characters.update_one({"user_id": user["user_id"]}, {"$inc": {"esperienza": value}})
        else:
            # Failure
            event_passed = False
            for key, value in event.get("fallimento", {}).items():
                if key == "vita":
                    effects_applied.append(f"{value} Vita")
                    new_vita = max(1, character.get("vita", 100) + value)
                    await db.characters.update_one({"user_id": user["user_id"]}, {"$set": {"vita": new_vita}})
                elif key == "berry":
                    current_berry = character.get("berry", 0)
                    loss = min(abs(value), current_berry)
                    effects_applied.append(f"-{loss} Berry")
                    await db.characters.update_one({"user_id": user["user_id"]}, {"$inc": {"berry": -loss}})
    else:
        # Simple event - apply effects
        for effect in event.get("effetti", []):
            if effect["tipo"] == "energia":
                value = effect["valore"]
                if value > 0:
                    max_energia = character.get("energia_max", 100)
                    current = character.get("energia", 100)
                    actual = min(value, max_energia - current)
                    if actual > 0:
                        effects_applied.append(f"+{actual} Energia")
                        await db.characters.update_one({"user_id": user["user_id"]}, {"$inc": {"energia": actual}})
                else:
                    effects_applied.append(f"{value} Energia")
                    await db.characters.update_one({"user_id": user["user_id"]}, {"$inc": {"energia": value}})
            elif effect["tipo"] == "berry":
                value = effect["valore"]
                effects_applied.append(f"+{value} Berry" if value > 0 else f"{value} Berry")
                await db.characters.update_one({"user_id": user["user_id"]}, {"$inc": {"berry": value}})
            elif effect["tipo"] == "vita":
                value = effect["valore"]
                effects_applied.append(f"{value} Vita")
                new_vita = max(1, character.get("vita", 100) + value)
                await db.characters.update_one({"user_id": user["user_id"]}, {"$set": {"vita": new_vita}})
    
    # Update progress only if event was passed
    new_progress = nav_progress
    if event_passed:
        new_progress = nav_progress + 1
        await db.characters.update_one(
            {"user_id": user["user_id"]},
            {"$set": {"navigazione_progresso": new_progress}}
        )
    
    # Add to logbook
    await add_logbook_entry(
        user["user_id"],
        "navigazione",
        f"Tappa {nav_progress + 1}/3 verso {next_island['name']}: {event['nome']} - {'Superato!' if event_passed else 'Fallito!'}"
    )
    
    return {
        "dice_result": dice_result,
        "bonuses": {"nave": nave_bonus, "fortuna": fortuna_bonus},
        "total": total_roll,
        "difficulty": difficulty,
        "event": {
            "nome": event["nome"],
            "descrizione": event["descrizione"],
            "tipo": event["tipo"]
        },
        "challenge": challenge_result,
        "event_passed": event_passed,
        "effects_applied": effects_applied,
        "progress": {
            "before": nav_progress,
            "after": new_progress,
            "required": 3,
            "complete": new_progress >= 3
        },
        "destination": next_island["name"]
    }

@api_router.post("/navigation/advance")
async def advance_to_next_island(request: Request):
    """Move to the next island after completing 3 navigation stages"""
    user = await get_current_user(request)
    
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    
    nav_progress = character.get("navigazione_progresso", 0)
    if nav_progress < 3:
        raise HTTPException(status_code=400, detail=f"Devi completare la navigazione! Progresso: {nav_progress}/3")
    
    current_sea = character.get("mare_corrente", "east_blue")
    current_island = character.get("isola_corrente", "dawn_island")
    
    # Get next island
    sea_islands = get_islands_by_sea(current_sea)
    island_ids = [iid for iid, _ in sea_islands]
    current_index = island_ids.index(current_island) if current_island in island_ids else 0
    
    if current_index >= len(island_ids) - 1:
        raise HTTPException(status_code=400, detail="Sei già all'ultima isola!")
    
    next_island_id = island_ids[current_index + 1]
    next_island = ISLANDS[next_island_id]
    
    # Move to next island and reset progress
    await db.characters.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"isola_corrente": next_island_id, "navigazione_progresso": 0}}
    )
    
    await add_logbook_entry(
        user["user_id"],
        "navigazione",
        f"Arrivato a {next_island['name']}!"
    )
    
    return {
        "message": f"Sei arrivato a {next_island['name']}!",
        "island": {"id": next_island_id, **next_island}
    }

@api_router.post("/navigation/go-back")
async def go_back_to_previous_island(request: Request):
    """Return to the previous island (always available)"""
    user = await get_current_user(request)
    
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    
    current_sea = character.get("mare_corrente", "east_blue")
    current_island = character.get("isola_corrente", "dawn_island")
    
    # Get previous island
    sea_islands = get_islands_by_sea(current_sea)
    island_ids = [iid for iid, _ in sea_islands]
    current_index = island_ids.index(current_island) if current_island in island_ids else 0
    
    if current_index <= 0:
        raise HTTPException(status_code=400, detail="Sei già alla prima isola di questo mare!")
    
    prev_island_id = island_ids[current_index - 1]
    prev_island = ISLANDS[prev_island_id]
    
    # Move back and reset progress
    await db.characters.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"isola_corrente": prev_island_id, "navigazione_progresso": 0}}
    )
    
    await add_logbook_entry(
        user["user_id"],
        "navigazione",
        f"Tornato a {prev_island['name']} per riposare"
    )
    
    return {
        "message": f"Sei tornato a {prev_island['name']}",
        "island": {"id": prev_island_id, **prev_island}
    }

# ============ SHOP ============

SHOP_ITEMS = {
    "pozione_vita": {"name": "Pozione Vita", "price": 100, "effect": {"vita": 30}},
    "bevanda_energia": {"name": "Bevanda Energia", "price": 80, "effect": {"energia": 25}},
    "spada_base": {"name": "Spada Base", "price": 500, "tipo": "arma", "bonus_attacco": 10},
    "barca_piccola": {"name": "Barca Piccola", "price": 5000, "tipo": "nave", "velocita": 1},
    "caravella": {"name": "Caravella", "price": 20000, "tipo": "nave", "velocita": 2},
    "brigantino": {"name": "Brigantino", "price": 50000, "tipo": "nave", "velocita": 3},
    # Cards
    "carta_vento_favorevole": {"name": "Carta Vento Favorevole", "price": 200, "tipo": "carta", "categoria": "storytelling", "effect": {"bonus_dado": 2}},
    "carta_fuga_rapida": {"name": "Carta Fuga Rapida", "price": 300, "tipo": "carta", "categoria": "duello", "effect": {"skip_turno_nemico": True}},
    "carta_tesoro_nascosto": {"name": "Carta Tesoro Nascosto", "price": 500, "tipo": "carta", "categoria": "eventi", "effect": {"bonus_berry": 1000}},
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
        raise HTTPException(status_code=400, detail="Oggetto non trovato")
    
    item = SHOP_ITEMS[item_id]
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    # Check berry balance
    berry = character.get("berry", 0)
    if berry < item["price"]:
        raise HTTPException(status_code=400, detail=f"Berry insufficienti! Hai {berry}, servono {item['price']}")
    
    # Deduct price
    await db.characters.update_one(
        {"user_id": user["user_id"]},
        {"$inc": {"berry": -item["price"]}}
    )
    
    if item.get("tipo") == "nave":
        await db.characters.update_one(
            {"user_id": user["user_id"]},
            {"$set": {"nave": item_id}}
        )
    elif item.get("tipo") == "arma":
        await db.characters.update_one(
            {"user_id": user["user_id"]},
            {"$push": {"armi": {"id": item_id, **item}}}
        )
    elif item.get("tipo") == "carta":
        categoria = item.get("categoria", "risorse")
        await db.characters.update_one(
            {"user_id": user["user_id"]},
            {"$push": {f"carte.{categoria}": {"id": item_id, **item}}}
        )
    else:
        await db.characters.update_one(
            {"user_id": user["user_id"]},
            {"$push": {"oggetti": {"id": item_id, **item}}}
        )
    
    # Log to logbook
    await add_logbook_entry(user["user_id"], "acquisto", f"Hai acquistato {item['name']} per {item['price']} Berry")
    
    return {"message": f"Acquistato {item['name']}", "item": item}

# ============ LOG BOOK SYSTEM ============

async def add_logbook_entry(user_id: str, tipo: str, descrizione: str, dettagli: Dict = None):
    """Add an entry to the character's logbook"""
    entry = {
        "entry_id": f"log_{uuid.uuid4().hex[:8]}",
        "tipo": tipo,  # navigazione, combattimento, evento, acquisto, ciurma, altro
        "descrizione": descrizione,
        "dettagli": dettagli or {},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    await db.characters.update_one(
        {"user_id": user_id},
        {"$push": {"logbook": {"$each": [entry], "$slice": -100}}}  # Keep last 100 entries
    )
    return entry

async def generate_ai_logbook_entry(user_id: str, evento: str, contesto: Dict):
    """Generate a narrative logbook entry using AI"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        api_key = os.getenv("EMERGENT_LLM_KEY")
        session_id = f"logbook_{uuid.uuid4().hex[:8]}"
        
        character = await db.characters.find_one({"user_id": user_id}, {"_id": 0})
        char_name = character.get("nome_personaggio", "Pirata")
        
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=f"""Sei lo scrittore del diario di bordo di {char_name}, un pirata nel mondo di One Piece.
Scrivi in prima persona come se fossi il personaggio che annota nel suo diario.
Sii conciso (max 2-3 frasi), evocativo e in stile piratesco.
Usa termini nautici e riferimenti al mondo di One Piece quando appropriato."""
        )
        chat.with_model("gemini", "gemini-3-flash-preview")
        
        message = UserMessage(text=f"Scrivi un'annotazione nel diario di bordo per questo evento: {evento}\nContesto: {contesto}")
        response = await chat.send_message(message)
        
        entry = await add_logbook_entry(user_id, "diario", response, {"evento_originale": evento})
        return entry
        
    except Exception as e:
        logger.error(f"AI logbook error: {e}")
        return await add_logbook_entry(user_id, "evento", evento)

@api_router.get("/logbook")
async def get_logbook(request: Request, limit: int = 20):
    """Get character's logbook entries"""
    user = await get_current_user(request)
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    
    logbook = character.get("logbook", [])
    # Return most recent entries first
    return {"entries": list(reversed(logbook[-limit:]))}

@api_router.post("/logbook/add")
async def add_manual_logbook_entry(data: Dict[str, str], request: Request):
    """Manually add a logbook entry"""
    user = await get_current_user(request)
    
    descrizione = data.get("descrizione", "")
    if not descrizione:
        raise HTTPException(status_code=400, detail="Descrizione richiesta")
    
    entry = await add_logbook_entry(user["user_id"], "nota", descrizione)
    return {"entry": entry}

# ============ NAVIGATION WITH DICE ============

NAVIGATION_EVENTS = [
    {"tipo": "calma", "nome": "Mare Calmo", "desc": "Navigazione tranquilla.", "effect": {"energia_recovery": 10}},
    {"tipo": "tempesta", "nome": "Tempesta!", "desc": "Una tempesta colpisce la nave!", "effect": {"danno_nave": 10, "ritardo": 1}},
    {"tipo": "pirati", "nome": "Pirati Nemici!", "desc": "Una nave pirata vi attacca!", "effect": {"combattimento": "pirata_novizio"}},
    {"tipo": "marine", "nome": "Pattuglia Marina!", "desc": "La Marina vi ha avvistato!", "effect": {"combattimento": "marine_soldato"}},
    {"tipo": "tesoro", "nome": "Tesoro alla Deriva!", "desc": "Trovate un forziere galleggiante!", "effect": {"berry": 500, "chance_carta": 0.3}},
    {"tipo": "mercante", "nome": "Nave Mercantile", "desc": "Incontrate un mercante viaggiatore.", "effect": {"shop_sconto": 0.2}},
    {"tipo": "mostro", "nome": "Re del Mare!", "desc": "Un gigantesco mostro marino emerge!", "effect": {"combattimento": "re_del_mare", "fuga_possibile": True}},
    {"tipo": "isola_misteriosa", "nome": "Isola Misteriosa!", "desc": "Avvistate un'isola non segnata sulla mappa!", "effect": {"evento_speciale": True}},
    {"tipo": "corrente", "nome": "Corrente Favorevole", "desc": "Una corrente marina vi spinge avanti!", "effect": {"bonus_movimento": 2}},
    {"tipo": "nebbia", "nome": "Nebbia Fitta", "desc": "La nebbia rallenta il viaggio.", "effect": {"ritardo": 1}},
]

@api_router.post("/navigation/roll-dice")
async def roll_navigation_dice(data: Dict[str, Any], request: Request):
    """Roll dice for navigation and generate event"""
    user = await get_current_user(request)
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    
    if not character.get("nave"):
        raise HTTPException(status_code=400, detail="Hai bisogno di una nave per navigare!")
    
    destinazione = data.get("destinazione", "open_sea")
    carta_usata = data.get("carta_id")
    
    # Base dice roll (1-6)
    dado = random.randint(1, 6)
    bonus = 0
    
    # Apply card bonus if used
    if carta_usata:
        carte_storytelling = character.get("carte", {}).get("storytelling", [])
        for i, carta in enumerate(carte_storytelling):
            if carta.get("id") == carta_usata:
                bonus = carta.get("effect", {}).get("bonus_dado", 0)
                # Remove used card
                await db.characters.update_one(
                    {"user_id": user["user_id"]},
                    {"$pull": {"carte.storytelling": {"id": carta_usata}}}
                )
                break
    
    # Ship speed bonus
    nave_id = character.get("nave")
    nave_speed = SHOP_ITEMS.get(nave_id, {}).get("velocita", 1)
    
    movimento_totale = dado + bonus + nave_speed
    
    # Generate random event
    evento = random.choice(NAVIGATION_EVENTS)
    
    # Apply event effects
    effects_applied = []
    
    if evento["effect"].get("energia_recovery"):
        recovery = evento["effect"]["energia_recovery"]
        await db.characters.update_one(
            {"user_id": user["user_id"]},
            {"$inc": {"energia": recovery}}
        )
        effects_applied.append(f"+{recovery} Energia")
    
    if evento["effect"].get("berry"):
        berry_gain = evento["effect"]["berry"]
        await db.characters.update_one(
            {"user_id": user["user_id"]},
            {"$inc": {"berry": berry_gain}}
        )
        effects_applied.append(f"+{berry_gain} Berry")
    
    if evento["effect"].get("bonus_movimento"):
        movimento_totale += evento["effect"]["bonus_movimento"]
        effects_applied.append(f"+{evento['effect']['bonus_movimento']} Movimento")
    
    # Update navigation progress
    progress = character.get("navigazione_progresso", 0) + movimento_totale
    distanza_necessaria = 10  # Default distance to next island
    
    await db.characters.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"navigazione_progresso": progress}}
    )
    
    # Check if arrived
    arrivato = progress >= distanza_necessaria
    
    # Log to logbook
    await generate_ai_logbook_entry(
        user["user_id"],
        f"Navigazione: dado {dado}, movimento {movimento_totale}. Evento: {evento['nome']}",
        {"destinazione": destinazione, "evento": evento["tipo"]}
    )
    
    return {
        "dado": dado,
        "bonus": bonus,
        "velocita_nave": nave_speed,
        "movimento_totale": movimento_totale,
        "progresso": progress,
        "distanza_necessaria": distanza_necessaria,
        "arrivato": arrivato,
        "evento": evento,
        "effetti_applicati": effects_applied
    }

@api_router.post("/navigation/arrive")
async def arrive_at_destination(data: Dict[str, str], request: Request):
    """Arrive at destination island"""
    user = await get_current_user(request)
    island_id = data.get("island_id")
    
    if island_id not in ISLANDS:
        raise HTTPException(status_code=400, detail="Isola non trovata")
    
    island = ISLANDS[island_id]
    
    await db.characters.update_one(
        {"user_id": user["user_id"]},
        {"$set": {
            "isola_corrente": island_id,
            "navigazione_progresso": 0
        }}
    )
    
    # Log arrival
    await generate_ai_logbook_entry(
        user["user_id"],
        f"Arrivo a {island['name']}",
        {"island_id": island_id, "saga": island["saga"]}
    )
    
    return {"message": f"Arrivato a {island['name']}", "island": island}

# ============ CREW SYSTEM ============

@api_router.post("/crew/create")
async def create_crew(data: Dict[str, str], request: Request):
    """Create a new crew"""
    user = await get_current_user(request)
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    
    if character.get("ciurma_id"):
        raise HTTPException(status_code=400, detail="Sei già in una ciurma!")
    
    nome_ciurma = data.get("nome")
    if not nome_ciurma:
        raise HTTPException(status_code=400, detail="Nome ciurma richiesto")
    
    # Check if crew name exists
    existing = await db.crews.find_one({"nome": nome_ciurma})
    if existing:
        raise HTTPException(status_code=400, detail="Nome ciurma già in uso")
    
    crew_id = f"crew_{uuid.uuid4().hex[:12]}"
    crew = {
        "crew_id": crew_id,
        "nome": nome_ciurma,
        "fondatore_id": character["character_id"],
        "fondatore_nome": character["nome_personaggio"],
        "capitano_id": character["character_id"],
        "membri": [{
            "character_id": character["character_id"],
            "nome": character["nome_personaggio"],
            "ruolo": "capitano",
            "mestiere": character["mestiere"]
        }],
        "nave": character.get("nave"),
        "jolly_roger": data.get("jolly_roger", "default"),
        "taglia_totale": character.get("taglia", 0),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.crews.insert_one(crew)
    
    # Update character
    await db.characters.update_one(
        {"user_id": user["user_id"]},
        {"$set": {
            "ciurma_id": crew_id,
            "ciurma_ruolo": "fondatore"
        }}
    )
    
    # Log
    await add_logbook_entry(user["user_id"], "ciurma", f"Hai fondato la ciurma '{nome_ciurma}'!")
    
    crew.pop("_id", None)
    return {"crew": crew}

@api_router.post("/crew/join")
async def join_crew(data: Dict[str, str], request: Request):
    """Join an existing crew"""
    user = await get_current_user(request)
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    
    if character.get("ciurma_id"):
        raise HTTPException(status_code=400, detail="Sei già in una ciurma!")
    
    crew_id = data.get("crew_id")
    crew = await db.crews.find_one({"crew_id": crew_id}, {"_id": 0})
    
    if not crew:
        raise HTTPException(status_code=404, detail="Ciurma non trovata")
    
    # Add member
    nuovo_membro = {
        "character_id": character["character_id"],
        "nome": character["nome_personaggio"],
        "ruolo": "membro",
        "mestiere": character["mestiere"]
    }
    
    await db.crews.update_one(
        {"crew_id": crew_id},
        {
            "$push": {"membri": nuovo_membro},
            "$inc": {"taglia_totale": character.get("taglia", 0)}
        }
    )
    
    # Update character
    await db.characters.update_one(
        {"user_id": user["user_id"]},
        {"$set": {
            "ciurma_id": crew_id,
            "ciurma_ruolo": "membro"
        }}
    )
    
    # Log
    await add_logbook_entry(user["user_id"], "ciurma", f"Ti sei unito alla ciurma '{crew['nome']}'!")
    
    return {"message": f"Ti sei unito alla ciurma {crew['nome']}!"}

@api_router.post("/crew/leave")
async def leave_crew(request: Request):
    """Leave current crew"""
    user = await get_current_user(request)
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    
    crew_id = character.get("ciurma_id")
    if not crew_id:
        raise HTTPException(status_code=400, detail="Non sei in una ciurma")
    
    crew = await db.crews.find_one({"crew_id": crew_id}, {"_id": 0})
    
    # Check if founder
    if crew.get("fondatore_id") == character["character_id"]:
        # If founder leaves, disband crew or transfer ownership
        if len(crew.get("membri", [])) <= 1:
            # Disband
            await db.crews.delete_one({"crew_id": crew_id})
        else:
            # Transfer to first other member
            new_captain = next((m for m in crew["membri"] if m["character_id"] != character["character_id"]), None)
            if new_captain:
                await db.crews.update_one(
                    {"crew_id": crew_id},
                    {
                        "$set": {"capitano_id": new_captain["character_id"]},
                        "$pull": {"membri": {"character_id": character["character_id"]}},
                        "$inc": {"taglia_totale": -character.get("taglia", 0)}
                    }
                )
    else:
        # Regular member leaves
        await db.crews.update_one(
            {"crew_id": crew_id},
            {
                "$pull": {"membri": {"character_id": character["character_id"]}},
                "$inc": {"taglia_totale": -character.get("taglia", 0)}
            }
        )
    
    # Update character
    await db.characters.update_one(
        {"user_id": user["user_id"]},
        {"$set": {
            "ciurma_id": None,
            "ciurma_ruolo": None
        }}
    )
    
    await add_logbook_entry(user["user_id"], "ciurma", f"Hai lasciato la ciurma '{crew['nome']}'")
    
    return {"message": "Hai lasciato la ciurma"}

@api_router.get("/crew/my")
async def get_my_crew(request: Request):
    """Get current user's crew info"""
    user = await get_current_user(request)
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    
    crew_id = character.get("ciurma_id")
    if not crew_id:
        return {"crew": None}
    
    crew = await db.crews.find_one({"crew_id": crew_id}, {"_id": 0})
    return {"crew": crew}

@api_router.get("/crew/search")
async def search_crews(request: Request, query: str = ""):
    """Search for crews to join"""
    await get_current_user(request)
    
    filter_query = {}
    if query:
        filter_query["nome"] = {"$regex": query, "$options": "i"}
    
    crews = await db.crews.find(filter_query, {"_id": 0}).limit(20).to_list(20)
    return {"crews": crews}

# ============ WEBSOCKET CHAT ============

chat_rooms: Dict[str, Dict[str, WebSocket]] = {}  # room_id -> {user_id: websocket}

@app.websocket("/ws/chat/{room_id}")
async def websocket_chat(websocket: WebSocket, room_id: str):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    # Get token from query params
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Token required")
        return
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
    except JWTError:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    # Get user info
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    character = await db.characters.find_one({"user_id": user_id}, {"_id": 0})
    username = character.get("nome_personaggio") if character else user.get("display_username", "Anonimo")
    
    # Add to room
    if room_id not in chat_rooms:
        chat_rooms[room_id] = {}
    chat_rooms[room_id][user_id] = websocket
    
    try:
        # Notify join
        join_msg = {
            "type": "system",
            "message": f"{username} è entrato nella chat",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await broadcast_to_room(room_id, join_msg)
        
        while True:
            data = await websocket.receive_json()
            
            message = {
                "type": "message",
                "user_id": user_id,
                "username": username,
                "content": data.get("content", ""),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Save to DB
            await db.chat_messages.insert_one({
                "room_id": room_id,
                **message
            })
            
            # Broadcast to room
            await broadcast_to_room(room_id, message)
            
    except WebSocketDisconnect:
        # Remove from room
        if room_id in chat_rooms and user_id in chat_rooms[room_id]:
            del chat_rooms[room_id][user_id]
        
        # Notify leave
        leave_msg = {
            "type": "system",
            "message": f"{username} ha lasciato la chat",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await broadcast_to_room(room_id, leave_msg)

async def broadcast_to_room(room_id: str, message: Dict):
    """Broadcast message to all users in a chat room"""
    if room_id not in chat_rooms:
        return
    
    disconnected = []
    for uid, ws in chat_rooms[room_id].items():
        try:
            await ws.send_json(message)
        except:
            disconnected.append(uid)
    
    # Clean up disconnected
    for uid in disconnected:
        del chat_rooms[room_id][uid]

@api_router.get("/chat/{room_id}/history")
async def get_chat_history(room_id: str, request: Request, limit: int = 50):
    """Get chat history for a room"""
    await get_current_user(request)
    
    messages = await db.chat_messages.find(
        {"room_id": room_id},
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    
    return {"messages": list(reversed(messages))}

# ============ CARD EFFECTS ============

CARD_EFFECTS = {
    "carta_vento_favorevole": {
        "tipo": "navigazione",
        "descrizione": "+2 al tiro del dado durante la navigazione",
        "effect": {"bonus_dado": 2}
    },
    "carta_fuga_rapida": {
        "tipo": "combattimento",
        "descrizione": "Il nemico perde un turno",
        "effect": {"skip_turno_nemico": True}
    },
    "carta_tesoro_nascosto": {
        "tipo": "evento",
        "descrizione": "Guadagni 1000 Berry extra",
        "effect": {"bonus_berry": 1000}
    },
    "carta_cura_miracolosa": {
        "tipo": "combattimento",
        "descrizione": "Recupera 50% della vita massima",
        "effect": {"heal_percent": 0.5}
    },
    "carta_attacco_sorpresa": {
        "tipo": "combattimento",
        "descrizione": "Il prossimo attacco infligge il doppio del danno",
        "effect": {"damage_multiplier": 2}
    },
    "carta_scudo_temporale": {
        "tipo": "combattimento",
        "descrizione": "Riduce i danni subiti del 50% per 2 turni",
        "effect": {"damage_reduction": 0.5, "durata": 2}
    }
}

@api_router.post("/cards/use")
async def use_card(data: Dict[str, str], request: Request):
    """Use a card and apply its effects"""
    user = await get_current_user(request)
    card_id = data.get("card_id")
    contesto = data.get("contesto", "generale")  # navigazione, combattimento, evento
    
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    
    # Find card in character's collection
    card_found = None
    card_categoria = None
    
    for categoria in ["storytelling", "eventi", "duello", "risorse"]:
        carte = character.get("carte", {}).get(categoria, [])
        for carta in carte:
            if carta.get("id") == card_id:
                card_found = carta
                card_categoria = categoria
                break
        if card_found:
            break
    
    if not card_found:
        raise HTTPException(status_code=400, detail="Carta non trovata nel tuo inventario")
    
    effect = card_found.get("effect", {})
    effects_applied = []
    
    # Apply effects based on context
    if effect.get("bonus_berry"):
        await db.characters.update_one(
            {"user_id": user["user_id"]},
            {"$inc": {"berry": effect["bonus_berry"]}}
        )
        effects_applied.append(f"+{effect['bonus_berry']} Berry")
    
    if effect.get("heal_percent"):
        heal_amount = int(character["vita_max"] * effect["heal_percent"])
        new_vita = min(character["vita_max"], character["vita"] + heal_amount)
        await db.characters.update_one(
            {"user_id": user["user_id"]},
            {"$set": {"vita": new_vita}}
        )
        effects_applied.append(f"+{heal_amount} Vita")
    
    # Remove used card
    await db.characters.update_one(
        {"user_id": user["user_id"]},
        {"$pull": {f"carte.{card_categoria}": {"id": card_id}}}
    )
    
    # Log
    await add_logbook_entry(
        user["user_id"], 
        "carta", 
        f"Hai usato la carta '{card_found.get('name', card_id)}'"
    )
    
    return {
        "message": f"Carta usata: {card_found.get('name', card_id)}",
        "effects_applied": effects_applied,
        "effect": effect
    }

@api_router.get("/cards/effects")
async def get_card_effects(request: Request):
    """Get all available card effects"""
    await get_current_user(request)
    return {"effects": CARD_EFFECTS}

# ============ INVENTORY / ITEMS USAGE ============

@api_router.get("/inventory")
async def get_inventory(request: Request):
    """Get character's full inventory"""
    user = await get_current_user(request)
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    
    return {
        "oggetti": character.get("oggetti", []),
        "armi": character.get("armi", []),
        "carte": character.get("carte", {}),
        "nave": character.get("nave"),
        "berry": character.get("berry", 0)
    }

@api_router.post("/inventory/use-item")
async def use_item(data: Dict[str, str], request: Request):
    """Use a consumable item from inventory"""
    user = await get_current_user(request)
    item_id = data.get("item_id")
    
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    
    # Find item in character's inventory
    oggetti = character.get("oggetti", [])
    item_found = None
    item_index = None
    
    for i, item in enumerate(oggetti):
        if item.get("id") == item_id:
            item_found = item
            item_index = i
            break
    
    if not item_found:
        raise HTTPException(status_code=400, detail="Oggetto non trovato nel tuo inventario")
    
    effect = item_found.get("effect", {})
    effects_applied = []
    
    # Apply effects
    if effect.get("vita"):
        heal_amount = effect["vita"]
        new_vita = min(character["vita_max"], character["vita"] + heal_amount)
        await db.characters.update_one(
            {"user_id": user["user_id"]},
            {"$set": {"vita": new_vita}}
        )
        effects_applied.append(f"+{heal_amount} Vita (ora: {new_vita}/{character['vita_max']})")
    
    if effect.get("energia"):
        energy_amount = effect["energia"]
        new_energia = min(character["energia_max"], character["energia"] + energy_amount)
        await db.characters.update_one(
            {"user_id": user["user_id"]},
            {"$set": {"energia": new_energia}}
        )
        effects_applied.append(f"+{energy_amount} Energia (ora: {new_energia}/{character['energia_max']})")
    
    # Remove used item from inventory
    await db.characters.update_one(
        {"user_id": user["user_id"]},
        {"$pull": {"oggetti": {"id": item_id}}}
    )
    
    # Log to logbook
    await add_logbook_entry(
        user["user_id"], 
        "oggetto", 
        f"Hai usato '{item_found.get('name', item_id)}'"
    )
    
    return {
        "message": f"Usato: {item_found.get('name', item_id)}",
        "effects_applied": effects_applied,
        "effect": effect
    }

@api_router.post("/inventory/equip-weapon")
async def equip_weapon(data: Dict[str, str], request: Request):
    """Equip a weapon (mark as active)"""
    user = await get_current_user(request)
    weapon_id = data.get("weapon_id")
    
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    
    # Find weapon
    armi = character.get("armi", [])
    weapon_found = None
    
    for arma in armi:
        if arma.get("id") == weapon_id:
            weapon_found = arma
            break
    
    if not weapon_found:
        raise HTTPException(status_code=400, detail="Arma non trovata nel tuo inventario")
    
    # Set all weapons to not equipped, then equip selected one
    await db.characters.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"armi.$[].equipped": False}}
    )
    
    await db.characters.update_one(
        {"user_id": user["user_id"], "armi.id": weapon_id},
        {"$set": {"armi.$.equipped": True}}
    )
    
    return {"message": f"Equipaggiato: {weapon_found.get('name', weapon_id)}"}

# ============ NARRATIVE SYSTEM ============

# Pre-written narrative texts for common events
NARRATIVE_TEMPLATES = {
    # Island arrival
    "arrival": [
        "La tua nave attracca dolcemente al porto di {location}. L'aria salmastra porta con sé il profumo di nuove avventure...",
        "Dopo un lungo viaggio, finalmente metti piede su {location}. Cosa ti riserverà questa terra?",
        "Le onde si infrangono sulle rocce mentre approdi a {location}. Una nuova avventura ti attende!",
    ],
    # Zone entry
    "zone_entry": [
        "Ti addentri in {location}. L'atmosfera cambia, ogni passo potrebbe nascondere sorprese...",
        "Entri cautamente in {location}. I tuoi sensi sono all'erta.",
        "{location} si apre davanti a te. Cosa scoprirai in questo luogo?",
    ],
    # Monster encounter
    "monster_encounter": [
        "Un rumore minaccioso rompe il silenzio! Dalle ombre emerge una creatura ostile!",
        "Il terreno trema... qualcosa di pericoloso si avvicina!",
        "ATTENZIONE! Un nemico ti ha individuato e si prepara ad attaccare!",
    ],
    # Treasure found
    "treasure_found": [
        "Qualcosa luccica tra le rocce... potrebbe essere un tesoro!",
        "Il tuo occhio allenato nota qualcosa di nascosto. Un'opportunità?",
        "Un forziere abbandonato! Cosa conterrà?",
    ],
    # Battle start
    "battle_start": [
        "Lo scontro è inevitabile! Prepara le tue armi, {player}!",
        "Il nemico ti sfida! È il momento di combattere, {player}!",
        "Non c'è via di fuga... che la battaglia abbia inizio!",
    ],
    # Victory
    "victory": [
        "Con un colpo decisivo, la vittoria è tua! Il nemico cade sconfitto.",
        "Hai trionfato! La tua forza si è dimostrata superiore.",
        "La battaglia è vinta! Raccogli i frutti della tua vittoria.",
    ],
    # Defeat
    "defeat": [
        "Le forze ti abbandonano... questa volta la vittoria non è stata tua.",
        "Il nemico si è dimostrato più forte. Dovrai riprenderti e tornare più preparato.",
        "Sconfitto, ma non arreso. Ogni caduta è una lezione.",
    ],
    # Navigation events
    "navigation_calm": [
        "Il mare è calmo, le stelle guidano la rotta. Un viaggio sereno.",
        "Onde gentili cullano la nave. La navigazione procede senza intoppi.",
    ],
    "navigation_storm": [
        "Il cielo si oscura! Una tempesta si abbatte sulla nave!",
        "Onde gigantesche si infrangono contro lo scafo! Resistere sarà difficile!",
    ],
    "navigation_pirates": [
        "All'orizzonte una bandiera nera! Pirati in avvicinamento!",
        "ALLARME! Una nave nemica vi intercetta! Preparatevi!",
    ],
    # Shop
    "shop_enter": [
        "Entri nel negozio. Gli scaffali sono pieni di oggetti interessanti...",
        "Il mercante ti saluta con un sorriso. 'Cosa posso fare per te, pirata?'",
    ],
    "shop_buy": [
        "Affare fatto! Hai acquistato {item} per {price} Berry.",
        "Il mercante ti consegna {item}. 'Buon viaggio, nakama!'",
    ],
    # Random events
    "random_positive": [
        "Un colpo di fortuna! Qualcosa di buono ti è capitato.",
        "Gli dei del mare ti sorridono oggi!",
    ],
    "random_negative": [
        "Sfortuna! Un imprevisto ti colpisce.",
        "Non tutto va sempre come sperato...",
    ],
}

# Event types with action options
EVENT_ACTIONS = {
    "monster_encounter": [
        {"id": "combat", "label": "⚔️ Combatti", "action": "start_battle", "color": "red"},
        {"id": "card", "label": "🃏 Usa Carta", "action": "use_card", "color": "purple"},
        {"id": "flee", "label": "🏃 Fuggi", "action": "flee", "color": "yellow"},
    ],
    "treasure_found": [
        {"id": "collect", "label": "💰 Raccogli", "action": "collect_treasure", "color": "gold"},
        {"id": "examine", "label": "🔍 Esamina", "action": "examine_treasure", "color": "blue"},
        {"id": "leave", "label": "❌ Ignora", "action": "leave", "color": "gray"},
    ],
    "npc_encounter": [
        {"id": "talk", "label": "💬 Parla", "action": "talk_npc", "color": "blue"},
        {"id": "trade", "label": "🤝 Commercia", "action": "trade_npc", "color": "gold"},
        {"id": "challenge", "label": "⚔️ Sfida", "action": "challenge_npc", "color": "red"},
        {"id": "leave", "label": "👋 Vai via", "action": "leave", "color": "gray"},
    ],
    "navigation_danger": [
        {"id": "face", "label": "💪 Affronta", "action": "face_danger", "color": "red"},
        {"id": "evade", "label": "🌊 Evita", "action": "evade_danger", "color": "blue"},
        {"id": "card", "label": "🃏 Usa Carta", "action": "use_card", "color": "purple"},
    ],
}

@api_router.get("/narrative/templates")
async def get_narrative_templates():
    """Get all narrative templates for client-side rendering"""
    return {"templates": NARRATIVE_TEMPLATES, "actions": EVENT_ACTIONS}

@api_router.post("/narrative/generate")
async def generate_narrative(data: Dict[str, Any], request: Request):
    """Generate narrative text - uses AI for special events, templates for common ones"""
    user = await get_current_user(request)
    
    event_type = data.get("event_type", "general")
    context = data.get("context", {})
    use_ai = data.get("use_ai", False)  # Only use AI for special moments
    
    # Get character info for personalization
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    player_name = character.get("nome_personaggio", "Pirata") if character else "Pirata"
    
    # Try template first
    template_key = event_type
    if template_key in NARRATIVE_TEMPLATES:
        template = random.choice(NARRATIVE_TEMPLATES[template_key])
        narrative = template.format(
            location=context.get("location", "questo luogo"),
            player=player_name,
            item=context.get("item", "un oggetto"),
            price=context.get("price", "???"),
            enemy=context.get("enemy", "un nemico"),
            **context
        )
        
        # Get available actions for this event type
        actions = EVENT_ACTIONS.get(event_type, [])
        
        return {
            "narrative": narrative,
            "source": "template",
            "event_type": event_type,
            "actions": actions,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    # Use AI for custom/special narratives
    if use_ai:
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            api_key = os.getenv("EMERGENT_LLM_KEY")
            session_id = f"narrative_{uuid.uuid4().hex[:8]}"
            
            chat = LlmChat(
                api_key=api_key,
                session_id=session_id,
                system_message="""Sei il narratore di un gioco RPG di One Piece.
Il tuo compito è creare brevi narrazioni epiche ed emozionanti (2-3 frasi max).
Usa un tono avventuroso e coinvolgente, in stile anime/manga.
Non usare emoji. Scrivi in italiano."""
            )
            chat.with_model("gemini", "gemini-3-flash-preview")
            
            prompt = f"Crea una breve narrazione per questo evento: {event_type}. Contesto: {context}. Personaggio: {player_name}."
            message = UserMessage(text=prompt)
            
            response = await chat.send_message(message)
            
            return {
                "narrative": response.strip(),
                "source": "ai",
                "event_type": event_type,
                "actions": EVENT_ACTIONS.get(event_type, []),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"AI narrative generation error: {e}")
    
    # Fallback
    return {
        "narrative": f"Un evento si verifica: {event_type}",
        "source": "fallback",
        "event_type": event_type,
        "actions": [],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@api_router.post("/narrative/action")
async def execute_narrative_action(data: Dict[str, str], request: Request):
    """Execute an action from a narrative event"""
    user = await get_current_user(request)
    
    action_id = data.get("action_id")
    event_type = data.get("event_type")
    context = data.get("context", {})
    
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    
    result = {"success": False, "message": "", "effects": [], "next_event": None}
    
    if action_id == "flee":
        # Flee from monster - chance based on speed
        flee_chance = min(80, 30 + character.get("velocita", 10))
        success = random.randint(1, 100) <= flee_chance
        
        if success:
            result["success"] = True
            result["message"] = "Sei riuscito a fuggire!"
            result["effects"].append("-10 Energia")
            await db.characters.update_one(
                {"user_id": user["user_id"]},
                {"$inc": {"energia": -10}}
            )
        else:
            result["success"] = False
            result["message"] = "Non sei riuscito a fuggire! Il nemico ti attacca!"
            result["next_event"] = {"type": "forced_battle", "enemy": context.get("enemy")}
    
    elif action_id == "collect":
        # Collect treasure
        berry_amount = random.randint(50, 200)
        result["success"] = True
        result["message"] = f"Hai trovato {berry_amount} Berry!"
        result["effects"].append(f"+{berry_amount} Berry")
        await db.characters.update_one(
            {"user_id": user["user_id"]},
            {"$inc": {"berry": berry_amount}}
        )
        await add_logbook_entry(user["user_id"], "tesoro", f"Trovato tesoro: {berry_amount} Berry")
    
    elif action_id == "examine":
        # Examine treasure - might find extra or trap
        roll = random.randint(1, 100)
        if roll > 70:
            # Found extra treasure
            berry_amount = random.randint(100, 500)
            result["success"] = True
            result["message"] = f"Un tesoro nascosto! Hai trovato {berry_amount} Berry!"
            result["effects"].append(f"+{berry_amount} Berry")
            await db.characters.update_one(
                {"user_id": user["user_id"]},
                {"$inc": {"berry": berry_amount}}
            )
        elif roll < 20:
            # Trap!
            damage = random.randint(10, 30)
            result["success"] = False
            result["message"] = f"Era una trappola! Subisci {damage} danni!"
            result["effects"].append(f"-{damage} Vita")
            new_vita = max(1, character.get("vita", 100) - damage)
            await db.characters.update_one(
                {"user_id": user["user_id"]},
                {"$set": {"vita": new_vita}}
            )
        else:
            berry_amount = random.randint(50, 150)
            result["success"] = True
            result["message"] = f"Hai trovato {berry_amount} Berry."
            result["effects"].append(f"+{berry_amount} Berry")
            await db.characters.update_one(
                {"user_id": user["user_id"]},
                {"$inc": {"berry": berry_amount}}
            )
    
    elif action_id == "leave":
        result["success"] = True
        result["message"] = "Decidi di proseguire..."
    
    elif action_id == "talk":
        # Talk to NPC
        dialogues = [
            "L'NPC ti racconta storie del mare...",
            "Ricevi un consiglio utile per il viaggio.",
            "L'NPC condivide informazioni sull'isola.",
        ]
        result["success"] = True
        result["message"] = random.choice(dialogues)
        # Small chance of receiving gift
        if random.randint(1, 100) > 80:
            berry_gift = random.randint(20, 50)
            result["message"] += f" Ti regala {berry_gift} Berry!"
            result["effects"].append(f"+{berry_gift} Berry")
            await db.characters.update_one(
                {"user_id": user["user_id"]},
                {"$inc": {"berry": berry_gift}}
            )
    
    elif action_id == "face":
        # Face danger during navigation
        stat_check = character.get("difesa", 10) + random.randint(1, 20)
        difficulty = context.get("difficulty", 15)
        
        if stat_check >= difficulty:
            result["success"] = True
            result["message"] = "Hai affrontato il pericolo con coraggio!"
            exp_gain = random.randint(20, 50)
            result["effects"].append(f"+{exp_gain} EXP")
            await db.characters.update_one(
                {"user_id": user["user_id"]},
                {"$inc": {"esperienza": exp_gain}}
            )
        else:
            result["success"] = False
            damage = random.randint(15, 35)
            result["message"] = f"Il pericolo ti ha sopraffatto! -{damage} Vita"
            result["effects"].append(f"-{damage} Vita")
            new_vita = max(1, character.get("vita", 100) - damage)
            await db.characters.update_one(
                {"user_id": user["user_id"]},
                {"$set": {"vita": new_vita}}
            )
    
    elif action_id == "evade":
        # Evade danger
        evade_check = character.get("agilita", 10) + random.randint(1, 20)
        difficulty = context.get("difficulty", 12)
        
        if evade_check >= difficulty:
            result["success"] = True
            result["message"] = "Hai evitato il pericolo con astuzia!"
        else:
            result["success"] = False
            result["message"] = "Non sei riuscito ad evitare! Il pericolo ti colpisce!"
            damage = random.randint(10, 25)
            result["effects"].append(f"-{damage} Vita")
            new_vita = max(1, character.get("vita", 100) - damage)
            await db.characters.update_one(
                {"user_id": user["user_id"]},
                {"$set": {"vita": new_vita}}
            )
    
    # Add timestamp
    result["timestamp"] = datetime.now(timezone.utc).isoformat()
    
    return result

# ============ ENHANCED CHAT SYSTEM ============

@api_router.get("/chat/rooms")
async def get_available_chat_rooms(request: Request):
    """Get available chat rooms based on character location"""
    user = await get_current_user(request)
    
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    
    rooms = []
    
    # Sea-level chat (always available)
    current_sea = character.get("mare_corrente", "east_blue")
    sea_names = {
        "east_blue": "East Blue",
        "west_blue": "West Blue", 
        "north_blue": "North Blue",
        "south_blue": "South Blue"
    }
    rooms.append({
        "room_id": f"mare_{current_sea}",
        "name": f"🌊 {sea_names.get(current_sea, current_sea)}",
        "type": "sea",
        "description": "Chat generale del mare"
    })
    
    # Island-level chat (if on an island)
    current_island = character.get("isola_corrente")
    if current_island and current_island in ISLANDS:
        island_name = ISLANDS[current_island].get("name", current_island)
        rooms.append({
            "room_id": f"isola_{current_island}",
            "name": f"🏝️ {island_name}",
            "type": "island",
            "description": f"Chat dell'isola {island_name}"
        })
    
    # Zone-level chat (if in a zone)
    current_zone = character.get("zona_corrente")
    if current_zone and current_island:
        island_data = ISLANDS.get(current_island, {})
        zones = island_data.get("zone", [])
        zone_info = next((z for z in zones if z.get("id") == current_zone), None)
        if zone_info:
            rooms.append({
                "room_id": f"zona_{current_island}_{current_zone}",
                "name": f"📍 {zone_info.get('name', current_zone)}",
                "type": "zone",
                "description": f"Chat della zona {zone_info.get('name')}"
            })
    
    return {"rooms": rooms}

@api_router.post("/chat/send")
async def send_chat_message(data: Dict[str, str], request: Request):
    """Send a message to a chat room (HTTP fallback for non-WebSocket clients)"""
    user = await get_current_user(request)
    
    room_id = data.get("room_id")
    content = data.get("content", "").strip()
    
    if not content:
        raise HTTPException(status_code=400, detail="Messaggio vuoto")
    
    if len(content) > 500:
        raise HTTPException(status_code=400, detail="Messaggio troppo lungo (max 500 caratteri)")
    
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    username = character.get("nome_personaggio") if character else user.get("display_username", "Anonimo")
    
    message = {
        "message_id": str(uuid.uuid4()),
        "room_id": room_id,
        "type": "message",
        "user_id": user["user_id"],
        "username": username,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Save to DB (creates a copy to avoid _id being added to original)
    await db.chat_messages.insert_one({**message})
    
    # Broadcast via WebSocket if connections exist
    await broadcast_to_room(room_id, message)
    
    return {"message": message}

@api_router.post("/chat/system-message")
async def add_system_message(data: Dict[str, str], request: Request):
    """Add a system/narrative message to a chat room (internal use)"""
    user = await get_current_user(request)
    
    room_id = data.get("room_id")
    content = data.get("content")
    message_type = data.get("type", "system")  # system, narrative, event
    
    message = {
        "message_id": str(uuid.uuid4()),
        "room_id": room_id,
        "type": message_type,
        "user_id": "system",
        "username": "📜 Narratore" if message_type == "narrative" else "⚙️ Sistema",
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Save to DB (use copy to avoid _id being added)
    await db.chat_messages.insert_one({**message})
    
    # Broadcast
    await broadcast_to_room(room_id, message)
    
    return {"message": message}

@api_router.post("/narrative/event-with-chat")
async def trigger_narrative_event(data: Dict[str, Any], request: Request):
    """Trigger a narrative event and broadcast to appropriate chat room"""
    user = await get_current_user(request)
    
    event_type = data.get("event_type")
    context = data.get("context", {})
    
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    
    player_name = character.get("nome_personaggio", "Pirata")
    current_island = character.get("isola_corrente", "")
    current_zone = character.get("zona_corrente", "")
    
    # Determine target room (most specific available)
    if current_zone:
        room_id = f"zona_{current_island}_{current_zone}"
    elif current_island:
        room_id = f"isola_{current_island}"
    else:
        current_sea = character.get("mare_corrente", "east_blue")
        room_id = f"mare_{current_sea}"
    
    # Generate narrative
    if event_type in NARRATIVE_TEMPLATES:
        template = random.choice(NARRATIVE_TEMPLATES[event_type])
        narrative = template.format(
            location=context.get("location", "questo luogo"),
            player=player_name,
            item=context.get("item", "un oggetto"),
            price=context.get("price", "???"),
            enemy=context.get("enemy", "un nemico"),
            **{k: v for k, v in context.items() if k not in ["location", "player", "item", "price", "enemy"]}
        )
    else:
        narrative = f"[{player_name}] Un evento si verifica: {event_type}"
    
    # Create narrative message
    message = {
        "message_id": str(uuid.uuid4()),
        "room_id": room_id,
        "type": "narrative",
        "user_id": "system",
        "username": "📜 Narratore",
        "content": narrative,
        "event_type": event_type,
        "actions": EVENT_ACTIONS.get(event_type, []),
        "context": context,
        "target_player": user["user_id"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Save and broadcast (use copy to avoid _id)
    await db.chat_messages.insert_one({**message})
    await broadcast_to_room(room_id, message)
    
    return {
        "narrative": narrative,
        "room_id": room_id,
        "message": message,
        "actions": EVENT_ACTIONS.get(event_type, [])
    }

# ============ ROOT & HEALTH ============

@api_router.get("/")
async def root():
    return {"message": "One Piece RPG - The Grand Line Architect API", "version": "3.0.0"}

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
