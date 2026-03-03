import React, { useState, useEffect, useCallback, useRef } from "react";
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import "@/App.css";

import { 
  Anchor, Map, Swords, Users, Package, User, Skull, Shield, Heart, 
  Zap, ChevronRight, ChevronLeft, Star, Crown, Compass, LogOut, Dice6, Ship,
  MessageCircle, ShoppingBag, Scroll, Target, Home, MapPin, Info, AlertTriangle,
  Eye, EyeOff, Briefcase, UserCircle, Backpack, Sword, FlaskConical, CreditCard
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ============ AUTH CONTEXT ============
const AuthContext = ({ children }) => {
  const [user, setUser] = useState(null);
  const [character, setCharacter] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  const checkAuth = useCallback(async () => {
    if (window.location.hash?.includes('session_id=')) {
      setLoading(false);
      return;
    }

    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const response = await axios.get(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      });
      setUser(response.data);
      
      try {
        const charResponse = await axios.get(`${API}/characters/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setCharacter(charResponse.data);
      } catch (e) {}
    } catch (error) {
      localStorage.removeItem('token');
      setToken(null);
    }
    setLoading(false);
  }, [token]);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = async (newToken, userData) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
    setUser(userData);
    
    // Load character after login
    try {
      const charResponse = await axios.get(`${API}/characters/me`, {
        headers: { Authorization: `Bearer ${newToken}` }
      });
      setCharacter(charResponse.data);
    } catch (e) {
      // No character yet - that's ok
      setCharacter(null);
    }
  };

  const logout = async () => {
    try {
      await axios.post(`${API}/auth/logout`, {}, { withCredentials: true });
    } catch (e) {}
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setCharacter(null);
  };

  return (
    <div className="auth-context">
      {loading ? (
        <LoadingScreen />
      ) : (
        <AppRouter user={user} character={character} setCharacter={setCharacter} token={token} login={login} logout={logout} />
      )}
    </div>
  );
};

const LoadingScreen = () => (
  <div className="min-h-screen bg-[#051923] flex items-center justify-center">
    <motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: "linear" }}>
      <Compass className="w-16 h-16 text-[#FFC300]" />
    </motion.div>
  </div>
);

const AppRouter = ({ user, character, setCharacter, token, login, logout }) => {
  const location = useLocation();
  
  if (location.hash?.includes('session_id=')) {
    return <AuthCallback login={login} />;
  }

  // Check for demo mode
  const isDemo = localStorage.getItem('demoMode') === 'true';
  const demoCharacter = {
    character_id: "demo-character",
    user_id: "demo-user",
    nome_personaggio: "Demo Pirate",
    ruolo: "pirata",
    genere: "maschio",
    eta: 20,
    razza: "umano",
    stile_combattimento: "corpo_misto",
    mestiere: "capitano",
    sogno: "Diventare il Re dei Pirati",
    storia_carattere: "Un pirata determinato in cerca di avventura",
    tratti_caratteriali: ["Coraggioso", "Determinato", "Leale"],
    livello: 5,
    esperienza: 250,
    vita: 120,
    vita_max: 120,
    energia: 100,
    energia_max: 100,
    attacco: 25,
    difesa: 20,
    velocita: 22,
    fortuna: 15,
    taglia: 50000,
    berry: 5000,
    mare_corrente: "east_blue",
    isola_corrente: "dawn_island",
    nave: "barca_piccola",
    oggetti: [
      { id: "pozione_vita", name: "Pozione Vita", effect: { vita: 30 } },
      { id: "bevanda_energia", name: "Bevanda Energia", effect: { energia: 20 } }
    ],
    armi: [
      { id: "spada_base", name: "Spada Base", bonus_attacco: 5, equipped: true }
    ],
    carte: {
      storytelling: [{ id: "carta_vento", name: "Vento Favorevole", effect: { navigazione: 1 } }]
    },
    logbook: []
  };
  const demoUser = { user_id: "demo-user", username: "DemoPlayer", email: "demo@test.com" };

  const effectiveUser = isDemo ? demoUser : user;
  const effectiveCharacter = isDemo ? demoCharacter : character;
  const effectiveToken = isDemo ? "demo-token" : token;

  const exitDemo = () => {
    localStorage.removeItem('demoMode');
    window.location.href = '/';
  };

  return (
    <Routes>
      <Route path="/" element={effectiveUser ? <Dashboard user={effectiveUser} character={effectiveCharacter} token={effectiveToken} logout={isDemo ? exitDemo : logout} isDemo={isDemo} /> : <LandingPage />} />
      <Route path="/login" element={<LoginPage login={login} />} />
      <Route path="/register" element={<RegisterPage login={login} />} />
      <Route path="/dashboard" element={<Dashboard user={effectiveUser} character={effectiveCharacter} token={effectiveToken} logout={isDemo ? exitDemo : logout} isDemo={isDemo} />} />
      <Route path="/create-character" element={<CharacterCreation token={effectiveToken} setCharacter={setCharacter} />} />
      <Route path="/world-map" element={<WorldMap token={effectiveToken} character={effectiveCharacter} isDemo={isDemo} />} />
      <Route path="/explore" element={<ExploreIsland token={effectiveToken} character={effectiveCharacter} isDemo={isDemo} />} />
      <Route path="/battle" element={<BattleArena token={effectiveToken} character={effectiveCharacter} isDemo={isDemo} />} />
      <Route path="/character" element={<CharacterSheet token={effectiveToken} character={effectiveCharacter} setCharacter={setCharacter} isDemo={isDemo} />} />
      <Route path="/shop" element={<Shop token={effectiveToken} character={effectiveCharacter} isDemo={isDemo} />} />
      <Route path="/inventory" element={<Inventory token={effectiveToken} character={effectiveCharacter} isDemo={isDemo} />} />
    </Routes>
  );
};

const AuthCallback = ({ login }) => {
  const navigate = useNavigate();
  const hasProcessed = useRef(false);

  useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const processAuth = async () => {
      const hash = window.location.hash;
      const sessionId = hash.split('session_id=')[1]?.split('&')[0];
      
      if (sessionId) {
        try {
          const response = await axios.get(`${API}/auth/session?session_id=${sessionId}`, { withCredentials: true });
          login(response.data.session_token || sessionId, response.data);
          navigate('/dashboard', { replace: true });
        } catch (error) {
          navigate('/login', { replace: true });
        }
      }
    };
    processAuth();
  }, [login, navigate]);

  return <LoadingScreen />;
};

// ============ LANDING PAGE ============
const LandingPage = () => {
  const navigate = useNavigate();

  const enterDemo = () => {
    localStorage.setItem('demoMode', 'true');
    window.location.href = '/dashboard';
  };

  return (
    <div className="min-h-screen bg-[#051923] relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-[#003566]/30 to-[#051923]" />
      
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center p-8">
        <motion.div initial={{ opacity: 0, y: -50 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }} className="text-center mb-12">
          <h1 className="font-pirate text-6xl md:text-8xl text-[#FFC300] mb-4 drop-shadow-lg">The Grand Line</h1>
          <h2 className="font-pirate text-2xl md:text-4xl text-[#E3D5CA] mb-4">Architect</h2>
          <p className="text-[#E3D5CA]/80 text-lg max-w-lg mx-auto">
            Crea il tuo pirata, esplora il Grand Line, combatti nemici epici e diventa il Re dei Pirati!
          </p>
        </motion.div>

        <motion.div className="flex flex-col gap-4 w-full max-w-sm" initial={{ opacity: 0, y: 50 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.3 }}>
          <motion.button onClick={() => navigate('/register')} className="btn-gold py-4 px-8 text-lg font-pirate rounded-lg" whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} data-testid="start-adventure-btn">
            Inizia l'Avventura
          </motion.button>
          
          <motion.button onClick={() => navigate('/login')} className="bg-[#3E2723] text-[#E3D5CA] py-3 px-8 rounded-lg border-2 border-[#D4AF37] font-bold" whileHover={{ scale: 1.02 }} data-testid="login-btn">
            Accedi
          </motion.button>

          <motion.button onClick={() => {
            const redirectUrl = window.location.origin + '/dashboard';
            window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
          }} className="glass py-3 px-8 rounded-lg text-[#E3D5CA] font-medium flex items-center justify-center gap-2" whileHover={{ scale: 1.02 }} data-testid="google-login-btn">
            <img src="https://www.google.com/favicon.ico" alt="Google" className="w-5 h-5" />
            Accedi con Google
          </motion.button>

          <div className="relative my-2">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-[#E3D5CA]/20"></div>
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="px-2 bg-[#051923] text-[#E3D5CA]/50">oppure</span>
            </div>
          </div>

          <motion.button 
            onClick={enterDemo} 
            className="py-3 px-8 rounded-lg text-[#2A9D8F] font-medium border-2 border-[#2A9D8F]/50 hover:bg-[#2A9D8F]/10 transition-colors flex items-center justify-center gap-2" 
            whileHover={{ scale: 1.02 }}
            data-testid="demo-btn"
          >
            <Eye className="w-5 h-5" />
            🎮 Modalità Demo / Preview
          </motion.button>
        </motion.div>
      </div>
    </div>
  );
};

// ============ REGISTER PAGE ============
const RegisterPage = ({ login }) => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      console.log('Registering user...', { username, email });
      const response = await axios.post(`${API}/auth/register`, { username, email, password });
      console.log('Registration response:', response.data);
      
      if (response.data.token) {
        await login(response.data.token, response.data.user);
        navigate('/create-character');
      } else {
        setError('Risposta server non valida');
        setLoading(false);
      }
    } catch (err) {
      console.error('Registration error:', err);
      setError(err.response?.data?.detail || 'Errore durante la registrazione');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#051923] flex items-center justify-center p-4">
      <motion.div className="glass p-8 rounded-xl w-full max-w-md" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}>
        <h1 className="font-pirate text-3xl text-[#FFC300] mb-6 text-center">Registrazione</h1>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-[#D4AF37] mb-1 text-sm">Username (per contatti e amici)</label>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Il tuo username" className="input-dark w-full rounded-lg" data-testid="register-username" required />
          </div>
          <div>
            <label className="block text-[#D4AF37] mb-1 text-sm">Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" className="input-dark w-full rounded-lg" data-testid="register-email" required />
          </div>
          <div>
            <label className="block text-[#D4AF37] mb-1 text-sm">Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" className="input-dark w-full rounded-lg" data-testid="register-password" required />
          </div>
          
          {error && <p className="text-[#D00000] text-sm">{error}</p>}
          
          <button type="submit" disabled={loading} className="btn-gold w-full py-3 rounded-lg font-pirate" data-testid="register-submit">
            {loading ? 'Caricamento...' : 'Crea Account'}
          </button>
        </form>

        <p className="mt-4 text-center text-[#E3D5CA]/60">
          Hai già un account? <button onClick={() => navigate('/login')} className="text-[#FFC300] hover:underline">Accedi</button>
        </p>
      </motion.div>
    </div>
  );
};

// ============ LOGIN PAGE ============
const LoginPage = ({ login }) => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      console.log('Logging in...', email);
      const response = await axios.post(`${API}/auth/login`, { email, password });
      console.log('Login response:', response.data);
      
      if (response.data.token) {
        await login(response.data.token, response.data.user);
        navigate('/dashboard');
      } else {
        setError('Risposta server non valida');
        setLoading(false);
      }
    } catch (err) {
      console.error('Login error:', err);
      setError(err.response?.data?.detail || 'Errore durante il login');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#051923] flex items-center justify-center p-4">
      <motion.div className="glass p-8 rounded-xl w-full max-w-md" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}>
        <h1 className="font-pirate text-3xl text-[#FFC300] mb-6 text-center">Accedi</h1>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" className="input-dark w-full rounded-lg" data-testid="login-email" required />
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" className="input-dark w-full rounded-lg" data-testid="login-password" required />
          
          {error && <p className="text-[#D00000] text-sm">{error}</p>}
          
          <button type="submit" disabled={loading} className="btn-gold w-full py-3 rounded-lg font-pirate" data-testid="login-submit">
            {loading ? 'Caricamento...' : 'Accedi'}
          </button>
        </form>

        <p className="mt-4 text-center text-[#E3D5CA]/60">
          Non hai un account? <button onClick={() => navigate('/register')} className="text-[#FFC300] hover:underline">Registrati</button>
        </p>
      </motion.div>
    </div>
  );
};

// ============ CHARACTER CREATION (NEW SYSTEM) ============
const CharacterCreation = ({ token, setCharacter }) => {
  const navigate = useNavigate();
  const authToken = token || localStorage.getItem('token');
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [checkingExisting, setCheckingExisting] = useState(true);
  
  // Game data from backend
  const [races, setRaces] = useState({});
  const [fightingStyles, setFightingStyles] = useState({});
  const [mestieri, setMestieri] = useState({});
  
  // Character data
  const [charData, setCharData] = useState({
    nome_personaggio: '',
    ruolo: 'pirata',
    genere: '',
    eta: 16,
    razza: '',
    stile_combattimento: '',
    sogno: '',
    storia_carattere: '',
    mestiere: '',
    mare_partenza: 'east_blue',
    colore_capelli: '',
    colore_occhi: '',
    particolarita: ''
  });
  
  const [nameError, setNameError] = useState('');
  const [traits, setTraits] = useState([]);
  const [extractingTraits, setExtractingTraits] = useState(false);

  // Fetch game data and check existing character
  useEffect(() => {
    const init = async () => {
      if (!authToken) {
        navigate('/login');
        return;
      }
      
      try {
        // Check if character exists
        const charResponse = await axios.get(`${API}/characters/me`, { headers: { Authorization: `Bearer ${authToken}` } });
        if (charResponse.data?.character_id) {
          setCharacter(charResponse.data);
          navigate('/dashboard');
          return;
        }
      } catch (e) {}
      
      // Fetch game data
      try {
        const [racesRes, stylesRes, mestieriRes] = await Promise.all([
          axios.get(`${API}/game/races`, { headers: { Authorization: `Bearer ${authToken}` } }),
          axios.get(`${API}/game/fighting-styles`, { headers: { Authorization: `Bearer ${authToken}` } }),
          axios.get(`${API}/game/mestieri`, { headers: { Authorization: `Bearer ${authToken}` } })
        ]);
        setRaces(racesRes.data.races);
        setFightingStyles(stylesRes.data.styles);
        setMestieri(mestieriRes.data.mestieri);
      } catch (e) {
        console.error('Error fetching game data:', e);
      }
      
      setCheckingExisting(false);
    };
    init();
  }, [authToken, navigate, setCharacter]);

  // Validate character name
  const validateName = async (name) => {
    if (!name) return;
    try {
      const response = await axios.post(`${API}/characters/validate-name`, { nome: name }, { headers: { Authorization: `Bearer ${authToken}` } });
      if (!response.data.valid) {
        setNameError(response.data.message);
      } else {
        setNameError('');
      }
    } catch (e) {}
  };

  // Extract traits from story
  const extractTraits = async () => {
    if (!charData.storia_carattere || charData.storia_carattere.length < 20) {
      setError('Scrivi almeno 20 caratteri per la storia del personaggio');
      return;
    }
    
    setExtractingTraits(true);
    try {
      const response = await axios.post(`${API}/characters/extract-traits`, 
        { storia_carattere: charData.storia_carattere },
        { headers: { Authorization: `Bearer ${authToken}` } }
      );
      setTraits(response.data.traits);
    } catch (e) {
      setError('Errore nell\'estrazione dei tratti');
    }
    setExtractingTraits(false);
  };

  // Create character
  const handleCreate = async () => {
    if (traits.length < 3) {
      setError('Servono almeno 3 tratti caratteriali');
      return;
    }
    
    setLoading(true);
    setError('');
    try {
      const response = await axios.post(`${API}/characters`, charData, { headers: { Authorization: `Bearer ${authToken}` } });
      // Update traits
      await axios.put(`${API}/characters/me/traits`, { traits }, { headers: { Authorization: `Bearer ${authToken}` } });
      setCharacter(response.data);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Errore durante la creazione');
    }
    setLoading(false);
  };

  const totalSteps = 8;

  if (checkingExisting) return <LoadingScreen />;

  // Info Box Component
  const InfoBox = ({ title, advantages, disadvantages }) => (
    <div className="mt-3 p-3 bg-[#003566]/30 rounded-lg text-sm">
      <p className="font-bold text-[#FFC300] mb-2">{title}</p>
      {advantages && (
        <div className="mb-2">
          <span className="text-[#2A9D8F]">Vantaggi: </span>
          <span className="text-[#E3D5CA]/80">{advantages.join(', ')}</span>
        </div>
      )}
      {disadvantages && (
        <div>
          <span className="text-[#D00000]">Svantaggi: </span>
          <span className="text-[#E3D5CA]/80">{disadvantages.join(', ')}</span>
        </div>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-[#051923] p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="font-pirate text-4xl text-[#FFC300] mb-4 text-center">Crea il Tuo Personaggio</h1>
        
        {/* Progress */}
        <div className="flex justify-center gap-1 mb-8">
          {[...Array(totalSteps)].map((_, i) => (
            <div key={i} className={`w-8 h-2 rounded-full ${i + 1 === step ? 'bg-[#FFC300]' : i + 1 < step ? 'bg-[#2A9D8F]' : 'bg-[#3E2723]'}`} />
          ))}
        </div>

        <AnimatePresence mode="wait">
          {/* STEP 1: Nome Personaggio */}
          {step === 1 && (
            <motion.div key="step1" initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -50 }} className="glass p-8 rounded-xl">
              <h2 className="font-pirate text-2xl text-[#E3D5CA] mb-6">Nome del Personaggio</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-[#D4AF37] mb-2">Nome del tuo pirata</label>
                  <input
                    type="text"
                    value={charData.nome_personaggio}
                    onChange={(e) => {
                      setCharData({ ...charData, nome_personaggio: e.target.value });
                      validateName(e.target.value);
                    }}
                    placeholder="Es: Monkey Luffy (senza la D.!)"
                    className="input-dark w-full rounded-lg"
                    data-testid="char-name"
                  />
                  {nameError && (
                    <div className="mt-2 p-3 bg-[#D00000]/20 border border-[#D00000] rounded-lg flex items-start gap-2">
                      <AlertTriangle className="w-5 h-5 text-[#D00000] flex-shrink-0 mt-0.5" />
                      <p className="text-[#D00000] text-sm">{nameError}</p>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="flex justify-end mt-6">
                <button onClick={() => !nameError && charData.nome_personaggio && setStep(2)} disabled={!charData.nome_personaggio || nameError} className="btn-gold py-3 px-8 rounded-lg font-pirate disabled:opacity-50">
                  Continua <ChevronRight className="inline w-5 h-5" />
                </button>
              </div>
            </motion.div>
          )}

          {/* STEP 2: Genere & Età */}
          {step === 2 && (
            <motion.div key="step2" initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -50 }} className="glass p-8 rounded-xl">
              <h2 className="font-pirate text-2xl text-[#E3D5CA] mb-6">Genere ed Età</h2>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-[#D4AF37] mb-3">Genere</label>
                  <div className="grid grid-cols-3 gap-3">
                    {[
                      { id: 'maschio', label: 'Maschio' },
                      { id: 'femmina', label: 'Femmina' },
                      { id: 'non_definito', label: 'Non definito' }
                    ].map((g) => (
                      <button
                        key={g.id}
                        onClick={() => setCharData({ ...charData, genere: g.id })}
                        className={`p-4 rounded-lg border-2 transition-colors ${charData.genere === g.id ? 'border-[#FFC300] bg-[#FFC300]/10' : 'border-[#3E2723]'}`}
                      >
                        <span className="text-[#E3D5CA]">{g.label}</span>
                      </button>
                    ))}
                  </div>
                </div>
                
                <div>
                  <label className="block text-[#D4AF37] mb-2">Età (minimo 16 anni)</label>
                  <input
                    type="number"
                    min="16"
                    max="100"
                    value={charData.eta}
                    onChange={(e) => setCharData({ ...charData, eta: Math.max(16, parseInt(e.target.value) || 16) })}
                    className="input-dark w-32 rounded-lg"
                  />
                </div>
              </div>
              
              <div className="flex justify-between mt-6">
                <button onClick={() => setStep(1)} className="glass px-6 py-3 rounded-lg text-[#E3D5CA]">
                  <ChevronLeft className="inline w-5 h-5" /> Indietro
                </button>
                <button onClick={() => charData.genere && setStep(3)} disabled={!charData.genere} className="btn-gold py-3 px-8 rounded-lg font-pirate disabled:opacity-50">
                  Continua <ChevronRight className="inline w-5 h-5" />
                </button>
              </div>
            </motion.div>
          )}

          {/* STEP 3: Razza */}
          {step === 3 && (
            <motion.div key="step3" initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -50 }} className="glass p-8 rounded-xl">
              <h2 className="font-pirate text-2xl text-[#E3D5CA] mb-6">Scegli la Razza</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(races).map(([raceId, race]) => (
                  <button
                    key={raceId}
                    onClick={() => setCharData({ ...charData, razza: raceId })}
                    className={`p-4 rounded-lg border-2 text-left transition-colors ${charData.razza === raceId ? 'border-[#FFC300] bg-[#FFC300]/10' : 'border-[#3E2723]'}`}
                  >
                    <h3 className="font-bold text-[#E3D5CA] mb-1">{race.name}</h3>
                    <p className="text-sm text-[#E3D5CA]/60 mb-2">{race.description}</p>
                    <div className="flex gap-2 flex-wrap">
                      <span className="text-xs px-2 py-1 rounded bg-[#2A9D8F]/30 text-[#2A9D8F]">FOR: {race.bonus.forza}</span>
                      <span className="text-xs px-2 py-1 rounded bg-[#00A8E8]/30 text-[#00A8E8]">VEL: {race.bonus.velocita}</span>
                      <span className="text-xs px-2 py-1 rounded bg-[#D00000]/30 text-[#D00000]">RES: {race.bonus.resistenza}</span>
                      <span className="text-xs px-2 py-1 rounded bg-[#7209B7]/30 text-[#7209B7]">AGI: {race.bonus.agilita}</span>
                    </div>
                  </button>
                ))}
              </div>
              
              {charData.razza && races[charData.razza] && (
                <InfoBox 
                  title={races[charData.razza].name}
                  advantages={races[charData.razza].vantaggi}
                  disadvantages={races[charData.razza].svantaggi}
                />
              )}
              
              <div className="flex justify-between mt-6">
                <button onClick={() => setStep(2)} className="glass px-6 py-3 rounded-lg text-[#E3D5CA]">
                  <ChevronLeft className="inline w-5 h-5" /> Indietro
                </button>
                <button onClick={() => charData.razza && setStep(4)} disabled={!charData.razza} className="btn-gold py-3 px-8 rounded-lg font-pirate disabled:opacity-50">
                  Continua <ChevronRight className="inline w-5 h-5" />
                </button>
              </div>
            </motion.div>
          )}

          {/* STEP 4: Stile Combattimento */}
          {step === 4 && (
            <motion.div key="step4" initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -50 }} className="glass p-8 rounded-xl">
              <h2 className="font-pirate text-2xl text-[#E3D5CA] mb-6">Stile di Combattimento</h2>
              
              <div className="space-y-3">
                {Object.entries(fightingStyles).map(([styleId, style]) => (
                  <button
                    key={styleId}
                    onClick={() => setCharData({ ...charData, stile_combattimento: styleId })}
                    className={`w-full p-4 rounded-lg border-2 text-left transition-colors ${charData.stile_combattimento === styleId ? 'border-[#D00000] bg-[#D00000]/10' : 'border-[#3E2723]'}`}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-bold text-[#E3D5CA]">{style.name}</h3>
                        <p className="text-sm text-[#E3D5CA]/60">{style.description}</p>
                      </div>
                      <Swords className={`w-6 h-6 ${charData.stile_combattimento === styleId ? 'text-[#D00000]' : 'text-[#D4AF37]'}`} />
                    </div>
                  </button>
                ))}
              </div>
              
              {charData.stile_combattimento && fightingStyles[charData.stile_combattimento] && (
                <InfoBox 
                  title={fightingStyles[charData.stile_combattimento].name}
                  advantages={fightingStyles[charData.stile_combattimento].vantaggi}
                  disadvantages={fightingStyles[charData.stile_combattimento].svantaggi}
                />
              )}
              
              <div className="flex justify-between mt-6">
                <button onClick={() => setStep(3)} className="glass px-6 py-3 rounded-lg text-[#E3D5CA]">
                  <ChevronLeft className="inline w-5 h-5" /> Indietro
                </button>
                <button onClick={() => charData.stile_combattimento && setStep(5)} disabled={!charData.stile_combattimento} className="btn-gold py-3 px-8 rounded-lg font-pirate disabled:opacity-50">
                  Continua <ChevronRight className="inline w-5 h-5" />
                </button>
              </div>
            </motion.div>
          )}

          {/* STEP 5: Mestiere */}
          {step === 5 && (
            <motion.div key="step5" initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -50 }} className="glass p-8 rounded-xl">
              <h2 className="font-pirate text-2xl text-[#E3D5CA] mb-6">Scegli il tuo Mestiere</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-[60vh] overflow-y-auto">
                {Object.entries(mestieri).map(([mestiereId, mestiere]) => (
                  <button
                    key={mestiereId}
                    onClick={() => setCharData({ ...charData, mestiere: mestiereId })}
                    className={`p-4 rounded-lg border-2 text-left transition-colors ${charData.mestiere === mestiereId ? 'border-[#FFC300] bg-[#FFC300]/10' : 'border-[#3E2723]'}`}
                  >
                    <h3 className="font-bold text-[#E3D5CA] flex items-center gap-2">
                      <Briefcase className="w-4 h-4 text-[#D4AF37]" />
                      {mestiere.name}
                    </h3>
                    <p className="text-xs text-[#E3D5CA]/60 mt-1">{mestiere.description}</p>
                  </button>
                ))}
              </div>
              
              <p className="text-xs text-[#E3D5CA]/50 mt-4">
                <Info className="w-4 h-4 inline mr-1" />
                Inizierai come Principiante. Il livello aumenta con l'esperienza.
              </p>
              
              <div className="flex justify-between mt-6">
                <button onClick={() => setStep(4)} className="glass px-6 py-3 rounded-lg text-[#E3D5CA]">
                  <ChevronLeft className="inline w-5 h-5" /> Indietro
                </button>
                <button onClick={() => charData.mestiere && setStep(6)} disabled={!charData.mestiere} className="btn-gold py-3 px-8 rounded-lg font-pirate disabled:opacity-50">
                  Continua <ChevronRight className="inline w-5 h-5" />
                </button>
              </div>
            </motion.div>
          )}

          {/* STEP 6: Sogno & Storia */}
          {step === 6 && (
            <motion.div key="step6" initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -50 }} className="glass p-8 rounded-xl">
              <h2 className="font-pirate text-2xl text-[#E3D5CA] mb-6">Sogno e Carattere</h2>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-[#D4AF37] mb-2">Il tuo Sogno (max 100 caratteri)</label>
                  <input
                    type="text"
                    maxLength={100}
                    value={charData.sogno}
                    onChange={(e) => setCharData({ ...charData, sogno: e.target.value })}
                    placeholder="Es: Diventare il Re dei Pirati!"
                    className="input-dark w-full rounded-lg"
                  />
                  <p className="text-xs text-[#E3D5CA]/50 mt-1">{charData.sogno.length}/100</p>
                </div>
                
                <div>
                  <label className="block text-[#D4AF37] mb-2">Storia e Carattere (max 1000 caratteri)</label>
                  <textarea
                    maxLength={1000}
                    rows={6}
                    value={charData.storia_carattere}
                    onChange={(e) => setCharData({ ...charData, storia_carattere: e.target.value })}
                    placeholder="Descrivi la storia del tuo personaggio, il suo carattere, le sue peculiarità. L'AI analizzerà questa descrizione per estrarre i tratti caratteriali che influenzeranno il gameplay..."
                    className="input-dark w-full rounded-lg resize-none"
                  />
                  <p className="text-xs text-[#E3D5CA]/50 mt-1">{charData.storia_carattere.length}/1000</p>
                </div>
                
                <button
                  onClick={extractTraits}
                  disabled={extractingTraits || charData.storia_carattere.length < 20}
                  className="w-full py-3 rounded-lg bg-[#7209B7] text-white font-bold disabled:opacity-50"
                >
                  {extractingTraits ? 'Analizzando...' : 'Analizza Carattere (AI)'}
                </button>
                
                {traits.length > 0 && (
                  <div className="p-4 bg-[#7209B7]/20 rounded-lg">
                    <h4 className="text-[#FFC300] font-bold mb-2">Tratti Estratti:</h4>
                    <div className="flex flex-wrap gap-2">
                      {traits.map((trait, i) => (
                        <span key={i} className="px-3 py-1 bg-[#7209B7]/40 rounded-full text-[#E3D5CA] text-sm">
                          {trait}
                          <button onClick={() => setTraits(traits.filter((_, idx) => idx !== i))} className="ml-2 text-[#D00000]">×</button>
                        </span>
                      ))}
                    </div>
                    {traits.length < 3 && <p className="text-[#D00000] text-sm mt-2">Servono almeno 3 tratti!</p>}
                  </div>
                )}
              </div>
              
              <div className="flex justify-between mt-6">
                <button onClick={() => setStep(5)} className="glass px-6 py-3 rounded-lg text-[#E3D5CA]">
                  <ChevronLeft className="inline w-5 h-5" /> Indietro
                </button>
                <button onClick={() => traits.length >= 3 && setStep(7)} disabled={traits.length < 3} className="btn-gold py-3 px-8 rounded-lg font-pirate disabled:opacity-50">
                  Continua <ChevronRight className="inline w-5 h-5" />
                </button>
              </div>
            </motion.div>
          )}

          {/* STEP 7: Aspetto (Opzionale) */}
          {step === 7 && (
            <motion.div key="step7" initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -50 }} className="glass p-8 rounded-xl">
              <h2 className="font-pirate text-2xl text-[#E3D5CA] mb-6">Aspetto Fisico (Opzionale)</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div>
                  <label className="block text-[#D4AF37] mb-2">Colore Capelli</label>
                  <input type="text" value={charData.colore_capelli} onChange={(e) => setCharData({ ...charData, colore_capelli: e.target.value })} placeholder="Es: Nero" className="input-dark w-full rounded-lg" />
                </div>
                <div>
                  <label className="block text-[#D4AF37] mb-2">Colore Occhi</label>
                  <input type="text" value={charData.colore_occhi} onChange={(e) => setCharData({ ...charData, colore_occhi: e.target.value })} placeholder="Es: Marroni" className="input-dark w-full rounded-lg" />
                </div>
                <div>
                  <label className="block text-[#D4AF37] mb-2">Particolarità</label>
                  <input type="text" value={charData.particolarita} onChange={(e) => setCharData({ ...charData, particolarita: e.target.value })} placeholder="Es: Cicatrice sotto l'occhio" className="input-dark w-full rounded-lg" />
                </div>
              </div>
              
              <div className="flex justify-between">
                <button onClick={() => setStep(6)} className="glass px-6 py-3 rounded-lg text-[#E3D5CA]">
                  <ChevronLeft className="inline w-5 h-5" /> Indietro
                </button>
                <button onClick={() => setStep(8)} className="btn-gold py-3 px-8 rounded-lg font-pirate">
                  Continua <ChevronRight className="inline w-5 h-5" />
                </button>
              </div>
            </motion.div>
          )}

          {/* STEP 8: Scelta Mare & Conferma */}
          {step === 8 && (
            <motion.div key="step8" initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -50 }} className="glass p-8 rounded-xl">
              <h2 className="font-pirate text-2xl text-[#E3D5CA] mb-2">Scegli il Tuo Mare</h2>
              <p className="text-[#E3D5CA]/60 mb-6">Da quale dei quattro mari vuoi iniziare la tua avventura?</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                {[
                  { 
                    id: 'east_blue', 
                    name: 'East Blue', 
                    color: '#3B82F6',
                    icon: '🌅',
                    description: 'Il mare più debole dei quattro, ma patria di grandi pirati come Gol D. Roger e Monkey D. Luffy.',
                    start: 'Dawn Island (Foosha Village)'
                  },
                  { 
                    id: 'west_blue', 
                    name: 'West Blue', 
                    color: '#10B981',
                    icon: '🌿',
                    description: 'Mare occidentale, patria degli studiosi di Ohara e del potente regno di Kano.',
                    start: 'Ohara'
                  },
                  { 
                    id: 'north_blue', 
                    name: 'North Blue', 
                    color: '#8B5CF6',
                    icon: '❄️',
                    description: 'Mare settentrionale, freddo e misterioso. Patria del Supernova Trafalgar Law.',
                    start: 'Downs'
                  },
                  { 
                    id: 'south_blue', 
                    name: 'South Blue', 
                    color: '#F59E0B',
                    icon: '☀️',
                    description: 'Mare meridionale, noto per le arti marziali e come luogo di nascita di Portgas D. Ace.',
                    start: 'Baterilla'
                  }
                ].map((sea) => (
                  <motion.button
                    key={sea.id}
                    onClick={() => setCharData({ ...charData, mare_partenza: sea.id })}
                    className={`p-4 rounded-xl text-left transition-all ${
                      charData.mare_partenza === sea.id 
                        ? `border-2 bg-opacity-20` 
                        : 'glass border-2 border-transparent'
                    }`}
                    style={{ 
                      borderColor: charData.mare_partenza === sea.id ? sea.color : 'transparent',
                      backgroundColor: charData.mare_partenza === sea.id ? `${sea.color}20` : undefined
                    }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-3xl">{sea.icon}</span>
                      <div className="flex-1">
                        <h3 className="font-pirate text-xl" style={{ color: sea.color }}>{sea.name}</h3>
                        <p className="text-[#E3D5CA]/70 text-sm mt-1">{sea.description}</p>
                        <p className="text-[#D4AF37] text-xs mt-2">🏝️ Inizio: {sea.start}</p>
                      </div>
                    </div>
                  </motion.button>
                ))}
              </div>
              
              {/* Summary */}
              <div className="p-4 bg-[#003566]/30 rounded-lg mb-6">
                <h3 className="font-pirate text-xl text-[#FFC300] mb-3">Riepilogo Personaggio</h3>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <p><span className="text-[#D4AF37]">Nome:</span> {charData.nome_personaggio}</p>
                  <p><span className="text-[#D4AF37]">Genere:</span> {charData.genere}</p>
                  <p><span className="text-[#D4AF37]">Età:</span> {charData.eta}</p>
                  <p><span className="text-[#D4AF37]">Razza:</span> {races[charData.razza]?.name}</p>
                  <p><span className="text-[#D4AF37]">Stile:</span> {fightingStyles[charData.stile_combattimento]?.name}</p>
                  <p><span className="text-[#D4AF37]">Mestiere:</span> {mestieri[charData.mestiere]?.name}</p>
                  <p><span className="text-[#D4AF37]">Mare:</span> {charData.mare_partenza === 'east_blue' ? 'East Blue' : charData.mare_partenza === 'west_blue' ? 'West Blue' : charData.mare_partenza === 'north_blue' ? 'North Blue' : 'South Blue'}</p>
                </div>
                <p className="mt-2"><span className="text-[#D4AF37]">Sogno:</span> {charData.sogno}</p>
                <p className="mt-2"><span className="text-[#D4AF37]">Tratti:</span> {traits.join(', ')}</p>
              </div>
              
              {error && <p className="text-[#D00000] text-sm mb-4">{error}</p>}
              
              <div className="flex justify-between">
                <button onClick={() => setStep(7)} className="glass px-6 py-3 rounded-lg text-[#E3D5CA]">
                  <ChevronLeft className="inline w-5 h-5" /> Indietro
                </button>
                <button onClick={handleCreate} disabled={loading} className="btn-gold py-3 px-8 rounded-lg font-pirate disabled:opacity-50" data-testid="create-character-btn">
                  {loading ? 'Creazione...' : '⚓ Salpa!'}
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

// ============ DASHBOARD ============
const Dashboard = ({ user, character, token, logout, isDemo }) => {
  const navigate = useNavigate();
  const [narrativeExpanded, setNarrativeExpanded] = useState(false);

  useEffect(() => {
    if (!isDemo && !user) navigate('/login');
    else if (!isDemo && !character) navigate('/create-character');
  }, [user, character, navigate, isDemo]);

  if (!isDemo && (!user || !character)) return <LoadingScreen />;

  const menuItems = [
    { icon: Map, label: 'Mappa', path: '/world-map', color: '#00A8E8' },
    { icon: Compass, label: 'Esplora', path: '/explore', color: '#2A9D8F' },
    { icon: Swords, label: 'Arena', path: '/battle', color: '#D00000' },
    { icon: Backpack, label: 'Inventario', path: '/inventory', color: '#7209B7' },
    { icon: UserCircle, label: 'Personaggio', path: '/character', color: '#FFC300' },
    { icon: ShoppingBag, label: 'Negozio', path: '/shop', color: '#D4AF37' },
  ];

  return (
    <div className="min-h-screen bg-[#051923] pb-16">
      {/* Demo Banner */}
      {isDemo && (
        <div className="bg-[#2A9D8F] p-2 text-center">
          <p className="text-white text-sm font-medium">
            🎮 <strong>Modalità Demo</strong> - Stai visualizzando una preview. Le modifiche non vengono salvate.
            <button onClick={logout} className="ml-4 underline hover:no-underline">Esci dalla demo</button>
          </p>
        </div>
      )}

      <div className="p-4 md:p-8">
        <div className="flex justify-between items-start mb-8">
          <div>
            <h1 className="font-pirate text-3xl text-[#FFC300]">{character.nome_personaggio}</h1>
            <p className="text-[#E3D5CA]/70">{character.ruolo} • Lv.{character.livello} • {mestieri[character.mestiere]?.name || character.mestiere}</p>
          </div>
          <button onClick={logout} className="glass p-3 rounded-lg text-[#E3D5CA] hover:text-[#D00000]" data-testid="logout-btn">
            <LogOut className="w-6 h-6" />
          </button>
        </div>

        {/* Stats */}
        <div className="glass p-4 rounded-xl mb-6">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Heart className="w-4 h-4 text-[#D00000]" />
                <span className="text-sm text-[#E3D5CA]/70">Vita</span>
              </div>
              <div className="hp-bar">
                <div className="hp-bar-fill bg-[#D00000]" style={{ width: `${(character.vita / character.vita_max) * 100}%` }} />
              </div>
              <span className="text-xs text-[#E3D5CA]">{character.vita}/{character.vita_max}</span>
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Zap className="w-4 h-4 text-[#00A8E8]" />
                <span className="text-sm text-[#E3D5CA]/70">Energia</span>
              </div>
              <div className="hp-bar">
                <div className="hp-bar-fill bg-[#00A8E8]" style={{ width: `${(character.energia / character.energia_max) * 100}%` }} />
              </div>
              <span className="text-xs text-[#E3D5CA]">{character.energia}/{character.energia_max}</span>
            </div>
            <div className="text-center">
              <p className="text-xs text-[#E3D5CA]/70">Berry</p>
              <p className="font-pirate text-xl text-[#D4AF37]">฿ {(character.berry || 0).toLocaleString()}</p>
            </div>
            <div className="text-center">
              <p className="text-xs text-[#E3D5CA]/70">Taglia</p>
              <p className="font-pirate text-xl text-[#FFC300]">{(character.taglia || 0).toLocaleString()} B</p>
            </div>
            <div className="text-center">
              <p className="text-xs text-[#E3D5CA]/70">ATK / DEF</p>
              <p className="text-[#E3D5CA]">{character.attacco} / {character.difesa}</p>
            </div>
          </div>
        </div>

        {/* Menu */}
        <div className="grid grid-cols-2 gap-4 mb-20">
          {menuItems.map((item) => (
            <motion.button key={item.path} onClick={() => navigate(item.path)} className="glass p-6 rounded-xl text-left" whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <item.icon className="w-10 h-10 mb-3" style={{ color: item.color }} />
              <h3 className="font-pirate text-xl text-[#E3D5CA]">{item.label}</h3>
            </motion.button>
          ))}
        </div>
      </div>

      {/* Narrative Panel */}
      <NarrativePanel 
        token={token} 
        character={character} 
        isDemo={isDemo}
        isExpanded={narrativeExpanded}
        setIsExpanded={setNarrativeExpanded}
      />
    </div>
  );
};

// Mestieri constant for dashboard display
const mestieri = {
  capitano: { name: "Capitano" },
  guerriero: { name: "Guerriero" },
  navigatore: { name: "Navigatore" },
  cecchino: { name: "Cecchino" },
  cuoco: { name: "Cuoco" },
  medico: { name: "Medico" },
  archeologo: { name: "Archeologo" },
  carpentiere: { name: "Carpentiere" },
  musicista: { name: "Musicista" },
  timoniere: { name: "Timoniere" },
  scienziato: { name: "Scienziato" },
  ipnotista: { name: "Ipnotista" }
};

// ============ CHARACTER SHEET ============
const CharacterSheet = ({ token, character, setCharacter, isDemo }) => {
  const navigate = useNavigate();
  const authToken = token || localStorage.getItem('token');
  const [showPrivate, setShowPrivate] = useState(true);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showAbilityDistribute, setShowAbilityDistribute] = useState(false);
  const [abilityDistribution, setAbilityDistribution] = useState({ forza: 0, velocita: 0, resistenza: 0, agilita: 0 });
  const [distributing, setDistributing] = useState(false);

  const availablePoints = character?.punti_abilita_disponibili || 0;
  const totalToDistribute = Object.values(abilityDistribution).reduce((a, b) => a + b, 0);

  const handleDistribute = async () => {
    if (isDemo || distributing || totalToDistribute === 0) return;
    setDistributing(true);
    try {
      const res = await axios.post(`${API}/ability-points/distribute`, abilityDistribution, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      // Update character locally
      if (setCharacter) {
        setCharacter(prev => ({
          ...prev,
          forza: res.data.nuove_abilita.forza,
          velocita: res.data.nuove_abilita.velocita,
          resistenza: res.data.nuove_abilita.resistenza,
          agilita: res.data.nuove_abilita.agilita,
          attacco: res.data.nuovi_stats.attacco,
          difesa: res.data.nuovi_stats.difesa,
          punti_abilita_disponibili: res.data.punti_rimanenti
        }));
      }
      setAbilityDistribution({ forza: 0, velocita: 0, resistenza: 0, agilita: 0 });
      setShowAbilityDistribute(false);
    } catch (e) {
      console.error('Error distributing points:', e);
    }
    setDistributing(false);
  };

  const handleDelete = async () => {
    try {
      await axios.delete(`${API}/characters/me`, { headers: { Authorization: `Bearer ${authToken}` } });
      localStorage.removeItem('token');
      window.location.href = '/';
    } catch (e) {}
  };

  if (!character) return <LoadingScreen />;

  const expPercent = character.esperienza_prossimo_livello > 0 
    ? (character.esperienza_livello / character.esperienza_prossimo_livello) * 100 
    : 0;

  return (
    <div className="min-h-screen bg-[#051923] p-4 pb-20">
      <div className="glass p-4 flex justify-between items-center mb-6">
        <button onClick={() => navigate('/dashboard')} className="text-[#E3D5CA] hover:text-[#FFC300]">
          <Home className="w-6 h-6" />
        </button>
        <h1 className="font-pirate text-2xl text-[#FFC300]">Scheda Personaggio</h1>
        <button onClick={() => setShowPrivate(!showPrivate)} className="text-[#E3D5CA]">
          {showPrivate ? <EyeOff className="w-6 h-6" /> : <Eye className="w-6 h-6" />}
        </button>
      </div>

      <div className="max-w-2xl mx-auto space-y-4">
        {/* Basic Info (PUBLIC) */}
        <div className="glass p-6 rounded-xl">
          <h2 className="font-pirate text-2xl text-[#FFC300] mb-4">{character.nome_personaggio}</h2>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <p><span className="text-[#D4AF37]">Ruolo:</span> {character.ruolo}</p>
            <p><span className="text-[#D4AF37]">Livello:</span> {character.livello}</p>
            <p><span className="text-[#D4AF37]">EXP:</span> {character.esperienza}</p>
            <p><span className="text-[#D4AF37]">Genere:</span> {character.genere}</p>
            <p><span className="text-[#D4AF37]">Razza:</span> {character.razza}</p>
            <p><span className="text-[#D4AF37]">Mestiere:</span> {mestieri[character.mestiere]?.name} ({character.mestiere_livello})</p>
            <p><span className="text-[#D4AF37]">Stile:</span> {character.stile_combattimento}</p>
            <p><span className="text-[#D4AF37]">Taglia:</span> {(character.taglia || 0).toLocaleString()} Berry</p>
            <p><span className="text-[#D4AF37]">Berry:</span> ฿{(character.berry || 0).toLocaleString()}</p>
          </div>
          {character.sogno && <p className="mt-3"><span className="text-[#D4AF37]">Sogno:</span> {character.sogno}</p>}
        </div>

        {/* COMBAT LEVEL & EXP BAR (NEW!) */}
        <div className="glass p-6 rounded-xl border-2 border-[#7209B7]/50">
          <h3 className="font-pirate text-xl text-[#7209B7] mb-4 flex items-center gap-2">
            ⚔️ Livello Combattimento
          </h3>
          <div className="flex items-center justify-between mb-3">
            <span className="text-3xl font-bold text-[#FFC300]">Lv. {character.livello_combattimento || 1}</span>
            <span className="text-sm text-[#E3D5CA]/70">
              Moltiplicatore EXP: x{Math.max(1, Math.floor((character.livello_combattimento || 1) / 4) + 1)}
            </span>
          </div>
          
          {/* EXP Progress Bar */}
          <div className="mb-2">
            <div className="flex justify-between text-xs text-[#E3D5CA]/70 mb-1">
              <span>EXP Livello</span>
              <span>{character.esperienza_livello || 0} / {character.esperienza_prossimo_livello || 100}</span>
            </div>
            <div className="h-4 bg-[#051923] rounded-full overflow-hidden border border-[#7209B7]/30">
              <motion.div 
                className="h-full bg-gradient-to-r from-[#7209B7] to-[#B5179E]"
                initial={{ width: 0 }}
                animate={{ width: `${expPercent}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>
          
          {/* Total EXP */}
          <div className="text-center mt-3">
            <span className="text-xs text-[#E3D5CA]/50">EXP Totale: </span>
            <span className="text-sm text-[#D4AF37] font-bold">{(character.esperienza_totale || 0).toLocaleString()}</span>
          </div>
        </div>

        {/* ABILITY POINTS (NEW!) */}
        <div className="glass p-6 rounded-xl border-2 border-[#2A9D8F]/50">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-pirate text-xl text-[#2A9D8F] flex items-center gap-2">
              💪 Punti Abilità
            </h3>
            {availablePoints > 0 && (
              <motion.button
                onClick={() => setShowAbilityDistribute(!showAbilityDistribute)}
                className="px-4 py-2 bg-[#2A9D8F] text-white rounded-lg font-bold text-sm"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                animate={{ boxShadow: ['0 0 0 0 rgba(42, 157, 143, 0.4)', '0 0 0 10px rgba(42, 157, 143, 0)', '0 0 0 0 rgba(42, 157, 143, 0.4)'] }}
                transition={{ repeat: Infinity, duration: 1.5 }}
              >
                Distribuisci ({availablePoints})
              </motion.button>
            )}
          </div>

          <div className="flex items-center justify-center gap-4 mb-4">
            <div className="text-center">
              <p className="text-xs text-[#E3D5CA]/70">Disponibili</p>
              <p className="text-2xl font-bold text-[#2A9D8F]">{availablePoints}</p>
            </div>
            <div className="text-center">
              <p className="text-xs text-[#E3D5CA]/70">Totali Guadagnati</p>
              <p className="text-xl text-[#D4AF37]">{character.punti_abilita_totali || 0}</p>
            </div>
          </div>

          {/* Distribution Panel */}
          <AnimatePresence>
            {showAbilityDistribute && availablePoints > 0 && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="overflow-hidden"
              >
                <div className="border-t border-[#2A9D8F]/30 pt-4 mt-4">
                  <p className="text-sm text-[#E3D5CA]/70 mb-3">
                    Punti da distribuire: <span className="text-[#2A9D8F] font-bold">{availablePoints - totalToDistribute}</span>
                  </p>
                  
                  <div className="grid grid-cols-2 gap-4">
                    {[
                      { key: 'forza', label: 'Forza', icon: '💪', current: character.forza },
                      { key: 'velocita', label: 'Velocità', icon: '⚡', current: character.velocita },
                      { key: 'resistenza', label: 'Resistenza', icon: '🛡️', current: character.resistenza },
                      { key: 'agilita', label: 'Agilità', icon: '🏃', current: character.agilita }
                    ].map(stat => (
                      <div key={stat.key} className="bg-[#051923]/50 p-3 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm">{stat.icon} {stat.label}</span>
                          <span className="text-[#D4AF37]">{stat.current} {abilityDistribution[stat.key] > 0 && <span className="text-[#2A9D8F]">+{abilityDistribution[stat.key]}</span>}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => setAbilityDistribution(prev => ({ ...prev, [stat.key]: Math.max(0, prev[stat.key] - 1) }))}
                            disabled={abilityDistribution[stat.key] === 0}
                            className="w-8 h-8 bg-[#D00000]/30 rounded text-[#D00000] disabled:opacity-30"
                          >-</button>
                          <span className="flex-1 text-center font-bold">{abilityDistribution[stat.key]}</span>
                          <button
                            onClick={() => setAbilityDistribution(prev => ({ ...prev, [stat.key]: prev[stat.key] + 1 }))}
                            disabled={totalToDistribute >= availablePoints}
                            className="w-8 h-8 bg-[#2A9D8F]/30 rounded text-[#2A9D8F] disabled:opacity-30"
                          >+</button>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Preview */}
                  {totalToDistribute > 0 && (
                    <div className="mt-4 p-3 bg-[#051923]/50 rounded-lg">
                      <p className="text-xs text-[#E3D5CA]/70 mb-2">Anteprima dopo distribuzione:</p>
                      <div className="flex justify-around text-sm">
                        <div>
                          <span className="text-[#D00000]">ATK</span>
                          <span className="mx-1">{character.attacco}</span>
                          <span className="text-[#2A9D8F]">→ {character.forza + abilityDistribution.forza + character.velocita + abilityDistribution.velocita}</span>
                        </div>
                        <div>
                          <span className="text-[#00A8E8]">DEF</span>
                          <span className="mx-1">{character.difesa}</span>
                          <span className="text-[#2A9D8F]">→ {character.resistenza + abilityDistribution.resistenza + character.agilita + abilityDistribution.agilita}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="flex gap-3 mt-4">
                    <button
                      onClick={handleDistribute}
                      disabled={isDemo || distributing || totalToDistribute === 0}
                      className="flex-1 py-2 bg-[#2A9D8F] text-white rounded-lg font-bold disabled:opacity-50"
                    >
                      {distributing ? 'Applicando...' : `Conferma (+${totalToDistribute} punti)`}
                    </button>
                    <button
                      onClick={() => {
                        setAbilityDistribution({ forza: 0, velocita: 0, resistenza: 0, agilita: 0 });
                        setShowAbilityDistribute(false);
                      }}
                      className="px-4 py-2 glass rounded-lg text-[#E3D5CA]"
                    >
                      Annulla
                    </button>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Combat Stats (PUBLIC) */}
        <div className="glass p-6 rounded-xl">
          <h3 className="font-pirate text-xl text-[#D00000] mb-4">Statistiche Combattimento</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-[#D4AF37] text-sm">Vita</p>
              <div className="hp-bar"><div className="hp-bar-fill bg-[#D00000]" style={{ width: `${(character.vita / character.vita_max) * 100}%` }} /></div>
              <p className="text-xs text-[#E3D5CA]">{character.vita}/{character.vita_max}</p>
            </div>
            <div>
              <p className="text-[#D4AF37] text-sm">Energia</p>
              <div className="hp-bar"><div className="hp-bar-fill bg-[#00A8E8]" style={{ width: `${(character.energia / character.energia_max) * 100}%` }} /></div>
              <p className="text-xs text-[#E3D5CA]">{character.energia}/{character.energia_max}</p>
            </div>
          </div>
          
          {/* Stats with formula explanation */}
          <div className="mt-4 space-y-3">
            <div className="flex items-center justify-between p-2 bg-[#D00000]/10 rounded-lg">
              <div className="flex items-center gap-2">
                <Swords className="w-5 h-5 text-[#D00000]" />
                <span className="text-[#D00000] font-bold">ATTACCO</span>
              </div>
              <div className="text-right">
                <span className="text-xl font-bold text-[#E3D5CA]">{character.attacco}</span>
                <p className="text-xs text-[#E3D5CA]/50">= Forza ({character.forza}) + Velocità ({character.velocita})</p>
              </div>
            </div>
            
            <div className="flex items-center justify-between p-2 bg-[#00A8E8]/10 rounded-lg">
              <div className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-[#00A8E8]" />
                <span className="text-[#00A8E8] font-bold">DIFESA</span>
              </div>
              <div className="text-right">
                <span className="text-xl font-bold text-[#E3D5CA]">{character.difesa}</span>
                <p className="text-xs text-[#E3D5CA]/50">= Resistenza ({character.resistenza}) + Agilità ({character.agilita})</p>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-4 gap-2 mt-4 text-center">
            <div className="p-2 bg-[#051923]/50 rounded"><p className="text-xs text-[#D4AF37]">FOR</p><p className="text-[#E3D5CA] font-bold">{character.forza}</p></div>
            <div className="p-2 bg-[#051923]/50 rounded"><p className="text-xs text-[#D4AF37]">VEL</p><p className="text-[#E3D5CA] font-bold">{character.velocita}</p></div>
            <div className="p-2 bg-[#051923]/50 rounded"><p className="text-xs text-[#D4AF37]">RES</p><p className="text-[#E3D5CA] font-bold">{character.resistenza}</p></div>
            <div className="p-2 bg-[#051923]/50 rounded"><p className="text-xs text-[#D4AF37]">AGI</p><p className="text-[#E3D5CA] font-bold">{character.agilita}</p></div>
          </div>
          
          <div className="mt-4 text-center">
            <p className="text-xs text-[#D4AF37]">Aspettativa Vita</p>
            <p className="text-[#E3D5CA]">{character.aspettativa_vita}/{character.aspettativa_vita_max}</p>
          </div>
        </div>

        {/* Traits (PUBLIC) */}
        {character.tratti_carattere?.length > 0 && (
          <div className="glass p-6 rounded-xl">
            <h3 className="font-pirate text-xl text-[#7209B7] mb-3">Carattere</h3>
            <div className="flex flex-wrap gap-2">
              {character.tratti_carattere.map((t, i) => (
                <span key={i} className="px-3 py-1 bg-[#7209B7]/30 rounded-full text-sm text-[#E3D5CA]">{t}</span>
              ))}
            </div>
          </div>
        )}

        {/* PRIVATE SECTION */}
        {showPrivate && (
          <>
            <div className="glass p-6 rounded-xl border border-[#FFC300]/30">
              <h3 className="font-pirate text-xl text-[#FFC300] mb-3 flex items-center gap-2">
                <EyeOff className="w-5 h-5" /> Info Private
              </h3>
              <div className="text-sm space-y-2">
                <p><span className="text-[#D4AF37]">Abilità Base Raw:</span> FOR {character.abilita_base?.forza_raw}, VEL {character.abilita_base?.velocita_raw}, RES {character.abilita_base?.resistenza_raw}, AGI {character.abilita_base?.agilita_raw}</p>
                <p><span className="text-[#D4AF37]">Armi Speciali:</span> {character.armi_speciali?.length || 0}</p>
                <p><span className="text-[#D4AF37]">Poteri Segreti:</span> {character.poteri_segreti?.length || 0}</p>
                <p><span className="text-[#D4AF37]">Missioni Attive:</span> {character.missioni_attive?.length || 0}</p>
              </div>
            </div>

            <div className="glass p-6 rounded-xl border border-[#D00000]/30">
              <h3 className="font-pirate text-xl text-[#D00000] mb-3">Zona Pericolosa</h3>
              {!showDeleteConfirm ? (
                <button onClick={() => setShowDeleteConfirm(true)} className="bg-[#D00000]/20 text-[#D00000] py-2 px-4 rounded-lg border border-[#D00000]">
                  Elimina Personaggio
                </button>
              ) : (
                <div className="space-y-3">
                  <p className="text-[#E3D5CA]/80">Sei sicuro? Questa azione è irreversibile!</p>
                  <div className="flex gap-3">
                    <button onClick={handleDelete} className="bg-[#D00000] text-white py-2 px-4 rounded-lg">Sì, elimina</button>
                    <button onClick={() => setShowDeleteConfirm(false)} className="glass py-2 px-4 rounded-lg text-[#E3D5CA]">Annulla</button>
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

// ============ EXPLORE ISLAND ============
const ExploreIsland = ({ token, character, isDemo }) => {
  const navigate = useNavigate();
  const authToken = token || localStorage.getItem('token');
  const [islandInfo, setIslandInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedZone, setSelectedZone] = useState(null);
  const [eventResult, setEventResult] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [stats, setStats] = useState({ vita: 0, vita_max: 0, energia: 0, energia_max: 0, berry: 0 });

  // Demo data
  const demoIslandInfo = {
    island_id: "dawn_island",
    island: {
      name: "Dawn Island",
      storia: "L'isola dove tutto ha avuto inizio. Patria di Monkey D. Luffy, Portgas D. Ace e Sabo.",
      pericolo: 2,
      zone: [
        { id: "foosha", name: "Foosha Village", descrizione: "Tranquillo villaggio di pescatori dove Luffy è cresciuto." },
        { id: "mt_colubo", name: "Mt. Colubo", descrizione: "Montagna selvaggia dove vivono i banditi di montagna." },
        { id: "gray_terminal", name: "Gray Terminal", descrizione: "Enorme discarica ai confini del regno." },
        { id: "midway_forest", name: "Midway Forest", descrizione: "Foresta dove Ace, Sabo e Luffy costruirono la loro base." },
        { id: "goa_kingdom", name: "Goa Kingdom", descrizione: "Il regno più ricco dell'East Blue." }
      ]
    },
    visited_zones: ["foosha"],
    character_stats: { vita: 120, vita_max: 120, energia: 100, energia_max: 100, berry: 5000 }
  };

  const fetchIslandInfo = async () => {
    if (isDemo) {
      setIslandInfo(demoIslandInfo);
      setStats(demoIslandInfo.character_stats);
      setLoading(false);
      return;
    }
    try {
      const res = await axios.get(`${API}/exploration/current-island`, { headers: { Authorization: `Bearer ${authToken}` } });
      setIslandInfo(res.data);
      setStats(res.data.character_stats);
    } catch (e) {
      console.error('Error fetching island info:', e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchIslandInfo();
  }, [authToken, isDemo]);

  const visitZone = async (zoneId) => {
    if (isDemo) {
      setSelectedZone(islandInfo.island.zone.find(z => z.id === zoneId));
      return;
    }
    setProcessing(true);
    try {
      const res = await axios.post(`${API}/exploration/visit-zone`, { zone_id: zoneId }, { headers: { Authorization: `Bearer ${authToken}` } });
      setSelectedZone(res.data.zone);
      fetchIslandInfo(); // Refresh to update visited zones
    } catch (e) {
      console.error('Error visiting zone:', e);
    }
    setProcessing(false);
  };

  const triggerEvent = async () => {
    if (isDemo) {
      // Demo random event
      const demoEvents = [
        { event: { categoria: "scoperta", tipo: "tesoro", nome: "Forziere abbandonato", descrizione: "Trovi un vecchio forziere nascosto!" }, effects_applied: ["+100 Berry"] },
        { event: { categoria: "sociale", tipo: "npc", nome: "Anziano del villaggio", descrizione: "Un anziano ti racconta storie del passato." }, effects_applied: ["+25 EXP"] },
        { event: { categoria: "riposo", tipo: "riposo", nome: "Locanda accogliente", descrizione: "Trovi una locanda dove riposarti." }, effects_applied: ["+50 Vita", "+30 Energia"] },
        { event: { categoria: "combattimento", tipo: "nemico", nome: "Bandito di strada", descrizione: "Un bandito ti attacca per rubarti i Berry!" }, effects_applied: ["+50 Berry", "+20 EXP"] },
      ];
      setEventResult(demoEvents[Math.floor(Math.random() * demoEvents.length)]);
      return;
    }
    setProcessing(true);
    setEventResult(null);
    try {
      const res = await axios.post(`${API}/exploration/random-event`, {}, { headers: { Authorization: `Bearer ${authToken}` } });
      setEventResult(res.data);
      fetchIslandInfo(); // Refresh stats
    } catch (e) {
      console.error('Error triggering event:', e);
    }
    setProcessing(false);
  };

  const eventIcons = {
    scoperta: '💎',
    sociale: '👥',
    riposo: '🏠',
    combattimento: '⚔️',
    pericolo: '⚠️'
  };

  const eventColors = {
    scoperta: '#D4AF37',
    sociale: '#00A8E8',
    riposo: '#2A9D8F',
    combattimento: '#D00000',
    pericolo: '#F59E0B'
  };

  if (loading) return <LoadingScreen />;

  return (
    <div className="min-h-screen bg-[#051923]">
      {/* Header */}
      <div className="glass p-4 flex justify-between items-center">
        <button onClick={() => navigate('/dashboard')} className="text-[#E3D5CA] hover:text-[#FFC300]">
          <Home className="w-6 h-6" />
        </button>
        <div className="text-center">
          <h1 className="font-pirate text-2xl text-[#2A9D8F]">Esplora Isola</h1>
          <p className="text-sm text-[#E3D5CA]/60">{islandInfo?.island?.name}</p>
        </div>
        <button onClick={() => navigate('/world-map')} className="text-[#E3D5CA] hover:text-[#00A8E8]">
          <Map className="w-6 h-6" />
        </button>
      </div>

      {/* Stats Bar */}
      <div className="p-4 glass mx-4 mt-4 rounded-xl">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="flex items-center justify-center gap-1 mb-1">
              <Heart className="w-4 h-4 text-[#D00000]" />
              <span className="text-xs text-[#E3D5CA]/70">Vita</span>
            </div>
            <p className="font-bold text-[#E3D5CA]">{stats.vita}/{stats.vita_max}</p>
          </div>
          <div>
            <div className="flex items-center justify-center gap-1 mb-1">
              <Zap className="w-4 h-4 text-[#00A8E8]" />
              <span className="text-xs text-[#E3D5CA]/70">Energia</span>
            </div>
            <p className="font-bold text-[#E3D5CA]">{stats.energia}/{stats.energia_max}</p>
          </div>
          <div>
            <div className="flex items-center justify-center gap-1 mb-1">
              <span className="text-[#D4AF37]">฿</span>
              <span className="text-xs text-[#E3D5CA]/70">Berry</span>
            </div>
            <p className="font-bold text-[#D4AF37]">{stats.berry?.toLocaleString()}</p>
          </div>
        </div>
      </div>

      {/* Island Info */}
      <div className="p-4">
        <div className="glass p-4 rounded-xl mb-4">
          <p className="text-[#E3D5CA]/80 text-sm">{islandInfo?.island?.storia}</p>
          <div className="flex items-center gap-2 mt-2">
            {[...Array(islandInfo?.island?.pericolo || 1)].map((_, i) => (
              <Skull key={i} className="w-4 h-4 text-[#D00000]" />
            ))}
            <span className="text-xs text-[#E3D5CA]/60">Livello pericolo</span>
          </div>
        </div>

        {/* Event Button */}
        <motion.button
          onClick={triggerEvent}
          disabled={processing}
          className="w-full py-4 rounded-xl bg-gradient-to-r from-[#7209B7] to-[#3A0CA3] text-white font-pirate text-xl mb-4 flex items-center justify-center gap-3"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <Dice6 className="w-6 h-6" />
          {processing ? 'Cercando evento...' : '🎲 Evento Casuale'}
        </motion.button>

        {/* Event Result */}
        <AnimatePresence>
          {eventResult && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="glass p-4 rounded-xl mb-4 border-2"
              style={{ borderColor: eventColors[eventResult.event?.categoria] }}
            >
              <div className="flex items-start gap-3">
                <span className="text-3xl">{eventIcons[eventResult.event?.categoria]}</span>
                <div className="flex-1">
                  <h3 className="font-bold text-[#E3D5CA]">{eventResult.event?.nome}</h3>
                  <p className="text-sm text-[#E3D5CA]/70 mt-1">{eventResult.event?.descrizione}</p>
                  {eventResult.effects_applied?.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {eventResult.effects_applied.map((effect, i) => (
                        <span key={i} className={`text-xs px-2 py-1 rounded ${effect.startsWith('+') ? 'bg-[#2A9D8F]/20 text-[#2A9D8F]' : 'bg-[#D00000]/20 text-[#D00000]'}`}>
                          {effect}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
              <button onClick={() => setEventResult(null)} className="mt-3 w-full py-2 glass rounded-lg text-[#E3D5CA]/70 text-sm">
                Chiudi
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Zone List */}
        <h3 className="font-pirate text-xl text-[#E3D5CA] mb-3">Zone dell'Isola</h3>
        {islandInfo?.island?.zone?.length > 0 ? (
          <div className="space-y-2">
            {islandInfo.island.zone.map((zone) => {
              const isVisited = islandInfo.visited_zones?.includes(zone.id);
              return (
                <motion.button
                  key={zone.id}
                  onClick={() => visitZone(zone.id)}
                  disabled={processing}
                  className={`w-full p-4 rounded-xl text-left transition-all ${isVisited ? 'glass border border-[#2A9D8F]/50' : 'glass'}`}
                  whileHover={{ scale: 1.01 }}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-bold text-[#E3D5CA] flex items-center gap-2">
                        {zone.name}
                        {isVisited && <span className="text-xs text-[#2A9D8F]">✓ Visitata</span>}
                      </h4>
                      <p className="text-sm text-[#E3D5CA]/60 mt-1">{zone.descrizione}</p>
                    </div>
                    <ChevronRight className="w-5 h-5 text-[#E3D5CA]/40" />
                  </div>
                </motion.button>
              );
            })}
          </div>
        ) : (
          <div className="glass p-6 rounded-xl text-center">
            <MapPin className="w-12 h-12 text-[#E3D5CA]/30 mx-auto mb-2" />
            <p className="text-[#E3D5CA]/60">Quest'isola non ha zone esplorabili specifiche.</p>
            <p className="text-[#E3D5CA]/60 text-sm mt-1">Usa "Evento Casuale" per esplorare!</p>
          </div>
        )}
      </div>

      {/* Zone Detail Modal */}
      <AnimatePresence>
        {selectedZone && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50"
            onClick={() => setSelectedZone(null)}
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.9 }}
              className="glass p-6 rounded-xl max-w-md w-full"
              onClick={e => e.stopPropagation()}
            >
              <h2 className="font-pirate text-2xl text-[#2A9D8F] mb-2">{selectedZone.name}</h2>
              <p className="text-[#E3D5CA]/80 mb-4">{selectedZone.descrizione}</p>
              
              <div className="space-y-2">
                <button
                  onClick={() => { setSelectedZone(null); triggerEvent(); }}
                  className="w-full py-3 rounded-lg bg-[#7209B7] text-white font-bold"
                >
                  🎲 Cerca Evento qui
                </button>
                <button
                  onClick={() => setSelectedZone(null)}
                  className="w-full py-2 glass rounded-lg text-[#E3D5CA]"
                >
                  Chiudi
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Narrative Panel */}
      <NarrativePanel 
        token={token} 
        character={character} 
        isDemo={isDemo}
        isExpanded={false}
        setIsExpanded={() => {}}
      />
    </div>
  );
};

// ============ WORLD MAP (Four Seas Navigation) ============
const WorldMap = ({ token, character, isDemo }) => {
  const navigate = useNavigate();
  const authToken = token || localStorage.getItem('token');
  const [islands, setIslands] = useState([]);
  const [seaInfo, setSeaInfo] = useState({});
  const [currentIsland, setCurrentIsland] = useState(null);
  const [selectedIsland, setSelectedIsland] = useState(null);
  const [traveling, setTraveling] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [viewingSea, setViewingSea] = useState(null);
  const [viewingIslands, setViewingIslands] = useState([]);
  const [allSeas, setAllSeas] = useState({});
  // Navigation system state
  const [showNavModal, setShowNavModal] = useState(false);
  const [navStatus, setNavStatus] = useState(null);
  const [diceRolling, setDiceRolling] = useState(false);
  const [diceResult, setDiceResult] = useState(null);
  const [diceAnimation, setDiceAnimation] = useState(1);

  const seaColors = {
    east_blue: '#3B82F6',
    west_blue: '#10B981',
    north_blue: '#8B5CF6',
    south_blue: '#F59E0B'
  };

  const seaNames = {
    east_blue: 'East Blue',
    west_blue: 'West Blue',
    north_blue: 'North Blue',
    south_blue: 'South Blue'
  };

  const seaIcons = {
    east_blue: '🌅',
    west_blue: '🌿',
    north_blue: '❄️',
    south_blue: '☀️'
  };

  // Demo mock islands for East Blue
  const demoIslands = [
    { id: "dawn_island", name: "Dawn Island", sea: "east_blue", order: 1, x: 10, y: 70, storia: "L'isola dove tutto ha avuto inizio. Patria di Monkey D. Luffy.", zone: [{id: "foosha", name: "Foosha Village", descrizione: "Villaggio di pescatori dove Luffy è cresciuto."}], pericolo: 2, sbloccata: true, corrente: true, can_travel_back: false, can_travel_forward: false },
    { id: "shells_town", name: "Shells Town", sea: "east_blue", order: 2, x: 20, y: 60, storia: "Città portuale con una base della Marina.", zone: [], pericolo: 3, sbloccata: true, corrente: false, can_travel_back: false, can_travel_forward: true },
    { id: "shimotsuki_village", name: "Shimotsuki Village", sea: "east_blue", order: 3, x: 28, y: 55, storia: "Villaggio fondato da samurai di Wano.", zone: [], pericolo: 2, sbloccata: false, corrente: false, can_travel_back: false, can_travel_forward: false },
    { id: "organ_islands", name: "Organ Islands", sea: "east_blue", order: 4, x: 36, y: 50, storia: "Arcipelago devastato da Buggy il Clown.", zone: [{id: "orange_town", name: "Orange Town", descrizione: "Città principale dell'arcipelago."}], pericolo: 4, sbloccata: false, corrente: false, can_travel_back: false, can_travel_forward: false },
    { id: "gecko_islands", name: "Gecko Islands", sea: "east_blue", order: 5, x: 52, y: 48, storia: "Casa di Usopp e Kaya.", zone: [{id: "syrup_village", name: "Syrup Village", descrizione: "Tranquillo villaggio."}], pericolo: 3, sbloccata: false, corrente: false, can_travel_back: false, can_travel_forward: false },
    { id: "baratie", name: "Baratie", sea: "east_blue", order: 6, x: 60, y: 42, storia: "Il famoso ristorante galleggiante.", zone: [], pericolo: 5, sbloccata: false, corrente: false, can_travel_back: false, can_travel_forward: false },
    { id: "conomi_islands", name: "Conomi Islands", sea: "east_blue", order: 7, x: 70, y: 38, storia: "Arcipelago liberato da Arlong.", zone: [], pericolo: 6, sbloccata: false, corrente: false, can_travel_back: false, can_travel_forward: false },
    { id: "loguetown", name: "Loguetown", sea: "east_blue", order: 8, x: 85, y: 50, storia: "La Città dell'Inizio e della Fine.", zone: [], pericolo: 5, sbloccata: false, corrente: false, can_travel_back: false, can_travel_forward: false },
  ];

  const fetchIslands = async () => {
    if (isDemo) {
      setIslands(demoIslands);
      setSeaInfo({ name: "East Blue", description: "Il mare più debole dei quattro, ma patria di grandi pirati." });
      setCurrentIsland("dawn_island");
      return;
    }
    try {
      const res = await axios.get(`${API}/world/islands`, { headers: { Authorization: `Bearer ${authToken}` } });
      setIslands(res.data.islands);
      setSeaInfo(res.data.sea_info || {});
      setCurrentIsland(res.data.isola_corrente);
    } catch (e) {
      console.error('Error fetching islands:', e);
    }
  };

  const fetchAllSeas = async () => {
    if (isDemo) {
      setAllSeas({
        east_blue: { name: "East Blue", color: "#3B82F6" },
        west_blue: { name: "West Blue", color: "#10B981" },
        north_blue: { name: "North Blue", color: "#8B5CF6" },
        south_blue: { name: "South Blue", color: "#F59E0B" }
      });
      return;
    }
    try {
      const res = await axios.get(`${API}/world/seas`, { headers: { Authorization: `Bearer ${authToken}` } });
      setAllSeas(res.data.seas);
    } catch (e) {
      console.error('Error fetching seas:', e);
    }
  };

  const fetchSeaIslands = async (seaId) => {
    if (isDemo) {
      // In demo, just show a message that this is demo mode
      setMessage({ type: 'info', text: '🎮 In modalità demo, solo East Blue è disponibile.' });
      return;
    }
    try {
      const res = await axios.get(`${API}/world/seas/${seaId}/islands`, { headers: { Authorization: `Bearer ${authToken}` } });
      setViewingIslands(res.data.islands);
      setViewingSea(seaId);
    } catch (e) {
      console.error('Error fetching sea islands:', e);
    }
  };

  useEffect(() => {
    fetchIslands();
    fetchAllSeas();
  }, [authToken, isDemo]);

  // Navigation status
  const fetchNavStatus = async () => {
    if (isDemo) {
      setNavStatus({
        current_island: { id: "dawn_island", name: "Dawn Island" },
        next_island: { id: "shells_town", name: "Shells Town" },
        prev_island: null,
        progress: 0,
        progress_required: 3,
        has_ship: true,
        can_advance: false,
        can_go_back: false,
        character_stats: { vita: 120, vita_max: 120, energia: 100, energia_max: 100, berry: 5000, attacco: 25, difesa: 20, velocita: 22 }
      });
      return;
    }
    try {
      const res = await axios.get(`${API}/navigation/status`, { headers: { Authorization: `Bearer ${authToken}` } });
      setNavStatus(res.data);
    } catch (e) {
      console.error('Error fetching nav status:', e);
    }
  };

  const openNavigation = () => {
    fetchNavStatus();
    setShowNavModal(true);
    setDiceResult(null);
  };

  const travelTo = async (islandId) => {
    if (isDemo) {
      setMessage({ type: 'info', text: '🎮 In modalità demo, usa il sistema di navigazione con il dado.' });
      return;
    }
    setTraveling(true);
    setMessage({ type: '', text: '' });
    try {
      const res = await axios.post(`${API}/world/travel`, { island_id: islandId }, { headers: { Authorization: `Bearer ${authToken}` } });
      setMessage({ type: 'success', text: `⚓ ${res.data.message}` });
      setSelectedIsland(null);
      fetchIslands();
    } catch (e) {
      setMessage({ type: 'error', text: `❌ ${e.response?.data?.detail || 'Errore durante il viaggio'}` });
    }
    setTraveling(false);
  };

  // New 3-stage dice navigation
  const rollDice = async () => {
    if (isDemo) {
      setDiceRolling(true);
      setDiceResult(null);
      
      const animationInterval = setInterval(() => {
        setDiceAnimation(Math.floor(Math.random() * 6) + 1);
      }, 100);
      
      setTimeout(() => {
        clearInterval(animationInterval);
        const result = Math.floor(Math.random() * 6) + 1;
        setDiceAnimation(result);
        const events = [
          { nome: "Mare Calmo", descrizione: "La navigazione procede senza intoppi.", tipo: "positivo" },
          { nome: "Corrente Contraria", descrizione: "Una corrente rallenta il viaggio.", tipo: "neutro" },
          { nome: "Tempesta!", descrizione: "Una tempesta si abbatte sulla nave!", tipo: "sfida" },
          { nome: "Pirati Nemici!", descrizione: "Una nave pirata vi attacca!", tipo: "sfida" }
        ];
        const eventPassed = result >= 2;
        const newProgress = eventPassed ? Math.min((navStatus?.progress || 0) + 1, 3) : (navStatus?.progress || 0);
        
        setDiceResult({
          dice_result: result,
          bonuses: { nave: 1, fortuna: 0 },
          total: result + 1,
          difficulty: result >= 5 ? "facile" : result >= 3 ? "medio" : "difficile",
          event: events[Math.floor(Math.random() * events.length)],
          challenge: result < 3 ? { stat_used: "attacco", stat_value: 25, roll: 12, total: 37, needed: 30, passed: eventPassed } : null,
          event_passed: eventPassed,
          effects_applied: result >= 4 ? ["+30 Berry"] : result < 3 && !eventPassed ? ["-20 Vita"] : ["-10 Energia"],
          progress: { before: navStatus?.progress || 0, after: newProgress, required: 3, complete: newProgress >= 3 }
        });
        setDiceRolling(false);
        
        setNavStatus(prev => ({ 
          ...prev, 
          progress: newProgress, 
          can_advance: newProgress >= 3 
        }));
      }, 2000);
      return;
    }

    setDiceRolling(true);
    setDiceResult(null);
    
    const animationInterval = setInterval(() => {
      setDiceAnimation(Math.floor(Math.random() * 6) + 1);
    }, 100);

    try {
      const res = await axios.post(`${API}/navigation/roll-dice`, {}, { headers: { Authorization: `Bearer ${authToken}` } });
      
      setTimeout(() => {
        clearInterval(animationInterval);
        setDiceAnimation(res.data.dice_result);
        setDiceResult(res.data);
        setDiceRolling(false);
        fetchNavStatus();
      }, 2000);
    } catch (e) {
      clearInterval(animationInterval);
      setDiceRolling(false);
      setDiceResult({ error: e.response?.data?.detail || 'Errore' });
    }
  };

  const advanceToIsland = async () => {
    if (isDemo) {
      setMessage({ type: 'success', text: '🎮 Demo: Arrivato all\'isola successiva!' });
      setShowNavModal(false);
      setNavStatus(prev => ({ ...prev, progress: 0, can_advance: false }));
      setDiceResult(null);
      return;
    }
    try {
      const res = await axios.post(`${API}/navigation/advance`, {}, { headers: { Authorization: `Bearer ${authToken}` } });
      setMessage({ type: 'success', text: `⚓ ${res.data.message}` });
      setShowNavModal(false);
      setDiceResult(null);
      fetchIslands();
      fetchNavStatus();
    } catch (e) {
      setMessage({ type: 'error', text: e.response?.data?.detail || 'Errore' });
    }
  };

  const goBackToIsland = async () => {
    if (isDemo) {
      setMessage({ type: 'info', text: '🎮 Demo: Tornato all\'isola precedente!' });
      setShowNavModal(false);
      return;
    }
    try {
      const res = await axios.post(`${API}/navigation/go-back`, {}, { headers: { Authorization: `Bearer ${authToken}` } });
      setMessage({ type: 'success', text: `⬅️ ${res.data.message}` });
      setShowNavModal(false);
      setDiceResult(null);
      fetchIslands();
      fetchNavStatus();
    } catch (e) {
      setMessage({ type: 'error', text: e.response?.data?.detail || 'Errore' });
    }
  };

  const currentSeaColor = seaColors[character?.mare_corrente] || '#3B82F6';
  const displaySea = viewingSea || character?.mare_corrente;
  const displayIslands = viewingSea ? viewingIslands : islands;
  const isViewingOtherSea = viewingSea && viewingSea !== character?.mare_corrente;

  // Check if can use dice (has ship and not at last island)
  const canUseDice = character?.nave && !isViewingOtherSea && islands.some(i => i.can_travel_forward);

  return (
    <div className="min-h-screen bg-[#051923]">
      {/* Header */}
      <div className="glass p-4 flex justify-between items-center">
        <button onClick={() => navigate('/dashboard')} className="text-[#E3D5CA] hover:text-[#FFC300]">
          <Home className="w-6 h-6" />
        </button>
        <div className="text-center">
          <h1 className="font-pirate text-2xl" style={{ color: seaColors[displaySea] }}>
            {seaIcons[displaySea]} {seaNames[displaySea] || 'East Blue'}
          </h1>
          {isViewingOtherSea && (
            <span className="text-xs text-[#FFC300]">👁️ Solo visualizzazione</span>
          )}
        </div>
        <Ship className="w-6 h-6" style={{ color: seaColors[displaySea] }} />
      </div>

      {/* Sea Selector */}
      <div className="p-4 flex gap-2 overflow-x-auto">
        {Object.entries(seaNames).map(([seaId, name]) => (
          <button
            key={seaId}
            onClick={() => seaId === character?.mare_corrente ? setViewingSea(null) : fetchSeaIslands(seaId)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg whitespace-nowrap text-sm transition-all ${
              (viewingSea === seaId || (!viewingSea && seaId === character?.mare_corrente))
                ? 'ring-2 ring-offset-2 ring-offset-[#051923]'
                : 'glass opacity-70 hover:opacity-100'
            }`}
            style={{ 
              backgroundColor: seaColors[seaId] + '30',
              color: seaColors[seaId],
              ringColor: seaColors[seaId]
            }}
          >
            <span>{seaIcons[seaId]}</span>
            <span>{name}</span>
            {seaId === character?.mare_corrente && <span className="text-xs">📍</span>}
          </button>
        ))}
        {viewingSea && viewingSea !== character?.mare_corrente && (
          <button
            onClick={() => setViewingSea(null)}
            className="px-3 py-2 rounded-lg bg-[#D00000]/20 text-[#D00000] text-sm"
          >
            ✕ Chiudi
          </button>
        )}
      </div>

      {/* Message */}
      {message.text && (
        <motion.div 
          initial={{ opacity: 0, y: -10 }} 
          animate={{ opacity: 1, y: 0 }}
          className={`mx-4 mb-4 p-3 rounded-lg ${
            message.type === 'success' ? 'bg-[#2A9D8F]/20 border border-[#2A9D8F]' : 
            message.type === 'info' ? 'bg-[#00A8E8]/20 border border-[#00A8E8]' :
            'bg-[#D00000]/20 border border-[#D00000]'
          }`}
        >
          <p className={
            message.type === 'success' ? 'text-[#2A9D8F]' : 
            message.type === 'info' ? 'text-[#00A8E8]' :
            'text-[#D00000]'
          }>{message.text}</p>
        </motion.div>
      )}

      {/* Sea Map */}
      <div className="px-4 pb-4">
        <div className="relative w-full h-[45vh] rounded-xl border-2 overflow-hidden" style={{ borderColor: seaColors[displaySea], backgroundColor: `${seaColors[displaySea]}10` }}>
          {/* Wave pattern background */}
          <div className="absolute inset-0 opacity-10" style={{ 
            backgroundImage: `repeating-linear-gradient(90deg, transparent, transparent 50px, ${seaColors[displaySea]}20 50px, ${seaColors[displaySea]}20 100px)` 
          }} />
          
          {/* Connection lines */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none">
            {displayIslands.slice(0, -1).map((island, i) => {
              const next = displayIslands[i + 1];
              if (!next) return null;
              const isUnlocked = !isViewingOtherSea && island.sbloccata && next.sbloccata;
              return (
                <line
                  key={`line-${i}`}
                  x1={`${island.x}%`}
                  y1={`${island.y}%`}
                  x2={`${next.x}%`}
                  y2={`${next.y}%`}
                  stroke={isViewingOtherSea ? seaColors[displaySea] : (isUnlocked ? seaColors[displaySea] : '#3E2723')}
                  strokeWidth="2"
                  strokeDasharray={isViewingOtherSea || !next.sbloccata ? "5,5" : "0"}
                  opacity={isViewingOtherSea ? "0.3" : "0.5"}
                />
              );
            })}
          </svg>

          {/* Islands */}
          {displayIslands.map((island, idx) => {
            const isAccessible = isViewingOtherSea ? true : island.sbloccata;
            const isCurrent = !isViewingOtherSea && island.corrente;
            
            return (
              <motion.div
                key={island.id}
                className="absolute cursor-pointer"
                style={{ left: `${island.x}%`, top: `${island.y}%`, transform: 'translate(-50%, -50%)' }}
                whileHover={isAccessible ? { scale: 1.2 } : {}}
                onClick={() => isAccessible && setSelectedIsland({ ...island, isViewOnly: isViewingOtherSea })}
              >
                {/* Island marker */}
                <div className={`relative w-10 h-10 rounded-full flex items-center justify-center transition-all ${
                  isCurrent 
                    ? 'ring-4 ring-[#FFC300] animate-pulse' 
                    : isAccessible 
                      ? 'ring-2 ring-opacity-50' 
                      : 'opacity-40'
                }`} style={{ 
                  backgroundColor: isCurrent ? '#FFC300' : isAccessible ? seaColors[displaySea] : '#3E2723',
                  ringColor: seaColors[displaySea]
                }}>
                  {isCurrent ? (
                    <Anchor className="w-5 h-5 text-[#051923]" />
                  ) : isAccessible ? (
                    <MapPin className="w-5 h-5 text-white" />
                  ) : (
                    <span className="text-[#E3D5CA]/50">?</span>
                  )}
                </div>
                
                {/* Island name */}
                <div className="absolute top-12 left-1/2 -translate-x-1/2 whitespace-nowrap text-center">
                  <p className={`text-xs font-bold ${
                    isCurrent ? 'text-[#FFC300]' : isAccessible ? 'text-[#E3D5CA]' : 'text-[#3E2723]'
                  }`}>
                    {island.name}
                  </p>
                  {isCurrent && <span className="text-[10px] text-[#FFC300]/60">📍 Sei qui</span>}
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Navigation instructions */}
        <div className="flex justify-center gap-4 mt-4 text-xs flex-wrap">
          <span className="flex items-center gap-1 text-[#E3D5CA]/60">
            <div className="w-3 h-3 rounded-full bg-[#FFC300]" /> Posizione attuale
          </span>
          <span className="flex items-center gap-1 text-[#E3D5CA]/60">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: seaColors[displaySea] }} /> Accessibile
          </span>
          {!isViewingOtherSea && (
            <span className="flex items-center gap-1 text-[#E3D5CA]/60">
              <div className="w-3 h-3 rounded-full bg-[#3E2723]" /> Bloccata
            </span>
          )}
        </div>

        {/* Dice Navigation Button */}
        {!isViewingOtherSea && (
          <div className="mt-4 flex gap-3">
            <motion.button
              onClick={openNavigation}
              disabled={!canUseDice}
              className={`flex-1 py-4 rounded-xl font-pirate text-lg flex items-center justify-center gap-3 ${
                canUseDice 
                  ? 'bg-gradient-to-r from-[#D4AF37] to-[#FFC300] text-[#051923]' 
                  : 'bg-[#3E2723] text-[#E3D5CA]/50'
              }`}
              whileHover={canUseDice ? { scale: 1.02 } : {}}
              whileTap={canUseDice ? { scale: 0.98 } : {}}
            >
              <Dice6 className="w-6 h-6" />
              🎲 Naviga con il Dado
            </motion.button>
            <button
              onClick={() => navigate('/explore')}
              className="py-4 px-6 rounded-xl glass text-[#2A9D8F] font-bold"
            >
              <Compass className="w-6 h-6" />
            </button>
          </div>
        )}
        {!isViewingOtherSea && !character?.nave && (
          <p className="text-center text-[#D00000] text-sm mt-2">🚢 Compra una nave al negozio per navigare!</p>
        )}
      </div>

      {/* Navigation Modal (3 Stages) */}
      <AnimatePresence>
        {showNavModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/90 flex items-center justify-center p-4 z-50"
            onClick={() => !diceRolling && setShowNavModal(false)}
          >
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.8 }}
              className="glass p-6 rounded-xl max-w-lg w-full max-h-[90vh] overflow-y-auto"
              onClick={e => e.stopPropagation()}
            >
              {/* Header */}
              <div className="text-center mb-4">
                <h2 className="font-pirate text-2xl text-[#FFC300]">🚢 Navigazione</h2>
                <p className="text-[#E3D5CA]/70 text-sm">
                  {navStatus?.current_island?.name} → {navStatus?.next_island?.name || "???"}
                </p>
              </div>

              {/* Progress Bar */}
              <div className="mb-6">
                <div className="flex justify-between text-xs text-[#E3D5CA]/60 mb-1">
                  <span>Progresso</span>
                  <span>{navStatus?.progress || 0} / {navStatus?.progress_required || 3}</span>
                </div>
                <div className="h-4 bg-[#3E2723] rounded-full overflow-hidden">
                  <motion.div 
                    className="h-full bg-gradient-to-r from-[#2A9D8F] to-[#FFC300]"
                    initial={{ width: 0 }}
                    animate={{ width: `${((navStatus?.progress || 0) / (navStatus?.progress_required || 3)) * 100}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
                <div className="flex justify-between mt-1">
                  {[1, 2, 3].map(step => (
                    <div key={step} className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                      (navStatus?.progress || 0) >= step 
                        ? 'bg-[#2A9D8F] text-white' 
                        : 'bg-[#3E2723] text-[#E3D5CA]/40'
                    }`}>
                      {(navStatus?.progress || 0) >= step ? '✓' : step}
                    </div>
                  ))}
                </div>
              </div>

              {/* Dice Display */}
              <div className="flex justify-center mb-4">
                <motion.div
                  className="w-24 h-24 bg-[#3E2723] rounded-2xl flex items-center justify-center border-4 border-[#D4AF37] shadow-xl"
                  animate={diceRolling ? { 
                    rotateX: [0, 360], 
                    rotateY: [0, 360],
                    scale: [1, 1.1, 1]
                  } : {}}
                  transition={{ duration: 0.3, repeat: diceRolling ? Infinity : 0 }}
                >
                  <span className="font-pirate text-5xl text-[#FFC300]">{diceAnimation}</span>
                </motion.div>
              </div>

              {/* Dice Result */}
              {diceResult && !diceResult.error && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mb-4 p-4 rounded-lg border-2"
                  style={{ 
                    borderColor: diceResult.event_passed ? '#2A9D8F' : '#D00000',
                    backgroundColor: diceResult.event_passed ? 'rgba(42,157,143,0.1)' : 'rgba(208,0,0,0.1)'
                  }}
                >
                  {/* Dice stats */}
                  <div className="flex justify-center gap-3 mb-3 text-sm">
                    <span className="px-2 py-1 bg-[#051923] rounded">🎲 {diceResult.dice_result}</span>
                    <span className="px-2 py-1 bg-[#051923] rounded text-[#2A9D8F]">+{diceResult.bonuses?.nave || 0} Nave</span>
                    <span className="px-2 py-1 bg-[#051923] rounded text-[#D4AF37]">= {diceResult.total}</span>
                  </div>

                  {/* Event */}
                  <div className="text-center mb-3">
                    <p className={`font-bold text-lg ${
                      diceResult.difficulty === 'facile' ? 'text-[#2A9D8F]' : 
                      diceResult.difficulty === 'medio' ? 'text-[#F59E0B]' : 'text-[#D00000]'
                    }`}>
                      {diceResult.event?.nome}
                    </p>
                    <p className="text-[#E3D5CA]/70 text-sm">{diceResult.event?.descrizione}</p>
                  </div>

                  {/* Challenge result if any */}
                  {diceResult.challenge && (
                    <div className="p-2 bg-[#051923] rounded mb-3 text-sm">
                      <p className="text-[#E3D5CA]/60">
                        Sfida: {diceResult.challenge.stat_used} ({diceResult.challenge.stat_value}) + 🎲{diceResult.challenge.roll} = {diceResult.challenge.total}
                      </p>
                      <p className={diceResult.challenge.passed ? 'text-[#2A9D8F]' : 'text-[#D00000]'}>
                        Necessario: {diceResult.challenge.needed} → {diceResult.challenge.passed ? '✓ Superato!' : '✗ Fallito!'}
                      </p>
                    </div>
                  )}

                  {/* Effects */}
                  {diceResult.effects_applied?.length > 0 && (
                    <div className="flex flex-wrap gap-2 justify-center mb-3">
                      {diceResult.effects_applied.map((effect, i) => (
                        <span key={i} className={`text-xs px-2 py-1 rounded ${
                          effect.startsWith('+') ? 'bg-[#2A9D8F]/20 text-[#2A9D8F]' : 'bg-[#D00000]/20 text-[#D00000]'
                        }`}>
                          {effect}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Result */}
                  <p className={`text-center font-bold ${diceResult.event_passed ? 'text-[#2A9D8F]' : 'text-[#D00000]'}`}>
                    {diceResult.event_passed ? '✓ Tappa completata!' : '✗ Tappa fallita - Riprova!'}
                  </p>
                </motion.div>
              )}

              {diceResult?.error && (
                <div className="mb-4 p-4 bg-[#D00000]/20 rounded-lg border border-[#D00000]">
                  <p className="text-[#D00000] text-center">{diceResult.error}</p>
                </div>
              )}

              {/* Actions */}
              <div className="space-y-3">
                {/* Roll dice button */}
                {(navStatus?.progress || 0) < 3 && (
                  <motion.button
                    onClick={rollDice}
                    disabled={diceRolling}
                    className="w-full py-4 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#FFC300] text-[#051923] font-pirate text-xl"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    {diceRolling ? '🎲 Tirando...' : `🎲 Tira il Dado (Tappa ${(navStatus?.progress || 0) + 1}/3)`}
                  </motion.button>
                )}

                {/* Advance button when complete */}
                {navStatus?.can_advance && (
                  <motion.button
                    onClick={advanceToIsland}
                    className="w-full py-4 rounded-xl bg-gradient-to-r from-[#2A9D8F] to-[#00A8E8] text-white font-pirate text-xl"
                    whileHover={{ scale: 1.02 }}
                    animate={{ scale: [1, 1.05, 1] }}
                    transition={{ duration: 1, repeat: Infinity }}
                  >
                    ⚓ Sbarca a {navStatus?.next_island?.name}!
                  </motion.button>
                )}

                {/* Go back button - always available except at first island */}
                {navStatus?.can_go_back && (
                  <button
                    onClick={goBackToIsland}
                    className="w-full py-3 rounded-xl glass text-[#00A8E8] border border-[#00A8E8]/50"
                  >
                    ⬅️ Torna a {navStatus?.prev_island?.name} (recupera)
                  </button>
                )}

                {/* Close */}
                <button
                  onClick={() => { setShowNavModal(false); setDiceResult(null); }}
                  className="w-full py-2 rounded-xl glass text-[#E3D5CA]/70 text-sm"
                >
                  Chiudi
                </button>
              </div>

              {/* Legend */}
              <div className="mt-4 p-3 bg-[#051923]/50 rounded-lg text-xs text-[#E3D5CA]/50">
                <p>🎲 5-6: Evento facile | 🎲 3-4: Evento medio | 🎲 1-2: Evento difficile (sfida)</p>
                <p className="mt-1">Completa 3 tappe per raggiungere l'isola successiva!</p>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Selected Island Modal */}
      <AnimatePresence>
        {selectedIsland && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 flex items-end md:items-center justify-center p-4 z-50"
            onClick={() => setSelectedIsland(null)}
          >
            <motion.div
              initial={{ y: 100 }}
              animate={{ y: 0 }}
              exit={{ y: 100 }}
              className="glass p-6 rounded-xl max-w-lg w-full max-h-[80vh] overflow-y-auto"
              onClick={e => e.stopPropagation()}
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="font-pirate text-2xl" style={{ color: seaColors[selectedIsland.sea] }}>{selectedIsland.name}</h2>
                  <div className="flex items-center gap-2 mt-1">
                    {[...Array(selectedIsland.pericolo || 1)].map((_, i) => (
                      <Skull key={i} className="w-4 h-4 text-[#D00000]" />
                    ))}
                    <span className="text-xs text-[#E3D5CA]/60">Livello pericolo</span>
                  </div>
                </div>
                <button onClick={() => setSelectedIsland(null)} className="text-[#E3D5CA]/60 hover:text-[#E3D5CA]">✕</button>
              </div>

              {selectedIsland.isViewOnly && (
                <div className="mb-4 p-2 bg-[#FFC300]/10 rounded border border-[#FFC300]/30">
                  <p className="text-[#FFC300] text-xs text-center">👁️ Visualizzazione - Non puoi navigare qui</p>
                </div>
              )}

              <p className="text-[#E3D5CA]/80 text-sm mb-4">{selectedIsland.storia}</p>

              {/* Internal Zones */}
              {selectedIsland.zone?.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-[#D4AF37] text-sm mb-2 font-bold">🗺️ Zone esplorabili:</h4>
                  <div className="space-y-2">
                    {selectedIsland.zone.map((zona, i) => (
                      <div key={i} className="p-3 bg-[#003566]/30 rounded-lg">
                        <p className="font-bold text-[#E3D5CA]">{zona.name}</p>
                        <p className="text-xs text-[#E3D5CA]/70 mt-1">{zona.descrizione}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Navigation buttons - only for current sea */}
              {!selectedIsland.isViewOnly && (
                <>
                  {selectedIsland.corrente ? (
                    <div className="p-3 bg-[#FFC300]/10 rounded-lg border border-[#FFC300]/30">
                      <p className="text-[#FFC300] text-sm text-center">📍 Sei attualmente su quest'isola</p>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {selectedIsland.can_travel_back && (
                        <button
                          onClick={() => travelTo(selectedIsland.id)}
                          disabled={traveling}
                          className="w-full py-3 rounded-lg bg-[#00A8E8] text-white font-bold"
                        >
                          {traveling ? '⏳ Navigando...' : '⬅️ Torna indietro'}
                        </button>
                      )}
                      {selectedIsland.can_travel_forward && (
                        <button
                          onClick={() => travelTo(selectedIsland.id)}
                          disabled={traveling || !character?.nave}
                          className={`w-full py-3 rounded-lg font-bold ${character?.nave ? 'btn-gold' : 'bg-[#3E2723] text-[#E3D5CA]/50'}`}
                        >
                          {traveling ? '⏳ Navigando...' : character?.nave ? '➡️ Naviga verso quest\'isola' : '🚢 Serve una nave per avanzare'}
                        </button>
                      )}
                      {!selectedIsland.can_travel_back && !selectedIsland.can_travel_forward && selectedIsland.sbloccata && (
                        <div className="p-3 bg-[#D00000]/10 rounded-lg border border-[#D00000]/30">
                          <p className="text-[#D00000] text-sm text-center">Non puoi viaggiare qui direttamente</p>
                        </div>
                      )}
                    </div>
                  )}
                </>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Narrative Panel */}
      <NarrativePanel 
        token={token} 
        character={character} 
        isDemo={isDemo}
        isExpanded={false}
        setIsExpanded={() => {}}
      />
    </div>
  );
};

// ============ BATTLE ARENA (improved) ============
const BattleArena = ({ token, character, isDemo }) => {
  const navigate = useNavigate();
  const authToken = token || localStorage.getItem('token');
  const [battle, setBattle] = useState(null);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [phases, setPhases] = useState(null);
  const [currentPhase, setCurrentPhase] = useState('contrattacco'); // Default to attack phase
  const [showStatsPopup, setShowStatsPopup] = useState(false);
  const [playerStats, setPlayerStats] = useState(null);

  // Fetch battle phases info
  useEffect(() => {
    const fetchPhases = async () => {
      try {
        const res = await axios.get(`${API}/battle/phases`, { headers: { Authorization: `Bearer ${authToken}` } });
        setPhases(res.data.phases);
      } catch (e) {
        console.error('Error fetching phases:', e);
      }
    };
    if (authToken) fetchPhases();
  }, [authToken]);

  const startBattle = async (opponentId) => {
    setLoading(true);
    try {
      const res = await axios.post(`${API}/battle/start`, { opponent_type: 'npc', opponent_id: opponentId }, { headers: { Authorization: `Bearer ${authToken}` } });
      setBattle(res.data.battle);
      setCurrentPhase('contrattacco');
    } catch (e) {
      console.error('Battle start error:', e);
    }
    setLoading(false);
  };

  // New phase-based action
  const doPhaseAction = async (fase, azione, parametri = {}) => {
    if (!battle || battle.turno_corrente !== 'player1' || actionLoading) return;
    setActionLoading(true);
    try {
      const res = await axios.post(`${API}/battle/${battle.battle_id}/phase-action`, 
        { fase, azione, parametri }, 
        { headers: { Authorization: `Bearer ${authToken}` } }
      );
      if (res.data.success) {
        setBattle(res.data.battle);
        // Auto-advance to next phase if available
        if (res.data.next_phase) {
          setCurrentPhase(res.data.next_phase);
        }
      }
    } catch (e) {
      console.error('Phase action error:', e);
    }
    setActionLoading(false);
  };

  // End turn
  const endTurn = async () => {
    if (!battle || actionLoading) return;
    setActionLoading(true);
    try {
      const res = await axios.post(`${API}/battle/${battle.battle_id}/end-turn`, {}, { headers: { Authorization: `Bearer ${authToken}` } });
      setBattle(res.data.battle);
      setCurrentPhase('reazione'); // Start next turn with reaction phase
    } catch (e) {
      console.error('End turn error:', e);
    }
    setActionLoading(false);
  };

  // Fetch character stats popup
  const fetchCharacterStats = async () => {
    if (!battle) return;
    try {
      const res = await axios.get(`${API}/battle/${battle.battle_id}/character-stats`, { headers: { Authorization: `Bearer ${authToken}` } });
      setPlayerStats(res.data);
      setShowStatsPopup(true);
    } catch (e) {
      console.error('Error fetching stats:', e);
    }
  };

  // Legacy action (fallback)
  const doAction = async (actionType, actionName) => {
    if (!battle || battle.turno_corrente !== 'player1' || actionLoading) return;
    setActionLoading(true);
    try {
      const res = await axios.post(`${API}/battle/${battle.battle_id}/action`, { action_type: actionType, action_name: actionName }, { headers: { Authorization: `Bearer ${authToken}` } });
      setBattle(res.data.battle);
    } catch (e) {
      console.error('Action error:', e);
    }
    setActionLoading(false);
  };

  const npcInfo = {
    marine_soldato: { name: 'Marine Soldato', desc: 'Lv.2 - Un soldato della Marina', difficulty: '⭐', level: 2 },
    pirata_novizio: { name: 'Pirata Novizio', desc: 'Lv.1 - Un pirata alle prime armi', difficulty: '⭐', level: 1 },
    marine_capitano: { name: 'Marine Capitano', desc: 'Lv.5 - Un ufficiale della Marina', difficulty: '⭐⭐', level: 5 },
    capitano_pirata: { name: 'Capitano Pirata', desc: 'Lv.8 - Un temibile capitano pirata', difficulty: '⭐⭐⭐', level: 8 },
    boss_marine: { name: 'Ammiraglio Marine', desc: 'Lv.15 - Boss con Haki', difficulty: '⭐⭐⭐⭐', level: 15 }
  };

  // Phase icons and colors
  const phaseConfig = {
    reazione: { icon: '🛡️', color: '#00A8E8', name: 'Reazione' },
    attivazione: { icon: '🃏', color: '#7209B7', name: 'Attivazione' },
    contrattacco: { icon: '⚔️', color: '#D00000', name: 'Contrattacco' }
  };

  if (!battle) {
    return (
      <div className="min-h-screen bg-[#051923] p-4">
        <div className="glass p-4 flex justify-between items-center mb-6">
          <button onClick={() => navigate('/dashboard')} className="text-[#E3D5CA]"><Home className="w-6 h-6" /></button>
          <h1 className="font-pirate text-2xl text-[#FFC300]">Arena di Combattimento</h1>
          <div className="w-6" />
        </div>
        
        <p className="text-center text-[#E3D5CA]/70 mb-6">Scegli il tuo avversario</p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
          {Object.entries(npcInfo).map(([id, info]) => (
            <motion.button 
              key={id} 
              onClick={() => startBattle(id)} 
              disabled={loading}
              className="glass p-4 rounded-lg text-left hover:border-[#D00000] border-2 border-transparent transition-colors"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="flex justify-between items-start">
                <div>
                  <Skull className="w-8 h-8 text-[#D00000] mb-2" />
                  <p className="font-bold text-[#E3D5CA]">{info.name}</p>
                  <p className="text-sm text-[#E3D5CA]/60">{info.desc}</p>
                  <p className="text-xs text-[#D4AF37] mt-1">HP: {info.level * 100} | EN: {info.level * 50}</p>
                </div>
                <span className="text-lg">{info.difficulty}</span>
              </div>
            </motion.button>
          ))}
        </div>
        
        {loading && (
          <div className="text-center mt-6">
            <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: "linear" }}>
              <Swords className="w-8 h-8 text-[#FFC300] mx-auto" />
            </motion.div>
            <p className="text-[#E3D5CA]/70 mt-2">Preparando la battaglia...</p>
          </div>
        )}
      </div>
    );
  }

  const isPlayerTurn = battle.turno_corrente === 'player1';
  const isBattleOver = battle.stato === 'finita';
  const playerWon = battle.vincitore === 'player1';
  const pendingAttack = battle.azione_avversario_pendente;
  const completedPhases = battle.fasi_completate || [];

  return (
    <div className="min-h-screen bg-[#0f0f1a] flex flex-col">
      {/* Turn & Phase indicator */}
      {!isBattleOver && (
        <div className={`p-2 ${isPlayerTurn ? 'bg-[#2A9D8F]' : 'bg-[#D00000]'}`}>
          <div className="flex justify-between items-center max-w-lg mx-auto">
            <p className="font-pixel text-sm text-white">
              {isPlayerTurn ? '🎯 TUO TURNO' : '⏳ Turno avversario'}
            </p>
            <p className="text-xs text-white/80">Turno {battle.numero_turno}</p>
          </div>
        </div>
      )}

      {/* Phase Tabs */}
      {!isBattleOver && isPlayerTurn && (
        <div className="flex justify-center gap-2 p-2 bg-[#051923]">
          {['reazione', 'attivazione', 'contrattacco'].map(phase => {
            const config = phaseConfig[phase];
            const isCompleted = completedPhases.includes(phase);
            const isActive = currentPhase === phase;
            const isDisabled = isCompleted || (phase === 'reazione' && !pendingAttack);
            
            return (
              <button
                key={phase}
                onClick={() => !isCompleted && setCurrentPhase(phase)}
                disabled={isDisabled}
                className={`px-4 py-2 rounded-lg font-bold text-sm transition-all ${
                  isActive ? `bg-[${config.color}] text-white` : 
                  isCompleted ? 'bg-[#333] text-[#666] line-through' :
                  'bg-[#1a1a2e] text-[#E3D5CA]/70 hover:text-white'
                }`}
                style={isActive ? { backgroundColor: config.color } : {}}
              >
                {config.icon} {config.name}
                {isCompleted && ' ✓'}
              </button>
            );
          })}
        </div>
      )}

      {/* Pending Attack Warning */}
      {pendingAttack && isPlayerTurn && (
        <motion.div 
          className="bg-[#D00000]/20 border-l-4 border-[#D00000] p-3 mx-4 mt-2 rounded"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <p className="text-[#D00000] font-bold">⚠️ Attacco in arrivo!</p>
          <p className="text-sm text-[#E3D5CA]">{pendingAttack.tipo} - {pendingAttack.danno} danni</p>
          <p className="text-xs text-[#E3D5CA]/70">Usa la fase REAZIONE per difenderti!</p>
        </motion.div>
      )}

      {/* Enemy */}
      <div className="flex-1 p-4">
        <motion.div 
          className="gameboy-panel p-4 rounded-lg max-w-lg mx-auto"
          animate={!isPlayerTurn && !isBattleOver ? { x: [0, -5, 5, 0] } : {}}
          transition={{ duration: 0.3 }}
        >
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-pixel text-xl text-[#D00000]">{battle.player2.nome}</h3>
              <p className="text-xs text-[#E3D5CA]/60">Lv.{battle.player2.livello_combattimento || 1}</p>
            </div>
            {battle.player2.taglia > 0 && (
              <span className="text-xs bg-[#D00000]/30 px-2 py-1 rounded text-[#D00000]">
                ฿{battle.player2.taglia.toLocaleString()}
              </span>
            )}
          </div>
          <div className="hp-bar mt-2">
            <motion.div 
              className="hp-bar-fill bg-[#D00000]" 
              initial={false}
              animate={{ width: `${(battle.player2.vita / battle.player2.vita_max) * 100}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
          <p className="font-pixel text-sm text-[#E3D5CA]">HP: {battle.player2.vita}/{battle.player2.vita_max}</p>
          <p className="font-pixel text-xs text-[#00A8E8]">EN: {battle.player2.energia}/{battle.player2.energia_max}</p>
        </motion.div>
      </div>

      {/* Battle Log */}
      <div className="p-4 max-h-32 overflow-y-auto bg-[#000]/30">
        <AnimatePresence>
          {battle.log.slice(-5).map((l, i) => (
            <motion.p 
              key={`${battle.numero_turno}-${i}-${l.substring(0,10)}`}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="font-pixel text-sm text-[#E3D5CA]/80 mb-1"
            >
              &gt; {l}
            </motion.p>
          ))}
        </AnimatePresence>
      </div>

      {/* Player Panel */}
      <div className="gameboy-panel p-4">
        <div className="max-w-lg mx-auto">
          {/* Player Stats Header - Click for popup */}
          <div 
            className="flex justify-between items-center cursor-pointer hover:bg-[#FFC300]/10 rounded p-2 -m-2 mb-2"
            onClick={fetchCharacterStats}
          >
            <div>
              <h3 className="font-pixel text-xl text-[#FFC300]">{battle.player1.nome}</h3>
              <p className="text-xs text-[#E3D5CA]/60">Lv.{battle.player1.livello_combattimento || 1} • Clicca per stats</p>
            </div>
            <UserCircle className="w-6 h-6 text-[#FFC300]" />
          </div>

          {/* HP & Energy */}
          <div className="grid grid-cols-2 gap-2">
            <div>
              <div className="hp-bar">
                <motion.div 
                  className="hp-bar-fill bg-[#D00000]" 
                  initial={false}
                  animate={{ width: `${(battle.player1.vita / battle.player1.vita_max) * 100}%` }}
                />
              </div>
              <p className="font-pixel text-xs">HP: {battle.player1.vita}/{battle.player1.vita_max}</p>
            </div>
            <div>
              <div className="hp-bar">
                <motion.div 
                  className="hp-bar-fill bg-[#00A8E8]" 
                  initial={false}
                  animate={{ width: `${(battle.player1.energia / battle.player1.energia_max) * 100}%` }}
                />
              </div>
              <p className="font-pixel text-xs">EN: {battle.player1.energia}/{battle.player1.energia_max}</p>
            </div>
          </div>

          {/* Stats Grid - Always visible */}
          <div className="grid grid-cols-4 gap-1 mt-2 text-center text-xs">
            <div className="bg-[#D00000]/20 rounded p-1">
              <span className="text-[#D00000]">FOR</span>
              <p className="font-bold">{battle.player1.forza}</p>
            </div>
            <div className="bg-[#00A8E8]/20 rounded p-1">
              <span className="text-[#00A8E8]">VEL</span>
              <p className="font-bold">{battle.player1.velocita}</p>
            </div>
            <div className="bg-[#2A9D8F]/20 rounded p-1">
              <span className="text-[#2A9D8F]">RES</span>
              <p className="font-bold">{battle.player1.resistenza}</p>
            </div>
            <div className="bg-[#7209B7]/20 rounded p-1">
              <span className="text-[#7209B7]">AGI</span>
              <p className="font-bold">{battle.player1.agilita}</p>
            </div>
          </div>

          {/* Phase Actions */}
          {!isBattleOver && isPlayerTurn && (
            <div className="mt-4">
              {/* REAZIONE Phase */}
              {currentPhase === 'reazione' && pendingAttack && (
                <div className="space-y-2">
                  <p className="text-xs text-[#00A8E8] mb-2">🛡️ Come reagisci all'attacco?</p>
                  <div className="grid grid-cols-2 gap-2">
                    <button onClick={() => doPhaseAction('reazione', 'subire')} disabled={actionLoading} className="gameboy-button text-sm">
                      😤 Subisci (+10 EN)
                    </button>
                    <button onClick={() => doPhaseAction('reazione', 'schivata')} disabled={actionLoading || battle.player1.energia < 8} className="gameboy-button text-sm">
                      🏃 Schiva (8 EN)
                    </button>
                    <button onClick={() => doPhaseAction('reazione', 'parata')} disabled={actionLoading || battle.player1.energia < 10} className="gameboy-button text-sm">
                      🛡️ Para (10 EN)
                    </button>
                    <button onClick={() => doPhaseAction('reazione', 'contrasto')} disabled={actionLoading || battle.player1.energia < 15} className="gameboy-button text-sm">
                      💥 Contrasta (15 EN)
                    </button>
                  </div>
                </div>
              )}

              {/* ATTIVAZIONE Phase */}
              {currentPhase === 'attivazione' && (
                <div className="space-y-2">
                  <p className="text-xs text-[#7209B7] mb-2">🃏 Vuoi attivare qualcosa?</p>
                  <div className="grid grid-cols-2 gap-2">
                    <button onClick={() => doPhaseAction('attivazione', 'usa_carta')} disabled={actionLoading} className="gameboy-button text-sm">
                      🃏 Usa Carta
                    </button>
                    <button onClick={() => doPhaseAction('attivazione', 'usa_oggetto')} disabled={actionLoading} className="gameboy-button text-sm">
                      📦 Usa Oggetto
                    </button>
                    <button onClick={() => doPhaseAction('attivazione', 'salta')} disabled={actionLoading} className="gameboy-button text-sm col-span-2">
                      ⏭️ Salta Fase
                    </button>
                  </div>
                </div>
              )}

              {/* CONTRATTACCO Phase */}
              {currentPhase === 'contrattacco' && (
                <div className="space-y-2">
                  <p className="text-xs text-[#D00000] mb-2">⚔️ Contrattacca!</p>
                  <div className="grid grid-cols-2 gap-2">
                    <button onClick={() => doPhaseAction('contrattacco', 'pugno')} disabled={actionLoading || battle.player1.energia < 5} className="gameboy-button text-sm">
                      👊 Pugno (5 EN)
                    </button>
                    <button onClick={() => doPhaseAction('contrattacco', 'calcio')} disabled={actionLoading || battle.player1.energia < 5} className="gameboy-button text-sm">
                      🦵 Calcio (5 EN)
                    </button>
                    <button onClick={() => doPhaseAction('contrattacco', 'colpo_potente')} disabled={actionLoading || battle.player1.energia < 15} className="gameboy-button text-sm">
                      💪 Potente (15 EN)
                    </button>
                    <button onClick={() => doPhaseAction('contrattacco', 'tecnica_segreta')} disabled={actionLoading || battle.player1.energia < 25} className="gameboy-button text-sm">
                      ⚡ Segreta (25 EN)
                    </button>
                    <button onClick={() => doPhaseAction('contrattacco', 'riposo')} disabled={actionLoading} className="gameboy-button text-sm col-span-2">
                      💤 Riposa (+20 EN)
                    </button>
                  </div>
                </div>
              )}

              {/* End Turn Button */}
              <button 
                onClick={endTurn} 
                disabled={actionLoading}
                className="w-full mt-3 py-2 bg-[#2A9D8F] text-white rounded-lg font-bold"
              >
                ✅ Fine Turno
              </button>
            </div>
          )}

          {actionLoading && (
            <div className="text-center mt-2">
              <p className="font-pixel text-xs text-[#FFC300] animate-pulse">Eseguendo azione...</p>
            </div>
          )}

          {/* Battle Over */}
          {isBattleOver && (
            <motion.div 
              className="mt-4 text-center"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
            >
              <p className={`font-pirate text-3xl ${playerWon ? 'text-[#FFC300]' : 'text-[#D00000]'}`}>
                {playerWon ? '🎉 VITTORIA!' : '💀 SCONFITTA'}
              </p>
              
              {battle.rewards && (
                <div className="mt-3 p-3 bg-[#FFC300]/10 rounded-lg">
                  <p className="text-sm text-[#E3D5CA]">Ricompense:</p>
                  <p className="font-pirate text-lg text-[#FFC300]">
                    +{battle.rewards.exp_gained || battle.rewards.exp || 0} EXP
                  </p>
                  {battle.rewards.berry > 0 && (
                    <p className="text-[#D4AF37]">+฿{battle.rewards.berry}</p>
                  )}
                  {battle.rewards.ability_points_earned > 0 && (
                    <p className="text-[#2A9D8F]">+{battle.rewards.ability_points_earned} Punti Abilità 💪</p>
                  )}
                  {battle.rewards.leveled_up && (
                    <p className="text-[#7209B7] font-bold">🎉 LEVEL UP! → Lv.{battle.rewards.new_level}</p>
                  )}
                </div>
              )}
              
              <div className="flex gap-3 justify-center mt-4">
                <button onClick={() => setBattle(null)} className="glass px-6 py-2 rounded-lg text-[#E3D5CA]">
                  Nuova Battaglia
                </button>
                <button onClick={() => navigate('/dashboard')} className="btn-gold px-6 py-2 rounded-lg">
                  Dashboard
                </button>
              </div>
            </motion.div>
          )}
        </div>
      </div>

      {/* Character Stats Popup */}
      <AnimatePresence>
        {showStatsPopup && playerStats && (
          <motion.div
            className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowStatsPopup(false)}
          >
            <motion.div
              className="glass p-6 rounded-xl max-w-md w-full max-h-[80vh] overflow-y-auto"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              onClick={e => e.stopPropagation()}
            >
              <div className="flex justify-between items-center mb-4">
                <h2 className="font-pirate text-2xl text-[#FFC300]">{playerStats.player.nome}</h2>
                <button onClick={() => setShowStatsPopup(false)} className="text-[#E3D5CA]">✕</button>
              </div>
              
              <p className="text-[#D4AF37] mb-4">Livello Combattimento: {playerStats.player.livello_combattimento}</p>
              
              {/* Stats */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="bg-[#D00000]/20 p-3 rounded-lg text-center">
                  <p className="text-xs text-[#D00000]">FORZA</p>
                  <p className="text-2xl font-bold">{playerStats.player.forza}</p>
                </div>
                <div className="bg-[#00A8E8]/20 p-3 rounded-lg text-center">
                  <p className="text-xs text-[#00A8E8]">VELOCITÀ</p>
                  <p className="text-2xl font-bold">{playerStats.player.velocita}</p>
                </div>
                <div className="bg-[#2A9D8F]/20 p-3 rounded-lg text-center">
                  <p className="text-xs text-[#2A9D8F]">RESISTENZA</p>
                  <p className="text-2xl font-bold">{playerStats.player.resistenza}</p>
                </div>
                <div className="bg-[#7209B7]/20 p-3 rounded-lg text-center">
                  <p className="text-xs text-[#7209B7]">AGILITÀ</p>
                  <p className="text-2xl font-bold">{playerStats.player.agilita}</p>
                </div>
              </div>
              
              {/* Derived Stats */}
              <div className="flex justify-around mb-4">
                <div className="text-center">
                  <p className="text-xs text-[#E3D5CA]/70">ATK</p>
                  <p className="text-xl font-bold text-[#D00000]">{playerStats.player.attacco}</p>
                  <p className="text-xs text-[#E3D5CA]/50">FOR + VEL</p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-[#E3D5CA]/70">DEF</p>
                  <p className="text-xl font-bold text-[#00A8E8]">{playerStats.player.difesa}</p>
                  <p className="text-xs text-[#E3D5CA]/50">RES + AGI</p>
                </div>
              </div>
              
              {/* Haki */}
              {playerStats.player.haki && (
                <div className="mb-4">
                  <p className="text-sm text-[#D4AF37] mb-2">Haki:</p>
                  <div className="flex gap-2">
                    {playerStats.player.haki.osservazione && <span className="px-2 py-1 bg-[#00A8E8]/30 rounded text-xs">👁️ Osservazione</span>}
                    {playerStats.player.haki.armatura && <span className="px-2 py-1 bg-[#333]/50 rounded text-xs">⚫ Armatura</span>}
                    {playerStats.player.haki.conquistatore && <span className="px-2 py-1 bg-[#D4AF37]/30 rounded text-xs">👑 Conquistatore</span>}
                    {!playerStats.player.haki.osservazione && !playerStats.player.haki.armatura && !playerStats.player.haki.conquistatore && (
                      <span className="text-xs text-[#E3D5CA]/50">Nessun Haki risvegliato</span>
                    )}
                  </div>
                </div>
              )}
              
              {/* Battle Info */}
              <div className="border-t border-[#E3D5CA]/20 pt-3">
                <p className="text-xs text-[#E3D5CA]/70">Turno: {playerStats.battle_info.turno}</p>
                <p className="text-xs text-[#E3D5CA]/70">Fasi completate: {playerStats.battle_info.fasi_completate.join(', ') || 'Nessuna'}</p>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// ============ INVENTORY ============
const Inventory = ({ token, character }) => {
  const navigate = useNavigate();
  const authToken = token || localStorage.getItem('token');
  const [inventory, setInventory] = useState({ oggetti: [], armi: [], carte: {}, nave: null, berry: 0 });
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState(null);
  const [using, setUsing] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [activeTab, setActiveTab] = useState('oggetti');

  const fetchInventory = async () => {
    try {
      const res = await axios.get(`${API}/inventory`, { headers: { Authorization: `Bearer ${authToken}` } });
      setInventory(res.data);
    } catch (e) {
      console.error('Error fetching inventory:', e);
    }
    setLoading(false);
  };

  useEffect(() => {
    if (authToken) fetchInventory();
  }, [authToken]);

  const consumeItem = async (itemId) => {
    setUsing(true);
    setMessage({ type: '', text: '' });
    try {
      const res = await axios.post(`${API}/inventory/use-item`, { item_id: itemId }, { headers: { Authorization: `Bearer ${authToken}` } });
      setMessage({ type: 'success', text: `✅ ${res.data.message}. Effetti: ${res.data.effects_applied.join(', ')}` });
      setSelectedItem(null);
      fetchInventory(); // Refresh inventory
    } catch (e) {
      setMessage({ type: 'error', text: `❌ ${e.response?.data?.detail || 'Errore'}` });
    }
    setUsing(false);
  };

  const activateCard = async (cardId, categoria) => {
    setUsing(true);
    setMessage({ type: '', text: '' });
    try {
      const res = await axios.post(`${API}/cards/use`, { card_id: cardId }, { headers: { Authorization: `Bearer ${authToken}` } });
      setMessage({ type: 'success', text: `✅ ${res.data.message}. Effetti: ${res.data.effects_applied.join(', ') || 'Applicati'}` });
      setSelectedItem(null);
      fetchInventory(); // Refresh inventory
    } catch (e) {
      setMessage({ type: 'error', text: `❌ ${e.response?.data?.detail || 'Errore'}` });
    }
    setUsing(false);
  };

  const equipWeapon = async (weaponId) => {
    setUsing(true);
    try {
      const res = await axios.post(`${API}/inventory/equip-weapon`, { weapon_id: weaponId }, { headers: { Authorization: `Bearer ${authToken}` } });
      setMessage({ type: 'success', text: `✅ ${res.data.message}` });
      setSelectedItem(null);
      fetchInventory();
    } catch (e) {
      setMessage({ type: 'error', text: `❌ ${e.response?.data?.detail || 'Errore'}` });
    }
    setUsing(false);
  };

  // Count total items
  const totalOggetti = inventory.oggetti?.length || 0;
  const totalArmi = inventory.armi?.length || 0;
  const totalCarte = Object.values(inventory.carte || {}).reduce((acc, arr) => acc + (arr?.length || 0), 0);

  const tabs = [
    { id: 'oggetti', label: 'Consumabili', icon: FlaskConical, count: totalOggetti },
    { id: 'armi', label: 'Armi', icon: Sword, count: totalArmi },
    { id: 'carte', label: 'Carte', icon: CreditCard, count: totalCarte },
  ];

  if (loading) return <LoadingScreen />;

  return (
    <div className="min-h-screen bg-[#051923] p-4">
      {/* Header */}
      <div className="glass p-4 flex justify-between items-center mb-6">
        <button onClick={() => navigate('/dashboard')} className="text-[#E3D5CA] hover:text-[#FFC300]">
          <Home className="w-6 h-6" />
        </button>
        <h1 className="font-pirate text-2xl text-[#FFC300]">Inventario</h1>
        <div className="text-right">
          <p className="text-xs text-[#E3D5CA]/70">Berry</p>
          <p className="font-pirate text-lg text-[#D4AF37]">฿ {(inventory.berry || 0).toLocaleString()}</p>
        </div>
      </div>

      {/* Message */}
      {message.text && (
        <motion.div 
          initial={{ opacity: 0, y: -10 }} 
          animate={{ opacity: 1, y: 0 }}
          className={`mb-4 p-3 rounded-lg ${message.type === 'success' ? 'bg-[#2A9D8F]/20 border border-[#2A9D8F]' : 'bg-[#D00000]/20 border border-[#D00000]'}`}
        >
          <p className={message.type === 'success' ? 'text-[#2A9D8F]' : 'text-[#D00000]'}>{message.text}</p>
        </motion.div>
      )}

      {/* Ship Info */}
      {inventory.nave && (
        <div className="glass p-4 rounded-xl mb-4 flex items-center gap-3">
          <Ship className="w-8 h-8 text-[#00A8E8]" />
          <div>
            <p className="text-[#D4AF37] text-sm">La tua nave</p>
            <p className="text-[#E3D5CA] font-bold capitalize">{inventory.nave.replace('_', ' ')}</p>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg whitespace-nowrap transition-colors ${
              activeTab === tab.id 
                ? 'bg-[#2A9D8F] text-white' 
                : 'glass text-[#E3D5CA]'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
            {tab.count > 0 && (
              <span className={`text-xs px-2 py-0.5 rounded-full ${activeTab === tab.id ? 'bg-white/20' : 'bg-[#FFC300]/20 text-[#FFC300]'}`}>
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="space-y-3">
        {/* Consumabili */}
        {activeTab === 'oggetti' && (
          <>
            {totalOggetti === 0 ? (
              <div className="glass p-8 rounded-xl text-center">
                <FlaskConical className="w-12 h-12 text-[#E3D5CA]/30 mx-auto mb-3" />
                <p className="text-[#E3D5CA]/60">Nessun oggetto consumabile</p>
                <button onClick={() => navigate('/shop')} className="mt-4 btn-gold px-4 py-2 rounded-lg text-sm">
                  Vai al Negozio
                </button>
              </div>
            ) : (
              inventory.oggetti.map((item, idx) => (
                <motion.div
                  key={`${item.id}-${idx}`}
                  className={`glass p-4 rounded-xl cursor-pointer transition-all ${selectedItem?.id === item.id && selectedItem?.type === 'oggetto' ? 'border-2 border-[#2A9D8F]' : ''}`}
                  onClick={() => setSelectedItem({ ...item, type: 'oggetto' })}
                  whileHover={{ scale: 1.01 }}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-bold text-[#E3D5CA]">{item.name}</h3>
                      {item.effect && (
                        <p className="text-sm text-[#2A9D8F]">
                          {item.effect.vita && `+${item.effect.vita} Vita`}
                          {item.effect.energia && `+${item.effect.energia} Energia`}
                        </p>
                      )}
                    </div>
                    {selectedItem?.id === item.id && selectedItem?.type === 'oggetto' && (
                      <button
                        onClick={(e) => { e.stopPropagation(); consumeItem(item.id); }}
                        disabled={using}
                        className="btn-gold px-4 py-2 rounded-lg text-sm"
                      >
                        {using ? '...' : '🧪 Usa Ora'}
                      </button>
                    )}
                  </div>
                </motion.div>
              ))
            )}
          </>
        )}

        {/* Armi */}
        {activeTab === 'armi' && (
          <>
            {totalArmi === 0 ? (
              <div className="glass p-8 rounded-xl text-center">
                <Sword className="w-12 h-12 text-[#E3D5CA]/30 mx-auto mb-3" />
                <p className="text-[#E3D5CA]/60">Nessuna arma</p>
                <button onClick={() => navigate('/shop')} className="mt-4 btn-gold px-4 py-2 rounded-lg text-sm">
                  Vai al Negozio
                </button>
              </div>
            ) : (
              inventory.armi.map((arma, idx) => (
                <motion.div
                  key={`${arma.id}-${idx}`}
                  className={`glass p-4 rounded-xl cursor-pointer transition-all ${selectedItem?.id === arma.id && selectedItem?.type === 'arma' ? 'border-2 border-[#D00000]' : ''} ${arma.equipped ? 'border border-[#FFC300]' : ''}`}
                  onClick={() => setSelectedItem({ ...arma, type: 'arma' })}
                  whileHover={{ scale: 1.01 }}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-bold text-[#E3D5CA] flex items-center gap-2">
                        {arma.name}
                        {arma.equipped && <span className="text-xs bg-[#FFC300]/20 text-[#FFC300] px-2 py-0.5 rounded">Equipaggiata</span>}
                      </h3>
                      {arma.bonus_attacco && (
                        <p className="text-sm text-[#D00000]">+{arma.bonus_attacco} ATK</p>
                      )}
                    </div>
                    {selectedItem?.id === arma.id && selectedItem?.type === 'arma' && !arma.equipped && (
                      <button
                        onClick={(e) => { e.stopPropagation(); equipWeapon(arma.id); }}
                        disabled={using}
                        className="bg-[#D00000] text-white px-4 py-2 rounded-lg text-sm font-bold"
                      >
                        {using ? '...' : '⚔️ Equipaggia'}
                      </button>
                    )}
                  </div>
                </motion.div>
              ))
            )}
          </>
        )}

        {/* Carte */}
        {activeTab === 'carte' && (
          <>
            {totalCarte === 0 ? (
              <div className="glass p-8 rounded-xl text-center">
                <CreditCard className="w-12 h-12 text-[#E3D5CA]/30 mx-auto mb-3" />
                <p className="text-[#E3D5CA]/60">Nessuna carta</p>
                <button onClick={() => navigate('/shop')} className="mt-4 btn-gold px-4 py-2 rounded-lg text-sm">
                  Vai al Negozio
                </button>
              </div>
            ) : (
              Object.entries(inventory.carte || {}).map(([categoria, carte]) => (
                carte && carte.length > 0 && (
                  <div key={categoria} className="mb-4">
                    <h3 className="font-pirate text-lg text-[#7209B7] mb-2 capitalize">
                      {categoria === 'storytelling' ? '📖 Storytelling' : 
                       categoria === 'eventi' ? '🎭 Eventi' :
                       categoria === 'duello' ? '⚔️ Duello' : '💎 Risorse'}
                    </h3>
                    {carte.map((carta, idx) => (
                      <motion.div
                        key={`${carta.id}-${idx}`}
                        className={`glass p-4 rounded-xl mb-2 cursor-pointer transition-all ${selectedItem?.id === carta.id && selectedItem?.type === 'carta' ? 'border-2 border-[#7209B7]' : ''}`}
                        onClick={() => setSelectedItem({ ...carta, type: 'carta', categoria })}
                        whileHover={{ scale: 1.01 }}
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <h4 className="font-bold text-[#E3D5CA]">{carta.name}</h4>
                            {carta.effect && (
                              <p className="text-sm text-[#7209B7]">
                                {Object.entries(carta.effect).map(([k, v]) => `${k}: ${v}`).join(', ')}
                              </p>
                            )}
                          </div>
                          {selectedItem?.id === carta.id && selectedItem?.type === 'carta' && (
                            <button
                              onClick={(e) => { e.stopPropagation(); activateCard(carta.id, categoria); }}
                              disabled={using}
                              className="bg-[#7209B7] text-white px-4 py-2 rounded-lg text-sm font-bold"
                            >
                              {using ? '...' : '🃏 Usa Ora'}
                            </button>
                          )}
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )
              ))
            )}
          </>
        )}
      </div>
    </div>
  );
};

// ============ SHOP ============
const Shop = ({ token, character, isDemo }) => {
  const navigate = useNavigate();
  const authToken = token || localStorage.getItem('token');
  const [items, setItems] = useState({});
  const [buying, setBuying] = useState(null);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [currentBerry, setCurrentBerry] = useState(character?.berry || 0);

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await axios.get(`${API}/shop/items`, { headers: { Authorization: `Bearer ${authToken}` } });
        setItems(res.data.items);
      } catch (e) {}
    };
    if (authToken) fetch();
  }, [authToken]);

  useEffect(() => {
    setCurrentBerry(character?.berry || 0);
  }, [character]);

  const buy = async (itemId) => {
    setBuying(itemId);
    setMessage({ type: '', text: '' });
    try {
      const res = await axios.post(`${API}/shop/buy`, { item_id: itemId }, { headers: { Authorization: `Bearer ${authToken}` } });
      setMessage({ type: 'success', text: `✅ ${res.data.message}` });
      // Update local berry count
      const item = items[itemId];
      setCurrentBerry(prev => prev - item.price);
    } catch (e) {
      const errorMsg = e.response?.data?.detail || 'Errore durante l\'acquisto';
      setMessage({ type: 'error', text: `❌ ${errorMsg}` });
    }
    setBuying(null);
  };

  // Group items by type
  const groupedItems = Object.entries(items).reduce((acc, [id, item]) => {
    const tipo = item.tipo || 'consumabile';
    if (!acc[tipo]) acc[tipo] = [];
    acc[tipo].push({ id, ...item });
    return acc;
  }, {});

  const tipoLabels = {
    consumabile: '🧪 Consumabili',
    arma: '⚔️ Armi',
    nave: '🚢 Navi',
    carta: '🃏 Carte'
  };

  return (
    <div className="min-h-screen bg-[#051923] p-4">
      <div className="glass p-4 flex justify-between items-center mb-6">
        <button onClick={() => navigate('/dashboard')} className="text-[#E3D5CA]"><Home className="w-6 h-6" /></button>
        <h1 className="font-pirate text-2xl text-[#FFC300]">Negozio</h1>
        <div className="text-right">
          <p className="text-xs text-[#E3D5CA]/70">I tuoi Berry</p>
          <p className="font-pirate text-lg text-[#D4AF37]">฿ {currentBerry.toLocaleString()}</p>
        </div>
      </div>

      {message.text && (
        <motion.div 
          initial={{ opacity: 0, y: -10 }} 
          animate={{ opacity: 1, y: 0 }}
          className={`mb-4 p-3 rounded-lg ${message.type === 'success' ? 'bg-[#2A9D8F]/20 border border-[#2A9D8F]' : 'bg-[#D00000]/20 border border-[#D00000]'}`}
        >
          <p className={message.type === 'success' ? 'text-[#2A9D8F]' : 'text-[#D00000]'}>{message.text}</p>
        </motion.div>
      )}

      <div className="space-y-6">
        {Object.entries(groupedItems).map(([tipo, itemList]) => (
          <div key={tipo}>
            <h2 className="font-pirate text-xl text-[#E3D5CA] mb-3">{tipoLabels[tipo] || tipo}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {itemList.map((item) => {
                const canAfford = currentBerry >= item.price;
                return (
                  <motion.div 
                    key={item.id} 
                    className={`glass p-4 rounded-xl flex justify-between items-center ${!canAfford ? 'opacity-60' : ''}`}
                    whileHover={canAfford ? { scale: 1.01 } : {}}
                  >
                    <div>
                      <h3 className="font-bold text-[#E3D5CA]">{item.name}</h3>
                      <p className={`text-sm font-pirate ${canAfford ? 'text-[#D4AF37]' : 'text-[#D00000]'}`}>
                        ฿ {item.price.toLocaleString()}
                      </p>
                      {item.effect && (
                        <p className="text-xs text-[#E3D5CA]/60 mt-1">
                          {Object.entries(item.effect).map(([k, v]) => `${k}: ${v}`).join(', ')}
                        </p>
                      )}
                    </div>
                    <button 
                      onClick={() => buy(item.id)} 
                      disabled={!canAfford || buying === item.id}
                      className={`px-4 py-2 rounded-lg text-sm font-bold transition-colors ${
                        canAfford 
                          ? 'btn-gold' 
                          : 'bg-[#3E2723] text-[#E3D5CA]/50 cursor-not-allowed'
                      }`}
                    >
                      {buying === item.id ? '...' : canAfford ? 'Compra' : 'Non hai abbastanza'}
                    </button>
                  </motion.div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Narrative Panel */}
      <NarrativePanel 
        token={token} 
        character={character} 
        isDemo={isDemo}
        isExpanded={false}
        setIsExpanded={() => {}}
      />
    </div>
  );
};

// ============ NARRATIVE PANEL ============
const NarrativePanel = ({ token, character, isDemo, isExpanded, setIsExpanded }) => {
  const authToken = token || localStorage.getItem('token');
  const [activeTab, setActiveTab] = useState('narrative'); // narrative, chat_sea, chat_island, chat_zone
  const [messages, setMessages] = useState([]);
  const [chatRooms, setChatRooms] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [currentRoom, setCurrentRoom] = useState(null);
  const [loading, setLoading] = useState(false);
  const [pendingAction, setPendingAction] = useState(null);
  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);

  // Fetch available chat rooms based on character location
  const fetchChatRooms = useCallback(async () => {
    if (isDemo || !authToken) return;
    try {
      const res = await axios.get(`${API}/chat/rooms`, { headers: { Authorization: `Bearer ${authToken}` } });
      setChatRooms(res.data.rooms || []);
      // Set default room to sea chat
      if (res.data.rooms?.length > 0 && !currentRoom) {
        setCurrentRoom(res.data.rooms[0]);
      }
    } catch (e) {
      console.error('Error fetching chat rooms:', e);
    }
  }, [authToken, isDemo, currentRoom]);

  // Fetch chat history for current room
  const fetchChatHistory = useCallback(async (roomId) => {
    if (isDemo || !authToken || !roomId) return;
    try {
      const res = await axios.get(`${API}/chat/${roomId}/history?limit=50`, { headers: { Authorization: `Bearer ${authToken}` } });
      setMessages(res.data.messages || []);
    } catch (e) {
      console.error('Error fetching chat history:', e);
    }
  }, [authToken, isDemo]);

  // Connect to WebSocket for real-time chat
  const connectWebSocket = useCallback((roomId) => {
    if (isDemo || !authToken || !roomId) return;
    
    // Close existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${BACKEND_URL.replace(/^http/, 'ws')}/ws/chat/${roomId}?token=${authToken}`;
    
    try {
      wsRef.current = new WebSocket(wsUrl);
      
      wsRef.current.onopen = () => {
        console.log('WebSocket connected to room:', roomId);
      };
      
      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setMessages(prev => [...prev, data]);
      };
      
      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      wsRef.current.onclose = () => {
        console.log('WebSocket disconnected');
      };
    } catch (e) {
      console.error('WebSocket connection error:', e);
    }
  }, [authToken, isDemo]);

  useEffect(() => {
    fetchChatRooms();
  }, [fetchChatRooms]);

  useEffect(() => {
    if (currentRoom) {
      fetchChatHistory(currentRoom.room_id);
      connectWebSocket(currentRoom.room_id);
    }
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [currentRoom, fetchChatHistory, connectWebSocket]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Send chat message
  const sendMessage = async () => {
    if (!inputMessage.trim() || !currentRoom || isDemo) return;
    
    try {
      await axios.post(`${API}/chat/send`, {
        room_id: currentRoom.room_id,
        content: inputMessage
      }, { headers: { Authorization: `Bearer ${authToken}` } });
      
      setInputMessage('');
    } catch (e) {
      console.error('Error sending message:', e);
    }
  };

  // Execute narrative action
  const executeAction = async (action) => {
    if (isDemo) {
      // Demo action results
      const demoResults = {
        combat: { success: true, message: "Ti prepari al combattimento!", effects: [], next_event: { type: 'battle' } },
        flee: { success: Math.random() > 0.3, message: Math.random() > 0.3 ? "Sei fuggito!" : "Non riesci a fuggire!", effects: ["-10 Energia"] },
        collect: { success: true, message: "Hai raccolto 150 Berry!", effects: ["+150 Berry"] },
        examine: { success: true, message: "Hai trovato un oggetto nascosto!", effects: ["+50 EXP"] },
        leave: { success: true, message: "Prosegui il tuo viaggio...", effects: [] }
      };
      const result = demoResults[action.id] || demoResults.leave;
      addNarrativeMessage(result.message, result.success ? 'success' : 'warning');
      setPendingAction(null);
      return;
    }
    
    setLoading(true);
    try {
      const res = await axios.post(`${API}/narrative/action`, {
        action_id: action.id,
        event_type: pendingAction?.event_type,
        context: pendingAction?.context || {}
      }, { headers: { Authorization: `Bearer ${authToken}` } });
      
      addNarrativeMessage(res.data.message, res.data.success ? 'success' : 'warning');
      
      if (res.data.effects?.length > 0) {
        addNarrativeMessage(`Effetti: ${res.data.effects.join(', ')}`, 'effect');
      }
      
      // Handle next event (e.g., forced battle)
      if (res.data.next_event?.type === 'forced_battle') {
        addNarrativeMessage("Non c'è via di scampo... preparati a combattere!", 'danger');
      }
      
      setPendingAction(null);
    } catch (e) {
      console.error('Error executing action:', e);
      addNarrativeMessage("Errore nell'esecuzione dell'azione", 'error');
    }
    setLoading(false);
  };

  // Add narrative message locally
  const addNarrativeMessage = (content, type = 'narrative') => {
    setMessages(prev => [...prev, {
      message_id: `local-${Date.now()}`,
      type,
      username: type === 'error' ? '⚠️ Errore' : '📜 Narratore',
      content,
      timestamp: new Date().toISOString()
    }]);
  };

  // Trigger a narrative event (can be called from parent components)
  const triggerNarrativeEvent = async (eventType, context = {}) => {
    if (isDemo) {
      const demoNarratives = {
        monster_encounter: "Un rumore minaccioso rompe il silenzio! Un nemico ti ha individuato!",
        treasure_found: "Qualcosa luccica tra le rocce... potrebbe essere un tesoro!",
        arrival: `Approdi a ${context.location || 'questa isola'}. Una nuova avventura ti attende!`,
        zone_entry: `Ti addentri in ${context.location || 'questa zona'}. L'atmosfera cambia...`
      };
      
      addNarrativeMessage(demoNarratives[eventType] || "Un evento si verifica...", 'narrative');
      
      // Set pending action for events that have options
      const demoActions = {
        monster_encounter: [
          { id: 'combat', label: '⚔️ Combatti', color: 'red' },
          { id: 'flee', label: '🏃 Fuggi', color: 'yellow' }
        ],
        treasure_found: [
          { id: 'collect', label: '💰 Raccogli', color: 'gold' },
          { id: 'examine', label: '🔍 Esamina', color: 'blue' },
          { id: 'leave', label: '❌ Ignora', color: 'gray' }
        ]
      };
      
      if (demoActions[eventType]) {
        setPendingAction({ event_type: eventType, actions: demoActions[eventType], context });
      }
      return;
    }
    
    try {
      const res = await axios.post(`${API}/narrative/event-with-chat`, {
        event_type: eventType,
        context
      }, { headers: { Authorization: `Bearer ${authToken}` } });
      
      if (res.data.actions?.length > 0) {
        setPendingAction({
          event_type: eventType,
          actions: res.data.actions,
          context
        });
      }
    } catch (e) {
      console.error('Error triggering narrative event:', e);
    }
  };

  // Expose triggerNarrativeEvent to parent via ref
  useEffect(() => {
    window.narrativePanel = { triggerEvent: triggerNarrativeEvent };
  }, []);

  const getMessageStyle = (msg) => {
    switch (msg.type) {
      case 'narrative':
        return 'bg-[#7209B7]/20 border-l-4 border-[#7209B7] text-[#E3D5CA]';
      case 'success':
        return 'bg-[#2A9D8F]/20 border-l-4 border-[#2A9D8F] text-[#2A9D8F]';
      case 'warning':
        return 'bg-[#F59E0B]/20 border-l-4 border-[#F59E0B] text-[#F59E0B]';
      case 'danger':
        return 'bg-[#D00000]/20 border-l-4 border-[#D00000] text-[#D00000]';
      case 'effect':
        return 'bg-[#D4AF37]/20 border-l-4 border-[#D4AF37] text-[#D4AF37]';
      case 'error':
        return 'bg-[#D00000]/30 border-l-4 border-[#D00000] text-[#D00000]';
      case 'system':
        return 'bg-[#051923]/50 text-[#E3D5CA]/60 italic text-sm';
      default:
        return 'bg-[#003566]/20 text-[#E3D5CA]';
    }
  };

  const actionColors = {
    red: 'bg-[#D00000] hover:bg-[#D00000]/80',
    yellow: 'bg-[#F59E0B] hover:bg-[#F59E0B]/80 text-black',
    gold: 'bg-[#D4AF37] hover:bg-[#D4AF37]/80 text-black',
    blue: 'bg-[#00A8E8] hover:bg-[#00A8E8]/80',
    purple: 'bg-[#7209B7] hover:bg-[#7209B7]/80',
    gray: 'bg-[#6B7280] hover:bg-[#6B7280]/80'
  };

  // Demo messages
  useEffect(() => {
    if (isDemo && messages.length === 0) {
      setMessages([
        { message_id: '1', type: 'system', username: '⚙️ Sistema', content: 'Benvenuto nel pannello narrativo!', timestamp: new Date().toISOString() },
        { message_id: '2', type: 'narrative', username: '📜 Narratore', content: 'La tua avventura nei mari ha inizio. Cosa ti riserverà il destino?', timestamp: new Date().toISOString() }
      ]);
    }
  }, [isDemo]);

  return (
    <motion.div
      className="fixed bottom-0 left-0 right-0 z-40"
      initial={{ y: '100%' }}
      animate={{ y: isExpanded ? 0 : 'calc(100% - 48px)' }}
      transition={{ type: 'spring', damping: 25, stiffness: 200 }}
    >
      {/* Toggle Bar */}
      <div 
        className="glass h-12 flex items-center justify-between px-4 cursor-pointer border-t border-[#D4AF37]/30"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <MessageCircle className="w-5 h-5 text-[#D4AF37]" />
          <span className="font-pirate text-[#FFC300]">Narrazione & Chat</span>
          {pendingAction && (
            <span className="bg-[#D00000] text-white text-xs px-2 py-0.5 rounded-full animate-pulse">
              Azione richiesta!
            </span>
          )}
        </div>
        <motion.div animate={{ rotate: isExpanded ? 180 : 0 }}>
          <ChevronRight className="w-5 h-5 text-[#E3D5CA] rotate-90" />
        </motion.div>
      </div>

      {/* Panel Content */}
      <div className="glass h-64 flex flex-col border-t border-[#003566]/50">
        {/* Tabs */}
        <div className="flex border-b border-[#003566]/50 overflow-x-auto">
          <button
            onClick={() => setActiveTab('narrative')}
            className={`px-4 py-2 text-sm font-bold whitespace-nowrap ${activeTab === 'narrative' ? 'text-[#FFC300] border-b-2 border-[#FFC300]' : 'text-[#E3D5CA]/60 hover:text-[#E3D5CA]'}`}
          >
            📜 Narrazione
          </button>
          {chatRooms.map(room => (
            <button
              key={room.room_id}
              onClick={() => { setActiveTab('chat'); setCurrentRoom(room); }}
              className={`px-4 py-2 text-sm font-bold whitespace-nowrap ${activeTab === 'chat' && currentRoom?.room_id === room.room_id ? 'text-[#00A8E8] border-b-2 border-[#00A8E8]' : 'text-[#E3D5CA]/60 hover:text-[#E3D5CA]'}`}
            >
              {room.name}
            </button>
          ))}
          {isDemo && (
            <>
              <button
                onClick={() => setActiveTab('chat_sea')}
                className={`px-4 py-2 text-sm font-bold whitespace-nowrap ${activeTab === 'chat_sea' ? 'text-[#00A8E8] border-b-2 border-[#00A8E8]' : 'text-[#E3D5CA]/60 hover:text-[#E3D5CA]'}`}
              >
                🌊 East Blue
              </button>
              <button
                onClick={() => setActiveTab('chat_island')}
                className={`px-4 py-2 text-sm font-bold whitespace-nowrap ${activeTab === 'chat_island' ? 'text-[#2A9D8F] border-b-2 border-[#2A9D8F]' : 'text-[#E3D5CA]/60 hover:text-[#E3D5CA]'}`}
              >
                🏝️ Dawn Island
              </button>
            </>
          )}
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {messages.map((msg, i) => (
            <motion.div
              key={msg.message_id || i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className={`p-2 rounded ${getMessageStyle(msg)}`}
            >
              <div className="flex justify-between items-start mb-1">
                <span className="font-bold text-sm">{msg.username}</span>
                <span className="text-xs opacity-50">
                  {new Date(msg.timestamp).toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
              <p className="text-sm">{msg.content}</p>
            </motion.div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Action Buttons (when event has options) */}
        {pendingAction && (
          <div className="p-3 bg-[#051923]/80 border-t border-[#D4AF37]/30">
            <p className="text-xs text-[#E3D5CA]/70 mb-2">Scegli un'azione:</p>
            <div className="flex flex-wrap gap-2">
              {pendingAction.actions.map(action => (
                <motion.button
                  key={action.id}
                  onClick={() => executeAction(action)}
                  disabled={loading}
                  className={`px-4 py-2 rounded-lg font-bold text-sm text-white ${actionColors[action.color] || actionColors.gray}`}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  {loading ? '...' : action.label}
                </motion.button>
              ))}
            </div>
          </div>
        )}

        {/* Chat Input (only for chat tabs) */}
        {(activeTab === 'chat' || activeTab.startsWith('chat_')) && !pendingAction && (
          <div className="p-3 border-t border-[#003566]/50 flex gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder={isDemo ? "Chat disabilitata in demo..." : "Scrivi un messaggio..."}
              disabled={isDemo}
              className="flex-1 bg-[#051923] border border-[#003566] rounded-lg px-3 py-2 text-sm text-[#E3D5CA] placeholder-[#E3D5CA]/40 focus:outline-none focus:border-[#00A8E8]"
            />
            <button
              onClick={sendMessage}
              disabled={isDemo || !inputMessage.trim()}
              className="px-4 py-2 bg-[#00A8E8] text-white rounded-lg font-bold disabled:opacity-50"
            >
              Invia
            </button>
          </div>
        )}

        {/* Demo Event Trigger Buttons */}
        {isDemo && activeTab === 'narrative' && !pendingAction && (
          <div className="p-3 border-t border-[#003566]/50 flex gap-2 overflow-x-auto">
            <button
              onClick={() => triggerNarrativeEvent('monster_encounter', { enemy: 'Pirata Selvaggio' })}
              className="px-3 py-1.5 bg-[#D00000] text-white rounded-lg text-xs font-bold whitespace-nowrap"
            >
              🐙 Test Mostro
            </button>
            <button
              onClick={() => triggerNarrativeEvent('treasure_found', {})}
              className="px-3 py-1.5 bg-[#D4AF37] text-black rounded-lg text-xs font-bold whitespace-nowrap"
            >
              💎 Test Tesoro
            </button>
            <button
              onClick={() => triggerNarrativeEvent('arrival', { location: 'Dawn Island' })}
              className="px-3 py-1.5 bg-[#2A9D8F] text-white rounded-lg text-xs font-bold whitespace-nowrap"
            >
              ⚓ Test Arrivo
            </button>
            <button
              onClick={() => triggerNarrativeEvent('zone_entry', { location: 'Foosha Village' })}
              className="px-3 py-1.5 bg-[#7209B7] text-white rounded-lg text-xs font-bold whitespace-nowrap"
            >
              📍 Test Zona
            </button>
          </div>
        )}
      </div>
    </motion.div>
  );
};

// ============ MAIN ============
function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <AuthContext />
      </BrowserRouter>
    </div>
  );
}

export default App;
