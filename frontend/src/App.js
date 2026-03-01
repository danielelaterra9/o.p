import { useState, useEffect, useCallback, useRef } from "react";
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import "@/App.css";

// Icons
import { 
  Anchor, Map, Swords, Users, Package, User, Skull, Shield, Heart, 
  Zap, ChevronRight, Star, Crown, Compass, LogOut, Dice6, Ship,
  MessageCircle, ShoppingBag, Scroll, Target, Settings, Home,
  MapPin, Waves, Wind, Send, X, Play, Square, Clock
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
    // CRITICAL: Skip auth check if returning from OAuth
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
      
      // Try to get character
      try {
        const charResponse = await axios.get(`${API}/characters/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setCharacter(charResponse.data);
      } catch (e) {
        // No character yet
      }
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

// ============ LOADING SCREEN ============
const LoadingScreen = () => (
  <div className="min-h-screen bg-[#051923] flex items-center justify-center">
    <motion.div
      animate={{ rotate: 360 }}
      transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
    >
      <Compass className="w-16 h-16 text-[#FFC300]" />
    </motion.div>
  </div>
);

// ============ APP ROUTER ============
const AppRouter = ({ user, character, setCharacter, token, login, logout }) => {
  const location = useLocation();
  
  // Handle OAuth callback
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
      <Route path="/island" element={<IslandExplorer token={token} character={character} />} />
      <Route path="/battle/:battleId" element={<BattleArena token={token} character={character} />} />
      <Route path="/battle" element={<BattleArena token={token} character={character} />} />
      <Route path="/character" element={<CharacterSheet token={token} character={character} />} />
      <Route path="/cards" element={<CardCollection token={token} character={character} />} />
      <Route path="/shop" element={<Shop token={token} character={character} />} />
    </Routes>
  );
};

// ============ AUTH CALLBACK ============
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
          const response = await axios.get(`${API}/auth/session?session_id=${sessionId}`, {
            withCredentials: true
          });
          login(response.data.session_token || sessionId, response.data);
          navigate('/dashboard', { replace: true });
        } catch (error) {
          console.error('Auth error:', error);
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
    <div className="min-h-screen bg-ocean relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-[#051923]/80 to-[#051923]" />
      
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center p-8">
        <motion.div
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-12"
        >
          <h1 className="font-pirate text-6xl md:text-8xl text-[#FFC300] mb-4 drop-shadow-lg">
            The Grand Line
          </h1>
          <h2 className="font-pirate text-2xl md:text-4xl text-[#E3D5CA] mb-4">
            Architect
          </h2>
          <p className="text-[#E3D5CA]/80 text-lg max-w-lg mx-auto">
            Crea il tuo pirata, esplora il Grand Line, combatti nemici epici e diventa il Re dei Pirati!
          </p>
        </motion.div>

        <motion.div 
          className="flex flex-col gap-4 w-full max-w-sm"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
        >
          <motion.button
            onClick={() => navigate('/register')}
            className="btn-gold py-4 px-8 text-lg font-pirate rounded-lg"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            data-testid="start-adventure-btn"
          >
            Inizia l'Avventura
          </motion.button>
          
          <motion.button
            onClick={() => navigate('/login')}
            className="bg-[#3E2723] text-[#E3D5CA] py-3 px-8 rounded-lg border-2 border-[#D4AF37] font-bold"
            whileHover={{ scale: 1.02 }}
            data-testid="login-btn"
          >
            Accedi
          </motion.button>

          <motion.button
            onClick={() => {
              // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
              const redirectUrl = window.location.origin + '/dashboard';
              window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
            }}
            className="glass py-3 px-8 rounded-lg text-[#E3D5CA] font-medium flex items-center justify-center gap-2"
            whileHover={{ scale: 1.02 }}
            data-testid="google-login-btn"
          >
            <img src="https://www.google.com/favicon.ico" alt="Google" className="w-5 h-5" />
            Accedi con Google
          </motion.button>
        </motion.div>
      </div>
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
      const response = await axios.post(`${API}/auth/login`, { email, password });
      login(response.data.token, response.data.user);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Errore durante il login');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-[#051923] flex items-center justify-center p-4">
      <motion.div 
        className="glass p-8 rounded-xl w-full max-w-md"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
      >
        <h1 className="font-pirate text-3xl text-[#FFC300] mb-6 text-center">Accedi</h1>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            className="input-dark w-full rounded-lg"
            data-testid="login-email"
            required
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            className="input-dark w-full rounded-lg"
            data-testid="login-password"
            required
          />
          
          {error && <p className="text-[#D00000] text-sm">{error}</p>}
          
          <button
            type="submit"
            disabled={loading}
            className="btn-gold w-full py-3 rounded-lg font-pirate"
            data-testid="login-submit"
          >
            {loading ? 'Caricamento...' : 'Accedi'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => {
              // REMINDER: DO NOT HARDCODE THE URL
              const redirectUrl = window.location.origin + '/dashboard';
              window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
            }}
            className="text-[#00A8E8] hover:underline flex items-center justify-center gap-2 mx-auto"
          >
            <img src="https://www.google.com/favicon.ico" alt="Google" className="w-4 h-4" />
            Accedi con Google
          </button>
          
          <p className="mt-4 text-[#E3D5CA]/60">
            Non hai un account?{' '}
            <button onClick={() => navigate('/register')} className="text-[#FFC300] hover:underline">
              Registrati
            </button>
          </p>
        </div>
      </motion.div>
    </div>
  );
};

// ============ REGISTER PAGE ============
const RegisterPage = ({ login }) => {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/auth/register`, { name, email, password });
      login(response.data.token, response.data.user);
      navigate('/create-character');
    } catch (err) {
      setError(err.response?.data?.detail || 'Errore durante la registrazione');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-[#051923] flex items-center justify-center p-4">
      <motion.div 
        className="glass p-8 rounded-xl w-full max-w-md"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
      >
        <h1 className="font-pirate text-3xl text-[#FFC300] mb-6 text-center">Registrati</h1>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Nome Capitano"
            className="input-dark w-full rounded-lg"
            data-testid="register-name"
            required
          />
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            className="input-dark w-full rounded-lg"
            data-testid="register-email"
            required
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            className="input-dark w-full rounded-lg"
            data-testid="register-password"
            required
          />
          
          {error && <p className="text-[#D00000] text-sm">{error}</p>}
          
          <button
            type="submit"
            disabled={loading}
            className="btn-gold w-full py-3 rounded-lg font-pirate"
            data-testid="register-submit"
          >
            {loading ? 'Caricamento...' : 'Crea Account'}
          </button>
        </form>

        <p className="mt-4 text-center text-[#E3D5CA]/60">
          Hai già un account?{' '}
          <button onClick={() => navigate('/login')} className="text-[#FFC300] hover:underline">
            Accedi
          </button>
        </p>
      </motion.div>
    </div>
  );
};

// ============ DASHBOARD ============
const Dashboard = ({ user, character, token, logout }) => {
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      navigate('/login');
    } else if (!character) {
      navigate('/create-character');
    }
  }, [user, character, navigate]);

  if (!user || !character) return <LoadingScreen />;

  const menuItems = [
    { icon: Map, label: 'Mappa Mondo', path: '/world-map', color: '#00A8E8' },
    { icon: MapPin, label: 'Esplora Isola', path: '/island', color: '#2A9D8F' },
    { icon: Swords, label: 'Arena', path: '/battle', color: '#D00000' },
    { icon: User, label: 'Personaggio', path: '/character', color: '#FFC300' },
    { icon: Scroll, label: 'Carte', path: '/cards', color: '#7209B7' },
    { icon: ShoppingBag, label: 'Negozio', path: '/shop', color: '#D4AF37' },
  ];

  return (
    <div className="min-h-screen bg-wood">
      <div className="absolute inset-0 bg-[#051923]/70" />
      
      <div className="relative z-10 p-4 md:p-8">
        {/* Header */}
        <div className="flex justify-between items-start mb-8">
          <div>
            <h1 className="font-pirate text-3xl md:text-4xl text-[#FFC300]">Benvenuto, {character.name}</h1>
            <p className="text-[#E3D5CA]/70">{character.title} • Lv.{character.level}</p>
          </div>
          <button
            onClick={logout}
            className="glass p-3 rounded-lg text-[#E3D5CA] hover:text-[#D00000] transition-colors"
            data-testid="logout-btn"
          >
            <LogOut className="w-6 h-6" />
          </button>
        </div>

        {/* Stats Bar */}
        <div className="glass p-4 rounded-xl mb-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Heart className="w-4 h-4 text-[#D00000]" />
                <span className="text-sm text-[#E3D5CA]/70">HP</span>
              </div>
              <div className="hp-bar">
                <div className="hp-bar-fill bg-[#D00000]" style={{ width: `${(character.hp / character.max_hp) * 100}%` }} />
              </div>
              <span className="text-xs text-[#E3D5CA]">{character.hp}/{character.max_hp}</span>
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Zap className="w-4 h-4 text-[#00A8E8]" />
                <span className="text-sm text-[#E3D5CA]/70">Energia</span>
              </div>
              <div className="hp-bar">
                <div className="hp-bar-fill bg-[#00A8E8]" style={{ width: `${(character.energy / character.max_energy) * 100}%` }} />
              </div>
              <span className="text-xs text-[#E3D5CA]">{character.energy}/{character.max_energy}</span>
            </div>
            <div className="text-center">
              <p className="text-xs text-[#E3D5CA]/70">Taglia</p>
              <p className="font-pirate text-xl text-[#FFC300]">{character.bounty?.toLocaleString()} B</p>
            </div>
            <div className="text-center">
              <p className="text-xs text-[#E3D5CA]/70">Isola</p>
              <p className="font-pirate text-lg text-[#E3D5CA]">{character.current_island}</p>
            </div>
          </div>
        </div>

        {/* Menu Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {menuItems.map((item) => (
            <motion.button
              key={item.path}
              onClick={() => navigate(item.path)}
              className="glass p-6 rounded-xl text-left hover:border-[#D4AF37] transition-colors"
              whileHover={{ scale: 1.02, y: -4 }}
              whileTap={{ scale: 0.98 }}
              data-testid={`menu-${item.label.toLowerCase().replace(' ', '-')}`}
            >
              <item.icon className="w-10 h-10 mb-3" style={{ color: item.color }} />
              <h3 className="font-pirate text-xl text-[#E3D5CA]">{item.label}</h3>
            </motion.button>
          ))}
        </div>

        {/* Quick Info */}
        {character.ship && (
          <div className="glass p-4 rounded-xl mt-6 flex items-center gap-4">
            <Ship className="w-8 h-8 text-[#D4AF37]" />
            <div>
              <p className="text-sm text-[#E3D5CA]/70">La tua nave</p>
              <p className="font-pirate text-[#FFC300]">{character.ship}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// ============ CHARACTER CREATION ============
const CharacterCreation = ({ token, setCharacter }) => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [charData, setCharData] = useState({
    name: '',
    title: 'Aspirante Pirata',
    body_type: 'normal',
    hair_color: '#3E2723',
    outfit: 'pirate',
    race: 'human',
    fighting_style: 'brawler',
    devil_fruit: null
  });
  const [loading, setLoading] = useState(false);

  const bodyTypes = [
    { id: 'slim', label: 'Agile', desc: '+10 ATK, +15 SPD, -5 DEF' },
    { id: 'normal', label: 'Equilibrato', desc: 'Stats bilanciati' },
    { id: 'muscular', label: 'Forte', desc: '+5 ATK, +10 DEF' },
    { id: 'giant', label: 'Gigante', desc: '+15 ATK, +15 DEF, -10 SPD' }
  ];

  const races = [
    { id: 'human', label: 'Umano' },
    { id: 'fishman', label: 'Uomo Pesce' },
    { id: 'mink', label: 'Mink' },
    { id: 'longarm', label: 'Braccialunghe' }
  ];

  const fightingStyles = [
    { id: 'brawler', label: 'Lottatore', desc: 'Pugni e calci' },
    { id: 'swordsman', label: 'Spadaccino', desc: 'Maestro della spada' },
    { id: 'shooter', label: 'Tiratore', desc: 'Armi da fuoco' },
    { id: 'martial_artist', label: 'Artista Marziale', desc: 'Arti marziali' }
  ];

  const devilFruits = [
    { id: null, name: 'Nessuno', type: '-', desc: 'Può nuotare' },
    { id: 'gomu_gomu', name: 'Gomu Gomu', type: 'Paramisha', desc: 'Corpo di gomma' },
    { id: 'mera_mera', name: 'Mera Mera', type: 'Rogia', desc: 'Potere del fuoco' },
    { id: 'hito_hito', name: 'Hito Hito', type: 'Zoan', desc: 'Trasformazione' },
    { id: 'ope_ope', name: 'Ope Ope', type: 'Paramisha', desc: 'Room - Controllo spaziale' }
  ];

  const hairColors = ['#3E2723', '#FFD700', '#FF6B35', '#1a1a1a', '#D00000', '#00A8E8', '#2A9D8F', '#7209B7'];

  const handleCreate = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/characters`, charData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCharacter(response.data);
      navigate('/dashboard');
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-[#051923] p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="font-pirate text-4xl text-[#FFC300] mb-8 text-center">Crea il Tuo Pirata</h1>

        {/* Progress */}
        <div className="flex justify-center gap-2 mb-8">
          {[1, 2, 3, 4].map((s) => (
            <div
              key={s}
              className={`w-3 h-3 rounded-full ${s === step ? 'bg-[#FFC300]' : s < step ? 'bg-[#2A9D8F]' : 'bg-[#3E2723]'}`}
            />
          ))}
        </div>

        <AnimatePresence mode="wait">
          {/* Step 1: Name & Title */}
          {step === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              className="glass p-8 rounded-xl"
            >
              <h2 className="font-pirate text-2xl text-[#E3D5CA] mb-6">Identità</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-[#D4AF37] mb-2">Nome Pirata</label>
                  <input
                    type="text"
                    value={charData.name}
                    onChange={(e) => setCharData({ ...charData, name: e.target.value })}
                    placeholder="Es: Monkey D. Rufy"
                    className="input-dark w-full rounded-lg"
                    data-testid="char-name"
                  />
                </div>
                <div>
                  <label className="block text-[#D4AF37] mb-2">Titolo</label>
                  <input
                    type="text"
                    value={charData.title}
                    onChange={(e) => setCharData({ ...charData, title: e.target.value })}
                    placeholder="Es: Il Futuro Re dei Pirati"
                    className="input-dark w-full rounded-lg"
                  />
                </div>
              </div>
              <button
                onClick={() => setStep(2)}
                disabled={!charData.name}
                className="btn-gold w-full py-3 rounded-lg mt-6 font-pirate"
              >
                Continua <ChevronRight className="inline w-5 h-5" />
              </button>
            </motion.div>
          )}

          {/* Step 2: Body & Race */}
          {step === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              className="glass p-8 rounded-xl"
            >
              <h2 className="font-pirate text-2xl text-[#E3D5CA] mb-6">Aspetto</h2>
              
              <div className="mb-6">
                <label className="block text-[#D4AF37] mb-3">Tipo Corpo</label>
                <div className="grid grid-cols-2 gap-3">
                  {bodyTypes.map((type) => (
                    <button
                      key={type.id}
                      onClick={() => setCharData({ ...charData, body_type: type.id })}
                      className={`p-4 rounded-lg border-2 transition-colors ${charData.body_type === type.id ? 'border-[#FFC300] bg-[#FFC300]/10' : 'border-[#3E2723]'}`}
                    >
                      <span className="block font-bold text-[#E3D5CA]">{type.label}</span>
                      <span className="text-xs text-[#00A8E8]">{type.desc}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div className="mb-6">
                <label className="block text-[#D4AF37] mb-3">Razza</label>
                <div className="grid grid-cols-2 gap-3">
                  {races.map((race) => (
                    <button
                      key={race.id}
                      onClick={() => setCharData({ ...charData, race: race.id })}
                      className={`p-3 rounded-lg border-2 transition-colors ${charData.race === race.id ? 'border-[#FFC300] bg-[#FFC300]/10' : 'border-[#3E2723]'}`}
                    >
                      <span className="text-[#E3D5CA]">{race.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div className="mb-6">
                <label className="block text-[#D4AF37] mb-3">Colore Capelli</label>
                <div className="flex gap-3 flex-wrap">
                  {hairColors.map((color) => (
                    <button
                      key={color}
                      onClick={() => setCharData({ ...charData, hair_color: color })}
                      className={`w-10 h-10 rounded-full border-4 transition-transform ${charData.hair_color === color ? 'border-[#FFC300] scale-110' : 'border-transparent'}`}
                      style={{ backgroundColor: color }}
                    />
                  ))}
                </div>
              </div>

              <div className="flex gap-4">
                <button onClick={() => setStep(1)} className="glass px-6 py-3 rounded-lg text-[#E3D5CA]">Indietro</button>
                <button onClick={() => setStep(3)} className="btn-gold flex-1 py-3 rounded-lg font-pirate">
                  Continua <ChevronRight className="inline w-5 h-5" />
                </button>
              </div>
            </motion.div>
          )}

          {/* Step 3: Fighting Style */}
          {step === 3 && (
            <motion.div
              key="step3"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              className="glass p-8 rounded-xl"
            >
              <h2 className="font-pirate text-2xl text-[#E3D5CA] mb-6">Stile di Combattimento</h2>
              
              <div className="grid grid-cols-2 gap-4">
                {fightingStyles.map((style) => (
                  <button
                    key={style.id}
                    onClick={() => setCharData({ ...charData, fighting_style: style.id })}
                    className={`p-6 rounded-lg border-2 text-left transition-all ${charData.fighting_style === style.id ? 'border-[#D00000] bg-[#D00000]/10' : 'border-[#3E2723]'}`}
                  >
                    <Swords className={`w-8 h-8 mb-2 ${charData.fighting_style === style.id ? 'text-[#D00000]' : 'text-[#D4AF37]'}`} />
                    <span className="block font-bold text-[#E3D5CA]">{style.label}</span>
                    <span className="text-xs text-[#E3D5CA]/60">{style.desc}</span>
                  </button>
                ))}
              </div>

              <div className="flex gap-4 mt-6">
                <button onClick={() => setStep(2)} className="glass px-6 py-3 rounded-lg text-[#E3D5CA]">Indietro</button>
                <button onClick={() => setStep(4)} className="btn-gold flex-1 py-3 rounded-lg font-pirate">
                  Continua <ChevronRight className="inline w-5 h-5" />
                </button>
              </div>
            </motion.div>
          )}

          {/* Step 4: Devil Fruit */}
          {step === 4 && (
            <motion.div
              key="step4"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              className="glass p-8 rounded-xl"
            >
              <h2 className="font-pirate text-2xl text-[#E3D5CA] mb-6">
                <Star className="inline w-6 h-6 text-[#7209B7] mr-2" />
                Frutto del Diavolo
              </h2>
              
              <div className="space-y-3">
                {devilFruits.map((fruit) => (
                  <button
                    key={fruit.id || 'none'}
                    onClick={() => setCharData({ ...charData, devil_fruit: fruit.id })}
                    className={`w-full p-4 rounded-lg border-2 text-left flex justify-between items-center transition-all ${charData.devil_fruit === fruit.id ? 'border-[#7209B7] bg-[#7209B7]/10' : 'border-[#3E2723]'}`}
                  >
                    <div>
                      <span className="font-bold text-[#E3D5CA]">{fruit.name}</span>
                      <span className={`ml-2 text-xs px-2 py-1 rounded ${fruit.type === 'Rogia' ? 'bg-[#D00000]/30 text-[#D00000]' : fruit.type === 'Zoan' ? 'bg-[#2A9D8F]/30 text-[#2A9D8F]' : fruit.type === 'Paramisha' ? 'bg-[#7209B7]/30 text-[#00A8E8]' : 'bg-[#3E2723]'}`}>
                        {fruit.type}
                      </span>
                    </div>
                    <span className="text-sm text-[#E3D5CA]/60">{fruit.desc}</span>
                  </button>
                ))}
              </div>

              <div className="flex gap-4 mt-6">
                <button onClick={() => setStep(3)} className="glass px-6 py-3 rounded-lg text-[#E3D5CA]">Indietro</button>
                <button
                  onClick={handleCreate}
                  disabled={loading}
                  className="btn-gold flex-1 py-3 rounded-lg font-pirate"
                  data-testid="create-character-btn"
                >
                  {loading ? 'Creazione...' : 'Crea Personaggio'}
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

// ============ WORLD MAP ============
const WorldMap = ({ token, character }) => {
  const navigate = useNavigate();
  const [islands, setIslands] = useState([]);
  const [diceRolling, setDiceRolling] = useState(false);
  const [diceResult, setDiceResult] = useState(null);
  const [event, setEvent] = useState(null);

  useEffect(() => {
    const fetchIslands = async () => {
      try {
        const response = await axios.get(`${API}/world/islands`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setIslands(response.data.islands);
      } catch (err) {
        console.error(err);
      }
    };
    fetchIslands();
  }, [token]);

  const rollDice = async (destination) => {
    setDiceRolling(true);
    setDiceResult(null);
    
    try {
      const response = await axios.post(`${API}/world/roll-dice`, 
        { destination },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      
      setTimeout(() => {
        setDiceResult(response.data.dice_result);
        setEvent(response.data.event);
        setDiceRolling(false);
      }, 1000);
    } catch (err) {
      console.error(err);
      setDiceRolling(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#051923]">
      {/* Header */}
      <div className="glass p-4 flex justify-between items-center">
        <button onClick={() => navigate('/dashboard')} className="text-[#E3D5CA] hover:text-[#FFC300]">
          <Home className="w-6 h-6" />
        </button>
        <h1 className="font-pirate text-2xl text-[#FFC300]">Mappa del Grand Line</h1>
        <div className="w-6" />
      </div>

      {/* Map Container */}
      <div className="relative w-full h-[60vh] bg-parchment overflow-hidden m-4 rounded-xl border-4 border-[#3E2723]">
        <div className="absolute inset-0 bg-[#051923]/30" />
        
        {/* Sea Route Lines */}
        <svg className="absolute inset-0 w-full h-full" style={{ zIndex: 1 }}>
          <path
            d="M 10% 70% Q 25% 50% 40% 45% T 60% 40% T 85% 35% T 95% 30%"
            fill="none"
            stroke="#D4AF37"
            strokeWidth="3"
            strokeDasharray="10,5"
            opacity="0.6"
          />
        </svg>

        {/* Islands */}
        {islands.map((island) => (
          <motion.div
            key={island.id}
            className={`absolute map-node ${island.current ? 'active' : ''} ${!island.unlocked ? 'locked' : ''}`}
            style={{ left: `${island.x}%`, top: `${island.y}%` }}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: Math.random() * 0.5 }}
            onClick={() => island.unlocked && !island.current && rollDice(island.id)}
            data-testid={`island-${island.id}`}
          >
            <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 whitespace-nowrap">
              <p className={`text-xs font-bold ${island.current ? 'text-[#D00000]' : island.unlocked ? 'text-[#FFC300]' : 'text-[#3E2723]'}`}>
                {island.name}
              </p>
              <p className="text-xs text-[#3E2723]/60">{island.saga}</p>
            </div>
          </motion.div>
        ))}

        {/* Current Ship */}
        {character?.ship && (
          <motion.div
            className="absolute"
            style={{ left: `${islands.find(i => i.current)?.x || 10}%`, top: `${(islands.find(i => i.current)?.y || 70) - 5}%` }}
            animate={{ y: [0, -5, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <Ship className="w-8 h-8 text-[#3E2723]" />
          </motion.div>
        )}
      </div>

      {/* Controls */}
      <div className="p-4 space-y-4">
        {/* Dice */}
        <div className="glass p-6 rounded-xl flex items-center justify-center gap-8">
          <div className={`dice ${diceRolling ? 'rolling' : ''}`}>
            {diceResult || '?'}
          </div>
          
          <div className="text-center">
            <button
              onClick={() => rollDice('open_sea')}
              disabled={diceRolling || !character?.ship}
              className="btn-gold px-8 py-3 rounded-lg font-pirate"
              data-testid="roll-dice-btn"
            >
              <Dice6 className="inline w-5 h-5 mr-2" />
              Naviga in Mare Aperto
            </button>
            {!character?.ship && (
              <p className="text-[#D00000] text-sm mt-2">Hai bisogno di una nave!</p>
            )}
          </div>
        </div>

        {/* Event Display */}
        <AnimatePresence>
          {event && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="glass p-6 rounded-xl"
            >
              <h3 className="font-pirate text-xl text-[#FFC300] mb-2">{event.name}</h3>
              <p className="text-[#E3D5CA]/80 mb-4">{event.description}</p>
              
              {event.type === 'battle' && (
                <button
                  onClick={() => navigate('/battle')}
                  className="btn-gold px-6 py-2 rounded-lg"
                >
                  <Swords className="inline w-4 h-4 mr-2" />
                  Combatti!
                </button>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

// ============ ISLAND EXPLORER ============
const IslandExplorer = ({ token, character }) => {
  const navigate = useNavigate();
  const [zones, setZones] = useState({});
  const [currentZone, setCurrentZone] = useState(null);
  const [npcInteraction, setNpcInteraction] = useState(null);

  useEffect(() => {
    const fetchZones = async () => {
      try {
        const response = await axios.get(`${API}/island/zones`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setZones(response.data.zones);
      } catch (err) {
        console.error(err);
      }
    };
    fetchZones();
  }, [token]);

  const interactWithNpc = async (npcId, zone) => {
    try {
      const response = await axios.post(`${API}/island/interact-npc`, 
        { npc_id: npcId, zone },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      setNpcInteraction(response.data);
    } catch (err) {
      console.error(err);
    }
  };

  const zoneIcons = {
    dock: Ship,
    tavern: MessageCircle,
    market: ShoppingBag,
    plaza: Users,
    hospital: Heart,
    beach: Waves,
    forest: Wind,
    mansion: Crown
  };

  return (
    <div className="min-h-screen bg-[#051923]">
      {/* Header */}
      <div className="glass p-4 flex justify-between items-center">
        <button onClick={() => navigate('/dashboard')} className="text-[#E3D5CA] hover:text-[#FFC300]">
          <Home className="w-6 h-6" />
        </button>
        <h1 className="font-pirate text-2xl text-[#FFC300]">{character?.current_island || 'Isola'}</h1>
        <button onClick={() => navigate('/world-map')} className="text-[#E3D5CA] hover:text-[#FFC300]">
          <Map className="w-6 h-6" />
        </button>
      </div>

      <div className="p-4">
        {/* Zones Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {Object.entries(zones).map(([zoneId, zone]) => {
            const Icon = zoneIcons[zoneId] || MapPin;
            return (
              <motion.div
                key={zoneId}
                onClick={() => setCurrentZone({ id: zoneId, ...zone })}
                className={`zone-card ${currentZone?.id === zoneId ? 'border-[#FFC300]' : ''}`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                data-testid={`zone-${zoneId}`}
              >
                <Icon className="w-8 h-8 text-[#D4AF37] mb-2" />
                <h3 className="font-pirate text-lg text-[#E3D5CA]">{zone.name}</h3>
                <p className="text-xs text-[#E3D5CA]/60">{zone.description}</p>
              </motion.div>
            );
          })}
        </div>

        {/* Zone Details */}
        <AnimatePresence>
          {currentZone && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="glass p-6 rounded-xl"
            >
              <h2 className="font-pirate text-2xl text-[#FFC300] mb-4">{currentZone.name}</h2>
              <p className="text-[#E3D5CA]/80 mb-6">{currentZone.description}</p>
              
              <h3 className="text-[#D4AF37] mb-3">Personaggi Presenti:</h3>
              <div className="space-y-2">
                {currentZone.npcs?.map((npcId) => (
                  <button
                    key={npcId}
                    onClick={() => interactWithNpc(npcId, currentZone.id)}
                    className="w-full p-3 rounded-lg bg-[#3E2723]/50 hover:bg-[#3E2723] flex items-center gap-3 transition-colors"
                  >
                    <User className="w-6 h-6 text-[#D4AF37]" />
                    <span className="text-[#E3D5CA] capitalize">{npcId.replace('_', ' ')}</span>
                  </button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* NPC Interaction Modal */}
        <AnimatePresence>
          {npcInteraction && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50"
              onClick={() => setNpcInteraction(null)}
            >
              <motion.div
                initial={{ scale: 0.9 }}
                animate={{ scale: 1 }}
                className="glass p-6 rounded-xl max-w-md w-full"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex justify-between items-start mb-4">
                  <h3 className="font-pirate text-xl text-[#FFC300] capitalize">
                    {npcInteraction.npc_id?.replace('_', ' ')}
                  </h3>
                  <button onClick={() => setNpcInteraction(null)} className="text-[#E3D5CA]/60 hover:text-[#E3D5CA]">
                    <X className="w-5 h-5" />
                  </button>
                </div>
                
                <p className="text-[#E3D5CA] mb-6 italic">"{npcInteraction.interaction?.dialogue}"</p>
                
                {npcInteraction.interaction?.action === 'shop' && (
                  <button
                    onClick={() => navigate('/shop')}
                    className="btn-gold w-full py-3 rounded-lg"
                  >
                    <ShoppingBag className="inline w-4 h-4 mr-2" />
                    Apri Negozio
                  </button>
                )}
                
                {npcInteraction.interaction?.action === 'heal' && (
                  <button className="btn-gold w-full py-3 rounded-lg">
                    <Heart className="inline w-4 h-4 mr-2" />
                    Curati ({npcInteraction.interaction.cost} Berry)
                  </button>
                )}
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

// ============ BATTLE ARENA ============
const BattleArena = ({ token, character }) => {
  const navigate = useNavigate();
  const [battle, setBattle] = useState(null);
  const [loading, setLoading] = useState(false);
  const [narration, setNarration] = useState('');
  const [selectedAction, setSelectedAction] = useState(null);
  const [turnTimer, setTurnTimer] = useState(180);
  const [damageDisplay, setDamageDisplay] = useState(null);

  // Start battle with NPC
  const startBattle = async (opponentId) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/battle/start`, 
        { opponent_type: 'npc', opponent_id: opponentId },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      setBattle(response.data.battle);
      await getNarration(`La battaglia inizia contro ${response.data.battle.player2.name}!`);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  // Execute action
  const executeAction = async (actionType, actionName) => {
    if (!battle || battle.current_turn !== 'player1') return;

    try {
      const response = await axios.post(`${API}/battle/${battle.battle_id}/action`,
        { action_type: actionType, action_name: actionName },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      
      setBattle(response.data.battle);
      
      // Show damage
      if (response.data.result.damage > 0) {
        setDamageDisplay({ value: response.data.result.damage, target: 'enemy' });
        setTimeout(() => setDamageDisplay(null), 1000);
      }
      
      // Get narration
      await getNarration(response.data.result.log_entry);
      
      // NPC turn (simulated)
      if (!response.data.result.battle_ended && battle.player2.is_npc) {
        setTimeout(() => simulateNpcTurn(), 2000);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const simulateNpcTurn = async () => {
    // NPC makes a random action
    const actions = ['basic_attack', 'special_move'];
    const actionType = actions[Math.floor(Math.random() * actions.length)];
    const actionName = actionType === 'basic_attack' ? 'Attacco' : battle.player2.special_moves[0];
    
    try {
      // Simulate NPC action client-side for demo
      const damage = Math.floor(Math.random() * 15) + 10;
      
      setBattle(prev => ({
        ...prev,
        player1: { ...prev.player1, hp: Math.max(0, prev.player1.hp - damage) },
        current_turn: 'player1',
        turn_number: prev.turn_number + 1
      }));
      
      setDamageDisplay({ value: damage, target: 'player' });
      setTimeout(() => setDamageDisplay(null), 1000);
      
      await getNarration(`${battle.player2.name} usa ${actionName}! Infligge ${damage} danni!`);
    } catch (err) {
      console.error(err);
    }
  };

  const getNarration = async (action) => {
    try {
      const response = await axios.post(`${API}/ai/narrate-battle`,
        { context: `Battaglia tra ${character?.name} e ${battle?.player2?.name || 'nemico'}`, action },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      setNarration(response.data.narration);
    } catch (err) {
      setNarration(action);
    }
  };

  // Timer effect
  useEffect(() => {
    if (!battle || battle.status === 'finished') return;
    
    const timer = setInterval(() => {
      setTurnTimer((prev) => {
        if (prev <= 0) return 180;
        return prev - 1;
      });
    }, 1000);
    
    return () => clearInterval(timer);
  }, [battle]);

  const actions = [
    { type: 'movement', name: 'Avanza', icon: Target, desc: 'Muoviti verso il nemico', cost: 3 },
    { type: 'movement', name: 'Indietreggia', icon: Shield, desc: 'Aumenta distanza', cost: 3 },
    { type: 'basic_attack', name: 'Pugno', icon: Swords, desc: '10-20 danni', cost: 5 },
    { type: 'basic_attack', name: 'Calcio', icon: Swords, desc: '12-18 danni', cost: 5 },
    ...(character?.special_moves || []).map(move => ({
      type: 'special_move', name: move, icon: Star, desc: '20-40 danni', cost: 20
    })),
    { type: 'pass', name: 'Passa', icon: Clock, desc: 'Recupera energia', cost: 0 },
  ];

  if (!battle) {
    return (
      <div className="min-h-screen bg-[#051923] p-4">
        <div className="glass p-4 flex justify-between items-center mb-6">
          <button onClick={() => navigate('/dashboard')} className="text-[#E3D5CA] hover:text-[#FFC300]">
            <Home className="w-6 h-6" />
          </button>
          <h1 className="font-pirate text-2xl text-[#FFC300]">Arena di Combattimento</h1>
          <div className="w-6" />
        </div>

        <div className="text-center mb-8">
          <h2 className="font-pirate text-xl text-[#E3D5CA] mb-4">Scegli il tuo avversario</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            { id: 'marine_grunt', name: 'Marine Soldato', difficulty: 'Facile', bounty: 0 },
            { id: 'pirate_rookie', name: 'Pirata Novizio', difficulty: 'Facile', bounty: 5000000 },
            { id: 'marine_captain', name: 'Marine Capitano', difficulty: 'Medio', bounty: 0 },
            { id: 'pirate_captain', name: 'Capitano Pirata', difficulty: 'Difficile', bounty: 30000000 },
          ].map((opponent) => (
            <motion.button
              key={opponent.id}
              onClick={() => startBattle(opponent.id)}
              disabled={loading}
              className="wanted-poster p-6 text-left"
              whileHover={{ rotate: 0, scale: 1.02 }}
              initial={{ rotate: Math.random() * 4 - 2 }}
              data-testid={`opponent-${opponent.id}`}
            >
              <div className="relative z-10">
                <h3 className="font-pirate text-2xl text-[#8B0000] mb-1">WANTED</h3>
                <div className="w-full h-24 bg-[#D7C297] border-2 border-[#3E2723] mb-2 flex items-center justify-center">
                  <Skull className="w-12 h-12 text-[#3E2723]" />
                </div>
                <p className="font-pirate text-xl text-[#3E2723]">{opponent.name}</p>
                <p className="text-sm text-[#5D4037]">Difficoltà: {opponent.difficulty}</p>
                {opponent.bounty > 0 && (
                  <p className="font-pirate text-[#8B0000]">{opponent.bounty.toLocaleString()} Berry</p>
                )}
              </div>
            </motion.button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0f0f1a] flex flex-col">
      {/* Enemy Section */}
      <div className="flex-1 p-4 bg-gradient-to-b from-[#1a1a2e] to-[#0f0f1a] relative">
        <motion.div 
          className="gameboy-panel p-4 rounded-lg max-w-lg mx-auto"
          animate={damageDisplay?.target === 'enemy' ? { x: [-10, 10, -10, 0] } : {}}
        >
          <div className="flex justify-between items-center mb-4">
            <div>
              <h3 className="font-pixel text-2xl text-[#D00000]">{battle.player2.name}</h3>
              <p className="font-pixel text-sm text-[#E3D5CA]/60">
                {battle.player2.bounty > 0 ? `${battle.player2.bounty.toLocaleString()} B` : 'MARINE'}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-[#FFC300]" />
              <span className="font-pixel text-[#FFC300]">{Math.floor(turnTimer / 60)}:{(turnTimer % 60).toString().padStart(2, '0')}</span>
            </div>
          </div>
          
          <div className="hp-bar mb-2">
            <div 
              className="hp-bar-fill bg-[#D00000]" 
              style={{ width: `${(battle.player2.hp / battle.player2.max_hp) * 100}%` }}
            />
          </div>
          <p className="font-pixel text-sm text-[#E3D5CA]">HP: {battle.player2.hp}/{battle.player2.max_hp}</p>
        </motion.div>

        {/* Damage Display */}
        <AnimatePresence>
          {damageDisplay && (
            <motion.div
              className={`absolute font-pixel text-5xl ${damageDisplay.target === 'enemy' ? 'text-[#D00000] top-1/4 left-1/2' : 'text-[#D00000] bottom-1/4 left-1/2'}`}
              initial={{ opacity: 1, y: 0, scale: 1 }}
              animate={{ opacity: 0, y: -50, scale: 1.5 }}
              exit={{ opacity: 0 }}
              style={{ transform: 'translateX(-50%)' }}
            >
              -{damageDisplay.value}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Narration */}
      {narration && (
        <div className="chat-bubble narration mx-4 my-2">
          <p className="font-pixel text-lg">{narration}</p>
        </div>
      )}

      {/* Player Section */}
      <motion.div 
        className="gameboy-panel p-4"
        animate={damageDisplay?.target === 'player' ? { x: [-10, 10, -10, 0] } : {}}
      >
        <div className="max-w-lg mx-auto">
          {/* Player Stats */}
          <div className="flex items-center gap-4 mb-4">
            <Crown className="w-10 h-10 text-[#FFC300]" />
            <div className="flex-1">
              <h3 className="font-pixel text-xl text-[#FFC300]">{battle.player1.name}</h3>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <div className="hp-bar h-5">
                    <div 
                      className="hp-bar-fill bg-[#D00000]" 
                      style={{ width: `${(battle.player1.hp / battle.player1.max_hp) * 100}%` }}
                    />
                  </div>
                  <p className="font-pixel text-xs text-[#E3D5CA]">HP: {battle.player1.hp}/{battle.player1.max_hp}</p>
                </div>
                <div>
                  <div className="hp-bar h-5">
                    <div 
                      className="hp-bar-fill bg-[#00A8E8]" 
                      style={{ width: `${(battle.player1.energy / battle.player1.max_energy) * 100}%` }}
                    />
                  </div>
                  <p className="font-pixel text-xs text-[#E3D5CA]">EN: {battle.player1.energy}/{battle.player1.max_energy}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Action Grid */}
          <div className="grid grid-cols-2 gap-2">
            {actions.slice(0, 6).map((action) => (
              <button
                key={action.name}
                onClick={() => executeAction(action.type, action.name)}
                disabled={battle.current_turn !== 'player1' || battle.player1.energy < action.cost}
                className="gameboy-button text-left"
                data-testid={`action-${action.name.toLowerCase()}`}
              >
                <action.icon className="w-4 h-4 inline mr-2" />
                {action.name}
                {action.cost > 0 && <span className="text-xs ml-1">(-{action.cost})</span>}
              </button>
            ))}
          </div>

          {battle.current_turn !== 'player1' && (
            <p className="font-pixel text-center text-[#D00000] mt-4 animate-pulse">
              Turno del nemico...
            </p>
          )}
        </div>
      </motion.div>

      {/* Battle End */}
      {battle.status === 'finished' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-black/80 flex items-center justify-center z-50"
        >
          <div className="text-center">
            <h2 className="font-pirate text-5xl text-[#FFC300] mb-4">
              {battle.winner === 'player1' ? 'VITTORIA!' : 'SCONFITTA'}
            </h2>
            <button
              onClick={() => navigate('/dashboard')}
              className="btn-gold px-8 py-3 rounded-lg font-pirate"
            >
              Continua
            </button>
          </div>
        </motion.div>
      )}
    </div>
  );
};

// ============ CHARACTER SHEET ============
const CharacterSheet = ({ token, character }) => {
  const navigate = useNavigate();

  if (!character) return <LoadingScreen />;

  return (
    <div className="min-h-screen bg-[#051923] p-4">
      <div className="glass p-4 flex justify-between items-center mb-6">
        <button onClick={() => navigate('/dashboard')} className="text-[#E3D5CA] hover:text-[#FFC300]">
          <Home className="w-6 h-6" />
        </button>
        <h1 className="font-pirate text-2xl text-[#FFC300]">Scheda Personaggio</h1>
        <div className="w-6" />
      </div>

      <div className="max-w-2xl mx-auto space-y-6">
        {/* Wanted Poster */}
        <div className="wanted-poster p-8 mx-auto max-w-sm">
          <div className="relative z-10 text-center">
            <h2 className="font-pirate text-3xl text-[#8B0000] mb-1">WANTED</h2>
            <p className="text-sm text-[#5D4037] mb-4">DEAD OR ALIVE</p>
            
            <div className="w-full h-48 bg-[#D7C297] border-4 border-[#3E2723] mb-4 flex items-center justify-center">
              <User className="w-20 h-20 text-[#3E2723]" />
            </div>
            
            <h3 className="font-pirate text-2xl text-[#3E2723]">{character.name}</h3>
            <p className="text-[#5D4037]">{character.title}</p>
            
            <div className="border-t-2 border-dashed border-[#5D4037] mt-4 pt-4">
              <p className="font-pirate text-3xl text-[#8B0000]">
                {character.bounty?.toLocaleString()} <span className="text-xl">Berry</span>
              </p>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="glass p-6 rounded-xl">
          <h3 className="font-pirate text-xl text-[#FFC300] mb-4">Statistiche</h3>
          <div className="grid grid-cols-2 gap-4">
            {Object.entries(character.stats || {}).map(([stat, value]) => (
              <div key={stat}>
                <div className="flex justify-between mb-1">
                  <span className="text-[#E3D5CA] capitalize">{stat}</span>
                  <span className="text-[#FFC300]">{value}</span>
                </div>
                <div className="h-2 bg-[#3E2723] rounded-full">
                  <div 
                    className="h-full bg-[#D4AF37] rounded-full" 
                    style={{ width: `${Math.min(value, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Devil Fruit */}
        {character.devil_fruit && (
          <div className="glass p-6 rounded-xl">
            <h3 className="font-pirate text-xl text-[#7209B7] mb-2">
              <Star className="inline w-5 h-5 mr-2" />
              Frutto del Diavolo
            </h3>
            <p className="text-[#E3D5CA] capitalize">{character.devil_fruit.replace('_', ' ')}</p>
          </div>
        )}

        {/* Special Moves */}
        <div className="glass p-6 rounded-xl">
          <h3 className="font-pirate text-xl text-[#D00000] mb-4">Mosse Speciali</h3>
          <div className="space-y-2">
            {(character.special_moves || []).map((move, i) => (
              <div key={i} className="flex items-center gap-3 p-3 bg-[#3E2723]/50 rounded-lg">
                <Swords className="w-5 h-5 text-[#D4AF37]" />
                <span className="text-[#E3D5CA]">{move}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Inventory Preview */}
        <div className="glass p-6 rounded-xl">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-pirate text-xl text-[#FFC300]">Inventario</h3>
            <span className="text-sm text-[#E3D5CA]/60">{(character.inventory || []).length} oggetti</span>
          </div>
          <div className="grid grid-cols-6 gap-2">
            {[...Array(12)].map((_, i) => (
              <div key={i} className={`inventory-slot ${i >= (character.inventory || []).length ? 'empty' : ''}`}>
                {i < (character.inventory || []).length && (
                  <Package className="w-6 h-6 text-[#D4AF37]" />
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// ============ CARD COLLECTION ============
const CardCollection = ({ token, character }) => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('storytelling');

  const cardTypes = [
    { id: 'storytelling', label: 'Storytelling', color: '#00A8E8' },
    { id: 'events', label: 'Eventi', color: '#2A9D8F' },
    { id: 'duel', label: 'Duello', color: '#D00000' },
    { id: 'resources', label: 'Risorse', color: '#FFC300' },
  ];

  const cards = character?.cards || {};

  return (
    <div className="min-h-screen bg-[#051923] p-4">
      <div className="glass p-4 flex justify-between items-center mb-6">
        <button onClick={() => navigate('/dashboard')} className="text-[#E3D5CA] hover:text-[#FFC300]">
          <Home className="w-6 h-6" />
        </button>
        <h1 className="font-pirate text-2xl text-[#FFC300]">Collezione Carte</h1>
        <div className="w-6" />
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {cardTypes.map((type) => (
          <button
            key={type.id}
            onClick={() => setActiveTab(type.id)}
            className={`px-4 py-2 rounded-lg whitespace-nowrap transition-colors ${activeTab === type.id ? 'bg-[#D4AF37] text-[#3E2723]' : 'glass text-[#E3D5CA]'}`}
            style={activeTab === type.id ? { backgroundColor: type.color } : {}}
          >
            {type.label}
          </button>
        ))}
      </div>

      {/* Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {(cards[activeTab] || []).length > 0 ? (
          cards[activeTab].map((cardId, i) => (
            <motion.div
              key={`${cardId}-${i}`}
              className={`game-card ${activeTab} p-4`}
              whileHover={{ scale: 1.05, rotate: 2 }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
            >
              <div className="relative z-10">
                <div className="w-full h-24 bg-[#D7C297] rounded mb-3 flex items-center justify-center">
                  <Scroll className="w-10 h-10 text-[#3E2723]" />
                </div>
                <h4 className="font-pirate text-lg text-[#3E2723]">{cardId}</h4>
                <p className="text-xs text-[#5D4037]">Carta {activeTab}</p>
              </div>
            </motion.div>
          ))
        ) : (
          <div className="col-span-full text-center py-12">
            <Scroll className="w-16 h-16 text-[#3E2723] mx-auto mb-4" />
            <p className="text-[#E3D5CA]/60">Nessuna carta in questa categoria</p>
            <p className="text-sm text-[#E3D5CA]/40">Completa eventi e missioni per ottenere carte!</p>
          </div>
        )}
      </div>
    </div>
  );
};

// ============ SHOP ============
const Shop = ({ token, character }) => {
  const navigate = useNavigate();
  const [items, setItems] = useState({});
  const [buying, setBuying] = useState(false);

  useEffect(() => {
    const fetchItems = async () => {
      try {
        const response = await axios.get(`${API}/shop/items`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setItems(response.data.items);
      } catch (err) {
        console.error(err);
      }
    };
    fetchItems();
  }, [token]);

  const buyItem = async (itemId) => {
    setBuying(true);
    try {
      await axios.post(`${API}/shop/buy`, 
        { item_id: itemId },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      // Show success feedback
    } catch (err) {
      console.error(err);
    }
    setBuying(false);
  };

  const itemIcons = {
    health_potion: Heart,
    energy_drink: Zap,
    basic_sword: Swords,
    small_boat: Ship,
    caravel: Ship,
    brigantine: Ship
  };

  return (
    <div className="min-h-screen bg-[#051923] p-4">
      <div className="glass p-4 flex justify-between items-center mb-6">
        <button onClick={() => navigate('/dashboard')} className="text-[#E3D5CA] hover:text-[#FFC300]">
          <Home className="w-6 h-6" />
        </button>
        <h1 className="font-pirate text-2xl text-[#FFC300]">Negozio</h1>
        <div className="w-6" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(items).map(([itemId, item]) => {
          const Icon = itemIcons[itemId] || Package;
          return (
            <motion.div
              key={itemId}
              className="glass p-6 rounded-xl"
              whileHover={{ scale: 1.02 }}
            >
              <div className="flex items-start gap-4">
                <div className="w-16 h-16 bg-[#3E2723] rounded-lg flex items-center justify-center">
                  <Icon className="w-8 h-8 text-[#D4AF37]" />
                </div>
                <div className="flex-1">
                  <h3 className="font-pirate text-xl text-[#E3D5CA]">{item.name}</h3>
                  <p className="text-sm text-[#E3D5CA]/60">
                    {item.effect?.heal && `+${item.effect.heal} HP`}
                    {item.effect?.energy && `+${item.effect.energy} Energia`}
                    {item.effect?.attack_bonus && `+${item.effect.attack_bonus} ATK`}
                    {item.type === 'ship' && `Nave - Velocità ${item.speed}`}
                  </p>
                  <div className="flex justify-between items-center mt-3">
                    <p className="font-pirate text-[#FFC300]">{item.price.toLocaleString()} Berry</p>
                    <button
                      onClick={() => buyItem(itemId)}
                      disabled={buying}
                      className="btn-gold px-4 py-2 rounded text-sm"
                      data-testid={`buy-${itemId}`}
                    >
                      Compra
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

// ============ MAIN APP ============
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
