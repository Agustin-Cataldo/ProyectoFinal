# Clockwork Requiem
**Género:** Hack & Slash Roguelike 2D (Steampunk & Fantasía Medieval Gótica)  
**Motor / Framework:** Python 3.1x con `pygame-ce` (Pygame Community Edition)  
**Objetivo de Rendimiento:** 60 FPS estables  

---

## 1. Resumen de Reglas de Juego y Mecánicas Implementadas

| Parámetro | Valor / Regla | Implementación en Código |
|---|---|---|
| **Estructura** | 50 Niveles divididos en 5 Mazmorras (10 niveles c/u) | `systems/dungeon_manager.py` |
| **Combate con Jefes** | Nivel 10 de cada Mazmorra obligatorio | `entities/boss.py` (`ElementalBoss`) |
| **Elementos de Mazmorra** | 10 elementos posibles; se aleatorizan al reiniciar | `settings.py` -> `DUNGEON_ELEMENTS` |
| **Vida Base Jugador** | 1000 HP | `settings.py` -> `PLAYER_BASE_HP = 1000` |
| **Maná Base Jugador** | 500 MP (Gasto por hechizo, recarga +10 en melee y +50-75 al matar) | `settings.py`, `entities/player.py` |
| **Roles / Clases Medievales** | 6 Especializaciones: Berserker Bárbaro, Paladín Templario, Pícaro Sombrío, Mago Arcano, Cazador Real y Nigromante Abisal (o Sin Rol) | `systems/role_system.py`, `ui/role_menu.py` |
| **Armas y Animaciones Únicas** | Gran Hacha Bárbara, Maza Sagrada, Dagas Gemelas, Ballesta de Repetición, Guadaña Espectral, Bastón y Espada con animación de swing en arco y retroceso | `entities/weapons.py`, `utils/asset_loader.py`, `entities/player.py` |
| **Escalado de Dificultad** | +3.5% Vida y Daño a enemigos por nivel, mayor probabilidad de élites y jefes más feroces | `systems/dungeon_manager.py`, `entities/enemy.py` |
| **Daño Base Jugador** | 50 Puntos | `settings.py` -> `PLAYER_BASE_DAMAGE = 50` |
| **Arma Inicial** | Espada de piedra mediana (+20 Daño suplementario) | Total inicial = **70 DMG** |
| **Cartas Estándar** | Pool estricto de 32 cartas (Daño, Vida, Vel., Magia) | Selección de 1 de 3 cada 3 niveles |
| **Cartas Doradas** | Pool estricto de 16 cartas (Combos dobles / Únicas) | Probabilidad cada 5 niveles completados |
| **Regla Sagrada de Magia** | **Oscuridad y Luz son EXCLUSIVAS de Cartas Doradas** | Comprobado matemáticamente en `test_integrity.py` |
| **Controles y Habilidades** | Movimiento 8D, Espada [L-Click], Magias WoL Activas [R-Click / Q], Dash [Espacio] | `entities/player.py`, `game_engine.py` |
| **Gráficos y Hechizos Avanzados** | Estelas de cometa, 10 formas elementales animadas, magma burbujeante, vórtices y halos | `systems/combat_system.py` |
| **Animaciones Visuales** | Bamboleo de caminata, inclinación dinámica, estelas fantasma de dash y hit-flash blanco | `entities/player.py`, `entities/enemy.py`, `entities/boss.py` |
| **Bestiario Común** | Autómata Minero, Embestidor con Pistón, Tirador (Ráfaga Triple), Dron Volador y Demoledor | `entities/enemy.py` |
| **Espíritus Malignos (Élites)** | 5 Variantes con mecánicas elementales: Penumbra, Llama Fatua, Glacial, Tormenta, Nigromante | `entities/enemy.py` |
| **10 Jefes Elementales (Nivel 10)** | Arquetipos únicos con avisos telegrafiados (100% esquivables, No-Hit Viable) y Furia al < 50% HP | `entities/boss.py` |
| **Magia Elemental (WoL)** | Fuego (Lava), Agua (Tsunami), Viento (Vórtice Succionador), Tierra (Falla), Trueno (Arco Voltaico), Naturaleza (Zarzas), Luz (Estrella Sagrada), Oscuridad (Singularidad Abisal) | `systems/combat_system.py` |

---

## 2. Arquitectura de Software y Estructura Modular (SOLID)

El proyecto cumple estrictamente con el **Principio de Responsabilidad Única (SRP)**:

```
proyecto_hack_and_slash/
│
├── main.py                     # Punto de entrada. Inicialización gráfica y Double Buffering.
├── settings.py                 # Constantes globales, balance de stats y paletas de color.
├── game_engine.py              # Máquina de estados finita (State Pattern) y delta-time a 60 FPS.
├── test_integrity.py           # Batería de pruebas automatizadas y validación de reglas.
├── run_game.bat                # Lanzador rápido de un solo clic para Windows.
│
├── entities/
│   ├── player.py               # Clase Player: traslación 8D, hitboxes, 1000 HP y animación de swing.
│   ├── weapons.py              # Catálogo de Armas Medievales (Espada, Hacha, Maza, Dagas, Ballesta, Guadaña, Bastón).
│   ├── enemy.py                # Clase base Enemy, monstruos comunes y 5 variantes de espíritus élite.
│   └── boss.py                 # Clase ElementalBoss: patrones por fases y furia al < 50% HP.
│
├── systems/
│   ├── combat_system.py        # Detección de arcos de corte, números de daño y partículas.
│   ├── card_system.py          # Pool de 32 estándar + 16 doradas. Reglas de exclusividad.
│   ├── role_system.py          # Catálogo de especializaciones iniciales (Berserker, Mago, etc.).
│   └── dungeon_manager.py      # Ciclo de los 50 niveles, 5 mazmorras y temas elementales.
│
├── ui/
│   ├── ui_manager.py           # HUD Steampunk, manómetros de HP, monitor de 60 FPS.
│   ├── card_menu.py            # Menú interactivo modal de selección de cartas [1, 2, 3].
│   └── role_menu.py            # Menú interactivo de selección de rol antes de iniciar partida.
│
└── utils/
    └── asset_loader.py         # Fábrica de sprites Pixel Art procedimentales resilientes.
```

---

## 3. Instrucciones de Ejecución

Para iniciar el videojuego:

### Opción A (Recomendada):
Doble clic en el archivo:
```
run_game.bat
```

### Opción B (Desde la Terminal / PowerShell):
```powershell
cd C:\Users\User\.gemini\antigravity\scratch\proyecto_hack_and_slash
py main.py
```

### Para correr la Batería de Pruebas de Integridad:
```powershell
py test_integrity.py
```

### Controles en el Juego:
* **Mover al Héroe:** Teclas `W, A, S, D` o Flechas del teclado.
* **Apuntar:** Mueve el ratón (el héroe y la espada apuntan en 360 grados).
* **Ataque con Espada de Piedra:** `Clic Izquierdo` del ratón.
* **Hechizo Mágico Primario Activo:** `Clic Derecho` o tecla `E` (desbloqueado con cartas).
* **Hechizo Mágico Secundario Activo:** Tecla `Q` (desbloqueado con cartas).
* **Dash / Esquiva con Impulso de Vapor:** `Barra Espaciadora` (otorga invulnerabilidad i-frames).
* **Elegir Carta de Mejora (cada 3 niveles):** Clic sobre la carta o presionar teclas `1`, `2` o `3`.
* **Reiniciar Partida tras Derrota / Victoria:** Tecla `Espacio` o `R`.

---

## 4. Guía para la Defensa Oral ante el Tribunal Universitario

### Pregunta 1: "¿Por qué utilizaste esta separación modular en carpetas y archivos?"
> **Respuesta modelo:** *"Apliqué el Principio de Responsabilidad Única (SRP) de la arquitectura SOLID. Cada módulo tiene un único motivo para cambiar: si se requiere calibrar daño o vida, se modifica `settings.py`; si se ajusta la física del corte con espada, se modifica `combat_system.py`; y si se altera la probabilidad de cartas, se modifica `card_system.py`. Esto evita el acoplamiento y facilita el mantenimiento y la escalabilidad."*

### Pregunta 2: "¿Cómo garantizaste que el juego corra a 60 FPS estables sin sobrecargar la CPU?"
> **Respuesta modelo:** *"Se tomaron tres decisiones técnicas: 
> 1. Gráficos en Pixel Art optimizados mediante superficies cacheadas en memoria (`utils/asset_loader.py`).
> 2. Control de tiempo delta (`dt`) en el game loop sincronizado con el reloj de Pygame a 60 ticks.
> 3. Algoritmo de colisión espacial y barrido angular basado en distancias euclidianas sin llamar a cálculos trigonométricos innecesarios para cada frame."*

### Pregunta 3: "¿Cómo se implementó la regla de que las magias de Luz y Oscuridad no aparezcan en cartas comunes?"
> **Respuesta modelo:** *"Se modeló mediante dos pools independientes en `card_system.py`. La reserva de 32 cartas estándar solo contiene los 6 elementos base (Fuego, Agua, Viento, Tierra, Trueno, Naturaleza) y cartas de atributos. Las magias de Luz y Oscuridad están estrictamente tipadas con atributos de exclusividad y solo se instancian dentro de la reserva de 16 cartas doradas. Esto está validado por aserciones de código y la suite `test_integrity.py`."*
