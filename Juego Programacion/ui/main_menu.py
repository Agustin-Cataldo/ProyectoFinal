"""
================================================================================
MÓDULO: ui/main_menu.py
RESPONSABILIDAD: Menú Principal interactivo, responsivo y temático Steampunk/Medieval.
CONCEPTO ACADÉMICO: Patrón State para navegación UI, Polimorfismo de vistas modales
                    y Feedback visual inmediato por teclado y ratón.
================================================================================
Ofrece:
1. Vista Principal con 5 botones navegables (Ratón y Teclado [1]-[5], W/S o Flechas):
   - JUGAR / SELECCIÓN DE PERSONAJE
   - MANUAL & CONTROLES
   - CÓDICE DE PERSONAJES (6 Clases y 300 Cartas)
   - CRÉDITOS ACADÉMICOS
   - SALIR DEL JUEGO
2. Vistas Modales integradas:
   - CONTROLES: Guía completa de atajos de teclado, ratón, maná y mecánicas.
   - CÓDICE: Explorador interactivo de los 6 Personajes con sus armas, pasivas y barajas.
   - CRÉDITOS: Ficha académica oficial de Agustín Cataldo y especificaciones del motor.
3. Efectos visuales de partículas ambientales (ascuas de latón y vapor flotante).
"""

import math
import random
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BLACK, COLOR_BRASS, COLOR_COPPER,
    COLOR_DARK_STONE, COLOR_GOLD, COLOR_WHITE, COLOR_STEAM, COLOR_RED_HEALTH,
    COLOR_MANA, ELEMENT_COLORS
)


class MenuParticle:
    """Partícula decorativa de vapor o ascua para el fondo del menú principal."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.reset(random_y=True)

    def reset(self, random_y: bool = False):
        self.x = random.uniform(20, self.width - 20)
        self.y = random.uniform(50, self.height - 20) if random_y else self.height + random.uniform(5, 30)
        self.vx = random.uniform(-15.0, 15.0)
        self.vy = random.uniform(-40.0, -18.0)
        self.size = random.uniform(1.5, 3.5)
        self.max_life = random.uniform(3.5, 6.5)
        self.life = random.uniform(0.1, self.max_life) if random_y else self.max_life
        # Tipos: 0 = ascua dorada, 1 = brasa de latón, 2 = vapor frío
        p_type = random.random()
        if p_type < 0.50:
            self.base_color = (241, 196, 15)   # Oro
        elif p_type < 0.80:
            self.base_color = (212, 160, 23)   # Latón
        else:
            self.base_color = (180, 210, 230)  # Vapor

    def update(self, dt: float):
        self.life -= dt
        if self.life <= 0:
            self.reset(random_y=False)
            return

        self.x += self.vx * dt + math.sin(self.life * 2.5) * 0.4
        self.y += self.vy * dt

    def draw(self, surface: pygame.Surface):
        alpha_ratio = min(1.0, max(0.0, self.life / self.max_life))
        alpha = int(alpha_ratio * 160)
        if alpha <= 0:
            return

        p_surf = pygame.Surface((int(self.size * 2) + 2, int(self.size * 2) + 2), pygame.SRCALPHA)
        color = (*self.base_color, alpha)
        pygame.draw.circle(p_surf, color, (p_surf.get_width() // 2, p_surf.get_height() // 2), int(self.size))
        surface.blit(p_surf, (self.x - self.size, self.y - self.size))


class MainMenu:
    """Menú Principal completo con navegación modal, accesibilidad y estética Steampunk."""

    VIEW_MAIN = "MAIN"
    VIEW_CONTROLS = "CONTROLS"
    VIEW_CODEX = "CODEX"
    VIEW_CREDITS = "CREDITS"

    def __init__(self, audio_system=None):
        self.audio_system = audio_system
        # Tipografías retro nativas escaladas
        self.font_title_main = pygame.font.SysFont("Consolas", 42, bold=True)
        self.font_title_sub = pygame.font.SysFont("Consolas", 22, bold=True)
        self.font_badge = pygame.font.SysFont("Consolas", 13, bold=True)
        self.font_btn = pygame.font.SysFont("Consolas", 18, bold=True)
        self.font_btn_badge = pygame.font.SysFont("Consolas", 13, bold=True)
        self.font_heading = pygame.font.SysFont("Consolas", 22, bold=True)
        self.font_body = pygame.font.SysFont("Consolas", 14)
        self.font_body_bold = pygame.font.SysFont("Consolas", 14, bold=True)
        self.font_footer = pygame.font.SysFont("Consolas", 12)
        self.font_tiny = pygame.font.SysFont("Consolas", 11, bold=True)

        self.current_view = self.VIEW_MAIN
        self.selected_btn_index = 0
        self.anim_timer = 0.0

        # Partículas ambientales
        self.particles = [MenuParticle(SCREEN_WIDTH, SCREEN_HEIGHT) for _ in range(45)]

        # Configuración de los 5 botones del menú principal
        self.buttons = [
            {"id": "PLAY",     "hotkey": "[1]", "label": "⚔️  JUGAR / NUEVA PARTIDA",        "desc": "Inicia la odisea y elige tu Personaje con su baraja exclusiva de 50 cartas."},
            {"id": "CONTROLS", "hotkey": "[2]", "label": "📖  CÓMO JUGAR & CONTROLES",       "desc": "Guía completa de controles [WASD, Clics, Espacio] y mecánicas de combate."},
            {"id": "CODEX",    "hotkey": "[3]", "label": "🃏  CÓDICE DE PERSONAJES (12)",     "desc": "Consulta las estadísticas, armas insignia y barajas de los 12 héroes."},
            {"id": "CREDITS",  "hotkey": "[4]", "label": "📜  CRÉDITOS & PROYECTO",          "desc": "Ficha técnica, especificaciones del motor y créditos del juego."},
            {"id": "QUIT",     "hotkey": "[5]", "label": "🚪  SALIR AL ESCRITORIO",          "desc": "Cierra la aplicación limpiamente."}
        ]

        self.btn_rects = []
        self._calculate_button_rects()

        # Índice de personaje seleccionado en el Códice (0 a 5)
        self.codex_char_index = 0

    def _calculate_button_rects(self):
        """Calcula las cajas de colisión centradas para los botones."""
        self.btn_rects.clear()
        btn_w = 540
        btn_h = 52
        gap = 14
        start_y = 270
        c_x = SCREEN_WIDTH // 2 - btn_w // 2

        for i in range(len(self.buttons)):
            y = start_y + i * (btn_h + gap)
            self.btn_rects.append(pygame.Rect(c_x, y, btn_w, btn_h))

    def update(self, dt: float):
        """Actualiza animaciones, partículas y parpadeo de interfaces."""
        self.anim_timer += dt
        for p in self.particles:
            p.update(dt)

    def handle_event(self, event: pygame.event.Event) -> str:
        """
        Procesa eventos de ratón y teclado.
        Retorna 'PLAY' para iniciar selección de personaje, 'QUIT' para salir, o None.
        """
        mouse_pos = getattr(event, 'pos', pygame.mouse.get_pos())

        # -------------------------------------------------------------
        # 1. EVENTOS EN LA VISTA PRINCIPAL
        # -------------------------------------------------------------
        if self.current_view == self.VIEW_MAIN:
            # Movimiento del ratón
            if event.type == pygame.MOUSEMOTION:
                prev_idx = self.selected_btn_index
                for idx, rect in enumerate(self.btn_rects):
                    if rect.collidepoint(mouse_pos):
                        self.selected_btn_index = idx
                        if self.selected_btn_index != prev_idx and self.audio_system:
                            self.audio_system.play_sfx("ui_hover")
                        break

            # Clic izquierdo
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for idx, rect in enumerate(self.btn_rects):
                    if rect.collidepoint(mouse_pos):
                        if self.audio_system:
                            self.audio_system.play_sfx("ui_select")
                        return self._activate_button(idx)

            # Entrada por teclado
            elif event.type == pygame.KEYDOWN:
                # Navegación vertical
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected_btn_index = (self.selected_btn_index - 1) % len(self.buttons)
                    if self.audio_system:
                        self.audio_system.play_sfx("ui_hover")
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected_btn_index = (self.selected_btn_index + 1) % len(self.buttons)
                    if self.audio_system:
                        self.audio_system.play_sfx("ui_hover")

                # Confirmación
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                    if self.audio_system:
                        self.audio_system.play_sfx("ui_select")
                    return self._activate_button(self.selected_btn_index)

                # Atajos numéricos directos [1] al [5]
                elif event.key == pygame.K_1 or event.key == pygame.K_KP1:
                    if self.audio_system:
                        self.audio_system.play_sfx("ui_select")
                    return self._activate_button(0)
                elif event.key == pygame.K_2 or event.key == pygame.K_KP2:
                    if self.audio_system:
                        self.audio_system.play_sfx("ui_select")
                    return self._activate_button(1)
                elif event.key == pygame.K_3 or event.key == pygame.K_KP3:
                    if self.audio_system:
                        self.audio_system.play_sfx("ui_select")
                    return self._activate_button(2)
                elif event.key == pygame.K_4 or event.key == pygame.K_KP4:
                    if self.audio_system:
                        self.audio_system.play_sfx("ui_select")
                    return self._activate_button(3)
                elif event.key == pygame.K_5 or event.key == pygame.K_KP5:
                    if self.audio_system:
                        self.audio_system.play_sfx("ui_select")
                    return self._activate_button(4)

                # Escape para salir
                elif event.key == pygame.K_ESCAPE:
                    if self.audio_system:
                        self.audio_system.play_sfx("ui_select")
                    return "QUIT"

        # -------------------------------------------------------------
        # 2. EVENTOS EN VISTAS MODALES (CONTROLES, CÓDICE, CRÉDITOS)
        # -------------------------------------------------------------
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.audio_system:
                        self.audio_system.play_sfx("ui_select")
                    self.current_view = self.VIEW_MAIN
                elif self.current_view == self.VIEW_CODEX:
                    # Cambiar entre personajes con flechas o números [1]-[9]
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        self.codex_char_index = (self.codex_char_index - 1) % 12
                        if self.audio_system:
                            self.audio_system.play_sfx("ui_hover")
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.codex_char_index = (self.codex_char_index + 1) % 12
                        if self.audio_system:
                            self.audio_system.play_sfx("ui_hover")
                    elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6):
                        self.codex_char_index = event.key - pygame.K_1
                        if self.audio_system:
                            self.audio_system.play_sfx("ui_hover")

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Botón de retorno al menú
                back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT - 75, 320, 42)
                if back_rect.collidepoint(mouse_pos):
                    if self.audio_system:
                        self.audio_system.play_sfx("ui_select")
                    self.current_view = self.VIEW_MAIN
                    return None

                # Si está en códice, comprobar 12 pestañas de personaje (2 filas de 6)
                if self.current_view == self.VIEW_CODEX:
                    tab_w = 170
                    tab_h = 28
                    start_tab_x = (SCREEN_WIDTH - (6 * tab_w + 5 * 8)) // 2
                    modal_top = (SCREEN_HEIGHT - 600) // 2 - 10
                    for c_idx in range(12):
                        row = c_idx // 6
                        col = c_idx % 6
                        tx = start_tab_x + col * (tab_w + 8)
                        ty = modal_top + 55 + row * (tab_h + 5)
                        t_rect = pygame.Rect(tx, ty, tab_w, tab_h)
                        if t_rect.collidepoint(mouse_pos):
                            if self.codex_char_index != c_idx and self.audio_system:
                                self.audio_system.play_sfx("ui_hover")
                            self.codex_char_index = c_idx
                            break

        return None

    def _activate_button(self, index: int) -> str:
        """Ejecuta la acción asignada al botón."""
        btn_id = self.buttons[index]["id"]
        if btn_id == "PLAY":
            return "PLAY"
        elif btn_id == "CONTROLS":
            self.current_view = self.VIEW_CONTROLS
        elif btn_id == "CODEX":
            self.current_view = self.VIEW_CODEX
        elif btn_id == "CREDITS":
            self.current_view = self.VIEW_CREDITS
        elif btn_id == "QUIT":
            return "QUIT"
        return None

    # =========================================================================
    # RENDERIZADO GENERAL
    # =========================================================================

    def draw(self, surface: pygame.Surface):
        """Renderiza la vista correspondiente según el estado interno del menú."""
        # 1. Fondo oscuro medieval con viñeta
        surface.fill(COLOR_BLACK)
        self._draw_background_effects(surface)

        # 2. Renderizado según la vista activa
        if self.current_view == self.VIEW_MAIN:
            self._draw_main_view(surface)
        elif self.current_view == self.VIEW_CONTROLS:
            self._draw_controls_view(surface)
        elif self.current_view == self.VIEW_CODEX:
            self._draw_codex_view(surface)
        elif self.current_view == self.VIEW_CREDITS:
            self._draw_credits_view(surface)

    def _draw_background_effects(self, surface: pygame.Surface):
        """Dibuja el fondo de piedra, ascuas flotantes y marco gótico."""
        # Círculo rúnico decorativo giratorio en el fondo
        c_x, c_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        faint_rune = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pulse = 0.5 + 0.5 * math.sin(self.anim_timer * 1.5)
        rune_alpha = int(25 + 20 * pulse)
        pygame.draw.circle(faint_rune, (212, 160, 23, rune_alpha), (c_x, c_y), 320, 2)
        pygame.draw.circle(faint_rune, (184, 115, 51, rune_alpha), (c_x, c_y), 240, 1)
        pygame.draw.circle(faint_rune, (212, 160, 23, rune_alpha), (c_x, c_y), 160, 1)

        # Rayos y hendiduras rúnicas
        for i in range(8):
            angle = i * (math.pi / 4) + self.anim_timer * 0.1
            x1 = c_x + math.cos(angle) * 160
            y1 = c_y + math.sin(angle) * 160
            x2 = c_x + math.cos(angle) * 320
            y2 = c_y + math.sin(angle) * 320
            pygame.draw.line(faint_rune, (212, 160, 23, rune_alpha // 2), (x1, y1), (x2, y2), 1)

        surface.blit(faint_rune, (0, 0))

        # Dibujar partículas de vapor y brasas
        for p in self.particles:
            p.draw(surface)

        # Marco exterior gótico con remaches
        pygame.draw.rect(surface, COLOR_BRASS, (12, 12, SCREEN_WIDTH - 24, SCREEN_HEIGHT - 24), 2)
        pygame.draw.rect(surface, (45, 48, 56), (16, 16, SCREEN_WIDTH - 32, SCREEN_HEIGHT - 32), 1)

        # Remaches en las esquinas
        rivets = [
            (24, 24), (SCREEN_WIDTH - 24, 24),
            (24, SCREEN_HEIGHT - 24), (SCREEN_WIDTH - 24, SCREEN_HEIGHT - 24)
        ]
        for rx, ry in rivets:
            pygame.draw.circle(surface, COLOR_GOLD, (rx, ry), 5)
            pygame.draw.circle(surface, COLOR_DARK_STONE, (rx, ry), 3)

    # =========================================================================
    # VISTA 1: MENÚ PRINCIPAL
    # =========================================================================

    def _draw_main_view(self, surface: pygame.Surface):
        """Renderiza el banner de título y la botonera interactiva."""
        c_x = SCREEN_WIDTH // 2

        # -------------------------------------------------------------
        # BANNER DE TÍTULO STEAMPUNK
        # -------------------------------------------------------------
        # Sombra de título
        t_shadow = self.font_title_main.render("STEAM & BLADE: ELEMENTAL ODYSSEY", True, (15, 12, 8))
        surface.blit(t_shadow, t_shadow.get_rect(center=(c_x + 3, 103)))

        # Título principal en latón y oro
        t_main = self.font_title_main.render("STEAM & BLADE: ELEMENTAL ODYSSEY", True, COLOR_BRASS)
        surface.blit(t_main, t_main.get_rect(center=(c_x, 100)))

        # Subtítulo de género y ambientación
        sub_text = "HACK & SLASH ROGUELIKE · DARK STEAMPUNK ODYSSEY"
        sub_surf = self.font_title_sub.render(sub_text, True, COLOR_STEAM)
        surface.blit(sub_surf, sub_surf.get_rect(center=(c_x, 148)))

        # Insignia de características clave
        badge_text = "✦ 12 PERSONAJES LEGENDARIOS · 600 CARTAS ÚNICAS · 10 JEFES ELEMENTALES · 50 SALAS ✦"
        badge_surf = self.font_badge.render(badge_text, True, COLOR_GOLD)
        badge_rect = badge_surf.get_rect(center=(c_x, 185))
        # Fondo de la insignia
        bg_rect = badge_rect.inflate(30, 10)
        pygame.draw.rect(surface, (25, 27, 34), bg_rect, border_radius=4)
        pygame.draw.rect(surface, COLOR_COPPER, bg_rect, 1, border_radius=4)
        surface.blit(badge_surf, badge_rect)

        # -------------------------------------------------------------
        # BOTONES DEL MENÚ PRINCIPAL
        # -------------------------------------------------------------
        pulse = 0.5 + 0.5 * math.sin(self.anim_timer * 6.0)

        for idx, btn in enumerate(self.buttons):
            rect = self.btn_rects[idx]
            is_hovered = (idx == self.selected_btn_index)

            # Colores dinámicos
            if is_hovered:
                bg_color = (45, 48, 62)
                border_color = COLOR_GOLD
                border_w = 2
                text_color = COLOR_GOLD
                # Resplandor sutil
                glow_rect = rect.inflate(8, 6)
                pygame.draw.rect(surface, (80, 65, 20), glow_rect, border_radius=8)
            else:
                bg_color = (24, 26, 32)
                border_color = COLOR_COPPER
                border_w = 1
                text_color = COLOR_WHITE

            # Cuerpo del botón
            pygame.draw.rect(surface, bg_color, rect, border_radius=6)
            pygame.draw.rect(surface, border_color, rect, border_w, border_radius=6)

            # Remache decorativo lateral
            dot_color = COLOR_GOLD if is_hovered else COLOR_BRASS
            pygame.draw.circle(surface, dot_color, (rect.left + 16, rect.centery), 4)
            pygame.draw.circle(surface, dot_color, (rect.right - 16, rect.centery), 4)

            # Placa de Hotkey a la izquierda [1]
            badge_surf = self.font_btn_badge.render(btn["hotkey"], True, COLOR_STEAM if not is_hovered else COLOR_GOLD)
            surface.blit(badge_surf, (rect.left + 30, rect.centery - badge_surf.get_height() // 2))

            # Texto del botón
            label_str = btn["label"]
            if is_hovered:
                label_str = f"▶  {label_str}  ◀"
            label_surf = self.font_btn.render(label_str, True, text_color)
            label_rect = label_surf.get_rect(center=(rect.centerx, rect.centery))
            surface.blit(label_surf, label_rect)

        # -------------------------------------------------------------
        # PANEL INFERIOR DE DESCRIPCIÓN RÁPIDA
        # -------------------------------------------------------------
        active_btn = self.buttons[self.selected_btn_index]
        desc_text = f"INFO: {active_btn['desc']}"
        desc_surf = self.font_body.render(desc_text, True, COLOR_STEAM)
        surface.blit(desc_surf, desc_surf.get_rect(center=(c_x, SCREEN_HEIGHT - 85)))

        # Indicador de atajos de navegación
        nav_info = "Navegación: [W/S] o [Flechas Arriba/Abajo] para elegir | [Enter/Espacio] confirmar | [1-5] acceso rápido"
        nav_surf = self.font_footer.render(nav_info, True, (130, 140, 155))
        surface.blit(nav_surf, nav_surf.get_rect(center=(c_x, SCREEN_HEIGHT - 55)))

    # =========================================================================
    # VISTA 2: MANUAL Y CONTROLES
    # =========================================================================

    def _draw_controls_view(self, surface: pygame.Surface):
        """Renderiza la ventana modal de Controles y Mecánicas del juego."""
        c_x = SCREEN_WIDTH // 2
        modal_w, modal_h = 1060, 560
        modal_rect = pygame.Rect(c_x - modal_w // 2, (SCREEN_HEIGHT - modal_h) // 2 - 15, modal_w, modal_h)

        # Fondo del modal con borde de latón
        pygame.draw.rect(surface, (18, 20, 26), modal_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_GOLD, modal_rect, 2, border_radius=8)

        # Título del manual
        title = self.font_heading.render("⚔️ GUÍA DE COMBATE, CONTROLES Y ARSENAL STEAMPUNK ⚔️", True, COLOR_GOLD)
        surface.blit(title, title.get_rect(center=(c_x, modal_rect.top + 35)))

        col_w = (modal_w - 70) // 2
        col1_x = modal_rect.left + 30
        col2_x = col1_x + col_w + 20
        start_y = modal_rect.top + 75

        # --- COLUMNA 1: CONTROLES DIRECTOS ---
        pygame.draw.rect(surface, (28, 30, 40), (col1_x, start_y, col_w, 375), border_radius=6)
        pygame.draw.rect(surface, COLOR_BRASS, (col1_x, start_y, col_w, 375), 1, border_radius=6)

        c1_title = self.font_body_bold.render("--- CONTROLES DE COMBATE (TECLADO & RATÓN) ---", True, COLOR_GOLD)
        surface.blit(c1_title, (col1_x + 15, start_y + 15))

        controls_list = [
            ("Movimiento Omnidireccional:", "Teclas [W, A, S, D] o [Flechas] (60 FPS fluidos)."),
            ("Ataque Principal / Arma:",     "[Clic Izquierdo] apuntando con el ratón."),
            ("Armas por Personaje:",         "Hacha, Maza, Dagas, Dardo Arcano, Saetas, Guadaña."),
            ("Magia Primaria Activa:",       "[Clic Derecho] o [Tecla E] (Gasta maná de la barra)."),
            ("Magia Secundaria Activa:",     "[Tecla Q] (Permite alternar 2 elementos a la vez)."),
            ("Esquiva de Vapor (Dash):",     "[Barra Espaciadora] (Otorga i-frames invulnerables)."),
            ("Dardo Arcano del Mago:",       "[Clic Izq / V] Disparo gratuito de 0 MP que recarga."),
            ("Menú y Pausa:",                "[ESC] para volver o salir de las ventanas.")
        ]

        y_offset = start_y + 50
        for header, detail in controls_list:
            h_surf = self.font_body_bold.render(f"• {header}", True, COLOR_STEAM)
            surface.blit(h_surf, (col1_x + 15, y_offset))
            d_surf = self.font_body.render(f"   {detail}", True, COLOR_WHITE)
            surface.blit(d_surf, (col1_x + 15, y_offset + 18))
            y_offset += 40

        # --- COLUMNA 2: REGLAS ROGUELIKE Y PROGRESIÓN ---
        pygame.draw.rect(surface, (28, 30, 40), (col2_x, start_y, col_w, 375), border_radius=6)
        pygame.draw.rect(surface, COLOR_BRASS, (col2_x, start_y, col_w, 375), 1, border_radius=6)

        c2_title = self.font_body_bold.render("--- MECÁNICAS ROGUELIKE Y SISTEMA DE CARTAS ---", True, COLOR_GOLD)
        surface.blit(c2_title, (col2_x + 15, start_y + 15))

        rules_list = [
            ("Vida & Maná Base:",           "1000 HP / 500 MP iniciales (modificados por personaje)."),
            ("Recuperación de Maná:",       "+10 MP por golpe cuerpo a cuerpo y +50-75 MP por baja."),
            ("Regeneración de Calma:",      "Tras 10s continuos sin recibir daño, curas +10 HP."),
            ("Mazmorras & Jefes:",          "5 Mazmorras de 10 salas (50 en total). Jefe en sala 10."),
            ("Combate Justo Telegrafiado:", "Los ataques de jefes tienen advertencias visuales de esquiva."),
            ("Cartas Slay the Spire 2:",    "Cada 3 niveles eliges 1 de 3 cartas únicas de tu baraja."),
            ("Barajas Especializadas:",     "Cada personaje posee 50 cartas de mejora exclusivas."),
            ("Magias de Luz y Oscuridad:",  "100% exclusivas de cartas Doradas / Raras.")
        ]

        y_offset = start_y + 50
        for header, detail in rules_list:
            h_surf = self.font_body_bold.render(f"• {header}", True, COLOR_GOLD)
            surface.blit(h_surf, (col2_x + 15, y_offset))
            d_surf = self.font_body.render(f"   {detail}", True, COLOR_WHITE)
            surface.blit(d_surf, (col2_x + 15, y_offset + 18))
            y_offset += 40

        # Botón de volver
        self._draw_back_button(surface)

    # =========================================================================
    # VISTA 3: CÓDICE DE PERSONAJES
    # =========================================================================

    def _draw_codex_view(self, surface: pygame.Surface):
        """Renderiza el compendio interactivo de los 12 Personajes y sus barajas de 50 cartas."""
        c_x = SCREEN_WIDTH // 2
        modal_w, modal_h = 1120, 600
        modal_rect = pygame.Rect(c_x - modal_w // 2, (SCREEN_HEIGHT - modal_h) // 2 - 10, modal_w, modal_h)

        pygame.draw.rect(surface, (18, 20, 26), modal_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_GOLD, modal_rect, 2, border_radius=8)

        title = self.font_heading.render("🃏 CÓDICE DE PERSONAJES & BARAJAS EXCLUSIVAS (SLAY THE SPIRE 2) 🃏", True, COLOR_GOLD)
        surface.blit(title, title.get_rect(center=(c_x, modal_rect.top + 28)))

        # Datos resumidos de los 12 personajes para el códice
        char_data = [
            {
                "id": "berserker", "name": "Berserker Bárbaro", "icon": "[🪓]", "color": (214, 48, 49),
                "hp": "1250 HP", "mp": "500 MP", "weapon": "Gran Hacha Bárbara (135° arco amplio)",
                "perks": "Robo de Vida: +5 HP por impacto acertado (+8 en crítico). Magia inicial: Fuego (Meteorito Ígneo).",
                "deck": "Baraja Roja de Furia: 50 Cartas Únicas (Sed de sangre, Hachas enloquecidas, Furia Ciega)."
            },
            {
                "id": "paladin", "name": "Paladín Templario", "icon": "[🛡️]", "color": (241, 196, 15),
                "hp": "1150 HP", "mp": "600 MP", "weapon": "Maza Sagrada de Guerra (Ondas doradas)",
                "perks": "Mitigación: 25% reducción de todo el daño. Regeneración: +14 HP/2s. Magia inicial: Luz Celestial.",
                "deck": "Baraja Dorada de la Fe: 50 Cartas Únicas (Escudo de Luz, Castigo Divino, Juicio Sagrado)."
            },
            {
                "id": "rogue", "name": "Pícaro Sombrío", "icon": "[🗡️]", "color": (46, 204, 113),
                "hp": "900 HP", "mp": "550 MP", "weapon": "Dagas Gemelas de Asesino (0.20s CD)",
                "perks": "Críticos Letales: 50% probabilidad de crítico (x2.2). +30% Velocidad. Magia inicial: Viento Ciclónico.",
                "deck": "Baraja Verde de Veneno: 50 Cartas Únicas (Hoja Envenenada, Danza Sombría, Golpe Fantasma)."
            },
            {
                "id": "mage", "name": "Mago Arcano", "icon": "[🔮]", "color": (155, 89, 182),
                "hp": "900 HP", "mp": "800 MP", "weapon": "Bastón Rúnico de Éter (Proyectil Arcano)",
                "perks": "Disparo Arcano 0 MP: genera +18 MP al impactar. +35% Daño Mágico. Magias iniciales: Fuego y Trueno.",
                "deck": "Baraja Azul Arcana: 50 Cartas Únicas (Sobrecarga de Maná, Éter Infinito, Agujero Negro)."
            },
            {
                "id": "hunter", "name": "Cazador Real", "icon": "[🏹]", "color": (230, 126, 34),
                "hp": "950 HP", "mp": "600 MP", "weapon": "Ballesta Pesada de Repetición",
                "perks": "Saetas Penetrantes: atraviesan 2 enemigos. +15% Velocidad. Magia inicial: Naturaleza (Zarzas).",
                "deck": "Baraja Naranja de Puntería: 50 Cartas Únicas (Saeta Caza-Dragones, Perforación, Ojo de Halcón)."
            },
            {
                "id": "necromancer", "name": "Nigromante Abisal", "icon": "[💀]", "color": (108, 92, 231),
                "hp": "850 HP", "mp": "750 MP", "weapon": "Guadaña Espectral de Almas (145° arco)",
                "perks": "Cosecha de Almas: +8 HP y +20 MP por cada enemigo eliminado. Magia de Oscuridad innata.",
                "deck": "Baraja Púrpura de Muerte: 50 Cartas Únicas (Pacto de Sangre, Segador Apocalíptico, Resurrección)."
            },
            {
                "id": "runeknight", "name": "Caballero Rúnico", "icon": "[⚔️]", "color": (52, 152, 219),
                "hp": "1200 HP", "mp": "650 MP", "weapon": "Espadón Rúnico Ancestral (Esquirlas de luz)",
                "perks": "Espadón Rúnico: Gran alcance y libera esquirlas cortantes de luz. 15% reducción de daño. Magia Metal.",
                "deck": "Baraja Rúnica de Acero: 50 Cartas Únicas (Filo Rúnico, Égida Radiante, Tajo Quebrantador)."
            },
            {
                "id": "alchemist", "name": "Alquimista de Plaga", "icon": "[⚗️]", "color": (46, 204, 113),
                "hp": "920 HP", "mp": "750 MP", "weapon": "Frascos Alquímicos Volátiles (Charcos)",
                "perks": "Frascos de Área: Charcos de ácido y fuego continuos. +10% velocidad y Magia Naturaleza.",
                "deck": "Baraja Alquímica de Miasma: 50 Cartas Únicas (Miasma Cáustico, Catalizador de Vapor, Fuego Alquímico)."
            },
            {
                "id": "monk", "name": "Monje Asceta", "icon": "[🥋]", "color": (241, 196, 15),
                "hp": "1050 HP", "mp": "650 MP", "weapon": "Guanteletes del Loto de Acero (0.18s CD)",
                "perks": "Ráfaga 0.18s y 40% críticos. Ondas sónicas y Magia de Trueno (Descarga de Ki).",
                "deck": "Baraja Marcial de Ki: 50 Cartas Únicas (Puño Relámpago, Palma Sónica, Vacío Interior)."
            },
            {
                "id": "artificer", "name": "Artificiero Steampunk", "icon": "[⚙️]", "color": (230, 126, 34),
                "hp": "1100 HP", "mp": "600 MP", "weapon": "Cañón Portátil de Vapor y Metralla",
                "perks": "Cañón de Vapor: Disparos explosivos con onda de choque y nubes de vapor. 18% blindaje.",
                "deck": "Baraja Mecánica de Fusión: 50 Cartas Únicas (Metralla Pesada, Presión de Caldera, Retroceso Brutal)."
            },
            {
                "id": "shaman", "name": "Chamán de las Bestias", "icon": "[🐺]", "color": (26, 188, 156),
                "hp": "1000 HP", "mp": "800 MP", "weapon": "Tótem Espiritual Primordial (120°)",
                "perks": "Sanación Primitiva: Sana +4 HP al impactar enemigos. 800 MP y 2 Magias (Tierra y Naturaleza).",
                "deck": "Baraja Espiritual Primordial: 50 Cartas Únicas (Espíritu de Lobo, Furia de Oso, Vínculo Telúrico)."
            },
            {
                "id": "inquisitor", "name": "Inquisidor de Sangre", "icon": "[⛓️]", "color": (192, 57, 43),
                "hp": "980 HP", "mp": "700 MP", "weapon": "Mangual de la Penitencia Carmesí (360°)",
                "perks": "Mangual en 360°: Barre a todos los enemigos circundantes con chispas de fuego sagrado.",
                "deck": "Baraja Sagrada de Penitencia: 50 Cartas Únicas (Flagelo Ígneo, Sangre de Mártir, Juicio Férreo)."
            }
        ]

        # -------------------------------------------------------------
        # PESTAÑAS SUPERIORES PARA LOS 12 PERSONAJES (2 FILAS DE 6)
        # -------------------------------------------------------------
        tab_w = 170
        tab_h = 28
        start_tab_x = (SCREEN_WIDTH - (6 * tab_w + 5 * 8)) // 2

        for i, c in enumerate(char_data):
            row = i // 6
            col = i % 6
            tx = start_tab_x + col * (tab_w + 8)
            ty = modal_rect.top + 55 + row * (tab_h + 5)
            t_rect = pygame.Rect(tx, ty, tab_w, tab_h)
            is_active = (i == self.codex_char_index)

            t_bg = (40, 44, 58) if is_active else (24, 26, 32)
            t_border = c["color"] if is_active else COLOR_DARK_STONE
            pygame.draw.rect(surface, t_bg, t_rect, border_radius=4)
            pygame.draw.rect(surface, t_border, t_rect, 2 if is_active else 1, border_radius=4)

            tab_text = f"[{i + 1}] {c['name'].split()[0]}"
            t_surf = self.font_tiny.render(tab_text, True, c["color"] if is_active else COLOR_STEAM)
            surface.blit(t_surf, t_surf.get_rect(center=t_rect.center))

        # -------------------------------------------------------------
        # PANEL DETALLADO DEL PERSONAJE SELECCIONADO
        # -------------------------------------------------------------
        active = char_data[self.codex_char_index]
        detail_rect = pygame.Rect(modal_rect.left + 35, modal_rect.top + 128, modal_w - 70, 375)
        pygame.draw.rect(surface, (25, 27, 36), detail_rect, border_radius=6)
        pygame.draw.rect(surface, active["color"], detail_rect, 2, border_radius=6)

        # Encabezado del personaje
        name_surf = self.font_heading.render(f"{active['icon']}  {active['name'].upper()}", True, active["color"])
        surface.blit(name_surf, (detail_rect.left + 25, detail_rect.top + 16))

        # Cuadrícula de estadísticas
        stats_y = detail_rect.top + 55
        stat_boxes = [
            ("Constitución Máxima:", active["hp"], COLOR_RED_HEALTH),
            ("Reserva de Maná:",      active["mp"], COLOR_MANA),
            ("Arma Insignia:",         active["weapon"], COLOR_GOLD),
        ]

        b_x = detail_rect.left + 25
        for s_title, s_val, s_col in stat_boxes:
            box_r = pygame.Rect(b_x, stats_y, 320, 56)
            pygame.draw.rect(surface, (18, 20, 26), box_r, border_radius=4)
            pygame.draw.rect(surface, s_col, box_r, 1, border_radius=4)

            st_surf = self.font_body.render(s_title, True, COLOR_STEAM)
            surface.blit(st_surf, (box_r.left + 12, box_r.top + 6))
            sv_surf = self.font_body_bold.render(s_val, True, s_col)
            surface.blit(sv_surf, (box_r.left + 12, box_r.top + 28))
            b_x += 340

        # Bloque de Rasgos Tácticos y Pasivas
        perks_y = stats_y + 70
        pygame.draw.rect(surface, (20, 22, 28), (detail_rect.left + 25, perks_y, detail_rect.width - 50, 70), border_radius=4)
        pygame.draw.rect(surface, COLOR_BRASS, (detail_rect.left + 25, perks_y, detail_rect.width - 50, 70), 1, border_radius=4)

        p_title = self.font_body_bold.render("• IDENTIDAD TÁCTICA Y PASIVAS:", True, COLOR_GOLD)
        surface.blit(p_title, (detail_rect.left + 40, perks_y + 10))
        p_desc = self.font_body.render(active["perks"], True, COLOR_WHITE)
        surface.blit(p_desc, (detail_rect.left + 40, perks_y + 34))

        # Bloque de la Baraja de 50 Cartas
        deck_y = perks_y + 82
        pygame.draw.rect(surface, (20, 22, 28), (detail_rect.left + 25, deck_y, detail_rect.width - 50, 80), border_radius=4)
        pygame.draw.rect(surface, active["color"], (detail_rect.left + 25, deck_y, detail_rect.width - 50, 80), 1, border_radius=4)

        d_title = self.font_body_bold.render(f"• BARAJA ESPECIALIZADA: 50 CARTAS DE MEJORA ÚNICAS", True, active["color"])
        surface.blit(d_title, (detail_rect.left + 40, deck_y + 10))
        d_desc = self.font_body.render(active["deck"], True, COLOR_WHITE)
        surface.blit(d_desc, (detail_rect.left + 40, deck_y + 32))
        d_extra = self.font_body.render("Cada 3 niveles superados recibes 3 cartas aleatorias de este mazo (con probabilidad de dorada cada 5 rondas).", True, COLOR_STEAM)
        surface.blit(d_extra, (detail_rect.left + 40, deck_y + 54))

        # Navegación del códice
        info_nav = "Navegación: Presiona [1] a [6] o Flechas [Izquierda/Derecha] para cambiar de personaje (1 a 12)."
        in_surf = self.font_footer.render(info_nav, True, (130, 140, 155))
        surface.blit(in_surf, in_surf.get_rect(center=(c_x, modal_rect.bottom - 46)))

        self._draw_back_button(surface)

    # =========================================================================
    # VISTA 4: CRÉDITOS Y FICHA TÉCNICA
    # =========================================================================

    def _draw_credits_view(self, surface: pygame.Surface):
        """Renderiza la ficha académica oficial de Agustín Cataldo."""
        c_x = SCREEN_WIDTH // 2
        modal_w, modal_h = 960, 520
        modal_rect = pygame.Rect(c_x - modal_w // 2, (SCREEN_HEIGHT - modal_h) // 2 - 20, modal_w, modal_h)

        pygame.draw.rect(surface, (18, 20, 26), modal_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_GOLD, modal_rect, 2, border_radius=8)

        # Título
        title = self.font_heading.render("📜 CRÉDITOS & MEMORIA TÉCNICA DEL PROYECTO 📜", True, COLOR_GOLD)
        surface.blit(title, title.get_rect(center=(c_x, modal_rect.top + 35)))

        content_box = pygame.Rect(modal_rect.left + 35, modal_rect.top + 70, modal_w - 70, 360)
        pygame.draw.rect(surface, (25, 27, 36), content_box, border_radius=6)
        pygame.draw.rect(surface, COLOR_BRASS, content_box, 1, border_radius=6)

        credits_lines = [
            ("PROYECTO:",        "Steam & Blade: Elemental Odyssey"),
            ("AUTOR / DESARROLLADOR:", "Agustín Cataldo"),
            ("ÁMBITO ACADÉMICO:", "Proyecto Final de Asignatura / Ingeniería de Software en Videojuegos"),
            ("MOTOR Y TECNOLOGÍA:", "Python 3 + Pygame-ce 2.5.8 ejecutándose a 60 FPS estables"),
            ("PATRONES DE DISEÑO:", "Patrón State (Game Engine), Patrón Strategy (Roles y Cartas), Componentes UI"),
            ("CONTENIDO INTEGRADO:", "12 Personajes Legendarios con arsenal y armas distintivas."),
            ("",                   "600 Cartas de Mejora Únicas (50 cartas exclusivas por personaje)."),
            ("",                   "10 Jefes Elementales con mecánicas y ataques telegrafiados justos."),
            ("",                   "Regeneración de calma (+10 HP tras 10s sin daño) y escalado Roguelike (+4.5%/nivel)."),
            ("VERSIÓN DEL MOTOR:",  "Release Final - Octubre 2026")
        ]

        y_p = content_box.top + 20
        for label, val in credits_lines:
            if label:
                lbl_surf = self.font_body_bold.render(label, True, COLOR_GOLD)
                surface.blit(lbl_surf, (content_box.left + 25, y_p))
                val_surf = self.font_body.render(val, True, COLOR_WHITE)
                surface.blit(val_surf, (content_box.left + 230, y_p))
            else:
                val_surf = self.font_body.render(f"• {val}", True, COLOR_STEAM)
                surface.blit(val_surf, (content_box.left + 230, y_p))
            y_p += 28

        self._draw_back_button(surface)

    def _draw_back_button(self, surface: pygame.Surface):
        """Renderiza el botón común de volver al menú principal en las vistas modales."""
        c_x = SCREEN_WIDTH // 2
        back_rect = pygame.Rect(c_x - 160, SCREEN_HEIGHT - 75, 320, 42)
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = back_rect.collidepoint(mouse_pos)

        bg_col = (50, 45, 30) if is_hovered else (25, 27, 34)
        border_col = COLOR_GOLD if is_hovered else COLOR_COPPER

        pygame.draw.rect(surface, bg_col, back_rect, border_radius=6)
        pygame.draw.rect(surface, border_col, back_rect, 2 if is_hovered else 1, border_radius=6)

        text = "◀  [ESC] Volver al Menú Principal" if not is_hovered else "▶  [ESC] Volver al Menú Principal  ◀"
        b_surf = self.font_btn.render(text, True, COLOR_GOLD if is_hovered else COLOR_WHITE)
        surface.blit(b_surf, b_surf.get_rect(center=back_rect.center))
