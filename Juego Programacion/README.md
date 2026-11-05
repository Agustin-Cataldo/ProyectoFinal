# Steam & Blade: Elemental Odyssey

> **Hack & Slash Roguelike 2D — Retro Pixel Art (Dark Steampunk & Medieval Gothic)**  
> **Motor:** Python 3 + `pygame-ce` (60 FPS estables, Double Buffering y Delta Time cinemático)  
> **Estado:** Release Final — 100% de objetivos cumplidos, 0 errores.

---

## 1. Resumen de Características y Reglas de Juego

| Parámetro | Regla / Valor | Módulos Clave |
|---|---|---|
| **Estructura** | 50 Niveles divididos en 5 Mazmorras de 10 niveles c/u | `systems/dungeon_manager.py` |
| **Jefes Elementales** | Nivel 10 de cada Mazmorra (10 Jefes Colosales de 3000 HP con 20 ataques firma) | `entities/boss.py` |
| **Temas Elementales** | 10 elementos que se aleatorizan al iniciar/reiniciar partida | `settings.py` |
| **Estadísticas Jugador** | 1000 HP base, 500 MP de Maná, 70 DMG inicial (50 base + 20 espada de piedra) | `settings.py`, `entities/player.py` |
| **12 Personajes Legendarios** | Héroes con armas, pasivas y barajas temáticas exclusivas (estilo Slay the Spire 2) | `systems/role_system.py`, `ui/role_menu.py` |
| **13 Armas Medievales** | Hacha, Maza, Dagas, Ballesta, Guadaña, Bastón, Cañón, Tótem, Mangual, etc. | `entities/weapons.py`, `utils/asset_loader.py` |
| **600 Cartas de Mejora** | 50 cartas exclusivas por personaje + 32 estándar + 16 doradas | `systems/character_cards_database.py` |
| **Regla de Magia Exclusiva** | Magias de **Oscuridad y Luz** exclusivas de Cartas Doradas | `systems/card_system.py` |
| **Bestiario Completo (16 Tipos)**| 10 autómatas comunes y tácticos, 1 invocación, 5 espíritus élite | `entities/enemy.py` |
| **Menú de Pausa Modal** | Acceso con `[ESC]` o `[P]`, simulación congelada, estadísticas y controles | `ui/pause_menu.py` |
| **Motor de Audio Procedural** | 39 efectos de sonido (SFX) y 3 temas musicales (BGM) sintetizados matemáticamente | `systems/audio_system.py`, `assets/audio/` |
| **Combate y Supervivencia** | Dash con i-frames `[Espacio]`, Curación de Paciencia (+10 HP tras 10s sin daño) | `entities/player.py` |

---

## 2. Controles de Juego

* **Mover al Héroe:** Teclas `[W]`, `[A]`, `[S]`, `[D]` o Flechas del teclado.
* **Apuntar:** Movimiento del ratón (giro cinemático de 360 grados).
* **Ataque Principal:** `Clic Izquierdo` del ratón.
* **Hechizo Mágico Primario:** Tecla `[1]` (Consume Maná).
* **Hechizo Mágico Secundario:** Tecla `[2]` (Consume Maná).
* **Impulso de Vapor (Dash):** `Barra Espaciadora` (Otorga cuadros de invulnerabilidad).
* **Menú de Pausa:** Tecla `[ESC]` o tecla `[P]`.
* **Silenciar / Activar Audio:** Tecla `[M]`.
* **Ajustar Volumen:** Teclas `[+]` y `[-]`.

---

## 3. Instrucciones de Ejecución

### Opción A (Recomendada con un clic):
Haz doble clic en:
```bat
run_game.bat
```

### Opción B (Desde Consola / PowerShell):
```powershell
py -m pip install -r requirements.txt
py main.py
```

### Batería Integral de Pruebas:
```powershell
py test_integrity.py
py test_new_enemies.py
py audit_all_systems.py
```
