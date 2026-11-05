"""
================================================================================
MÓDULO: systems/combat_system.py
RESPONSABILIDAD: Motor de resolución de combates, física mágica inspirada en
                 'Wizard of Legend', trampas de terreno, ondas expansivas y proyectiles.
CONCEPTO ACADÉMICO: Simulación de Partículas, Zonas de Área (AoE) y Patrón Strategy.
================================================================================
Implementa:
1. Hechizos Mágicos Complejos estilo 'Wizard of Legend':
   - Fuego: Bola ígnea explosiva que crea charcos de lava ardiente.
   - Agua: Tsunami penetrante a presión que empuja en abanico y ralentiza.
   - Viento: Ciclón boomerang con vórtice gravitacional que succiona enemigos.
   - Tierra: Falla sísmica con estacas de roca que perforan y aturden.
   - Trueno: Centella de arco voltaico encadenada a múltiples objetivos.
   - Naturaleza: Zarzas venenosas que enraízan e inmovilizan.
   - Luz (DORADA): Juicio divino vertical que desata 8 rayos celestiales y sana al jugador.
   - Oscuridad (DORADA): Singularidad abisal (agujero negro) que aspira la sala y drena vida.

2. Ondas de Choque (Shockwaves) de Jefes y Demoledores (Esquivables con Dash).
"""

import math
import random
import pygame
from settings import (
    COLOR_WHITE, COLOR_RED_HEALTH, COLOR_GOLD, COLOR_BRASS, COLOR_COPPER,
    COLOR_STEAM, ELEMENT_COLORS, PLAYER_ATTACK_RANGE, PLAYER_ATTACK_ARC_DEG,
    MANA_SPELL_COSTS, MANA_REGEN_KILL_MIN, MANA_REGEN_KILL_MAX, MANA_REGEN_MELEE_HIT
)


class DamageText:
    """Representa un número de daño que flota y se desvanece en pantalla."""

    def __init__(self, x: float, y: float, amount, color=COLOR_WHITE, is_critical=False):
        self.x = x
        self.y = y
        if isinstance(amount, (int, float)):
            self.text = f"{int(amount)}"
            if is_critical:
                self.text += "!"
        else:
            self.text = str(amount)
        self.color = color
        self.lifetime = 0.65
        self.max_lifetime = self.lifetime
        self.vel_y = -65.0
        self.vel_x = random.uniform(-20, 20)

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        self.y += self.vel_y * dt
        self.x += self.vel_x * dt
        return self.lifetime > 0

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        alpha = max(0, min(255, int((self.lifetime / self.max_lifetime) * 255)))
        # Sombra de alto contraste para visibilidad instantánea
        shadow_surf = font.render(self.text, True, (8, 10, 14))
        shadow_surf.set_alpha(alpha)
        surface.blit(shadow_surf, (int(self.x) - shadow_surf.get_width() // 2 + 1, int(self.y) - shadow_surf.get_height() // 2 + 1))

        txt_surf = font.render(self.text, True, self.color)
        txt_surf.set_alpha(alpha)
        rect = txt_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(txt_surf, rect)


class Particle:
    """Partícula simple de vapor, chispa o magia para retroalimentación de impacto."""

    def __init__(self, x: float, y: float, color=COLOR_STEAM, speed=120.0, life=0.35, size=3):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        self.vel_x = math.cos(angle) * random.uniform(speed * 0.3, speed)
        self.vel_y = math.sin(angle) * random.uniform(speed * 0.3, speed)
        self.life = life
        self.max_life = life
        self.size = size

    def update(self, dt: float) -> bool:
        self.life -= dt
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        return self.life > 0

    def draw(self, surface: pygame.Surface):
        if self.life > 0:
            current_size = max(1, int(self.size * (self.life / self.max_life)))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), current_size)


class Projectile:
    """Proyectil elemental balístico con diseño visual avanzado (estela, rotación, rebotes y físicas)."""

    def __init__(self, x: float, y: float, dir_x: float, dir_y: float, damage: float,
                 speed=420.0, element="Fuego", is_player=True, radius=10, pierces=False,
                 on_hit_effect=None):
        self.pos = pygame.math.Vector2(x, y)
        self.spawn_pos = pygame.math.Vector2(x, y)
        direction = pygame.math.Vector2(dir_x, dir_y)
        if direction.length_squared() > 0:
            self.vel = direction.normalize() * speed
        else:
            self.vel = pygame.math.Vector2(speed, 0)
        self.damage = damage
        self.element = element
        self.is_player = is_player
        self.radius = radius
        self.lifetime = 2.5
        self.pierces = pierces
        self.on_hit_effect = on_hit_effect
        self.hit_entities = set()
        self.color = ELEMENT_COLORS.get(element, COLOR_GOLD)
        self.trail = []
        self.anim_time = 0.0
        self.particle_timer = 0.0

        # Propiedades mecánicas avanzadas de hechizos creativos
        self.is_boomerang = False
        self.boomerang_state = 0         # 0: saliendo, 1: regresando al jugador
        self.boomerang_max_dist = 320.0
        self.is_homing = False
        self.is_orbiting = False
        self.orbit_angle = 0.0
        self.orbit_radius = 55.0
        self.ricochets_left = 0
        self.destroys_bullets = False
        self.launched = False

    def _emit_flight_particles(self, combat_system):
        """Emite micropartículas temáticas en vuelo para evitar gráficos planos de tipo PNG."""
        px, py = self.pos.x, self.pos.y
        elem = self.element
        if elem == "Fuego":
            combat_system.particles.append(Particle(px + random.uniform(-4, 4), py + random.uniform(-4, 4),
                                                    color=random.choice([(255, 110, 20), (255, 190, 30), (230, 50, 20)]),
                                                    speed=45.0, life=0.25, size=random.randint(2, 4)))
        elif elem == "Agua":
            combat_system.particles.append(Particle(px + random.uniform(-3, 3), py + random.uniform(-3, 3),
                                                    color=random.choice([(0, 215, 245), (41, 128, 185), (180, 245, 255)]),
                                                    speed=35.0, life=0.28, size=random.randint(2, 3)))
        elif elem == "Viento":
            combat_system.particles.append(Particle(px + random.uniform(-4, 4), py + random.uniform(-4, 4),
                                                    color=random.choice([(26, 188, 156), (160, 245, 225), (200, 255, 240)]),
                                                    speed=60.0, life=0.22, size=2))
        elif elem == "Tierra":
            combat_system.particles.append(Particle(px + random.uniform(-4, 4), py + random.uniform(-4, 4),
                                                    color=random.choice([(140, 70, 35), (205, 145, 90), (100, 48, 22)]),
                                                    speed=40.0, life=0.30, size=random.randint(2, 4)))
        elif elem == "Trueno":
            combat_system.particles.append(Particle(px + random.uniform(-5, 5), py + random.uniform(-5, 5),
                                                    color=random.choice([(255, 240, 90), (255, 255, 220), (243, 156, 18)]),
                                                    speed=85.0, life=0.18, size=random.randint(2, 3)))
        elif elem == "Naturaleza":
            combat_system.particles.append(Particle(px + random.uniform(-3, 3), py + random.uniform(-3, 3),
                                                    color=random.choice([(46, 204, 113), (160, 255, 130), (39, 174, 96)]),
                                                    speed=35.0, life=0.26, size=random.randint(2, 3)))
        elif elem in ("Vapor (Steampunk)", "Vapor"):
            combat_system.particles.append(Particle(px + random.uniform(-5, 5), py + random.uniform(-5, 5),
                                                    color=random.choice([(235, 240, 245), (200, 215, 225), COLOR_STEAM]),
                                                    speed=30.0, life=0.35, size=random.randint(3, 5)))
        elif elem == "Metal":
            combat_system.particles.append(Particle(px + random.uniform(-3, 3), py + random.uniform(-3, 3),
                                                    color=random.choice([(220, 225, 235), COLOR_BRASS, (255, 255, 255)]),
                                                    speed=50.0, life=0.20, size=2))
        elif elem == "Oscuridad":
            combat_system.particles.append(Particle(px + random.uniform(-4, 4), py + random.uniform(-4, 4),
                                                    color=random.choice([(142, 68, 173), (90, 30, 120), (50, 15, 75)]),
                                                    speed=40.0, life=0.28, size=random.randint(2, 4)))
        elif elem == "Luz":
            combat_system.particles.append(Particle(px + random.uniform(-4, 4), py + random.uniform(-4, 4),
                                                    color=random.choice([(255, 255, 230), COLOR_GOLD, (255, 245, 180)]),
                                                    speed=55.0, life=0.24, size=random.randint(2, 4)))

    def update(self, dt: float, player=None, enemies=None, combat_system=None) -> bool:
        self.lifetime -= dt
        self.anim_time += dt

        # Emisión periódica de partículas elementales en vuelo
        if combat_system is not None:
            self.particle_timer += dt
            if self.particle_timer >= 0.05:
                self.particle_timer = 0.0
                self._emit_flight_particles(combat_system)

        # 1. MECÁNICA DE BÚMERAN (VIENTO): Viaja hacia adelante, luego gira y regresa al jugador
        if self.is_boomerang:
            if self.boomerang_state == 0:
                dist = (self.pos - self.spawn_pos).length()
                if dist >= self.boomerang_max_dist:
                    self.boomerang_state = 1
                    self.hit_entities.clear()  # Puede volver a golpear en el viaje de regreso
            elif self.boomerang_state == 1 and player:
                to_player = player.pos - self.pos
                if to_player.length() <= 28.0:
                    player.restore_mana(20.0)
                    if combat_system:
                        combat_system.create_damage_text(player.pos.x, player.pos.y - 30,
                                                         "+20 MP (Búmeran)", color=(26, 188, 156), is_critical=True)
                        combat_system.emit_impact_particles(player.pos.x, player.pos.y, count=12, color=(26, 188, 156))
                    return False
                if to_player.length_squared() > 0:
                    self.vel = to_player.normalize() * 540.0

        # 2. MECÁNICA TELEDIRIGIDA (HOMING / AGUA): Rastrea al enemigo más cercano
        elif self.is_homing and enemies:
            closest = None
            min_d = 360.0
            for e in enemies:
                if getattr(e, 'is_alive', True):
                    d = (e.pos - self.pos).length()
                    if d < min_d:
                        min_d = d
                        closest = e
            if closest:
                diff_tgt = closest.pos - self.pos
                if diff_tgt.length_squared() > 0:
                    to_target = diff_tgt.normalize()
                    self.vel = self.vel.lerp(to_target * 440.0, dt * 5.5)

        # 3. MECÁNICA ORBITANTE (METAL): Gira como escudo protector y luego se dispara
        elif self.is_orbiting and player:
            self.orbit_angle += 7.5 * dt
            self.pos.x = player.pos.x + math.cos(self.orbit_angle) * self.orbit_radius
            self.pos.y = player.pos.y + math.sin(self.orbit_angle) * self.orbit_radius
            if self.lifetime <= 1.0 and not self.launched:
                self.launched = True
                self.is_orbiting = False
                self.vel = player.aim_vector.copy() * 580.0
                self.ricochets_left = 2
            return self.lifetime > 0

        # Movimiento cinemático estándar
        self.pos += self.vel * dt

        # 4. MECÁNICA DE REBOTE EN PAREDES (RICOCHET / METAL)
        if self.ricochets_left > 0:
            bounced = False
            if self.pos.x < 45:
                self.vel.x = abs(self.vel.x)
                self.pos.x = 46
                bounced = True
            elif self.pos.x > 1235:
                self.vel.x = -abs(self.vel.x)
                self.pos.x = 1234
                bounced = True
            if self.pos.y < 45:
                self.vel.y = abs(self.vel.y)
                self.pos.y = 46
                bounced = True
            elif self.pos.y > 675:
                self.vel.y = -abs(self.vel.y)
                self.pos.y = 674
                bounced = True
            if bounced:
                self.ricochets_left -= 1
                if combat_system:
                    combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=10, color=(200, 210, 225))

        # 5. DESTRUCCIÓN DE PROYECTILES HOSTILES (VIENTO)
        if self.destroys_bullets and combat_system:
            for other in list(combat_system.projectiles):
                if not other.is_player and (other.pos - self.pos).length() <= self.radius + other.radius + 12:
                    combat_system.emit_impact_particles(other.pos.x, other.pos.y, count=6, color=(26, 188, 156))
                    combat_system.projectiles.remove(other)

        # Registro de estela de cometa
        self.trail.append((self.pos.x, self.pos.y))
        if len(self.trail) > 6:
            self.trail.pop(0)

        return self.lifetime > 0

    def draw(self, surface: pygame.Surface):
        cx, cy = int(self.pos.x), int(self.pos.y)

        # 1. Dibujar estela de cometa con desvanecimiento gradual de radio y transparencia
        t_len = len(self.trail)
        for i, (tx, ty) in enumerate(self.trail):
            prog = (i + 1) / (t_len + 1)
            t_rad = max(2, int(self.radius * prog * 0.75))
            alpha = int(140 * prog)
            t_surf = pygame.Surface((t_rad * 2 + 2, t_rad * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(t_surf, (*self.color[:3], alpha), (t_rad + 1, t_rad + 1), t_rad)
            surface.blit(t_surf, (int(tx - t_rad - 1), int(ty - t_rad - 1)))

        # 2. Resplandor / Halo exterior
        halo_rad = self.radius + 5
        halo_surf = pygame.Surface((halo_rad * 2 + 4, halo_rad * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(halo_surf, (*self.color[:3], 65), (halo_rad + 2, halo_rad + 2), halo_rad)
        surface.blit(halo_surf, (cx - halo_rad - 2, cy - halo_rad - 2))

        # 3. Representación visual hiper-detallada procedimental (cero PNGs planos)
        elem = self.element

        if elem == "Fuego":
            # Bola de fuego ardiente: corona de llamaradas giratorias, manto incandescente y núcleo blanco fundido
            flame_jitter = int(3 * math.sin(self.anim_time * 28.0))
            # Lenguas de fuego externas dinámicas
            for k in range(5):
                ang = self.anim_time * 14.0 + k * (2 * math.pi / 5)
                flame_d = self.radius + flame_jitter + int(4 * math.sin(self.anim_time * 18.0 + k))
                fx = cx + int(math.cos(ang) * flame_d)
                fy = cy + int(math.sin(ang) * flame_d)
                pygame.draw.circle(surface, (255, 110, 20), (fx, fy), max(2, self.radius // 3))
            pygame.draw.circle(surface, (255, 75, 15), (cx, cy), self.radius + flame_jitter + 2)
            pygame.draw.circle(surface, (243, 156, 18), (cx, cy), self.radius + flame_jitter)
            pygame.draw.circle(surface, (231, 76, 60), (cx, cy), max(3, self.radius - 2))
            pygame.draw.circle(surface, (255, 255, 210), (cx, cy), max(2, self.radius // 2))

        elif elem == "Agua":
            # Hidro-esfera con anillos de onda expansiva, gotículas satélite y curvatura de cristal líquido
            wave_r = self.radius + int(4 * abs(math.sin(self.anim_time * 12.0)))
            pygame.draw.circle(surface, (0, 230, 240), (cx, cy), wave_r + 2, 1)
            # Gotas orbitales giratorias
            for k in range(3):
                ang = self.anim_time * 9.0 + k * (2 * math.pi / 3)
                ox = cx + int(math.cos(ang) * (self.radius + 5))
                oy = cy + int(math.sin(ang) * (self.radius + 5))
                pygame.draw.circle(surface, (150, 245, 255), (ox, oy), 2)
            pygame.draw.circle(surface, (0, 190, 220), (cx, cy), self.radius)
            pygame.draw.circle(surface, (41, 128, 185), (cx, cy), max(2, self.radius - 2))
            pygame.draw.circle(surface, COLOR_WHITE, (cx - max(1, self.radius // 3), cy - max(1, self.radius // 3)), max(2, self.radius // 3))

        elif elem == "Viento":
            # Turbina ciclónica de 4 aspas cortantes con anillo de vórtice translúcido
            rot = self.anim_time * 24.0
            r = self.radius
            pts = []
            for k in range(4):
                ang = rot + (math.pi / 2) * k
                pts.append((cx + int(math.cos(ang) * (r + 7)), cy + int(math.sin(ang) * (r + 7))))
                mid_ang = ang + 0.38
                pts.append((cx + int(math.cos(mid_ang) * (r * 0.35)), cy + int(math.sin(mid_ang) * (r * 0.35))))
            if len(pts) >= 4:
                pygame.draw.polygon(surface, (26, 188, 156), pts)
                pygame.draw.polygon(surface, (160, 240, 220), pts, 1)
            pygame.draw.circle(surface, (160, 245, 230), (cx, cy), max(2, r - 3), 1)
            pygame.draw.circle(surface, COLOR_WHITE, (cx, cy), max(2, r // 2))

        elif elem == "Tierra":
            # Meteorito facetado poligonal con grietas de lava brillantes y fragmentos rocosos
            rot = self.anim_time * 7.0
            pts = []
            sides = 7
            for k in range(sides):
                ang = rot + (2 * math.pi / sides) * k
                var = 1.0 + 0.22 * math.sin(k * 2.3)
                pts.append((cx + int(math.cos(ang) * self.radius * var), cy + int(math.sin(ang) * self.radius * var)))
            pygame.draw.polygon(surface, (140, 70, 35), pts)
            pygame.draw.polygon(surface, (80, 35, 18), pts, 2)
            # Grietas de magma brillantes
            pygame.draw.line(surface, (255, 160, 40), (cx - 4, cy - 3), (cx + 5, cy + 4), 2)
            pygame.draw.line(surface, (255, 225, 90), (cx - 1, cy + 1), (cx + 6, cy - 4), 1)
            pygame.draw.circle(surface, (220, 180, 140), (cx, cy), max(1, self.radius // 3))

        elif elem == "Trueno":
            # Núcleo de plasma eléctrico con rayos en zigzag parpadeantes de alto voltaje
            pygame.draw.circle(surface, (255, 235, 90), (cx, cy), self.radius + 1)
            pygame.draw.circle(surface, (243, 156, 18), (cx, cy), self.radius)
            pygame.draw.circle(surface, COLOR_WHITE, (cx, cy), max(2, self.radius // 2))
            for k in range(4):
                ang = (self.anim_time * 36.0) + (k * 1.57)
                mid_x = cx + int(math.cos(ang + 0.3) * (self.radius + 4))
                mid_y = cy + int(math.sin(ang + 0.3) * (self.radius + 4))
                sx = cx + int(math.cos(ang) * (self.radius + 10))
                sy = cy + int(math.sin(ang) * (self.radius + 10))
                pygame.draw.line(surface, (255, 255, 180), (cx, cy), (mid_x, mid_y), 2)
                pygame.draw.line(surface, COLOR_WHITE, (mid_x, mid_y), (sx, sy), 2)

        elif elem == "Naturaleza":
            # Semilla de zarza esmeralda con hojas de espinas, zarcillos y núcleo bioluminiscente
            pygame.draw.circle(surface, (39, 174, 96), (cx, cy), self.radius)
            pygame.draw.circle(surface, (46, 204, 113), (cx, cy), max(2, self.radius - 3))
            rot = self.anim_time * 12.0
            for k in range(4):
                ang = rot + (math.pi / 2) * k
                lx = cx + int(math.cos(ang) * (self.radius + 6))
                ly = cy + int(math.sin(ang) * (self.radius + 6))
                pygame.draw.line(surface, (30, 130, 60), (cx, cy), (lx, ly), 2)
                pygame.draw.circle(surface, (160, 255, 120), (lx, ly), 3)
            pygame.draw.circle(surface, COLOR_WHITE, (cx, cy), max(1, self.radius // 3))

        elif elem in ("Vapor (Steampunk)", "Vapor"):
            # Cápsula de bronce a presión con engranaje dentado, remaches y vapor hirviente
            rot = self.anim_time * 8.0
            teeth = 8
            pts = []
            for k in range(teeth):
                ang = rot + (2 * math.pi / teeth) * k
                pts.append((cx + int(math.cos(ang) * (self.radius + 4)), cy + int(math.sin(ang) * (self.radius + 4))))
                mid_ang = ang + (math.pi / teeth)
                pts.append((cx + int(math.cos(mid_ang) * (self.radius - 1)), cy + int(math.sin(mid_ang) * (self.radius - 1))))
            pygame.draw.polygon(surface, COLOR_BRASS, pts)
            pygame.draw.circle(surface, COLOR_COPPER, (cx, cy), self.radius, 2)
            pygame.draw.circle(surface, (220, 235, 245), (cx, cy), max(2, self.radius // 2))
            pygame.draw.circle(surface, COLOR_WHITE, (cx, cy), max(1, self.radius // 3))

        elif elem == "Metal":
            # Sierra circular rotatoria de acero con filo plateado deslumbrante y núcleo remachado
            rot = self.anim_time * 28.0
            pts = []
            teeth = 8
            for k in range(teeth):
                ang = rot + (2 * math.pi / teeth) * k
                pts.append((cx + int(math.cos(ang) * (self.radius + 6)), cy + int(math.sin(ang) * (self.radius + 6))))
                mid_ang = ang + (math.pi / teeth)
                pts.append((cx + int(math.cos(mid_ang) * (self.radius * 0.45)), cy + int(math.sin(mid_ang) * (self.radius * 0.45))))
            pygame.draw.polygon(surface, (220, 225, 235), pts)
            pygame.draw.polygon(surface, (130, 140, 150), pts, 1)
            pygame.draw.circle(surface, COLOR_BRASS, (cx, cy), max(2, self.radius // 2))
            pygame.draw.circle(surface, COLOR_WHITE, (cx, cy), max(1, self.radius // 3))

        elif elem == "Oscuridad":
            # Agujero negro cósmico: horizonte de sucesos, espirales de acreción violeta y núcleo abisal
            aura_rad = self.radius + int(4 * math.sin(self.anim_time * 14.0)) + 4
            pygame.draw.circle(surface, (155, 89, 182), (cx, cy), aura_rad, 2)
            rot = self.anim_time * 16.0
            for arm in [0.0, math.pi]:
                spiral_pts = []
                for st in range(5):
                    s_rad = (self.radius * (st + 1)) / 4.0
                    s_ang = rot + arm + st * 0.45
                    spiral_pts.append((cx + int(math.cos(s_ang) * s_rad), cy + int(math.sin(s_ang) * s_rad)))
                if len(spiral_pts) >= 2:
                    pygame.draw.lines(surface, (185, 120, 225), False, spiral_pts, 1)
            pygame.draw.circle(surface, (90, 30, 120), (cx, cy), self.radius + 1)
            pygame.draw.circle(surface, (15, 8, 24), (cx, cy), max(3, self.radius - 2))
            pygame.draw.circle(surface, (0, 0, 0), (cx, cy), max(2, self.radius - 4))

        elif elem == "Luz":
            # Estrella solar celestial de 8 rayos volumétricos, cruz destellante y núcleo dorado divino
            r = self.radius + 8
            pts = []
            for k in range(8):
                ang = (math.pi / 4) * k + self.anim_time * 2.0
                pts.append((cx + int(math.cos(ang) * r), cy + int(math.sin(ang) * r)))
                mid_ang = ang + (math.pi / 8)
                pts.append((cx + int(math.cos(mid_ang) * (r * 0.35)), cy + int(math.sin(mid_ang) * (r * 0.35))))
            pygame.draw.polygon(surface, (255, 255, 220), pts)
            pygame.draw.polygon(surface, COLOR_GOLD, pts, 1)
            pygame.draw.line(surface, COLOR_WHITE, (cx - r - 2, cy), (cx + r + 2, cy), 1)
            pygame.draw.line(surface, COLOR_WHITE, (cx, cy - r - 2), (cx, cy + r + 2), 1)
            pygame.draw.circle(surface, COLOR_WHITE, (cx, cy), 4)

        else:
            pygame.draw.circle(surface, self.color, (cx, cy), self.radius)
            pygame.draw.circle(surface, COLOR_WHITE, (cx, cy), max(2, self.radius // 2))


class GroundHazard:
    """
    Zona de Terreno Activa (Inspirada en Wizard of Legend):
    - Lava ardiente: Daño continuo por quemadura con burbujas animadas.
    - Vórtice Ciclónico: Succión gravitatoria física con espirales rotatorias.
    - Singularidad Abisal: Agujero negro con horizonte de sucesos y atracción.
    - Zarzas: Enraíza (inmoviliza) con enredaderas y espinas.
    - Roca: Picos sísmicos emergentes de la tierra.
    """

    def __init__(self, x: float, y: float, hazard_type: str, radius: float,
                 duration: float, damage_per_sec: float, color, is_player=True):
        self.pos = pygame.math.Vector2(x, y)
        self.hazard_type = hazard_type
        self.radius = radius
        self.duration = duration
        self.max_duration = duration
        self.damage_per_sec = damage_per_sec
        self.color = color
        self.is_player = is_player
        self.tick_timer = 0.0
        self.is_sanctuary = (hazard_type == "Santuario")
        self.blocks_bullets = (hazard_type == "Roca")
        self.pulls_enemies = (hazard_type in ("Vórtice", "Singularidad"))

    def update(self, dt: float, player, enemies, combat_system) -> bool:
        self.duration -= dt
        self.tick_timer += dt

        # Succión física para Vórtice de Viento y Singularidad de Oscuridad
        if self.hazard_type in ("Vórtice", "Singularidad"):
            suction_power = 240.0 if self.hazard_type == "Singularidad" else 150.0
            for enemy in enemies:
                diff = self.pos - enemy.pos
                dist = diff.length()
                if 0 < dist < self.radius * 2.4:
                    pull_force = diff.normalize() * (suction_power * (1.0 - dist / (self.radius * 2.5)))
                    enemy.pos += pull_force * dt

        # Santuario Celestial de Luz: Sana al jugador continuamente
        if self.is_sanctuary and player:
            dist = (self.pos - player.pos).length()
            if dist <= self.radius:
                player.heal(25.0 * dt)

        # Monolitos de Roca: Bloquean y absorben balas enemigas
        if self.blocks_bullets and combat_system:
            for o in list(combat_system.projectiles):
                if not o.is_player and (self.pos - o.pos).length() <= self.radius + o.radius:
                    combat_system.emit_impact_particles(o.pos.x, o.pos.y, count=6, color=(160, 82, 45))
                    combat_system.projectiles.remove(o)

        # Tics periódicos de daño cada 0.25s
        if self.tick_timer >= 0.25:
            self.tick_timer = 0.0
            damage_tick = self.damage_per_sec * 0.25

            if self.is_player:
                for enemy in enemies:
                    dist = (self.pos - enemy.pos).length()
                    if dist <= self.radius + enemy.radius:
                        enemy.take_damage(damage_tick)
                        combat_system.create_damage_text(enemy.pos.x, enemy.pos.y - 10,
                                                         damage_tick, color=self.color)
                        # Efecto de inmovilización para zarzas
                        if self.hazard_type == "Zarzas":
                            enemy.attack_timer = max(enemy.attack_timer, 0.4)

                        # Drenaje vampírico de singularidad oscura
                        if self.hazard_type == "Singularidad":
                            player.heal(damage_tick * 0.35)
            else:
                # Daño al jugador si es trampa de enemigo/jefe
                dist = (self.pos - player.pos).length()
                if dist <= self.radius + player.radius:
                    if player.take_damage(damage_tick):
                        combat_system.create_damage_text(player.pos.x, player.pos.y - 10,
                                                         damage_tick, color=COLOR_RED_HEALTH)

        return self.duration > 0

    def draw(self, surface: pygame.Surface):
        alpha_ratio = max(0.0, self.duration / self.max_duration)
        alpha = int(120 * alpha_ratio)
        cx, cy = int(self.pos.x), int(self.pos.y)
        r = int(self.radius)

        surf_size = r * 2 + 10
        hazard_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        hc = (r + 5, r + 5)

        # 1. Base translúcida elemental
        color_with_alpha = (*self.color[:3], alpha)
        pygame.draw.circle(hazard_surf, color_with_alpha, hc, r)
        pygame.draw.circle(hazard_surf, (*self.color[:3], int(alpha * 1.5)), hc, r, 2)

        # 2. Detalles visuales animados según el tipo de terreno
        if self.hazard_type == "Lava":
            for k in range(4):
                bx = hc[0] + int(r * 0.45 * math.sin(self.duration * 4.0 + k * 1.5))
                by = hc[1] + int(r * 0.45 * math.cos(self.duration * 4.0 + k * 2.2))
                b_size = max(2, int(6 * abs(math.sin(self.duration * 6.0 + k))))
                pygame.draw.circle(hazard_surf, (255, 220, 80, alpha), (bx, by), b_size)

        elif self.hazard_type in ("Vórtice", "Ciclón"):
            rot = self.duration * 6.0
            for arm in range(3):
                arm_pts = []
                for step in range(5):
                    step_rad = (r * (step + 1)) / 5.0
                    ang = rot + (arm * 2.09) + (step * 0.35)
                    arm_pts.append((hc[0] + int(math.cos(ang) * step_rad),
                                    hc[1] + int(math.sin(ang) * step_rad)))
                if len(arm_pts) >= 2:
                    pygame.draw.lines(hazard_surf, (255, 255, 255, alpha), False, arm_pts, 2)

        elif self.hazard_type == "Zarzas":
            for arm in range(4):
                ang = (arm * 1.57) + 0.3
                ex = hc[0] + int(math.cos(ang) * r * 0.8)
                ey = hc[1] + int(math.sin(ang) * r * 0.8)
                pygame.draw.line(hazard_surf, (20, 90, 40, alpha), hc, (ex, ey), 3)
                pygame.draw.circle(hazard_surf, (140, 240, 90, alpha), (ex, ey), 4)

        elif self.hazard_type == "Singularidad":
            pygame.draw.circle(hazard_surf, (10, 5, 20, int(220 * alpha_ratio)), hc, int(r * 0.4))
            pygame.draw.circle(hazard_surf, (142, 68, 173, alpha), hc, int(r * 0.4), 2)

        elif self.hazard_type == "Roca":
            for k in [-14, 0, 14]:
                spike_pts = [
                    (hc[0] + k - 8, hc[1] + 10),
                    (hc[0] + k, hc[1] - 16),
                    (hc[0] + k + 8, hc[1] + 10)
                ]
                pygame.draw.polygon(hazard_surf, (160, 82, 45, alpha), spike_pts)
                pygame.draw.polygon(hazard_surf, (90, 45, 25, alpha), spike_pts, 2)

        elif self.hazard_type == "Vapor":
            # Nube densa de vapor hirviente pulsante
            for k in range(5):
                vx = hc[0] + int(r * 0.4 * math.cos(self.duration * 3.0 + k * 1.25))
                vy = hc[1] + int(r * 0.4 * math.sin(self.duration * 3.0 + k * 1.25))
                v_size = max(4, int(12 * abs(math.sin(self.duration * 4.0 + k))))
                pygame.draw.circle(hazard_surf, (220, 235, 245, int(alpha * 0.8)), (vx, vy), v_size)
            pygame.draw.circle(hazard_surf, (200, 225, 240, alpha), hc, int(r * 0.7), 2)

        elif self.hazard_type == "Santuario":
            # Santuario bendito con runas de luz celestial y rayos dorados
            pygame.draw.circle(hazard_surf, (255, 245, 200, int(alpha * 0.5)), hc, r)
            pygame.draw.circle(hazard_surf, (241, 196, 15, alpha), hc, r, 2)
            pygame.draw.circle(hazard_surf, (255, 255, 255, alpha), hc, int(r * 0.5), 1)
            # Rayos celestiales de 8 puntas
            for i in range(8):
                ang = (self.duration * 0.5) + (i * 0.785)
                px = hc[0] + int(math.cos(ang) * (r * 0.85))
                py = hc[1] + int(math.sin(ang) * (r * 0.85))
                pygame.draw.line(hazard_surf, (255, 255, 220, alpha), hc, (px, py), 1)

        surface.blit(hazard_surf, (cx - r - 5, cy - r - 5))


class Shockwave:
    """Onda de choque anular expansiva en 360° que debe esquivarse con Dash."""

    def __init__(self, x: float, y: float, max_radius: float, speed: float,
                 damage: float, color=COLOR_GOLD, is_player=False):
        self.pos = pygame.math.Vector2(x, y)
        self.current_radius = 15.0
        self.max_radius = max_radius
        self.speed = speed
        self.damage = damage
        self.color = color
        self.is_player = is_player
        self.hit_targets = set()

    def update(self, dt: float, player, enemies, combat_system) -> bool:
        self.current_radius += self.speed * dt

        if not self.is_player:
            dist = (self.pos - player.pos).length()
            if abs(dist - self.current_radius) <= player.radius + 12:
                if player not in self.hit_targets and not player.is_dashing:
                    if player.take_damage(self.damage):
                        combat_system.trigger_screen_shake(intensity=5.5, duration=0.20)
                        combat_system.create_damage_text(player.pos.x, player.pos.y - 15,
                                                         self.damage, color=(255, 60, 60), is_critical=True)
                        combat_system.emit_impact_particles(player.pos.x, player.pos.y, count=14,
                                                            color=self.color)
                    self.hit_targets.add(player)

        return self.current_radius < self.max_radius

    def draw(self, surface: pygame.Surface):
        progress = min(1.0, max(0.0, self.current_radius / max(1.0, self.max_radius)))
        alpha = max(0, min(255, int((1.0 - progress) * 230)))
        if alpha <= 0:
            return

        cx, cy = int(self.pos.x), int(self.pos.y)
        r = int(self.current_radius)
        if r <= 2:
            return

        sw_surf = pygame.Surface((r * 2 + 12, r * 2 + 12), pygame.SRCALPHA)
        sc = (r + 6, r + 6)

        # 1. Halo difuso exterior translúcido
        glow_col = (*self.color[:3], int(alpha * 0.35))
        pygame.draw.circle(sw_surf, glow_col, sc, r + 2, 4)

        # 2. Cresta anular principal
        main_col = (*self.color[:3], alpha)
        pygame.draw.circle(sw_surf, main_col, sc, r, 2)

        # 3. Onda de compresión interior de alta energía
        if r > 6:
            inner_col = (255, 255, 255, int(alpha * 0.65))
            pygame.draw.circle(sw_surf, inner_col, sc, max(1, r - 3), 1)

        surface.blit(sw_surf, (cx - r - 6, cy - r - 6))


class CombatSystem:
    """Controlador central de combates, físicas arcanas y hechizos creativos."""

    def __init__(self, audio_system=None):
        self.audio_system = audio_system
        self.damage_texts = []
        self.particles = []
        self.projectiles = []
        self.ground_hazards = []
        self.shockwaves = []
        self.lightning_chains = []  # Rayos encadenados animados
        self.font = pygame.font.SysFont("Consolas", 18, bold=True)
        self.screen_shake_time = 0.0
        self.screen_shake_intensity = 0.0

    def play_sfx(self, name: str, volume: float = 1.0):
        """Reproduce un efecto de sonido a través del subsistema de audio si está configurado."""
        if self.audio_system:
            self.audio_system.play_sfx(name, volume)

    def trigger_screen_shake(self, intensity=4.0, duration=0.16):
        """Activa una sacudida de pantalla cinemática para impactos contundentes."""
        self.screen_shake_time = max(self.screen_shake_time, duration)
        self.screen_shake_intensity = max(self.screen_shake_intensity, intensity)

    def get_screen_shake_offset(self) -> tuple:
        """Calcula el desplazamiento X, Y actual de la pantalla si hay sacudida activa."""
        if self.screen_shake_time > 0:
            ox = random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity)
            oy = random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity)
            return (int(ox), int(oy))
        return (0, 0)

    def create_damage_text(self, x: float, y: float, amount: float, color=COLOR_WHITE, is_critical=False):
        self.damage_texts.append(DamageText(x, y, amount, color, is_critical))

    def emit_impact_particles(self, x: float, y: float, count=10, color=COLOR_STEAM):
        for _ in range(count):
            self.particles.append(Particle(x, y, color=color, speed=160.0, life=0.35, size=4))

    def spawn_ground_hazard(self, x: float, y: float, hazard_type: str, radius: float,
                            duration: float, damage_per_sec: float, color, is_player=True):
        """Crea una zona elemental persistente en el suelo."""
        hz = GroundHazard(x, y, hazard_type, radius, duration, damage_per_sec, color, is_player)
        self.ground_hazards.append(hz)

    def spawn_shockwave(self, x: float, y: float, max_radius=320.0, speed=260.0,
                        damage=45.0, color=COLOR_GOLD, is_player=False):
        """Genera un anillo expansivo en 360°."""
        sw = Shockwave(x, y, max_radius, speed, damage, color, is_player)
        self.shockwaves.append(sw)

    def spawn_projectile(self, x: float, y: float, dir_x: float, dir_y: float,
                         damage: float, speed=400.0, element="Fuego", is_player=True,
                         radius=10, pierces=False, on_hit_effect=None):
        proj = Projectile(x, y, dir_x, dir_y, damage, speed, element, is_player,
                          radius, pierces, on_hit_effect)
        self.projectiles.append(proj)

    def cast_basic_arcane_bolt(self, player, target_pos: tuple) -> bool:
        """
        Dardo Arcano de Éter básico para el Mago (Clic Izquierdo).
        Costo: 0 MP (Auto-ataque infinito a distancia).
        Efecto: Daño moderado y recarga +15 MP por cada impacto acertado para nunca quedar bloqueado.
        """
        dir_vec = pygame.math.Vector2(target_pos[0] - player.pos.x, target_pos[1] - player.pos.y)
        if dir_vec.length_squared() > 0:
            dir_norm = dir_vec.normalize()
        else:
            dir_norm = player.aim_vector.copy()

        def on_arcane_hit(pos):
            # Recargar maná al acertar al enemigo
            player.restore_mana(15.0)
            self.create_damage_text(player.pos.x + random.uniform(-10, 10), player.pos.y - 30,
                                    "+15 MP", color=(155, 89, 182))
            self.emit_impact_particles(pos.x, pos.y, count=14, color=(175, 110, 210))

        bolt_damage = 42.0 * player.bonus_damage_mult
        self.play_sfx("magic_bolt")
        self.spawn_projectile(
            x=player.pos.x + dir_norm.x * 22,
            y=player.pos.y + dir_norm.y * 22,
            dir_x=dir_norm.x,
            dir_y=dir_norm.y,
            damage=bolt_damage,
            speed=560.0,
            element="Luz",
            is_player=True,
            radius=9,
            on_hit_effect=on_arcane_hit
        )
        self.emit_impact_particles(player.pos.x + dir_norm.x * 20,
                                   player.pos.y + dir_norm.y * 20,
                                   count=6, color=(155, 89, 182))
        return True

    def cast_player_active_magic(self, player, element: str, target_pos: tuple, targets=None) -> bool:
        """
        Despliega hechizos avanzados inspirados en 'Wizard of Legend':
        Cada elemento consume maná específico y posee mecánicas únicas de área y físicas.
        """
        # Comprobar costo de Maná de la reserva de 500 MP
        mana_cost = MANA_SPELL_COSTS.get(element, 75)
        if not player.has_mana(mana_cost):
            self.create_damage_text(player.pos.x, player.pos.y - 30, f"¡Sin Maná ({mana_cost} MP)!",
                                    color=(52, 152, 219), is_critical=True)
            return False

        # Consumir maná
        player.spend_mana(mana_cost)

        elem_sfx_map = {
            "Fuego": "spell_fire", "Trueno": "spell_thunder", "Agua": "spell_water",
            "Viento": "spell_wind", "Tierra": "spell_earth", "Naturaleza": "spell_nature",
            "Luz": "spell_light", "Oscuridad": "spell_darkness", "Vapor": "spell_steam",
            "Vapor (Steampunk)": "spell_steam", "Metal": "spell_metal"
        }
        self.play_sfx(elem_sfx_map.get(element, "spell_fire"))

        dir_vec = pygame.math.Vector2(target_pos[0] - player.pos.x, target_pos[1] - player.pos.y)
        dist_to_target = dir_vec.length()
        if dist_to_target > 0:
            dir_norm = dir_vec.normalize()
        else:
            dir_norm = player.aim_vector.copy()

        # 1. FUEGO: Meteorito Cataclísmico con Onda de Choque, Caldera Ígnea y Chispas Rebotantes
        if element == "Fuego":
            def on_meteor_impact(pos):
                self.spawn_shockwave(pos.x, pos.y, max_radius=115.0, speed=320.0,
                                     damage=90.0 * player.bonus_damage_mult, color=(255, 90, 20), is_player=True)
                self.spawn_ground_hazard(pos.x, pos.y, "Lava", radius=75.0, duration=3.5,
                                         damage_per_sec=85.0, color=(231, 76, 60))
                for diag_ang in [0.78, 2.35, 3.92, 5.49]:
                    p = Projectile(pos.x, pos.y, math.cos(diag_ang), math.sin(diag_ang),
                                   damage=40.0 * player.bonus_damage_mult, speed=380.0,
                                   element="Fuego", is_player=True, radius=8, pierces=True)
                    p.ricochets_left = 2
                    self.projectiles.append(p)
                self.emit_impact_particles(pos.x, pos.y, count=35, color=(255, 120, 20))

            self.spawn_projectile(
                x=player.pos.x + dir_norm.x * 24, y=player.pos.y + dir_norm.y * 24,
                dir_x=dir_norm.x, dir_y=dir_norm.y,
                damage=95.0 * player.bonus_damage_mult, speed=520.0,
                element="Fuego", is_player=True, radius=16, on_hit_effect=on_meteor_impact
            )

        # 2. AGUA: Maremoto Penetrante en Creciente + 3 Burbujas Cautivas Teledirigidas
        elif element == "Agua":
            base_angle = math.atan2(dir_norm.y, dir_norm.x)
            for ang_offset in [-0.22, 0.0, 0.22]:
                shoot_ang = base_angle + ang_offset
                self.spawn_projectile(
                    x=player.pos.x + dir_norm.x * 24, y=player.pos.y + dir_norm.y * 24,
                    dir_x=math.cos(shoot_ang), dir_y=math.sin(shoot_ang),
                    damage=60.0 * player.bonus_damage_mult, speed=460.0,
                    element="Agua", is_player=True, radius=13, pierces=True
                )
            for b_ang in [-0.45, 0.0, 0.45]:
                bubble = Projectile(
                    player.pos.x + dir_norm.x * 26, player.pos.y + dir_norm.y * 26,
                    math.cos(base_angle + b_ang), math.sin(base_angle + b_ang),
                    damage=45.0 * player.bonus_damage_mult, speed=320.0,
                    element="Agua", is_player=True, radius=9, pierces=False
                )
                bubble.is_homing = True
                self.projectiles.append(bubble)
            self.emit_impact_particles(player.pos.x + dir_norm.x * 25, player.pos.y + dir_norm.y * 25,
                                       count=20, color=(0, 220, 245))

        # 3. VIENTO: Búmeran Ciclónico con Vórtice Succionador y Destrucción de Proyectiles
        elif element == "Viento":
            boomerang = Projectile(
                player.pos.x + dir_norm.x * 24, player.pos.y + dir_norm.y * 24,
                dir_x=dir_norm.x, dir_y=dir_norm.y,
                damage=65.0 * player.bonus_damage_mult, speed=520.0,
                element="Viento", is_player=True, radius=14, pierces=True
            )
            boomerang.is_boomerang = True
            boomerang.destroys_bullets = True
            boomerang.boomerang_max_dist = min(360.0, max(120.0, dist_to_target))
            self.projectiles.append(boomerang)

            vort_x = player.pos.x + dir_norm.x * min(280.0, dist_to_target)
            vort_y = player.pos.y + dir_norm.y * min(280.0, dist_to_target)
            self.spawn_ground_hazard(vort_x, vort_y, "Vórtice", radius=95.0,
                                     duration=2.8, damage_per_sec=70.0, color=(26, 188, 156))
            self.emit_impact_particles(player.pos.x + dir_norm.x * 25, player.pos.y + dir_norm.y * 25,
                                       count=18, color=(26, 188, 156))

        # 4. TIERRA: Fractura Tectónica con 4 Monolitos Defensivos que Bloquean Balas
        elif element == "Tierra":
            for i in range(1, 5):
                spike_x = player.pos.x + dir_norm.x * (i * 62.0)
                spike_y = player.pos.y + dir_norm.y * (i * 62.0)
                rock_hz = GroundHazard(spike_x, spike_y, "Roca", radius=38.0,
                                       duration=2.8, damage_per_sec=95.0, color=(160, 82, 45), is_player=True)
                rock_hz.blocks_bullets = True
                self.ground_hazards.append(rock_hz)
                self.emit_impact_particles(spike_x, spike_y, count=12, color=(120, 60, 30))
            self.spawn_shockwave(player.pos.x, player.pos.y, max_radius=90.0, speed=280.0,
                                 damage=50.0 * player.bonus_damage_mult, color=(160, 82, 45), is_player=True)

        # 5. TRUENO: Cadena de Relámpagos Bifurcados (True Chain Lightning Fractal)
        elif element == "Trueno":
            self.spawn_chain_lightning(player, target_pos, enemies=targets)

        # 6. NATURALEZA: Enredadera Parásita e Invocación de Flor de Esporas Drenadoras
        elif element == "Naturaleza":
            def on_nature_impact(pos):
                vine_hz = GroundHazard(pos.x, pos.y, "Zarzas", radius=80.0, duration=3.0,
                                       damage_per_sec=75.0, color=(39, 174, 96), is_player=True)
                self.ground_hazards.append(vine_hz)
                player.heal(15.0)
                self.create_damage_text(player.pos.x, player.pos.y - 25, "+15 HP (Drenaje)",
                                        color=(46, 204, 113), is_critical=True)
                self.emit_impact_particles(pos.x, pos.y, count=22, color=(46, 204, 113))

            self.spawn_projectile(
                x=player.pos.x + dir_norm.x * 24, y=player.pos.y + dir_norm.y * 24,
                dir_x=dir_norm.x, dir_y=dir_norm.y,
                damage=70.0 * player.bonus_damage_mult, speed=460.0,
                element="Naturaleza", is_player=True, radius=13, on_hit_effect=on_nature_impact
            )

        # 7. LUZ (EXCLUSIVA DORADA): Lanza Solar Celestial & Santuario Bendito (+25 HP/s y +35% DMG)
        elif element == "Luz":
            impact_x = player.pos.x + dir_norm.x * min(280.0, dist_to_target)
            impact_y = player.pos.y + dir_norm.y * min(280.0, dist_to_target)

            player.heal(50.0)
            self.create_damage_text(player.pos.x, player.pos.y - 35, "+50 HP", color=(254, 249, 231), is_critical=True)
            self.spawn_shockwave(impact_x, impact_y, max_radius=130.0, speed=380.0,
                                 damage=130.0 * player.bonus_damage_mult, color=(255, 255, 220), is_player=True)

            for i in range(8):
                theta = (2 * math.pi / 8) * i
                self.spawn_projectile(
                    x=impact_x, y=impact_y,
                    dir_x=math.cos(theta), dir_y=math.sin(theta),
                    damage=85.0 * player.bonus_damage_mult, speed=480.0,
                    element="Luz", is_player=True, radius=12, pierces=True
                )

            sanctuary = GroundHazard(impact_x, impact_y, "Santuario", radius=95.0,
                                     duration=4.5, damage_per_sec=30.0, color=(254, 249, 231), is_player=True)
            sanctuary.is_sanctuary = True
            self.ground_hazards.append(sanctuary)
            self.emit_impact_particles(impact_x, impact_y, count=40, color=(255, 255, 240))

        # 8. OSCURIDAD (EXCLUSIVA DORADA): Singularidad Abisal Total con Implosión Vampírica
        elif element == "Oscuridad":
            sing_x = player.pos.x + dir_norm.x * min(260.0, dist_to_target)
            sing_y = player.pos.y + dir_norm.y * min(260.0, dist_to_target)

            singularity = GroundHazard(sing_x, sing_y, "Singularidad", radius=125.0,
                                       duration=3.0, damage_per_sec=140.0, color=(142, 68, 173), is_player=True)
            singularity.pulls_enemies = True
            self.ground_hazards.append(singularity)
            self.emit_impact_particles(sing_x, sing_y, count=35, color=(142, 68, 173))

        # 9. VAPOR: Deflagración Neumática 360° (Empuje violento, deflexión de balas y boost de velocidad)
        elif element in ("Vapor (Steampunk)", "Vapor"):
            self.spawn_shockwave(player.pos.x, player.pos.y, max_radius=135.0, speed=450.0,
                                 damage=75.0 * player.bonus_damage_mult, color=COLOR_STEAM, is_player=True)
            for other in list(self.projectiles):
                if not other.is_player and (other.pos - player.pos).length() <= 150.0:
                    self.emit_impact_particles(other.pos.x, other.pos.y, count=8, color=COLOR_STEAM)
                    self.projectiles.remove(other)

            self.spawn_ground_hazard(player.pos.x, player.pos.y, "Vapor", radius=90.0,
                                     duration=2.5, damage_per_sec=65.0, color=COLOR_STEAM)
            player.speed_mult = min(1.8, player.speed_mult + 0.35)
            self.create_damage_text(player.pos.x, player.pos.y - 30, "+35% Vel (Propulsor)",
                                    color=COLOR_STEAM, is_critical=True)
            self.emit_impact_particles(player.pos.x, player.pos.y, count=30, color=(220, 235, 245))

        # 10. METAL: Danza de Guillotinas Orbitantes con Rebote en Paredes
        elif element == "Metal":
            for k in range(3):
                saw = Projectile(
                    player.pos.x, player.pos.y, 1.0, 0.0,
                    damage=70.0 * player.bonus_damage_mult, speed=520.0,
                    element="Metal", is_player=True, radius=11, pierces=True
                )
                saw.is_orbiting = True
                saw.orbit_angle = (2 * math.pi / 3) * k
                saw.orbit_radius = 58.0
                saw.lifetime = 3.2
                self.projectiles.append(saw)
            self.emit_impact_particles(player.pos.x, player.pos.y, count=20, color=(190, 195, 205))

        elem_col = ELEMENT_COLORS.get(element, COLOR_GOLD)
        self.emit_impact_particles(player.pos.x + dir_norm.x * 20,
                                   player.pos.y + dir_norm.y * 20,
                                   count=8, color=elem_col)
        return True

    def spawn_chain_lightning(self, player, target_pos: tuple, enemies=None):
        """Despliega un relámpago bifurcado que salta instantáneamente entre múltiples enemigos."""
        if enemies is None:
            enemies = []

        initial_target = None
        min_dist = 280.0
        t_vec = pygame.math.Vector2(target_pos[0], target_pos[1])
        for e in enemies:
            if getattr(e, 'is_alive', True):
                d = (e.pos - t_vec).length()
                if d < min_dist:
                    min_dist = d
                    initial_target = e

        if initial_target is None:
            min_dist = 360.0
            for e in enemies:
                if getattr(e, 'is_alive', True):
                    d = (e.pos - player.pos).length()
                    if d < min_dist:
                        min_dist = d
                        initial_target = e

        segments = []
        struck_targets = set()
        prev_pos = (player.pos.x, player.pos.y)

        if initial_target:
            curr = initial_target
            dmg = 100.0 * player.bonus_damage_mult
            for _ in range(5):
                curr.take_damage(dmg)
                curr.hit_flash_timer = 0.10
                struck_targets.add(curr)
                self.create_damage_text(curr.pos.x, curr.pos.y - 15, dmg, color=COLOR_GOLD, is_critical=True)
                self.emit_impact_particles(curr.pos.x, curr.pos.y, count=14, color=COLOR_GOLD)

                p1 = prev_pos
                p2 = (curr.pos.x, curr.pos.y)
                mid1 = ((p1[0] * 2 + p2[0]) / 3 + random.uniform(-12, 12),
                        (p1[1] * 2 + p2[1]) / 3 + random.uniform(-12, 12))
                mid2 = ((p1[0] + p2[0] * 2) / 3 + random.uniform(-12, 12),
                        (p1[1] + p2[1] * 2) / 3 + random.uniform(-12, 12))
                segments.extend([(p1, mid1), (mid1, mid2), (mid2, p2)])

                prev_pos = p2
                dmg *= 0.80

                next_target = None
                closest_d = 240.0
                for other in enemies:
                    if getattr(other, 'is_alive', True) and other not in struck_targets:
                        d = (other.pos - curr.pos).length()
                        if d < closest_d:
                            closest_d = d
                            next_target = other
                if not next_target:
                    break
                curr = next_target
        else:
            p1 = (player.pos.x, player.pos.y)
            p2 = (target_pos[0], target_pos[1])
            mid1 = ((p1[0] + p2[0]) / 2 + random.uniform(-15, 15), (p1[1] + p2[1]) / 2 + random.uniform(-15, 15))
            segments.extend([(p1, mid1), (mid1, p2)])
            self.emit_impact_particles(target_pos[0], target_pos[1], count=16, color=COLOR_GOLD)

        if segments:
            self.lightning_chains.append({"segments": segments, "timer": 0.22, "color": COLOR_GOLD})

    def cast_cannon_shell(self, player, enemies) -> bool:
        """Dispara una bala de mortero pesado de vapor que detona al impacto."""
        self.play_sfx("cannon_shot")
        dir_norm = player.aim_vector.copy()
        raw_damage = (player.base_damage + player.weapon_damage) * player.bonus_damage_mult

        def on_shell_hit(pos):
            self.spawn_shockwave(pos.x, pos.y, max_radius=85.0, speed=280.0,
                                 damage=raw_damage * 0.6, color=(255, 140, 20), is_player=True)
            self.spawn_ground_hazard(pos.x, pos.y, "Vapor", radius=65.0, duration=1.8,
                                     damage_per_sec=55.0, color=COLOR_STEAM)
            self.emit_impact_particles(pos.x, pos.y, count=25, color=(255, 150, 30))
            player.restore_mana(MANA_REGEN_MELEE_HIT)

        self.spawn_projectile(
            x=player.pos.x + dir_norm.x * 26, y=player.pos.y + dir_norm.y * 26,
            dir_x=dir_norm.x, dir_y=dir_norm.y,
            damage=raw_damage, speed=560.0,
            element="Vapor", is_player=True, radius=13, on_hit_effect=on_shell_hit
        )
        self.emit_impact_particles(player.pos.x + dir_norm.x * 24, player.pos.y + dir_norm.y * 24,
                                   count=12, color=COLOR_STEAM)
        return True

    def cast_alchemist_flask(self, player, enemies) -> bool:
        """Lanza un frasco alquímico volátil que estalla en un charco de fuego y miasma ácido."""
        self.play_sfx("flask_throw")
        dir_norm = player.aim_vector.copy()
        raw_damage = (player.base_damage + player.weapon_damage) * player.bonus_damage_mult

        def on_flask_hit(pos):
            self.spawn_ground_hazard(pos.x, pos.y, "Lava", radius=55.0, duration=2.5,
                                     damage_per_sec=65.0, color=(46, 204, 113))
            self.emit_impact_particles(pos.x, pos.y, count=20, color=(46, 204, 113))
            player.restore_mana(MANA_REGEN_MELEE_HIT)

        self.spawn_projectile(
            x=player.pos.x + dir_norm.x * 24, y=player.pos.y + dir_norm.y * 24,
            dir_x=dir_norm.x, dir_y=dir_norm.y,
            damage=raw_damage, speed=480.0,
            element="Naturaleza", is_player=True, radius=10, on_hit_effect=on_flask_hit
        )
        self.emit_impact_particles(player.pos.x + dir_norm.x * 22, player.pos.y + dir_norm.y * 22,
                                   count=8, color=(46, 204, 113))
        return True

    def cast_crossbow_bolt(self, player, targets) -> bool:
        """Dispara una saeta afilada de ballesta pesada a alta velocidad que perfora objetivos."""
        self.play_sfx("crossbow_shot")
        dir_norm = player.aim_vector.copy()
        raw_damage = (player.base_damage + player.weapon_damage) * player.bonus_damage_mult
        crit_chance = getattr(player, 'crit_chance', 0.15)
        is_crit = random.random() < crit_chance
        final_damage = raw_damage * (getattr(player, 'crit_multiplier', 2.0) if is_crit else 1.0)

        def on_bolt_hit(pos):
            self.emit_impact_particles(pos.x, pos.y, count=10, color=(212, 160, 23))
            player.restore_mana(MANA_REGEN_MELEE_HIT)

        self.spawn_projectile(
            x=player.pos.x + dir_norm.x * 26,
            y=player.pos.y + dir_norm.y * 26,
            dir_x=dir_norm.x,
            dir_y=dir_norm.y,
            damage=final_damage,
            speed=700.0,
            element="Metal",
            is_player=True,
            radius=6,
            pierces=True,
            on_hit_effect=on_bolt_hit
        )
        self.emit_impact_particles(player.pos.x + dir_norm.x * 22,
                                   player.pos.y + dir_norm.y * 22,
                                   count=6, color=(200, 195, 185))
        return True

    def process_player_melee_attack(self, player, enemies) -> int:
        """
        Cálculo del ataque del arma medieval según el arquetipo del jugador.
        Aplica alcance, ángulo, daño de arma, robo de vida y pasivas únicas.
        """
        w_type = getattr(player, 'weapon_type', 'sword')

        # Armas a distancia o arrojadizas
        if w_type == "crossbow":
            self.cast_crossbow_bolt(player, enemies)
            return 1
        elif w_type == "cannon":
            self.cast_cannon_shell(player, enemies)
            return 1
        elif w_type == "flask":
            self.cast_alchemist_flask(player, enemies)
            return 1

        hits = 0
        damage = player.total_damage

        # Amplitud angular y alcance según el arma medieval (12 arquetipos)
        w_ranges = {
            "sword": 82.0,
            "axe": 96.0,
            "mace": 78.0,
            "daggers": 70.0,
            "scythe": 105.0,
            "greatsword": 115.0,
            "fists": 68.0,
            "totem": 95.0,
            "flail": 92.0
        }
        w_arcs = {
            "sword": 110.0,
            "axe": 135.0,
            "mace": 90.0,
            "daggers": 80.0,
            "scythe": 145.0,
            "greatsword": 130.0,
            "fists": 70.0,
            "totem": 120.0,
            "flail": 360.0
        }
        attack_range = w_ranges.get(w_type, PLAYER_ATTACK_RANGE)
        attack_arc = w_arcs.get(w_type, PLAYER_ATTACK_ARC_DEG)

        half_arc = attack_arc / 2.0
        aim_deg = player.facing_angle

        cut_tip_x = player.pos.x + player.aim_vector.x * (attack_range * 0.7)
        cut_tip_y = player.pos.y + player.aim_vector.y * (attack_range * 0.7)

        w_p_colors = {
            "sword": COLOR_BRASS,
            "axe": (220, 40, 40),
            "mace": (255, 215, 70),
            "daggers": (46, 204, 113),
            "scythe": (155, 89, 182),
            "greatsword": (52, 152, 219),
            "fists": (241, 196, 15),
            "totem": (26, 188, 156),
            "flail": (192, 57, 43)
        }
        self.emit_impact_particles(cut_tip_x, cut_tip_y, count=5, color=w_p_colors.get(w_type, COLOR_BRASS))

        w_sfx = {
            "sword": "slash_sword", "axe": "axe_swing", "mace": "blunt_mace",
            "daggers": "dagger_slice", "scythe": "slash_scythe", "greatsword": "slash_greatsword",
            "fists": "fist_punch", "totem": "blunt_totem", "flail": "slash_flail"
        }
        self.play_sfx(w_sfx.get(w_type, "slash_sword"))

        for enemy in enemies:
            dx = enemy.pos.x - player.pos.x
            dy = enemy.pos.y - player.pos.y
            dist_sq = dx * dx + dy * dy

            effective_range = attack_range + enemy.radius
            if dist_sq <= effective_range * effective_range:
                angle_to_enemy = math.degrees(math.atan2(dy, dx))
                diff = (angle_to_enemy - aim_deg + 180) % 360 - 180

                # Para armas de 360° como el flail, abarca toda la circunferencia
                if abs(diff) <= half_arc or half_arc >= 179.0:
                    crit_chance = getattr(player, 'crit_chance', 0.15)
                    crit_mult = getattr(player, 'crit_multiplier', 2.0)
                    is_crit = random.random() < crit_chance
                    final_damage = damage * (crit_mult if is_crit else 1.0)

                    enemy.take_damage(final_damage)
                    enemy.hit_flash_timer = 0.08  # Parpadeo de impacto blanco
                    hits += 1
                    self.play_sfx("enemy_hit")
                    if is_crit:
                        self.trigger_screen_shake(intensity=3.2, duration=0.10)

                    # Robo de vida pasivo (Berserker Bárbaro - balanceado: +5 HP base, +8 si es crítico)
                    life_steal = getattr(player, 'life_steal', 0.0)
                    if life_steal > 0:
                        actual_steal = life_steal + (3.0 if is_crit else 0.0)
                        player.heal(actual_steal)
                        self.play_sfx("heal", 0.5)
                        self.create_damage_text(player.pos.x, player.pos.y - 45,
                                                f"+{int(actual_steal)} HP", color=(214, 48, 49))

                    # Bendición Sagrada de Paladín (Onda expansiva dorada)
                    if getattr(player, 'holy_shockwave', False) and hits == 1:
                        self.spawn_shockwave(cut_tip_x, cut_tip_y, max_radius=100.0, speed=240.0,
                                             damage=25.0, color=(255, 220, 90), is_player=True)

                    # Pasiva Chamán: Sanación Espiritual (+4 HP por impacto)
                    if w_type == "totem":
                        player.heal(4.0)
                        self.create_damage_text(player.pos.x, player.pos.y - 40, "+4 HP 🌿", color=(46, 204, 113))

                    # Pasiva Monje: Impacto de Ki sónico
                    if w_type == "fists" and (is_crit or hits == 1):
                        self.spawn_shockwave(enemy.pos.x, enemy.pos.y, max_radius=45.0, speed=220.0,
                                             damage=15.0, color=(241, 196, 15), is_player=True)

                    # Pasiva Inquisidor: Penitencia Carmesí (fuego y sangrado al golpear)
                    if w_type == "flail":
                        self.emit_impact_particles(enemy.pos.x, enemy.pos.y, count=6, color=(192, 57, 43))

                    # Recuperación de Maná en combate cuerpo a cuerpo (+10 MP)
                    player.restore_mana(MANA_REGEN_MELEE_HIT)
                    self.create_damage_text(player.pos.x + random.uniform(-10, 10), player.pos.y - 25,
                                            f"+{MANA_REGEN_MELEE_HIT} MP", color=(52, 152, 219))

                    # Recompensa mayor si el golpe elimina al enemigo (+50-75 MP)
                    if not enemy.is_alive and not getattr(enemy, 'mana_awarded', False):
                        enemy.mana_awarded = True
                        self.play_sfx("enemy_death")
                        regen = random.randint(MANA_REGEN_KILL_MIN, MANA_REGEN_KILL_MAX)
                        player.restore_mana(regen)

                        # Cosecha de Almas (Nigromante Abisal: +8 HP y +20 MP extra por alma recolectada)
                        if getattr(player, 'soul_harvest', False):
                            player.heal(8.0)
                            player.restore_mana(20.0)
                            self.create_damage_text(enemy.pos.x, enemy.pos.y - 50, "+8 HP +20 MP 💀",
                                                    color=(155, 89, 182), is_critical=True)
                            self.emit_impact_particles(enemy.pos.x, enemy.pos.y, count=22, color=(142, 68, 173))
                        else:
                            self.create_damage_text(enemy.pos.x, enemy.pos.y - 35, f"+{regen} MP",
                                                    color=(46, 204, 113), is_critical=True)
                            self.emit_impact_particles(enemy.pos.x, enemy.pos.y, count=18, color=COLOR_BRASS)

                    # Empuje de retroceso físico respetando la resistencia al derribo (super-armadura)
                    knock_dir = pygame.math.Vector2(dx, dy)
                    if knock_dir.length_squared() > 0:
                        knock_resist = getattr(enemy, 'knockback_resistance', 0.0)
                        knock_dist = 22.0 * max(0.0, 1.0 - knock_resist)
                        if knock_dist > 0:
                            enemy.pos += knock_dir.normalize() * knock_dist

                    hit_color = COLOR_GOLD if is_crit else COLOR_WHITE
                    self.create_damage_text(enemy.pos.x, enemy.pos.y - 15, final_damage,
                                            color=hit_color, is_critical=is_crit)
                    self.emit_impact_particles(enemy.pos.x, enemy.pos.y, count=8, color=w_p_colors.get(w_type, (220, 50, 50)))

        # Pasiva Caballero Rúnico: Al acertar con el espadón, libera 2 esquirlas rúnicas cortantes
        if w_type == "greatsword" and hits > 0:
            dir_norm = player.aim_vector.copy()
            for angle_offset in (-15, 15):
                rad = math.radians(player.facing_angle + angle_offset)
                sx = math.cos(rad)
                sy = math.sin(rad)
                self.spawn_projectile(
                    x=cut_tip_x, y=cut_tip_y, dir_x=sx, dir_y=sy,
                    damage=damage * 0.45, speed=480.0, element="Luz",
                    is_player=True, radius=7, pierces=True
                )

        return hits

    def update(self, dt: float, player, enemies):
        """Actualiza todas las entidades de combate (proyectiles, trampas, ondas, temblor)."""
        if self.screen_shake_time > 0:
            self.screen_shake_time -= dt
            if self.screen_shake_time <= 0:
                self.screen_shake_intensity = 0.0

        if player.is_dashing:
            self.emit_impact_particles(player.pos.x, player.pos.y, count=2, color=COLOR_STEAM)

        self.damage_texts = [txt for txt in self.damage_texts if txt.update(dt)]
        self.particles = [p for p in self.particles if p.update(dt)]

        self.ground_hazards = [hz for hz in self.ground_hazards if hz.update(dt, player, enemies, self)]
        self.shockwaves = [sw for sw in self.shockwaves if sw.update(dt, player, enemies, self)]

        # Actualizar rayos de relámpago encadenados
        self.lightning_chains = [c for c in self.lightning_chains if c["timer"] > 0]
        for c in self.lightning_chains:
            c["timer"] -= dt

        alive_projectiles = []
        for proj in self.projectiles:
            if not proj.update(dt, player, enemies, self):
                continue

            hit = False
            if proj.is_player:
                for enemy in enemies:
                    dist = (proj.pos - enemy.pos).length()
                    if dist <= proj.radius + enemy.radius:
                        if enemy not in proj.hit_entities:
                            proj.hit_entities.add(enemy)
                            enemy.take_damage(proj.damage)
                            enemy.hit_flash_timer = 0.08  # Parpadeo de impacto blanco
                            self.create_damage_text(enemy.pos.x, enemy.pos.y - 15, proj.damage,
                                                    color=proj.color)
                            self.emit_impact_particles(proj.pos.x, proj.pos.y, count=12, color=proj.color)

                            # Recompensa de Maná y Pasivas si el proyectil eliminó al enemigo
                            if not enemy.is_alive and not getattr(enemy, 'mana_awarded', False):
                                enemy.mana_awarded = True
                                self.play_sfx("enemy_death")
                                self.play_sfx("mana", 0.6)
                                regen = random.randint(MANA_REGEN_KILL_MIN, MANA_REGEN_KILL_MAX)
                                player.restore_mana(regen)

                                # Cosecha de Almas (Nigromante Abisal: +8 HP y +20 MP extra por baja)
                                if getattr(player, 'soul_harvest', False):
                                    player.heal(8.0)
                                    player.restore_mana(20.0)
                                    self.create_damage_text(enemy.pos.x, enemy.pos.y - 50, "+8 HP +20 MP 💀",
                                                            color=(155, 89, 182), is_critical=True)
                                    self.emit_impact_particles(enemy.pos.x, enemy.pos.y, count=22, color=(142, 68, 173))
                                else:
                                    self.create_damage_text(enemy.pos.x, enemy.pos.y - 30, f"+{regen} MP",
                                                            color=(46, 204, 113), is_critical=True)
                                    self.emit_impact_particles(enemy.pos.x, enemy.pos.y, count=18, color=COLOR_BRASS)

                            if proj.on_hit_effect:
                                proj.on_hit_effect(proj.pos)

                            if not proj.pierces:
                                hit = True
                                break
            else:
                dist = (proj.pos - player.pos).length()
                if dist <= proj.radius + player.radius:
                    if player.take_damage(proj.damage):
                        self.trigger_screen_shake(intensity=4.5, duration=0.16)
                        self.create_damage_text(player.pos.x, player.pos.y - 15, proj.damage,
                                                color=COLOR_RED_HEALTH)
                        self.emit_impact_particles(player.pos.x, player.pos.y, count=10,
                                                   color=COLOR_RED_HEALTH)
                    hit = True

            if not hit:
                alive_projectiles.append(proj)

        self.projectiles = alive_projectiles

    def draw(self, surface: pygame.Surface):
        """Dibuja en capas estratificadas: Trampas -> Ondas -> Proyectiles -> Partículas -> Textos."""
        for hz in self.ground_hazards:
            hz.draw(surface)

        for sw in self.shockwaves:
            sw.draw(surface)

        # Rayos de relámpago encadenados
        for c in self.lightning_chains:
            alpha = max(0, min(255, int((c["timer"] / 0.22) * 255)))
            for s_start, s_end in c["segments"]:
                pygame.draw.line(surface, (*c["color"][:3], alpha), s_start, s_end, 4)
                pygame.draw.line(surface, (255, 255, 255, alpha), s_start, s_end, 2)

        for proj in self.projectiles:
            proj.draw(surface)

        for p in self.particles:
            p.draw(surface)

        for txt in self.damage_texts:
            txt.draw(surface, self.font)
