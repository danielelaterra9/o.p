import React, { useEffect, useState } from 'react';

/**
 * Sistema di Animazioni Mosse - Stile One Piece
 * 
 * Ogni mossa ha un'animazione unica con:
 * - Linee di velocità (speed lines)
 * - Effetti di impatto
 * - Flash di luce
 * - Onomatopee giapponesi
 * - Colori tematici
 */

// Configurazione animazioni per ogni tipo di mossa
const MOVE_ANIMATIONS = {
  // === MOSSE DI ATTACCO ===
  pugno: {
    name: 'Pugno',
    onomatopoeia: 'ドン!',
    onomatopoeiaAlt: 'DON!',
    color: '#FF6B35',
    secondaryColor: '#FFD700',
    icon: '👊',
    type: 'impact',
    duration: 600,
  },
  gomitata: {
    name: 'Gomitata',
    onomatopoeia: 'バキ!',
    onomatopoeiaAlt: 'BAKI!',
    color: '#E63946',
    secondaryColor: '#FF8C00',
    icon: '💪',
    type: 'impact',
    duration: 550,
  },
  ginocchiata: {
    name: 'Ginocchiata',
    onomatopoeia: 'ゴッ!',
    onomatopoeiaAlt: 'GOT!',
    color: '#D62828',
    secondaryColor: '#FCBF49',
    icon: '🦵',
    type: 'impact',
    duration: 550,
  },
  testata: {
    name: 'Testata',
    onomatopoeia: 'ガン!',
    onomatopoeiaAlt: 'GAN!',
    color: '#7B2CBF',
    secondaryColor: '#E0AAFF',
    icon: '🗣️',
    type: 'impact',
    duration: 650,
  },
  calcio: {
    name: 'Calcio',
    onomatopoeia: 'ドカッ!',
    onomatopoeiaAlt: 'DOKA!',
    color: '#2196F3',
    secondaryColor: '#00BCD4',
    icon: '🦶',
    type: 'sweep',
    duration: 700,
  },
  
  // === MOSSE DI DIFESA ===
  schivata: {
    name: 'Schivata',
    onomatopoeia: 'シュッ!',
    onomatopoeiaAlt: 'SHU!',
    color: '#00C853',
    secondaryColor: '#76FF03',
    icon: '💨',
    type: 'dodge',
    duration: 500,
  },
  parata: {
    name: 'Parata',
    onomatopoeia: 'ガキン!',
    onomatopoeiaAlt: 'GAKIN!',
    color: '#607D8B',
    secondaryColor: '#B0BEC5',
    icon: '🛡️',
    type: 'block',
    duration: 450,
  },
  protezione: {
    name: 'Protezione',
    onomatopoeia: 'ドーン!',
    onomatopoeiaAlt: 'DOON!',
    color: '#3F51B5',
    secondaryColor: '#7C4DFF',
    icon: '🙅',
    type: 'shield',
    duration: 700,
  },

  // === FALLBACK PER MOSSE FUTURE ===
  default: {
    name: 'Attacco',
    onomatopoeia: 'ズドン!',
    onomatopoeiaAlt: 'ZUDON!',
    color: '#FF5722',
    secondaryColor: '#FFC107',
    icon: '⚡',
    type: 'impact',
    duration: 600,
  }
};

// Componente per le linee di velocità (Speed Lines)
const SpeedLines = ({ color, direction = 'right' }) => (
  <div className="speed-lines-container">
    {[...Array(12)].map((_, i) => (
      <div
        key={i}
        className="speed-line"
        style={{
          '--line-index': i,
          '--line-color': color,
          '--direction': direction === 'right' ? '1' : '-1',
          top: `${5 + i * 8}%`,
          animationDelay: `${i * 30}ms`,
        }}
      />
    ))}
  </div>
);

// Componente per l'effetto impatto
const ImpactEffect = ({ color, secondaryColor }) => (
  <div className="impact-container">
    {/* Cerchi di impatto */}
    {[...Array(3)].map((_, i) => (
      <div
        key={i}
        className="impact-ring"
        style={{
          '--ring-index': i,
          '--ring-color': i % 2 === 0 ? color : secondaryColor,
          animationDelay: `${i * 100}ms`,
        }}
      />
    ))}
    {/* Raggi di impatto */}
    {[...Array(8)].map((_, i) => (
      <div
        key={`ray-${i}`}
        className="impact-ray"
        style={{
          '--ray-index': i,
          '--ray-color': color,
          transform: `rotate(${i * 45}deg)`,
        }}
      />
    ))}
  </div>
);

// Componente per effetto schivata
const DodgeEffect = ({ color }) => (
  <div className="dodge-container">
    {[...Array(5)].map((_, i) => (
      <div
        key={i}
        className="dodge-trail"
        style={{
          '--trail-index': i,
          '--trail-color': color,
          opacity: 1 - i * 0.2,
          animationDelay: `${i * 50}ms`,
        }}
      />
    ))}
  </div>
);

// Componente per effetto scudo/blocco
const ShieldEffect = ({ color, secondaryColor }) => (
  <div className="shield-container">
    <div 
      className="shield-hex"
      style={{ '--shield-color': color }}
    />
    <div 
      className="shield-glow"
      style={{ '--glow-color': secondaryColor }}
    />
    {[...Array(6)].map((_, i) => (
      <div
        key={i}
        className="shield-particle"
        style={{
          '--particle-index': i,
          '--particle-color': secondaryColor,
          transform: `rotate(${i * 60}deg) translateY(-60px)`,
        }}
      />
    ))}
  </div>
);

// Componente per effetto sweep (calcio ampio)
const SweepEffect = ({ color, secondaryColor }) => (
  <div className="sweep-container">
    <div 
      className="sweep-arc"
      style={{ '--sweep-color': color }}
    />
    <div 
      className="sweep-trail"
      style={{ '--trail-color': secondaryColor }}
    />
  </div>
);

// Componente Onomatopea
const Onomatopoeia = ({ text, altText, color }) => (
  <div className="onomatopoeia-container">
    <span 
      className="onomatopoeia-text japanese"
      style={{ '--text-color': color }}
    >
      {text}
    </span>
    <span 
      className="onomatopoeia-text romaji"
      style={{ '--text-color': color }}
    >
      {altText}
    </span>
  </div>
);

// Componente principale MoveAnimation
const MoveAnimation = ({ 
  moveId, 
  isPlaying = false, 
  onComplete,
  showOnomatopoeia = true,
  size = 'medium', // small, medium, large, fullscreen
  position = 'center' // center, left, right
}) => {
  const [isAnimating, setIsAnimating] = useState(false);
  const [showText, setShowText] = useState(false);

  // Ottieni configurazione della mossa
  const moveConfig = MOVE_ANIMATIONS[moveId] || MOVE_ANIMATIONS.default;

  useEffect(() => {
    if (isPlaying) {
      setIsAnimating(true);
      
      // Mostra onomatopea dopo un breve delay
      const textTimer = setTimeout(() => {
        setShowText(true);
      }, 100);

      // Completa animazione
      const completeTimer = setTimeout(() => {
        setIsAnimating(false);
        setShowText(false);
        if (onComplete) onComplete();
      }, moveConfig.duration);

      return () => {
        clearTimeout(textTimer);
        clearTimeout(completeTimer);
      };
    }
  }, [isPlaying, moveConfig.duration, onComplete]);

  if (!isAnimating) return null;

  const sizeClasses = {
    small: 'w-32 h-32',
    medium: 'w-48 h-48',
    large: 'w-64 h-64',
    fullscreen: 'w-full h-full fixed inset-0'
  };

  const positionClasses = {
    center: 'mx-auto',
    left: 'ml-0 mr-auto',
    right: 'mr-0 ml-auto'
  };

  // Renderizza effetto basato sul tipo di mossa
  const renderEffect = () => {
    switch (moveConfig.type) {
      case 'impact':
        return <ImpactEffect color={moveConfig.color} secondaryColor={moveConfig.secondaryColor} />;
      case 'dodge':
        return <DodgeEffect color={moveConfig.color} />;
      case 'block':
      case 'shield':
        return <ShieldEffect color={moveConfig.color} secondaryColor={moveConfig.secondaryColor} />;
      case 'sweep':
        return <SweepEffect color={moveConfig.color} secondaryColor={moveConfig.secondaryColor} />;
      default:
        return <ImpactEffect color={moveConfig.color} secondaryColor={moveConfig.secondaryColor} />;
    }
  };

  return (
    <div 
      className={`move-animation-wrapper ${sizeClasses[size]} ${positionClasses[position]}`}
      style={{ '--animation-duration': `${moveConfig.duration}ms` }}
    >
      {/* Background flash */}
      <div 
        className="animation-flash"
        style={{ '--flash-color': moveConfig.color }}
      />
      
      {/* Speed lines */}
      <SpeedLines 
        color={moveConfig.color} 
        direction={moveConfig.type === 'dodge' ? 'left' : 'right'} 
      />
      
      {/* Main effect */}
      <div className="effect-container">
        {renderEffect()}
      </div>
      
      {/* Icon */}
      <div className="move-icon">
        <span className="icon-emoji">{moveConfig.icon}</span>
      </div>
      
      {/* Onomatopoeia */}
      {showOnomatopoeia && showText && (
        <Onomatopoeia 
          text={moveConfig.onomatopoeia}
          altText={moveConfig.onomatopoeiaAlt}
          color={moveConfig.color}
        />
      )}
    </div>
  );
};

// Hook per usare le animazioni facilmente
export const useMoveAnimation = () => {
  const [currentMove, setCurrentMove] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const playAnimation = (moveId) => {
    setCurrentMove(moveId);
    setIsPlaying(true);
  };

  const onAnimationComplete = () => {
    setIsPlaying(false);
    setCurrentMove(null);
  };

  return {
    currentMove,
    isPlaying,
    playAnimation,
    onAnimationComplete,
    AnimationComponent: () => (
      <MoveAnimation
        moveId={currentMove}
        isPlaying={isPlaying}
        onComplete={onAnimationComplete}
      />
    )
  };
};

// Esporta configurazioni per uso esterno
export const getMoveAnimationConfig = (moveId) => {
  return MOVE_ANIMATIONS[moveId] || MOVE_ANIMATIONS.default;
};

export const registerMoveAnimation = (moveId, config) => {
  MOVE_ANIMATIONS[moveId] = { ...MOVE_ANIMATIONS.default, ...config };
};

export default MoveAnimation;
