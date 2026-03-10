# NumCrunch Academy 🎮🦕

<div align="center">

![NumCrunch Academy Banner](https://github.com/moderatedan/NumCrunch-Academy/raw/main/media/screenshots/banner.jpg)

**Math = Escape! Solve problems, dodge the dinosaur, avoid bombs, and level up through epic stages.**

[![Download AppImage](https://img.shields.io/badge/Download-v2.0_AppImage-FF6B00?style=for-the-badge&logo=linux&logoColor=white)](https://github.com/moderatedan/NumCrunch-Academy/releases/latest/download/NumCrunch_Academy.AppImage)
&nbsp;&nbsp;
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## 🕹️ About

A math game I made for my son — just like Number Munchers helped me learn primes and multiplication tables back in the day, but with cooler characters and a dinosaur bad guy to make it more intense.

Navigate the grid, find the correct answer, and munch it before the dino catches you. As your score climbs, the game gets harder — new operations, faster enemies, and bombs on the board.

Free and open-source. A future Android version will have one small ad (or just $1 for no ads).

![Gameplay Screenshot](https://github.com/moderatedan/NumCrunch-Academy/raw/main/media/screenshots/game_screenshot.jpg)

---

## ✨ Features

**Stage Progression System**
- 🟢 **Stage 1 — Neon Classroom** (0-49 pts): Addition & subtraction. The dino is slow. Learn the ropes.
- 🟡 **Stage 2 — Chalkboard Challenge** (50-99 pts): Multiplication joins the mix. Dino speeds up. Bombs appear on the grid.
- 🔴 **Stage 3 — Venice Voyage** (100+ pts): All 4 operations including division. The dino is relentless. More bombs.

**Combat & Effects**
- 💣 Visible bombs on the grid — step on one and BOOM, you lose a life with explosion particles
- 💀 Epic skull death animation — screen shakes, skull zooms in, then GAME OVER
- 🎉 Confetti burst when you level up
- 💥 Screen shake and player flash when the dino catches you
- ❤️ Bonus life awarded at each stage transition

**Gameplay**
- 🦕 Dinosaur enemy that actively chases you — gets faster each stage
- 🔊 Sound effects: munch, hurt, victory, background music
- 🎨 Custom sprites: green blob player, armored T-Rex enemy
- 🖼️ Unique hand-crafted backgrounds for each stage

---

## 🚀 Download & Play

### Linux (AppImage — one click, no install)

```bash
# Download the AppImage
wget https://github.com/moderatedan/NumCrunch-Academy/releases/latest/download/NumCrunch_Academy.AppImage

# Make it executable
chmod +x NumCrunch_Academy.AppImage

# Run it
./NumCrunch_Academy.AppImage
```

### Run from Source

```bash
# Clone the repo
git clone https://github.com/moderatedan/NumCrunch-Academy.git
cd NumCrunch-Academy

# Install pygame
pip install pygame

# Launch
cd build/AppDir/usr/bin
python3 NumCrunch_Academy.py
```

### Requirements (source only)
- Python 3.8+
- Pygame 2.0+

---

## 🎮 Controls

| Key | Action |
|-----|--------|
| ⬆️⬇️⬅️➡️ Arrow Keys | Move around the grid |
| Move onto correct answer | Auto-munches it! |
| Avoid the dinosaur | He chases you! |
| Avoid bombs | They explode on contact! |

---

## 📋 Roadmap

- [x] Stage progression with 3 unique backgrounds
- [x] Scaling difficulty (operations, enemy speed, bombs)
- [x] Confetti, explosions, screen shake effects
- [x] Skull game over animation
- [x] AppImage for Linux
- [ ] Snap Store release
- [ ] Flatpak release
- [ ] Android version (free with small ad / $1 ad-free)
- [ ] High score leaderboard
- [ ] More stages and backgrounds
- [ ] Boss battles

---

## 🛠️ Built With

- **Python 3** + **Pygame** — game engine
- **AppImage** — Linux distribution
- **Claude AI** — development partner
- Built on **Linux Mint** 🐧

---

## 📜 License

MIT License — free to use, modify, and distribute.

© 2025 Num Crunch Games | Daniel Brummitt

---

<div align="center">

**If you like the game, give it a ⭐ on GitHub!**

Made with ❤️ for kids who want to have fun while learning math.

</div>
