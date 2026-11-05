"""
================================================================================
MÓDULO: ui/role_menu.py
RESPONSABILIDAD: Menú interactivo de Selección de Personaje estilo Slay the Spire 2
                 con soporte de pestañas, páginas, flechas y alta riqueza visual.
CONCEPTO ACADÉMICO: Interfaz Gráfica Modal Paginada y Feedback Visual Reactivo.
================================================================================
Presenta los 12 Personajes Legendarios organizados en 2 páginas de 6 héroes:
- Página 1: Héroes Clásicos (Berserker, Paladín, Pícaro, Mago, Cazador, Nigromante)
- Página 2: Maestros Arcanos (Caballero Rúnico, Alquimista, Monje, Artificiero, Chamán, Inquisidor)
Diseño visual limpio y moderno:
- Medallón y retrato Pixel Art de cada personaje.
- Relicario con sprite procedural del arma exclusiva.
- Barras de estadísticas tácticas (Salud, Ataque, Agilidad/Maná).
- Insignia de arquetipo y cinta con mecánica pasiva única sin sobrecarga de texto.
Navegación fluida mediante flechas laterales (◀ y ▶), pestañas superiores y teclado [A / D / Tab / 1-6].
"""

import math
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BRASS, COLOR_COPPER,
    COLOR_DARK_STONE, COLOR_GOLD, COLOR_WHITE, COLOR_STEAM
)
from systems.role_system import Role, RoleSystem
from utils.asset_loader import AssetLoader

# Ficha técnica visual y concisa para cada uno de los 12 héroes
ROLE_VISUAL_SPECS = {
    "berserker": {
        "archetype": "TANQUE BERSERKER",
        "weapon_name": "Gran Hacha Bárbara",
        "hp_val": "1250 HP", "hp_pct": 0.95,
        "dmg_val": "30 DMG", "dmg_pct": 0.85,
        "mob_val": "0.85x VEL", "mob_pct": 0.45,
        "mob_label": "AGI",
        "perk": "🩸 Robo de Sangre (+5 HP) & Magia de Fuego"
    },
    "paladin": {
        "archetype": "BALUARTE SAGRADO",
        "weapon_name": "Maza Sagrada de Guerra",
        "hp_val": "1150 HP", "hp_pct": 0.85,
        "dmg_val": "26 DMG", "dmg_pct": 0.72,
        "mob_val": "+14 HP/2s", "mob_pct": 0.70,
        "mob_label": "REG",
        "perk": "🛡️ 25% Mitigación & Magia de Luz Celestial"
    },
    "rogue": {
        "archetype": "ASESINO SOMBRÍO",
        "weapon_name": "Dagas Gemelas Venenosas",
        "hp_val": "900 HP", "hp_pct": 0.58,
        "dmg_val": "x2.2 CRIT", "dmg_pct": 0.90,
        "mob_val": "1.30x VEL", "mob_pct": 1.00,
        "mob_label": "AGI",
        "perk": "⚡ 50% Críticos (x2.2) & Magia de Viento"
    },
    "mage": {
        "archetype": "SEÑOR ARCANO",
        "weapon_name": "Bastón Rúnico de Éter",
        "hp_val": "900 HP", "hp_pct": 0.58,
        "dmg_val": "+35% MAG", "dmg_pct": 0.95,
        "mob_val": "800 MP", "mob_pct": 0.95,
        "mob_label": "MP",
        "perk": "🔮 Dardo Arcano (0 MP) & Magias Fuego y Trueno"
    },
    "hunter": {
        "archetype": "TIRADOR DE ÉLITE",
        "weapon_name": "Ballesta de Repetición",
        "hp_val": "950 HP", "hp_pct": 0.65,
        "dmg_val": "38 DMG", "dmg_pct": 0.88,
        "mob_val": "1.15x VEL", "mob_pct": 0.75,
        "mob_label": "AGI",
        "perk": "🏹 Saetas Perforantes & Magia de Naturaleza"
    },
    "necromancer": {
        "archetype": "SEÑOR DE ALMAS",
        "weapon_name": "Guadaña Espectral",
        "hp_val": "850 HP", "hp_pct": 0.50,
        "dmg_val": "28 DMG", "dmg_pct": 0.78,
        "mob_val": "750 MP", "mob_pct": 0.88,
        "mob_label": "MP",
        "perk": "💀 Cosecha de Almas & Magia de Oscuridad"
    },
    "runeknight": {
        "archetype": "CABALLERO RÚNICO",
        "weapon_name": "Espadón Ancestral",
        "hp_val": "1200 HP", "hp_pct": 0.90,
        "dmg_val": "32 DMG", "dmg_pct": 0.85,
        "mob_val": "15% ESC.", "mob_pct": 0.65,
        "mob_label": "ESC",
        "perk": "💎 Filo Rúnico & Magia de Metal Ancestral"
    },
    "alchemist": {
        "archetype": "PLAGA VOLÁTIL",
        "weapon_name": "Frascos Alquímicos",
        "hp_val": "920 HP", "hp_pct": 0.60,
        "dmg_val": "30 DMG (Área)", "dmg_pct": 0.80,
        "mob_val": "750 MP", "mob_pct": 0.85,
        "mob_label": "MP",
        "perk": "⚗️ Frascos Ácidos & Magia de Naturaleza"
    },
    "monk": {
        "archetype": "MAESTRO DE KI",
        "weapon_name": "Guanteletes de Loto",
        "hp_val": "1050 HP", "hp_pct": 0.75,
        "dmg_val": "0.18s CD", "dmg_pct": 0.92,
        "mob_val": "650 MP", "mob_pct": 0.75,
        "mob_label": "MP",
        "perk": "🥋 Ráfaga Sónica & Magia de Trueno"
    },
    "artificer": {
        "archetype": "INGENIERO VAPOR",
        "weapon_name": "Cañón de Metralla",
        "hp_val": "1100 HP", "hp_pct": 0.80,
        "dmg_val": "44 DMG (Expl)", "dmg_pct": 0.96,
        "mob_val": "600 MP", "mob_pct": 0.70,
        "mob_label": "MP",
        "perk": "⚙️ Metralla Explosiva & Magia de Vapor"
    },
    "shaman": {
        "archetype": "CHAMÁN BESTIAL",
        "weapon_name": "Tótem Primordial",
        "hp_val": "1000 HP", "hp_pct": 0.70,
        "dmg_val": "26 DMG", "dmg_pct": 0.72,
        "mob_val": "800 MP", "mob_pct": 0.95,
        "mob_label": "MP",
        "perk": "🐺 Tótem Sanador & Magia Tierra/Naturaleza"
    },
    "inquisitor": {
        "archetype": "VERDUGO CARMESÍ",
        "weapon_name": "Mangual Dentado",
        "hp_val": "980 HP", "hp_pct": 0.68,
        "dmg_val": "28 DMG (360°)", "dmg_pct": 0.82,
        "mob_val": "700 MP", "mob_pct": 0.80,
        "mob_label": "MP",
        "perk": "⛓️ Giro Penitente & Magia de Fuego"
    }
}


class RoleMenu:
    """Ventana interactiva de selección de Personaje inicial con diseño visual de alta fidelidad."""

    def __init__(self, role_system: RoleSystem, audio_system=None):
        self.role_system = role_system
        self.audio_system = audio_system
        self.font_title = pygame.font.SysFont("Consolas", 26, bold=True)
        self.font_sub = pygame.font.SysFont("Consolas", 13)
        self.font_tab = pygame.font.SysFont("Consolas", 13, bold=True)
        self.font_name = pygame.font.SysFont("Consolas", 14, bold=True)
        self.font_archetype = pygame.font.SysFont("Consolas", 10, bold=True)
        self.font_weapon = pygame.font.SysFont("Consolas", 11, bold=True)
        self.font_meter_lbl = pygame.font.SysFont("Consolas", 10, bold=True)
        self.font_meter_val = pygame.font.SysFont("Consolas", 10, bold=True)
        self.font_deck = pygame.font.SysFont("Consolas", 10, bold=True)
        self.font_perk = pygame.font.SysFont("Consolas", 11, bold=True)
        self.font_btn = pygame.font.SysFont("Consolas", 12, bold=True)
        self.font_desc = pygame.font.SysFont("Consolas", 11)
        self.font_stat = pygame.font.SysFont("Consolas", 11, bold=True)
        self.font_arrow = pygame.font.SysFont("Consolas", 32, bold=True)

        # Paginación
        self.current_page = 0
        self.page_size = 6
        self.total_pages = 2

        # Dimensiones para cuadrícula de 2 filas x 3 columnas (6 personajes por página)
        self.card_width = 370
        self.card_height = 252
        self.gap_x = 22
        self.gap_y = 16

        total_w = 3 * self.card_width + 2 * self.gap_x
        self.start_x = (SCREEN_WIDTH - total_w) // 2
        self.start_y = 125

        self.roles = []
        self.card_rects = []
        self.hovered_index = -1

        # Flechas laterales de navegación en los márgenes de la pantalla
        arrow_w, arrow_h = 44, 95
        arrow_y = SCREEN_HEIGHT // 2 - 40
        self.left_arrow_rect = pygame.Rect(14, arrow_y, arrow_w, arrow_h)
        self.right_arrow_rect = pygame.Rect(SCREEN_WIDTH - 14 - arrow_w, arrow_y, arrow_w, arrow_h)

        # Pestañas superiores interactivas
        tab_w, tab_h = 240, 28
        tab_y = 86
        self.tab1_rect = pygame.Rect(SCREEN_WIDTH // 2 - tab_w - 10, tab_y, tab_w, tab_h)
        self.tab2_rect = pygame.Rect(SCREEN_WIDTH // 2 + 10, tab_y, tab_w, tab_h)

        self.anim_timer = 0.0

    def set_roles(self, roles: list):
        """Asigna los personajes disponibles y calcula sus posiciones de renderizado."""
        self.roles = roles
        self.card_rects.clear()

        # Posicionamiento en 2 filas x 3 columnas para los 6 slots visibles
        for i in range(self.page_size):
            col = i % 3
            row = i // 3
            x = self.start_x + col * (self.card_width + self.gap_x)
            y = self.start_y + row * (self.card_height + self.gap_y)
            self.card_rects.append(pygame.Rect(x, y, self.card_width, self.card_height))

    def get_current_page_roles(self) -> list:
        """Retorna la lista de personajes de la página actual."""
        start = self.current_page * self.page_size
        end = start + self.page_size
        return self.roles[start:end]

    def prev_page(self):
        """Retrocede a la página anterior."""
        self.current_page = (self.current_page - 1) % self.total_pages
        if self.audio_system:
            self.audio_system.play_sfx("ui_hover")

    def next_page(self):
        """Avanza a la página siguiente."""
        self.current_page = (self.current_page + 1) % self.total_pages
        if self.audio_system:
            self.audio_system.play_sfx("ui_hover")

    def handle_event(self, event: pygame.event.Event):
        """
        Procesa la interacción del usuario:
        - Clic en flechas laterales ◀ / ▶
        - Clic en pestañas superiores
        - Teclas [A], [D], [Flechas], [Tab] para cambiar página
        - Clic o teclas [1] a [6] para elegir personaje
        """
        mouse_pos = getattr(event, 'pos', pygame.mouse.get_pos())

        if event.type == pygame.MOUSEMOTION:
            old_hover = self.hovered_index
            self.hovered_index = -1
            for idx, rect in enumerate(self.card_rects):
                if rect.collidepoint(mouse_pos):
                    self.hovered_index = idx
                    break
            if self.hovered_index != -1 and self.hovered_index != old_hover and self.audio_system:
                self.audio_system.play_sfx("ui_hover")

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 1. Flechas laterales
            if self.left_arrow_rect.collidepoint(mouse_pos):
                self.prev_page()
                return None
            if self.right_arrow_rect.collidepoint(mouse_pos):
                self.next_page()
                return None

            # 2. Pestañas superiores
            if self.tab1_rect.collidepoint(mouse_pos):
                if self.current_page != 0 and self.audio_system:
                    self.audio_system.play_sfx("ui_hover")
                self.current_page = 0
                return None
            if self.tab2_rect.collidepoint(mouse_pos):
                if self.current_page != 1 and self.audio_system:
                    self.audio_system.play_sfx("ui_hover")
                self.current_page = 1
                return None

            # 3. Botón de volver
            back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 45, 300, 32)
            if back_rect.collidepoint(mouse_pos):
                if self.audio_system:
                    self.audio_system.play_sfx("ui_select")
                return "BACK"

            # 4. Tarjetas de personaje
            page_roles = self.get_current_page_roles()
            for idx, rect in enumerate(self.card_rects):
                if rect.collidepoint(mouse_pos) and idx < len(page_roles):
                    if self.audio_system:
                        self.audio_system.play_sfx("ui_select")
                    return page_roles[idx]

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.audio_system:
                    self.audio_system.play_sfx("ui_select")
                return "BACK"

            # Cambio de página por teclado
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.prev_page()
                return None
            elif event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_TAB):
                self.next_page()
                return None

            # Selección numérica [1] a [6] en la página actual
            key_map = {
                pygame.K_1: 0,
                pygame.K_2: 1,
                pygame.K_3: 2,
                pygame.K_4: 3,
                pygame.K_5: 4,
                pygame.K_6: 5
            }
            if event.key in key_map:
                slot_idx = key_map[event.key]
                page_roles = self.get_current_page_roles()
                if slot_idx < len(page_roles):
                    if self.audio_system:
                        self.audio_system.play_sfx("ui_select")
                    return page_roles[slot_idx]

        return None

    def _draw_stat_meter(self, surface: pygame.Surface, x: int, y: int, label: str,
                         label_col: tuple, pct: float, fill_col: tuple, fill_hi_col: tuple,
                         val_text: str):
        """Renderiza una barra táctica de estadística con muescas y valor numérico."""
        # 1. Etiqueta
        lbl_surf = self.font_meter_lbl.render(label, True, label_col)
        surface.blit(lbl_surf, (x, y - 1))

        # 2. Marco y fondo de la barra
        bar_x = x + 28
        bar_w = 120
        bar_h = 9
        bar_rect = pygame.Rect(bar_x, y, bar_w, bar_h)
        pygame.draw.rect(surface, (16, 18, 24), bar_rect, border_radius=2)
        pygame.draw.rect(surface, (45, 48, 60), bar_rect, 1, border_radius=2)

        # 3. Relleno proporcional
        clamped_pct = max(0.08, min(1.0, pct))
        filled_w = max(4, int((bar_w - 2) * clamped_pct))
        fill_rect = pygame.Rect(bar_x + 1, y + 1, filled_w, bar_h - 2)
        pygame.draw.rect(surface, fill_col, fill_rect)
        # Línea de brillo superior
        pygame.draw.line(surface, fill_hi_col, (bar_x + 1, y + 1), (bar_x + filled_w - 1, y + 1), 1)

        # 4. Muescas tácticas divisorias (cada 24 px)
        for nx in range(bar_x + 24, bar_x + bar_w - 4, 24):
            pygame.draw.line(surface, (10, 12, 16), (nx, y), (nx, y + bar_h - 1), 1)

        # 5. Valor numérico a la derecha
        val_surf = self.font_meter_val.render(val_text, True, COLOR_WHITE)
        surface.blit(val_surf, (bar_x + bar_w + 6, y - 1))

    def draw(self, surface: pygame.Surface):
        """Renderiza el menú visual con pestañas, flechas laterales y las 6 tarjetas de personaje."""
        self.anim_timer += 0.03
        pulse = math.sin(self.anim_timer) * 3.0
        mouse_pos = pygame.mouse.get_pos()

        # 1. Capa de oscurecimiento de fondo
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 12, 16, 240))
        surface.blit(overlay, (0, 0))

        # 2. Título principal y subtítulo estilizado
        t1 = self.font_title.render("⚔️ SELECCIÓN DE HÉROE ⚔️", True, COLOR_GOLD)
        surface.blit(t1, t1.get_rect(center=(SCREEN_WIDTH // 2, 34)))

        sub_text = "Elige tu arquetipo de combate • Cada héroe posee su propia baraja exclusiva de 50 cartas únicas"
        t2 = self.font_sub.render(sub_text, True, COLOR_STEAM)
        surface.blit(t2, t2.get_rect(center=(SCREEN_WIDTH // 2, 62)))

        # 3. Pestañas de Navegación Superiores
        is_t1_hov = self.tab1_rect.collidepoint(mouse_pos)
        is_t2_hov = self.tab2_rect.collidepoint(mouse_pos)

        # Tab 1: Clásicos
        t1_col = COLOR_GOLD if (self.current_page == 0) else ((45, 50, 60) if not is_t1_hov else (70, 75, 88))
        t1_txt_col = COLOR_GOLD if (self.current_page == 0) else (COLOR_WHITE if is_t1_hov else COLOR_STEAM)
        pygame.draw.rect(surface, (20, 22, 28), self.tab1_rect, border_radius=5)
        pygame.draw.rect(surface, t1_col, self.tab1_rect, 2 if self.current_page == 0 else 1, border_radius=5)
        t1_lbl = self.font_tab.render("PÁG 1: HÉROES CLÁSICOS (1-6)", True, t1_txt_col)
        surface.blit(t1_lbl, t1_lbl.get_rect(center=self.tab1_rect.center))

        # Tab 2: Nuevos Maestros
        t2_col = COLOR_GOLD if (self.current_page == 1) else ((45, 50, 60) if not is_t2_hov else (70, 75, 88))
        t2_txt_col = COLOR_GOLD if (self.current_page == 1) else (COLOR_WHITE if is_t2_hov else COLOR_STEAM)
        pygame.draw.rect(surface, (20, 22, 28), self.tab2_rect, border_radius=5)
        pygame.draw.rect(surface, t2_col, self.tab2_rect, 2 if self.current_page == 1 else 1, border_radius=5)
        t2_lbl = self.font_tab.render("PÁG 2: NUEVOS MAESTROS (7-12)", True, t2_txt_col)
        surface.blit(t2_lbl, t2_lbl.get_rect(center=self.tab2_rect.center))

        # 4. Flechas Laterales de Navegación (Izquierda y Derecha)
        # Flecha Izquierda ◀
        is_left_hov = self.left_arrow_rect.collidepoint(mouse_pos)
        l_offset = int(pulse) if is_left_hov else 0
        l_draw_rect = self.left_arrow_rect.copy()
        l_draw_rect.x += l_offset
        pygame.draw.rect(surface, (30, 32, 40) if is_left_hov else (18, 20, 25), l_draw_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_GOLD if is_left_hov else (80, 85, 100), l_draw_rect, 2, border_radius=8)
        left_txt = self.font_arrow.render("◀", True, COLOR_GOLD if is_left_hov else COLOR_STEAM)
        surface.blit(left_txt, left_txt.get_rect(center=l_draw_rect.center))

        # Flecha Derecha ▶
        is_right_hov = self.right_arrow_rect.collidepoint(mouse_pos)
        r_offset = int(pulse) if is_right_hov else 0
        r_draw_rect = self.right_arrow_rect.copy()
        r_draw_rect.x -= r_offset
        pygame.draw.rect(surface, (30, 32, 40) if is_right_hov else (18, 20, 25), r_draw_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_GOLD if is_right_hov else (80, 85, 100), r_draw_rect, 2, border_radius=8)
        right_txt = self.font_arrow.render("▶", True, COLOR_GOLD if is_right_hov else COLOR_STEAM)
        surface.blit(right_txt, right_txt.get_rect(center=r_draw_rect.center))

        # 5. Dibujar las 6 tarjetas de personaje de la página activa
        page_roles = self.get_current_page_roles()
        for idx, role in enumerate(page_roles):
            if idx >= len(self.card_rects):
                break
            rect = self.card_rects[idx]
            is_hovered = (self.hovered_index == idx)

            draw_rect = rect.copy()
            if is_hovered:
                draw_rect.y -= 4

            role_spec = ROLE_VISUAL_SPECS.get(role.role_id, {
                "archetype": "AVENTURERO",
                "weapon_name": getattr(role, "weapon_name", "Espada Templada"),
                "hp_val": "1000 HP", "hp_pct": 0.70,
                "dmg_val": "25 DMG", "dmg_pct": 0.70,
                "mob_val": "1.00x VEL", "mob_pct": 0.70,
                "mob_label": "AGI",
                "perk": f"✔ {role.pros[0]}" if role.pros else "Héroe polivalente"
            })

            # Resplandor exterior en hover
            if is_hovered:
                glow_rect = draw_rect.inflate(8, 8)
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                glow_col = (min(255, role.color[0] // 3), min(255, role.color[1] // 3), min(255, role.color[2] // 3), 70)
                pygame.draw.rect(glow_surf, glow_col, (0, 0, glow_rect.width, glow_rect.height), border_radius=10)
                surface.blit(glow_surf, glow_rect.topleft)

            # Fondo de la tarjeta con relieve de piedra oscura
            pygame.draw.rect(surface, (20, 22, 28), draw_rect, border_radius=8)
            pygame.draw.rect(surface, (27, 29, 37), draw_rect.inflate(-4, -4), border_radius=6)

            # Marco temático o dorado brillante
            border_col = COLOR_GOLD if is_hovered else role.color
            pygame.draw.rect(surface, border_col, draw_rect, 3 if is_hovered else 2, border_radius=8)

            # A. Encabezado de la Tarjeta (x, y, w, 36)
            header_rect = pygame.Rect(draw_rect.x, draw_rect.y, draw_rect.width, 36)
            pygame.draw.rect(surface, (15, 17, 22), header_rect, border_top_left_radius=8, border_top_right_radius=8)
            pygame.draw.line(surface, (40, 44, 56), (header_rect.left, header_rect.bottom),
                             (header_rect.right, header_rect.bottom), 1)

            slot_num = idx + 1
            # Insignia numérica
            num_box = pygame.Rect(draw_rect.x + 8, draw_rect.y + 7, 24, 22)
            pygame.draw.rect(surface, (28, 30, 40), num_box, border_radius=4)
            pygame.draw.rect(surface, role.color, num_box, 1, border_radius=4)
            num_surf = self.font_name.render(str(slot_num), True, COLOR_GOLD)
            surface.blit(num_surf, num_surf.get_rect(center=num_box.center))

            # Nombre del Rol
            name_surf = self.font_name.render(role.name, True, role.color)
            surface.blit(name_surf, (draw_rect.x + 38, draw_rect.y + 10))

            # Píldora de Arquetipo a la derecha
            arch_text = role_spec["archetype"]
            arch_surf = self.font_archetype.render(arch_text, True, role.color)
            arch_w = arch_surf.get_width() + 14
            arch_box = pygame.Rect(draw_rect.right - arch_w - 8, draw_rect.y + 7, arch_w, 22)
            pygame.draw.rect(surface, (24, 26, 36), arch_box, border_radius=11)
            pygame.draw.rect(surface, role.color, arch_box, 1, border_radius=11)
            surface.blit(arch_surf, arch_surf.get_rect(center=arch_box.center))

            # B. Columna Izquierda: Vitrina Visual de Héroe y Arma
            showcase_rect = pygame.Rect(draw_rect.x + 10, draw_rect.y + 44, 88, 112)
            pygame.draw.rect(surface, (16, 18, 24), showcase_rect, border_radius=6)
            pygame.draw.rect(surface, (45, 50, 62), showcase_rect, 1, border_radius=6)

            # Retrato / Medallón del Personaje (72x72)
            portrait = AssetLoader.get_role_portrait(role.role_id, role.color, role.weapon_type, size=72)
            surface.blit(portrait, (showcase_rect.centerx - 36, showcase_rect.y + 4))

            # Relicario del Arma debajo del retrato
            weapon_box = pygame.Rect(showcase_rect.x + 6, showcase_rect.y + 80, showcase_rect.width - 12, 26)
            pygame.draw.rect(surface, (24, 26, 34), weapon_box, border_radius=4)
            pygame.draw.rect(surface, (60, 65, 80), weapon_box, 1, border_radius=4)

            raw_w_sprite = AssetLoader.get_weapon_sprite(role.weapon_type)
            w_w, w_h = raw_w_sprite.get_size()
            scale = min(70 / max(1, w_w), 20 / max(1, w_h), 1.0)
            scaled_w_sprite = pygame.transform.smoothscale(
                raw_w_sprite,
                (max(1, int(w_w * scale)), max(1, int(w_h * scale)))
            )
            surface.blit(scaled_w_sprite, scaled_w_sprite.get_rect(center=weapon_box.center))

            # C. Columna Derecha: Especificaciones y Barras Tácticas
            stats_x = draw_rect.x + 106
            stats_y = draw_rect.y + 44

            # Subtítulo del arma
            w_name_surf = self.font_weapon.render(f"⚔️ {role_spec['weapon_name']}", True, (225, 200, 130))
            surface.blit(w_name_surf, (stats_x + 2, stats_y + 2))

            # Barra 1: Salud (HP)
            self._draw_stat_meter(
                surface, stats_x + 2, stats_y + 24, "HP",
                (231, 76, 60), role_spec["hp_pct"],
                (214, 48, 49), (255, 120, 120), role_spec["hp_val"]
            )

            # Barra 2: Ataque (ATQ)
            self._draw_stat_meter(
                surface, stats_x + 2, stats_y + 45, "ATQ",
                (243, 156, 18), role_spec["dmg_pct"],
                (230, 126, 34), (255, 205, 80), role_spec["dmg_val"]
            )

            # Barra 3: Agilidad o Maná (AGI / MP / REG)
            self._draw_stat_meter(
                surface, stats_x + 2, stats_y + 66, role_spec["mob_label"],
                (52, 152, 219), role_spec["mob_pct"],
                (41, 128, 185), (130, 210, 255), role_spec["mob_val"]
            )

            # Tag de Baraja de 50 Cartas
            deck_surf = self.font_deck.render("🎴 Baraja Exclusiva: 50 Cartas Únicas", True, COLOR_GOLD)
            surface.blit(deck_surf, (stats_x + 4, stats_y + 90))

            # D. Cinta de Mecánica Pasiva Única (Perk Ribbon)
            perk_rect = pygame.Rect(draw_rect.x + 10, draw_rect.y + 162, draw_rect.width - 20, 32)
            pygame.draw.rect(surface, (22, 24, 32), perk_rect, border_radius=5)
            pygame.draw.rect(surface, role.color, perk_rect, 1, border_radius=5)
            # Acento lateral de color
            pygame.draw.rect(surface, role.color, (perk_rect.x, perk_rect.y, 4, perk_rect.height),
                             border_top_left_radius=5, border_bottom_left_radius=5)
            perk_surf = self.font_perk.render(role_spec["perk"], True, (240, 244, 252))
            surface.blit(perk_surf, (perk_rect.x + 10, perk_rect.y + 8))

            # E. Botón Interactivo de Elección
            btn_rect = pygame.Rect(draw_rect.x + 10, draw_rect.y + 202, draw_rect.width - 20, 38)
            if is_hovered:
                pygame.draw.rect(surface, (60, 48, 20), btn_rect, border_radius=6)
                pygame.draw.rect(surface, COLOR_GOLD, btn_rect, 2, border_radius=6)
                btn_str = f"▶ [ {slot_num} ] ELEGIR ESTE HÉROE ◀"
                btn_surf = self.font_btn.render(btn_str, True, COLOR_GOLD)
            else:
                pygame.draw.rect(surface, (25, 27, 34), btn_rect, border_radius=6)
                pygame.draw.rect(surface, (60, 65, 80), btn_rect, 1, border_radius=6)
                btn_str = f"[ {slot_num} ] Clic o tecla para Seleccionar"
                btn_surf = self.font_btn.render(btn_str, True, COLOR_STEAM)

            surface.blit(btn_surf, btn_surf.get_rect(center=btn_rect.center))

        # 6. Barra inferior de atajos y botón de volver
        back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 45, 300, 32)
        is_back_hovered = back_rect.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (45, 42, 35) if is_back_hovered else (24, 26, 32), back_rect, border_radius=4)
        pygame.draw.rect(surface, COLOR_GOLD if is_back_hovered else COLOR_COPPER, back_rect, 1, border_radius=4)
        back_text = self.font_sub.render("◀ [ESC] Volver  •  [A / D / Tab] Cambiar Pestaña", True,
                                         COLOR_GOLD if is_back_hovered else COLOR_WHITE)
        surface.blit(back_text, back_text.get_rect(center=back_rect.center))
