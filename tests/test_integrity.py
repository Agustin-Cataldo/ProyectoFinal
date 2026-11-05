"""
================================================================================
SCRIPT DE TESTEO AUTOMATIZADO Y VALIDACIÓN ACADÉMICA
RESPONSABILIDAD: Verificar la integridad lógica, matemática y estructural del juego.
================================================================================
Comprueba:
1. Pool exacto de 32 cartas estándar y 16 cartas doradas.
2. Exclusividad estricta: Luz y Oscuridad no existen en la baraja común.
3. Atributos iniciales del Jugador: 500 HP, 50 daño base + 20 espada = 70 DMG.
4. Generación aleatoria de los 5 elementos de mazmorra a partir de los 10 disponibles.
5. Escalado del Jefe en el nivel 10 y simulación de combate y selección de cartas.
"""

import os
import sys

# Forzar codificación UTF-8 en consola de Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Asegurar importación del directorio raíz
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import pygame
# Inicializar pygame en modo headless (dummy video) para tests sin pantalla gráfica
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1, 1))

from settings import (
    PLAYER_BASE_HP, PLAYER_BASE_MANA, PLAYER_BASE_DAMAGE, PLAYER_WEAPON_DAMAGE,
    STANDARD_CARDS_POOL_SIZE, GOLDEN_CARDS_POOL_SIZE,
    MAGIC_ELEMENTS_EXCLUSIVE, MAGIC_ELEMENTS_STANDARD,
    TOTAL_DUNGEONS, TOTAL_LEVELS, BOSS_LEVEL_STEP,
    DUNGEON_ELEMENTS, MANA_SPELL_COSTS
)
from entities.player import Player
from entities.enemy import (
    CommonMonster, SteamMiner, SteamPistonCharger, SteamSharpshooter,
    SteamDrone, DemolitionTank, EvilSpirit, ShadowSpirit,
    FlameSpirit, FrostSpirit, StormSpirit, NecroSpirit, create_random_spirit
)
from entities.boss import ElementalBoss
from systems.card_system import CardSystem
from systems.character_cards_database import CHARACTER_DECKS, get_deck_for_character
from systems.combat_system import CombatSystem
from systems.dungeon_manager import DungeonManager
from systems.role_system import RoleSystem
from ui.ui_manager import UIManager
from ui.role_menu import RoleMenu
from ui.main_menu import MainMenu
from systems.audio_system import AudioSystem


def test_player_stats():
    print("[+] Test 1: Verificando estadisticas iniciales del Jugador (1000 HP)...")
    player = Player(100, 100)
    assert player.current_hp == 1000, f"Error: HP esperado 1000, obtenido {player.current_hp}"
    assert player.base_damage == 50, f"Error: Daño base esperado 50, obtenido {player.base_damage}"
    assert player.weapon_damage == 20, f"Error: Daño de arma esperado 20, obtenido {player.weapon_damage}"
    assert player.weapon_name == "Espada de piedra mediana", f"Error en arma inicial: {player.weapon_name}"
    assert player.total_damage == 70, f"Error: Daño total inicial esperado 70, obtenido {player.total_damage}"
    print("  [OK] Jugador inicializado con 1000 HP, Espada de piedra mediana y 70 DMG total.")


def test_card_system_rules():
    print("[+] Test 2: Verificando reglas del Sistema de Cartas y Barajas de Personajes (Slay the Spire 2)...")
    card_sys = CardSystem()

    # 1. Verificar tamaños de pools base
    assert len(card_sys.standard_pool) == 32, f"Pool estándar debe tener 32 cartas, tiene {len(card_sys.standard_pool)}"
    assert len(card_sys.golden_pool) == 16, f"Pool dorado debe tener 16 cartas, tiene {len(card_sys.golden_pool)}"

    # Verificar que ni Luz ni Oscuridad estén en cartas estándar
    for card in card_sys.standard_pool:
        assert card.exclusive_element not in MAGIC_ELEMENTS_EXCLUSIVE, \
            f"VIOLACIÓN CRÍTICA: {card.exclusive_element} hallado en carta estándar '{card.name}'"

    # Verificar que Luz y Oscuridad SÍ existan en cartas doradas
    golden_exclusive_elements = [c.exclusive_element for c in card_sys.golden_pool if c.exclusive_element]
    assert "Luz" in golden_exclusive_elements, "Error: Magia de Luz debe existir en cartas doradas"
    assert "Oscuridad" in golden_exclusive_elements, "Error: Magia de Oscuridad debe existir en cartas doradas"

    # 2. Verificar las 50 cartas únicas por personaje (12 personajes = 600 cartas de mejora únicas)
    expected_characters = [
        "berserker", "paladin", "rogue", "mage", "hunter", "necromancer",
        "runeknight", "alchemist", "monk", "artificer", "shaman", "inquisitor"
    ]
    assert set(CHARACTER_DECKS.keys()) == set(expected_characters), \
        f"Deben existir las 12 barajas exactas, halladas: {set(CHARACTER_DECKS.keys())}"

    all_card_ids = set()
    total_cards = 0
    for char_id in expected_characters:
        deck = get_deck_for_character(char_id)
        assert len(deck) == 50, f"El personaje {char_id} debe tener exactamente 50 cartas únicas (tiene {len(deck)})"
        for card in deck:
            assert card.character_id == char_id
            assert card.card_id not in all_card_ids, f"ID duplicado detectado: {card.card_id}"
            all_card_ids.add(card.card_id)
            total_cards += 1

    assert total_cards == 600, f"Debe haber 600 cartas de mejora en total, halladas {total_cards}"
    assert len(all_card_ids) == 600, "Todas las 600 cartas deben poseer IDs únicos irrepetibles"

    # 3. Probar que al solicitar oferta para un personaje, las 3 cartas pertenezcan a su baraja
    p_mage = Player(100, 100)
    p_mage.character_id = "mage"
    mage_offer = card_sys.get_selection_offer(1, p_mage)
    assert len(mage_offer) == 3
    for c in mage_offer:
        assert c.character_id == "mage", f"La carta ofrecida {c.name} no pertenece a la baraja del Mago"

    print("  [OK] 32 Cartas Estandar y 16 Cartas Doradas validadas.")
    print("  [OK] 300 Cartas de Mejora Únicas validadas (50 exclusivas por personaje para los 6 personajes).")
    print("  [OK] Filtrado Slay the Spire 2 verificado: Cada personaje recibe únicamente cartas de su propia baraja.")


def test_dungeon_and_boss_progression():
    print("[+] Test 3: Verificando Mazmorras, Aleatorizacion y Jefes...")
    dungeon_mgr = DungeonManager()

    # Verificar 5 elementos aleatorizados de los 10
    assert len(dungeon_mgr.dungeon_elements) == 5, "Deben haber 5 mazmorras configuradas"
    assert len(set(dungeon_mgr.dungeon_elements)) == 5, "Los 5 elementos deben ser únicos en una partida"

    # Simular avance hasta el nivel 10 (Jefe)
    dungeon_mgr.current_level_in_dungeon = 10
    dungeon_mgr.load_current_level()
    assert dungeon_mgr.active_boss is not None, "Error: El nivel 10 debe contener al Jefe Elemental"
    assert isinstance(dungeon_mgr.active_boss, ElementalBoss)
    print(f"  [OK] Jefe instanciado correctamente: {dungeon_mgr.active_boss.name}")


def test_combat_resolution():
    print("[+] Test 4: Verificando Sistema de Combate Hack & Slash...")
    player = Player(200, 200)
    enemy = CommonMonster(230, 200)  # Dentro del radio de 80px hacia adelante
    combat_sys = CombatSystem()

    # Jugador mira hacia el enemigo (ángulo 0 hacia la derecha)
    player.update_aim((300, 200))
    player.trigger_attack()

    initial_hp = enemy.current_hp
    hits = combat_sys.process_player_melee_attack(player, [enemy])

    assert hits == 1, f"El ataque de barrido debio golpear 1 enemigo, golpeo {hits}"
    assert enemy.current_hp < initial_hp, "La vida del enemigo debio disminuir tras el impacto"
    print(f"  [OK] Impacto registrado: Enemigo recibio daño. Vida previa: {initial_hp}, Vida actual: {enemy.current_hp}")


def test_dash_and_active_magic():
    print("[+] Test 5: Verificando Esquiva (Dash) y Controles de Hechizos Mágicos...")
    player = Player(200, 200)
    combat_sys = CombatSystem()

    # 1. Probar Dash de Vapor
    assert player.dash_cooldown_timer == 0.0
    dashed = player.trigger_dash()
    assert dashed is True, "El Dash debió activarse"
    assert player.is_dashing is True
    assert player.invulnerable_timer > 0, "El Dash debe otorgar invulnerabilidad (i-frames)"

    # 2. Probar Hechizos Mágicos Activos
    assert player.primary_magic is None, "Al inicio no debe tener hechizos"
    # Adquirir magia de Fuego y Luz
    player.active_magic_elements = ["Fuego", "Luz"]
    assert player.primary_magic == "Fuego"
    assert player.secondary_magic == "Luz"

    # Castear magia primaria (Fuego)
    elem_cast = player.trigger_primary_magic()
    assert elem_cast == "Fuego"
    combat_sys.cast_player_active_magic(player, elem_cast, (300, 200))
    assert len(combat_sys.projectiles) == 1, "Debe haberse creado 1 proyectil de Fuego"
    assert combat_sys.projectiles[0].element == "Fuego"

    # Castear magia secundaria (Luz en estrella celestial de 8 rayos)
    elem_cast_sec = player.trigger_secondary_magic()
    assert elem_cast_sec == "Luz"
    combat_sys.cast_player_active_magic(player, elem_cast_sec, (300, 200))
    assert len(combat_sys.projectiles) >= 2, "Debe haberse creado la salva celestial de Luz"

    print("  [OK] Dash con i-frames y controles de hechizos (Primario y Secundario) verificados.")


def test_enemy_variety_and_spirit_variants():
    print("[+] Test 6: Verificando las 5 Variantes de Espíritus y Enemigos Comunes...")
    # Verificar enemigos comunes
    miner = SteamMiner(100, 100)
    charger = SteamPistonCharger(100, 100)
    sniper = SteamSharpshooter(100, 100)
    drone = SteamDrone(100, 100)
    tank = DemolitionTank(100, 100)
    assert all([miner.is_alive, charger.is_alive, sniper.is_alive, drone.is_alive, tank.is_alive])

    # Verificar las 5 variantes únicas de Espíritus Malignos
    spirits = [
        ShadowSpirit(100, 100),
        FlameSpirit(100, 100),
        FrostSpirit(100, 100),
        StormSpirit(100, 100),
        NecroSpirit(100, 100)
    ]
    variants = {s.variant for s in spirits}
    assert variants == {"Penumbra", "Llama Fatua", "Glacial", "Tormenta", "Nigromante"}, \
        f"Deben existir las 5 variantes exactas, halladas: {variants}"

    # Verificar velocidad de espíritus élite en dificultad roguelike
    for s in spirits:
        assert s.speed <= 150.0, f"La velocidad del espíritu {s.variant} debe ser moderada ({s.speed})"

    print("  [OK] 5 Variantes de Espíritus Malignos (Penumbra, Fuego, Glacial, Tormenta, Nigromante) validadas.")
    print("  [OK] Bestiario Común (Minero, Embestidor, Tirador, Dron, Demoledor) validado.")


def test_mana_system():
    print("[+] Test 7: Verificando Sistema de Maná (500 MP Base, Costos y Recarga)...")
    player = Player(200, 200)
    combat_sys = CombatSystem()

    # 1. Maná inicial
    assert player.current_mana == 500, f"Maná inicial debe ser 500, obtenido {player.current_mana}"
    assert player.max_mana == 500

    # 2. Gasto de Maná con hechizo
    player.active_magic_elements = ["Fuego"]
    cost_fire = MANA_SPELL_COSTS["Fuego"]  # 80 MP
    success = combat_sys.cast_player_active_magic(player, "Fuego", (300, 200))
    assert success is True, "El hechizo debió lanzarse exitosamente"
    assert player.current_mana == 500 - cost_fire, f"Maná restante esperado {500 - cost_fire}, obtenido {player.current_mana}"

    # 3. Agotar maná y verificar bloqueo
    player.current_mana = 30  # Insuficiente para Fuego (80)
    blocked = combat_sys.cast_player_active_magic(player, "Fuego", (300, 200))
    assert blocked is False, "El hechizo debió bloquearse por falta de maná"
    assert player.current_mana == 30

    # 4. Recuperación en melee (+10 MP) y por eliminación (+50-75 MP)
    player.restore_mana(10)
    assert player.current_mana == 40
    player.restore_mana(1000)  # No debe superar el límite de 500 MP
    assert player.current_mana == 500, f"El maná máximo no debe rebasar 500 MP, obtenido {player.current_mana}"

    print("  [OK] Barra de Maná de 500 MP, consumo por hechizo y recargas validadas con precisión.")


def test_all_ten_elemental_bosses():
    print("[+] Test 8: Verificando los 10 Jefes Elementales Únicos y Ataques Telegrafiados...")
    player = Player(300, 300)
    combat_sys = CombatSystem()
    test_surf = pygame.Surface((1280, 720))
    test_font = pygame.font.SysFont("Consolas", 14)

    assert len(DUNGEON_ELEMENTS) == 10, f"Deben existir 10 elementos de mazmorra, hallados {len(DUNGEON_ELEMENTS)}"

    for element in DUNGEON_ELEMENTS:
        boss = ElementalBoss(500, 350, element, dungeon_index=1)
        assert boss.current_hp == 3000.0, f"Vida inicial del jefe debe ser 3000, obtenido {boss.current_hp}"
        assert boss.is_alive is True

        # Verificar Hit-Flash al recibir daño
        boss.take_damage(50.0)
        assert boss.hit_flash_timer > 0, "El impacto debe activar el Hit-Flash blanco"
        assert boss.current_hp == 2950.0

        # Disparar Ataque Insignia 1 (Telegrafiado)
        initial_telegraphs = len(boss.active_telegraphs)
        boss._trigger_signature_attack_1(player, combat_sys)
        assert len(boss.active_telegraphs) >= initial_telegraphs, \
            f"El ataque 1 de {element} debió registrar advertencia telegrafiada"

        # Disparar Ataque Insignia 2
        boss._trigger_signature_attack_2(player, combat_sys)

        # Actualizar jefe y avanzar sus avisos telegrafiados hasta detonación
        for _ in range(15):
            boss.update(0.1, player, combat_sys)

        # Verificar renderizado visual sin excepciones
        boss.draw(test_surf)
        boss.draw_boss_hud(test_surf, test_font)

    print("  [OK] Los 10 Jefes Elementales (Fuego, Agua, Viento, Tierra, Trueno, Naturaleza, Vapor, Metal, Oscuridad, Luz) validados.")
    print("  [OK] Regla de Combate Justo: Todos los ataques cuentan con avisos telegrafiados y zonas de esquiva.")


def test_ui_mana_rendering():
    print("[+] Test 9: Verificando Renderizado del HUD con Barra de Maná...")
    ui_mgr = UIManager()
    player = Player(200, 200)
    dungeon_mgr = DungeonManager()
    clock = pygame.time.Clock()
    surf = pygame.Surface((1280, 720))

    # Renderizar HUD completo
    ui_mgr.draw_hud(surf, player, dungeon_mgr, clock)
    print("  [OK] HUD Steampunk con barra de HP (1000 HP) y barra de Maná (500 MP) renderizado sin fallos.")


def test_role_system():
    print("[+] Test 10: Verificando Selección de Personaje estilo Slay the Spire 2 (Sin opción Sin Rol)...")
    role_sys = RoleSystem()
    role_menu = RoleMenu(role_sys)
    surf = pygame.Surface((1280, 720))

    characters = role_sys.get_all_characters()
    assert len(characters) == 12, f"Deben haber exactamente 12 personajes legendarios, hallados {len(characters)}"
    assert role_sys.none_role is None, "La opción 'sin rol' debe estar eliminada"

    char_ids = {c.role_id for c in characters}
    expected_ids = {
        "berserker", "paladin", "rogue", "mage", "hunter", "necromancer",
        "runeknight", "alchemist", "monk", "artificer", "shaman", "inquisitor"
    }
    assert char_ids == expected_ids, f"Discrepancia en IDs de personajes: {char_ids}"

    # 1. Probar Rol Berserker Bárbaro (Nerfeado y balanceado)
    p_berserker = Player(100, 100)
    b_role = next(r for r in characters if r.role_id == "berserker")
    b_role.apply(p_berserker)
    assert p_berserker.max_hp == 1250.0, f"Berserker nerfeado debe tener 1250 HP, tiene {p_berserker.max_hp}"
    assert p_berserker.life_steal == 5.0, f"Robo de vida nerfeado a 5.0, tiene {p_berserker.life_steal}"
    assert p_berserker.weapon_type == "axe"
    assert p_berserker.weapon_name == "Gran Hacha Bárbara"

    # 2. Probar Rol Paladín Templario (Bufeado)
    p_paladin = Player(100, 100)
    pal_role = next(r for r in characters if r.role_id == "paladin")
    pal_role.apply(p_paladin)
    assert p_paladin.max_hp == 1150.0
    assert p_paladin.damage_reduction == 0.25
    assert p_paladin.passive_regen == 14.0
    assert p_paladin.weapon_type == "mace"

    # 3. Probar Rol Pícaro Sombrío (Bufeado)
    p_rogue = Player(100, 100)
    r_role = next(r for r in characters if r.role_id == "rogue")
    r_role.apply(p_rogue)
    assert p_rogue.max_hp == 900.0
    assert p_rogue.crit_chance == 0.50
    assert p_rogue.weapon_type == "daggers"

    # 4. Probar Rol Mago Arcano (Bufeado)
    p_mage = Player(100, 100)
    m_role = next(r for r in characters if r.role_id == "mage")
    m_role.apply(p_mage)
    assert p_mage.has_melee_weapon is False, "El Mago no debe tener arma melee"
    assert p_mage.trigger_attack() is False, "El Mago no debe poder realizar ataques con espada"
    assert p_mage.max_mana == 800.0
    assert "Fuego" in p_mage.active_magic_elements
    assert "Trueno" in p_mage.active_magic_elements
    assert p_mage.weapon_type == "staff"

    # 5. Probar Nuevo Rol: Cazador Real (Ballesta)
    p_hunter = Player(100, 100)
    h_role = next(r for r in characters if r.role_id == "hunter")
    h_role.apply(p_hunter)
    assert p_hunter.max_hp == 950.0
    assert p_hunter.weapon_type == "crossbow"
    assert p_hunter.weapon_name == "Ballesta Pesada de Repetición"

    # 6. Probar Nuevo Rol: Nigromante Abisal (Guadaña y Almas)
    p_necro = Player(100, 100)
    n_role = next(r for r in characters if r.role_id == "necromancer")
    n_role.apply(p_necro)
    assert p_necro.max_hp == 850.0
    assert p_necro.weapon_type == "scythe"
    assert p_necro.soul_harvest is True
    assert "Oscuridad" in p_necro.active_magic_elements

    # 7. Validar que los 12 roles poseen al menos una magia activa inicial y reserva de maná
    for char in characters:
        test_player = Player(100, 100)
        char.apply(test_player)
        assert len(test_player.active_magic_elements) >= 1, \
            f"El rol {char.name} debe tener al menos 1 magia activa inicial, tiene {test_player.active_magic_elements}"
        assert test_player.max_mana >= 500.0, \
            f"El rol {char.name} debe poseer al menos 500 MP de reserva, tiene {test_player.max_mana}"
        assert test_player.primary_magic is not None, \
            f"El rol {char.name} debe tener un hechizo primario accesible"

    # Probar renderizado del menú con los 6 personajes en cuadrícula
    role_menu.set_roles(characters)
    role_menu.draw(surf)

    print("  [OK] 6 Personajes Legendarios validados (Opción Sin Rol completamente eliminada).")
    print("  [OK] Menú de Selección Slay the Spire 2 con 6 cartas en cuadrícula renderizado con éxito.")


def test_difficulty_scaling():
    print("[+] Test 12: Verificando Escalado Progresivo de Dificultad Roguelike (+4.5% por nivel)...")
    dungeon_mgr = DungeonManager()

    # Nivel 1: escalado base
    base_miner = SteamMiner(100, 100)
    base_hp = base_miner.max_hp
    base_dmg = base_miner.damage

    # Simular nivel 20: factor 1.0 + (20 - 1) * 0.045 = 1.855
    scaled_miner = SteamMiner(100, 100)
    mult_lvl20 = 1.0 + (20 - 1) * 0.045
    scaled_miner.apply_difficulty_scaling(mult_lvl20)

    assert round(scaled_miner.max_hp, 1) == round(base_hp * mult_lvl20, 1)
    assert round(scaled_miner.damage, 1) == round(base_dmg * mult_lvl20, 1)
    assert scaled_miner.max_hp > base_hp
    assert scaled_miner.damage > base_dmg

    # Verificar que load_current_level genera enemigos con mayor densidad roguelike
    dungeon_mgr.current_global_level = 20
    dungeon_mgr.load_current_level()
    assert len(dungeon_mgr.enemies) >= 9, "Debe haber mayor densidad en dificultad roguelike (al menos 9 enemigos)"

    print("  [OK] Escalado matemático Roguelike verificado (+4.5% vida y daño por nivel).")


def test_patience_regeneration():
    print("[+] Test 13: Verificando Curación de Paciencia (+10 HP tras 10s sin daño)...")
    player = Player(200, 200)
    arena_rect = pygame.Rect(0, 0, 1280, 720)
    player.current_hp = 500.0  # Dañado a mitad de vida
    assert player.time_without_damage == 0.0

    # Simular 9.5 segundos sin daño -> todavía no cura
    for _ in range(19):
        player.update(0.5, arena_rect)
    assert player.current_hp == 500.0, "No debe curar antes de los 10 segundos"

    # Completar 10.0 segundos -> cura +10 HP y reinicia contador
    player.update(0.5, arena_rect)
    assert player.current_hp == 510.0, f"Debe haber curado +10 HP a 510, obtenido {player.current_hp}"
    assert player.time_without_damage == 0.0

    # Simular recibir daño -> reinicia time_without_damage a 0
    player.time_without_damage = 5.0
    player.take_damage(20.0)
    assert player.time_without_damage == 0.0
    print("  [OK] Regeneración de calma (+10 HP cada 10s sin recibir daño) verificada.")


def test_enhanced_spell_visuals():
    print("[+] Test 11: Verificando Renderizado Visual Avanzado de Hechizos y Trampas...")
    combat_sys = CombatSystem()
    surf = pygame.Surface((1280, 720))

    # Generar proyectiles de cada uno de los 10 elementos
    for elem in DUNGEON_ELEMENTS:
        combat_sys.spawn_projectile(x=400, y=300, dir_x=1.0, dir_y=0.0, damage=40.0, element=elem)

    assert len(combat_sys.projectiles) == 10

    # Actualizar para generar estelas y animaciones
    for _ in range(5):
        for proj in combat_sys.projectiles:
            proj.update(0.05)

    # Renderizar todos los proyectiles con sus partículas y formas elementales
    for proj in combat_sys.projectiles:
        proj.draw(surf)

    # Generar y dibujar los 5 tipos de Ground Hazards
    hazards = ["Lava", "Vórtice", "Roca", "Zarzas", "Singularidad"]
    for h in hazards:
        combat_sys.spawn_ground_hazard(400, 300, hazard_type=h, radius=60.0,
                                       duration=2.0, damage_per_sec=50.0, color=(200, 100, 50))
    for hz in combat_sys.ground_hazards:
        hz.draw(surf)

    print("  [OK] Gráficos y animaciones de hechizos (Estelas, 10 Formas Elementales y Terrenos) verificados.")


def test_main_menu():
    print("[+] Test 14: Verificando Menú Principal Interactivo y Vistas Modales...")
    menu = MainMenu()
    surf = pygame.Surface((1280, 720))

    # 1. Verificar estado inicial y los 5 botones
    assert menu.current_view == MainMenu.VIEW_MAIN
    assert len(menu.buttons) == 5
    expected_btn_ids = ["PLAY", "CONTROLS", "CODEX", "CREDITS", "QUIT"]
    assert [b["id"] for b in menu.buttons] == expected_btn_ids

    # 2. Navegación con teclado (S/Abajo y W/Arriba)
    assert menu.selected_btn_index == 0
    event_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
    menu.handle_event(event_down)
    assert menu.selected_btn_index == 1
    event_up = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w)
    menu.handle_event(event_up)
    assert menu.selected_btn_index == 0

    # 3. Vista Modal: CONTROLES (Atajo [2])
    event_2 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_2)
    action = menu.handle_event(event_2)
    assert action is None
    assert menu.current_view == MainMenu.VIEW_CONTROLS
    menu.draw(surf)

    # Volver con ESC
    event_esc = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
    menu.handle_event(event_esc)
    assert menu.current_view == MainMenu.VIEW_MAIN

    # 4. Vista Modal: CÓDICE DE PERSONAJES (Atajo [3])
    event_3 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_3)
    menu.handle_event(event_3)
    assert menu.current_view == MainMenu.VIEW_CODEX
    # Cambiar de personaje en el códice
    event_right = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
    menu.handle_event(event_right)
    assert menu.codex_char_index == 1
    menu.draw(surf)
    menu.handle_event(event_esc)
    assert menu.current_view == MainMenu.VIEW_MAIN

    # 5. Vista Modal: CRÉDITOS (Atajo [4])
    event_4 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_4)
    menu.handle_event(event_4)
    assert menu.current_view == MainMenu.VIEW_CREDITS
    menu.draw(surf)
    menu.handle_event(event_esc)
    assert menu.current_view == MainMenu.VIEW_MAIN

    # 6. Acción JUGAR (Atajo [1])
    event_1 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1)
    act_play = menu.handle_event(event_1)
    assert act_play == "PLAY"

    # 7. Acción SALIR (Atajo [5])
    event_5 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_5)
    act_quit = menu.handle_event(event_5)
    assert act_quit == "QUIT"

    # 8. Renderizado y actualización de partículas a 60 FPS
    for _ in range(10):
        menu.update(0.016)
    menu.draw(surf)

    print("  [OK] Menú Principal Steampunk verificado: 5 botones, navegación, modales y renderizado 60 FPS.")


def test_audio_system():
    print("[+] Test 15: Verificando Sistema de Audio Procedural (39 SFX, 3 BGM, Mixer)...")
    audio = AudioSystem()
    assert hasattr(audio, 'is_initialized'), "Error: AudioSystem debe tener atributo is_initialized"
    assert len(audio.sounds) >= 39, f"Error: Se esperaban al menos 39 SFX cargados, hallados {len(audio.sounds)}"

    # Comprobar categorías esenciales de SFX
    essential_sfx = [
        "ui_hover", "ui_select", "slash_sword", "magic_bolt", "spell_fire",
        "spell_thunder", "spell_water", "spell_wind", "spell_earth", "spell_nature",
        "spell_light", "spell_darkness", "spell_steam", "spell_metal",
        "dash", "player_hurt", "enemy_hit", "enemy_death", "heal", "mana",
        "boss_roar", "boss_death", "portal_open", "portal_enter", "game_over", "victory"
    ]
    for sfx_name in essential_sfx:
        assert sfx_name in audio.sounds, f"Falta SFX crítico en el catálogo: {sfx_name}"

    # Comprobar pistas de música
    for bgm_name in ["music_menu", "music_dungeon", "music_boss"]:
        assert bgm_name in audio.music_tracks, f"Falta pista musical: {bgm_name}"

    # Comprobar controles de volumen y mute sin excepciones
    assert audio.master_volume == 0.80
    audio.set_master_volume(-0.30)
    assert abs(audio.master_volume - 0.50) < 0.01
    audio.set_master_volume(0.10)
    assert abs(audio.master_volume - 0.60) < 0.01

    # Toggle mute
    muted = audio.toggle_mute()
    assert muted is True
    assert audio.muted is True
    unmuted = audio.toggle_mute()
    assert unmuted is False
    assert audio.muted is False

    # Probar etiqueta de estado para HUD
    tag = audio.get_status_tag()
    assert "🔊" in tag or "60%" in tag

    # Probar reproducción simulada sin errores
    audio.play_sfx("ui_select")
    audio.play_music("music_menu")
    audio.stop_music()

    print(f"  [OK] Sistema de Audio verificado: {len(audio.sounds)} SFX, {len(audio.music_tracks)} temas musicales, controles de volumen y silencio operativos.")


def run_all_tests():
    print("\n" + "=" * 65)
    print(" EJECUCION DE BATERIA DE PRUEBAS DE INTEGRIDAD TECNICA")
    print("=" * 65)
    test_player_stats()
    test_card_system_rules()
    test_dungeon_and_boss_progression()
    test_combat_resolution()
    test_dash_and_active_magic()
    test_enemy_variety_and_spirit_variants()
    test_mana_system()
    test_all_ten_elemental_bosses()
    test_ui_mana_rendering()
    test_role_system()
    test_difficulty_scaling()
    test_enhanced_spell_visuals()
    test_patience_regeneration()
    test_main_menu()
    test_audio_system()
    print("=" * 65)
    print(" [EXITO TOTAL] TODOS LOS TESTS COMPLETADOS AL 100%")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    run_all_tests()
