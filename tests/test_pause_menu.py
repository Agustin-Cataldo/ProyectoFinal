import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

from game_engine import GameEngine
from ui.pause_menu import PauseMenu

print("=== INICIANDO PRUEBAS DEL MENÚ DE PAUSA ===")

engine = GameEngine(screen, clock)

# 1. Iniciar partida con un personaje
all_chars = engine.role_system.get_all_characters()
paladin_role = all_chars[1]  # Paladín Templario
engine.reset_game(role=paladin_role)
assert engine.current_state == GameEngine.STATE_PLAYING, "Debe estar en PLAYING"

# 2. Pulsar tecla ESC para pausar
pause_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
pygame.event.post(pause_event)
engine.handle_events()
assert engine.current_state == GameEngine.STATE_PAUSED, f"El estado debe ser PAUSED, obtenido {engine.current_state}"
print("  [OK] Tecla [ESC] transiciona correctamente a STATE_PAUSED.")

# 3. Verificar que el combate se congela durante la pausa
initial_enemy_x = engine.dungeon_manager.enemies[0].pos.x if engine.dungeon_manager.enemies else 0
engine.update(1.0)  # Simular 1 segundo transcurrido en pausa
if engine.dungeon_manager.enemies:
    assert engine.dungeon_manager.enemies[0].pos.x == initial_enemy_x, "Los enemigos no deben moverse mientras está pausado"
print("  [OK] El tiempo del mundo y los enemigos están 100% congelados durante la pausa.")

# 4. Renderizar la vista principal de pausa
engine.draw()
print("  [OK] Menú de Pausa dibujado exitosamente en pantalla.")

base_dir = os.path.dirname(os.path.abspath(__file__))

# 5. Guardar screenshot para inspección visual
screenshot_path = os.path.join(base_dir, "screenshot_pause_menu.png")
pygame.image.save(screen, screenshot_path)
print(f"  [OK] Captura de pantalla guardada en: {screenshot_path}")

# 6. Probar subvista de CONTROLES
ctrl_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_c)
pygame.event.post(ctrl_event)
engine.handle_events()
assert engine.pause_menu.view == "CONTROLS", "Debe cambiar a la vista CONTROLS"
engine.draw()
screenshot_ctrl_path = os.path.join(base_dir, "screenshot_pause_controls.png")
pygame.image.save(screen, screenshot_ctrl_path)
print("  [OK] Subvista de CONTROLES abierta y renderizada.")

# Volver a MAIN desde CONTROLS con ESC
esc_back_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
pygame.event.post(esc_back_event)
engine.handle_events()
assert engine.pause_menu.view == "MAIN", "Debe regresar a la vista MAIN"
print("  [OK] Retorno desde CONTROLES a MAIN verificado.")

# 7. Probar reanudación (RESUME) con tecla P
p_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p)
pygame.event.post(p_event)
engine.handle_events()
assert engine.current_state == GameEngine.STATE_PLAYING, "Debe regresar a STATE_PLAYING al pulsar P"
print("  [OK] Reanudación con tecla [P] verificada.")

# 8. Volver a pausar con tecla P
pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p))
engine.handle_events()
assert engine.current_state == GameEngine.STATE_PAUSED

# Probar silenciar/activar con tecla M o 3
init_mute = engine.audio_system.muted
pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_m))
engine.handle_events()
assert engine.audio_system.muted != init_mute, "Tecla M debe alternar estado de silenciado"
pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_3))
engine.handle_events()
assert engine.audio_system.muted == init_mute, "Tecla 3 debe alternar estado de silenciado"
print("  [OK] Silenciar y alternar audio en pausa verificado.")

# 9. Probar reinicio (RESTART) con tecla R
pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))
engine.handle_events()
assert engine.current_state == GameEngine.STATE_PLAYING, "Reiniciar debe volver a PLAYING"
assert engine.dungeon_manager.current_global_level == 1, "Debe reiniciar al nivel 1"
print("  [OK] Reinicio de partida desde el menú de pausa verificado.")

# 10. Pausar y salir al Menú Principal con tecla 5
pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
engine.handle_events()
assert engine.current_state == GameEngine.STATE_PAUSED

pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_5))
engine.handle_events()
assert engine.current_state == GameEngine.STATE_MENU, "Debe regresar a STATE_MENU al presionar 5"
print("  [OK] Salir al Menú Principal verificado.")

print("\n=== TODAS LAS PRUEBAS DEL MENÚ DE PAUSA SUPERADAS AL 100% ===")
