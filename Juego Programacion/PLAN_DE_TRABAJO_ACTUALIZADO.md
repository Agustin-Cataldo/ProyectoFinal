# 📋 Plan de Trabajo Actualizado — Steam & Blade: Elemental Odyssey

> **Proyecto:** *Steam & Blade: Elemental Odyssey*  
> **Género:** Hack & Slash Roguelike 2D (Dark Steampunk & Medieval Gothic)  
> **Tecnología:** Python 3 + `pygame-ce` (Sin dependencias externas de assets ni librerías pesadas)  
> **Objetivo de Rendimiento:** 60 FPS estables con *Delta-Time* y *Double Buffering*  
> **Estado Actual:** **FASE FINAL COMPLETADA (100% CUMPLIDO — CERO ERRORES)**  
> **Ubicación de Exportación Portátil:** `C:\Users\User\Desktop\Juego Programacion`  

---

## 📑 Resumen Ejecutivo de Entregables Completados

| Hito / Sistema | Especificación Requerida | Estado | Módulos Clave |
| :--- | :--- | :---: | :--- |
| **Combate Hack & Slash** | Ataque en abanico, 13 armas medievales, Dash con i-frames | ✅ 100% | `entities/player.py`, `entities/weapons.py`, `systems/combat_system.py` |
| **Mazmorras y 50 Niveles** | 5 Mazmorras de 10 niveles, 10 elementos aleatorios, Nivel 10 Jefe | ✅ 100% | `systems/dungeon_manager.py`, `settings.py` |
| **Cartas & Magias** | 32 estándar, 16 doradas, exclusividad de Luz/Oscuridad, 2 magias activas | ✅ 100% | `systems/card_system.py`, `systems/combat_system.py` |
| **Expansión Slay the Spire 2** | 12 Personajes Legendarios, 600 Cartas Únicas (50 por personaje) | ✅ 100% | `systems/role_system.py`, `systems/character_cards_database.py`, `ui/role_menu.py` |
| **Jefes Elementales** | 10 Jefes con 20 ataques firma telegrafiados y Furia Calamidad | ✅ 100% | `entities/boss.py` |
| **Bestiario Completo** | 16 arquetipos (10 comunes/tácticos, 1 invocación, 5 espíritus élite) | ✅ 100% | `entities/enemy.py` |
| **Audio Procedural** | 39 SFX y 3 pistas BGM sintetizadas matemáticamente | ✅ 100% | `systems/audio_system.py`, `assets/audio/` |
| **Menú de Pausa Modal** | Pausa en `ESC`/`P`, mundo congelado, estadísticas en vivo y controles | ✅ 100% | `ui/pause_menu.py`, `game_engine.py` |
| **Solución de 5 Bugs** | Hit-flash temporal, colisión de muros, visuales de magia, balance jefes/enemigos | ✅ 100% | `entities/enemy.py`, `entities/boss.py`, `systems/combat_system.py` |
| **5 Nuevas Variantes** | Artificiero, Médico de Peste, Guardián de Latón, Cultista, Segador | ✅ 100% | `entities/enemy.py`, `utils/asset_loader.py` |
| **Portabilidad & Entrega** | Carpeta de Escritorio con instaladores `.bat` y guía `LEEME.txt` | ✅ 100% | `Desktop\Juego Programacion\` |
| **Auditoría Técnica** | 6 Baterías automatizadas de pruebas con 100% de aprobación | ✅ 100% | `audit_all_systems.py`, `test_*.py` |

---

## 🗓️ Cronograma Detallado de Fases y Cambios Realizados

### Fase 1: Arquitectura Base y Motor de Combate Hack & Slash
- **Arquitectura de Software:** Implementación del patrón de diseño *State* en `game_engine.py` gestionando estados: `MAIN_MENU`, `ROLE_SELECTION`, `PLAYING`, `CARD_SELECTION`, `SPELL_SWAP`, `PAUSED` y `GAME_OVER`.
- **Movimiento Cinemático:** Control 8D vectorial con suavizado, rotación en 360 grados apuntando al cursor del ratón y animación de bamboleo de caminata.
- **Parámetros del Jugador:** 1000 HP base, 50 DMG base + 20 DMG suplementario con la Espada de Piedra inicial = **70 DMG total inicial**.
- **Mecánica de Dash:** Impulso de vapor explosivo (Barra Espaciadora) a 620 px/s con estela de fantasmas translúcidos y **cuadros de invulnerabilidad (i-frames)** durante 0.18s.
- **Curación de Paciencia:** Regeneración pasiva de calma que otorga **+10 HP cada 10 segundos continuos** sin recibir daño.

### Fase 2: Progresión de Mazmorras y Escalado Roguelike
- **Estructura de 50 Niveles:** Divididos en 5 Mazmorras sucesivas de 10 niveles cada una en `systems/dungeon_manager.py`.
- **Aleatorización Elemental:** Al inicio o reinicio de partida, se eligen y ordenan aleatoriamente 5 de los 10 temas elementales: *Fuego, Agua, Viento, Tierra, Trueno, Naturaleza, Vapor, Metal, Oscuridad y Luz*.
- **Combate de Fin de Mazmorra:** En el nivel 10 de cada mazmorra se bloquea la sala y se engendra el Jefe Elemental correspondiente a la ambientación.
- **Escalado Matemático:** Escalado roguelike de +4.5% de vida y daño en enemigos por nivel global, asegurando una curva de reto progresiva.

### Fase 3: Sistema de Cartas y Magia Elemental Activa
- **Reserva de Cartas Globales:** 32 cartas estándar y 16 cartas doradas implementadas en `systems/card_system.py`.
- **Regla Sagrada de Magia:** Los elementos *Oscuridad* y *Luz* se establecieron como **exclusivos de Cartas Doradas**, comprobado matemáticamente en tests.
- **Interfaz de Elección:** Modal interactivo con 3 cartas presentadas cada 3 niveles completados, permitiendo selección con teclas `[1]`, `[2]`, `[3]` o clic.
- **Ranuras de Magia Dual:** El jugador puede equipar y alternar un Hechizo Primario (tecla `[1]`) y un Hechizo Secundario (tecla `[2]`), ambos gobernados por una barra de **500 MP de Maná base**.

### Fase 4: Expansión Estilo Slay the Spire 2 (12 Personajes & 600 Cartas)
- **12 Personajes Legendarios:**
  1. *Guerrero de Vapor* (Gran Hacha Bárbara).
  2. *Paladín de la Luz* (Maza Sagrada y Gran Escudo).
  3. *Pícaro Sombrío* (Dagas Gemelas Venenosas).
  4. *Mago Arcano* (Bastón Rúnico y auto-ataque de dardo arcano).
  5. *Cazador Real* (Ballesta Mecánica de Repetición).
  6. *Nigromante Abisal* (Guadaña Espectral Cosechadora).
  7. *Alquimista de Vapor* (Frascos de Ácido Alquímico).
  8. *Monje del Templo* (Guanteletes de Puño Férreo).
  9. *Artillero Pesado* (Cañón Portátil de Asedio).
  10. *Chamán Elemental* (Tótem Tribal Conductor).
  11. *Caballero Oscuro* (Espadón Maldito a Dos Manos).
  12. *Flagelante Fanático* (Mangual de Cadena Punzante).
- **Barajas Exclusivas (600 Cartas):** Cada personaje cuenta con una baraja de 50 cartas exclusivas temáticas en `systems/character_cards_database.py`, garantizando que ningún héroe reciba cartas ajenas a su especialización.
- **Selector Slay the Spire 2:** Menú en cuadrícula navegable de 6 cartas por página con previsualizaciones de estadísticas, animaciones de hover y cartas de armas distintivas.

### Fase 5: Los 10 Jefes Elementales y Avisos Telegrafiados
- Implementación de la clase colosal `ElementalBoss` (3000 HP base) con **20 ataques firma únicos** (2 por cada elemento).
- **Filosofía de Combate Justo:** Todos los ataques mayores proyectan zonas de peligro rojas/doradas previas (líneas láser, círculos de aviso, conos de expansión), permitiendo al jugador esquivar mediante habilidad pura (*No-Hit Viable*).
- **Mecánica de Calamidad y Furia:** Al caer por debajo del 50% de HP, el jefe entra en *Enrage*, reduciendo sus tiempos de recarga en 40% y desatando ondas de choque sísmicas con cada golpe.

### Fase 6: Sistema de Audio Procedural Completo
- **Síntesis Matemática Pura:** En `systems/audio_system.py`, se sintetizaron 39 efectos de sonido (golpes de 13 armas, 10 magias elementales, dash, gemidos de daño, portales y fanfarrias) y 3 pistas de música de fondo (Menú, Mazmorra y Jefes).
- **Controles de Audio:** Silencio rápido con tecla `[M]`, ajuste dinámico de volumen con `[+]` y `[-]`, y reproducción multicanal sin bloqueos.

### Fase 7: Menús, Códice & HUD Steampunk
- **Menú Principal:** Logotipo con relieve de latón, 5 botones interactivos con sonido, Códice de Personajes con visor de barajas y vista de controles.
- **HUD Dinámico:** Manómetro de vida en rojo sangre, medidor de maná en éter azul brillante, indicador de nivel de mazmorra, medidor de cartas activas y monitor de 60 FPS en esquina.

### Fase 8: Menú de Pausa Modal
- Implementación de `ui/pause_menu.py`:
  * Acceso instantáneo con tecla `[ESC]` o `[P]`.
  * Congelamiento total de la simulación física del combate, partículas y temporizadores.
  * Tarjeta de héroe con estadísticas en vivo (HP actual/máximo, arma activa, daño base y cartas acumuladas).
  * 5 Botones: Continuar, Ver Controles, Silenciar Audio, Reiniciar Nivel y Salir al Menú Principal.
  * Submodal de ayuda con guía visual de teclas y mecánicas.

### Fase 9: Resolución de los 5 Puntos Críticos y Bugs
1. **Hit-Flash Blanco Persistente:** Corregido integrando `update_base(dt)` en todas las clases, con decaimiento estricto de `hit_flash_timer` a 0.0.
2. **Clipping en Paredes de la Arena:** Confinamiento perimetral estricto con límites de pantalla y grosor de muro (38px de margen), impidiendo que cualquier entidad atraviese los límites.
3. **Revamp Visual de Magias:** Transformación de proyectiles planos en vórtices multicapa procedimentales, estelas de partículas en vuelo y mecánica de arco voltaico en cadena para el *Trueno*.
4. **Dificultad de Jefes:** Super-armadura completa (`knockback_resistance = 1.0`), cadencias de ataque aceleradas y daño de contacto amenazante.
5. **Dificultad de Enemigos Comunes:** Ajuste de agresividad, mayor vida y daño, y resistencia al empuje en enemigos pesados.

### Fase 10: Bestiario Expandido (5 Nuevas Variantes de Enemigos)
Ampliación del bestiario común a **10 variantes de autómatas y herejes tácticos** en `entities/enemy.py`:
1. **Artificiero de Relojería (`ClockworkBombardier`):** Lanza bombas temporizadas con mecha que estallan en onda sísmica y 4 esquirlas de metralla metálica.
2. **Médico de la Peste Alquímico (`AlchemicalPlagueDoctor`):** Emite un aura de miasma corrosivo (16 DMG/s), arroja charcos de ácido y emite pulsos de vapor que sanan +28 HP a los enemigos cercanos.
3. **Guardián de Escudo de Latón (`BrassShieldGuardian`):** Gran escudo torre direccional que bloquea el 75% del daño frontal (requiere flanqueo o apuñalar por la espalda con Dash) y *Shield Bash* sísmico a corta distancia.
4. **Cultista de la Forja Arcana (`ArcaneCultist`):** Canaliza un rito de 1.1s con puntero láser telegrafiado hacia el jugador, desatando una andanada de 3 orbes arcanos y quedando exhausto/vulnerable.
5. **Segador Mecánico de Cadena (`CursedReaper`):** Asesino veloz (165 px/s) con arpón de vapor para impulsarse hacia el jugador y torbellino de guadaña en 360° telegrafiado.

### Fase 11: Despersonalización de Título
- Se retiró la mención "Proyecto Agustín Cataldo" en `settings.py`, `ui/main_menu.py`, `main.py` y `run_game.bat`, estableciendo el título comercial oficial **"Steam & Blade: Elemental Odyssey"**.

### Fase 12: Empaquetado y Exportación Portátil
- Copia limpia y autónoma en:
  `C:\Users\User\Desktop\Juego Programacion`
- Inclusión de:
  * `run_game.bat` (lanzador inteligente de doble clic).
  * `instalar_dependencias.bat` (instalador automático de `pygame-ce`).
  * `LEEME_INSTRUCCIONES.txt` (guía en texto plano para el usuario final).
  * `requirements.txt` y scripts de verificación.

### Fase 13: Auditoría y Batería de Pruebas Automatizadas
- **100% de Aprobación en todas las suites:**
  * `test_integrity.py` (15/15 tests superados).
  * `test_new_enemies.py` (6/6 pruebas superadas).
  * `test_user_fixes.py` (5/5 validaciones superadas).
  * `test_pause_menu.py` (100% superado).
  * `test_gameplay_flow.py` (flujo headless superado).
  * `audit_all_systems.py` (**0 errores** detectados en 648 cartas, 12 personajes, 13 armas, 10 jefes y 16 enemigos).
