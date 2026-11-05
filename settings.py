"""
================================================================================
MÓDULO: settings.py
RESPONSABILIDAD: Almacén central de configuración y constantes del juego.
CONCEPTO ACADÉMICO: Principio de Responsabilidad Única (SRP) y Separación de 
                    Configuración vs. Lógica de Negocio.
================================================================================
Este archivo centraliza todos los parámetros numéricos, mecánicos y visuales.
Si el tribunal universitario solicita modificar la vida del jugador, la velocidad,
el daño de la espada o las tasas de aparición, únicamente se debe alterar este archivo,
garantizando que el código de los motores y entidades permanezca intacto.
"""

# -----------------------------------------------------------------------------
# 1. PARÁMETROS GENERALES DE LA VENTANA Y RENDIMIENTO
# -----------------------------------------------------------------------------
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
GAME_TITLE = "Clockwork Requiem"

# -----------------------------------------------------------------------------
# 2. ATRIBUTOS BASE DEL JUGADOR (ESPECIFICACIÓN OFICIAL)
# -----------------------------------------------------------------------------
# Vida inicial establecida por requerimiento académico: 1000 HP
PLAYER_BASE_HP = 1000

# Maná inicial para lanzamiento de hechizos arcanos: 500 MP
PLAYER_BASE_MANA = 500

# Costos de Maná por elemento (Equilibrado para evitar spam y premiar combate cuerpo a cuerpo)
MANA_SPELL_COSTS = {
    "Naturaleza":         65,
    "Agua":               70,
    "Viento":             70,
    "Vapor (Steampunk)":  70,
    "Vapor":              70,
    "Trueno":             75,
    "Metal":              75,
    "Fuego":              80,
    "Tierra":             85,
    "Luz":                120,  # Dorada: Daño masivo estelar + Cura 60 HP
    "Oscuridad":          130   # Dorada: Agujero negro + Drenaje vampírico
}

# Recuperación de Maná en combate
MANA_REGEN_KILL_MIN = 50       # 50 a 75 MP por enemigo eliminado
MANA_REGEN_KILL_MAX = 75
MANA_REGEN_MELEE_HIT = 10      # +10 MP por cada golpe con la espada de piedra

# Daño base a puño limpio / cuerpo a cuerpo: 50 puntos
PLAYER_BASE_DAMAGE = 50

# Arma inicial requerida: Espada de piedra mediana
PLAYER_INITIAL_WEAPON = "Espada de piedra mediana"
PLAYER_WEAPON_DAMAGE = 20  # Daño suplementario (+20)

# Daño inicial total combinado = 50 (Base) + 20 (Arma) = 70 DMG
PLAYER_TOTAL_INITIAL_DAMAGE = PLAYER_BASE_DAMAGE + PLAYER_WEAPON_DAMAGE

# Velocidad de traslación base en píxeles por segundo
PLAYER_BASE_SPEED = 260.0

# Radio de colisión del jugador (para física y hitboxes en 2D)
PLAYER_RADIUS = 22

# Tiempo de enfriamiento entre ataques de espada (segundos)
PLAYER_ATTACK_COOLDOWN = 0.35

# Parámetros del tajo de la espada (Hack & Slash en área)
PLAYER_ATTACK_RANGE = 82       # Alcance en píxeles hacia adelante
PLAYER_ATTACK_ARC_DEG = 110    # Amplitud angular del corte en grados

# Tiempo de invulnerabilidad tras recibir un impacto (i-frames en segundos)
PLAYER_INVULNERABILITY_TIME = 0.60

# Sistema de Esquiva / Dash con Impulso de Vapor (Barra Espaciadora)
PLAYER_DASH_SPEED = 620.0      # Velocidad explosiva del dash
PLAYER_DASH_DURATION = 0.18    # Duración en segundos
PLAYER_DASH_COOLDOWN = 0.95    # Tiempo de recarga entre dashes

# Enfriamiento base para el hechizo activo (segundos)
MAGIC_SPELL_COOLDOWN = 1.2     # Cooldown ágil (controlado principalmente por Maná)
MAGIC_SPELL_BASE_DAMAGE = 65.0 # Daño base de proyectiles mágicos del jugador

# -----------------------------------------------------------------------------
# 3. ESTRUCTURA DE NIVELES Y MAZMORRAS
# -----------------------------------------------------------------------------
TOTAL_DUNGEONS = 5          # Cantidad de mazmorras para completar el juego
LEVELS_PER_DUNGEON = 10     # Cada mazmorra consta de 10 niveles
TOTAL_LEVELS = 50           # Condición de victoria: superar los 50 niveles
BOSS_LEVEL_STEP = 10        # El nivel 10 de cada mazmorra contiene al Jefe

# Los 10 temas elementales posibles para las mazmorras (se aleatorizan al reiniciar)
DUNGEON_ELEMENTS = [
    "Fuego",
    "Agua",
    "Viento",
    "Tierra",
    "Trueno",
    "Naturaleza",
    "Vapor (Steampunk)",
    "Metal",
    "Oscuridad",
    "Luz"
]

# -----------------------------------------------------------------------------
# 4. SISTEMA DE CARTAS DE MEJORA Y MAGIA ELEMENTAL
# -----------------------------------------------------------------------------
STANDARD_CARDS_POOL_SIZE = 32   # Reserva total de cartas estándar
GOLDEN_CARDS_POOL_SIZE = 16     # Reserva total de cartas doradas

CARD_OFFER_INTERVAL = 3         # Cada 3 niveles completados se eligen cartas
CARDS_OFFERED_COUNT = 3         # Se presentan 3 cartas para elegir 1

GOLDEN_CARD_INTERVAL = 5        # Cada 5 rondas existe probabilidad de carta dorada
GOLDEN_CARD_CHANCE = 0.40       # 40% de probabilidad de que una carta sea dorada cada 5 rondas

# Los 8 Elementos Mágicos del juego
MAGIC_ELEMENTS_ALL = [
    "Fuego", "Agua", "Viento", "Tierra", 
    "Trueno", "Naturaleza", "Oscuridad", "Luz"
]

# REGLA CRÍTICA DE MAGIA:
# Magias estándar que pueden aparecer en cartas normales
MAGIC_ELEMENTS_STANDARD = [
    "Fuego", "Agua", "Viento", "Tierra", "Trueno", "Naturaleza"
]

# Magias EXCLUSIVAS que ÚNICAMENTE pueden aparecer en Cartas Doradas
MAGIC_ELEMENTS_EXCLUSIVE = [
    "Oscuridad", "Luz"
]

# -----------------------------------------------------------------------------
# 5. ATRIBUTOS DE LOS ENEMIGOS Y VARIANTES (DIFICULTAD ROGUELIKE INTENSA)
# -----------------------------------------------------------------------------
# 5.1. Variedad de Enemigos Comunes (Pesadilla Roguelike: mayor agresividad, vida y daño)
COMMON_MINER_HP = 140          # Autómata Minero
COMMON_MINER_DAMAGE = 42       # Quita 42 HP
COMMON_MINER_SPEED = 175.0     # Más ágil en persecución

COMMON_CHARGER_HP = 180        # Autómata embestidor
COMMON_CHARGER_DAMAGE = 65     # Embestida muy letal (65 HP)
COMMON_CHARGER_SPEED = 160.0
COMMON_CHARGER_BURST = 500.0   # Velocidad de embestida explosiva rápida

COMMON_SNIPER_HP = 100         # Tirador de vapor / ballestero
COMMON_SNIPER_DAMAGE = 40      # Disparos certeros (40 HP)
COMMON_SNIPER_SPEED = 140.0

COMMON_DRONE_HP = 75           # Dron volador hostigador
COMMON_DRONE_DAMAGE = 32       # Hostigamiento rápido
COMMON_DRONE_SPEED = 280.0

COMMON_TANK_HP = 380           # Demoledor blindado pesado
COMMON_TANK_DAMAGE = 80        # Golpe de martillo demoledor (80 HP)
COMMON_TANK_SPEED = 115.0

COMMON_BOMBARDIER_HP = 160      # Artificiero de Relojería / Bombardero
COMMON_BOMBARDIER_DAMAGE = 50   # Daño de bomba y metralla (50 HP)
COMMON_BOMBARDIER_SPEED = 130.0 # Velocidad táctica a distancia

COMMON_PLAGUE_DOCTOR_HP = 210   # Médico de la Peste Alquímico (Soporte/Miasma)
COMMON_PLAGUE_DOCTOR_DAMAGE = 35 # Daño de contacto y ácido
COMMON_PLAGUE_DOCTOR_SPEED = 120.0 # Flotación alquímica

COMMON_SHIELD_GUARDIAN_HP = 260 # Guardián de Escudo de Latón (Tanque Frontal)
COMMON_SHIELD_GUARDIAN_DAMAGE = 48 # Golpe de escudo contundente
COMMON_SHIELD_GUARDIAN_SPEED = 110.0 # Avance con escudo torre

COMMON_ARCANE_CULTIST_HP = 130  # Cultista de la Forja Arcana (Canalizador)
COMMON_ARCANE_CULTIST_DAMAGE = 55 # Descargas rúnicas de éter
COMMON_ARCANE_CULTIST_SPEED = 135.0 # Desplazamiento ritual

COMMON_REAPER_HP = 220          # Segador Mecánico de Cadena (Asesino)
COMMON_REAPER_DAMAGE = 58       # Tajo de guadaña y arpón de vapor
COMMON_REAPER_SPEED = 165.0     # Gran velocidad de acecho

# 5.2. Espíritus Malignos (Élites con 5 Variantes Únicas)
ELITE_SPIRIT_HP = 420
ELITE_SPIRIT_DAMAGE = 72       # Hechizos élite peligrosos (72 HP)
ELITE_SPIRIT_SPEED = 140.0     # Agresividad roguelike calibrada (<= 150 px/s)
ELITE_SPAWN_CHANCE = 0.35      # 35% base de probabilidad de aparición élite

# 5.3. Jefe Elemental Colosal (Nivel 10)
BOSS_BASE_HP = 3000.0          # Vida titánica base para Mazmorra 1 (escala +35% por mazmorra)
BOSS_BASE_DAMAGE = 75.0        # Daño amenazante de proyectiles y contacto (era 55.0)

# -----------------------------------------------------------------------------
# 6. PALETAS DE COLOR (ESTÉTICA RETRO STEAMPUNK & ELEMENTOS)
# -----------------------------------------------------------------------------
# Colores generales de interfaz y entorno
COLOR_BLACK       = (10, 10, 14)
COLOR_DARK_STONE  = (32, 34, 40)
COLOR_FLOOR       = (45, 48, 56)
COLOR_WALL        = (22, 24, 28)
COLOR_WHITE       = (245, 245, 250)
COLOR_BRASS       = (212, 160, 23)     # Bronce/Latón Steampunk
COLOR_COPPER      = (184, 115, 51)     # Cobre Steampunk
COLOR_STEAM       = (200, 214, 229)    # Vapor blanco azulado
COLOR_RED_HEALTH  = (214, 48, 49)      # Barra de vida
COLOR_MANA        = (41, 128, 185)     # Barra de maná / éter azul
COLOR_MANA_BRIGHT = (52, 152, 219)     # Maná resplandeciente
COLOR_GREEN_EXP   = (46, 204, 113)
COLOR_GOLD        = (241, 196, 15)     # Cartas doradas

# Paletas cromáticas asociadas a cada elemento
ELEMENT_COLORS = {
    "Fuego":              (231, 76, 60),    # Rojo carmesí
    "Agua":               (52, 152, 219),   # Azul océano
    "Viento":             (26, 188, 156),   # Verde menta / turquesa
    "Tierra":             (160, 82, 45),    # Marrón siena
    "Trueno":             (243, 156, 18),   # Amarillo relámpago
    "Naturaleza":         (39, 174, 96),    # Verde bosque
    "Oscuridad":          (142, 68, 173),   # Púrpura sombrío
    "Luz":                (254, 249, 231),  # Blanco marfil / dorado celestial
    "Vapor (Steampunk)":  (178, 190, 195),  # Gris vapor
    "Metal":              (127, 140, 141)   # Gris acero
}
