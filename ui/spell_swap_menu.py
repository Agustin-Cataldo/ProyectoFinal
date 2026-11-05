"""
================================================================================
MÓDULO: ui/spell_swap_menu.py
RESPONSABILIDAD: Menú modal interactivo para la asignación y reemplazo de hechizos.
CONCEPTO ACADÉMICO: Interfaz Gráfica Modal, Gestión de Inventario Activo (Spell Slots).
================================================================================
Permite al jugador decidir explícitamente qué hacer al descubrir o seleccionar un nuevo hechizo:
1. Reemplazar Ranura 1 (Primaria - Clic Derecho / Tecla E)
2. Reemplazar Ranura 2 (Secundaria - Tecla Q)
3. No Reemplazar (Conservar los hechizos actuales intactos y descartar el nuevo)
"""

import math
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BRASS, COLOR_COPPER,
    COLOR_DARK_STONE, COLOR_GOLD, COLOR_WHITE, COLOR_STEAM,
    COLOR_MANA_BRIGHT, ELEMENT_COLORS, MANA_SPELL_COSTS
)

SPELL_DETAILS = {
    "Fuego": {
        "icon": "🔥",
        "title": "Meteorito Cataclísmico & Caldera Ígnea",
        "desc": "Dispara un colosal meteorito ígneo que desata una onda de choque sísmica al detonar, genera una caldera de lava hirviente en el suelo y dispersa 4 chispas ardientes rebotantes."
    },
    "Agua": {
        "icon": "🌊",
        "title": "Maremoto en Abanico & Burbujas Cautivas",
        "desc": "Despliega 3 olas oceánicas penetrantes en abanico combinadas con 3 orbes de agua cautiva que rastrean y persiguen fluidamente a los enemigos más cercanos (homing)."
    },
    "Viento": {
        "icon": "🌪️",
        "title": "Búmeran Ciclónico Gravitatorio",
        "desc": "Lanza un vórtice cortante que succiona enemigos a su vórtice, destruye proyectiles hostiles en su trayectoria y regresa volando hacia el jugador recargando +10 MP."
    },
    "Tierra": {
        "icon": "🪨",
        "title": "Fractura Tectónica & Monolitos Defensivos",
        "desc": "Terremoto frontal devastador que agrieta el terreno y levanta 4 monolitos de roca indestructibles que bloquean disparos y ataques enemigos."
    },
    "Trueno": {
        "icon": "⚡",
        "title": "Cadena de Relámpagos Bifurcados",
        "desc": "Arco voltaico instantáneo fractal que impacta al objetivo e inmediatamente se bifurca saltando entre hasta 5 enemigos encadenados con daño eléctrico."
    },
    "Naturaleza": {
        "icon": "🌿",
        "title": "Enredadera Parásita & Flor de Esporas",
        "desc": "Lanza zarcillos vivos que brotan en una flor de esporas drenadoras, atrapando a los enemigos e infundiendo +15 HP directamente a la vida del héroe."
    },
    "Luz": {
        "icon": "✨",
        "title": "Lanza Solar Celestial & Santuario Sagrado",
        "desc": "Lanza perforante de fotones que emite 8 rayos solares colaterales y engendra un santuario bendito en el suelo que sana +25 HP/s y aumenta el daño un +35%."
    },
    "Oscuridad": {
        "icon": "🌑",
        "title": "Agujero Negro & Singularidad Abisal",
        "desc": "Abre una singularidad gravitatoria de sala completa que devora y succiona a todos los enemigos antes de detonar en una implosión con robo de vida vampírico."
    },
    "Vapor": {
        "icon": "💨",
        "title": "Deflagración Neumática en 360°",
        "desc": "Onda de choque masiva de vapor a presión en 360° que empuja y aturde a los enemigos cercanos, disipa y refleja proyectiles, y otorga +35% de velocidad de escape."
    },
    "Vapor (Steampunk)": {
        "icon": "💨",
        "title": "Deflagración Neumática en 360°",
        "desc": "Onda de choque masiva de vapor a presión en 360° que empuja y aturde a los enemigos cercanos, disipa y refleja proyectiles, y otorga +35% de velocidad de escape."
    },
    "Metal": {
        "icon": "⚙️",
        "title": "Guillotinas Orbitantes & Sierras de Rebote",
        "desc": "Invoca 3 sierras cortantes dentadas que orbitan al héroe como escudo protector antes de dispararse en espiral y rebotar violentamente en los muros de la arena."
    }
}


class SpellSwapMenu:
    """Ventana emergente modal para reemplazar hechizos o descartar el nuevo."""

    def __init__(self, audio_system=None):
        self.audio_system = audio_system
        self.font_title = pygame.font.SysFont("Consolas", 24, bold=True)
        self.font_sub = pygame.font.SysFont("Consolas", 13)
        self.font_name = pygame.font.SysFont("Consolas", 16, bold=True)
        self.font_desc = pygame.font.SysFont("Consolas", 12)
        self.font_btn = pygame.font.SysFont("Consolas", 14, bold=True)

        self.new_spell = None
        self.current_spells = []

        # Dimensiones del modal central
        self.modal_w = 760
        self.modal_h = 520
        self.modal_x = (SCREEN_WIDTH - self.modal_w) // 2
        self.modal_y = (SCREEN_HEIGHT - self.modal_h) // 2

        # Rectángulos de botones
        btn_w = 220
        btn_h = 100
        gap = 18
        start_btn_x = self.modal_x + (self.modal_w - (3 * btn_w + 2 * gap)) // 2
        btn_y = self.modal_y + self.modal_h - btn_h - 25

        self.slot1_rect = pygame.Rect(start_btn_x, btn_y, btn_w, btn_h)
        self.slot2_rect = pygame.Rect(start_btn_x + btn_w + gap, btn_y, btn_w, btn_h)
        self.cancel_rect = pygame.Rect(start_btn_x + 2 * (btn_w + gap), btn_y, btn_w, btn_h)

        self.hovered_option = None
        self.anim_timer = 0.0

    def open(self, new_spell: str, current_spells: list):
        """Abre el modal con el nuevo hechizo descubierto y los hechizos actuales del jugador."""
        self.new_spell = new_spell
        self.current_spells = list(current_spells)
        self.hovered_option = None

    def handle_event(self, event: pygame.event.Event):
        """
        Procesa la selección del jugador:
        - Retorna ("SLOT_1", self.new_spell)
        - Retorna ("SLOT_2", self.new_spell)
        - Retorna ("CANCEL", None)
        - Retorna None si aún no se toma la decisión
        """
        mouse_pos = getattr(event, 'pos', pygame.mouse.get_pos())

        if event.type == pygame.MOUSEMOTION:
            old_hover = self.hovered_option
            if self.slot1_rect.collidepoint(mouse_pos):
                self.hovered_option = "SLOT_1"
            elif self.slot2_rect.collidepoint(mouse_pos):
                self.hovered_option = "SLOT_2"
            elif self.cancel_rect.collidepoint(mouse_pos):
                self.hovered_option = "CANCEL"
            else:
                self.hovered_option = None

            if self.hovered_option is not None and self.hovered_option != old_hover and self.audio_system:
                self.audio_system.play_sfx("ui_hover")

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.slot1_rect.collidepoint(mouse_pos):
                if self.audio_system:
                    self.audio_system.play_sfx("ui_select")
                return ("SLOT_1", self.new_spell)
            elif self.slot2_rect.collidepoint(mouse_pos):
                if self.audio_system:
                    self.audio_system.play_sfx("ui_select")
                return ("SLOT_2", self.new_spell)
            elif self.cancel_rect.collidepoint(mouse_pos):
                if self.audio_system:
                    self.audio_system.play_sfx("ui_select")
                return ("CANCEL", None)

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_1, pygame.K_KP1):
                if self.audio_system:
                    self.audio_system.play_sfx("ui_select")
                return ("SLOT_1", self.new_spell)
            elif event.key in (pygame.K_2, pygame.K_KP2):
                if self.audio_system:
                    self.audio_system.play_sfx("ui_select")
                return ("SLOT_2", self.new_spell)
            elif event.key in (pygame.K_3, pygame.K_KP3, pygame.K_ESCAPE, pygame.K_n):
                if self.audio_system:
                    self.audio_system.play_sfx("ui_select")
                return ("CANCEL", None)

        return None

    def draw(self, surface: pygame.Surface):
        """Dibuja el modal de gestión de hechizos."""
        if not self.new_spell:
            return

        self.anim_timer += 0.04
        mouse_pos = pygame.mouse.get_pos()

        # 1. Capa de oscurecimiento global
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 10, 14, 230))
        surface.blit(overlay, (0, 0))

        # 2. Marco principal del modal
        modal_rect = pygame.Rect(self.modal_x, self.modal_y, self.modal_w, self.modal_h)
        pygame.draw.rect(surface, (20, 22, 28), modal_rect, border_radius=10)
        pygame.draw.rect(surface, COLOR_BRASS, modal_rect, 3, border_radius=10)

        # 3. Encabezado gótico
        header_rect = pygame.Rect(self.modal_x, self.modal_y, self.modal_w, 48)
        pygame.draw.rect(surface, (14, 16, 20), header_rect, border_top_left_radius=10, border_top_right_radius=10)
        pygame.draw.rect(surface, COLOR_BRASS, header_rect, 1, border_top_left_radius=10, border_top_right_radius=10)

        t1 = self.font_title.render("✨ ASIGNACIÓN DE HECHIZO ELEMENTAL ✨", True, COLOR_GOLD)
        surface.blit(t1, t1.get_rect(center=(modal_rect.centerx, self.modal_y + 24)))

        sub_msg = "Has descubierto una nueva técnica mágica. Elige dónde equiparla o descártala sin modificar tus hechizos."
        t2 = self.font_sub.render(sub_msg, True, COLOR_STEAM)
        surface.blit(t2, t2.get_rect(center=(modal_rect.centerx, self.modal_y + 68)))

        # 4. Tarjeta del NUEVO HECHIZO
        spell_info = SPELL_DETAILS.get(self.new_spell, {
            "icon": "✨",
            "title": f"Técnica de {self.new_spell}",
            "desc": f"Despliega el poder arcano concentrado del elemento {self.new_spell}."
        })
        elem_color = ELEMENT_COLORS.get(self.new_spell, COLOR_GOLD)
        mana_cost = MANA_SPELL_COSTS.get(self.new_spell, 75)

        new_card_rect = pygame.Rect(self.modal_x + 35, self.modal_y + 92, self.modal_w - 70, 160)
        pygame.draw.rect(surface, (28, 30, 38), new_card_rect, border_radius=8)
        pygame.draw.rect(surface, elem_color, new_card_rect, 2, border_radius=8)

        # Título del nuevo hechizo
        new_tag = f"NUEVO HECHIZO: {spell_info['icon']} {self.new_spell.upper()} — {spell_info['title']}"
        new_tag_surf = self.font_name.render(new_tag, True, elem_color)
        surface.blit(new_tag_surf, (new_card_rect.x + 16, new_card_rect.y + 14))

        cost_txt = f"Costo: {mana_cost} MP"
        cost_surf = self.font_name.render(cost_txt, True, COLOR_MANA_BRIGHT)
        surface.blit(cost_surf, (new_card_rect.right - cost_surf.get_width() - 16, new_card_rect.y + 14))

        # Descripción con salto de línea automático
        desc_y = new_card_rect.y + 45
        words = spell_info["desc"].split(" ")
        line = ""
        for w in words:
            test_line = f"{line} {w}".strip()
            if self.font_desc.size(test_line)[0] < new_card_rect.width - 32:
                line = test_line
            else:
                surface.blit(self.font_desc.render(line, True, (220, 225, 235)), (new_card_rect.x + 16, desc_y))
                desc_y += 18
                line = w
        if line:
            surface.blit(self.font_desc.render(line, True, (220, 225, 235)), (new_card_rect.x + 16, desc_y))

        # 5. Opciones interactivas de asignación (Botones 1, 2 y 3)
        s1_spell = self.current_spells[0] if len(self.current_spells) > 0 else "Vacío"
        s2_spell = self.current_spells[1] if len(self.current_spells) > 1 else "Vacío"

        # --- BOTÓN 1: RANURA 1 ---
        is_s1_hov = self.slot1_rect.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (36, 38, 48) if is_s1_hov else (24, 26, 32), self.slot1_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD if is_s1_hov else (100, 105, 120), self.slot1_rect, 2 if is_s1_hov else 1, border_radius=6)

        t_btn1 = self.font_btn.render("[1] RANURA 1", True, COLOR_GOLD if is_s1_hov else COLOR_WHITE)
        surface.blit(t_btn1, t_btn1.get_rect(center=(self.slot1_rect.centerx, self.slot1_rect.y + 22)))

        t_sub1 = self.font_sub.render("(Clic Derecho / E)", True, COLOR_STEAM)
        surface.blit(t_sub1, t_sub1.get_rect(center=(self.slot1_rect.centerx, self.slot1_rect.y + 44)))

        t_cur1 = self.font_desc.render(f"Actual: {s1_spell}", True, ELEMENT_COLORS.get(s1_spell, (180, 180, 190)))
        surface.blit(t_cur1, t_cur1.get_rect(center=(self.slot1_rect.centerx, self.slot1_rect.y + 66)))

        t_act1 = self.font_desc.render("▶ Asignar / Reemplazar", True, (46, 204, 113) if is_s1_hov else (160, 165, 175))
        surface.blit(t_act1, t_act1.get_rect(center=(self.slot1_rect.centerx, self.slot1_rect.y + 84)))

        # --- BOTÓN 2: RANURA 2 ---
        is_s2_hov = self.slot2_rect.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (36, 38, 48) if is_s2_hov else (24, 26, 32), self.slot2_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD if is_s2_hov else (100, 105, 120), self.slot2_rect, 2 if is_s2_hov else 1, border_radius=6)

        t_btn2 = self.font_btn.render("[2] RANURA 2", True, COLOR_GOLD if is_s2_hov else COLOR_WHITE)
        surface.blit(t_btn2, t_btn2.get_rect(center=(self.slot2_rect.centerx, self.slot2_rect.y + 22)))

        t_sub2 = self.font_sub.render("(Tecla Q)", True, COLOR_STEAM)
        surface.blit(t_sub2, t_sub2.get_rect(center=(self.slot2_rect.centerx, self.slot2_rect.y + 44)))

        t_cur2 = self.font_desc.render(f"Actual: {s2_spell}", True, ELEMENT_COLORS.get(s2_spell, (180, 180, 190)))
        surface.blit(t_cur2, t_cur2.get_rect(center=(self.slot2_rect.centerx, self.slot2_rect.y + 66)))

        t_act2 = self.font_desc.render("▶ Asignar / Reemplazar", True, (46, 204, 113) if is_s2_hov else (160, 165, 175))
        surface.blit(t_act2, t_act2.get_rect(center=(self.slot2_rect.centerx, self.slot2_rect.y + 84)))

        # --- BOTÓN 3: NO REEMPLAZAR (DES броси / CONSERVAR) ---
        is_c_hov = self.cancel_rect.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (48, 30, 32) if is_c_hov else (28, 22, 24), self.cancel_rect, border_radius=6)
        pygame.draw.rect(surface, (231, 76, 60) if is_c_hov else (140, 70, 70), self.cancel_rect, 2 if is_c_hov else 1, border_radius=6)

        t_btn3 = self.font_btn.render("[3] NO REEMPLAZAR", True, (255, 120, 120) if is_c_hov else (230, 100, 100))
        surface.blit(t_btn3, t_btn3.get_rect(center=(self.cancel_rect.centerx, self.cancel_rect.y + 22)))

        t_sub3 = self.font_sub.render("([ESC] o Tecla 3)", True, COLOR_STEAM)
        surface.blit(t_sub3, t_sub3.get_rect(center=(self.cancel_rect.centerx, self.cancel_rect.y + 44)))

        t_cur3 = self.font_desc.render("Conservar actuales", True, (210, 215, 225))
        surface.blit(t_cur3, t_cur3.get_rect(center=(self.cancel_rect.centerx, self.cancel_rect.y + 66)))

        t_act3 = self.font_desc.render("✖ Descartar Nuevo Hechizo", True, (231, 76, 60))
        surface.blit(t_act3, t_act3.get_rect(center=(self.cancel_rect.centerx, self.cancel_rect.y + 84)))
