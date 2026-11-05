"""
================================================================================
MÓDULO: ui/card_menu.py
RESPONSABILIDAD: Menú modal interactivo y ultra-visual de selección de cartas.
CONCEPTO ACADÉMICO: Interfaz Gráfica Modal, Feedback Visual de Alta Fidelidad
                    y Reducción de Carga Cognitiva mediante Pastillas de Datos (Stat Badges).
================================================================================
Diseñado con estética roguelike premium (estilo Slay the Spire 2 & Hades):
- Fichas de cartas con ilustraciones vectoriales temáticas por rol y elemento.
- Información ultra-directa: badges y pastillas de estadísticas de alto contraste
  en lugar de muros de texto saturantes.
- Soporte para elevación por hover, efectos de brillo y selección con ratón o teclas [1, 2, 3].
"""

import math
import re
import pygame
from typing import List, Dict, Any, Optional

from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BRASS, COLOR_COPPER,
    COLOR_DARK_STONE, COLOR_GOLD, COLOR_WHITE, COLOR_STEAM,
    COLOR_RED_HEALTH, COLOR_MANA_BRIGHT, ELEMENT_COLORS
)
from systems.card_system import Card


# Paletas cromáticas y estilos por Rol
ROLE_THEMES = {
    "berserker": {
        "title": "BERSERKER BÁRBARO",
        "bg_dark": (28, 16, 18),
        "bg_inner": (42, 20, 24),
        "border": (195, 45, 45),
        "accent": (245, 75, 75),
        "emblem": "axe",
        "tag": "Furia & Sangre"
    },
    "paladin": {
        "title": "BALUARTE SAGRADO",
        "bg_dark": (32, 28, 16),
        "bg_inner": (46, 40, 22),
        "border": (225, 185, 45),
        "accent": (255, 225, 95),
        "emblem": "hammer",
        "tag": "Luz Divina"
    },
    "rogue": {
        "title": "ASESINO SOMBRÍO",
        "bg_dark": (16, 28, 22),
        "bg_inner": (22, 42, 32),
        "border": (38, 185, 95),
        "accent": (85, 235, 140),
        "emblem": "daggers",
        "tag": "Veneno & Críticos"
    },
    "mage": {
        "title": "SEÑOR ARCANO",
        "bg_dark": (18, 22, 38),
        "bg_inner": (26, 34, 58),
        "border": (55, 135, 235),
        "accent": (115, 185, 255),
        "emblem": "staff",
        "tag": "Éter & Maná"
    },
    "hunter": {
        "title": "TIRADOR DE ÉLITE",
        "bg_dark": (32, 24, 16),
        "bg_inner": (48, 34, 20),
        "border": (220, 125, 35),
        "accent": (255, 165, 70),
        "emblem": "crossbow",
        "tag": "Puntería & Trampas"
    },
    "necromancer": {
        "title": "SEÑOR DE ALMAS",
        "bg_dark": (26, 16, 34),
        "bg_inner": (38, 22, 50),
        "border": (165, 75, 225),
        "accent": (215, 135, 255),
        "emblem": "scythe",
        "tag": "Cosecha Espectral"
    },
    "runeknight": {
        "title": "CABALLERO RÚNICO",
        "bg_dark": (18, 26, 36),
        "bg_inner": (26, 38, 54),
        "border": (65, 165, 225),
        "accent": (120, 210, 255),
        "emblem": "runesword",
        "tag": "Filo Rúnico"
    },
    "alchemist": {
        "title": "PLAGA VOLÁTIL",
        "bg_dark": (18, 30, 18),
        "bg_inner": (26, 44, 26),
        "border": (115, 205, 45),
        "accent": (165, 245, 95),
        "emblem": "flask",
        "tag": "Química Caústica"
    },
    "monk": {
        "title": "MAESTRO DE KI",
        "bg_dark": (16, 28, 36),
        "bg_inner": (22, 42, 54),
        "border": (0, 215, 240),
        "accent": (100, 245, 255),
        "emblem": "fist",
        "tag": "Ráfaga de Ki"
    },
    "artificer": {
        "title": "INGENIERO VAPOR",
        "bg_dark": (34, 22, 16),
        "bg_inner": (48, 32, 22),
        "border": (215, 115, 30),
        "accent": (255, 160, 65),
        "emblem": "cannon",
        "tag": "Metralla & Calderas"
    },
    "shaman": {
        "title": "CHAMÁN BESTIAL",
        "bg_dark": (32, 22, 16),
        "bg_inner": (46, 32, 22),
        "border": (190, 110, 55),
        "accent": (235, 155, 95),
        "emblem": "totem",
        "tag": "Tótems & Tierra"
    },
    "inquisitor": {
        "title": "VERDUGO CARMESÍ",
        "bg_dark": (32, 16, 20),
        "bg_inner": (46, 22, 28),
        "border": (225, 45, 65),
        "accent": (255, 95, 115),
        "emblem": "flail",
        "tag": "Giro Penitente"
    }
}

DEFAULT_THEME = {
    "title": "MEJORA STEAMPUNK",
    "bg_dark": (22, 24, 30),
    "bg_inner": (34, 38, 48),
    "border": COLOR_BRASS,
    "accent": COLOR_GOLD,
    "emblem": "gear",
    "tag": "Runa Arcana"
}


class BadgeExtractor:
    """Extrae pastillas de estadísticas directas y concisas a partir de datos de la carta."""

    @staticmethod
    def extract(card: Card) -> List[Dict[str, Any]]:
        desc = getattr(card, 'description', '')
        name = getattr(card, 'name', '')
        elem = getattr(card, 'exclusive_element', None)
        cat = getattr(card, 'category', 'Ataque')

        badges = []

        # 1. Elemento Mágico
        if elem:
            elem_icons = {
                "Fuego": "🔥", "Agua": "🌊", "Viento": "🌪️", "Tierra": "🪨",
                "Trueno": "⚡", "Naturaleza": "🌿", "Luz": "☀️", "Oscuridad": "🌑",
                "Vapor": "💨", "Vapor (Steampunk)": "💨", "Metal": "⚙️"
            }
            ic = elem_icons.get(elem, "🔮")
            badges.append({
                "text": f"{ic} MAGIA {elem.upper()}",
                "bg": (65, 25, 20) if elem in ("Fuego", "Luz") else (20, 35, 65),
                "border": (245, 160, 40) if elem in ("Fuego", "Luz") else (70, 170, 245),
                "color": (255, 245, 220)
            })

        # 2. Daño porcentual
        m_dmg_pct = re.search(r'([+-]?\d+)%\s*daño', desc, re.IGNORECASE)
        if m_dmg_pct:
            val = m_dmg_pct.group(1)
            badges.append({
                "text": f"⚔️ {val}% DAÑO",
                "bg": (70, 18, 22),
                "border": (230, 60, 65),
                "color": (255, 230, 230)
            })

        # 3. Daño plano
        m_dmg_flat = re.search(r'([+-]?\d+)\s*daño', desc, re.IGNORECASE)
        if m_dmg_flat and not m_dmg_pct:
            val = m_dmg_flat.group(1)
            badges.append({
                "text": f"⚔️ +{val} DMG",
                "bg": (70, 18, 22),
                "border": (230, 60, 65),
                "color": (255, 230, 230)
            })

        # 4. Salud Máxima
        m_hp = re.search(r'([+-]?\d+)\s*HP\s*m[áa]ximo|\+([0-9]+)\s*HP(?!\s*robo)(?!\s*extra)(?!\s*/)', desc, re.IGNORECASE)
        if m_hp:
            val = m_hp.group(1) or m_hp.group(2)
            badges.append({
                "text": f"❤️ +{val} HP",
                "bg": (18, 65, 30),
                "border": (45, 200, 95),
                "color": (230, 255, 235)
            })

        # 5. Curación Directa
        m_heal = re.search(r'(?:cura|restaura)\s*([0-9]+)\s*HP', desc, re.IGNORECASE)
        if m_heal:
            val = m_heal.group(1)
            badges.append({
                "text": f"💚 +{val} SALUD",
                "bg": (20, 60, 45),
                "border": (40, 210, 150),
                "color": (225, 255, 245)
            })

        # 6. Maná Máximo
        m_mp = re.search(r'([+-]?\d+)\s*Man[áa]\s*M[áa]ximo|\+([0-9]+)\s*MP(?!\s*/)', desc, re.IGNORECASE)
        if m_mp:
            val = m_mp.group(1) or m_mp.group(2)
            badges.append({
                "text": f"🔮 +{val} MP",
                "bg": (20, 40, 75),
                "border": (60, 150, 245),
                "color": (225, 245, 255)
            })

        # 7. Regeneración de Maná
        m_mpregen = re.search(r'([+-]?\d+)\s*MP/s', desc, re.IGNORECASE)
        if m_mpregen:
            val = m_mpregen.group(1)
            badges.append({
                "text": f"🔮 +{val} MP/s",
                "bg": (22, 45, 80),
                "border": (80, 160, 255),
                "color": (230, 248, 255)
            })

        # 8. Velocidad
        m_spd = re.search(r'([+-]\d+)%\s*velocidad', desc, re.IGNORECASE)
        if m_spd:
            val = m_spd.group(1)
            if '-' in val:
                badges.append({
                    "text": f"⚠️ {val}% VEL",
                    "bg": (65, 40, 15),
                    "border": (235, 140, 30),
                    "color": (255, 235, 210)
                })
            else:
                badges.append({
                    "text": f"💨 +{val}% VEL",
                    "bg": (15, 55, 70),
                    "border": (35, 185, 215),
                    "color": (225, 255, 255)
                })

        # 9. Mitigación / Escudo
        m_mit = re.search(r'(?:mitiga|reduce[a-z\s]*daño[a-z\s]*en|mitigaci[óo]n|reducci[óo]n[a-z\s]*daño)\s*(?:un\s*)?([0-9]+)%', desc, re.IGNORECASE)
        if not m_mit:
            m_mit = re.search(r'([0-9]+)%\s*(?:mitigaci[óo]n|reducci[óo]n)', desc, re.IGNORECASE)
        if m_mit:
            val = m_mit.group(1)
            badges.append({
                "text": f"🛡️ -{val}% DAÑO",
                "bg": (25, 45, 75),
                "border": (75, 160, 235),
                "color": (230, 245, 255)
            })

        # 10. Crítico
        m_crit = re.search(r'([+-]?\d+)%\s*cr[íi]tico', desc, re.IGNORECASE)
        if m_crit:
            val = m_crit.group(1)
            badges.append({
                "text": f"⚡ +{val}% CRÍT",
                "bg": (65, 55, 15),
                "border": (240, 195, 35),
                "color": (255, 250, 220)
            })

        # 11. Robo de Vida
        m_ls = re.search(r'([+-]?\d+)\s*HP\s*(?:extra\s*)?robo', desc, re.IGNORECASE)
        if m_ls:
            val = m_ls.group(1)
            badges.append({
                "text": f"🩸 +{val} ROBO",
                "bg": (70, 16, 32),
                "border": (225, 40, 85),
                "color": (255, 230, 235)
            })

        # 12. Cadencia / Cooldown
        m_cd = re.search(r'cooldown[a-z\s]*en\s*([0-9.]+)s|acelera[a-z\s]*([0-9]+)%', desc, re.IGNORECASE)
        if m_cd:
            val = m_cd.group(1) or f"+{m_cd.group(2)}%"
            badges.append({
                "text": f"⏱️ {val} CADENCIA",
                "bg": (65, 40, 18),
                "border": (235, 140, 35),
                "color": (255, 240, 220)
            })

        # Fallback si no hubo coincidencia regex
        if not badges:
            cat_clean = cat.upper()
            if "ATAQUE" in cat_clean or "DAÑO" in cat_clean:
                badges.append({"text": "⚔️ MEJORA DE COMBATE", "bg": (70, 18, 22), "border": (230, 60, 65), "color": (255, 230, 230)})
            elif "DEFENSA" in cat_clean or "VIDA" in cat_clean:
                badges.append({"text": "🛡️ PROTECCIÓN PASIVA", "bg": (18, 65, 30), "border": (45, 200, 95), "color": (230, 255, 235)})
            elif "HABILIDAD" in cat_clean or "VELOCIDAD" in cat_clean:
                badges.append({"text": "⚡ MANIOBRA TÁCTICA", "bg": (15, 55, 70), "border": (35, 185, 215), "color": (225, 255, 255)})
            else:
                badges.append({"text": "⭐ PODER SUPREMO", "bg": (65, 50, 15), "border": (240, 190, 35), "color": (255, 248, 210)})

        return badges[:3]

    @staticmethod
    def get_concise_summary(card: Card) -> str:
        """Genera un subtítulo ultra-conciso (máximo 5-7 palabras) para evitar sobrecarga."""
        name = getattr(card, 'name', '')
        desc = getattr(card, 'description', '')
        cat = getattr(card, 'category', 'Ataque')
        elem = getattr(card, 'exclusive_element', None)

        if elem:
            return f"Canaliza el poder elemental de {elem.lower()}"
        if "Cosecha" in name or "Alma" in name:
            return "Bajas enemigas recargan tu energía"
        if "Dragón" in name or "Titán" in name:
            return "Ascenso colosal de combate ancestral"
        if "Sacrificio" in name:
            return "Ataque letal a cambio de vitalidad"
        if "Escudo" in name or "Coraza" in name or "Piel" in name:
            return "Blindaje endurecido contra impactos"
        if "Furia" in name or "Frenesí" in name:
            return "Aumenta la fuerza destructiva"
        if "Veneno" in name or "Furtiv" in name:
            return "Golpes críticos y daño venenoso"
        if "Puntería" in name or "Saeta" in name:
            return "Disparos letales de largo alcance"
        if "Frasco" in name or "Alquim" in name:
            return "Compuestos químicos de área volátil"
        if "Ki" in name or "Palma" in name:
            return "Impactos rápidos a gran velocidad"
        if "Cañón" in name or "Metralla" in name:
            return "Detonaciones de vapor a presión"
        if "Tótem" in name:
            return "Invocación y sustento espiritual"

        # Simplificación de descripción corta si no excede 45 caracteres
        clean_desc = desc.split('.')[0].strip()
        if len(clean_desc) <= 45:
            return clean_desc
        return "Mejora directa para tu repertorio de héroe"


class CardMenu:
    """Ventana modal interactiva de selección de cartas con arte vectorial e información concisa."""

    def __init__(self, audio_system=None):
        self.audio_system = audio_system
        # Tipografías limpias y nítidas
        self.font_title = pygame.font.SysFont("Consolas", 26, bold=True)
        self.font_sub = pygame.font.SysFont("Consolas", 13)
        self.font_name = pygame.font.SysFont("Consolas", 17, bold=True)
        self.font_archetype = pygame.font.SysFont("Consolas", 11, bold=True)
        self.font_badge = pygame.font.SysFont("Consolas", 12, bold=True)
        self.font_summary = pygame.font.SysFont("Consolas", 12)
        self.font_btn = pygame.font.SysFont("Consolas", 13, bold=True)
        self.font_key = pygame.font.SysFont("Consolas", 12, bold=True)

        # Dimensiones de las cartas (3 en pantalla)
        self.card_width = 330
        self.card_height = 490
        self.card_gap = 36

        # Posicionamiento centrado
        total_w = 3 * self.card_width + 2 * self.card_gap
        self.start_x = (SCREEN_WIDTH - total_w) // 2
        self.start_y = (SCREEN_HEIGHT - self.card_height) // 2 + 35

        self.cards: List[Card] = []
        self.card_rects: List[pygame.Rect] = []
        self.hovered_index = -1
        self.anim_timer = 0.0

    def set_cards(self, cards: list):
        """Asigna las 3 cartas que se mostrarán en esta ronda de selección."""
        self.cards = list(cards)
        self.card_rects.clear()

        for i in range(len(self.cards)):
            x = self.start_x + i * (self.card_width + self.card_gap)
            y = self.start_y
            self.card_rects.append(pygame.Rect(x, y, self.card_width, self.card_height))
        self.hovered_index = -1

    def handle_event(self, event: pygame.event.Event) -> Optional[Card]:
        """Procesa selección mediante ratón o teclado [1, 2, 3]."""
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            prev_hover = self.hovered_index
            self.hovered_index = -1
            for idx, rect in enumerate(self.card_rects):
                if rect.collidepoint(mouse_pos):
                    self.hovered_index = idx
                    if self.hovered_index != prev_hover and self.audio_system:
                        self.audio_system.play_sfx("ui_hover")
                    break

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            for idx, rect in enumerate(self.card_rects):
                if rect.collidepoint(mouse_pos):
                    return self.cards[idx]

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_1, pygame.K_KP1) and len(self.cards) >= 1:
                return self.cards[0]
            elif event.key in (pygame.K_2, pygame.K_KP2) and len(self.cards) >= 2:
                return self.cards[1]
            elif event.key in (pygame.K_3, pygame.K_KP3) and len(self.cards) >= 3:
                return self.cards[2]
            elif event.key == pygame.K_LEFT:
                if self.hovered_index <= 0:
                    self.hovered_index = len(self.cards) - 1
                else:
                    self.hovered_index -= 1
                if self.audio_system:
                    self.audio_system.play_sfx("ui_hover")
            elif event.key == pygame.K_RIGHT:
                if self.hovered_index < 0 or self.hovered_index >= len(self.cards) - 1:
                    self.hovered_index = 0
                else:
                    self.hovered_index += 1
                if self.audio_system:
                    self.audio_system.play_sfx("ui_hover")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if 0 <= self.hovered_index < len(self.cards):
                    return self.cards[self.hovered_index]

        return None

    def draw(self, surface: pygame.Surface):
        """Renderiza el menú modal con cartas vectoriales y efectos visuales."""
        self.anim_timer += 0.035

        # 1. Fondo de oscurecimiento cinematográfico
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 10, 14, 225))
        surface.blit(overlay, (0, 0))

        # 2. Encabezado de la interfaz
        pulse_gold = int(220 + 35 * math.sin(self.anim_timer * 2.5))
        pulse_gold = max(180, min(255, pulse_gold))
        header_gold = (pulse_gold, int(pulse_gold * 0.82), 25)

        title_surf = self.font_title.render("⚙  SELECCIÓN DE MEJORA RÚNICA  ⚙", True, header_gold)
        surface.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, self.start_y - 62)))

        sub_surf = self.font_sub.render(
            "Elige 1 carta para potenciar a tu héroe  •  [1, 2, 3] o Clic para seleccionar",
            True, COLOR_STEAM
        )
        surface.blit(sub_surf, sub_surf.get_rect(center=(SCREEN_WIDTH // 2, self.start_y - 28)))

        # 3. Dibujar las 3 cartas
        for idx, (card, base_rect) in enumerate(zip(self.cards, self.card_rects)):
            is_hover = (idx == self.hovered_index)

            # Efecto de elevación por hover
            y_offset = -12 if is_hover else 0
            rect = pygame.Rect(base_rect.x, base_rect.y + y_offset, base_rect.width, base_rect.height)

            # Tema del rol
            char_id = getattr(card, 'character_id', None)
            theme = ROLE_THEMES.get(str(char_id).lower(), DEFAULT_THEME)

            self._draw_single_card(surface, card, rect, idx, is_hover, theme)

    def _draw_single_card(self, surface: pygame.Surface, card: Card, rect: pygame.Rect,
                          idx: int, is_hover: bool, theme: Dict[str, Any]):
        """Renderiza una tarjeta individual con marco, arte vectorial y pastillas de datos."""
        # 1. Sombra de elevación en hover
        if is_hover:
            shadow_surf = pygame.Surface((rect.width + 16, rect.height + 16), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, 120), shadow_surf.get_rect(), border_radius=14)
            surface.blit(shadow_surf, (rect.x - 8, rect.y + 10))

        # 2. Fondo base de la carta
        card_bg = theme["bg_dark"] if not card.is_golden else (38, 30, 14)
        pygame.draw.rect(surface, card_bg, rect, border_radius=10)

        # 3. Marco exterior decorativo
        border_color = COLOR_GOLD if card.is_golden else (theme["accent"] if is_hover else theme["border"])
        border_thick = 3 if (card.is_golden or is_hover) else 2
        pygame.draw.rect(surface, border_color, rect, border_thick, border_radius=10)

        # Halo brillante en hover
        if is_hover or card.is_golden:
            glow_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            glow_alpha = int(45 + 25 * math.sin(self.anim_timer * 4.0)) if card.is_golden else 35
            glow_col = (*border_color[:3], glow_alpha)
            pygame.draw.rect(glow_surf, glow_col, glow_surf.get_rect(), 4, border_radius=10)
            surface.blit(glow_surf, (rect.x, rect.y))

        # Remaches ornamentales en las 4 esquinas
        rivet_color = COLOR_GOLD if card.is_golden else COLOR_BRASS
        for rx, ry in [(rect.left + 8, rect.top + 8), (rect.right - 8, rect.top + 8),
                       (rect.left + 8, rect.bottom - 8), (rect.right - 8, rect.bottom - 8)]:
            pygame.draw.circle(surface, (15, 15, 18), (rx, ry), 3)
            pygame.draw.circle(surface, rivet_color, (rx, ry), 2)

        # =====================================================================
        # ENCABEZADO SUPERIOR: Botón [1,2,3], Categoría y Rareza
        # =====================================================================
        # A. Atajo numérico [1], [2], [3]
        key_rect = pygame.Rect(rect.left + 14, rect.top + 12, 28, 22)
        pygame.draw.rect(surface, (20, 22, 28), key_rect, border_radius=5)
        pygame.draw.rect(surface, rivet_color, key_rect, 1, border_radius=5)
        key_lbl = self.font_key.render(f"[{idx + 1}]", True, rivet_color)
        surface.blit(key_lbl, key_lbl.get_rect(center=key_rect.center))

        # B. Pastilla de Categoría (Centro)
        cat_text = getattr(card, 'category', 'Ataque').upper()
        cat_icons = {"ATAQUE": "⚔️", "DEFENSA": "🛡️", "HABILIDAD": "⚡", "PODER": "🔥", "MAGIA": "🔮"}
        cat_icon = cat_icons.get(cat_text, "✨")
        cat_label_str = f"{cat_icon} {cat_text}"
        cat_surf = self.font_archetype.render(cat_label_str, True, COLOR_STEAM)
        cat_rect = pygame.Rect(rect.centerx - 55, rect.top + 13, 110, 20)
        pygame.draw.rect(surface, (18, 20, 26), cat_rect, border_radius=10)
        pygame.draw.rect(surface, (55, 60, 75), cat_rect, 1, border_radius=10)
        surface.blit(cat_surf, cat_surf.get_rect(center=cat_rect.center))

        # C. Insignia de Rareza (Derecha)
        rarity_str = getattr(card, 'rarity', 'Común').upper()
        if card.is_golden:
            rar_color = COLOR_GOLD
            rar_text = "⭐ RARA"
        elif "POCO" in rarity_str:
            rar_color = (80, 200, 240)
            rar_text = "POCO COMÚN"
        else:
            rar_color = (180, 195, 210)
            rar_text = "COMÚN"
        rar_surf = self.font_archetype.render(rar_text, True, rar_color)
        surface.blit(rar_surf, (rect.right - rar_surf.get_width() - 14, rect.top + 15))

        # =====================================================================
        # TÍTULO DE LA CARTA & ARQUETIPO
        # =====================================================================
        name_clean = card.name.replace("⭐", "").strip()
        name_color = COLOR_GOLD if card.is_golden else COLOR_WHITE
        name_surf = self.font_name.render(name_clean, True, name_color)
        if name_surf.get_width() > rect.width - 30:
            # Escalar fuente ligeramente si es muy extenso
            small_font = pygame.font.SysFont("Consolas", 15, bold=True)
            name_surf = small_font.render(name_clean, True, name_color)
        surface.blit(name_surf, name_surf.get_rect(center=(rect.centerx, rect.top + 48)))

        # Subtítulo del Rol / Arquetipo
        arch_surf = self.font_archetype.render(f"— {theme['title']} —", True, theme["accent"])
        surface.blit(arch_surf, arch_surf.get_rect(center=(rect.centerx, rect.top + 68)))

        # =====================================================================
        # VENTANA ILUSTRATIVA VECTORIAL (ART BOX)
        # =====================================================================
        art_w = rect.width - 36
        art_h = 145
        art_rect = pygame.Rect(rect.left + 18, rect.top + 82, art_w, art_h)

        # Fondo del cuadro de arte
        pygame.draw.rect(surface, theme["bg_inner"], art_rect, border_radius=8)
        # Borde biselado
        pygame.draw.rect(surface, (20, 22, 28), art_rect, 2, border_radius=8)
        pygame.draw.rect(surface, theme["border"], art_rect, 1, border_radius=8)

        # Dibujar emblema vectorial temático
        self._draw_vector_emblem(surface, art_rect, card, theme)

        # =====================================================================
        # PASTILLAS DE ESTADÍSTICAS DIRECTAS (STAT BADGES)
        # =====================================================================
        badges = BadgeExtractor.extract(card)
        badges_start_y = art_rect.bottom + 14

        if len(badges) == 1:
            # 1 sola pastilla ancha centrada
            b = badges[0]
            bw = art_w
            bh = 34
            bx = rect.left + 18
            by = badges_start_y + 10
            self._draw_stat_pill(surface, bx, by, bw, bh, b)
        elif len(badges) == 2:
            # 2 pastillas lado a lado
            bw = (art_w - 10) // 2
            bh = 34
            by = badges_start_y + 10
            self._draw_stat_pill(surface, rect.left + 18, by, bw, bh, badges[0])
            self._draw_stat_pill(surface, rect.left + 18 + bw + 10, by, bw, bh, badges[1])
        elif len(badges) >= 3:
            # 2 arriba, 1 centrada abajo
            bw = (art_w - 10) // 2
            bh = 28
            by1 = badges_start_y
            self._draw_stat_pill(surface, rect.left + 18, by1, bw, bh, badges[0])
            self._draw_stat_pill(surface, rect.left + 18 + bw + 10, by1, bw, bh, badges[1])

            by2 = by1 + bh + 8
            bw_center = int(art_w * 0.85)
            bx_center = rect.centerx - bw_center // 2
            self._draw_stat_pill(surface, bx_center, by2, bw_center, bh, badges[2])

        # =====================================================================
        # SUBTÍTULO CONCISO / MICRO-RESUMEN
        # =====================================================================
        summary_text = BadgeExtractor.get_concise_summary(card)
        summary_surf = self.font_summary.render(summary_text, True, COLOR_STEAM)
        summary_y = rect.bottom - 82
        surface.blit(summary_surf, summary_surf.get_rect(center=(rect.centerx, summary_y)))

        # Divisor sutil
        div_y = rect.bottom - 60
        div_w = art_w - 40
        pygame.draw.line(surface, (45, 50, 62), (rect.centerx - div_w // 2, div_y),
                         (rect.centerx + div_w // 2, div_y), 1)

        # =====================================================================
        # BOTÓN INFERIOR DE ACCIÓN
        # =====================================================================
        btn_w = art_w
        btn_h = 36
        btn_rect = pygame.Rect(rect.left + 18, rect.bottom - 48, btn_w, btn_h)

        if is_hover:
            btn_bg = COLOR_GOLD if card.is_golden else COLOR_BRASS
            btn_border = COLOR_WHITE
            btn_text_col = (15, 15, 20)
        else:
            btn_bg = (24, 26, 34)
            btn_border = border_color
            btn_text_col = COLOR_WHITE

        pygame.draw.rect(surface, btn_bg, btn_rect, border_radius=6)
        pygame.draw.rect(surface, btn_border, btn_rect, 1, border_radius=6)

        btn_str = f"ELEGIR CARTA [{idx + 1}]"
        btn_surf = self.font_btn.render(btn_str, True, btn_text_col)
        surface.blit(btn_surf, btn_surf.get_rect(center=btn_rect.center))

    def _draw_stat_pill(self, surface: pygame.Surface, x: int, y: int, w: int, h: int, badge: Dict[str, Any]):
        """Dibuja una pastilla de estadística limpia, estilizada y de alto contraste."""
        pill_rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surface, badge["bg"], pill_rect, border_radius=7)
        pygame.draw.rect(surface, badge["border"], pill_rect, 1, border_radius=7)

        # Texto centrado
        txt_surf = self.font_badge.render(badge["text"], True, badge["color"])
        surface.blit(txt_surf, txt_surf.get_rect(center=pill_rect.center))

    def _draw_vector_emblem(self, surface: pygame.Surface, art_rect: pygame.Rect,
                            card: Card, theme: Dict[str, Any]):
        """Renderiza una ilustración vectorial pulida para el cuadro de arte."""
        cx = art_rect.centerx
        cy = art_rect.centery
        elem = getattr(card, 'exclusive_element', None)
        emblem_type = theme.get("emblem", "gear")

        # Resplandor suave de fondo en el arte
        glow_rad = 50
        glow_surf = pygame.Surface((glow_rad * 2, glow_rad * 2), pygame.SRCALPHA)
        glow_color = (*theme["accent"][:3], 35)
        pygame.draw.circle(glow_surf, glow_color, (glow_rad, glow_rad), glow_rad)
        surface.blit(glow_surf, (cx - glow_rad, cy - glow_rad))

        # Si la carta tiene elemento mágico, dibujar el emblema elemental
        if elem:
            self._draw_elemental_emblem(surface, cx, cy, elem)
            return

        # De lo contrario, dibujar el arma o emblema de rol
        if emblem_type == "axe":
            self._draw_axe_vector(surface, cx, cy, theme)
        elif emblem_type == "hammer":
            self._draw_hammer_vector(surface, cx, cy, theme)
        elif emblem_type == "daggers":
            self._draw_daggers_vector(surface, cx, cy, theme)
        elif emblem_type == "staff":
            self._draw_staff_vector(surface, cx, cy, theme)
        elif emblem_type == "crossbow":
            self._draw_crossbow_vector(surface, cx, cy, theme)
        elif emblem_type == "scythe":
            self._draw_scythe_vector(surface, cx, cy, theme)
        elif emblem_type == "runesword":
            self._draw_runesword_vector(surface, cx, cy, theme)
        elif emblem_type == "flask":
            self._draw_flask_vector(surface, cx, cy, theme)
        elif emblem_type == "fist":
            self._draw_fist_vector(surface, cx, cy, theme)
        elif emblem_type == "cannon":
            self._draw_cannon_vector(surface, cx, cy, theme)
        elif emblem_type == "totem":
            self._draw_totem_vector(surface, cx, cy, theme)
        elif emblem_type == "flail":
            self._draw_flail_vector(surface, cx, cy, theme)
        else:
            self._draw_gear_vector(surface, cx, cy, theme)

    # -------------------------------------------------------------------------
    # DIBUJADO VECTORIAL DE EMBLEMAS DE ROL Y ARMAS
    # -------------------------------------------------------------------------
    def _draw_axe_vector(self, surface, cx, cy, theme):
        """Hacha Bárbara de doble filo."""
        # Mango
        pygame.draw.line(surface, (80, 50, 30), (cx, cy - 42), (cx, cy + 42), 6)
        pygame.draw.line(surface, COLOR_BRASS, (cx, cy - 25), (cx, cy - 20), 8)
        # Hojas gemelas
        pts_left = [(cx - 2, cy - 25), (cx - 38, cy - 36), (cx - 44, cy), (cx - 35, cy + 26), (cx - 2, cy + 10)]
        pts_right = [(cx + 2, cy - 25), (cx + 38, cy - 36), (cx + 44, cy), (cx + 35, cy + 26), (cx + 2, cy + 10)]
        pygame.draw.polygon(surface, (180, 190, 205), pts_left)
        pygame.draw.polygon(surface, (180, 190, 205), pts_right)
        pygame.draw.lines(surface, theme["accent"], False, [(cx - 38, cy - 36), (cx - 44, cy), (cx - 35, cy + 26)], 2)
        pygame.draw.lines(surface, theme["accent"], False, [(cx + 38, cy - 36), (cx + 44, cy), (cx + 35, cy + 26)], 2)
        pygame.draw.circle(surface, COLOR_GOLD, (cx, cy - 8), 5)

    def _draw_hammer_vector(self, surface, cx, cy, theme):
        """Maza Sagrada de Guerra."""
        # Mango dorado
        pygame.draw.line(surface, (120, 95, 45), (cx, cy - 40), (cx, cy + 42), 5)
        # Cabeza de maza
        pygame.draw.rect(surface, (230, 200, 60), (cx - 30, cy - 38, 60, 24), border_radius=4)
        pygame.draw.rect(surface, (255, 245, 160), (cx - 22, cy - 34, 44, 16), border_radius=3)
        # Estrella sagrada en el centro
        pygame.draw.line(surface, (255, 255, 255), (cx, cy - 45), (cx, cy - 10), 2)
        pygame.draw.line(surface, (255, 255, 255), (cx - 35, cy - 26), (cx + 35, cy - 26), 2)

    def _draw_daggers_vector(self, surface, cx, cy, theme):
        """Dagas Gemelas Venenosas en cruz."""
        # Daga 1 (diagonal)
        pygame.draw.line(surface, (50, 50, 50), (cx - 32, cy - 32), (cx + 32, cy + 32), 4)
        pygame.draw.polygon(surface, (190, 210, 200), [(cx - 32, cy - 32), (cx - 8, cy - 6), (cx - 6, cy - 8)])
        # Daga 2
        pygame.draw.line(surface, (50, 50, 50), (cx + 32, cy - 32), (cx - 32, cy + 32), 4)
        # Filos verdes brillantes
        pygame.draw.circle(surface, theme["accent"], (cx - 28, cy - 28), 3)
        pygame.draw.circle(surface, theme["accent"], (cx + 28, cy - 28), 3)

    def _draw_staff_vector(self, surface, cx, cy, theme):
        """Bastón Rúnico con orbe de éter."""
        # Vara
        pygame.draw.line(surface, (90, 110, 140), (cx, cy - 42), (cx, cy + 42), 4)
        # Corona del bastón
        pygame.draw.circle(surface, (45, 65, 110), (cx, cy - 22), 16, 2)
        # Orbe brillante
        pygame.draw.circle(surface, (100, 180, 255), (cx, cy - 22), 9)
        pygame.draw.circle(surface, (240, 250, 255), (cx - 2, cy - 24), 3)
        # Anillo orbital
        pygame.draw.ellipse(surface, (140, 210, 255), (cx - 20, cy - 28, 40, 12), 1)

    def _draw_crossbow_vector(self, surface, cx, cy, theme):
        """Ballesta de Repetición."""
        # Fuste
        pygame.draw.line(surface, (110, 75, 45), (cx, cy - 35), (cx, cy + 35), 6)
        # Arco metálico
        pygame.draw.arc(surface, (190, 140, 60), (cx - 38, cy - 35, 76, 40), 0, math.pi, 4)
        # Cuerda tensada
        pygame.draw.line(surface, (240, 240, 250), (cx - 36, cy - 15), (cx, cy - 5), 2)
        pygame.draw.line(surface, (240, 240, 250), (cx + 36, cy - 15), (cx, cy - 5), 2)
        # Saeta cargada
        pygame.draw.line(surface, theme["accent"], (cx, cy - 36), (cx, cy - 4), 3)

    def _draw_scythe_vector(self, surface, cx, cy, theme):
        """Guadaña Espectral de Almas."""
        # Asta curva
        pygame.draw.line(surface, (50, 35, 60), (cx - 15, cy + 40), (cx + 12, cy - 35), 5)
        # Filo curvo de guadaña
        pts_blade = [(cx + 12, cy - 35), (cx - 40, cy - 38), (cx - 35, cy - 18), (cx + 5, cy - 22)]
        pygame.draw.polygon(surface, (185, 140, 230), pts_blade)
        pygame.draw.lines(surface, theme["accent"], False, [(cx + 12, cy - 35), (cx - 40, cy - 38)], 2)
        # Fuego fatuo
        pygame.draw.circle(surface, (220, 150, 255), (cx - 22, cy - 28), 4)

    def _draw_runesword_vector(self, surface, cx, cy, theme):
        """Espadón Rúnico Ancestral."""
        # Hoja recta y ancha
        pts_sword = [(cx, cy - 42), (cx + 12, cy - 30), (cx + 10, cy + 18), (cx - 10, cy + 18), (cx - 12, cy - 30)]
        pygame.draw.polygon(surface, (190, 210, 230), pts_sword)
        # Guarda
        pygame.draw.line(surface, (220, 180, 50), (cx - 24, cy + 18), (cx + 24, cy + 18), 5)
        # Empuñadura
        pygame.draw.line(surface, (60, 45, 30), (cx, cy + 18), (cx, cy + 40), 4)
        # Runas luminosas a lo largo de la hoja
        pygame.draw.circle(surface, theme["accent"], (cx, cy - 18), 3)
        pygame.draw.circle(surface, theme["accent"], (cx, cy - 5), 3)
        pygame.draw.circle(surface, theme["accent"], (cx, cy + 8), 3)

    def _draw_flask_vector(self, surface, cx, cy, theme):
        """Frasco Químico Alquímico."""
        # Cuello del matraz
        pygame.draw.rect(surface, (180, 215, 230), (cx - 6, cy - 34, 12, 14), 2)
        # Cuerpo cónico
        pts_flask = [(cx - 6, cy - 20), (cx + 6, cy - 20), (cx + 28, cy + 24), (cx - 28, cy + 24)]
        pygame.draw.polygon(surface, (30, 80, 35), pts_flask)
        pygame.draw.polygon(surface, theme["accent"], pts_flask, 2)
        # Burbujas de ácido
        pygame.draw.circle(surface, (190, 255, 100), (cx - 8, cy + 10), 4)
        pygame.draw.circle(surface, (190, 255, 100), (cx + 10, cy + 6), 3)
        pygame.draw.circle(surface, (190, 255, 100), (cx, cy - 2), 2)

    def _draw_fist_vector(self, surface, cx, cy, theme):
        """Puño de Ki Relampagueante."""
        # Silueta del puño
        pygame.draw.rect(surface, (210, 180, 140), (cx - 16, cy - 16, 32, 28), border_radius=6)
        # Cintas de combate
        pygame.draw.line(surface, (250, 250, 255), (cx - 16, cy - 6), (cx + 16, cy - 6), 2)
        pygame.draw.line(surface, (250, 250, 255), (cx - 16, cy + 4), (cx + 16, cy + 4), 2)
        # Ondas sónicas de Ki
        pygame.draw.arc(surface, theme["accent"], (cx - 28, cy - 26, 56, 52), -0.7, 0.7, 3)
        pygame.draw.arc(surface, theme["accent"], (cx - 38, cy - 36, 76, 72), -0.7, 0.7, 2)

    def _draw_cannon_vector(self, surface, cx, cy, theme):
        """Cañón de Vapor Steampunk."""
        # Cañón cilíndrico de bronce
        pygame.draw.rect(surface, (180, 115, 45), (cx - 30, cy - 14, 52, 24), border_radius=4)
        pygame.draw.rect(surface, (215, 160, 65), (cx - 32, cy - 17, 8, 30), border_radius=3)
        # Rueda dentada de soporte
        pygame.draw.circle(surface, (90, 95, 105), (cx + 8, cy + 16), 14)
        pygame.draw.circle(surface, COLOR_BRASS, (cx + 8, cy + 16), 5)
        # Nube de vapor saliendo
        pygame.draw.circle(surface, (220, 235, 250), (cx - 40, cy - 6), 7)
        pygame.draw.circle(surface, (220, 235, 250), (cx - 48, cy - 14), 5)

    def _draw_totem_vector(self, surface, cx, cy, theme):
        """Tótem Primordial Chamánico."""
        # Tronco tallado
        pygame.draw.rect(surface, (100, 65, 38), (cx - 20, cy - 35, 40, 70), border_radius=6)
        # Ojos iluminados del tótem
        pygame.draw.ellipse(surface, (255, 200, 50), (cx - 14, cy - 20, 10, 6))
        pygame.draw.ellipse(surface, (255, 200, 50), (cx + 4, cy - 20, 10, 6))
        # Boca ceremonial
        pygame.draw.rect(surface, (40, 25, 15), (cx - 12, cy - 4, 24, 8), border_radius=2)
        # Plumas laterales
        pygame.draw.polygon(surface, theme["accent"], [(cx - 20, cy - 25), (cx - 36, cy - 15), (cx - 20, cy - 5)])
        pygame.draw.polygon(surface, theme["accent"], [(cx + 20, cy - 25), (cx + 36, cy - 15), (cx + 20, cy - 5)])

    def _draw_flail_vector(self, surface, cx, cy, theme):
        """Mangual Dentado de Inquisidor."""
        # Mango
        pygame.draw.line(surface, (70, 50, 40), (cx - 25, cy + 30), (cx - 10, cy - 5), 5)
        # Cadena
        for offset in [(cx - 4, cy - 14), (cx + 4, cy - 20), (cx + 15, cy - 18)]:
            pygame.draw.circle(surface, (160, 170, 180), offset, 4, 1)
        # Bola con púas
        bx, by = cx + 22, cy - 6
        pygame.draw.circle(surface, (55, 55, 60), (bx, by), 14)
        for ang in range(0, 360, 45):
            rad = math.radians(ang)
            px = bx + int(19 * math.cos(rad))
            py = by + int(19 * math.sin(rad))
            pygame.draw.line(surface, theme["accent"], (bx, by), (px, py), 2)

    def _draw_gear_vector(self, surface, cx, cy, theme):
        """Engranaje Steampunk estándar."""
        pygame.draw.circle(surface, COLOR_BRASS, (cx, cy), 24)
        for ang in range(0, 360, 45):
            rad = math.radians(ang)
            px = cx + int(28 * math.cos(rad))
            py = cy + int(28 * math.sin(rad))
            pygame.draw.circle(surface, COLOR_GOLD, (px, py), 4)
        pygame.draw.circle(surface, theme["bg_inner"], (cx, cy), 10)
        pygame.draw.circle(surface, COLOR_COPPER, (cx, cy), 4)

    # -------------------------------------------------------------------------
    # DIBUJADO DE EMBLEMAS ELEMENTALES
    # -------------------------------------------------------------------------
    def _draw_elemental_emblem(self, surface, cx, cy, elem: str):
        """Emblemas de alta resolución para cartas elementales."""
        if elem == "Fuego":
            # Llamarada en capas
            pygame.draw.polygon(surface, (230, 60, 30), [(cx, cy - 35), (cx + 22, cy + 18), (cx - 22, cy + 18)])
            pygame.draw.polygon(surface, (255, 140, 20), [(cx, cy - 25), (cx + 15, cy + 16), (cx - 15, cy + 16)])
            pygame.draw.polygon(surface, (255, 230, 80), [(cx, cy - 10), (cx + 8, cy + 15), (cx - 8, cy + 15)])
        elif elem == "Trueno":
            # Relámpago en zigzag
            pts_bolt = [(cx + 6, cy - 36), (cx - 12, cy - 6), (cx + 2, cy - 6), (cx - 8, cy + 34), (cx + 16, cy + 2), (cx + 2, cy + 2)]
            pygame.draw.polygon(surface, (255, 225, 40), pts_bolt)
            pygame.draw.polygon(surface, (255, 255, 255), [(p[0] - 1, p[1]) for p in pts_bolt[:4]])
        elif elem == "Luz":
            # Estrella radiante de 8 puntas
            for ang in range(0, 360, 45):
                rad = math.radians(ang)
                dist = 34 if (ang % 90 == 0) else 20
                px = cx + int(dist * math.cos(rad))
                py = cy + int(dist * math.sin(rad))
                pygame.draw.line(surface, (255, 245, 180), (cx, cy), (px, py), 3)
            pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 12)
        elif elem == "Oscuridad":
            # Agujero negro abisal con disco de acreción
            pygame.draw.circle(surface, (140, 50, 200), (cx, cy), 28, 3)
            pygame.draw.ellipse(surface, (190, 80, 255), (cx - 36, cy - 14, 72, 28), 2)
            pygame.draw.circle(surface, (12, 10, 16), (cx, cy), 16)
        elif elem == "Agua":
            # Olas gemelas oceánicas
            pygame.draw.arc(surface, (50, 150, 240), (cx - 30, cy - 20, 36, 36), 0, math.pi, 4)
            pygame.draw.arc(surface, (90, 190, 255), (cx - 6, cy - 28, 38, 40), 0, math.pi, 4)
            pygame.draw.circle(surface, (220, 245, 255), (cx + 18, cy - 22), 4)
        elif elem == "Viento":
            # Vórtice espiral
            pygame.draw.arc(surface, (40, 200, 160), (cx - 26, cy - 26, 52, 52), 0.5, 3.2, 4)
            pygame.draw.arc(surface, (120, 240, 210), (cx - 16, cy - 16, 32, 32), 2.0, 5.0, 3)
        elif elem == "Naturaleza":
            # Flor de esporas y hojas
            for ang in range(0, 360, 72):
                rad = math.radians(ang)
                px = cx + int(16 * math.cos(rad))
                py = cy + int(16 * math.sin(rad))
                pygame.draw.circle(surface, (60, 200, 90), (px, py), 10)
            pygame.draw.circle(surface, (255, 220, 60), (cx, cy), 8)
        elif elem == "Tierra":
            # Cristales rocosos monolíticos
            pygame.draw.polygon(surface, (160, 95, 45), [(cx - 20, cy + 24), (cx - 12, cy - 20), (cx, cy + 24)])
            pygame.draw.polygon(surface, (200, 130, 65), [(cx - 4, cy + 24), (cx + 8, cy - 32), (cx + 20, cy + 24)])
        else:
            # Metal / Vapor
            pygame.draw.circle(surface, (160, 175, 190), (cx, cy), 22, 4)
            pygame.draw.line(surface, (220, 230, 240), (cx - 16, cy), (cx + 16, cy), 4)
