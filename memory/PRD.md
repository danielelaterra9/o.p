# The Grand Line Architect - PRD

## Problem Statement
RPG One Piece con 4 piani di gioco:
1. **Mappa e Storytelling** - Navigazione con dado virtuale, carte storytelling
2. **Eventi e Interazioni** - Missioni, zone isola, NPC, chat
3. **Schede Personaggio** - Stats, inventario, carte collezionabili
4. **Combattimento** - Stile Pokemon GameBoy, turni con timer, AI narrator

## User Personas
- Fan di One Piece (14-35 anni)
- Giocatori RPG casual e hardcore
- Utenti italiani principalmente

## Core Requirements (Static)
- Single player + multiplayer online + NPC bot
- Sistema carte collezionabili (Storytelling, Eventi, Duello, Risorse)
- Combattimento a turni con timer (3 min/turno, 20 min totale)
- AI Narrator per combattimento (Gemini 3 Flash)
- Generazione immagini AI (Gemini Nano Banana)
- Login email/password + Google OAuth

## What's Been Implemented (2026-03-01)

### Backend (FastAPI + MongoDB)
- ✅ Auth system (JWT + Google OAuth via Emergent)
- ✅ Character CRUD con stats calcolati
- ✅ World Map con 12 isole (East Blue → Grand Line → New World)
- ✅ Battle system a turni con formule danno
- ✅ AI Narration endpoint (Gemini 3 Flash)
- ✅ AI Avatar generation endpoint (Gemini Nano Banana)
- ✅ Shop system
- ✅ Cards collection system
- ✅ Island zones e NPC interactions

### Frontend (React + Framer Motion)
- ✅ Landing page con tema oceano
- ✅ Auth pages (Login, Register, Google OAuth callback)
- ✅ Character creation wizard (4 steps)
- ✅ Dashboard con stats e menu
- ✅ World Map con isole interattive
- ✅ Island Explorer con zone
- ✅ Battle Arena (stile GameBoy)
- ✅ Character Sheet
- ✅ Card Collection
- ✅ Shop

## Prioritized Backlog

### P0 (Critical - Next Sprint)
- [ ] Sistema dado virtuale completo con animazione nave
- [ ] Chat real-time (WebSocket) per interazioni
- [ ] Crew system (ciurma multiplayer)

### P1 (High Priority)
- [ ] Carte Storytelling con effetti gameplay
- [ ] Sistema eventi/missioni completabili
- [ ] Inventario dettagliato con uso oggetti
- [ ] Sistema economico (Berry) funzionante

### P2 (Medium Priority)
- [ ] Haki unlock tramite eventi speciali
- [ ] Trading system tra giocatori
- [ ] Sistema navi con upgrade
- [ ] Frutti del Diavolo con abilità speciali in battaglia

### P3 (Nice to Have)
- [ ] Sound effects e musica
- [ ] Animazioni combattimento avanzate
- [ ] Leaderboard e classifiche
- [ ] Storia principale con dialoghi

## Technical Stack
- Backend: FastAPI, MongoDB, emergentintegrations
- Frontend: React, Framer Motion, Tailwind CSS
- AI: Gemini 3 Flash (text), Gemini Nano Banana (images)
- Auth: JWT + Emergent Google OAuth

## Next Tasks
1. Implementare sistema dado con animazione nave
2. Aggiungere WebSocket per chat real-time
3. Sistema crew con join/leave
4. Carte con effetti concreti
5. Missioni ed eventi completabili
