"""
================================================================================
MÓDULO: game_engine.py
RESPONSABILIDAD: Orquestador general del ciclo de vida y máquina de estados del juego.
CONCEPTO ACADÉMICO: Patrón State (Máquina de Estados Finita Global) y Game Loop.
================================================================================
Coordina las transiciones entre estados:
- MENU: Pantalla de inicio con temática Steampunk.
- PLAYING: Bucle activo de combate Hack & Slash a 60 FPS.
- CARD_SELECT: Pausa interactiva para elegir mejoras cada 3 niveles.
- GAME_OVER: Pantalla de derrota con opción de reinicio aleatorizado.
- VICTORY: Pantalla de victoria tras superar los 50 niveles.
"""

import sys
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_TITLE,
    COLOR_BLACK, COLOR_BRASS, COLOR_STEAM, COLOR_WHITE, COLOR_GOLD
)
from entities.player import Player
from systems.combat_system import CombatSystem
from systems.card_system import CardSystem
from systems.dungeon_manager import DungeonManager
from systems.role_system import RoleSystem
from systems.audio_system import AudioSystem
from ui.ui_manager import UIManager
from ui.card_menu import CardMenu
from ui.role_menu import RoleMenu
from ui.main_menu import MainMenu
from ui.spell_swap_menu import SpellSwapMenu
from ui.pause_menu import PauseMenu


class GameEngine:
    """Núcleo del motor que integra entidades, sistemas y renderizado."""

    # Constantes de Estado
    STATE_MENU = "MENU"
    STATE_ROLE_SELECT = "ROLE_SELECT"
    STATE_PLAYING = "PLAYING"
    STATE_CARD_SELECT = "CARD_SELECT"
    STATE_SPELL_SWAP = "SPELL_SWAP"
    STATE_PAUSED = "PAUSED"
    STATE_GAME_OVER = "GAME_OVER"
    STATE_VICTORY = "VICTORY"

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock):
        self.screen = screen
        self.clock = clock
        self.running = True
        self.current_state = self.STATE_MENU

        # Inicialización de subsistemas
        self.audio_system = AudioSystem()
        self.combat_system = CombatSystem(audio_system=self.audio_system)
        self.card_system = CardSystem()
        self.role_system = RoleSystem()
        self.dungeon_manager = DungeonManager()
        self.ui_manager = UIManager()
        self.card_menu = CardMenu(audio_system=self.audio_system)
        self.role_menu = RoleMenu(self.role_system, audio_system=self.audio_system)
        self.main_menu = MainMenu(audio_system=self.audio_system)
        self.spell_swap_menu = SpellSwapMenu(audio_system=self.audio_system)
        self.pause_menu = PauseMenu(audio_system=self.audio_system)
        self._portal_was_active = False

        # Iniciar música ambiental del menú
        self.audio_system.play_music("music_menu")

        # Superficie de renderizado del mundo para soporte de temblor de pantalla (Screen Shake)
        self.world_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Instancia del Héroe (centrado en la parte inferior de la sala)
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120)

        # Rectángulo límite de la arena de combate
        self.arena_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

    def reset_game(self, role=None):
        """Reinicia la partida restableciendo al jugador, mazmorras y sistemas."""
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120)
        if role is not None:
            self.player.character_id = getattr(role, 'role_id', 'berserker')
            role.apply(self.player)
        self.dungeon_manager.reset_run()
        self.combat_system = CombatSystem(audio_system=self.audio_system)
        self.current_state = self.STATE_PLAYING
        self._portal_was_active = False
        self.audio_system.play_music("music_dungeon")

    def handle_events(self):
        """Distribuye los eventos de Pygame según el estado actual."""
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            # Controles globales de audio: Tecla M (Silenciar) y Teclas +/- (Volumen)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m and self.current_state not in (self.STATE_GAME_OVER, self.STATE_VICTORY):
                    self.audio_system.toggle_mute()
                elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                    self.audio_system.set_master_volume(+0.10)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self.audio_system.set_master_volume(-0.10)

            # Manejo según el estado activo
            if self.current_state == self.STATE_MENU:
                action = self.main_menu.handle_event(event)
                if action == "PLAY":
                    self.audio_system.play_sfx("ui_select")
                    all_characters = self.role_system.get_all_characters()
                    self.role_menu.set_roles(all_characters)
                    self.current_state = self.STATE_ROLE_SELECT
                elif action == "QUIT":
                    self.running = False
                    return

            elif self.current_state == self.STATE_ROLE_SELECT:
                chosen_role = self.role_menu.handle_event(event)
                if chosen_role == "BACK":
                    self.audio_system.play_sfx("ui_select")
                    self.audio_system.play_music("music_menu")
                    self.current_state = self.STATE_MENU
                elif chosen_role:
                    self.audio_system.play_sfx("ui_select")
                    self.reset_game(role=chosen_role)

            elif self.current_state == self.STATE_PLAYING:
                # 1. ATAQUE PRINCIPAL (Clic Izquierdo) - Arma Medieval o Dardo Arcano
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.player.trigger_attack():
                        targets = (self.dungeon_manager.enemies or []) + ([self.dungeon_manager.active_boss] if self.dungeon_manager.active_boss else [])
                        self.combat_system.process_player_melee_attack(self.player, targets)
                    elif not getattr(self.player, 'has_melee_weapon', True) or self.player.weapon_type == "staff":
                        if self.player.trigger_basic_arcane_shot():
                            self.combat_system.cast_basic_arcane_bolt(self.player, mouse_pos)

                # 2. HECHIZO MÁGICO PRINCIPAL (Clic Derecho)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    elem = self.player.trigger_primary_magic()
                    if elem:
                        targets = (self.dungeon_manager.enemies or []) + ([self.dungeon_manager.active_boss] if self.dungeon_manager.active_boss else [])
                        self.combat_system.cast_player_active_magic(self.player, elem, mouse_pos, targets=targets)

                # 3. CONTROLES POR TECLADO (Dash y Hechizos)
                elif event.type == pygame.KEYDOWN:
                    # Barra Espaciadora: Esquiva / Dash con i-frames
                    if event.key == pygame.K_SPACE:
                        if self.player.trigger_dash():
                            self.audio_system.play_sfx("dash")

                    # Tecla V: Alternativa para Disparo Arcano del Mago
                    elif event.key == pygame.K_v:
                        if not getattr(self.player, 'has_melee_weapon', True) or self.player.weapon_type == "staff":
                            if self.player.trigger_basic_arcane_shot():
                                self.combat_system.cast_basic_arcane_bolt(self.player, mouse_pos)

                    # Tecla E: Alternativa para Hechizo Mágico Principal
                    elif event.key == pygame.K_e:
                        elem = self.player.trigger_primary_magic()
                        if elem:
                            targets = (self.dungeon_manager.enemies or []) + ([self.dungeon_manager.active_boss] if self.dungeon_manager.active_boss else [])
                            self.combat_system.cast_player_active_magic(self.player, elem, mouse_pos, targets=targets)

                    # Tecla Q: Hechizo Mágico Secundario
                    elif event.key == pygame.K_q:
                        elem = self.player.trigger_secondary_magic()
                        if elem:
                            targets = (self.dungeon_manager.enemies or []) + ([self.dungeon_manager.active_boss] if self.dungeon_manager.active_boss else [])
                            self.combat_system.cast_player_active_magic(self.player, elem, mouse_pos, targets=targets)

                    # Tecla ESC o P: Pausar la partida
                    elif event.key in (pygame.K_ESCAPE, pygame.K_p):
                        self.audio_system.play_sfx("ui_select")
                        self.pause_menu.open()
                        self.current_state = self.STATE_PAUSED

            elif self.current_state == self.STATE_CARD_SELECT:
                # Delegar interacción al menú de cartas
                chosen_card = self.card_menu.handle_event(event)
                if chosen_card:
                    self.audio_system.play_sfx("ui_select")
                    # Aplicar efectos de la carta al jugador
                    chosen_card.apply(self.player)
                    # Comprobar si la carta generó un hechizo pendiente de intercambio
                    pending = getattr(self.player, '_pending_spell_swap', None)
                    if pending:
                        self.player._pending_spell_swap = None
                        self.spell_swap_menu.open(pending, self.player.active_magic_elements)
                        self.current_state = self.STATE_SPELL_SWAP
                    else:
                        # Reanudar combate
                        self.current_state = self.STATE_PLAYING

            elif self.current_state == self.STATE_SPELL_SWAP:
                result = self.spell_swap_menu.handle_event(event)
                if result:
                    self.audio_system.play_sfx("ui_select")
                    action, spell = result
                    if action == "SLOT_1" and spell:
                        # Reemplazar ranura primaria (índice 0)
                        if len(self.player.active_magic_elements) >= 1:
                            self.player.active_magic_elements[0] = spell
                        else:
                            self.player.active_magic_elements.append(spell)
                    elif action == "SLOT_2" and spell:
                        # Reemplazar ranura secundaria (índice 1)
                        if len(self.player.active_magic_elements) >= 2:
                            self.player.active_magic_elements[1] = spell
                        elif len(self.player.active_magic_elements) == 1:
                            self.player.active_magic_elements.append(spell)
                        else:
                            self.player.active_magic_elements.append(spell)
                    # "CANCEL" = no reemplazar, el hechizo se descarta
                    self.current_state = self.STATE_PLAYING

            elif self.current_state == self.STATE_PAUSED:
                action = self.pause_menu.handle_event(event)
                if action == "RESUME":
                    self.audio_system.play_sfx("ui_select")
                    self.current_state = self.STATE_PLAYING
                elif action == "RESTART":
                    self.audio_system.play_sfx("ui_select")
                    char_id = getattr(self.player, 'character_id', getattr(self.player, 'role_name', 'berserker'))
                    chosen_role = self.role_system.get_character(char_id)
                    self.reset_game(role=chosen_role)
                elif action == "MAIN_MENU":
                    self.audio_system.play_sfx("ui_select")
                    self.audio_system.play_music("music_menu")
                    self.current_state = self.STATE_MENU

            elif self.current_state in (self.STATE_GAME_OVER, self.STATE_VICTORY):
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_r):
                        self.audio_system.play_sfx("ui_select")
                        all_characters = self.role_system.get_all_characters()
                        self.role_menu.set_roles(all_characters)
                        self.current_state = self.STATE_ROLE_SELECT
                    elif event.key in (pygame.K_ESCAPE, pygame.K_m):
                        self.audio_system.play_sfx("ui_select")
                        self.audio_system.play_music("music_menu")
                        self.current_state = self.STATE_MENU

    def update(self, dt: float):
        """Actualiza la lógica física del juego según el estado."""
        if self.current_state == self.STATE_MENU:
            self.main_menu.update(dt)

        elif self.current_state == self.STATE_PAUSED:
            self.pause_menu.update(dt)

        elif self.current_state == self.STATE_PLAYING:
            # 1. Actualizar orientación del jugador hacia el ratón
            mouse_pos = pygame.mouse.get_pos()
            self.player.update_aim(mouse_pos)
            self.player.handle_input()
            prev_hp = self.player.current_hp
            self.player.update(dt, self.arena_rect)
            if self.player.current_hp < prev_hp and self.player.current_hp > 0:
                self.audio_system.play_sfx("player_hurt")

            # 2. Comprobar muerte del jugador
            if self.player.current_hp <= 0:
                self.current_state = self.STATE_GAME_OVER
                self.audio_system.stop_music()
                self.audio_system.play_sfx("game_over")
                return

            # 3. Actualizar mazmorra y enemigos
            prev_level = self.dungeon_manager.current_global_level
            should_offer_cards, is_victory = self.dungeon_manager.update(dt, self.player, self.combat_system)

            if is_victory:
                self.current_state = self.STATE_VICTORY
                self.audio_system.stop_music()
                self.audio_system.play_sfx("victory")
                return

            if self.dungeon_manager.current_global_level > prev_level:
                self.audio_system.play_sfx("portal_enter")

            # Manejo del portal de salida de sala
            if self.dungeon_manager.portal_active and not self._portal_was_active:
                self._portal_was_active = True
                self.audio_system.play_sfx("portal_open")
            elif not self.dungeon_manager.portal_active:
                self._portal_was_active = False

            # Detección de Jefe y cambio musical dinámico
            if self.dungeon_manager.active_boss:
                if self.audio_system.current_music_name != "music_boss":
                    self.audio_system.play_music("music_boss")
                    self.audio_system.play_sfx("boss_roar")
            elif self.audio_system.current_music_name == "music_boss":
                self.audio_system.play_music("music_dungeon")
                self.audio_system.play_sfx("boss_death")

            if should_offer_cards:
                # Desplegar oferta de 3 cartas exclusivas del personaje (con posible dorada cada 5 rondas)
                offered_cards = self.card_system.get_selection_offer(self.dungeon_manager.current_global_level, self.player)
                self.card_menu.set_cards(offered_cards)
                self.audio_system.play_sfx("ui_card")
                self.current_state = self.STATE_CARD_SELECT

            # 4. Actualizar proyectiles, números de daño y partículas
            targets = (self.dungeon_manager.enemies or []) + ([self.dungeon_manager.active_boss] if self.dungeon_manager.active_boss else [])
            self.combat_system.update(dt, self.player, targets)

    def draw(self):
        """Renderiza la escena completa según el estado del juego."""
        if self.current_state == self.STATE_MENU:
            self.main_menu.draw(self.screen)
        elif self.current_state == self.STATE_ROLE_SELECT:
            self.dungeon_manager.draw_arena(self.screen)
            self.role_menu.draw(self.screen)
        else:
            # 1. Dibujar el mundo de combate en la superficie del mundo con efecto de temblor cinemático
            shake_ox, shake_oy = self.combat_system.get_screen_shake_offset()
            self.dungeon_manager.draw_arena(self.world_surface)
            self.dungeon_manager.draw_entities(self.world_surface)
            self.player.draw(self.world_surface)
            self.combat_system.draw(self.world_surface)

            # Volcar mundo a pantalla aplicando sacudida
            self.screen.fill((10, 10, 14))
            self.screen.blit(self.world_surface, (shake_ox, shake_oy))

            # 5. Dibujar HUD nítido directamente en pantalla sin sacudida
            self.ui_manager.draw_hud(self.screen, self.player, self.dungeon_manager, self.clock, audio_mgr=self.audio_system)

            # Modales superpuestos si aplica
            if self.current_state == self.STATE_CARD_SELECT:
                self.card_menu.draw(self.screen)
            elif self.current_state == self.STATE_SPELL_SWAP:
                self.spell_swap_menu.draw(self.screen)
            elif self.current_state == self.STATE_PAUSED:
                self.pause_menu.draw(self.screen, self.player, self.dungeon_manager, audio_mgr=self.audio_system)
            elif self.current_state == self.STATE_GAME_OVER:
                self.ui_manager.draw_game_over(self.screen, self.dungeon_manager)
            elif self.current_state == self.STATE_VICTORY:
                self.ui_manager.draw_victory(self.screen)

        pygame.display.flip()

    def run(self):
        """Bucle principal de ejecución a 60 FPS con delta-time."""
        while self.running:
            # dt en segundos (aprox 0.0166s a 60 FPS)
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)  # Prevenir salto brusco ("spiral of death") si la ventana pierde foco

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()
