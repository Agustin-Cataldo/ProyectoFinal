"""
================================================================================
MÓDULO: ui/ui_manager.py
RESPONSABILIDAD: Renderizado del HUD Steampunk, barras de salud e indicadores.
CONCEPTO ACADÉMICO: Interfaz de Usuario Desacoplada y Monitoreo de Rendimiento.
================================================================================
Renderiza:
- Barra de salud con estética de manómetro/caldera de vapor (500 HP).
- Panel de daño y arma ("Espada de piedra mediana" +20 DMG).
- Indicador de Mazmorra (1-5), Elemento actual y Nivel (1-50).
- Contador de FPS en tiempo real para verificar la cota de 60 FPS exigida.
- Pantallas de Fin de Partida (Game Over) y Victoria.
"""

import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BRASS, COLOR_COPPER,
    COLOR_DARK_STONE, COLOR_RED_HEALTH, COLOR_WHITE, COLOR_GOLD,
    COLOR_STEAM, COLOR_MANA, COLOR_MANA_BRIGHT, ELEMENT_COLORS,
    MANA_SPELL_COSTS
)


class UIManager:
    """Administrador de la interfaz en pantalla y estados de visualización."""

    def __init__(self):
        # Tipografías retro nativas
        self.font_large = pygame.font.SysFont("Consolas", 32, bold=True)
        self.font_mid = pygame.font.SysFont("Consolas", 20, bold=True)
        self.font_small = pygame.font.SysFont("Consolas", 14, bold=True)
        self.font_tiny = pygame.font.SysFont("Consolas", 11, bold=True)

        # Barra fantasma de daño retardado
        self.ghost_hp = None

    def draw_hud(self, surface: pygame.Surface, player, dungeon_mgr, clock: pygame.time.Clock, audio_mgr=None):
        """Dibuja el HUD completo en la parte superior e inferior de la pantalla con estética Steampunk."""
        # ---------------------------------------------------------------------
        # 1. BARRA DE SALUD DEL JUGADOR (1000 HP BASE) CON GHOST BAR RETARDADA
        # ---------------------------------------------------------------------
        bar_x = 24
        bar_y = 20
        bar_w = 280
        bar_h = 24

        # Actualizar ghost bar suave
        if self.ghost_hp is None or self.ghost_hp > player.max_hp:
            self.ghost_hp = player.current_hp
        if self.ghost_hp > player.current_hp:
            self.ghost_hp -= max(0.5, (self.ghost_hp - player.current_hp) * 0.08)
        else:
            self.ghost_hp = player.current_hp

        # Placa base oscura
        pygame.draw.rect(surface, (14, 16, 22), (bar_x - 4, bar_y - 4, bar_w + 8, bar_h + 8), border_radius=4)
        pygame.draw.rect(surface, COLOR_BRASS, (bar_x - 3, bar_y - 3, bar_w + 6, bar_h + 6), 2, border_radius=4)
        pygame.draw.rect(surface, (25, 27, 34), (bar_x, bar_y, bar_w, bar_h), border_radius=2)

        # Relleno de Ghost HP (daño recibido recientemente)
        ghost_ratio = max(0.0, min(1.0, self.ghost_hp / player.max_hp))
        ghost_w = int(bar_w * ghost_ratio)
        if ghost_w > 0:
            pygame.draw.rect(surface, (230, 126, 34), (bar_x, bar_y, ghost_w, bar_h), border_radius=2)

        # Relleno de HP real
        hp_ratio = max(0.0, min(1.0, player.current_hp / player.max_hp))
        fill_w = int(bar_w * hp_ratio)
        if fill_w > 0:
            pygame.draw.rect(surface, COLOR_RED_HEALTH, (bar_x, bar_y, fill_w, bar_h), border_radius=2)
            # Brillo superior en la barra
            pygame.draw.line(surface, (255, 120, 120), (bar_x + 1, bar_y + 1), (bar_x + fill_w - 2, bar_y + 1), 1)

        # Divisiones cada 250 HP para legibilidad táctica
        quarter_step = bar_w / 4.0
        for q in range(1, 4):
            div_x = int(bar_x + q * quarter_step)
            pygame.draw.line(surface, (40, 42, 50), (div_x, bar_y), (div_x, bar_y + bar_h), 1)

        # Texto de HP numérico
        hp_text = f"HP: {int(player.current_hp)} / {int(player.max_hp)}"
        hp_surf = self.font_small.render(hp_text, True, COLOR_WHITE)
        surface.blit(hp_surf, (bar_x + 8, bar_y + 4))

        # ---------------------------------------------------------------------
        # 1.2. BARRA DE MANÁ DEL JUGADOR (500 MP BASE)
        # ---------------------------------------------------------------------
        mana_y = bar_y + bar_h + 7
        mana_h = 18

        # Marco exterior y fondo
        pygame.draw.rect(surface, (14, 16, 22), (bar_x - 4, mana_y - 4, bar_w + 8, mana_h + 8), border_radius=4)
        pygame.draw.rect(surface, COLOR_BRASS, (bar_x - 3, mana_y - 3, bar_w + 6, mana_h + 6), 2, border_radius=4)
        pygame.draw.rect(surface, (20, 25, 35), (bar_x, mana_y, bar_w, mana_h), border_radius=2)

        # Relleno de Maná
        mana_ratio = max(0.0, min(1.0, player.current_mana / player.max_mana))
        fill_mana_w = int(bar_w * mana_ratio)
        if fill_mana_w > 0:
            pygame.draw.rect(surface, COLOR_MANA, (bar_x, mana_y, fill_mana_w, mana_h), border_radius=2)
            pygame.draw.line(surface, COLOR_MANA_BRIGHT, (bar_x + 1, mana_y + 1), (bar_x + fill_mana_w - 2, mana_y + 1), 1)

        # Divisiones cada 125 MP
        for q in range(1, 4):
            div_x = int(bar_x + q * quarter_step)
            pygame.draw.line(surface, (25, 35, 50), (div_x, mana_y), (div_x, mana_y + mana_h), 1)

        # Texto de MP numérico
        mana_text = f"MP: {int(player.current_mana)} / {int(player.max_mana)}"
        mana_surf = self.font_small.render(mana_text, True, COLOR_WHITE)
        surface.blit(mana_surf, (bar_x + 8, mana_y + 2))

        # ---------------------------------------------------------------------
        # 2. PANEL DE COMBATE: ROL, ARMA Y DAÑO ACTUAL
        # ---------------------------------------------------------------------
        dmg_y = mana_y + mana_h + 9
        role_label = getattr(player, 'role_name', 'Aventurero')
        dmg_text = (f"Rol: [{role_label}] | Arma: {player.weapon_name} | "
                    f"Daño: {int(player.total_damage)} DMG")
        dmg_surf = self.font_small.render(dmg_text, True, COLOR_STEAM)
        surface.blit(dmg_surf, (bar_x, dmg_y))

        # ---------------------------------------------------------------------
        # 3. PANEL DE MAZMORRA Y ELEMENTO ACTUAL
        # ---------------------------------------------------------------------
        elem_name = dungeon_mgr.current_element
        elem_color = ELEMENT_COLORS.get(elem_name, COLOR_GOLD)

        info_text = (f"Mazmorra {dungeon_mgr.current_dungeon_index}/5 "
                     f"[{elem_name.upper()}] • Sala {dungeon_mgr.current_level_in_dungeon}/10 "
                     f"(Nivel Global: {dungeon_mgr.current_global_level}/50)")
        info_surf = self.font_mid.render(info_text, True, elem_color)
        info_rect = info_surf.get_rect(center=(SCREEN_WIDTH // 2, 22))

        # Placa gótica de fondo para la mazmorra
        bg_rect = info_rect.inflate(30, 12)
        pygame.draw.rect(surface, (16, 18, 24), bg_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_BRASS, bg_rect, 1, border_radius=6)
        surface.blit(info_surf, info_rect)

        # ---------------------------------------------------------------------
        # 4. DASH Y HECHIZOS MÁGICOS ACTIVOS DEL JUGADOR
        # ---------------------------------------------------------------------
        spell_y = dmg_y + 20

        # Indicador de Dash de vapor
        dash_ready = player.dash_cooldown_timer <= 0
        dash_txt = "[Espacio] Dash: LISTO" if dash_ready else f"[Espacio] Dash: {player.dash_cooldown_timer:.1f}s"
        dash_col = (46, 204, 113) if dash_ready else (230, 126, 34)
        surface.blit(self.font_small.render(dash_txt, True, dash_col), (bar_x, spell_y))

        # Indicador de Hechizo Primario (Clic Derecho)
        if player.primary_magic:
            m1_name = player.primary_magic
            m1_cost = MANA_SPELL_COSTS.get(m1_name, 75)
            m1_col = ELEMENT_COLORS.get(m1_name, COLOR_GOLD)
            can_afford = player.has_mana(m1_cost)

            if player.magic_primary_cooldown <= 0:
                if can_afford:
                    m1_txt = f"[Clic Der / E] {m1_name} ({m1_cost} MP): LISTO"
                    m1_state_col = m1_col
                else:
                    m1_txt = f"[Clic Der / E] {m1_name} ({m1_cost} MP): [¡FALTA MANÁ!]"
                    m1_state_col = (231, 76, 60)
            else:
                m1_txt = f"[Clic Der] {m1_name} ({m1_cost} MP): {player.magic_primary_cooldown:.1f}s"
                m1_state_col = (180, 185, 195)
            surface.blit(self.font_small.render(m1_txt, True, m1_state_col), (bar_x, spell_y + 18))

            # Indicador de Hechizo Secundario (Tecla Q)
            if player.secondary_magic:
                m2_name = player.secondary_magic
                m2_cost = MANA_SPELL_COSTS.get(m2_name, 75)
                m2_col = ELEMENT_COLORS.get(m2_name, COLOR_GOLD)
                can_afford_2 = player.has_mana(m2_cost)
                if player.magic_secondary_cooldown <= 0:
                    if can_afford_2:
                        m2_txt = f"[Q] {m2_name} ({m2_cost} MP): LISTO"
                        m2_state_col = m2_col
                    else:
                        m2_txt = f"[Q] {m2_name} ({m2_cost} MP): [¡FALTA MANÁ!]"
                        m2_state_col = (231, 76, 60)
                else:
                    m2_txt = f"[Q] {m2_name} ({m2_cost} MP): {player.magic_secondary_cooldown:.1f}s"
                    m2_state_col = (180, 185, 195)
                surface.blit(self.font_small.render(m2_txt, True, m2_state_col), (bar_x, spell_y + 36))
        else:
            info_spell = "[Clic Der] Magia: Desbloquea en cartas rúnicas (Niveles 3, 6, 9...)"
            surface.blit(self.font_small.render(info_spell, True, (160, 160, 170)), (bar_x, spell_y + 18))

        # ---------------------------------------------------------------------
        # 5. MONITOR DE FPS (REQUERIMIENTO: 60 FPS ESTABLES)
        # ---------------------------------------------------------------------
        fps = int(clock.get_fps())
        fps_color = (46, 204, 113) if fps >= 55 else (231, 76, 60)
        fps_text = f"FPS: {fps} (Objetivo: 60)"
        fps_surf = self.font_small.render(fps_text, True, fps_color)
        surface.blit(fps_surf, (SCREEN_WIDTH - 180, 20))

        # 6. ESTADO DE AUDIO (VOLUMEN Y SILENCIO [M])
        if audio_mgr:
            audio_text = audio_mgr.get_status_tag()
            audio_col = (200, 215, 230) if not audio_mgr.muted else (231, 76, 60)
            audio_surf = self.font_tiny.render(audio_text, True, audio_col)
            surface.blit(audio_surf, (SCREEN_WIDTH - 180, 42))

        # 7. INDICADOR DE PAUSA [ESC / P]
        pause_hint = "[ESC / P] Pausa"
        surface.blit(self.font_tiny.render(pause_hint, True, COLOR_GOLD), (SCREEN_WIDTH - 180, 60))

        # Si hay jefe activo, dibujar su HUD superior
        if dungeon_mgr.active_boss:
            dungeon_mgr.active_boss.draw_boss_hud(surface, self.font_small)

        # Indicador de sala despejada / portal
        if dungeon_mgr.portal_active and not dungeon_mgr.game_won:
            port_text = "¡SALA DESPEJADA! Entra al portal de vapor para avanzar."
            port_surf = self.font_mid.render(port_text, True, (0, 255, 255))
            port_rect = port_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 35))
            surface.blit(port_surf, port_rect)

    def draw_game_over(self, surface: pygame.Surface, dungeon_mgr):
        """Pantalla de Game Over con estadísticas alcanzadas."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        t1 = self.font_large.render("HAS CAÍDO EN COMBATE", True, COLOR_RED_HEALTH)
        t2 = self.font_mid.render(
            f"Alcanzaste el Nivel Global {dungeon_mgr.current_global_level}/50 "
            f"(Mazmorra {dungeon_mgr.current_dungeon_index})",
            True, COLOR_WHITE
        )
        t3 = self.font_mid.render("Presiona [ESPACIO] o [R] para reiniciar con nuevos elementos", True, COLOR_GOLD)

        surface.blit(t1, t1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)))
        surface.blit(t2, t2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
        surface.blit(t3, t3.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)))

    def draw_victory(self, surface: pygame.Surface):
        """Pantalla de Victoria Final al superar los 50 niveles."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 25, 40, 220))
        surface.blit(overlay, (0, 0))

        t1 = self.font_large.render("¡VICTORIA TOTAL! 50 NIVELES SUPERADOS", True, COLOR_GOLD)
        t2 = self.font_mid.render("Has conquistado las 5 Mazmorras Elementales y sus Jefes.", True, COLOR_WHITE)
        t3 = self.font_mid.render("Presiona [ESPACIO] para jugar una nueva partida.", True, (0, 255, 255))

        surface.blit(t1, t1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)))
        surface.blit(t2, t2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
        surface.blit(t3, t3.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)))
