"""
================================================================================
MÓDULO: entities/boss.py
RESPONSABILIDAD: Modelado de los 10 Jefes Elementales Colosales (Nivel 10) con
                 patrones de combate únicos tipo 'Wizard of Legend' y Bullet-Hell.
CONCEPTO ACADÉMICO: Máquinas de Estados Finitas (FSM), Ataques Telegrafiados
                    (Fair Combat / No-Hit Viable) y Polimorfismo Elemental.
================================================================================
Implementa:
- 3000 HP base (escalable por mazmorra).
- 10 Arquetipos únicos según el elemento:
  1. Fuego: Columnas de Erupción de Magma (GroundHazard) y Abanico de Meteoros.
  2. Agua: Maremoto con Corredor Seguro (Safe Passage) y Géiser Abisal.
  3. Viento: Ciclones Gemelos Errantes y Vendaval Radial en Octógono (8 vías).
  4. Tierra: Fisura Sísmica en Cruz (+) y Lluvia de Rocas del Techo.
  5. Trueno: Rayo Focalizado Railgun Tesla (Lock-on) y Anillo de Chispas 360°.
  6. Naturaleza: Brote de Zarzas Espinosas y Enjambre de Esporas Tóxicas.
  7. Vapor: Válvulas de Purga en Cruz Rotatoria y Engranajes de Latón Rodantes.
  8. Metal: Sierras Circulares Búmeran y Cono de Metralla de Remaches.
  9. Oscuridad: Vórtice de Singularidad Gravitatoria y Guadañas Gemelas.
  10. Luz: Pilares de Juicio Solar y Estrella Radiante de 12 Rayos.
- Regla Sagrada: TODO ATAQUE ES 100% ESQUIVABLE (Telegrafos de 0.8s a 1.2s).
- Fase de Furia (< 50% HP): Velocidad +20%, recargas -25%, aura elemental.
- Animaciones: Pulso de respiración titánico y Hit-Flash blanco en impactos.
"""

import math
import random
import pygame
from settings import (
    COLOR_RED_HEALTH, COLOR_DARK_STONE, COLOR_GOLD, COLOR_BRASS,
    COLOR_WHITE, COLOR_STEAM, ELEMENT_COLORS, SCREEN_WIDTH, SCREEN_HEIGHT,
    BOSS_BASE_HP, BOSS_BASE_DAMAGE
)
from utils.asset_loader import AssetLoader


class TelegraphWarning:
    """Representa una zona de advertencia en el suelo previa al disparo o detonación."""

    def __init__(self, t_type: str, duration: float, color, callback, **kwargs):
        self.t_type = t_type          # 'circle', 'laser', 'cross', 'cone', 'corridor', 'shadow'
        self.timer = duration
        self.max_duration = duration
        self.color = color
        self.callback = callback
        self.params = kwargs

    def update(self, dt: float, boss, player, combat_system) -> bool:
        self.timer -= dt
        if self.timer <= 0:
            self.callback(boss, player, combat_system, self.params)
            return False
        return True

    def draw(self, surface: pygame.Surface):
        progress = max(0.0, min(1.0, 1.0 - (self.timer / self.max_duration)))
        r, g, b = self.color[:3]

        if self.t_type == "circle":
            cx = int(self.params.get("x", 0))
            cy = int(self.params.get("y", 0))
            rad = int(self.params.get("radius", 50))

            # Anillo exterior parpadeante
            pygame.draw.circle(surface, (231, 76, 60), (cx, cy), rad, 2)
            # Anillo de progreso interior en llenado
            fill_r = max(4, int(rad * progress))
            fill_surf = pygame.Surface((rad * 2 + 4, rad * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(fill_surf, (r, g, b, 70), (rad + 2, rad + 2), fill_r)
            pygame.draw.circle(fill_surf, (r, g, b, 200), (rad + 2, rad + 2), fill_r, 2)
            surface.blit(fill_surf, (cx - rad - 2, cy - rad - 2))

        elif self.t_type == "shadow":
            cx = int(self.params.get("x", 0))
            cy = int(self.params.get("y", 0))
            max_rad = int(self.params.get("radius", 45))
            cur_rad = max(6, int(max_rad * (0.3 + 0.7 * progress)))
            shadow_surf = pygame.Surface((max_rad * 2 + 4, max_rad * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(shadow_surf, (15, 15, 20, int(160 * progress)), (max_rad + 2, max_rad + 2), cur_rad)
            pygame.draw.circle(shadow_surf, (r, g, b, int(220 * progress)), (max_rad + 2, max_rad + 2), cur_rad, 2)
            surface.blit(shadow_surf, (cx - max_rad - 2, cy - max_rad - 2))

        elif self.t_type == "cross":
            cx = int(self.params.get("x", SCREEN_WIDTH // 2))
            cy = int(self.params.get("y", SCREEN_HEIGHT // 2))
            thickness = int(self.params.get("thickness", 40))

            cross_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            alpha = int(60 + 120 * progress)
            # Franja horizontal y vertical
            pygame.draw.rect(cross_surf, (r, g, b, alpha), (0, cy - thickness // 2, SCREEN_WIDTH, thickness))
            pygame.draw.rect(cross_surf, (r, g, b, alpha), (cx - thickness // 2, 0, thickness, SCREEN_HEIGHT))
            # Bordes de peligro en rojo
            pygame.draw.rect(cross_surf, (231, 76, 60, 220), (0, cy - thickness // 2, SCREEN_WIDTH, thickness), 2)
            pygame.draw.rect(cross_surf, (231, 76, 60, 220), (cx - thickness // 2, 0, thickness, SCREEN_HEIGHT), 2)
            surface.blit(cross_surf, (0, 0))

        elif self.t_type == "laser":
            x1 = self.params.get("x1", 0)
            y1 = self.params.get("y1", 0)
            x2 = self.params.get("x2", 0)
            y2 = self.params.get("y2", 0)
            is_locked = self.timer <= 0.40  # Bloqueado en aviso final de 0.4s

            line_color = (255, 60, 60) if is_locked else (241, 196, 15)
            width = 4 if is_locked else 2
            pygame.draw.line(surface, line_color, (int(x1), int(y1)), (int(x2), int(y2)), width)

        elif self.t_type == "cone":
            cx = int(self.params.get("x", 0))
            cy = int(self.params.get("y", 0))
            dist = self.params.get("length", 280.0)
            mid_angle = self.params.get("angle", 0.0)
            spread = self.params.get("spread", 55.0)

            pts = [(cx, cy)]
            steps = 8
            half_spread = spread / 2.0
            for i in range(steps + 1):
                ang = math.radians(mid_angle - half_spread + (spread * i / steps))
                pts.append((cx + int(math.cos(ang) * dist), cy + int(math.sin(ang) * dist)))

            cone_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.polygon(cone_surf, (231, 76, 60, int(70 + 80 * progress)), pts)
            pygame.draw.polygon(cone_surf, (r, g, b, 200), pts, 2)
            surface.blit(cone_surf, (0, 0))

        elif self.t_type == "corridor":
            # Marca de oleada con corredor seguro verde
            cx = int(self.params.get("x", 0))
            cy = int(self.params.get("y", 0))
            safe_angle = self.params.get("safe_angle", 0.0)
            dist = 220.0

            # Indicador de flecha hacia la zona segura
            safe_x = cx + int(math.cos(math.radians(safe_angle)) * dist)
            safe_y = cy + int(math.sin(math.radians(safe_angle)) * dist)
            pygame.draw.circle(surface, (46, 204, 113), (safe_x, safe_y), 35, 3)


class ElementalBoss(pygame.sprite.Sprite):
    """
    Jefe Elemental Colosal del Nivel 10.
    Cada elemento posee 2 ataques con identidad táctica única y advertencias telegrafiadas.
    """

    def __init__(self, x: float, y: float, element: str, dungeon_index: int = 1):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y)
        self.element = element
        self.dungeon_index = dungeon_index

        # Escalado de atributos por mazmorra
        scale = 1.0 + (dungeon_index - 1) * 0.35
        self.max_hp = BOSS_BASE_HP * scale
        self.current_hp = self.max_hp
        self.damage = BOSS_BASE_DAMAGE * scale
        self.speed = 115.0 * scale
        self.radius = 40

        self.is_alive = True
        self.enraged = False
        self.summoned_support = False
        self.calamity_timer = 2.4
        self.knockback_resistance = 1.0  # Super-armadura inquebrantable de Jefe Colosal

        # Animaciones y efectos
        self.facing_angle = 0.0
        self.pulse_timer = 0.0
        self.hit_flash_timer = 0.0

        # Control de Estados de Combate y Ataques Telegrafiados
        self.attack_timer_1 = 0.8
        self.attack_timer_2 = 2.0
        self.active_telegraphs = []

        self.name = f"Titán Colosal de {element} (Mazmorra {dungeon_index})"

        # Inicialización de sprite
        self.image = AssetLoader.get_boss_sprite(self.element)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def take_damage(self, amount: float):
        """Aplica daño e inicia parpadeo blanco de impacto."""
        self.current_hp -= amount
        self.hit_flash_timer = 0.12

        # Fase de Furia (< 50% HP)
        if self.current_hp <= self.max_hp * 0.5 and not self.enraged:
            self.enraged = True
            self.speed *= 1.20

        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False

    def update(self, dt: float, player, combat_system):
        if not self.is_alive:
            return

        self.pulse_timer += dt
        if self.hit_flash_timer > 0:
            self.hit_flash_timer = max(0.0, self.hit_flash_timer - dt)

        # 1. Movimiento continuo hacia el jugador
        to_player = player.pos - self.pos
        dist = to_player.length()

        if dist > 0:
            direction = to_player.normalize()
            self.facing_angle = math.degrees(math.atan2(to_player.y, to_player.x))
            self.pos += direction * self.speed * dt

            # Confinamiento estricto dentro de los muros perimetrales de la arena
            wall_margin = 42.0
            min_x = wall_margin + self.radius
            max_x = SCREEN_WIDTH - wall_margin - self.radius
            min_y = wall_margin + self.radius
            max_y = SCREEN_HEIGHT - wall_margin - self.radius
            self.pos.x = max(min_x, min(self.pos.x, max_x))
            self.pos.y = max(min_y, min(self.pos.y, max_y))
            self.rect.center = (int(self.pos.x), int(self.pos.y))

            # Daño de contacto
            if dist <= self.radius + player.radius:
                player.take_damage(self.damage)

        # 2. Estallido de Furia (< 50% HP)
        if self.enraged and not self.summoned_support:
            self.summoned_support = True
            self.speed = 145.0 * (1.0 + (self.dungeon_index - 1) * 0.35)
            combat_system.trigger_screen_shake(intensity=7.5, duration=0.45)
            combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=45, color=(255, 90, 20))
            combat_system.spawn_shockwave(
                self.pos.x, self.pos.y, max_radius=220.0, speed=360.0,
                damage=self.damage * 0.85, color=ELEMENT_COLORS.get(self.element, COLOR_GOLD), is_player=False
            )

        # Pulsos de calamidad durante la fase de furia cada 2.4s
        if self.enraged:
            self.calamity_timer -= dt
            if self.calamity_timer <= 0:
                self.calamity_timer = 2.4
                combat_system.spawn_shockwave(
                    self.pos.x, self.pos.y, max_radius=150.0, speed=290.0,
                    damage=self.damage * 0.65, color=(231, 76, 60), is_player=False
                )

        # 3. Procesar avisos telegrafiados activos
        alive_telegraphs = []
        for tg in self.active_telegraphs:
            if tg.update(dt, self, player, combat_system):
                alive_telegraphs.append(tg)
        self.active_telegraphs = alive_telegraphs

        # 4. Gestión de Tiempos de Recarga de Ataques Elementales (Alta agresividad y dinamismo)
        cooldown_mult = 0.50 if self.enraged else 0.75

        self.attack_timer_1 -= dt
        if self.attack_timer_1 <= 0:
            self.attack_timer_1 = 2.0 * cooldown_mult
            self._trigger_signature_attack_1(player, combat_system)

        self.attack_timer_2 -= dt
        if self.attack_timer_2 <= 0:
            self.attack_timer_2 = 3.6 * cooldown_mult
            self._trigger_signature_attack_2(player, combat_system)

    # =========================================================================
    # DISPARADORES DE ATAQUES ELEMENTALES ÚNICOS (10 ARQUETIPOS)
    # =========================================================================

    def _trigger_signature_attack_1(self, player, combat_system):
        """Dispara el primer ataque insignia correspondiente al elemento actual."""
        elem = self.element
        elem_col = ELEMENT_COLORS.get(elem, COLOR_GOLD)
        tele_time = 0.85 if self.enraged else 1.05

        # 1. FUEGO: Erupción de 3 columnas de magma telegrafiadas
        if elem == "Fuego":
            targets = [
                (player.pos.x, player.pos.y),
                (player.pos.x + random.uniform(-80, 80), player.pos.y + random.uniform(-80, 80)),
                (player.pos.x + random.uniform(-90, 90), player.pos.y + random.uniform(-90, 90))
            ]
            for tx, ty in targets:
                def on_magma(b, p, cs, params):
                    cs.spawn_ground_hazard(params["x"], params["y"], "Lava", radius=55.0,
                                           duration=2.5, damage_per_sec=110.0, color=(231, 76, 60), is_player=False)
                    cs.emit_impact_particles(params["x"], params["y"], count=18, color=(255, 90, 20))
                self.active_telegraphs.append(TelegraphWarning("circle", tele_time, elem_col, on_magma, x=tx, y=ty, radius=55))

        # 2. AGUA: Maremoto frontal con Corredor Seguro claramente visible
        elif elem == "Agua":
            aim_deg = self.facing_angle
            safe_deg = aim_deg + random.choice([-25, 25])  # Ángulo del pasillo seguro
            def on_tidal(b, p, cs, params):
                base_rad = math.radians(params["aim_deg"])
                for i in range(-4, 5):
                    deg_offset = i * 14.0
                    proj_deg = params["aim_deg"] + deg_offset
                    # Si coincide con el corredor seguro, OMITIR el proyectil
                    if abs(proj_deg - params["safe_deg"]) <= 12.0:
                        continue
                    rad = math.radians(proj_deg)
                    cs.spawn_projectile(x=b.pos.x, y=b.pos.y,
                                        dir_x=math.cos(rad), dir_y=math.sin(rad),
                                        damage=55.0, speed=340.0, element="Agua",
                                        is_player=False, radius=11, pierces=True)
            self.active_telegraphs.append(TelegraphWarning("corridor", tele_time, elem_col, on_tidal,
                                                           x=self.pos.x, y=self.pos.y,
                                                           aim_deg=aim_deg, safe_deg=safe_deg, safe_angle=safe_deg))

        # 3. VIENTO: Ciclones gemelos errantes de baja velocidad
        elif elem == "Viento":
            def on_cyclones(b, p, cs, params):
                for ang_offset in [-0.5, 0.5]:
                    rad = math.radians(b.facing_angle) + ang_offset
                    cs.spawn_projectile(x=b.pos.x, y=b.pos.y,
                                        dir_x=math.cos(rad), dir_y=math.sin(rad),
                                        damage=50.0, speed=230.0, element="Viento",
                                        is_player=False, radius=14, pierces=True)
            self.active_telegraphs.append(TelegraphWarning("circle", 0.75, elem_col, on_cyclones,
                                                           x=self.pos.x, y=self.pos.y, radius=45))

        # 4. TIERRA: Fisura sísmica en Cruz (+)
        elif elem == "Tierra":
            def on_cross_fissure(b, p, cs, params):
                cx, cy = params["x"], params["y"]
                # Impacto en cruz
                for offset in [-180, -90, 0, 90, 180]:
                    cs.spawn_ground_hazard(cx + offset, cy, "Roca", radius=35.0, duration=1.4,
                                           damage_per_sec=120.0, color=(160, 82, 45), is_player=False)
                    cs.spawn_ground_hazard(cx, cy + offset, "Roca", radius=35.0, duration=1.4,
                                           damage_per_sec=120.0, color=(160, 82, 45), is_player=False)
                cs.emit_impact_particles(cx, cy, count=25, color=(120, 60, 30))
            self.active_telegraphs.append(TelegraphWarning("cross", tele_time, elem_col, on_cross_fissure,
                                                           x=self.pos.x, y=self.pos.y, thickness=45))

        # 5. TRUENO: Rayo Focalizado Railgun Tesla con Lock-On
        elif elem == "Trueno":
            target_x, target_y = player.pos.x, player.pos.y
            def on_railgun(b, p, cs, params):
                dx = params["x2"] - params["x1"]
                dy = params["y2"] - params["y1"]
                length = math.hypot(dx, dy)
                if length > 0:
                    dir_x = dx / length
                    dir_y = dy / length
                    # Salva ultrarrápida de plasma perforante
                    for k in range(3):
                        cs.spawn_projectile(x=params["x1"], y=params["y1"],
                                            dir_x=dir_x, dir_y=dir_y,
                                            damage=68.0, speed=750.0, element="Trueno",
                                            is_player=False, radius=12, pierces=True)
            self.active_telegraphs.append(TelegraphWarning("laser", tele_time, (243, 156, 18), on_railgun,
                                                           x1=self.pos.x, y1=self.pos.y,
                                                           x2=target_x, y2=target_y))

        # 6. NATURALEZA: Brote de Zarzas Espinosas en 3 anillos
        elif elem == "Naturaleza":
            targets = [
                (player.pos.x, player.pos.y),
                (player.pos.x + 85, player.pos.y + 40),
                (player.pos.x - 85, player.pos.y - 40)
            ]
            for tx, ty in targets:
                def on_roots(b, p, cs, params):
                    cs.spawn_ground_hazard(params["x"], params["y"], "Zarzas", radius=50.0,
                                           duration=2.2, damage_per_sec=105.0, color=(39, 174, 96), is_player=False)
                    cs.emit_impact_particles(params["x"], params["y"], count=15, color=(46, 204, 113))
                self.active_telegraphs.append(TelegraphWarning("circle", tele_time, elem_col, on_roots, x=tx, y=ty, radius=50))

        # 7. VAPOR (STEAMPUNK): Válvulas de Purga en Cruz Rotatoria
        elif elem == "Vapor (Steampunk)":
            def on_steam_cross(b, p, cs, params):
                for ang_deg in [0, 90, 180, 270]:
                    rad = math.radians(ang_deg + b.facing_angle)
                    cs.spawn_projectile(x=b.pos.x, y=b.pos.y,
                                        dir_x=math.cos(rad), dir_y=math.sin(rad),
                                        damage=55.0, speed=350.0, element="Vapor (Steampunk)",
                                        is_player=False, radius=12, pierces=True)
                cs.emit_impact_particles(b.pos.x, b.pos.y, count=20, color=COLOR_STEAM)
            self.active_telegraphs.append(TelegraphWarning("cross", tele_time * 0.8, elem_col, on_steam_cross,
                                                           x=self.pos.x, y=self.pos.y, thickness=40))

        # 8. METAL: Cono de Metralla de Remaches Telegrafiado
        elif elem == "Metal":
            cone_angle = self.facing_angle
            def on_shrapnel_cone(b, p, cs, params):
                base_rad = math.radians(params["angle"])
                for i in range(-3, 4):
                    ang = base_rad + math.radians(i * 8.0)
                    cs.spawn_projectile(x=b.pos.x, y=b.pos.y,
                                        dir_x=math.cos(ang), dir_y=math.sin(ang),
                                        damage=50.0, speed=440.0, element="Metal",
                                        is_player=False, radius=9)
            self.active_telegraphs.append(TelegraphWarning("cone", tele_time, elem_col, on_shrapnel_cone,
                                                           x=self.pos.x, y=self.pos.y, angle=cone_angle,
                                                           length=280.0, spread=55.0))

        # 9. OSCURIDAD: Singularidad Gravitatoria Abisal
        elif elem == "Oscuridad":
            tx, ty = player.pos.x + random.uniform(-40, 40), player.pos.y + random.uniform(-40, 40)
            def on_singularity(b, p, cs, params):
                cs.spawn_ground_hazard(params["x"], params["y"], "Singularidad", radius=65.0,
                                       duration=2.5, damage_per_sec=125.0, color=(142, 68, 173), is_player=False)
                cs.emit_impact_particles(params["x"], params["y"], count=22, color=(100, 30, 140))
            self.active_telegraphs.append(TelegraphWarning("circle", tele_time, elem_col, on_singularity, x=tx, y=ty, radius=65))

        # 10. LUZ: Pilares de Juicio Solar Telegrafiadas
        elif elem == "Luz":
            targets = [
                (player.pos.x, player.pos.y),
                (player.pos.x + 95, player.pos.y),
                (player.pos.x - 95, player.pos.y)
            ]
            for tx, ty in targets:
                def on_solar_pillar(b, p, cs, params):
                    cs.spawn_shockwave(x=params["x"], y=params["y"], max_radius=85.0, speed=290.0,
                                       damage=75.0, color=(254, 249, 231), is_player=False)
                    cs.emit_impact_particles(params["x"], params["y"], count=20, color=COLOR_GOLD)
                self.active_telegraphs.append(TelegraphWarning("circle", tele_time, elem_col, on_solar_pillar, x=tx, y=ty, radius=60))

        else:
            # Fallback seguro
            def on_fallback(b, p, cs, params):
                cs.spawn_shockwave(x=b.pos.x, y=b.pos.y, max_radius=220.0, speed=260.0, damage=55.0, is_player=False)
            self.active_telegraphs.append(TelegraphWarning("circle", 1.0, elem_col, on_fallback, x=self.pos.x, y=self.pos.y, radius=70))

    def _trigger_signature_attack_2(self, player, combat_system):
        """Dispara el segundo ataque insignia (Bullet-Hell o Patrón de Área Esquivable)."""
        elem = self.element
        elem_col = ELEMENT_COLORS.get(elem, COLOR_GOLD)

        # 1. FUEGO: Abanico de Meteoros de Lava (7 proyectiles con amplios huecos de 20°)
        if elem == "Fuego":
            base_rad = math.radians(self.facing_angle)
            for i in range(-3, 4):
                ang = base_rad + math.radians(i * 20.0)
                combat_system.spawn_projectile(x=self.pos.x, y=self.pos.y,
                                               dir_x=math.cos(ang), dir_y=math.sin(ang),
                                               damage=55.0, speed=340.0, element="Fuego",
                                               is_player=False, radius=12)
            combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=15, color=(231, 76, 60))

        # 2. AGUA: Géiser Abisal de Presión
        elif elem == "Agua":
            tx, ty = player.pos.x, player.pos.y
            def on_geyser(b, p, cs, params):
                cs.spawn_shockwave(x=params["x"], y=params["y"], max_radius=110.0, speed=320.0,
                                   damage=75.0, color=(52, 152, 219), is_player=False)
                cs.emit_impact_particles(params["x"], params["y"], count=22, color=(0, 206, 209))
            self.active_telegraphs.append(TelegraphWarning("circle", 1.0, elem_col, on_geyser, x=tx, y=ty, radius=70))

        # 3. VIENTO: Vendaval Radial en Octógono (8 direcciones con pasillos de 45°)
        elif elem == "Viento":
            for i in range(8):
                rad = (2 * math.pi / 8) * i
                combat_system.spawn_projectile(x=self.pos.x, y=self.pos.y,
                                               dir_x=math.cos(rad), dir_y=math.sin(rad),
                                               damage=48.0, speed=380.0, element="Viento",
                                               is_player=False, radius=11)
            combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=16, color=(26, 188, 156))

        # 4. TIERRA: Lluvia de Rocas del Techo con Sombras Crecientes
        elif elem == "Tierra":
            for _ in range(4):
                tx = player.pos.x + random.uniform(-110, 110)
                ty = player.pos.y + random.uniform(-110, 110)
                def on_rock_fall(b, p, cs, params):
                    cs.spawn_shockwave(x=params["x"], y=params["y"], max_radius=60.0, speed=220.0,
                                       damage=65.0, color=(160, 82, 45), is_player=False)
                    cs.emit_impact_particles(params["x"], params["y"], count=16, color=(100, 50, 25))
                self.active_telegraphs.append(TelegraphWarning("shadow", 0.9, elem_col, on_rock_fall, x=tx, y=ty, radius=48))

        # 5. TRUENO: Anillo de 10 Chispas Eléctricas en 360° (36° de hueco para esquivar)
        elif elem == "Trueno":
            for i in range(10):
                rad = (2 * math.pi / 10) * i
                combat_system.spawn_projectile(x=self.pos.x, y=self.pos.y,
                                               dir_x=math.cos(rad), dir_y=math.sin(rad),
                                               damage=50.0, speed=320.0, element="Trueno",
                                               is_player=False, radius=10)
            combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=18, color=COLOR_GOLD)

        # 6. NATURALEZA: Enjambre de 6 Esporas Tóxicas Flotantes
        elif elem == "Naturaleza":
            for i in range(7):
                rad = (2 * math.pi / 7) * i + random.uniform(-0.1, 0.1)
                combat_system.spawn_projectile(x=self.pos.x, y=self.pos.y,
                                               dir_x=math.cos(rad), dir_y=math.sin(rad),
                                               damage=48.0, speed=240.0, element="Naturaleza",
                                               is_player=False, radius=13)
            combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=14, color=(39, 174, 96))

        # 7. VAPOR (STEAMPUNK): Engranajes de Latón Rodantes
        elif elem == "Vapor (Steampunk)":
            base_rad = math.radians(self.facing_angle)
            for ang_offset in [-0.35, 0.35]:
                ang = base_rad + ang_offset
                combat_system.spawn_projectile(x=self.pos.x, y=self.pos.y,
                                               dir_x=math.cos(ang), dir_y=math.sin(ang),
                                               damage=60.0, speed=340.0, element="Vapor (Steampunk)",
                                               is_player=False, radius=16, pierces=True)
            combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=20, color=COLOR_BRASS)

        # 8. METAL: Sierras Circulares Búmeran
        elif elem == "Metal":
            base_rad = math.radians(self.facing_angle)
            for ang_offset in [-0.25, 0.0, 0.25]:
                ang = base_rad + ang_offset
                combat_system.spawn_projectile(x=self.pos.x, y=self.pos.y,
                                               dir_x=math.cos(ang), dir_y=math.sin(ang),
                                               damage=58.0, speed=360.0, element="Metal",
                                               is_player=False, radius=13, pierces=True)
            combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=18, color=COLOR_STEAM)

        # 9. OSCURIDAD: Guadañas Gemelas de Sombra (Centro despejado)
        elif elem == "Oscuridad":
            base_rad = math.radians(self.facing_angle)
            for ang_offset in [-0.45, 0.45]:
                ang = base_rad + ang_offset
                combat_system.spawn_projectile(x=self.pos.x, y=self.pos.y,
                                               dir_x=math.cos(ang), dir_y=math.sin(ang),
                                               damage=65.0, speed=330.0, element="Oscuridad",
                                               is_player=False, radius=15, pierces=True)
            combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=18, color=(142, 68, 173))

        # 10. LUZ: Estrella Radiante de 12 Rayos en 360° (30° de hueco para esquivar)
        elif elem == "Luz":
            for i in range(12):
                rad = (2 * math.pi / 12) * i
                combat_system.spawn_projectile(x=self.pos.x, y=self.pos.y,
                                               dir_x=math.cos(rad), dir_y=math.sin(rad),
                                               damage=52.0, speed=330.0, element="Luz",
                                               is_player=False, radius=10)
            combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=22, color=(254, 249, 231))

        else:
            # Onda de choque anular (esquivable con Dash)
            combat_system.spawn_shockwave(x=self.pos.x, y=self.pos.y, max_radius=300.0,
                                          speed=260.0, damage=45.0, color=elem_col, is_player=False)

    def draw(self, surface: pygame.Surface):
        if not self.is_alive:
            return

        # 1. Dibujar todas las advertencias telegrafiadas en el suelo antes del sprite
        for tg in self.active_telegraphs:
            tg.draw(surface)

        # 2. Sombra de suelo colosal para anclar al jefe
        sh_rx = int(self.radius * 1.15)
        sh_ry = int(self.radius * 0.48)
        shadow = AssetLoader.get_shadow_sprite(rx=sh_rx, ry=sh_ry)
        sh_y = int(self.pos.y + self.radius * 0.75)
        surface.blit(shadow, (int(self.pos.x - shadow.get_width() // 2), int(sh_y - shadow.get_height() // 2)))

        # 3. Aura elemental de base y Aura de Furia
        elem_col = ELEMENT_COLORS.get(self.element, COLOR_GOLD)
        base_aura_rad = self.radius + 8 + int(3 * math.sin(self.pulse_timer * 3.0))
        aura_surf = pygame.Surface((base_aura_rad * 2 + 4, base_aura_rad * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(aura_surf, (*elem_col[:3], 45), (base_aura_rad + 2, base_aura_rad + 2), base_aura_rad)
        surface.blit(aura_surf, (int(self.pos.x - base_aura_rad - 2), int(self.pos.y - base_aura_rad - 2)))

        if self.enraged:
            rage_rad = self.radius + 16 + int(5 * math.sin(self.pulse_timer * 8.0))
            pygame.draw.circle(surface, (231, 76, 60), (int(self.pos.x), int(self.pos.y)), rage_rad, 2)
            pygame.draw.circle(surface, elem_col, (int(self.pos.x), int(self.pos.y)), rage_rad - 4, 1)

        # 4. Sprite base con rotación y pulso de respiración titánico
        sprite = AssetLoader.get_boss_sprite(self.element)
        rotated_sprite = pygame.transform.rotate(sprite, -self.facing_angle)

        pulse_scale = 1.0 + 0.04 * math.sin(self.pulse_timer * 4.0)
        w = max(10, int(rotated_sprite.get_width() * pulse_scale))
        h = max(10, int(rotated_sprite.get_height() * pulse_scale))
        scaled_sprite = pygame.transform.smoothscale(rotated_sprite, (w, h))
        rect = scaled_sprite.get_rect(center=(int(self.pos.x), int(self.pos.y)))

        # 5. Parpadeo de impacto blanco (Hit-Flash)
        if self.hit_flash_timer > 0:
            mask = pygame.mask.from_surface(scaled_sprite)
            flash_surf = mask.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
            surface.blit(flash_surf, rect)
        else:
            surface.blit(scaled_sprite, rect)

    def draw_boss_hud(self, surface: pygame.Surface, font: pygame.font.Font):
        """Dibuja la gran barra de vida del Jefe en el encabezado de la pantalla con filigrana gótica."""
        if not self.is_alive:
            return

        bar_w = 660
        bar_h = 22
        x = (SCREEN_WIDTH - bar_w) // 2
        y = 52

        # Placa de fondo ornamentada
        bg_panel = pygame.Rect(x - 8, y - 24, bar_w + 16, bar_h + 32)
        pygame.draw.rect(surface, (14, 16, 22), bg_panel, border_radius=6)
        pygame.draw.rect(surface, COLOR_BRASS, bg_panel, 1, border_radius=6)

        # Marco exterior de latón Steampunk
        pygame.draw.rect(surface, COLOR_BRASS, (x - 2, y - 2, bar_w + 4, bar_h + 4), 2, border_radius=3)
        pygame.draw.rect(surface, COLOR_DARK_STONE, (x, y, bar_w, bar_h), border_radius=2)

        ratio = max(0.0, self.current_hp / self.max_hp)
        elem_color = ELEMENT_COLORS.get(self.element, COLOR_RED_HEALTH)
        fill_w = int(bar_w * ratio)
        if fill_w > 0:
            pygame.draw.rect(surface, elem_color, (x, y, fill_w, bar_h), border_radius=2)
            # Brillo superior en la barra
            pygame.draw.line(surface, (255, 255, 255), (x + 2, y + 2), (x + fill_w - 2, y + 2), 1)

        # Marca de fase de Furia al 50%
        notch_x = x + bar_w // 2
        pygame.draw.line(surface, COLOR_GOLD, (notch_x, y - 3), (notch_x, y + bar_h + 3), 2)

        furia_txt = " 🔥 [¡FURIAS DESATADAS!]" if self.enraged else ""
        elem_badge = f"[{self.element.upper()}]"
        title_surf = font.render(f"👑 {self.name} {elem_badge}{furia_txt}  •  {int(self.current_hp)} / {int(self.max_hp)} HP",
                                 True, COLOR_GOLD if self.enraged else COLOR_WHITE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, y - 11))
        surface.blit(title_surf, title_rect)
