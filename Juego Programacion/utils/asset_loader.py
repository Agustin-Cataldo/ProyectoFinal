"""
================================================================================
MÓDULO: utils/asset_loader.py
RESPONSABILIDAD: Generación y carga resiliente de recursos visuales Pixel Art.
CONCEPTO ACADÉMICO: Patrón Factory / Procedural Asset Generation.
================================================================================
Para garantizar que el proyecto se ejecute de inmediato sin riesgo de "FileNotFoundError"
en la máquina del tribunal, este módulo sintetiza gráficos Pixel Art puros mediante
superficies de Pygame, respetando la estética Steampunk, fantasía medieval y elemental.
"""

import math
import pygame
from settings import (
    COLOR_BLACK, COLOR_BRASS, COLOR_COPPER, COLOR_DARK_STONE, COLOR_FLOOR,
    COLOR_GOLD, COLOR_STEAM, COLOR_WALL, COLOR_WHITE, ELEMENT_COLORS
)


class AssetLoader:
    """
    Fábrica y repositorio en memoria de texturas y sprites pixel art.
    Implementa caché en diccionario para evitar regenerar superficies en cada frame.
    """
    _cache = {}

    @classmethod
    def get_shadow_sprite(cls, rx: int = 18, ry: int = 8) -> pygame.Surface:
        """Genera una sombra elíptica suave con degradado de opacidad para dar profundidad 2.5D."""
        cache_key = f"shadow_{rx}_{ry}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        w, h = rx * 2 + 4, ry * 2 + 4
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        # Capas concéntricas para difuminado suave
        for step in range(4):
            cur_rx = rx - step * (rx // 5)
            cur_ry = ry - step * (ry // 5)
            if cur_rx > 0 and cur_ry > 0:
                alpha = int(35 + step * 25)
                rect = pygame.Rect(w // 2 - cur_rx, h // 2 - cur_ry, cur_rx * 2, cur_ry * 2)
                pygame.draw.ellipse(surf, (0, 0, 0, alpha), rect)

        cls._cache[cache_key] = surf
        return surf


    @classmethod
    def get_torch_glow_sprite(cls, radius: int = 65, pulse_phase: float = 0.0) -> pygame.Surface:
        """Genera el halo de luz cálida de una antorcha con parpadeo dinámico."""
        # Cuantizar el pulso en 8 pasos para aprovechar la caché sin consumir memoria
        phase_bucket = int((pulse_phase % (2 * math.pi)) / (math.pi / 4))
        cache_key = f"torch_glow_{radius}_{phase_bucket}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        w = radius * 2
        surf = pygame.Surface((w, w), pygame.SRCALPHA)
        center = radius

        # Gradiente radial suave
        for r in range(radius, 0, -3):
            ratio = 1.0 - (r / radius)
            alpha = int(45 * (ratio ** 1.8))
            # Tonalidad cálida: centro dorado/ámbar, bordes naranja oscuro
            col = (255, int(150 + 60 * ratio), int(30 + 100 * ratio), alpha)
            pygame.draw.circle(surf, col, (center, center), r)

        cls._cache[cache_key] = surf
        return surf


    @classmethod
    def get_player_sprite(cls, angle=0) -> pygame.Surface:
        """
        Genera el sprite del héroe Steampunk: armadura de cobre, engranaje en el pecho,
        gafas protectoras victorianas y capa medieval.
        """
        cache_key = f"player_{int(angle)}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        # Superficie de 48x48 píxeles con transparencia
        size = 48
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        # Capa medieval (azul oscuro / cuero)
        pygame.draw.circle(surf, (30, 40, 60), (center - 4, center), 15)

        # Coraza de bronce / cobre Steampunk
        pygame.draw.circle(surf, COLOR_COPPER, (center, center), 12)
        pygame.draw.circle(surf, COLOR_BRASS, (center, center), 10)

        # Engranaje o núcleo central de vapor (brillo cian)
        pygame.draw.circle(surf, (0, 206, 209), (center, center), 4)

        # Casco / Cabeza con visor
        pygame.draw.circle(surf, COLOR_DARK_STONE, (center + 4, center), 7)
        # Gafas Steampunk de latón
        pygame.draw.circle(surf, COLOR_BRASS, (center + 6, center - 2), 3)
        pygame.draw.circle(surf, (255, 140, 0), (center + 6, center - 2), 2)  # Lente ámbar

        # Rotar hacia la dirección donde apunta el jugador
        rotated_surf = pygame.transform.rotate(surf, -angle)
        cls._cache[cache_key] = rotated_surf
        return rotated_surf

    @classmethod
    def get_sword_sprite(cls) -> pygame.Surface:
        """Compatibilidad con versiones previas: invoca get_weapon_sprite('sword')."""
        return cls.get_weapon_sprite("sword")

    @classmethod
    def get_weapon_sprite(cls, weapon_type: str = "sword") -> pygame.Surface:
        """
        Genera el sprite procedural Pixel Art del arma medieval seleccionada:
        - sword: Espada de Acero Templado (hoja afilada brillante, guarda dorada)
        - axe: Gran Hacha Bárbara (doble filo colosal con filo carmesí)
        - mace: Maza Sagrada de Guerra (cabeza estriada con resplandor celestial)
        - daggers: Dagas Gemelas de Asesino (hojas curvas con veneno esmeralda)
        - crossbow: Ballesta Pesada de Repetición (madera oscura y arco de acero)
        - scythe: Guadaña Espectral de Almas (filo en media luna espectral violeta)
        - staff: Bastón Rúnico de Éter (vara noble con orbe zafiro pulsante)
        """
        cache_key = f"weapon_art_{weapon_type}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        if weapon_type == "axe":
            # Gran Hacha Bárbara de Doble Filo
            w, h = 48, 28
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            # Mango de fresno rústico
            pygame.draw.rect(surf, (90, 50, 25), (4, 12, 40, 5))
            pygame.draw.rect(surf, (50, 25, 10), (4, 12, 10, 5))
            # Hojas gemelas de acero de batalla
            blade_color = (180, 185, 195)
            edge_color = (220, 50, 50)
            # Hoja superior
            pygame.draw.polygon(surf, blade_color, [(30, 10), (46, 2), (40, 14), (32, 14)])
            pygame.draw.polygon(surf, edge_color, [(44, 2), (46, 2), (40, 14), (38, 14)])
            # Hoja inferior
            pygame.draw.polygon(surf, blade_color, [(30, 18), (46, 26), (40, 14), (32, 14)])
            pygame.draw.polygon(surf, edge_color, [(44, 26), (46, 26), (40, 14), (38, 14)])
            # Remache y anillo de hierro central
            pygame.draw.circle(surf, (60, 65, 75), (34, 14), 5)
            pygame.draw.circle(surf, COLOR_GOLD, (34, 14), 2)

        elif weapon_type == "mace":
            # Maza Sagrada de Guerra
            w, h = 44, 22
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            # Mango metálico bendecido
            pygame.draw.rect(surf, (140, 110, 50), (4, 9, 30, 5))
            pygame.draw.circle(surf, COLOR_GOLD, (4, 11), 3)
            # Cabeza estrellada de la maza
            pygame.draw.circle(surf, (220, 190, 80), (34, 11), 8)
            pygame.draw.circle(surf, (255, 245, 180), (34, 11), 5)
            # Púas sagradas en cruz
            pygame.draw.line(surf, COLOR_GOLD, (34, 1), (34, 21), 3)
            pygame.draw.line(surf, COLOR_GOLD, (24, 11), (44, 11), 3)
            # Runa solar blanca
            pygame.draw.circle(surf, COLOR_WHITE, (34, 11), 2)

        elif weapon_type == "daggers":
            # Dagas Gemelas de Asesino
            w, h = 38, 20
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            # Daga 1 (principal)
            pygame.draw.rect(surf, (40, 40, 45), (4, 6, 8, 3))  # Empuñadura
            pygame.draw.polygon(surf, (160, 170, 180), [(12, 6), (34, 4), (36, 7), (12, 8)])
            pygame.draw.line(surf, (46, 204, 113), (16, 5), (35, 5), 2)  # Filo envenenado
            # Daga 2 (secundaria en ángulo inverso)
            pygame.draw.rect(surf, (40, 40, 45), (2, 13, 8, 3))
            pygame.draw.polygon(surf, (140, 150, 160), [(10, 13), (30, 11), (32, 14), (10, 15)])
            pygame.draw.line(surf, (39, 174, 96), (14, 12), (31, 12), 2)

        elif weapon_type == "crossbow":
            # Ballesta Pesada de Repetición
            w, h = 42, 28
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            # Cuerpo de madera noble
            pygame.draw.rect(surf, (95, 55, 30), (6, 12, 30, 5))
            pygame.draw.rect(surf, (60, 35, 15), (6, 12, 10, 7))  # Culata
            # Arco transversal de hierro
            pygame.draw.arc(surf, (150, 155, 165), pygame.Rect(18, 2, 20, 24), -1.2, 1.2, 4)
            # Cuerda tensada
            pygame.draw.line(surf, (220, 225, 230), (22, 4), (16, 14), 1)
            pygame.draw.line(surf, (220, 225, 230), (22, 24), (16, 14), 1)
            # Virote listo
            pygame.draw.line(surf, COLOR_BRASS, (16, 14), (38, 14), 2)
            pygame.draw.polygon(surf, (240, 240, 255), [(38, 14), (34, 12), (34, 16)])

        elif weapon_type == "scythe":
            # Guadaña Espectral de Almas
            w, h = 50, 34
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            # Astil largo de ébano oscuro
            pygame.draw.line(surf, (40, 35, 50), (4, 17), (40, 17), 4)
            pygame.draw.circle(surf, (142, 68, 173), (40, 17), 4)
            # Filo en media luna espectral violeta
            scythe_blade = [(40, 17), (46, 6), (42, 2), (28, 4), (40, 12)]
            pygame.draw.polygon(surf, (180, 140, 220), scythe_blade)
            pygame.draw.polygon(surf, (142, 68, 173), scythe_blade, 1)
            # Borde afilado resplandeciente
            pygame.draw.lines(surf, (255, 220, 255), False, [(42, 2), (28, 4), (38, 10)], 2)

        elif weapon_type == "staff":
            # Bastón Rúnico de Éter
            w, h = 46, 20
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            # Vara de madera noble pulida
            pygame.draw.line(surf, (100, 70, 45), (4, 10), (34, 10), 4)
            pygame.draw.rect(surf, COLOR_GOLD, (30, 7, 5, 6))  # Engarce
            # Orbe de cristal zafiro pulsante
            pygame.draw.circle(surf, (41, 128, 185), (38, 10), 7)
            pygame.draw.circle(surf, (52, 152, 219), (38, 10), 5)
            pygame.draw.circle(surf, COLOR_WHITE, (37, 8), 2)
            # Anillo de runas en órbita
            pygame.draw.circle(surf, (155, 89, 182), (38, 10), 9, 1)

        elif weapon_type == "greatsword":
            # Gran Espadón Rúnico de Dos Manos (Caballero Rúnico)
            w, h = 54, 20
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            # Hoja ancha de acero con runas grabadas
            blade_pts = [(14, 5), (46, 5), (52, 10), (46, 15), (14, 15)]
            pygame.draw.polygon(surf, (185, 195, 210), blade_pts)
            pygame.draw.polygon(surf, (70, 130, 180), blade_pts, 1)
            # Canal rúnico zafiro resplandeciente
            pygame.draw.line(surf, (52, 152, 219), (16, 10), (48, 10), 3)
            pygame.draw.line(surf, COLOR_WHITE, (18, 10), (46, 10), 1)
            # Guarda pesada de hierro y zafiros
            pygame.draw.rect(surf, (80, 85, 95), (10, 2, 5, 16))
            pygame.draw.circle(surf, (52, 152, 219), (12, 10), 3)
            # Empuñadura larga a dos manos y pomo pesado
            pygame.draw.rect(surf, (45, 30, 20), (2, 8, 9, 4))
            pygame.draw.circle(surf, COLOR_GOLD, (2, 10), 3)

        elif weapon_type == "flask":
            # Frascos Químicos de Miasma y Fuego Griego (Alquimista)
            w, h = 36, 22
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            # Matraz de vidrio alquímico
            pygame.draw.polygon(surf, (200, 240, 255), [(16, 4), (22, 4), (26, 17), (12, 17)])
            pygame.draw.polygon(surf, (46, 204, 113), [(17, 7), (21, 7), (25, 16), (13, 16)])  # Ácido verde
            # Burbujas incandescentes
            pygame.draw.circle(surf, (241, 196, 15), (19, 12), 3)
            pygame.draw.circle(surf, COLOR_WHITE, (18, 10), 1)
            # Cuello con corcho y cinta de cuero
            pygame.draw.rect(surf, (140, 90, 50), (17, 1, 4, 3))
            # Segundo vial de fuego
            pygame.draw.circle(surf, (231, 76, 60), (9, 13), 5)
            pygame.draw.circle(surf, (255, 160, 40), (9, 13), 3)

        elif weapon_type == "fists":
            # Guanteletes de Hierro de Impacto (Monje Asceta)
            w, h = 38, 22
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            # Guantelete derecho (principal)
            pygame.draw.rect(surf, (110, 115, 125), (14, 4, 18, 7), border_radius=3)
            pygame.draw.rect(surf, COLOR_BRASS, (14, 4, 6, 7))  # Refuerzo nudillos
            pygame.draw.circle(surf, (241, 196, 15), (28, 7), 3)  # Púa de impacto
            # Guantelete izquierdo (retrasado)
            pygame.draw.rect(surf, (90, 95, 105), (6, 12, 16, 7), border_radius=3)
            pygame.draw.rect(surf, COLOR_BRASS, (6, 12, 5, 7))
            pygame.draw.circle(surf, (230, 126, 34), (18, 15), 2)

        elif weapon_type == "cannon":
            # Cañón Portátil de Vapor y Metralla (Artificiero)
            w, h = 48, 24
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            # Tubo principal del cañón de bronce
            pygame.draw.rect(surf, COLOR_BRASS, (10, 6, 32, 12), border_radius=2)
            pygame.draw.rect(surf, (140, 100, 20), (10, 6, 32, 12), 1)
            # Boca del cañón con recámara oscura
            pygame.draw.rect(surf, (50, 45, 40), (38, 5, 6, 14), border_radius=1)
            pygame.draw.circle(surf, (20, 20, 22), (41, 12), 4)
            # Válvula de vapor superior y manómetro
            pygame.draw.rect(surf, COLOR_COPPER, (18, 2, 6, 4))
            pygame.draw.circle(surf, COLOR_WHITE, (21, 2), 2)
            # Empuñadura y culata de hierro
            pygame.draw.rect(surf, (60, 65, 70), (4, 9, 8, 9))

        elif weapon_type == "totem":
            # Tótem Espiritual y Garras (Chamán de las Bestias)
            w, h = 48, 24
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            # Mástil de madera tallada ancestral
            pygame.draw.line(surf, (120, 75, 40), (4, 12), (36, 12), 5)
            # Cabeza de tótem con forma de oso/lobo
            pygame.draw.rect(surf, (80, 50, 25), (30, 4, 14, 16), border_radius=3)
            # Ojos espirituales turquesas brillantes
            pygame.draw.circle(surf, (26, 188, 156), (36, 8), 2)
            pygame.draw.circle(surf, (26, 188, 156), (36, 16), 2)
            pygame.draw.circle(surf, COLOR_WHITE, (36, 8), 1)
            pygame.draw.circle(surf, COLOR_WHITE, (36, 16), 1)
            # Plumas y runas de invocación
            pygame.draw.polygon(surf, (241, 196, 15), [(24, 2), (28, 8), (22, 6)])

        elif weapon_type == "flail":
            # Mangual Dentado de Cadenas (Inquisidor de Sangre)
            w, h = 46, 26
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            # Mango de madera reforzada
            pygame.draw.line(surf, (90, 50, 30), (4, 13), (20, 13), 4)
            pygame.draw.circle(surf, COLOR_BRASS, (20, 13), 3)
            # Eslabones de cadena de hierro
            for cx in [24, 29, 34]:
                pygame.draw.circle(surf, (160, 165, 175), (cx, 13), 3, 1)
            # Bola pesada con púas ensangrentadas
            pygame.draw.circle(surf, (70, 75, 85), (38, 13), 7)
            pygame.draw.circle(surf, (192, 57, 43), (38, 13), 5)
            # Púas metálicas
            for ang in [0, 0.78, 1.57, 2.35, 3.14, 3.92, 4.71, 5.49]:
                px = 38 + int(math.cos(ang) * 9)
                py = 13 + int(math.sin(ang) * 9)
                pygame.draw.line(surf, (200, 205, 215), (38, 13), (px, py), 2)

        else:
            # Espada de Acero Templado (Default Medieval)
            w, h = 44, 14
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            blade_points = [(12, 4), (38, 4), (43, 7), (38, 10), (12, 10)]
            pygame.draw.polygon(surf, (200, 205, 215), blade_points)
            pygame.draw.line(surf, COLOR_WHITE, (14, 7), (40, 7), 2)
            # Guarda de oro noble
            pygame.draw.rect(surf, COLOR_GOLD, (9, 2, 4, 10))
            # Mango de cuero oscuro y pomo de latón
            pygame.draw.rect(surf, (80, 45, 20), (3, 5, 7, 4))
            pygame.draw.circle(surf, COLOR_BRASS, (2, 7), 3)

        cls._cache[cache_key] = surf
        return surf


    @classmethod
    def get_crossbow_bolt_sprite(cls, angle=0) -> pygame.Surface:
        """Genera el proyectil de saeta / virote de ballesta afilada."""
        cache_key = f"bolt_{int(angle)}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        w, h = 24, 8
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        # Eje de madera
        pygame.draw.rect(surf, (120, 80, 40), (2, 3, 16, 2))
        # Punta de acero
        pygame.draw.polygon(surf, (230, 235, 245), [(18, 1), (23, 4), (18, 7)])
        # Emplumado trasero de plumas rojas
        pygame.draw.polygon(surf, (214, 48, 49), [(1, 1), (5, 4), (1, 4)])
        pygame.draw.polygon(surf, (214, 48, 49), [(1, 7), (5, 4), (1, 4)])

        rotated_surf = pygame.transform.rotate(surf, -angle)
        cls._cache[cache_key] = rotated_surf
        return rotated_surf

    @classmethod
    def get_slash_arc_sprite(cls, radius=80, angle_span=110, color=None) -> pygame.Surface:
        """
        Genera el efecto visual de barrido semicircular (Slash Arc) del ataque Hack & Slash.
        """
        if color is None:
            color = (230, 240, 255)  # Brillo de acero/vapor por defecto

        cache_key = f"slash_{radius}_{angle_span}_{color}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        size = radius * 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (radius, radius)

        # Dibujar arco curvado con degradado visual
        rect = pygame.Rect(0, 0, size, size)
        start_rad = math.radians(-angle_span / 2)
        end_rad = math.radians(angle_span / 2)

        # Arco principal brillante
        pygame.draw.arc(surf, color, rect, start_rad, end_rad, 8)
        # Línea central nítida
        pygame.draw.arc(surf, COLOR_WHITE, rect.inflate(-4, -4), start_rad, end_rad, 3)

        cls._cache[cache_key] = surf
        return surf


    @classmethod
    def get_common_enemy_sprite(cls, angle=0) -> pygame.Surface:
        """Genera el sprite del Autómata Minero común."""
        return cls.get_miner_sprite(angle)

    @classmethod
    def get_miner_sprite(cls, angle=0) -> pygame.Surface:
        """Autómata Minero Medieval: armadura gótica de bronce oscuro, yelmo con visera y ojos ámbar incandescentes."""
        cache_key = f"miner_{int(angle)}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        size = 42
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        # Capa / hombreras de hierro oscuro
        pygame.draw.circle(surf, (45, 42, 40), (center, center), 14)
        pygame.draw.circle(surf, (75, 70, 65), (center, center), 12)
        # Coraza de bronce envejecido con remaches
        pygame.draw.circle(surf, COLOR_BRASS, (center, center), 9)
        pygame.draw.circle(surf, (160, 120, 30), (center, center), 9, 2)

        # Cabeza / Yelmo blindado con visera
        pygame.draw.circle(surf, (210, 205, 195), (center + 4, center), 7)
        pygame.draw.rect(surf, (40, 38, 42), (center + 3, center - 4, 6, 8), border_radius=2)
        # Ojos incandescentes de fuego mecánico
        pygame.draw.circle(surf, (255, 120, 0), (center + 6, center - 2), 2)
        pygame.draw.circle(surf, (255, 120, 0), (center + 6, center + 2), 2)
        pygame.draw.circle(surf, (255, 240, 150), (center + 7, center - 2), 1)
        pygame.draw.circle(surf, (255, 240, 150), (center + 7, center + 2), 1)

        # Chimenea de escape de vapor con boquilla de cobre
        pygame.draw.rect(surf, COLOR_COPPER, (center - 13, center - 5, 5, 10), border_radius=2)
        pygame.draw.circle(surf, (255, 80, 20), (center - 13, center), 2)

        rotated_surf = pygame.transform.rotate(surf, -angle)
        cls._cache[cache_key] = rotated_surf
        return rotated_surf

    @classmethod
    def get_charger_sprite(cls, angle=0, is_charging=False) -> pygame.Surface:
        """Autómata Embestidor: equipado con ariete frontal blindado y caldera reforzada."""
        cache_key = f"charger_{int(angle)}_{is_charging}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        size = 46
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        # Caldera (rojo incandescente si está en carga, cobre si normal)
        boiler_col = (245, 40, 25) if is_charging else COLOR_COPPER
        core_col = (255, 210, 50) if is_charging else COLOR_DARK_STONE
        pygame.draw.circle(surf, (50, 48, 55), (center, center), 16)
        pygame.draw.circle(surf, boiler_col, (center, center), 14)
        pygame.draw.circle(surf, core_col, (center, center), 9)

        # Ariete/Taladro frontal prominente con púas de choque
        piston_col = (255, 255, 255) if is_charging else (200, 205, 215)
        pygame.draw.polygon(surf, piston_col, [(center + 4, center - 8), (center + 21, center), (center + 4, center + 8)])
        pygame.draw.polygon(surf, (120, 125, 135), [(center + 4, center - 8), (center + 21, center), (center + 4, center + 8)], 2)

        # Doble chimenea humeante con tapas de bronce
        pygame.draw.rect(surf, (50, 50, 55), (center - 15, center - 9, 6, 6), border_radius=1)
        pygame.draw.rect(surf, (50, 50, 55), (center - 15, center + 3, 6, 6), border_radius=1)
        pygame.draw.circle(surf, COLOR_BRASS, (center - 15, center - 6), 2)
        pygame.draw.circle(surf, COLOR_BRASS, (center - 15, center + 6), 2)

        rotated_surf = pygame.transform.rotate(surf, -angle)
        cls._cache[cache_key] = rotated_surf
        return rotated_surf

    @classmethod
    def get_sniper_sprite(cls, angle=0) -> pygame.Surface:
        """Tirador de Vapor / Ballestero: capa oscura rasgada, ballesta mecánica y lente óptica."""
        cache_key = f"sniper_{int(angle)}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        size = 40
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        # Capa oscura rasgada
        pygame.draw.circle(surf, (30, 28, 38), (center - 3, center), 11)
        # Cráneo / Casco metálico
        pygame.draw.circle(surf, (225, 225, 215), (center - 1, center), 8)
        # Gafas telescópicas steampunk
        pygame.draw.circle(surf, COLOR_BRASS, (center + 4, center - 2), 4)
        pygame.draw.circle(surf, (0, 255, 230), (center + 4, center - 2), 2)
        pygame.draw.circle(surf, COLOR_WHITE, (center + 5, center - 3), 1)

        # Ballesta mecánica frontal con tensor doble
        pygame.draw.line(surf, COLOR_BRASS, (center + 2, center - 9), (center + 2, center + 9), 3)
        pygame.draw.line(surf, (130, 75, 30), (center - 2, center), (center + 14, center), 3)
        pygame.draw.polygon(surf, (240, 240, 255), [(center + 14, center), (center + 11, center - 2), (center + 11, center + 2)])

        rotated_surf = pygame.transform.rotate(surf, -angle)
        cls._cache[cache_key] = rotated_surf
        return rotated_surf

    @classmethod
    def get_tank_sprite(cls, angle=0) -> pygame.Surface:
        """Autómata Demoledor Pesado: acorazado con placas de hierro góticas y remaches."""
        cache_key = f"tank_{int(angle)}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        size = 56
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        # Chasis reforzado de acero oscuro con remaches
        pygame.draw.rect(surf, (45, 48, 56), (center - 20, center - 20, 40, 40), border_radius=7)
        pygame.draw.rect(surf, COLOR_BRASS, (center - 20, center - 20, 40, 40), 3, border_radius=7)

        # Placas protectoras de oruga en laterales
        pygame.draw.rect(surf, (30, 32, 38), (center - 22, center - 22, 10, 44), border_radius=3)

        # Torreta central blindada
        pygame.draw.circle(surf, COLOR_COPPER, (center, center), 13)
        pygame.draw.circle(surf, (230, 60, 40), (center, center), 7)
        pygame.draw.circle(surf, (255, 230, 100), (center, center), 3)

        # Martillo o escudo frontal titánico
        pygame.draw.rect(surf, (180, 185, 195), (center + 10, center - 16, 9, 32), border_radius=2)
        pygame.draw.line(surf, COLOR_GOLD, (center + 10, center), (center + 18, center), 2)

        rotated_surf = pygame.transform.rotate(surf, -angle)
        cls._cache[cache_key] = rotated_surf
        return rotated_surf

    @classmethod
    def get_drone_sprite(cls, pulse=0.0) -> pygame.Surface:
        """Dron Volador a Vapor: alas mecánicas batientes y ojo giroscópico."""
        size = 34
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        # Núcleo esférico
        pygame.draw.circle(surf, COLOR_DARK_STONE, (center, center), 7)
        pygame.draw.circle(surf, (0, 255, 200), (center, center), 4)

        # Alas mecánicas de cobre pulsantes
        wing_span = int(9 + 3 * math.sin(pulse * 2.0))
        pygame.draw.line(surf, COLOR_COPPER, (center, center - 4), (center, center - 4 - wing_span), 2)
        pygame.draw.line(surf, COLOR_COPPER, (center, center + 4), (center, center + 4 + wing_span), 2)
        pygame.draw.line(surf, COLOR_BRASS, (center - 3, center - 2 - wing_span), (center + 3, center - 2 - wing_span), 2)
        pygame.draw.line(surf, COLOR_BRASS, (center - 3, center + 2 + wing_span), (center + 3, center + 2 + wing_span), 2)

        return surf

    @classmethod
    def get_tank_sprite(cls, angle=0) -> pygame.Surface:
        """Autómata Demoledor Pesado: acorazado con placas de hierro y remaches."""
        cache_key = f"tank_{int(angle)}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        size = 52
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        # Chasis reforzado de acero oscuro
        pygame.draw.rect(surf, (55, 60, 70), (center - 18, center - 18, 36, 36), border_radius=6)
        pygame.draw.rect(surf, COLOR_BRASS, (center - 18, center - 18, 36, 36), 2, border_radius=6)

        # Torreta central
        pygame.draw.circle(surf, COLOR_COPPER, (center, center), 11)
        pygame.draw.circle(surf, (220, 50, 40), (center, center), 5)  # Núcleo de calor

        # Martillo o placa frontal
        pygame.draw.rect(surf, (160, 165, 175), (center + 8, center - 14, 8, 28))

        rotated_surf = pygame.transform.rotate(surf, -angle)
        cls._cache[cache_key] = rotated_surf
        return rotated_surf

    @classmethod
    def get_minion_sprite(cls, angle=0) -> pygame.Surface:
        """Mini-Autómata invocado por el Nigromante: frágil pero rápido."""
        cache_key = f"minion_{int(angle)}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        size = 24
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        pygame.draw.circle(surf, (120, 120, 110), (center, center), 7)
        pygame.draw.circle(surf, (40, 220, 80), (center + 2, center - 1), 2)
        rotated_surf = pygame.transform.rotate(surf, -angle)
        cls._cache[cache_key] = rotated_surf
        return rotated_surf

    @classmethod
    def get_bombardier_sprite(cls, angle=0) -> pygame.Surface:
        """Artificiero de Relojería / Bombardero: caldera trasera con bombas y cañón mortero frontal."""
        cache_key = f"bombardier_{int(angle)}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        size = 46
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        # Mochila / Caldera de vapor y depósito de municiones
        pygame.draw.circle(surf, (45, 42, 40), (center - 6, center), 14)
        pygame.draw.circle(surf, COLOR_COPPER, (center - 7, center), 10)
        pygame.draw.circle(surf, (255, 100, 20), (center - 8, center), 4)

        # Chimenea de escape de vapor
        pygame.draw.rect(surf, (50, 48, 55), (center - 15, center - 6, 6, 12), border_radius=2)
        pygame.draw.circle(surf, COLOR_BRASS, (center - 14, center), 2)

        # Torso con coraza de latón remachada
        pygame.draw.circle(surf, COLOR_BRASS, (center + 1, center), 9)
        pygame.draw.circle(surf, (150, 110, 20), (center + 1, center), 9, 2)

        # Yelmo blindado con monóculo óptico
        pygame.draw.circle(surf, (180, 185, 195), (center + 4, center), 6)
        pygame.draw.circle(surf, (255, 180, 0), (center + 6, center - 2), 3)
        pygame.draw.circle(surf, COLOR_WHITE, (center + 7, center - 2), 1)

        # Mortero / Cañón de brazo frontal lanzador de bombas
        pygame.draw.rect(surf, (70, 75, 85), (center + 5, center + 2, 13, 7), border_radius=2)
        pygame.draw.rect(surf, COLOR_BRASS, (center + 14, center + 1, 4, 9), border_radius=1)

        rotated_surf = pygame.transform.rotate(surf, -angle)
        cls._cache[cache_key] = rotated_surf
        return rotated_surf

    @classmethod
    def get_plague_doctor_sprite(cls, angle=0) -> pygame.Surface:
        """Médico de la Peste Alquímico: túnica de cuero oscuro, máscara picuda y viales venenosos."""
        cache_key = f"plague_doc_{int(angle)}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        size = 46
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        # Túnica y esclavina de cuero oscuro desgastado
        pygame.draw.circle(surf, (24, 25, 30), (center - 2, center), 15)
        pygame.draw.circle(surf, (42, 45, 52), (center - 2, center), 11)

        # Cinturón de reactivos y viales con ácido esmeralda
        pygame.draw.circle(surf, (46, 204, 113), (center - 8, center - 7), 3)
        pygame.draw.circle(surf, (39, 174, 96), (center - 8, center + 7), 3)
        pygame.draw.circle(surf, (155, 89, 182), (center - 11, center), 3)

        # Cabeza con máscara de pico icónica
        pygame.draw.circle(surf, (20, 20, 24), (center + 3, center), 8)
        beak_pts = [(center + 4, center - 4), (center + 18, center), (center + 4, center + 4)]
        pygame.draw.polygon(surf, (215, 205, 185), beak_pts)
        pygame.draw.polygon(surf, (130, 120, 105), beak_pts, 1)

        # Lentes redondas de latón con brillo verde alquímico
        pygame.draw.circle(surf, COLOR_BRASS, (center + 5, center - 3), 4)
        pygame.draw.circle(surf, (46, 204, 113), (center + 5, center - 3), 2)
        pygame.draw.circle(surf, COLOR_WHITE, (center + 6, center - 3), 1)

        # Bastón con pomo de matraz químico
        pygame.draw.line(surf, (90, 60, 30), (center + 2, center + 6), (center + 14, center + 12), 2)
        pygame.draw.circle(surf, (46, 204, 113), (center + 15, center + 13), 3)

        rotated_surf = pygame.transform.rotate(surf, -angle)
        cls._cache[cache_key] = rotated_surf
        return rotated_surf

    @classmethod
    def get_shield_guardian_sprite(cls, angle=0) -> pygame.Surface:
        """Guardián de Escudo de Latón: blindaje pesado con escudo torre reforzado al frente."""
        cache_key = f"shield_guardian_{int(angle)}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        size = 52
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        # Chasis acorazado y hombreras góticas
        pygame.draw.circle(surf, (48, 52, 60), (center - 4, center), 15)
        pygame.draw.circle(surf, (80, 85, 96), (center - 4, center), 12)
        pygame.draw.circle(surf, COLOR_BRASS, (center - 4, center), 8)

        # Yelmo de caballero con hendidura visor
        pygame.draw.circle(surf, (190, 195, 205), (center + 2, center), 7)
        pygame.draw.line(surf, (255, 140, 20), (center + 4, center - 2), (center + 4, center + 2), 2)

        # Escudo Torre Frontal de Latón masivo
        shield_rect = pygame.Rect(center + 8, center - 15, 7, 30)
        pygame.draw.rect(surf, COLOR_BRASS, shield_rect, border_radius=3)
        pygame.draw.rect(surf, (150, 105, 20), shield_rect, 2, border_radius=3)
        pygame.draw.line(surf, COLOR_COPPER, (center + 11, center - 10), (center + 11, center + 10), 2)
        pygame.draw.line(surf, COLOR_COPPER, (center + 9, center), (center + 13, center), 2)
        pygame.draw.circle(surf, COLOR_GOLD, (center + 11, center), 2)

        rotated_surf = pygame.transform.rotate(surf, -angle)
        cls._cache[cache_key] = rotated_surf
        return rotated_surf

    @classmethod
    def get_cultist_sprite(cls, angle=0, pulse=0.0) -> pygame.Surface:
        """Cultista de la Forja Arcana: túnica carmesí oscura, runa flotante y báculo de relojería."""
        cache_key = f"cultist_{int(angle)}_{int((pulse % 6.28) * 10)}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        size = 44
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        # Túnica ceremonial púrpura/carmesí profunda
        pygame.draw.circle(surf, (45, 15, 45), (center - 2, center), 13)
        pygame.draw.circle(surf, (80, 25, 70), (center - 2, center), 10)
        pygame.draw.circle(surf, COLOR_GOLD, (center - 2, center), 10, 1)

        # Capucha sombría con ojos violeta fulgurantes
        pygame.draw.circle(surf, (20, 10, 25), (center + 3, center), 6)
        pygame.draw.circle(surf, (170, 80, 255), (center + 5, center - 2), 2)
        pygame.draw.circle(surf, (170, 80, 255), (center + 5, center + 2), 2)

        # Báculo de engranajes con orbe arcano oscilante
        pygame.draw.line(surf, COLOR_BRASS, (center, center + 5), (center + 14, center + 10), 2)
        orb_y = center + 10 + int(2 * math.sin(pulse * 3.0))
        pygame.draw.circle(surf, (155, 89, 182), (center + 15, orb_y), 4)
        pygame.draw.circle(surf, COLOR_WHITE, (center + 15, orb_y), 2)

        rotated_surf = pygame.transform.rotate(surf, -angle)
        cls._cache[cache_key] = rotated_surf
        return rotated_surf

    @classmethod
    def get_reaper_sprite(cls, angle=0) -> pygame.Surface:
        """Segador Mecánico de Cadena: esqueleto de acero oscuro, engranajes y gran guadaña afilada."""
        cache_key = f"reaper_{int(angle)}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        size = 48
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        # Armazón esbelto de acero templado oscuro y cadena dorsal
        pygame.draw.circle(surf, (28, 30, 35), (center - 3, center), 12)
        pygame.draw.circle(surf, (60, 65, 75), (center - 3, center), 9)
        pygame.draw.circle(surf, COLOR_BRASS, (center - 5, center), 4)

        # Cráneo mecánico con visor carmesí
        pygame.draw.circle(surf, (215, 215, 220), (center + 2, center), 6)
        pygame.draw.line(surf, (240, 30, 30), (center + 3, center - 2), (center + 5, center + 2), 2)

        # Guadaña mecánica curva prominente
        pygame.draw.line(surf, (90, 85, 95), (center - 6, center - 12), (center + 10, center + 14), 2)
        scythe_blade = [(center - 6, center - 12), (center + 2, center - 20), (center + 14, center - 14), (center + 4, center - 13)]
        pygame.draw.polygon(surf, (220, 225, 235), scythe_blade)
        pygame.draw.polygon(surf, (150, 30, 30), scythe_blade, 1)

        rotated_surf = pygame.transform.rotate(surf, -angle)
        cls._cache[cache_key] = rotated_surf
        return rotated_surf

    @classmethod
    def get_elite_enemy_sprite(cls, pulse=0.0) -> pygame.Surface:
        """Compatibilidad: Espíritu espectral por defecto (Penumbra)."""
        return cls.get_spirit_variant_sprite("Penumbra", pulse)

    @classmethod
    def get_spirit_variant_sprite(cls, variant: str, pulse=0.0) -> pygame.Surface:
        """
        Genera el sprite único para cada una de las 5 variantes de Espíritus Malignos:
        1. Penumbra: Púrpura sombrío, núcleo abisal.
        2. Llama Fatua: Naranja ígneo, núcleo de fuego ardiente.
        3. Glacial: Azul cian gélido, escarcha luminosa.
        4. Tormenta: Amarillo relámpago, chispas eléctricas.
        5. Nigromante: Verde ectoplásmico oscuro, ojos demoníacos.
        """
        size = 48
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        # Paleta según variante
        palette = {
            "Penumbra":   ((138, 43, 226, 90), (75, 0, 130), (186, 85, 211), (255, 255, 255)),
            "Llama Fatua":((255, 69, 0, 100),  (180, 40, 0), (255, 165, 0),  (255, 255, 200)),
            "Glacial":    ((0, 206, 209, 95),  (0, 105, 148), (175, 238, 238),(255, 255, 255)),
            "Tormenta":   ((255, 215, 0, 100), (180, 140, 0),(255, 240, 100),(255, 255, 255)),
            "Nigromante": ((34, 139, 34, 95),  (20, 60, 20),  (50, 205, 50),   (200, 255, 200)),
        }
        glow_col, body_col, core_col, eye_col = palette.get(variant, palette["Penumbra"])

        # Aura espectral pulsante
        glow_radius = int(18 + 4 * math.sin(pulse))
        pygame.draw.circle(surf, glow_col, (center, center), glow_radius)

        # Núcleo espectral
        pygame.draw.circle(surf, body_col, (center, center), 12)
        pygame.draw.circle(surf, core_col, (center, center), 7)

        # Ojos relucientes
        pygame.draw.circle(surf, eye_col, (center + 3, center - 3), 2)
        pygame.draw.circle(surf, eye_col, (center + 3, center + 3), 2)

        return surf

    @classmethod
    def get_boss_sprite(cls, element: str) -> pygame.Surface:
        """
        Genera el sprite colosal para el Jefe Elemental del Nivel 10.
        """
        cache_key = f"boss_{element}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        size = 80
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        elem_color = ELEMENT_COLORS.get(element, COLOR_BRASS)

        # Corona de vapor y energía elemental
        pygame.draw.circle(surf, elem_color, (center, center), 34, 4)
        pygame.draw.circle(surf, COLOR_DARK_STONE, (center, center), 30)

        # Placas de armadura titánica
        pygame.draw.rect(surf, COLOR_BRASS, (center - 18, center - 18, 36, 36), 3)

        # Núcleo elemental gigante en el pecho
        pygame.draw.circle(surf, elem_color, (center, center), 14)
        pygame.draw.circle(surf, COLOR_WHITE, (center, center), 6)

        # Cuernos / chimeneas de vapor
        pygame.draw.rect(surf, COLOR_COPPER, (center - 24, center - 32, 8, 16))
        pygame.draw.rect(surf, COLOR_COPPER, (center + 16, center - 32, 8, 16))

        cls._cache[cache_key] = surf
        return surf


    @classmethod
    def get_arena_surface(cls, width: int, height: int, element: str) -> pygame.Surface:
        """
        Genera el fondo atmosférico de mazmorra gótica medieval con detalles del elemento actual:
        - Muros de piedra tallada con bloques y pilares en relieve.
        - Antorchas medievales en los muros con resplandor cálido.
        - Baldosas de piedra con texturas variadas y grietas.
        - Glifo rúnico elemental gigante en el centro de la arena.
        - Sombra perimetral de oclusión ambiental para sensación de profundidad.
        """
        cache_key = f"arena_gothic_{width}_{height}_{element}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        surf = pygame.Surface((width, height))
        elem_color = ELEMENT_COLORS.get(element, COLOR_BRASS)

        # 1. Suelo base de piedra oscura de mazmorra
        surf.fill((28, 30, 36))

        # 2. Cuadrícula de baldosas góticas (64x64) con variaciones de piedra
        tile_size = 64
        for x in range(0, width, tile_size):
            for y in range(0, height, tile_size):
                rect = pygame.Rect(x, y, tile_size, tile_size)
                # Alternancia de tono de baldosa
                coord_sum = (x // tile_size) + (y // tile_size)
                tile_bg = (38, 41, 49) if coord_sum % 2 == 0 else (33, 35, 42)
                pygame.draw.rect(surf, tile_bg, rect)
                pygame.draw.rect(surf, (22, 24, 28), rect, 1)

                # Detalles decorativos aleatorios deterministas
                seed_val = (x * 73856093 ^ y * 19349663) % 100
                if seed_val < 15:
                    # Grieta en la piedra
                    pygame.draw.line(surf, (18, 20, 24), (x + 12, y + 14), (x + 36, y + 42), 1)
                    pygame.draw.line(surf, (18, 20, 24), (x + 36, y + 42), (x + 50, y + 38), 1)
                elif seed_val < 25:
                    # Runa elemental pequeña grabada en la baldosa
                    pygame.draw.circle(surf, (*elem_color[:3],), (x + tile_size // 2, y + tile_size // 2), 3, 1)

        # 3. Glifo y Círculo Rúnico Gigante en el centro de la arena
        center_x = width // 2
        center_y = height // 2
        # Anillos concéntricos arcanos
        pygame.draw.circle(surf, elem_color, (center_x, center_y), 170, 2)
        pygame.draw.circle(surf, elem_color, (center_x, center_y), 130, 1)
        pygame.draw.circle(surf, elem_color, (center_x, center_y), 70, 2)
        # Estrella rúnica octogonal en el centro
        for i in range(8):
            ang = (math.pi / 4) * i
            x1 = center_x + int(math.cos(ang) * 70)
            y1 = center_y + int(math.sin(ang) * 70)
            x2 = center_x + int(math.cos(ang) * 170)
            y2 = center_y + int(math.sin(ang) * 170)
            pygame.draw.line(surf, elem_color, (x1, y1), (x2, y2), 1)
            # Runa orbital
            pygame.draw.circle(surf, elem_color, (x2, y2), 5, 1)

        # 4. Sombra perimetral de Oclusión Ambiental (viñeta hacia el interior)
        shadow_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        wall_thick = 36
        # Sombras proyectadas por los muros perimetrales
        for i in range(24):
            alpha = int(120 * (1.0 - i / 24.0))
            offset = wall_thick + i
            pygame.draw.rect(shadow_surf, (0, 0, 0, alpha),
                             (offset, offset, width - 2 * offset, height - 2 * offset), 1)
        surf.blit(shadow_surf, (0, 0))

        # 5. Muros perimetrales de bloques de piedra medieval tallada
        pygame.draw.rect(surf, (16, 17, 22), (0, 0, width, wall_thick))
        pygame.draw.rect(surf, (16, 17, 22), (0, height - wall_thick, width, wall_thick))
        pygame.draw.rect(surf, (16, 17, 22), (0, 0, wall_thick, height))
        pygame.draw.rect(surf, (16, 17, 22), (width - wall_thick, 0, wall_thick, height))

        # Bloques individuales de mampostería en los muros
        brick_w = 32
        for bx in range(0, width, brick_w):
            pygame.draw.line(surf, (30, 32, 40), (bx, 0), (bx, wall_thick), 1)
            pygame.draw.line(surf, (30, 32, 40), (bx, height - wall_thick), (bx, height), 1)
        brick_h = 24
        for by in range(0, height, brick_h):
            pygame.draw.line(surf, (30, 32, 40), (0, by), (wall_thick, by), 1)
            pygame.draw.line(surf, (30, 32, 40), (width - wall_thick, by), (width, by), 1)

        # Cenefa metálica de latón envejecido y remaches góticos
        pygame.draw.rect(surf, COLOR_BRASS, (wall_thick - 3, wall_thick - 3,
                                             width - 2 * wall_thick + 6, height - 2 * wall_thick + 6), 3)

        # 6. Columnas de piedra en las 4 esquinas y antorchas en los muros
        column_size = 46
        corners = [
            (0, 0),
            (width - column_size, 0),
            (0, height - column_size),
            (width - column_size, height - column_size)
        ]
        for cx, cy in corners:
            pygame.draw.rect(surf, (35, 38, 48), (cx, cy, column_size, column_size))
            pygame.draw.rect(surf, COLOR_BRASS, (cx, cy, column_size, column_size), 2)
            pygame.draw.circle(surf, elem_color, (cx + column_size // 2, cy + column_size // 2), 7, 2)

        # Antorchas medievales con soportes de bronce a lo largo de los muros
        torch_positions = [
            (width // 4, wall_thick - 4), (width // 2, wall_thick - 4), (width * 3 // 4, wall_thick - 4),
            (width // 4, height - wall_thick + 4), (width // 2, height - wall_thick + 4), (width * 3 // 4, height - wall_thick + 4),
            (wall_thick - 4, height // 3), (wall_thick - 4, height * 2 // 3),
            (width - wall_thick + 4, height // 3), (width - wall_thick + 4, height * 2 // 3)
        ]
        for tx, ty in torch_positions:
            # Soporte de latón
            pygame.draw.circle(surf, COLOR_BRASS, (tx, ty), 5)
            # Llama y resplandor
            pygame.draw.circle(surf, (255, 140, 20), (tx, ty), 4)
            pygame.draw.circle(surf, (255, 230, 100), (tx, ty), 2)

        cls._cache[cache_key] = surf
        return surf

    @classmethod
    def get_role_portrait(cls, role_id: str, role_color=(200, 200, 200),
                           weapon_type: str = "sword", size: int = 72) -> pygame.Surface:
        """
        Genera el medallón y busto pixel art procedural del personaje/rol seleccionado.
        Proporciona identidad visual inmediata a cada una de las 12 clases legendarias.
        """
        cache_key = f"role_portrait_{role_id}_{size}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        R = size // 2 - 2

        # 1. Medallón y fondo místico
        pygame.draw.circle(surf, (18, 20, 26), (cx, cy), R)
        tint = (max(10, min(255, role_color[0] // 5)),
                max(10, min(255, role_color[1] // 5)),
                max(10, min(255, role_color[2] // 5)))
        pygame.draw.circle(surf, tint, (cx, cy), R - 2)
        # Borde ornamental con el color temático del rol
        pygame.draw.circle(surf, role_color, (cx, cy), R, 2)
        pygame.draw.circle(surf, (role_color[0] // 2, role_color[1] // 2, role_color[2] // 2), (cx, cy), R - 3, 1)
        # Sombra de pedestal
        pygame.draw.ellipse(surf, (8, 9, 12, 190), (cx - 22, cy + 18, 44, 10))

        # 2. Busto característico según el arquetipo
        if role_id == "berserker":
            # Manto de piel salvaje
            pygame.draw.ellipse(surf, (80, 50, 30), (cx - 20, cy + 4, 40, 20))
            # Torso bronce y arnés de cuero
            pygame.draw.rect(surf, (170, 120, 85), (cx - 13, cy + 8, 26, 18), border_radius=3)
            pygame.draw.line(surf, (70, 40, 20), (cx - 12, cy + 8), (cx + 12, cy + 22), 3)
            pygame.draw.line(surf, (70, 40, 20), (cx + 12, cy + 8), (cx - 12, cy + 22), 3)
            pygame.draw.circle(surf, (220, 180, 50), (cx, cy + 15), 3)
            # Cabeza y Casco con cuernos
            pygame.draw.circle(surf, (180, 125, 90), (cx, cy - 6), 11)
            pygame.draw.rect(surf, (65, 70, 78), (cx - 11, cy - 16, 22, 13), border_radius=4)
            # Cuernos curvados de marfil
            pygame.draw.polygon(surf, (235, 230, 210), [(cx - 9, cy - 10), (cx - 19, cy - 19), (cx - 7, cy - 14)])
            pygame.draw.polygon(surf, (235, 230, 210), [(cx + 9, cy - 10), (cx + 19, cy - 19), (cx + 7, cy - 14)])
            # Ojos de furia carmesí
            pygame.draw.rect(surf, (255, 30, 30), (cx - 6, cy - 7, 4, 3))
            pygame.draw.rect(surf, (255, 30, 30), (cx + 2, cy - 7, 4, 3))
            # Barba guerrera
            pygame.draw.polygon(surf, (110, 45, 20), [(cx - 8, cy - 1), (cx + 8, cy - 1), (cx, cy + 9)])

        elif role_id == "paladin":
            # Halo sagrado divino
            pygame.draw.ellipse(surf, (255, 230, 100), (cx - 14, cy - 25, 28, 8), 2)
            # Capa blanca y oro
            pygame.draw.ellipse(surf, (240, 240, 245), (cx - 19, cy + 5, 38, 20))
            # Coraza dorada y cruz blanca
            pygame.draw.rect(surf, (220, 185, 60), (cx - 14, cy + 7, 28, 18), border_radius=4)
            pygame.draw.line(surf, (255, 255, 255), (cx, cy + 9), (cx, cy + 22), 3)
            pygame.draw.line(surf, (255, 255, 255), (cx - 6, cy + 14), (cx + 6, cy + 14), 3)
            # Casco templario con hendidura en T resplandeciente
            pygame.draw.rect(surf, (235, 205, 90), (cx - 10, cy - 16, 20, 18), border_radius=4)
            pygame.draw.line(surf, (255, 255, 240), (cx, cy - 12), (cx, cy - 2), 2)
            pygame.draw.line(surf, (255, 255, 240), (cx - 6, cy - 8), (cx + 6, cy - 8), 2)
            pygame.draw.circle(surf, (255, 255, 255), (cx, cy - 8), 2)

        elif role_id == "rogue":
            # Manto sombrío
            pygame.draw.ellipse(surf, (28, 30, 38), (cx - 18, cy + 5, 36, 20))
            pygame.draw.rect(surf, (40, 44, 52), (cx - 12, cy + 8, 24, 18), border_radius=3)
            # Dagas cruzadas en pecho
            pygame.draw.line(surf, (46, 204, 113), (cx - 10, cy + 10), (cx + 10, cy + 20), 2)
            pygame.draw.line(surf, (46, 204, 113), (cx + 10, cy + 10), (cx - 10, cy + 20), 2)
            # Capucha de asesino
            pygame.draw.polygon(surf, (22, 24, 30), [(cx - 12, cy - 4), (cx, cy - 21), (cx + 12, cy - 4), (cx, cy + 2)])
            # Sombra interior del rostro
            pygame.draw.ellipse(surf, (8, 9, 12), (cx - 7, cy - 9, 14, 10))
            # Ojos esmeralda venenosos
            pygame.draw.circle(surf, (46, 204, 113), (cx - 4, cy - 5), 2)
            pygame.draw.circle(surf, (46, 204, 113), (cx + 4, cy - 5), 2)
            pygame.draw.circle(surf, (255, 255, 255), (cx - 4, cy - 5), 1)
            pygame.draw.circle(surf, (255, 255, 255), (cx + 4, cy - 5), 1)

        elif role_id == "mage":
            # Túnica astral púrpura
            pygame.draw.ellipse(surf, (60, 30, 95), (cx - 19, cy + 5, 38, 20))
            pygame.draw.rect(surf, (85, 40, 130), (cx - 13, cy + 8, 26, 18), border_radius=4)
            pygame.draw.circle(surf, (241, 196, 15), (cx, cy + 14), 3)
            # Cabeza
            pygame.draw.circle(surf, (215, 180, 150), (cx, cy - 5), 9)
            # Sombrero picudo de archimago
            pygame.draw.polygon(surf, (70, 25, 115), [(cx - 15, cy - 8), (cx + 15, cy - 8), (cx - 3, cy - 26)])
            pygame.draw.ellipse(surf, (55, 20, 90), (cx - 16, cy - 10, 32, 6))
            pygame.draw.rect(surf, (241, 196, 15), (cx - 5, cy - 11, 10, 4))
            # Chispa arcana flotante
            pygame.draw.circle(surf, (210, 160, 255), (cx - 4, cy - 27), 3)
            pygame.draw.circle(surf, (255, 255, 255), (cx - 4, cy - 27), 1)
            # Ojos brillantes
            pygame.draw.rect(surf, (180, 120, 255), (cx - 5, cy - 6, 3, 2))
            pygame.draw.rect(surf, (180, 120, 255), (cx + 2, cy - 6, 3, 2))

        elif role_id == "hunter":
            # Capa de montaraz verde
            pygame.draw.ellipse(surf, (40, 80, 45), (cx - 18, cy + 5, 36, 20))
            # Jubón de cuero y canana
            pygame.draw.rect(surf, (95, 60, 35), (cx - 13, cy + 8, 26, 18), border_radius=3)
            pygame.draw.line(surf, (180, 140, 60), (cx - 11, cy + 8), (cx + 11, cy + 22), 3)
            # Capucha con pluma de halcón
            pygame.draw.polygon(surf, (45, 95, 50), [(cx - 11, cy - 3), (cx, cy - 18), (cx + 11, cy - 3), (cx, cy + 2)])
            pygame.draw.polygon(surf, (230, 126, 34), [(cx + 6, cy - 14), (cx + 17, cy - 24), (cx + 10, cy - 12)])
            pygame.draw.circle(surf, (220, 175, 140), (cx, cy - 5), 7)
            # Ojos de lince
            pygame.draw.circle(surf, (245, 180, 40), (cx - 3, cy - 5), 2)
            pygame.draw.circle(surf, (245, 180, 40), (cx + 3, cy - 5), 2)

        elif role_id == "necromancer":
            # Manto espectral oscuro
            pygame.draw.ellipse(surf, (30, 25, 45), (cx - 18, cy + 5, 36, 20))
            pygame.draw.rect(surf, (45, 35, 65), (cx - 13, cy + 8, 26, 18), border_radius=3)
            # Costillas de hueso sobre el pecho
            for py in [11, 15, 19]:
                pygame.draw.line(surf, (200, 200, 215), (cx - 8, cy + py), (cx + 8, cy + py), 2)
            # Capucha cadavérica con cuernos demoníacos
            pygame.draw.polygon(surf, (25, 20, 35), [(cx - 12, cy - 3), (cx, cy - 19), (cx + 12, cy - 3), (cx, cy + 2)])
            pygame.draw.polygon(surf, (80, 70, 95), [(cx - 10, cy - 12), (cx - 18, cy - 20), (cx - 8, cy - 16)])
            pygame.draw.polygon(surf, (80, 70, 95), [(cx + 10, cy - 12), (cx + 18, cy - 20), (cx + 8, cy - 16)])
            # Máscara esquelética y ojos de alma cian
            pygame.draw.ellipse(surf, (220, 220, 225), (cx - 6, cy - 8, 12, 10))
            pygame.draw.circle(surf, (0, 220, 255), (cx - 3, cy - 5), 2)
            pygame.draw.circle(surf, (0, 220, 255), (cx + 3, cy - 5), 2)
            pygame.draw.circle(surf, (255, 255, 255), (cx - 3, cy - 5), 1)
            pygame.draw.circle(surf, (255, 255, 255), (cx + 3, cy - 5), 1)

        elif role_id == "runeknight":
            # Capa azul zafiro
            pygame.draw.ellipse(surf, (30, 70, 120), (cx - 19, cy + 5, 38, 20))
            # Coraza de acero rúnico con circuitos de luz
            pygame.draw.rect(surf, (75, 85, 100), (cx - 14, cy + 7, 28, 18), border_radius=4)
            pygame.draw.circle(surf, (52, 152, 219), (cx, cy + 15), 5)
            pygame.draw.circle(surf, (255, 255, 255), (cx, cy + 15), 2)
            pygame.draw.line(surf, (52, 152, 219), (cx - 10, cy + 11), (cx + 10, cy + 11), 2)
            # Casco cerrado con celada rúnica
            pygame.draw.rect(surf, (90, 105, 125), (cx - 10, cy - 16, 20, 17), border_radius=4)
            pygame.draw.line(surf, (52, 152, 219), (cx - 7, cy - 8), (cx + 7, cy - 8), 3)
            pygame.draw.line(surf, (255, 255, 255), (cx - 5, cy - 8), (cx + 5, cy - 8), 1)
            # Cresta alada
            pygame.draw.polygon(surf, (52, 152, 219), [(cx, cy - 22), (cx - 4, cy - 16), (cx + 4, cy - 16)])

        elif role_id == "alchemist":
            # Traje de boticario
            pygame.draw.ellipse(surf, (30, 50, 40), (cx - 18, cy + 5, 36, 20))
            pygame.draw.rect(surf, (50, 70, 55), (cx - 13, cy + 8, 26, 18), border_radius=3)
            # Bandolera con viales verde y rojo
            pygame.draw.circle(surf, (46, 204, 113), (cx - 6, cy + 14), 3)
            pygame.draw.circle(surf, (231, 76, 60), (cx + 6, cy + 14), 3)
            # Máscara médica de pico de cuervo
            pygame.draw.rect(surf, (40, 42, 48), (cx - 10, cy - 14, 20, 14), border_radius=4)
            # Pico curvado
            pygame.draw.polygon(surf, (60, 62, 70), [(cx - 4, cy - 4), (cx + 4, cy - 4), (cx, cy + 5)])
            # Gafas redondas de bronce con líquido ácido
            pygame.draw.circle(surf, (180, 140, 40), (cx - 5, cy - 7), 5)
            pygame.draw.circle(surf, (180, 140, 40), (cx + 5, cy - 7), 5)
            pygame.draw.circle(surf, (46, 204, 113), (cx - 5, cy - 7), 3)
            pygame.draw.circle(surf, (46, 204, 113), (cx + 5, cy - 7), 3)
            pygame.draw.circle(surf, (255, 255, 255), (cx - 6, cy - 8), 1)
            pygame.draw.circle(surf, (255, 255, 255), (cx + 4, cy - 8), 1)

        elif role_id == "monk":
            # Torso con hombro descubierto y cinta azafrán
            pygame.draw.ellipse(surf, (180, 120, 40), (cx - 18, cy + 5, 36, 20))
            pygame.draw.rect(surf, (190, 135, 95), (cx - 12, cy + 8, 24, 18), border_radius=3)
            pygame.draw.line(surf, (230, 126, 34), (cx - 12, cy + 8), (cx + 12, cy + 22), 5)
            # Collar de cuentas budistas
            for ang in [0.5, 1.2, 1.9, 2.6]:
                bx = cx + int(math.cos(ang) * 9)
                by = cy + 13 + int(math.sin(ang) * 5)
                pygame.draw.circle(surf, (100, 65, 30), (bx, by), 2)
            # Cabeza rapada y cinta marcial
            pygame.draw.circle(surf, (205, 150, 110), (cx, cy - 6), 10)
            pygame.draw.rect(surf, (231, 76, 60), (cx - 10, cy - 11, 20, 4))
            # Ojos serenos y bindu dorado de Ki
            pygame.draw.circle(surf, (241, 196, 15), (cx, cy - 8), 2)
            pygame.draw.line(surf, (40, 30, 20), (cx - 6, cy - 5), (cx - 2, cy - 5), 2)
            pygame.draw.line(surf, (40, 30, 20), (cx + 2, cy - 5), (cx + 6, cy - 5), 2)
            # Aura de puños dorados en la base
            pygame.draw.circle(surf, (241, 196, 15), (cx - 14, cy + 18), 4)
            pygame.draw.circle(surf, (241, 196, 15), (cx + 14, cy + 18), 4)

        elif role_id == "artificer":
            # Coraza de bronce y cuero con caldera
            pygame.draw.ellipse(surf, (140, 90, 40), (cx - 19, cy + 5, 38, 20))
            pygame.draw.rect(surf, (180, 120, 50), (cx - 13, cy + 8, 26, 18), border_radius=3)
            # Manómetro en el pecho
            pygame.draw.circle(surf, (240, 240, 245), (cx, cy + 14), 4)
            pygame.draw.circle(surf, (200, 50, 50), (cx, cy + 14), 1)
            # Chimenea de escape de vapor en el hombro
            pygame.draw.rect(surf, (160, 100, 30), (cx - 17, cy + 2, 5, 9))
            pygame.draw.circle(surf, (240, 240, 255), (cx - 15, cy - 2), 3)
            pygame.draw.circle(surf, (240, 240, 255), (cx - 17, cy - 7), 2)
            # Casco de bronce con doble visor steampunk
            pygame.draw.rect(surf, (160, 110, 40), (cx - 10, cy - 15, 20, 15), border_radius=4)
            # Gafas de latón
            pygame.draw.circle(surf, (200, 150, 50), (cx - 5, cy - 7), 5)
            pygame.draw.circle(surf, (200, 150, 50), (cx + 5, cy - 7), 5)
            pygame.draw.circle(surf, (0, 206, 209), (cx - 5, cy - 7), 3)
            pygame.draw.circle(surf, (255, 140, 0), (cx + 5, cy - 7), 3)

        elif role_id == "shaman":
            # Manto de piel animal y plumas
            pygame.draw.ellipse(surf, (60, 50, 40), (cx - 19, cy + 5, 38, 20))
            pygame.draw.rect(surf, (110, 80, 60), (cx - 12, cy + 8, 24, 18), border_radius=3)
            # Tocado de calavera de lobo / cuernos
            pygame.draw.polygon(surf, (180, 175, 165), [(cx - 12, cy - 8), (cx, cy - 20), (cx + 12, cy - 8)])
            pygame.draw.polygon(surf, (230, 225, 215), [(cx - 8, cy - 10), (cx - 15, cy - 20), (cx - 5, cy - 15)])
            pygame.draw.polygon(surf, (230, 225, 215), [(cx + 8, cy - 10), (cx + 15, cy - 20), (cx + 5, cy - 15)])
            # Rostro con pintura de guerra turquesa
            pygame.draw.circle(surf, (175, 125, 90), (cx, cy - 6), 9)
            pygame.draw.line(surf, (26, 188, 156), (cx - 6, cy - 6), (cx + 6, cy - 6), 2)
            pygame.draw.line(surf, (26, 188, 156), (cx, cy - 11), (cx, cy - 1), 2)
            # Ojos espirituales turquesas
            pygame.draw.circle(surf, (26, 188, 156), (cx - 3, cy - 6), 2)
            pygame.draw.circle(surf, (26, 188, 156), (cx + 3, cy - 6), 2)

        elif role_id == "inquisitor":
            # Tabardo carmesí y cadenas pesadas de hierro
            pygame.draw.ellipse(surf, (130, 30, 30), (cx - 18, cy + 5, 36, 20))
            pygame.draw.rect(surf, (160, 35, 35), (cx - 13, cy + 8, 26, 18), border_radius=3)
            # Cadena de hierro cruzada
            for i in range(-8, 9, 4):
                pygame.draw.circle(surf, (160, 165, 175), (cx + i, cy + 15), 2, 1)
            # Capucha de verdugo rojo sangre
            pygame.draw.polygon(surf, (140, 25, 25), [(cx - 12, cy - 4), (cx, cy - 19), (cx + 12, cy - 4), (cx, cy + 2)])
            # Máscara de hierro con púas y ranuras
            pygame.draw.rect(surf, (70, 75, 85), (cx - 8, cy - 10, 16, 12), border_radius=3)
            pygame.draw.line(surf, (220, 50, 50), (cx - 6, cy - 6), (cx + 6, cy - 6), 2)
            pygame.draw.line(surf, (180, 185, 195), (cx - 5, cy - 3), (cx + 5, cy - 3), 1)

        else:
            # Héroe genérico / Aventurero
            pygame.draw.ellipse(surf, (40, 50, 70), (cx - 18, cy + 5, 36, 20))
            pygame.draw.rect(surf, (80, 85, 95), (cx - 12, cy + 8, 24, 18), border_radius=3)
            pygame.draw.circle(surf, (210, 165, 130), (cx, cy - 6), 10)
            pygame.draw.rect(surf, (50, 55, 65), (cx - 9, cy - 14, 18, 10), border_radius=3)
            pygame.draw.circle(surf, (255, 255, 255), (cx - 4, cy - 6), 2)
            pygame.draw.circle(surf, (255, 255, 255), (cx + 4, cy - 6), 2)

        cls._cache[cache_key] = surf
        return surf
