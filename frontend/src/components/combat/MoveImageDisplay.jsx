import React, { useState, useEffect, useCallback } from 'react';

/**
 * MoveImageDisplay - Mostra l'immagine AI di una mossa durante il combattimento
 * 
 * Le immagini sono generate una volta dall'AI e salvate nel database.
 * Stile ispirato a One Piece senza violare copyright.
 */

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';

// Cache locale per le immagini già caricate
const imageCache = new Map();

/**
 * Hook per gestire le immagini delle mosse
 */
export const useMoveImage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const getMoveImageUrl = useCallback((moveId) => {
    return `${BACKEND_URL}/api/moves/image/${moveId}`;
  }, []);

  const getMoveImageBase64 = useCallback(async (moveId, token) => {
    // Controlla cache
    if (imageCache.has(moveId)) {
      return imageCache.get(moveId);
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${BACKEND_URL}/api/moves/image/${moveId}/base64`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        if (response.status === 404) {
          return null; // Immagine non ancora generata
        }
        throw new Error('Errore caricamento immagine');
      }

      const data = await response.json();
      imageCache.set(moveId, data.image_base64);
      return data.image_base64;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const generateMoveImage = useCallback(async (moveId, token) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${BACKEND_URL}/api/moves/generate-image/${moveId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Errore generazione immagine');
      }

      const data = await response.json();
      // Invalida cache
      imageCache.delete(moveId);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    getMoveImageUrl,
    getMoveImageBase64,
    generateMoveImage,
    isLoading,
    error
  };
};

/**
 * Componente per mostrare l'immagine di una mossa
 */
const MoveImage = ({ 
  moveId, 
  moveName,
  size = 'medium', // small, medium, large
  showName = true,
  className = '',
  onError,
  fallbackIcon = '⚔️'
}) => {
  const [imageError, setImageError] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);
  const { getMoveImageUrl } = useMoveImage();

  const sizeClasses = {
    small: 'w-24 h-24',
    medium: 'w-48 h-48',
    large: 'w-72 h-72',
    full: 'w-full h-full'
  };

  const handleError = () => {
    setImageError(true);
    if (onError) onError();
  };

  const handleLoad = () => {
    setIsLoaded(true);
  };

  if (imageError) {
    return (
      <div className={`${sizeClasses[size]} ${className} flex flex-col items-center justify-center bg-gray-800/50 rounded-xl border-2 border-gray-600`}>
        <span className="text-6xl mb-2">{fallbackIcon}</span>
        {showName && <span className="text-white font-bold text-center px-2">{moveName || moveId}</span>}
        <span className="text-gray-400 text-xs mt-1">Immagine non disponibile</span>
      </div>
    );
  }

  return (
    <div className={`${sizeClasses[size]} ${className} relative overflow-hidden rounded-xl`}>
      {/* Loading skeleton */}
      {!isLoaded && (
        <div className="absolute inset-0 bg-gray-800 animate-pulse flex items-center justify-center">
          <span className="text-4xl animate-bounce">{fallbackIcon}</span>
        </div>
      )}
      
      {/* Immagine */}
      <img
        src={getMoveImageUrl(moveId)}
        alt={moveName || moveId}
        className={`w-full h-full object-cover transition-opacity duration-300 ${isLoaded ? 'opacity-100' : 'opacity-0'}`}
        onError={handleError}
        onLoad={handleLoad}
      />
      
      {/* Nome mossa overlay */}
      {showName && isLoaded && (
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-2">
          <p className="text-white font-bold text-center text-sm">{moveName || moveId}</p>
        </div>
      )}
    </div>
  );
};

/**
 * Componente per l'animazione durante il combattimento
 * Mostra l'immagine della mossa con effetti visivi
 */
export const BattleMoveAnimation = ({
  moveId,
  moveName,
  attackerName,
  defenderName,
  damage,
  isPlaying = false,
  onComplete,
  duration = 2000
}) => {
  const [phase, setPhase] = useState('idle'); // idle, enter, display, exit
  const { getMoveImageUrl } = useMoveImage();

  useEffect(() => {
    if (isPlaying) {
      setPhase('enter');
      
      // Fase display
      const displayTimer = setTimeout(() => {
        setPhase('display');
      }, 300);

      // Fase exit
      const exitTimer = setTimeout(() => {
        setPhase('exit');
      }, duration - 300);

      // Completamento
      const completeTimer = setTimeout(() => {
        setPhase('idle');
        if (onComplete) onComplete();
      }, duration);

      return () => {
        clearTimeout(displayTimer);
        clearTimeout(exitTimer);
        clearTimeout(completeTimer);
      };
    }
  }, [isPlaying, duration, onComplete]);

  if (phase === 'idle') return null;

  return (
    <div 
      className={`
        fixed inset-0 z-50 flex items-center justify-center
        bg-black/70 backdrop-blur-sm
        transition-opacity duration-300
        ${phase === 'enter' ? 'opacity-0' : 'opacity-100'}
        ${phase === 'exit' ? 'opacity-0' : ''}
      `}
    >
      {/* Container principale */}
      <div 
        className={`
          relative max-w-2xl w-full mx-4
          transition-all duration-500
          ${phase === 'enter' ? 'scale-50 rotate-12' : 'scale-100 rotate-0'}
          ${phase === 'exit' ? 'scale-150 opacity-0' : ''}
        `}
      >
        {/* Header con nomi */}
        <div className="flex justify-between items-center mb-4 px-4">
          <div className="text-left">
            <span className="text-yellow-400 font-bold text-xl">{attackerName}</span>
            <p className="text-gray-400 text-sm">Attaccante</p>
          </div>
          <div className="text-4xl">⚔️</div>
          <div className="text-right">
            <span className="text-red-400 font-bold text-xl">{defenderName}</span>
            <p className="text-gray-400 text-sm">Difensore</p>
          </div>
        </div>

        {/* Immagine mossa con cornice */}
        <div className="relative">
          {/* Bordo luminoso */}
          <div className="absolute -inset-1 bg-gradient-to-r from-yellow-500 via-red-500 to-yellow-500 rounded-2xl blur-sm animate-pulse" />
          
          {/* Container immagine */}
          <div className="relative bg-gray-900 rounded-2xl overflow-hidden border-4 border-yellow-500/50">
            <MoveImage
              moveId={moveId}
              moveName={moveName}
              size="full"
              showName={false}
              className="aspect-video"
            />
            
            {/* Overlay effetti */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/30" />
            
            {/* Nome mossa grande */}
            <div className="absolute top-4 left-0 right-0 text-center">
              <h2 
                className="text-3xl md:text-4xl font-black text-white uppercase tracking-wider"
                style={{
                  textShadow: '3px 3px 0 #000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 0 3px 6px rgba(0,0,0,0.5)'
                }}
              >
                {moveName || moveId}
              </h2>
            </div>

            {/* Danno */}
            {damage !== undefined && damage > 0 && (
              <div 
                className="absolute bottom-4 right-4 text-5xl md:text-6xl font-black text-red-500 animate-bounce"
                style={{
                  textShadow: '3px 3px 0 #000, -1px -1px 0 #000'
                }}
              >
                -{damage}
              </div>
            )}
          </div>
        </div>

        {/* Linee di velocità decorative */}
        <div className="absolute -left-20 top-1/2 -translate-y-1/2 opacity-50">
          {[...Array(5)].map((_, i) => (
            <div 
              key={i}
              className="h-1 bg-gradient-to-r from-transparent via-yellow-400 to-transparent mb-2"
              style={{
                width: `${100 + i * 20}px`,
                animationDelay: `${i * 100}ms`,
                animation: 'slideRight 0.5s ease-out forwards'
              }}
            />
          ))}
        </div>
        
        <div className="absolute -right-20 top-1/2 -translate-y-1/2 opacity-50 rotate-180">
          {[...Array(5)].map((_, i) => (
            <div 
              key={i}
              className="h-1 bg-gradient-to-r from-transparent via-red-400 to-transparent mb-2"
              style={{
                width: `${100 + i * 20}px`,
                animationDelay: `${i * 100}ms`,
                animation: 'slideRight 0.5s ease-out forwards'
              }}
            />
          ))}
        </div>
      </div>

      {/* Stili animazione */}
      <style>{`
        @keyframes slideRight {
          from {
            transform: translateX(-100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 0.5;
          }
        }
      `}</style>
    </div>
  );
};

/**
 * Hook per usare le animazioni in battaglia
 */
export const useBattleMoveAnimation = () => {
  const [animationState, setAnimationState] = useState({
    isPlaying: false,
    moveId: null,
    moveName: null,
    attackerName: null,
    defenderName: null,
    damage: null
  });

  const playMoveAnimation = useCallback((params) => {
    return new Promise((resolve) => {
      setAnimationState({
        isPlaying: true,
        ...params,
        onComplete: () => {
          setAnimationState(prev => ({ ...prev, isPlaying: false }));
          resolve();
        }
      });
    });
  }, []);

  const BattleAnimationOverlay = useCallback(() => {
    if (!animationState.isPlaying) return null;

    return (
      <BattleMoveAnimation
        moveId={animationState.moveId}
        moveName={animationState.moveName}
        attackerName={animationState.attackerName}
        defenderName={animationState.defenderName}
        damage={animationState.damage}
        isPlaying={true}
        onComplete={animationState.onComplete}
      />
    );
  }, [animationState]);

  return {
    playMoveAnimation,
    isAnimating: animationState.isPlaying,
    BattleAnimationOverlay
  };
};

/**
 * Griglia per visualizzare tutte le immagini delle mosse
 */
export const MoveImageGrid = ({ moves, onMoveClick }) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 p-4">
      {moves.map((move) => (
        <div 
          key={move.id}
          className="cursor-pointer transform transition-transform hover:scale-105"
          onClick={() => onMoveClick && onMoveClick(move)}
        >
          <MoveImage
            moveId={move.id}
            moveName={move.nome}
            size="medium"
          />
        </div>
      ))}
    </div>
  );
};

export default MoveImage;
