import React, { useState, useCallback } from 'react';
import MoveAnimation, { getMoveAnimationConfig, registerMoveAnimation } from './MoveAnimation';
import './MoveAnimation.css';

/**
 * BattleAnimationManager - Gestisce le animazioni durante il combattimento
 * 
 * Uso:
 * const { playMoveAnimation, BattleAnimationOverlay } = useBattleAnimations();
 * 
 * // Quando si usa una mossa:
 * await playMoveAnimation('pugno', { isCritical: false, isMiss: false });
 * 
 * // Nel render:
 * <BattleAnimationOverlay />
 */

// Registra animazioni per mosse speciali (razze, stili, armi, frutti)
const registerSpecialMoveAnimations = () => {
  // === MOSSE RAZZA: UOMO PESCE ===
  registerMoveAnimation('karate_uomo_pesce', {
    name: 'Karate Uomo Pesce',
    onomatopoeia: 'ザバーン!',
    onomatopoeiaAlt: 'ZABAAN!',
    color: '#00BCD4',
    secondaryColor: '#4DD0E1',
    icon: '🌊',
    type: 'sweep',
    duration: 750,
  });
  
  registerMoveAnimation('morso_squalo', {
    name: 'Morso Squalo',
    onomatopoeia: 'ガブッ!',
    onomatopoeiaAlt: 'GABU!',
    color: '#1565C0',
    secondaryColor: '#E53935',
    icon: '🦈',
    type: 'impact',
    duration: 600,
  });

  // === MOSSE RAZZA: SEMI-GIGANTE ===
  registerMoveAnimation('pugno_devastante', {
    name: 'Pugno Devastante',
    onomatopoeia: 'ドゴォン!',
    onomatopoeiaAlt: 'DOGOON!',
    color: '#8D6E63',
    secondaryColor: '#FFAB91',
    icon: '💥',
    type: 'impact',
    duration: 800,
  });
  
  registerMoveAnimation('carica_brutale', {
    name: 'Carica Brutale',
    onomatopoeia: 'ドドドド!',
    onomatopoeiaAlt: 'DODODO!',
    color: '#5D4037',
    secondaryColor: '#FF7043',
    icon: '🐂',
    type: 'sweep',
    duration: 850,
  });
  
  registerMoveAnimation('corpo_corazzato', {
    name: 'Corpo Corazzato',
    onomatopoeia: 'カキン!',
    onomatopoeiaAlt: 'KAKIN!',
    color: '#78909C',
    secondaryColor: '#B0BEC5',
    icon: '🛡️',
    type: 'shield',
    duration: 600,
  });
  
  registerMoveAnimation('impatto_sismico', {
    name: 'Impatto Sismico',
    onomatopoeia: 'ズゴゴゴ!',
    onomatopoeiaAlt: 'ZUGOGO!',
    color: '#6D4C41',
    secondaryColor: '#BCAAA4',
    icon: '🌋',
    type: 'impact',
    duration: 900,
  });

  // === MOSSE RAZZA: GIGANTE ===
  registerMoveAnimation('pugno_gigante', {
    name: 'Pugno del Gigante',
    onomatopoeia: 'ドォォン!',
    onomatopoeiaAlt: 'DOOON!',
    color: '#795548',
    secondaryColor: '#FF5722',
    icon: '🤜',
    type: 'impact',
    duration: 1000,
  });
  
  registerMoveAnimation('calpestamento', {
    name: 'Calpestamento',
    onomatopoeia: 'ズシン!',
    onomatopoeiaAlt: 'ZUSHIN!',
    color: '#4E342E',
    secondaryColor: '#8D6E63',
    icon: '🦶',
    type: 'impact',
    duration: 900,
  });

  // === MOSSE RAZZA: VISONE ===
  registerMoveAnimation('electro', {
    name: 'Electro',
    onomatopoeia: 'ビリビリ!',
    onomatopoeiaAlt: 'BIRIBIRI!',
    color: '#FFEB3B',
    secondaryColor: '#FFF176',
    icon: '⚡',
    type: 'impact',
    duration: 550,
  });
  
  registerMoveAnimation('forma_sulong', {
    name: 'Forma Sulong',
    onomatopoeia: 'ゴゴゴゴ!',
    onomatopoeiaAlt: 'GOGOGO!',
    color: '#E1F5FE',
    secondaryColor: '#B3E5FC',
    icon: '🌕',
    type: 'shield',
    duration: 1200,
  });

  // === MOSSE RAZZA: CYBORG ===
  registerMoveAnimation('cannone_interno', {
    name: 'Cannone Interno',
    onomatopoeia: 'ドカーン!',
    onomatopoeiaAlt: 'DOKAAN!',
    color: '#FF5722',
    secondaryColor: '#FFC107',
    icon: '💣',
    type: 'impact',
    duration: 700,
  });
  
  registerMoveAnimation('pugno_razzo', {
    name: 'Pugno Razzo',
    onomatopoeia: 'シュバッ!',
    onomatopoeiaAlt: 'SHUBA!',
    color: '#F44336',
    secondaryColor: '#FF9800',
    icon: '🚀',
    type: 'sweep',
    duration: 650,
  });

  // === MOSSE STILE: ARTI MARZIALI ===
  registerMoveAnimation('combo_marziale', {
    name: 'Combo Marziale',
    onomatopoeia: 'アタタタ!',
    onomatopoeiaAlt: 'ATATATA!',
    color: '#E91E63',
    secondaryColor: '#F48FB1',
    icon: '🥋',
    type: 'impact',
    duration: 800,
  });
  
  registerMoveAnimation('calcio_rotante', {
    name: 'Calcio Rotante',
    onomatopoeia: 'グルン!',
    onomatopoeiaAlt: 'GURUN!',
    color: '#9C27B0',
    secondaryColor: '#CE93D8',
    icon: '🌀',
    type: 'sweep',
    duration: 700,
  });

  // === MOSSE ARMA: SPADA ===
  registerMoveAnimation('fendente_spada', {
    name: 'Fendente',
    onomatopoeia: 'ザシュッ!',
    onomatopoeiaAlt: 'ZASHU!',
    color: '#9E9E9E',
    secondaryColor: '#E0E0E0',
    icon: '⚔️',
    type: 'sweep',
    duration: 500,
  });
  
  registerMoveAnimation('stoccata_spada', {
    name: 'Stoccata',
    onomatopoeia: 'ズバッ!',
    onomatopoeiaAlt: 'ZUBA!',
    color: '#607D8B',
    secondaryColor: '#B0BEC5',
    icon: '🗡️',
    type: 'impact',
    duration: 450,
  });

  // === CARTE COMBATTIMENTO ===
  registerMoveAnimation('carta_attacco_sorpresa', {
    name: 'Attacco Sorpresa',
    onomatopoeia: 'ハッ!',
    onomatopoeiaAlt: 'HA!',
    color: '#673AB7',
    secondaryColor: '#B39DDB',
    icon: '🃏',
    type: 'impact',
    duration: 550,
  });
  
  registerMoveAnimation('carta_guarigione', {
    name: 'Guarigione',
    onomatopoeia: 'キラーン!',
    onomatopoeiaAlt: 'KIRAAN!',
    color: '#4CAF50',
    secondaryColor: '#A5D6A7',
    icon: '💚',
    type: 'shield',
    duration: 800,
  });
};

// Inizializza le animazioni speciali
registerSpecialMoveAnimations();

/**
 * Hook per gestire le animazioni in battaglia
 */
export const useBattleAnimations = () => {
  const [animationState, setAnimationState] = useState({
    isPlaying: false,
    moveId: null,
    options: {},
  });

  const playMoveAnimation = useCallback((moveId, options = {}) => {
    return new Promise((resolve) => {
      setAnimationState({
        isPlaying: true,
        moveId,
        options,
        onComplete: resolve,
      });
    });
  }, []);

  const handleAnimationComplete = useCallback(() => {
    const { onComplete } = animationState;
    setAnimationState({
      isPlaying: false,
      moveId: null,
      options: {},
    });
    if (onComplete) onComplete();
  }, [animationState]);

  const BattleAnimationOverlay = useCallback(() => {
    if (!animationState.isPlaying) return null;

    const { moveId, options } = animationState;
    const config = getMoveAnimationConfig(moveId);

    return (
      <div 
        className={`
          fixed inset-0 z-50 flex items-center justify-center
          ${options.isCritical ? 'critical-hit' : ''}
          ${options.isMiss ? 'miss-effect' : ''}
          ${options.shakeScreen ? 'shake-on-impact' : ''}
        `}
        style={{ 
          backgroundColor: 'rgba(0,0,0,0.4)',
          backdropFilter: 'blur(2px)'
        }}
      >
        {/* Player indicator */}
        {options.attackerName && (
          <div className="absolute top-8 left-1/2 transform -translate-x-1/2 text-white text-xl font-bold">
            <span style={{ color: config.color }}>{options.attackerName}</span>
            <span className="text-gray-300"> usa </span>
            <span className="text-yellow-400">{config.name}</span>
          </div>
        )}

        {/* Main animation */}
        <MoveAnimation
          moveId={moveId}
          isPlaying={true}
          onComplete={handleAnimationComplete}
          size="large"
          showOnomatopoeia={!options.hideText}
        />

        {/* Damage number (if provided) */}
        {options.damage !== undefined && options.damage > 0 && (
          <div 
            className={`
              absolute bottom-1/4 text-6xl font-black
              ${options.isCritical ? 'text-yellow-400 animate-bounce' : 'text-red-500'}
            `}
            style={{
              textShadow: '3px 3px 0 #000, -1px -1px 0 #000',
              animation: 'damage-pop 0.5s ease-out forwards'
            }}
          >
            -{options.damage}
          </div>
        )}

        {/* Status effect indicator */}
        {options.statusEffect && (
          <div className="absolute bottom-8 text-center text-white">
            <span className="bg-purple-600/80 px-4 py-2 rounded-full">
              {options.statusEffect}
            </span>
          </div>
        )}
      </div>
    );
  }, [animationState, handleAnimationComplete]);

  return {
    playMoveAnimation,
    isAnimating: animationState.isPlaying,
    BattleAnimationOverlay,
  };
};

/**
 * Componente standalone per mostrare l'animazione di una mossa
 */
export const BattleMoveDisplay = ({ 
  moveId, 
  attacker, 
  defender, 
  damage,
  isCritical,
  isMiss,
  onComplete 
}) => {
  const config = getMoveAnimationConfig(moveId);

  return (
    <div className="relative w-full h-64 bg-gradient-to-r from-gray-900 to-gray-800 rounded-xl overflow-hidden">
      {/* Battle scene background */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_transparent_0%,_black_100%)]" />
      </div>

      {/* Attacker side */}
      <div className="absolute left-4 top-1/2 -translate-y-1/2 text-center">
        <div className="text-4xl mb-2">👤</div>
        <div className="text-white font-bold">{attacker}</div>
      </div>

      {/* Animation in center */}
      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
        <MoveAnimation
          moveId={moveId}
          isPlaying={true}
          onComplete={onComplete}
          size="medium"
        />
      </div>

      {/* Defender side */}
      <div className="absolute right-4 top-1/2 -translate-y-1/2 text-center">
        <div className="text-4xl mb-2">👤</div>
        <div className="text-white font-bold">{defender}</div>
        {damage > 0 && (
          <div className={`text-2xl font-bold ${isCritical ? 'text-yellow-400' : 'text-red-500'}`}>
            -{damage}
          </div>
        )}
      </div>

      {/* Move name banner */}
      <div 
        className="absolute bottom-0 left-0 right-0 py-2 text-center"
        style={{ backgroundColor: `${config.color}CC` }}
      >
        <span className="text-white font-bold text-lg">
          {config.icon} {config.name} {config.icon}
        </span>
      </div>
    </div>
  );
};

export default useBattleAnimations;
