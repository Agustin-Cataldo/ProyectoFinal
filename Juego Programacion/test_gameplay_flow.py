import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
from game_engine import GameEngine

def test_full_game_flow():
    print("[*] Iniciando simulación de flujo completo de juego headless...")
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    engine = GameEngine(screen, clock)

    # 1. Estado MENU inicial
    assert engine.current_state == GameEngine.STATE_MENU
    engine.draw()
    print("  -> Menú inicial dibujado correctamente.")

    # 2. Pulsar ESPACIO para ir a selección de personajes
    event_space = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
    pygame.event.post(event_space)
    engine.handle_events()
    assert engine.current_state == GameEngine.STATE_ROLE_SELECT
    assert len(engine.role_menu.roles) == 12
    engine.draw()
    print("  -> Menú de 12 Personajes Slay the Spire 2 abierto y renderizado.")

    # 2.1 Probar volver al Menú Principal con [ESC]
    event_esc = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
    pygame.event.post(event_esc)
    engine.handle_events()
    assert engine.current_state == GameEngine.STATE_MENU
    print("  -> Regreso al Menú Principal con [ESC] verificado.")

    # Volver a entrar con tecla [1] (JUGAR)
    event_1 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1)
    pygame.event.post(event_1)
    engine.handle_events()
    assert engine.current_state == GameEngine.STATE_ROLE_SELECT

    # 3. Elegir Personaje 4 (Mago Arcano) con la tecla '4'
    event_key4 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_4)
    pygame.event.post(event_key4)
    engine.handle_events()
    assert engine.current_state == GameEngine.STATE_PLAYING
    assert engine.player.role_name == "Mago Arcano"
    assert engine.player.character_id == "mage"
    assert engine.player.weapon_type == "staff"
    assert engine.player.has_melee_weapon is False
    print("  -> Mago Arcano seleccionado y partida iniciada con bastón rúnico.")

    # 4. Simular combate en sala activa
    engine.update(0.1)
    engine.draw()

    # Simular paso al nivel 3 y entrar al portal
    engine.dungeon_manager.current_global_level = 3
    engine.dungeon_manager.enemies.clear()
    engine.dungeon_manager.portal_active = True
    portal_rect = engine.dungeon_manager.portal_rect
    engine.player.pos.x = portal_rect.centerx
    engine.player.pos.y = portal_rect.centery

    should_offer, is_victory = engine.dungeon_manager.update(0.1, engine.player, engine.combat_system)
    assert should_offer is True
    assert not is_victory

    # Llamar al flujo de cartas como en engine.update
    offered_cards = engine.card_system.get_selection_offer(3, engine.player)
    engine.card_menu.set_cards(offered_cards)
    engine.current_state = GameEngine.STATE_CARD_SELECT
    assert len(offered_cards) == 3
    for c in offered_cards:
        assert c.character_id == "mage", f"Carta {c.name} no es de la baraja de Mago"
    print(f"  -> Oferta de cartas del Mago generada: {[c.name for c in offered_cards]}")
    engine.draw()

    # 5. Elegir la primera carta con la tecla '1'
    event_card1 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1)
    pygame.event.post(event_card1)
    engine.handle_events()
    if engine.current_state == GameEngine.STATE_SPELL_SWAP:
        # Si la carta era un hechizo nuevo, confirmar swap en ranura 1
        event_swap = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1)
        pygame.event.post(event_swap)
        engine.handle_events()
    assert engine.current_state == GameEngine.STATE_PLAYING
    print("  -> Carta aplicada con éxito al Mago y combate reanudado.")

    # 6. Probar Cazador Real con ballesta
    all_chars = engine.role_system.get_all_characters()
    hunter_char = next(c for c in all_chars if c.role_id == "hunter")
    engine.reset_game(role=hunter_char)
    assert engine.player.role_name == "Cazador"
    assert engine.player.weapon_type == "crossbow"
    hunter_offer = engine.card_system.get_selection_offer(1, engine.player)
    for c in hunter_offer:
        assert c.character_id == "hunter"
    print(f"  -> Cazador Real validado con cartas únicas: {[c.name for c in hunter_offer]}")

    # 7. Probar Nigromante Abisal con guadaña y almas
    necro_char = next(c for c in all_chars if c.role_id == "necromancer")
    engine.reset_game(role=necro_char)
    assert engine.player.role_name == "Nigromante"
    assert engine.player.weapon_type == "scythe"
    assert engine.player.soul_harvest is True
    necro_offer = engine.card_system.get_selection_offer(1, engine.player)
    for c in necro_offer:
        assert c.character_id == "necromancer"
    print(f"  -> Nigromante Abisal validado con cartas únicas: {[c.name for c in necro_offer]}")

    # 8. Probar curación de paciencia (+10 HP tras 10s)
    engine.player.current_hp = 500.0
    for _ in range(20):
        engine.player.update(0.5, engine.arena_rect)
    assert engine.player.current_hp == 510.0
    print("  -> Curación de paciencia (+10 HP tras 10s) comprobada durante el juego.")

    print("[*] ¡Simulación de flujo completo superada con 100% de éxito!")

if __name__ == "__main__":
    test_full_game_flow()
