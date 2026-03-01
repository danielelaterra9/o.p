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
        
        # Location
        "isola_corrente": "foosha",
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

ISLANDS = {
    "foosha": {"name": "Foosha Village", "saga": "East Blue", "x": 10, "y": 70, "eventi_richiesti": 0},
    "shells_town": {"name": "Shells Town", "saga": "East Blue", "x": 18, "y": 55, "eventi_richiesti": 1},
    "orange_town": {"name": "Orange Town", "saga": "East Blue", "x": 25, "y": 60, "eventi_richiesti": 2},
    "baratie": {"name": "Baratie", "saga": "East Blue", "x": 35, "y": 50, "eventi_richiesti": 3},
    "arlong_park": {"name": "Arlong Park", "saga": "East Blue", "x": 42, "y": 45, "eventi_richiesti": 4},
    "loguetown": {"name": "Loguetown", "saga": "East Blue", "x": 50, "y": 55, "eventi_richiesti": 5},
    "alabasta": {"name": "Alabasta", "saga": "Grand Line", "x": 60, "y": 40, "eventi_richiesti": 8},
    "skypiea": {"name": "Skypiea", "saga": "Grand Line", "x": 65, "y": 20, "eventi_richiesti": 12},
    "water_seven": {"name": "Water 7", "saga": "Grand Line", "x": 72, "y": 45, "eventi_richiesti": 15},
    "wano": {"name": "Wano", "saga": "New World", "x": 92, "y": 30, "eventi_richiesti": 30}
}

@api_router.get("/world/islands")
async def get_islands(request: Request):
    user = await get_current_user(request)
    character = await db.characters.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    if not character:
        raise HTTPException(status_code=404, detail="Personaggio non trovato")
    
    eventi_completati = len(character.get("carte", {}).get("eventi", []))
    
    islands_list = []
    for island_id, data in ISLANDS.items():
        islands_list.append({
            "id": island_id,
            **data,
            "sbloccata": eventi_completati >= data["eventi_richiesti"],
            "corrente": character.get("isola_corrente") == island_id
        })
    
    return {"islands": islands_list, "isola_corrente": character.get("isola_corrente")}

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
