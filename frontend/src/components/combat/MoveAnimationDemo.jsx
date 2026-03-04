import React, { useState } from 'react';
import MoveAnimation, { useMoveAnimation, getMoveAnimationConfig } from './MoveAnimation';
import './MoveAnimation.css';

/**
 * Demo Component per testare le animazioni delle mosse
 * Mostra tutte le mosse disponibili con i loro effetti
 */
const MoveAnimationDemo = () => {
  const [selectedMove, setSelectedMove] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const { playAnimation, AnimationComponent } = useMoveAnimation();

  const moves = [
    { id: 'pugno', name: 'Pugno', type: 'Attacco', stats: 'EN: -1 | CD: 1 | Dist: 1' },
    { id: 'gomitata', name: 'Gomitata', type: 'Attacco', stats: 'EN: -1 | CD: 1 | Dist: 1' },
    { id: 'ginocchiata', name: 'Ginocchiata', type: 'Attacco', stats: 'EN: -1 | CD: 1 | Dist: 1' },
    { id: 'testata', name: 'Testata', type: 'Attacco', stats: 'EN: -1 | CD: 1 | Dist: 1' },
    { id: 'calcio', name: 'Calcio', type: 'Attacco', stats: 'EN: -2 | CD: 1.5 | Dist: 2' },
    { id: 'schivata', name: 'Schivata', type: 'Difesa', stats: 'EN: -2 | CD: 0 | Dist: 2-5' },
    { id: 'parata', name: 'Parata', type: 'Difesa', stats: 'EN: -2 | CD: 0 | Tutte' },
    { id: 'protezione', name: 'Protezione', type: 'Difesa', stats: 'EN: -4 | CD: 0 | Tutte' },
  ];

  const handlePlayAnimation = (moveId) => {
    setSelectedMove(moveId);
    setIsPlaying(true);
  };

  const handleAnimationComplete = () => {
    setIsPlaying(false);
    setSelectedMove(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-2">
            ⚔️ Sistema Animazioni Mosse
          </h1>
          <p className="text-blue-300">Stile One Piece - Clicca su una mossa per vedere l'animazione</p>
        </div>

        {/* Animation Display Area */}
        <div className="relative bg-black/50 rounded-2xl p-8 mb-8 min-h-[300px] flex items-center justify-center border-2 border-yellow-500/30">
          {isPlaying ? (
            <MoveAnimation
              moveId={selectedMove}
              isPlaying={isPlaying}
              onComplete={handleAnimationComplete}
              size="large"
            />
          ) : (
            <div className="text-center text-gray-400">
              <span className="text-6xl mb-4 block">🎬</span>
              <p>Seleziona una mossa per vedere l'animazione</p>
            </div>
          )}
        </div>

        {/* Move Buttons Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {moves.map((move) => {
            const config = getMoveAnimationConfig(move.id);
            return (
              <button
                key={move.id}
                onClick={() => handlePlayAnimation(move.id)}
                disabled={isPlaying}
                className={`
                  relative p-4 rounded-xl transition-all duration-300
                  ${isPlaying ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105 hover:shadow-lg'}
                  ${move.type === 'Attacco' ? 'bg-red-900/50 hover:bg-red-800/50' : 'bg-blue-900/50 hover:bg-blue-800/50'}
                  border-2 border-transparent hover:border-yellow-500/50
                `}
                style={{
                  boxShadow: `0 0 20px ${config.color}30`
                }}
              >
                {/* Icon */}
                <span className="text-4xl block mb-2">{config.icon}</span>
                
                {/* Name */}
                <h3 className="text-white font-bold text-lg">{move.name}</h3>
                
                {/* Type Badge */}
                <span className={`
                  inline-block px-2 py-1 rounded text-xs mt-1
                  ${move.type === 'Attacco' ? 'bg-red-600' : 'bg-blue-600'}
                  text-white
                `}>
                  {move.type}
                </span>
                
                {/* Stats */}
                <p className="text-gray-400 text-xs mt-2">{move.stats}</p>
                
                {/* Onomatopoeia preview */}
                <p 
                  className="text-sm font-bold mt-2"
                  style={{ color: config.color }}
                >
                  {config.onomatopoeiaAlt}
                </p>
              </button>
            );
          })}
        </div>

        {/* Legend */}
        <div className="mt-8 p-4 bg-black/30 rounded-xl">
          <h3 className="text-yellow-400 font-bold mb-2">📖 Legenda</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-300">
            <div>
              <span className="text-red-400">EN:</span> Energia
            </div>
            <div>
              <span className="text-yellow-400">CD:</span> Coefficiente Danno
            </div>
            <div>
              <span className="text-blue-400">Dist:</span> Distanza Max
            </div>
            <div>
              <span className="text-green-400">Tipo:</span> Attacco/Difesa
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MoveAnimationDemo;
