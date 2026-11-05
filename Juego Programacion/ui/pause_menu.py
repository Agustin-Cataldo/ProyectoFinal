"""
================================================================================
MÓDULO: ui/pause_menu.py
RESPONSABILIDAD: Menú de Pausa interactivo, temático Steampunk/Medieval con
                 resumen de estadísticas del héroe, controles y ajustes.
CONCEPTO ACADÉMICO: Patrón State para navegación UI modal, desacoplamiento y
                    retroalimentación audiovisual completa.
================================================================================
Permite al jugador:
1. Pausar el combate en cualquier momento presionando [ESC] o [P].
2. Consultar el estado del héroe: Rol, HP, Maná, Arma y Hechizos equipados.
3. Consultar la Guía Rápida de Controles sin salir de la partida.
4. Ajustar el volumen del audio y silenciar/activar con un clic.
5. Reiniciar la partida o abandonar de vuelta al Menú Principal.
"""

import math
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BRASS, COLOR_COPPER,
    COLOR_DARK_STONE, COLOR_GOLD, COLOR_WHITE, COLOR_STEAM,
    COLOR_RED_HEALTH, COLOR_MANA, COLOR_MANA_BRIGHT, ELEMENT_COLORS
)


class PauseMenu:
    """Menú de Pausa Steampunk con panel de estado del héroe, controles y ajustes."""

    def __init__(self, audio_system=None):
        self.audio_system = audio_system
        self.font_title = pygame.font.SysFont("Consolas", 24, bold=True)
        self.font_mid = pygame.font.SysFont("Consolas", 16, bold=True)
        self.font_small = pygame.font.SysFont("Consolas", 13, bold=True)
        self.font_tiny = pygame.font.SysFont("Consolas", 11)

        # Dimensiones del modal central
        self.modal_w = 680
        self.modal_h = 560
        self.modal_x = (SCREEN_WIDTH - self.modal_w) // 2
        self.modal_y = (SCREEN_HEIGHT - self.modal_h) // 2

        # Vistas internas: "MAIN" o "CONTROLS"
        self.view = "MAIN"
        self.anim_time = 0.0
        self.hovered_btn = None
        self.selected_index = 0

        # Botones de la vista principal
        self.buttons_main = [
            {"id": "RESUME", "label": "▶ REANUDAR PARTIDA [ESC]", "key": "1"},
            {"id": "CONTROLS", "label": "📜 GUÍA DE CONTROLES [C]", "key": "2"},
            {"id": "MUTE", "label": "🔊 SILENCIAR / ACTIVAR AUDIO [M]", "key": "3"},
            {"id": "RESTART", "label": "🔄 REINICIAR PARTIDA [R]", "key": "4"},
            {"id": "MAIN_MENU", "label": "🚪 MENÚ PRINCIPAL", "key": "5"}
        ]

    def open(self):
        """Abre el menú de pausa restableciendo la vista principal."""
        self.view = "MAIN"
        self.hovered_btn = None
        self.selected_index = 0

    def update(self, dt: float):
        """Actualiza animaciones visuales (engranajes y brillos)."""
        self.anim_time += dt

    def handle_event(self, event: pygame.event.Event) -> str:
        """
        Procesa eventos de entrada del teclado y ratón.
        Retorna: 'RESUME', 'RESTART', 'MAIN_MENU' o None.
        """
        mouse_pos = pygame.mouse.get_pos()

        # -------------------------------------------------------------
        # VISTA: GUÍA DE CONTROLES
        # -------------------------------------------------------------
        if self.view == "CONTROLS":
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_c, pygame.K_RETURN, pygame.K_SPACE):
                    if self.audio_system:
                        self.audio_system.play_sfx("ui_select")
                    self.view = "MAIN"
                    return None

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                back_rect = pygame.Rect(self.modal_x + self.modal_w // 2 - 120, self.modal_y + self.modal_h - 55, 240, 38)
                if back_rect.collidepoint(mouse_pos):
                    if self.audio_system:
                        self.audio_system.play_sfx("ui_select")
                    self.view = "MAIN"
                    return None
            return None

        # -------------------------------------------------------------
        # VISTA: PRINCIPAL DE PAUSA
        # -------------------------------------------------------------
        # 1. Atajos de Teclado
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_p):
                return "RESUME"

            # Navegación arriba / abajo
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.buttons_main)
                if self.audio_system:
                    self.audio_system.play_sfx("ui_hover")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.buttons_main)
                if self.audio_system:
                    self.audio_system.play_sfx("ui_hover")

            # Activación con ENTER o ESPACIO
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                chosen_id = self.buttons_main[self.selected_index]["id"]
                return self._activate_button_action(chosen_id)

            # Atajos numéricos directos [1] al [5]
            elif event.key in (pygame.K_1, pygame.K_KP1):
                return "RESUME"
            elif event.key in (pygame.K_2, pygame.K_KP2, pygame.K_c):
                self.view = "CONTROLS"
                if self.audio_system:
                    self.audio_system.play_sfx("ui_select")
            elif event.key in (pygame.K_3, pygame.K_KP3):
                if self.audio_system:
                    self.audio_system.toggle_mute()
            elif event.key in (pygame.K_4, pygame.K_KP4, pygame.K_r):
                return "RESTART"
            elif event.key in (pygame.K_5, pygame.K_KP5):
                return "MAIN_MENU"

        # 2. Interacción con Ratón (Clics)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            btn_rects = self._get_main_button_rects()
            for i, r in enumerate(btn_rects):
                if r.collidepoint(mouse_pos):
                    btn_id = self.buttons_main[i]["id"]
                    return self._activate_button_action(btn_id)

            # Botones compactos de volumen +/-
            vol_down_rect = pygame.Rect(self.modal_x + self.modal_w - 110, self.modal_y + 265, 30, 26)
            vol_up_rect = pygame.Rect(self.modal_x + self.modal_w - 75, self.modal_y + 265, 30, 26)
            if vol_down_rect.collidepoint(mouse_pos):
                if self.audio_system:
                    self.audio_system.set_master_volume(-0.10)
            elif vol_up_rect.collidepoint(mouse_pos):
                if self.audio_system:
                    self.audio_system.set_master_volume(+0.10)

        return None

    def _activate_button_action(self, btn_id: str) -> str:
        """Ejecuta la acción asociada al botón presionado."""
        if btn_id == "RESUME":
            return "RESUME"
        elif btn_id == "CONTROLS":
            self.view = "CONTROLS"
            if self.audio_system:
                self.audio_system.play_sfx("ui_select")
            return None
        elif btn_id == "MUTE":
            if self.audio_system:
                self.audio_system.toggle_mute()
            return None
        elif btn_id == "RESTART":
            return "RESTART"
        elif btn_id == "MAIN_MENU":
            return "MAIN_MENU"
        return None

    def _get_main_button_rects(self):
        """Calcula los rectángulos en pantalla para los botones de la vista principal."""
        rects = []
        btn_w = 460
        btn_h = 42
        start_y = self.modal_y + 285
        spacing = 50
        for i in range(len(self.buttons_main)):
            bx = self.modal_x + (self.modal_w - btn_w) // 2
            by = start_y + i * spacing
            rects.append(pygame.Rect(bx, by, btn_w, btn_h))
        return rects

    def draw(self, surface: pygame.Surface, player, dungeon_mgr, audio_mgr=None):
        """Renderiza el menú de pausa superpuesto con estética Steampunk."""
        mouse_pos = pygame.mouse.get_pos()

        # 1. Capa de oscurecimiento semitransparente sobre el mundo de juego
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 12, 18, 195))
        surface.blit(overlay, (0, 0))

        # 2. Caja modal principal (Panel Steampunk reforzado)
        modal_rect = pygame.Rect(self.modal_x, self.modal_y, self.modal_w, self.modal_h)
        pygame.draw.rect(surface, (20, 24, 30), modal_rect, border_radius=10)

        # Bordes decorativos dobles de bronce y cobre
        pygame.draw.rect(surface, COLOR_BRASS, modal_rect, 3, border_radius=10)
        inner_rect = modal_rect.inflate(-8, -8)
        pygame.draw.rect(surface, COLOR_COPPER, inner_rect, 1, border_radius=8)

        # Remaches en las cuatro esquinas
        for cx, cy in [
            (modal_rect.left + 14, modal_rect.top + 14),
            (modal_rect.right - 14, modal_rect.top + 14),
            (modal_rect.left + 14, modal_rect.bottom - 14),
            (modal_rect.right - 14, modal_rect.bottom - 14)
        ]:
            pygame.draw.circle(surface, COLOR_GOLD, (cx, cy), 5)
            pygame.draw.circle(surface, (50, 35, 15), (cx, cy), 3)

        # Engranajes decorativos en las esquinas superiores
        self._draw_corner_cog(surface, modal_rect.left + 28, modal_rect.top + 28, radius=14, angle=self.anim_time * 2.0)
        self._draw_corner_cog(surface, modal_rect.right - 28, modal_rect.top + 28, radius=14, angle=-self.anim_time * 2.0)

        # Encabezado principal
        title_surf = self.font_title.render("⚙  JUEGO PAUSADO  ⚙", True, COLOR_GOLD)
        surface.blit(title_surf, title_surf.get_rect(center=(self.modal_x + self.modal_w // 2, self.modal_y + 34)))

        sub_surf = self.font_tiny.render("« Pulsa [ESC] o [P] para continuar el combate en tiempo real »", True, COLOR_STEAM)
        surface.blit(sub_surf, sub_surf.get_rect(center=(self.modal_x + self.modal_w // 2, self.modal_y + 58)))

        # Línea divisoria decorativa
        pygame.draw.line(surface, COLOR_BRASS, (self.modal_x + 30, self.modal_y + 72), (self.modal_x + self.modal_w - 30, self.modal_y + 72), 2)

        # -------------------------------------------------------------
        # RENDERIZADO SEGÚN LA VISTA
        # -------------------------------------------------------------
        if self.view == "MAIN":
            self._draw_main_view(surface, player, dungeon_mgr, audio_mgr, mouse_pos)
        elif self.view == "CONTROLS":
            self._draw_controls_view(surface, mouse_pos)

    def _draw_main_view(self, surface: pygame.Surface, player, dungeon_mgr, audio_mgr, mouse_pos):
        """Dibuja el resumen de estadísticas del héroe y los botones principales."""
        # 1. TARJETA DE ESTADO ACTUAL DEL HÉROE
        card_rect = pygame.Rect(self.modal_x + 30, self.modal_y + 82, self.modal_w - 60, 185)
        pygame.draw.rect(surface, (14, 17, 23), card_rect, border_radius=6)
        pygame.draw.rect(surface, (60, 68, 80), card_rect, 1, border_radius=6)

        # Título de la tarjeta
        role_label = getattr(player, 'role_name', 'Héroe Legendario')
        header_text = f"🛡️ HÉROE: [{role_label.upper()}]  •  MAZMORRA {dungeon_mgr.current_dungeon_index}/5 [{dungeon_mgr.current_element.upper()}]"
        surface.blit(self.font_small.render(header_text, True, COLOR_GOLD), (card_rect.left + 16, card_rect.top + 10))

        # Nivel y sala
        lvl_text = f"Sala Actual: {dungeon_mgr.current_level_in_dungeon}/10  |  Nivel Global: {dungeon_mgr.current_global_level}/50"
        surface.blit(self.font_tiny.render(lvl_text, True, COLOR_STEAM), (card_rect.left + 16, card_rect.top + 30))

        # Barras de Salud y Maná
        bar_x = card_rect.left + 16
        bar_w = 260

        # Barra de Vida
        hp_y = card_rect.top + 54
        pygame.draw.rect(surface, (25, 27, 34), (bar_x, hp_y, bar_w, 18), border_radius=3)
        hp_ratio = max(0.0, min(1.0, player.current_hp / player.max_hp))
        if hp_ratio > 0:
            pygame.draw.rect(surface, COLOR_RED_HEALTH, (bar_x, hp_y, int(bar_w * hp_ratio), 18), border_radius=3)
        pygame.draw.rect(surface, (80, 85, 95), (bar_x, hp_y, bar_w, 18), 1, border_radius=3)
        hp_txt = f"HP: {int(player.current_hp)} / {int(player.max_hp)}"
        surface.blit(self.font_tiny.render(hp_txt, True, COLOR_WHITE), (bar_x + 8, hp_y + 2))

        # Barra de Maná
        mp_y = hp_y + 24
        pygame.draw.rect(surface, (20, 25, 35), (bar_x, mp_y, bar_w, 18), border_radius=3)
        mp_ratio = max(0.0, min(1.0, player.current_mana / player.max_mana))
        if mp_ratio > 0:
            pygame.draw.rect(surface, COLOR_MANA, (bar_x, mp_y, int(bar_w * mp_ratio), 18), border_radius=3)
        pygame.draw.rect(surface, (60, 80, 110), (bar_x, mp_y, bar_w, 18), 1, border_radius=3)
        mp_txt = f"MP: {int(player.current_mana)} / {int(player.max_mana)}"
        surface.blit(self.font_tiny.render(mp_txt, True, COLOR_WHITE), (bar_x + 8, mp_y + 2))

        # Arma y daño
        w_name = getattr(player, 'weapon_name', 'Arma Medieval')
        w_dmg = int(player.total_damage)
        w_txt = f"⚔️ Arma: {w_name} ({w_dmg} DMG)"
        surface.blit(self.font_small.render(w_txt, True, (230, 240, 255)), (bar_x, mp_y + 28))

        # Columna derecha: Hechizos Activos Equipados
        right_x = card_rect.left + 300
        surface.blit(self.font_small.render("🔮 HECHIZOS RÚNICOS EQUIPADOS:", True, COLOR_GOLD), (right_x, card_rect.top + 34))

        # Hechizo Primario
        m1 = player.primary_magic
        if m1:
            col1 = ELEMENT_COLORS.get(m1, COLOR_GOLD)
            m1_txt = f"• Primario [Clic Der / E]: {m1}"
            surface.blit(self.font_tiny.render(m1_txt, True, col1), (right_x + 6, card_rect.top + 58))
        else:
            surface.blit(self.font_tiny.render("• Primario: (Ranura vacía)", True, (130, 135, 145)), (right_x + 6, card_rect.top + 58))

        # Hechizo Secundario
        m2 = player.secondary_magic
        if m2:
            col2 = ELEMENT_COLORS.get(m2, COLOR_GOLD)
            m2_txt = f"• Secundario [Tecla Q]: {m2}"
            surface.blit(self.font_tiny.render(m2_txt, True, col2), (right_x + 6, card_rect.top + 78))
        else:
            surface.blit(self.font_tiny.render("• Secundario: (Ranura vacía)", True, (130, 135, 145)), (right_x + 6, card_rect.top + 78))

        # Dash
        surface.blit(self.font_tiny.render("• Movilidad [Espacio]: Esquiva con i-frames", True, (46, 204, 113)), (right_x + 6, card_rect.top + 100))

        # Audio status rápido
        if audio_mgr:
            status_txt = f"🔊 Audio: {audio_mgr.get_status_tag()}   (Ajusta con [3], [+] o [-])"
            surface.blit(self.font_tiny.render(status_txt, True, COLOR_STEAM), (card_rect.left + 16, card_rect.bottom - 22))

        # 2. BOTONES INTERACTIVOS DE PAUSA
        btn_rects = self._get_main_button_rects()
        for i, b_data in enumerate(self.buttons_main):
            r = btn_rects[i]
            is_hover = r.collidepoint(mouse_pos)
            is_selected = (self.selected_index == i)

            # Sonido de hover
            if is_hover and self.hovered_btn != b_data["id"]:
                self.hovered_btn = b_data["id"]
                self.selected_index = i
                if self.audio_system:
                    self.audio_system.play_sfx("ui_hover")

            # Estilo del botón
            if is_hover or is_selected:
                bg_col = (45, 38, 22) if b_data["id"] != "MAIN_MENU" else (48, 22, 22)
                border_col = COLOR_GOLD if b_data["id"] != "MAIN_MENU" else (231, 76, 60)
                text_col = COLOR_WHITE
                # Resplandor suave
                glow_r = r.inflate(4, 4)
                pygame.draw.rect(surface, border_col, glow_r, 1, border_radius=7)
            else:
                bg_col = (24, 27, 34)
                border_col = COLOR_BRASS
                text_col = (200, 205, 215)

            pygame.draw.rect(surface, bg_col, r, border_radius=6)
            pygame.draw.rect(surface, border_col, r, 2, border_radius=6)

            # Etiqueta del botón
            txt_surf = self.font_mid.render(b_data["label"], True, text_col)
            surface.blit(txt_surf, txt_surf.get_rect(center=r.center))

    def _draw_controls_view(self, surface: pygame.Surface, mouse_pos):
        """Dibuja la vista modal interna con la guía rápida de controles."""
        card_rect = pygame.Rect(self.modal_x + 30, self.modal_y + 82, self.modal_w - 60, 400)
        pygame.draw.rect(surface, (14, 17, 23), card_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_BRASS, card_rect, 1, border_radius=6)

        surface.blit(self.font_mid.render("📜 GUÍA RÁPIDA DE CONTROLES Y COMBATE", True, COLOR_GOLD), (card_rect.left + 20, card_rect.top + 14))

        controls_list = [
            ("Movimiento del Héroe:", "[W] [A] [S] [D]  o  Flechas direccionales en 8 vías"),
            ("Ataque Principal:", "[Clic Izquierdo]  Arma medieval / Dardo Arcano"),
            ("Hechizo Primario:", "[Clic Derecho]  o  Tecla [E] (Consume Maná)"),
            ("Hechizo Secundario:", "Tecla [Q] (Consume Maná)"),
            ("Esquiva Táctica (Dash):", "Barra [Espacio] (Invulnerabilidad i-frames)"),
            ("Disparo Mago (Infinito):", "Tecla [V]  Proyectil de Éter (+15 MP al impactar)"),
            ("Pausar / Reanudar:", "Tecla [ESC]  o  Tecla [P]"),
            ("Silenciar Audio:", "Tecla [M]  Silenciar / Reactivar música y efectos"),
            ("Volumen Maestro:", "Teclas [+] y [-]  Ajustar volumen paso a paso"),
            ("Regla de Maná:", "Reserva de 500 MP. Golpear enemigos restaura +10 a +75 MP")
        ]

        start_y = card_rect.top + 45
        for i, (action, keys) in enumerate(controls_list):
            ay = start_y + i * 29
            # Acción
            surface.blit(self.font_small.render(action, True, (220, 225, 235)), (card_rect.left + 24, ay))
            # Tecla / Atajo
            surface.blit(self.font_small.render(keys, True, COLOR_GOLD), (card_rect.left + 230, ay))

        # Botón Volver
        back_rect = pygame.Rect(self.modal_x + self.modal_w // 2 - 120, self.modal_y + self.modal_h - 55, 240, 38)
        is_hover = back_rect.collidepoint(mouse_pos)
        bg_col = (45, 38, 22) if is_hover else (24, 27, 34)
        border_col = COLOR_GOLD if is_hover else COLOR_BRASS

        pygame.draw.rect(surface, bg_col, back_rect, border_radius=6)
        pygame.draw.rect(surface, border_col, back_rect, 2, border_radius=6)
        txt = self.font_mid.render("⬅ VOLVER A PAUSA", True, COLOR_WHITE if is_hover else (200, 205, 215))
        surface.blit(txt, txt.get_rect(center=back_rect.center))

    def _draw_corner_cog(self, surface: pygame.Surface, cx: int, cy: int, radius: float, angle: float):
        """Dibuja un engranaje giratorio decorativo en latón pulido."""
        teeth = 6
        pts = []
        for k in range(teeth):
            ang = angle + (2 * math.pi / teeth) * k
            pts.append((cx + int(math.cos(ang) * (radius + 3)), cy + int(math.sin(ang) * (radius + 3))))
            mid_ang = ang + (math.pi / teeth)
            pts.append((cx + int(math.cos(mid_ang) * (radius - 1)), cy + int(math.sin(mid_ang) * (radius - 1))))
        pygame.draw.polygon(surface, COLOR_BRASS, pts)
        pygame.draw.circle(surface, (140, 100, 20), (cx, cy), int(radius * 0.45))
        pygame.draw.circle(surface, COLOR_GOLD, (cx, cy), int(radius * 0.25))
