import { useState, useEffect, useCallback, useRef } from "react";
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

  const login = (newToken, userData) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
    setUser(userData);
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

  return (
    <Routes>
      <Route path="/" element={user ? <Dashboard user={user} character={character} token={token} logout={logout} /> : <LandingPage />} />
      <Route path="/login" element={<LoginPage login={login} />} />
      <Route path="/register" element={<RegisterPage login={login} />} />
      <Route path="/dashboard" element={<Dashboard user={user} character={character} token={token} logout={logout} />} />
      <Route path="/create-character" element={<CharacterCreation token={token} setCharacter={setCharacter} />} />
      <Route path="/world-map" element={<WorldMap token={token} character={character} />} />
      <Route path="/battle" element={<BattleArena token={token} character={character} />} />
      <Route path="/character" element={<CharacterSheet token={token} character={character} setCharacter={setCharacter} />} />
      <Route path="/shop" element={<Shop token={token} character={character} />} />
      <Route path="/inventory" element={<Inventory token={token} character={character} />} />
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
        login(response.data.token, response.data.user);
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
        login(response.data.token, response.data.user);
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
                    start: 'Foosha Village'
                  },
                  { 
                    id: 'west_blue', 
                    name: 'West Blue', 
                    color: '#10B981',
                    icon: '🌿',
                    description: 'Mare occidentale, patria degli studiosi di Ohara e del potente regno di Kano.',
                    start: 'Regno di Ilisia'
                  },
                  { 
                    id: 'north_blue', 
                    name: 'North Blue', 
                    color: '#8B5CF6',
                    icon: '❄️',
                    description: 'Mare settentrionale, freddo e misterioso. Patria del Supernova Trafalgar Law.',
                    start: 'Regno di Lvneel'
                  },
                  { 
                    id: 'south_blue', 
                    name: 'South Blue', 
                    color: '#F59E0B',
                    icon: '☀️',
                    description: 'Mare meridionale, noto per le arti marziali e come luogo di nascita di Portgas D. Ace.',
                    start: 'Regno di Briss'
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
const Dashboard = ({ user, character, token, logout }) => {
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) navigate('/login');
    else if (!character) navigate('/create-character');
  }, [user, character, navigate]);

  if (!user || !character) return <LoadingScreen />;

  const menuItems = [
    { icon: Map, label: 'Mappa', path: '/world-map', color: '#00A8E8' },
    { icon: Swords, label: 'Arena', path: '/battle', color: '#D00000' },
    { icon: Backpack, label: 'Inventario', path: '/inventory', color: '#2A9D8F' },
    { icon: UserCircle, label: 'Personaggio', path: '/character', color: '#FFC300' },
    { icon: ShoppingBag, label: 'Negozio', path: '/shop', color: '#D4AF37' },
  ];

  return (
    <div className="min-h-screen bg-[#051923]">
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
        <div className="grid grid-cols-2 gap-4">
          {menuItems.map((item) => (
            <motion.button key={item.path} onClick={() => navigate(item.path)} className="glass p-6 rounded-xl text-left" whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <item.icon className="w-10 h-10 mb-3" style={{ color: item.color }} />
              <h3 className="font-pirate text-xl text-[#E3D5CA]">{item.label}</h3>
            </motion.button>
          ))}
        </div>
      </div>
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
const CharacterSheet = ({ token, character, setCharacter }) => {
  const navigate = useNavigate();
  const authToken = token || localStorage.getItem('token');
  const [showPrivate, setShowPrivate] = useState(true);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const handleDelete = async () => {
    try {
      await axios.delete(`${API}/characters/me`, { headers: { Authorization: `Bearer ${authToken}` } });
      localStorage.removeItem('token');
      window.location.href = '/';
    } catch (e) {}
  };

  if (!character) return <LoadingScreen />;

  return (
    <div className="min-h-screen bg-[#051923] p-4">
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

        {/* Combat Stats (PUBLIC) */}
        <div className="glass p-6 rounded-xl">
          <h3 className="font-pirate text-xl text-[#D00000] mb-4">Abilità di Combattimento</h3>
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
          <div className="grid grid-cols-4 gap-2 mt-4 text-center">
            <div><p className="text-xs text-[#D4AF37]">ATK</p><p className="text-[#E3D5CA] font-bold">{character.attacco}</p></div>
            <div><p className="text-xs text-[#D4AF37]">DEF</p><p className="text-[#E3D5CA] font-bold">{character.difesa}</p></div>
            <div><p className="text-xs text-[#D4AF37]">FOR</p><p className="text-[#E3D5CA]">{character.forza}</p></div>
            <div><p className="text-xs text-[#D4AF37]">VEL</p><p className="text-[#E3D5CA]">{character.velocita}</p></div>
            <div><p className="text-xs text-[#D4AF37]">RES</p><p className="text-[#E3D5CA]">{character.resistenza}</p></div>
            <div><p className="text-xs text-[#D4AF37]">AGI</p><p className="text-[#E3D5CA]">{character.agilita}</p></div>
            <div className="col-span-2"><p className="text-xs text-[#D4AF37]">Aspettativa Vita</p><p className="text-[#E3D5CA]">{character.aspettativa_vita}/{character.aspettativa_vita_max}</p></div>
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

// ============ WORLD MAP (Four Seas Navigation) ============
const WorldMap = ({ token, character }) => {
  const navigate = useNavigate();
  const authToken = token || localStorage.getItem('token');
  const [islands, setIslands] = useState([]);
  const [seaInfo, setSeaInfo] = useState({});
  const [currentIsland, setCurrentIsland] = useState(null);
  const [selectedIsland, setSelectedIsland] = useState(null);
  const [traveling, setTraveling] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [viewingSea, setViewingSea] = useState(null); // For viewing other seas
  const [viewingIslands, setViewingIslands] = useState([]);
  const [allSeas, setAllSeas] = useState({});

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

  const fetchIslands = async () => {
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
    try {
      const res = await axios.get(`${API}/world/seas`, { headers: { Authorization: `Bearer ${authToken}` } });
      setAllSeas(res.data.seas);
    } catch (e) {
      console.error('Error fetching seas:', e);
    }
  };

  const fetchSeaIslands = async (seaId) => {
    try {
      const res = await axios.get(`${API}/world/seas/${seaId}/islands`, { headers: { Authorization: `Bearer ${authToken}` } });
      setViewingIslands(res.data.islands);
      setViewingSea(seaId);
    } catch (e) {
      console.error('Error fetching sea islands:', e);
    }
  };

  useEffect(() => {
    if (authToken) {
      fetchIslands();
      fetchAllSeas();
    }
  }, [authToken]);

  const travelTo = async (islandId) => {
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

  const currentSeaColor = seaColors[character?.mare_corrente] || '#3B82F6';
  const displaySea = viewingSea || character?.mare_corrente;
  const displayIslands = viewingSea ? viewingIslands : islands;
  const isViewingOtherSea = viewingSea && viewingSea !== character?.mare_corrente;

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
          className={`mx-4 mb-4 p-3 rounded-lg ${message.type === 'success' ? 'bg-[#2A9D8F]/20 border border-[#2A9D8F]' : 'bg-[#D00000]/20 border border-[#D00000]'}`}
        >
          <p className={message.type === 'success' ? 'text-[#2A9D8F]' : 'text-[#D00000]'}>{message.text}</p>
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
      </div>

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
    </div>
  );
};

// ============ BATTLE ARENA (improved) ============
const BattleArena = ({ token, character }) => {
  const navigate = useNavigate();
  const authToken = token || localStorage.getItem('token');
  const [battle, setBattle] = useState(null);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  const startBattle = async (opponentId) => {
    setLoading(true);
    try {
      const res = await axios.post(`${API}/battle/start`, { opponent_type: 'npc', opponent_id: opponentId }, { headers: { Authorization: `Bearer ${authToken}` } });
      setBattle(res.data.battle);
    } catch (e) {
      console.error('Battle start error:', e);
    }
    setLoading(false);
  };

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
    marine_soldato: { name: 'Marine Soldato', desc: 'Un soldato della Marina', difficulty: '⭐' },
    pirata_novizio: { name: 'Pirata Novizio', desc: 'Un pirata alle prime armi', difficulty: '⭐' },
    marine_capitano: { name: 'Marine Capitano', desc: 'Un ufficiale della Marina', difficulty: '⭐⭐' },
    capitano_pirata: { name: 'Capitano Pirata', desc: 'Un temibile capitano pirata', difficulty: '⭐⭐⭐' }
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

  return (
    <div className="min-h-screen bg-[#0f0f1a] flex flex-col">
      {/* Turn indicator */}
      {!isBattleOver && (
        <div className={`p-2 text-center ${isPlayerTurn ? 'bg-[#2A9D8F]' : 'bg-[#D00000]'}`}>
          <p className="font-pixel text-sm text-white">
            {isPlayerTurn ? '🎯 È il TUO turno!' : '⏳ Turno avversario...'}
          </p>
        </div>
      )}

      {/* Enemy */}
      <div className="flex-1 p-4">
        <motion.div 
          className="gameboy-panel p-4 rounded-lg max-w-lg mx-auto"
          animate={!isPlayerTurn && !isBattleOver ? { x: [0, -5, 5, 0] } : {}}
          transition={{ duration: 0.3 }}
        >
          <div className="flex justify-between items-start">
            <h3 className="font-pixel text-xl text-[#D00000]">{battle.player2.nome}</h3>
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
      <div className="p-4 max-h-40 overflow-y-auto bg-[#000]/30">
        <AnimatePresence>
          {battle.log.slice(-5).map((l, i) => (
            <motion.p 
              key={`${battle.numero_turno}-${i}`}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="font-pixel text-sm text-[#E3D5CA]/80 mb-1"
            >
              &gt; {l}
            </motion.p>
          ))}
        </AnimatePresence>
      </div>

      {/* Player */}
      <div className="gameboy-panel p-4">
        <div className="max-w-lg mx-auto">
          <h3 className="font-pixel text-xl text-[#FFC300]">{battle.player1.nome}</h3>
          <div className="grid grid-cols-2 gap-2 mt-2">
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

          {!isBattleOver && (
            <div className="grid grid-cols-2 gap-2 mt-4">
              <button 
                onClick={() => doAction('attacco_base', 'Pugno')} 
                disabled={!isPlayerTurn || actionLoading} 
                className={`gameboy-button ${!isPlayerTurn ? 'opacity-50' : ''}`}
              >
                👊 Pugno
              </button>
              <button 
                onClick={() => doAction('attacco_base', 'Calcio')} 
                disabled={!isPlayerTurn || actionLoading} 
                className={`gameboy-button ${!isPlayerTurn ? 'opacity-50' : ''}`}
              >
                🦵 Calcio
              </button>
              <button 
                onClick={() => doAction('attacco_speciale', 'Colpo Speciale')} 
                disabled={!isPlayerTurn || actionLoading || battle.player1.energia < 20} 
                className={`gameboy-button ${(!isPlayerTurn || battle.player1.energia < 20) ? 'opacity-50' : ''}`}
              >
                ⚡ Speciale (20 EN)
              </button>
              <button 
                onClick={() => doAction('difesa', 'Difendi')} 
                disabled={!isPlayerTurn || actionLoading} 
                className={`gameboy-button ${!isPlayerTurn ? 'opacity-50' : ''}`}
              >
                🛡️ Difendi
              </button>
              <button 
                onClick={() => doAction('passa', 'Riposa')} 
                disabled={!isPlayerTurn || actionLoading} 
                className={`gameboy-button col-span-2 ${!isPlayerTurn ? 'opacity-50' : ''}`}
              >
                💤 Riposa (+15 EN)
              </button>
            </div>
          )}

          {actionLoading && (
            <div className="text-center mt-2">
              <p className="font-pixel text-xs text-[#FFC300] animate-pulse">Eseguendo azione...</p>
            </div>
          )}

          {isBattleOver && (
            <motion.div 
              className="mt-4 text-center"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
            >
              <p className={`font-pirate text-3xl ${playerWon ? 'text-[#FFC300]' : 'text-[#D00000]'}`}>
                {playerWon ? '🎉 VITTORIA!' : '💀 SCONFITTA'}
              </p>
              
              {playerWon && battle.rewards && (
                <div className="mt-3 p-3 bg-[#FFC300]/10 rounded-lg">
                  <p className="text-sm text-[#E3D5CA]">Ricompense:</p>
                  <p className="font-pirate text-lg text-[#FFC300]">
                    +{battle.rewards.exp} EXP • +฿{battle.rewards.berry}
                  </p>
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

  const useItem = async (itemId) => {
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

  const useCard = async (cardId, categoria) => {
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
                        onClick={(e) => { e.stopPropagation(); useItem(item.id); }}
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
                              onClick={(e) => { e.stopPropagation(); useCard(carta.id, categoria); }}
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
const Shop = ({ token, character }) => {
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
    </div>
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
