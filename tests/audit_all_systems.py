import os
import sys
import traceback
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1280, 720))

from settings import DUNGEON_ELEMENTS, SCREEN_WIDTH, SCREEN_HEIGHT
from entities.player import Player
from entities.boss import ElementalBoss
from entities.enemy import (
    SteamMiner, SteamPistonCharger, SteamSharpshooter, SteamDrone,
    DemolitionTank, MiniMinion, ClockworkBombardier, AlchemicalPlagueDoctor,
    BrassShieldGuardian, ArcaneCultist, CursedReaper,
    ShadowSpirit, FlameSpirit, FrostSpirit, StormSpirit, NecroSpirit
)
from systems.card_system import CardSystem
from systems.role_system import RoleSystem
from systems.combat_system import CombatSystem
from systems.dungeon_manager import DungeonManager
from systems.audio_system import AudioSystem
from ui.ui_manager import UIManager
from ui.card_menu import CardMenu
from ui.role_menu import RoleMenu
from ui.main_menu import MainMenu
from ui.spell_swap_menu import SpellSwapMenu
from utils.asset_loader import AssetLoader

errors_found = []

print("=== INICIANDO AUDITORIA INTEGRAL DEL SISTEMA ===")

# -------------------------------------------------------------
# 1. AUDITORIA DE TODAS LAS CARTAS (348 cartas en CardSystem)
# -------------------------------------------------------------
print("\n[1] Auditando las 348 cartas del sistema...")
try:
    from systems.character_cards_database import CHARACTER_DECKS
    card_sys = CardSystem()
    all_cards = list(card_sys.standard_pool) + list(card_sys.golden_pool)
    for deck in CHARACTER_DECKS.values():
        all_cards.extend(deck)
    
    print(f"  Total de cartas a testear: {len(all_cards)}")
    for card in all_cards:
        p = Player(100, 100)
        try:
            card.apply(p)
        except Exception as e:
            errors_found.append(f"Error al aplicar carta '{card.name}' ({card.card_id}): {e}")
    print("  -> Verificación de cartas completada.")
except Exception as e:
    errors_found.append(f"Error catastrófico en CardSystem: {e}")

# -------------------------------------------------------------
# 2. AUDITORIA DE TODOS LOS ROLES (RoleSystem)
# -------------------------------------------------------------
print("\n[2] Auditando todos los roles y personajes...")
try:
    role_sys = RoleSystem()
    roles = role_sys.get_all_characters()
    print(f"  Total de roles a testear: {len(roles)}")
    for r in roles:
        p = Player(100, 100)
        try:
            r.apply(p)
            assert p.weapon_type is not None
            assert p.current_hp > 0
            assert p.current_mana > 0
        except Exception as e:
            errors_found.append(f"Error al aplicar rol '{r.name}' ({r.role_id}): {e}")
    print("  -> Verificación de roles completada.")
except Exception as e:
    errors_found.append(f"Error catastrófico en RoleSystem: {e}")

# -------------------------------------------------------------
# 3. AUDITORIA DE ARMAS Y COMBATE CUERPO A CUERPO / DISTANCIA
# -------------------------------------------------------------
print("\n[3] Auditando todos los 13 tipos de armas medievales y ataques...")
try:
    cs = CombatSystem()
    weapons = ["sword", "axe", "mace", "daggers", "crossbow", "scythe", "staff",
               "greatsword", "flask", "fists", "cannon", "totem", "flail"]
    surf = pygame.Surface((1280, 720))
    for w in weapons:
        p = Player(400, 300)
        p.weapon_type = w
        p.facing_angle = 45.0
        p.update_aim((500, 400))
        target = SteamMiner(430, 320)
        
        try:
            # Ataque
            if w == "staff":
                p.trigger_basic_arcane_shot()
                cs.cast_basic_arcane_bolt(p, (500, 400))
            else:
                p.trigger_attack()
                cs.process_player_melee_attack(p, [target])
            
            # Dibujar jugador con el arma activa y en reposo
            p.draw(surf)
            p.is_attacking = True
            p.swing_timer = 0.05
            p.draw(surf)
            
            # Sprite de asset loader
            ws = AssetLoader.get_weapon_sprite(w)
            assert ws is not None
        except Exception as e:
            errors_found.append(f"Error con arma '{w}': {e}\n{traceback.format_exc()}")
    print("  -> Verificación de armas completada.")
except Exception as e:
    errors_found.append(f"Error en combate con armas: {e}")

# -------------------------------------------------------------
# 4. AUDITORIA DE LOS 10 JEFES Y SUS 20 ATAQUES INSIGNIA
# -------------------------------------------------------------
print("\n[4] Auditando los 10 Jefes Elementales y sus 20 ataques firma...")
try:
    cs = CombatSystem()
    player = Player(400, 300)
    for elem in DUNGEON_ELEMENTS:
        boss = ElementalBoss(600, 360, elem, dungeon_index=1)
        try:
            boss._trigger_signature_attack_1(player, cs)
            boss._trigger_signature_attack_2(player, cs)
            
            # Ejecutar telegrafías
            for tele in list(boss.active_telegraphs):
                tele.timer = 0.0
                tele.update(0.016, boss, player, cs)
            
            # Actualizar y dibujar jefe
            boss.update(0.05, player, cs)
            boss.draw(surf)
            font = pygame.font.SysFont("Consolas", 14)
            boss.draw_boss_hud(surf, font)
        except Exception as e:
            errors_found.append(f"Error en Jefe de elemento '{elem}': {e}\n{traceback.format_exc()}")
    print("  -> Verificación de los 10 Jefes y 20 ataques completada.")
except Exception as e:
    errors_found.append(f"Error catastrófico en Jefes: {e}")

# -------------------------------------------------------------
# 5. AUDITORIA DE LOS 10 HECHIZOS MAGICOS ACTIVOS DEL JUGADOR
# -------------------------------------------------------------
print("\n[5] Auditando los 10 hechizos mágicos del jugador...")
try:
    cs = CombatSystem()
    target_dummy = SteamMiner(500, 300)
    for elem in DUNGEON_ELEMENTS:
        p = Player(400, 300)
        p.active_magic_elements = [elem]
        p.current_mana = 500.0
        try:
            cs.cast_player_active_magic(p, elem, (500, 300), targets=[target_dummy])
            cs.update(0.05, p, [target_dummy])
            cs.draw(surf)
        except Exception as e:
            errors_found.append(f"Error en hechizo elemental '{elem}': {e}\n{traceback.format_exc()}")
    print("  -> Verificación de hechizos completada.")
except Exception as e:
    errors_found.append(f"Error en magia del jugador: {e}")

# -------------------------------------------------------------
# 6. AUDITORIA DEL BESTIARIO COMPLETO (16 tipos de enemigos y variantes)
# -------------------------------------------------------------
print("\n[6] Auditando todos los 16 enemigos comunes, tácticos y espíritus malignos...")
try:
    cs = CombatSystem()
    p = Player(400, 300)
    enemy_classes = [
        SteamMiner, SteamPistonCharger, SteamSharpshooter, SteamDrone,
        DemolitionTank, MiniMinion, ClockworkBombardier, AlchemicalPlagueDoctor,
        BrassShieldGuardian, ArcaneCultist, CursedReaper,
        ShadowSpirit, FlameSpirit, FrostSpirit, StormSpirit, NecroSpirit
    ]
    for cls in enemy_classes:
        e = cls(450, 300)
        try:
            # Simular comportamiento
            e.update(0.05, p, [e], cs)
            e.take_damage(25.0)
            e.update(0.05, p, [e], cs)
            e.draw(surf)
        except Exception as e_err:
            errors_found.append(f"Error en enemigo '{cls.__name__}': {e_err}\n{traceback.format_exc()}")
    print("  -> Verificación de enemigos completada.")
except Exception as e:
    errors_found.append(f"Error en bestiario: {e}")

# -------------------------------------------------------------
# 7. AUDITORIA DE MODALES Y MENUS DE UI
# -------------------------------------------------------------
print("\n[7] Auditando todos los menús de interfaz (Main, Role, Card, SpellSwap, HUD)...")
try:
    audio = AudioSystem()
    clock = pygame.time.Clock()
    ui_mgr = UIManager()
    main_m = MainMenu(audio)
    role_m = RoleMenu(RoleSystem(), audio)
    card_m = CardMenu(audio)
    swap_m = SpellSwapMenu(audio)
    dm = DungeonManager()
    p = Player(400, 300)

    # Renderizados
    main_m.draw(surf)
    role_m.set_roles(RoleSystem().get_all_characters())
    role_m.draw(surf)
    
    card_m.set_cards(CardSystem().get_selection_offer(3, p))
    card_m.draw(surf)
    
    swap_m.open("Rayo Cósmico", ["Fuego", "Luz"])
    swap_m.draw(surf)

    from ui.pause_menu import PauseMenu
    pause_m = PauseMenu(audio)
    pause_m.open()
    pause_m.draw(surf, p, dm, audio_mgr=audio)
    pause_m.view = "CONTROLS"
    pause_m.draw(surf, p, dm, audio_mgr=audio)
    
    ui_mgr.draw_hud(surf, p, dm, clock, audio_mgr=audio)
    ui_mgr.draw_game_over(surf, dm)
    ui_mgr.draw_victory(surf)
    
    print("  -> Verificación de menús y HUD completada.")
except Exception as e:
    errors_found.append(f"Error en menús de UI: {e}\n{traceback.format_exc()}")

# -------------------------------------------------------------
# 8. AUDITORIA DE SIMULACION DE PROGRESION DE MAZMORRAS (1 a 10)
# -------------------------------------------------------------
print("\n[8] Auditando progresión de 10 mazmorras y portales...")
try:
    dm = DungeonManager()
    p = Player(400, 300)
    cs = CombatSystem()
    
    for level in range(1, 15):
        dm.advance_level(p)
        assert dm.current_global_level == level + 1
        dm.draw_arena(surf)
        dm.draw_entities(surf)
    print("  -> Verificación de progresión de mazmorras completada.")
except Exception as e:
    errors_found.append(f"Error en progresión de mazmorras: {e}\n{traceback.format_exc()}")

print("\n" + "=" * 60)
if len(errors_found) == 0:
    print("[RESULTADO FINAL]: ¡CERO ERRORES DETECTADOS EN TODO EL CODIGO!")
else:
    print(f"[RESULTADO FINAL]: Se encontraron {len(errors_found)} errores:")
    for err in errors_found:
        print(f"  - {err}")
print("=" * 60)
