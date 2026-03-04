/**
 * Combat Animation System - Stile One Piece
 * 
 * Esporta tutti i componenti e hooks per le animazioni di combattimento
 */

// Componente principale animazione mossa
export { default as MoveAnimation } from './MoveAnimation';
export { useMoveAnimation, getMoveAnimationConfig, registerMoveAnimation } from './MoveAnimation';

// Manager animazioni battaglia
export { default as useBattleAnimations } from './BattleAnimationManager';
export { BattleMoveDisplay } from './BattleAnimationManager';

// Demo per testing
export { default as MoveAnimationDemo } from './MoveAnimationDemo';

// CSS (deve essere importato separatamente)
// import './MoveAnimation.css';
