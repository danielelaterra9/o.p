import { useState } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Anchor, Map, Swords, Users, Package, User, Skull, Shield, Heart, Zap, ChevronRight, Star, Crown, Compass } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ============ COMPONENTS ============

// Wanted Poster Card Component
const WantedPoster = ({ name, bounty, title, avatar, stats }) => (
  <motion.div 
    className="wanted-poster p-6 max-w-sm mx-auto"
    initial={{ rotate: -2 }}
    whileHover={{ rotate: 0, scale: 1.02 }}
    transition={{ duration: 0.3 }}
  >
    <div className="relative z-10">
      <h2 className="font-bounty text-2xl text-center text-[#8B0000] mb-2">WANTED</h2>
      <h3 className="font-bounty text-sm text-center text-[#5D4037] mb-4">DEAD OR ALIVE</h3>
      
      <div className="w-full h-48 bg-[#D7C297] border-4 border-[#5D4037] mb-4 flex items-center justify-center overflow-hidden">
        {avatar ? (
          <img src={avatar} alt={name} className="w-full h-full object-cover" />
        ) : (
          <div className="text-center">
            <User className="w-20 h-20 text-[#5D4037] mx-auto" />
            <p className="text-[#5D4037] text-sm mt-2">Avatar Preview</p>
          </div>
        )}
      </div>
      
      <h3 className="font-pirate text-xl text-center text-[#3E2723] mb-1">{name || "Il Tuo Nome"}</h3>
      <p className="text-center text-[#5D4037] text-sm mb-3">{title || "Pirata Sconosciuto"}</p>
      
      <div className="border-t-2 border-dashed border-[#5D4037] pt-3">
        <p className="font-bounty text-center text-[#8B0000]">
          <span className="text-sm">TAGLIA</span><br />
          <span className="text-3xl">{bounty?.toLocaleString() || "???"}</span>
          <span className="text-lg"> Berry</span>
        </p>
      </div>
      
      {stats && (
        <div className="mt-4 grid grid-cols-3 gap-2 text-center text-[#3E2723]">
          <div>
            <Swords className="w-5 h-5 mx-auto text-[#8B0000]" />
            <span className="text-sm font-bold">{stats.attack}</span>
          </div>
          <div>
            <Shield className="w-5 h-5 mx-auto text-[#1a5f7a]" />
            <span className="text-sm font-bold">{stats.defense}</span>
          </div>
          <div>
            <Heart className="w-5 h-5 mx-auto text-[#FF3B30]" />
            <span className="text-sm font-bold">{stats.hp}</span>
          </div>
        </div>
      )}
    </div>
  </motion.div>
);

// Stat Bar Component
const StatBar = ({ label, current, max, color, icon: Icon }) => {
  const percentage = (current / max) * 100;
  const isCritical = percentage <= 20;
  
  return (
    <div className="mb-3">
      <div className="flex justify-between items-center mb-1">
        <div className="flex items-center gap-2">
          <Icon className="w-4 h-4" style={{ color }} />
          <span className="text-sm font-medium text-[#F4E4BC]">{label}</span>
        </div>
        <span className="text-sm font-bold text-[#F4E4BC]">{current}/{max}</span>
      </div>
      <div className="stat-bar">
        <div 
          className={`stat-bar-fill ${isCritical ? 'hp-critical' : ''}`}
          style={{ width: `${percentage}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
};

// Action Button Component
const ActionButton = ({ icon: Icon, label, description, onClick, disabled, cost }) => (
  <motion.button
    onClick={onClick}
    disabled={disabled}
    className={`glass-panel p-4 text-left w-full rounded-lg ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
    whileHover={!disabled ? { scale: 1.02, borderColor: '#D4AF37' } : {}}
    whileTap={!disabled ? { scale: 0.98 } : {}}
  >
    <div className="flex items-center gap-3">
      <div className="w-12 h-12 rounded-lg bg-[#D4AF37]/20 flex items-center justify-center">
        <Icon className="w-6 h-6 text-[#D4AF37]" />
      </div>
      <div className="flex-1">
        <h4 className="font-bold text-[#F4E4BC]">{label}</h4>
        <p className="text-sm text-[#F4E4BC]/70">{description}</p>
      </div>
      {cost && (
        <div className="text-right">
          <span className="text-xs text-[#00FFFF]">-{cost} ST</span>
        </div>
      )}
    </div>
  </motion.button>
);

// Map Island Node
const IslandNode = ({ name, saga, x, y, unlocked, current, onClick }) => (
  <motion.div
    className={`absolute map-node cursor-pointer ${!unlocked ? 'opacity-40' : ''}`}
    style={{ left: `${x}%`, top: `${y}%` }}
    onClick={unlocked ? onClick : undefined}
    whileHover={unlocked ? { scale: 1.15 } : {}}
    initial={{ scale: 0 }}
    animate={{ scale: 1 }}
    transition={{ delay: Math.random() * 0.5 }}
  >
    <div className={`w-16 h-16 rounded-full flex items-center justify-center ${current ? 'bg-[#D4AF37] border-4 border-[#F9A602]' : unlocked ? 'bg-[#5D4037] border-2 border-[#D4AF37]' : 'bg-[#3E2723] border-2 border-[#5D4037]'}`}>
      <Compass className={`w-8 h-8 ${current ? 'text-[#3E2723]' : 'text-[#F4E4BC]'}`} />
    </div>
    <p className={`text-xs text-center mt-1 font-bold ${current ? 'text-[#D4AF37]' : 'text-[#F4E4BC]'}`}>{name}</p>
    <p className="text-xs text-center text-[#F4E4BC]/60">{saga}</p>
  </motion.div>
);

// ============ PAGES ============

// Landing Page
const LandingPage = ({ onNavigate }) => (
  <div className="min-h-screen ocean-bg flex flex-col items-center justify-center p-8 relative">
    <motion.div
      initial={{ opacity: 0, y: -50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
      className="text-center mb-12"
    >
      <h1 className="font-pirate text-5xl md:text-7xl text-[#D4AF37] mb-4 drop-shadow-lg">
        The Grand Line
      </h1>
      <h2 className="font-pirate text-2xl md:text-3xl text-[#F4E4BC] mb-2">
        Logbook
      </h2>
      <p className="text-[#F4E4BC]/80 text-lg max-w-md mx-auto">
        Crea il tuo pirata, recluta la tua ciurma e conquista il Grand Line!
      </p>
    </motion.div>
    
    <motion.div 
      className="flex flex-col gap-4 w-full max-w-xs"
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, delay: 0.3 }}
    >
      <motion.button
        onClick={() => onNavigate('character')}
        className="btn-gold py-4 px-8 text-lg font-pirate rounded"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        data-testid="new-adventure-btn"
      >
        Nuova Avventura
      </motion.button>
      
      <motion.button
        onClick={() => onNavigate('battle')}
        className="bg-[#5D4037] text-[#F4E4BC] py-3 px-8 rounded border-2 border-[#D4AF37] font-bold"
        whileHover={{ scale: 1.02, backgroundColor: '#3E2723' }}
        data-testid="continue-btn"
      >
        Continua Partita
      </motion.button>
      
      <motion.button
        onClick={() => onNavigate('map')}
        className="glass-panel py-3 px-8 rounded text-[#F4E4BC] font-medium"
        whileHover={{ scale: 1.02 }}
        data-testid="explore-map-btn"
      >
        <Map className="w-5 h-5 inline mr-2" />
        Esplora Mappa
      </motion.button>
    </motion.div>
    
    <motion.div 
      className="absolute bottom-8 text-center"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 1 }}
    >
      <p className="text-[#F4E4BC]/50 text-sm">
        Versione Prototipo - One Piece RPG
      </p>
    </motion.div>
  </div>
);

// Character Creation Page
const CharacterCreationPage = ({ onNavigate }) => {
  const [character, setCharacter] = useState({
    name: '',
    title: 'Aspirante Pirata',
    bodyType: 'normal',
    hairStyle: 'short',
    hairColor: '#3E2723',
    outfit: 'pirate',
    devilFruit: null,
    stats: { attack: 50, defense: 40, hp: 100 }
  });
  
  const bodyTypes = [
    { id: 'slim', label: 'Agile', bonus: { attack: 10, defense: -5 } },
    { id: 'normal', label: 'Equilibrato', bonus: { attack: 0, defense: 0 } },
    { id: 'muscular', label: 'Forte', bonus: { attack: 5, defense: 10 } },
    { id: 'giant', label: 'Gigante', bonus: { attack: 15, defense: 15, hp: 50 } }
  ];
  
  const devilFruits = [
    { id: null, name: 'Nessuno', rarity: '-', effect: 'Può nuotare' },
    { id: 'gomu', name: 'Gomu Gomu', rarity: 'Paramisha', effect: '+20 ATK, Elasticità' },
    { id: 'mera', name: 'Mera Mera', rarity: 'Rogia', effect: '+30 ATK, Fuoco' },
    { id: 'hito', name: 'Hito Hito', rarity: 'Zoan', effect: '+25 DEF, Trasformazione' },
    { id: 'ope', name: 'Ope Ope', rarity: 'Paramisha', effect: 'Room, Controllo' }
  ];
  
  const hairColors = ['#3E2723', '#FFD700', '#FF6B35', '#1a1a1a', '#FF3B30', '#00FFFF', '#39FF14'];
  
  return (
    <div className="min-h-screen bg-[#0F1C2E] p-4 md:p-8">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="max-w-6xl mx-auto"
      >
        <div className="flex items-center justify-between mb-8">
          <h1 className="font-pirate text-3xl md:text-4xl text-[#D4AF37]">Crea il Tuo Pirata</h1>
          <motion.button
            onClick={() => onNavigate('landing')}
            className="text-[#F4E4BC]/70 hover:text-[#D4AF37]"
            whileHover={{ scale: 1.1 }}
          >
            <Anchor className="w-8 h-8" />
          </motion.button>
        </div>
        
        <div className="grid md:grid-cols-2 gap-8">
          {/* Left: Options */}
          <div className="space-y-6">
            {/* Name Input */}
            <div className="glass-panel p-6 rounded-xl">
              <label className="block text-[#D4AF37] font-bold mb-2">Nome Pirata</label>
              <input
                type="text"
                value={character.name}
                onChange={(e) => setCharacter({...character, name: e.target.value})}
                placeholder="Inserisci il nome..."
                className="input-parchment w-full p-3 rounded"
                data-testid="character-name-input"
              />
            </div>
            
            {/* Body Type */}
            <div className="glass-panel p-6 rounded-xl">
              <label className="block text-[#D4AF37] font-bold mb-4">Tipo Corpo</label>
              <div className="grid grid-cols-2 gap-3">
                {bodyTypes.map((type) => (
                  <motion.button
                    key={type.id}
                    onClick={() => setCharacter({...character, bodyType: type.id})}
                    className={`p-4 rounded-lg border-2 ${character.bodyType === type.id ? 'border-[#D4AF37] bg-[#D4AF37]/20' : 'border-[#5D4037] bg-[#5D4037]/20'}`}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <span className="block font-bold text-[#F4E4BC]">{type.label}</span>
                    <span className="text-xs text-[#00FFFF]">
                      {type.bonus.attack > 0 && `+${type.bonus.attack} ATK `}
                      {type.bonus.defense > 0 && `+${type.bonus.defense} DEF`}
                      {type.bonus.hp && ` +${type.bonus.hp} HP`}
                    </span>
                  </motion.button>
                ))}
              </div>
            </div>
            
            {/* Hair Color */}
            <div className="glass-panel p-6 rounded-xl">
              <label className="block text-[#D4AF37] font-bold mb-4">Colore Capelli</label>
              <div className="flex gap-3 flex-wrap">
                {hairColors.map((color) => (
                  <motion.button
                    key={color}
                    onClick={() => setCharacter({...character, hairColor: color})}
                    className={`w-10 h-10 rounded-full border-4 ${character.hairColor === color ? 'border-[#D4AF37]' : 'border-transparent'}`}
                    style={{ backgroundColor: color }}
                    whileHover={{ scale: 1.2 }}
                    whileTap={{ scale: 0.9 }}
                  />
                ))}
              </div>
            </div>
            
            {/* Devil Fruit */}
            <div className="glass-panel p-6 rounded-xl">
              <label className="block text-[#D4AF37] font-bold mb-4">
                <Star className="w-5 h-5 inline mr-2 text-[#39FF14]" />
                Frutto del Diavolo
              </label>
              <div className="space-y-2">
                {devilFruits.map((fruit) => (
                  <motion.button
                    key={fruit.id || 'none'}
                    onClick={() => setCharacter({...character, devilFruit: fruit.id})}
                    className={`w-full p-3 rounded-lg border-2 text-left flex justify-between items-center ${character.devilFruit === fruit.id ? 'border-[#39FF14] bg-[#39FF14]/10' : 'border-[#5D4037]'}`}
                    whileHover={{ scale: 1.01 }}
                  >
                    <div>
                      <span className="font-bold text-[#F4E4BC]">{fruit.name}</span>
                      <span className={`ml-2 text-xs px-2 py-1 rounded ${fruit.rarity === 'Rogia' ? 'bg-[#FF3B30]/30 text-[#FF3B30]' : fruit.rarity === 'Zoan' ? 'bg-[#39FF14]/30 text-[#39FF14]' : fruit.rarity === 'Paramisha' ? 'bg-[#6A0DAD]/30 text-[#00FFFF]' : 'bg-[#5D4037]'}`}>
                        {fruit.rarity}
                      </span>
                    </div>
                    <span className="text-xs text-[#F4E4BC]/60">{fruit.effect}</span>
                  </motion.button>
                ))}
              </div>
            </div>
          </div>
          
          {/* Right: Preview */}
          <div className="flex flex-col items-center gap-6">
            <WantedPoster
              name={character.name}
              bounty={character.devilFruit ? 50000000 : 10000000}
              title={character.title}
              stats={character.stats}
            />
            
            <motion.button
              onClick={() => onNavigate('battle')}
              className="btn-gold py-4 px-12 text-lg font-pirate rounded w-full max-w-sm"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              data-testid="start-adventure-btn"
            >
              <ChevronRight className="w-6 h-6 inline mr-2" />
              Inizia Avventura
            </motion.button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

// Attack Animation Component
const AttackAnimation = ({ type, onComplete }) => {
  const variants = {
    punch: {
      initial: { x: -200, y: 100, scale: 0.5, opacity: 0 },
      animate: { 
        x: [null, 0, 100], 
        y: [null, 0, -20],
        scale: [0.5, 1.5, 2],
        opacity: [0, 1, 0],
        rotate: [0, 0, 15]
      },
      transition: { duration: 0.6, times: [0, 0.6, 1] }
    },
    gomugomu: {
      initial: { x: -300, scaleX: 0.3, opacity: 0 },
      animate: { 
        x: [null, -100, 150], 
        scaleX: [0.3, 3, 1],
        opacity: [0, 1, 0]
      },
      transition: { duration: 0.8, times: [0, 0.5, 1] }
    },
    fire: {
      initial: { scale: 0, opacity: 0 },
      animate: { 
        scale: [0, 1.5, 2, 0],
        opacity: [0, 1, 1, 0]
      },
      transition: { duration: 0.7 }
    },
    slash: {
      initial: { x: -100, rotate: -45, opacity: 0, scale: 0.5 },
      animate: { 
        x: [null, 50, 150], 
        rotate: [-45, 0, 45],
        opacity: [0, 1, 0],
        scale: [0.5, 1.2, 0.8]
      },
      transition: { duration: 0.5 }
    },
    defend: {
      initial: { scale: 0, opacity: 0 },
      animate: { 
        scale: [0, 1.2, 1],
        opacity: [0, 0.8, 0]
      },
      transition: { duration: 0.8 }
    },
    heal: {
      initial: { y: 50, opacity: 0 },
      animate: { 
        y: [50, 0, -30],
        opacity: [0, 1, 0],
        scale: [0.5, 1.2, 0.8]
      },
      transition: { duration: 1 }
    }
  };

  const getIcon = () => {
    switch(type) {
      case 'punch': return '👊';
      case 'gomugomu': return '🥊';
      case 'fire': return '🔥';
      case 'slash': return '⚔️';
      case 'defend': return '🛡️';
      case 'heal': return '✨';
      default: return '💥';
    }
  };

  const getColor = () => {
    switch(type) {
      case 'punch': return '#D4AF37';
      case 'gomugomu': return '#FF3B30';
      case 'fire': return '#FF6B35';
      case 'slash': return '#00FFFF';
      case 'defend': return '#6A0DAD';
      case 'heal': return '#39FF14';
      default: return '#D4AF37';
    }
  };

  return (
    <motion.div
      className="absolute inset-0 flex items-center justify-center pointer-events-none z-50"
      initial="initial"
      animate="animate"
      variants={variants[type] || variants.punch}
      onAnimationComplete={onComplete}
    >
      <div 
        className="text-8xl filter drop-shadow-lg"
        style={{ 
          textShadow: `0 0 30px ${getColor()}, 0 0 60px ${getColor()}`,
        }}
      >
        {getIcon()}
      </div>
    </motion.div>
  );
};

// Impact Effect Component
const ImpactEffect = ({ position, color = '#FF3B30' }) => (
  <motion.div
    className="absolute pointer-events-none z-40"
    style={{ left: position.x, top: position.y }}
    initial={{ scale: 0, opacity: 1 }}
    animate={{ 
      scale: [0, 2, 3],
      opacity: [1, 0.8, 0]
    }}
    transition={{ duration: 0.5 }}
  >
    <svg width="120" height="120" viewBox="0 0 120 120">
      <motion.circle
        cx="60"
        cy="60"
        r="50"
        fill="none"
        stroke={color}
        strokeWidth="4"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 0.3 }}
      />
      {[0, 45, 90, 135, 180, 225, 270, 315].map((angle, i) => (
        <motion.line
          key={i}
          x1="60"
          y1="60"
          x2={60 + Math.cos(angle * Math.PI / 180) * 50}
          y2={60 + Math.sin(angle * Math.PI / 180) * 50}
          stroke={color}
          strokeWidth="3"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 0.2, delay: i * 0.02 }}
        />
      ))}
    </svg>
  </motion.div>
);

// Particle Effect Component
const ParticleEffect = ({ type, active }) => {
  const particles = Array.from({ length: 12 }, (_, i) => i);
  
  if (!active) return null;
  
  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden z-30">
      {particles.map((i) => (
        <motion.div
          key={i}
          className="absolute w-3 h-3 rounded-full"
          style={{
            left: '50%',
            top: '50%',
            backgroundColor: type === 'fire' ? '#FF6B35' : type === 'electric' ? '#00FFFF' : '#D4AF37'
          }}
          initial={{ x: 0, y: 0, opacity: 1 }}
          animate={{
            x: Math.cos(i * 30 * Math.PI / 180) * (100 + Math.random() * 50),
            y: Math.sin(i * 30 * Math.PI / 180) * (100 + Math.random() * 50),
            opacity: 0,
            scale: [1, 1.5, 0]
          }}
          transition={{ duration: 0.8, delay: i * 0.03 }}
        />
      ))}
    </div>
  );
};

// Battle Page
const BattlePage = ({ onNavigate }) => {
  const [playerHP, setPlayerHP] = useState(85);
  const [playerStamina, setPlayerStamina] = useState(60);
  const [enemyHP, setEnemyHP] = useState(100);
  const [battleLog, setBattleLog] = useState(['Combattimento iniziato!', 'Il Marine Captain ti sfida!']);
  const [isPlayerTurn, setIsPlayerTurn] = useState(true);
  const [showDamage, setShowDamage] = useState(null);
  const [currentAnimation, setCurrentAnimation] = useState(null);
  const [enemyShake, setEnemyShake] = useState(false);
  const [playerShake, setPlayerShake] = useState(false);
  const [showImpact, setShowImpact] = useState(null);
  const [particleType, setParticleType] = useState(null);
  const [hakiFlash, setHakiFlash] = useState(false);
  const [defending, setDefending] = useState(false);
  
  const handleAction = (action) => {
    if (!isPlayerTurn) return;
    
    let damage = 0;
    let staminaCost = 0;
    let message = '';
    let animationType = 'punch';
    let isCritical = Math.random() < 0.15; // 15% critical chance
    
    switch(action) {
      case 'attack':
        damage = Math.floor(Math.random() * 10) + 10;
        if (isCritical) {
          damage = Math.floor(damage * 1.5);
          message = `COLPO CRITICO! Attacco base! ${damage} danni!`;
          setHakiFlash(true);
          setTimeout(() => setHakiFlash(false), 300);
        } else {
          message = `Attacco base! ${damage} danni!`;
        }
        animationType = 'punch';
        break;
      case 'skill':
        damage = Math.floor(Math.random() * 20) + 20;
        staminaCost = 20;
        if (isCritical) {
          damage = Math.floor(damage * 1.5);
          message = `CRITICO! Gomu Gomu no Pistol! ${damage} danni!`;
          setHakiFlash(true);
          setTimeout(() => setHakiFlash(false), 300);
        } else {
          message = `Gomu Gomu no Pistol! ${damage} danni!`;
        }
        animationType = 'gomugomu';
        setParticleType('fire');
        setTimeout(() => setParticleType(null), 800);
        break;
      case 'defend':
        message = 'Ti difendi! +50% DEF per questo turno';
        animationType = 'defend';
        setDefending(true);
        break;
      case 'item':
        setPlayerHP(Math.min(100, playerHP + 30));
        message = 'Hai usato Carne! +30 HP';
        animationType = 'heal';
        break;
      default:
        break;
    }
    
    if (staminaCost > 0) {
      setPlayerStamina(Math.max(0, playerStamina - staminaCost));
    }
    
    // Start attack animation
    setCurrentAnimation(animationType);
    
    // After animation, apply damage
    setTimeout(() => {
      setCurrentAnimation(null);
      
      if (damage > 0) {
        setEnemyHP(Math.max(0, enemyHP - damage));
        setShowDamage({ value: damage, critical: isCritical });
        setEnemyShake(true);
        setShowImpact({ x: '60%', y: '30%' });
        
        setTimeout(() => {
          setShowDamage(null);
          setEnemyShake(false);
          setShowImpact(null);
        }, 800);
      }
      
      setBattleLog(prev => [...prev, message]);
    }, animationType === 'gomugomu' ? 600 : 400);
    
    setIsPlayerTurn(false);
    
    // Enemy turn simulation
    setTimeout(() => {
      const enemyDamage = defending ? Math.floor((Math.random() * 15 + 5) * 0.5) : Math.floor(Math.random() * 15) + 5;
      setDefending(false);
      
      // Enemy attack animation
      setCurrentAnimation('slash');
      
      setTimeout(() => {
        setCurrentAnimation(null);
        setPlayerHP(Math.max(0, playerHP - enemyDamage));
        setPlayerShake(true);
        setBattleLog(prev => [...prev, `Il nemico attacca! ${enemyDamage} danni!`]);
        
        setTimeout(() => {
          setPlayerShake(false);
          setIsPlayerTurn(true);
        }, 500);
      }, 400);
    }, 2000);
  };
  
  return (
    <div className={`min-h-screen bg-[#0F1C2E] flex flex-col relative ${hakiFlash ? 'haki-flash-active' : ''}`}>
      {/* Haki Flash Overlay */}
      <AnimatePresence>
        {hakiFlash && (
          <motion.div
            className="absolute inset-0 bg-[#6A0DAD] z-50 pointer-events-none"
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.4 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
          />
        )}
      </AnimatePresence>
      
      {/* Attack Animation */}
      <AnimatePresence>
        {currentAnimation && (
          <AttackAnimation 
            type={currentAnimation} 
            onComplete={() => {}}
          />
        )}
      </AnimatePresence>
      
      {/* Particle Effects */}
      <ParticleEffect type={particleType} active={!!particleType} />
      
      {/* Impact Effect */}
      <AnimatePresence>
        {showImpact && <ImpactEffect position={showImpact} color="#FF3B30" />}
      </AnimatePresence>
      
      {/* Top: Enemy Area */}
      <div className="flex-1 relative p-4 md:p-8" style={{background: 'linear-gradient(180deg, #1a3a5c 0%, #0F1C2E 100%)'}}>
        <motion.button
          onClick={() => onNavigate('landing')}
          className="absolute top-4 left-4 text-[#F4E4BC]/70 hover:text-[#D4AF37] z-10"
          whileHover={{ scale: 1.1 }}
        >
          <Anchor className="w-8 h-8" />
        </motion.button>
        
        <div className="max-w-4xl mx-auto">
          <motion.div 
            className="glass-panel p-6 rounded-xl mb-4"
            animate={enemyShake ? { x: [-10, 10, -10, 10, 0] } : {}}
            transition={{ duration: 0.4 }}
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-4">
                <motion.div 
                  className="w-16 h-16 rounded-full bg-[#5D4037] border-2 border-[#D4AF37] flex items-center justify-center"
                  animate={enemyShake ? { scale: [1, 0.9, 1] } : {}}
                >
                  <Skull className="w-10 h-10 text-[#F4E4BC]" />
                </motion.div>
                <div>
                  <h3 className="font-pirate text-xl text-[#FF3B30]">Marine Captain</h3>
                  <p className="text-sm text-[#F4E4BC]/70">Livello 5 - Boss</p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-bounty text-[#D4AF37]">10,000,000 Berry</p>
              </div>
            </div>
            
            <StatBar label="HP" current={enemyHP} max={100} color="#FF3B30" icon={Heart} />
          </motion.div>
          
          {/* Damage Number */}
          <AnimatePresence>
            {showDamage && (
              <motion.div
                className={`absolute font-bounty text-5xl ${showDamage.critical ? 'text-[#FFD700]' : 'text-[#FF3B30]'}`}
                style={{ left: '55%', top: '25%' }}
                initial={{ opacity: 1, y: 0, scale: 1 }}
                animate={{ 
                  opacity: 0, 
                  y: -80, 
                  scale: showDamage.critical ? 2 : 1.5,
                  rotate: showDamage.critical ? [0, -10, 10, 0] : 0
                }}
                exit={{ opacity: 0 }}
                transition={{ duration: 1 }}
              >
                {showDamage.critical && <span className="text-2xl">💥</span>}
                -{showDamage.value}
                {showDamage.critical && <span className="text-lg ml-1">CRITICO!</span>}
              </motion.div>
            )}
          </AnimatePresence>
          
          {/* Battle Log */}
          <div className="glass-panel p-4 rounded-xl h-32 overflow-y-auto">
            {battleLog.slice(-4).map((log, i) => (
              <motion.p 
                key={i}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className={`text-sm mb-1 ${log.includes('CRITICO') ? 'text-[#FFD700] font-bold' : 'text-[#F4E4BC]/80'}`}
              >
                &gt; {log}
              </motion.p>
            ))}
          </div>
        </div>
      </div>
      
      {/* Bottom: Player Area */}
      <motion.div 
        className="glass-panel p-4 md:p-6 rounded-t-3xl"
        animate={playerShake ? { x: [-5, 5, -5, 5, 0] } : {}}
        transition={{ duration: 0.3 }}
      >
        <div className="max-w-4xl mx-auto">
          {/* Player Stats */}
          <div className="flex items-center gap-4 mb-6">
            <motion.div 
              className={`w-14 h-14 rounded-full flex items-center justify-center ${defending ? 'bg-[#6A0DAD] border-2 border-[#00FFFF]' : 'bg-[#D4AF37] border-2 border-[#F9A602]'}`}
              animate={defending ? { 
                boxShadow: ['0 0 0px #6A0DAD', '0 0 20px #6A0DAD', '0 0 0px #6A0DAD']
              } : {}}
              transition={{ duration: 1, repeat: defending ? Infinity : 0 }}
            >
              {defending ? <Shield className="w-8 h-8 text-[#00FFFF]" /> : <Crown className="w-8 h-8 text-[#3E2723]" />}
            </motion.div>
            <div className="flex-1">
              <h3 className="font-pirate text-lg text-[#D4AF37]">
                Il Tuo Pirata
                {defending && <span className="ml-2 text-sm text-[#00FFFF]">(DIFESA ATTIVA)</span>}
              </h3>
              <div className="grid grid-cols-2 gap-2 mt-2">
                <StatBar label="HP" current={playerHP} max={100} color="#FF3B30" icon={Heart} />
                <StatBar label="Stamina" current={playerStamina} max={100} color="#00FFFF" icon={Zap} />
              </div>
            </div>
          </div>
          
          {/* Action Buttons */}
          <div className="grid grid-cols-2 gap-3">
            <ActionButton 
              icon={Swords} 
              label="Attacco Base" 
              description="10-20 danni"
              onClick={() => handleAction('attack')}
              disabled={!isPlayerTurn}
            />
            <ActionButton 
              icon={Zap} 
              label="Gomu Gomu no Pistol" 
              description="20-40 danni"
              onClick={() => handleAction('skill')}
              disabled={!isPlayerTurn || playerStamina < 20}
              cost={20}
            />
            <ActionButton 
              icon={Shield} 
              label="Difendi" 
              description="+50% DEF turno"
              onClick={() => handleAction('defend')}
              disabled={!isPlayerTurn}
            />
            <ActionButton 
              icon={Heart} 
              label="Usa Carne" 
              description="+30 HP"
              onClick={() => handleAction('item')}
              disabled={!isPlayerTurn}
            />
          </div>
          
          {!isPlayerTurn && (
            <motion.p 
              className="text-center mt-4 text-[#FF3B30] font-bold"
              animate={{ opacity: [1, 0.5, 1] }}
              transition={{ repeat: Infinity, duration: 1 }}
            >
              Turno del nemico...
            </motion.p>
          )}
        </div>
      </motion.div>
    </div>
  );
};

// Map Page
const MapPage = ({ onNavigate }) => {
  const islands = [
    { id: 1, name: 'Foosha', saga: 'East Blue', x: 10, y: 70, unlocked: true, current: true },
    { id: 2, name: 'Orange Town', saga: 'East Blue', x: 20, y: 55, unlocked: true },
    { id: 3, name: 'Baratie', saga: 'East Blue', x: 30, y: 65, unlocked: true },
    { id: 4, name: 'Arlong Park', saga: 'East Blue', x: 38, y: 45, unlocked: false },
    { id: 5, name: 'Loguetown', saga: 'East Blue', x: 48, y: 60, unlocked: false },
    { id: 6, name: 'Alabasta', saga: 'Grand Line', x: 58, y: 40, unlocked: false },
    { id: 7, name: 'Skypiea', saga: 'Grand Line', x: 65, y: 20, unlocked: false },
    { id: 8, name: 'Water 7', saga: 'Grand Line', x: 72, y: 50, unlocked: false },
    { id: 9, name: 'Thriller Bark', saga: 'Grand Line', x: 80, y: 35, unlocked: false },
    { id: 10, name: 'Wano', saga: 'New World', x: 90, y: 25, unlocked: false }
  ];
  
  return (
    <div className="min-h-screen bg-[#0F1C2E] p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="font-pirate text-3xl text-[#D4AF37]">
            <Map className="w-8 h-8 inline mr-3" />
            Mappa del Grand Line
          </h1>
          <motion.button
            onClick={() => onNavigate('landing')}
            className="text-[#F4E4BC]/70 hover:text-[#D4AF37]"
            whileHover={{ scale: 1.1 }}
          >
            <Anchor className="w-8 h-8" />
          </motion.button>
        </div>
        
        {/* Map Container */}
        <div 
          className="relative w-full rounded-xl overflow-hidden border-4 border-[#5D4037]"
          style={{ 
            height: '500px',
            background: `url('https://images.unsplash.com/photo-1695390046346-b308dbeeedec?w=1200') center/cover`,
          }}
        >
          {/* Overlay */}
          <div className="absolute inset-0 bg-[#0F1C2E]/40" />
          
          {/* Sea Routes */}
          <svg className="absolute inset-0 w-full h-full" style={{ zIndex: 1 }}>
            <path
              d="M 10% 70% Q 25% 55% 38% 45% T 58% 40% T 90% 25%"
              fill="none"
              stroke="#D4AF37"
              strokeWidth="2"
              strokeDasharray="10,5"
              opacity="0.5"
            />
          </svg>
          
          {/* Islands */}
          {islands.map((island) => (
            <IslandNode
              key={island.id}
              {...island}
              onClick={() => console.log(`Navigating to ${island.name}`)}
            />
          ))}
          
          {/* Legend */}
          <div className="absolute bottom-4 left-4 glass-panel p-4 rounded-lg">
            <h4 className="font-bold text-[#D4AF37] mb-2">Legenda</h4>
            <div className="flex items-center gap-2 text-sm text-[#F4E4BC]">
              <div className="w-4 h-4 rounded-full bg-[#D4AF37]" /> Posizione Attuale
            </div>
            <div className="flex items-center gap-2 text-sm text-[#F4E4BC]">
              <div className="w-4 h-4 rounded-full bg-[#5D4037] border border-[#D4AF37]" /> Sbloccato
            </div>
            <div className="flex items-center gap-2 text-sm text-[#F4E4BC]/50">
              <div className="w-4 h-4 rounded-full bg-[#3E2723]" /> Bloccato
            </div>
          </div>
        </div>
        
        {/* Current Location Info */}
        <div className="glass-panel p-6 rounded-xl mt-6">
          <h3 className="font-pirate text-xl text-[#D4AF37] mb-2">Foosha Village - East Blue</h3>
          <p className="text-[#F4E4BC]/80 mb-4">Il villaggio natale di Monkey D. Luffy. Qui inizia la tua avventura!</p>
          <div className="flex gap-4">
            <motion.button
              onClick={() => onNavigate('battle')}
              className="btn-gold py-3 px-6 rounded"
              whileHover={{ scale: 1.02 }}
            >
              <Swords className="w-5 h-5 inline mr-2" />
              Combatti
            </motion.button>
            <motion.button
              className="bg-[#5D4037] text-[#F4E4BC] py-3 px-6 rounded border border-[#D4AF37]"
              whileHover={{ scale: 1.02 }}
            >
              <Users className="w-5 h-5 inline mr-2" />
              Recluta
            </motion.button>
            <motion.button
              className="glass-panel py-3 px-6 rounded"
              whileHover={{ scale: 1.02 }}
            >
              <Package className="w-5 h-5 inline mr-2" />
              Negozio
            </motion.button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Crew Management Page
const CrewPage = ({ onNavigate }) => {
  const crewMembers = [
    { id: 1, name: 'Primo Ufficiale', role: 'Spadaccino', level: 5, attack: 60, defense: 50 },
    { id: 2, name: 'Navigatore', role: 'Supporto', level: 3, attack: 30, defense: 40 },
    { id: 3, name: 'Cuoco', role: 'Lottatore', level: 4, attack: 55, defense: 35 }
  ];
  
  return (
    <div className="min-h-screen bg-[#0F1C2E] p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="font-pirate text-3xl text-[#D4AF37]">
            <Users className="w-8 h-8 inline mr-3" />
            La Tua Ciurma
          </h1>
          <motion.button
            onClick={() => onNavigate('landing')}
            className="text-[#F4E4BC]/70 hover:text-[#D4AF37]"
            whileHover={{ scale: 1.1 }}
          >
            <Anchor className="w-8 h-8" />
          </motion.button>
        </div>
        
        <div className="grid md:grid-cols-3 gap-6">
          {crewMembers.map((member) => (
            <motion.div
              key={member.id}
              className="wanted-poster p-6"
              whileHover={{ rotate: 0, scale: 1.02 }}
              initial={{ rotate: Math.random() * 4 - 2 }}
            >
              <div className="relative z-10">
                <div className="w-full h-32 bg-[#D7C297] border-2 border-[#5D4037] mb-3 flex items-center justify-center">
                  <User className="w-16 h-16 text-[#5D4037]" />
                </div>
                <h3 className="font-pirate text-lg text-[#3E2723] text-center">{member.name}</h3>
                <p className="text-center text-[#5D4037] text-sm mb-3">{member.role} - Lv.{member.level}</p>
                <div className="grid grid-cols-2 gap-2 text-center text-[#3E2723]">
                  <div>
                    <Swords className="w-4 h-4 mx-auto text-[#8B0000]" />
                    <span className="text-sm font-bold">{member.attack}</span>
                  </div>
                  <div>
                    <Shield className="w-4 h-4 mx-auto text-[#1a5f7a]" />
                    <span className="text-sm font-bold">{member.defense}</span>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
          
          {/* Add Member Card */}
          <motion.div
            className="glass-panel p-6 rounded-xl flex flex-col items-center justify-center border-2 border-dashed border-[#D4AF37]/50 min-h-[280px] cursor-pointer"
            whileHover={{ scale: 1.02, borderColor: '#D4AF37' }}
          >
            <Users className="w-16 h-16 text-[#D4AF37]/50 mb-4" />
            <p className="text-[#F4E4BC]/70 text-center">Recluta nuovo membro</p>
          </motion.div>
        </div>
        
        {/* Ship Section */}
        <div className="glass-panel p-6 rounded-xl mt-8">
          <h2 className="font-pirate text-2xl text-[#D4AF37] mb-4">La Tua Nave</h2>
          <div className="grid md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto rounded-full bg-[#5D4037] flex items-center justify-center mb-2">
                <Anchor className="w-8 h-8 text-[#D4AF37]" />
              </div>
              <p className="text-[#F4E4BC] font-bold">Going Merry</p>
              <p className="text-[#F4E4BC]/60 text-sm">Caravella</p>
            </div>
            <div>
              <p className="text-[#D4AF37] font-bold mb-1">Salute Nave</p>
              <div className="stat-bar">
                <div className="stat-bar-fill bg-[#39FF14]" style={{ width: '75%' }} />
              </div>
              <p className="text-right text-xs text-[#F4E4BC]/60">75/100</p>
            </div>
            <div>
              <p className="text-[#D4AF37] font-bold mb-1">Capacità Cargo</p>
              <div className="stat-bar">
                <div className="stat-bar-fill bg-[#00FFFF]" style={{ width: '40%' }} />
              </div>
              <p className="text-right text-xs text-[#F4E4BC]/60">40/100</p>
            </div>
            <div>
              <p className="text-[#D4AF37] font-bold mb-1">Velocità</p>
              <div className="stat-bar">
                <div className="stat-bar-fill bg-[#D4AF37]" style={{ width: '60%' }} />
              </div>
              <p className="text-right text-xs text-[#F4E4BC]/60">60/100</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// ============ MAIN APP ============

function App() {
  const [currentPage, setCurrentPage] = useState('landing');
  
  const renderPage = () => {
    switch(currentPage) {
      case 'landing':
        return <LandingPage onNavigate={setCurrentPage} />;
      case 'character':
        return <CharacterCreationPage onNavigate={setCurrentPage} />;
      case 'battle':
        return <BattlePage onNavigate={setCurrentPage} />;
      case 'map':
        return <MapPage onNavigate={setCurrentPage} />;
      case 'crew':
        return <CrewPage onNavigate={setCurrentPage} />;
      default:
        return <LandingPage onNavigate={setCurrentPage} />;
    }
  };
  
  return (
    <div className="App">
      <AnimatePresence mode="wait">
        <motion.div
          key={currentPage}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
        >
          {renderPage()}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

export default App;
