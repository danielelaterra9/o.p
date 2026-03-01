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

### Backend v2 (FastAPI + MongoDB)
- ✅ Auth system con USERNAME separato dal nome personaggio
- ✅ Validazione nome personaggio (blocca "D." e "D ")
- ✅ 6 Razze con bonus stats: Umano, Uomo Pesce, Visone, Semi-gigante, Gigante, Cyborg
- ✅ 6 Stili di combattimento con vantaggi/svantaggi
- ✅ 12 Mestieri con abilità uniche (Capitano, Guerriero, Navigatore, Cecchino, Cuoco, Medico, Archeologo, Carpentiere, Musicista, Timoniere, Scienziato, Ipnotista)
- ✅ Sistema stats completo: Vita, Energia, ATK=FORxVEL, DEF=RESxAGI
- ✅ Aspettativa di vita con modificatori genere/razza
- ✅ AI Trait extraction dal carattere del personaggio
- ✅ Scheda personaggio con info PUBBLICHE e PRIVATE
- ✅ Battle system semplificato (no narrazione romanzata)
- ✅ Shop e World Map

### Frontend v2 (React + Framer Motion)
- ✅ Registrazione con campo USERNAME
- ✅ Character creation wizard 7 step:
  1. Nome personaggio (con validazione D.)
  2. Genere (M/F/Non definito) + Età (min 16)
  3. Razza con info vantaggi/svantaggi
  4. Stile combattimento con info
  5. Mestiere (12 scelte)
  6. Sogno (100 char) + Storia (1000 char) + AI traits
  7. Aspetto fisico + Riepilogo
- ✅ Dashboard con nuovi stats
- ✅ Character Sheet con toggle pubblico/privato
- ✅ Battle Arena semplificata

## Prioritized Backlog

### P0 (Critical - Next Sprint)
- [ ] Sistema dado virtuale con animazione nave
- [ ] Chat real-time (WebSocket)
- [ ] Sistema crew (ciurma multiplayer)

### P1 (High Priority)
- [ ] Carte con effetti gameplay reali
- [ ] Eventi/missioni completabili su isole
- [ ] Sistema economico Berry funzionante
- [ ] Livelli mestiere (principiante→esperto)

### P2 (Medium Priority)
- [ ] Haki unlock durante storia
- [ ] Trading tra giocatori
- [ ] Sistema navi con upgrade
- [ ] Frutti del Diavolo con abilità speciali

### P3 (Nice to Have)
- [ ] Sound effects
- [ ] Animazioni combattimento avanzate
- [ ] Leaderboard
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
5. Zone isola con eventi/missioni
