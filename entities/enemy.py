"""
================================================================================
MÓDULO: entities/enemy.py
RESPONSABILIDAD: Bestiario completo: Autómatas de vapor comunes y 5 variantes
                 únicas de Espíritus Malignos (Élites balanceados).
CONCEPTO ACADÉMICO: Polimorfismo, Patrón State local y Algoritmos de IA Vectorial.
================================================================================
Implementa:
1. Enemigos Comunes Diversificados:
   - Autómata Minero (Cuerpo a cuerpo base).
   - Autómata Embestidor (Carga de pistón telegrafiada con aturdimiento).
   - Tirador de Vapor / Ballestero (Ataques a distancia telegrafiados).
   - Dron de Vapor Volador (Hostigador rápido con poca vida).
   - Demoledor Blindado (Tanque pesado lento).
   - Mini-Autómata (Invocación frágil de 1 golpe).

2. 5 Variantes Únicas de Espíritus Malignos (Velocidad balanceada a 110 px/s
   con ventanas de inmovilidad/vulnerabilidad para ser castigados por la espada):
   - Penumbra: Dispara y se teletransporta, quedando vulnerable 1.5s.
   - Llama Fatua: Se detiene a cargar una espiral de 3 bolas de fuego.
   - Glacial: Canaliza un cono gélido inmóvil durante 2 segundos.
   - Tormenta: Marca un relámpago telegrafiado en el suelo y queda exhausto.
   - Nigromante: Levita quieto mientras invoca 2 mini-autómatas.
"""

import math
import random
import pygame
from settings import (
    COMMON_MINER_HP, COMMON_MINER_DAMAGE, COMMON_MINER_SPEED,
    COMMON_CHARGER_HP, COMMON_CHARGER_DAMAGE, COMMON_CHARGER_SPEED, COMMON_CHARGER_BURST,
    COMMON_SNIPER_HP, COMMON_SNIPER_DAMAGE, COMMON_SNIPER_SPEED,
    COMMON_DRONE_HP, COMMON_DRONE_DAMAGE, COMMON_DRONE_SPEED,
    COMMON_TANK_HP, COMMON_TANK_DAMAGE, COMMON_TANK_SPEED,
    ELITE_SPIRIT_HP, ELITE_SPIRIT_DAMAGE, ELITE_SPIRIT_SPEED,
    COMMON_BOMBARDIER_HP, COMMON_BOMBARDIER_DAMAGE, COMMON_BOMBARDIER_SPEED,
    COMMON_PLAGUE_DOCTOR_HP, COMMON_PLAGUE_DOCTOR_DAMAGE, COMMON_PLAGUE_DOCTOR_SPEED,
    COMMON_SHIELD_GUARDIAN_HP, COMMON_SHIELD_GUARDIAN_DAMAGE, COMMON_SHIELD_GUARDIAN_SPEED,
    COMMON_ARCANE_CULTIST_HP, COMMON_ARCANE_CULTIST_DAMAGE, COMMON_ARCANE_CULTIST_SPEED,
    COMMON_REAPER_HP, COMMON_REAPER_DAMAGE, COMMON_REAPER_SPEED,
    COLOR_RED_HEALTH, COLOR_DARK_STONE, COLOR_GOLD, COLOR_BRASS, COLOR_COPPER,
    COLOR_WHITE, COLOR_STEAM, SCREEN_WIDTH, SCREEN_HEIGHT
)
from utils.asset_loader import AssetLoader


class Enemy(pygame.sprite.Sprite):
    """Clase base abstracta para todos los oponentes del juego."""

    def __init__(self, x: float, y: float, hp: float, damage: float, speed: float, radius: float):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y)
        self.max_hp = hp
        self.current_hp = hp
        self.damage = damage
        self.speed = speed
        self.radius = radius

        self.facing_angle = 0.0
        self.is_alive = True
        self.attack_cooldown = 0.55                    # Cadencia rápida Roguelike
        self.attack_timer = 0.0
        self.hit_flash_timer = 0.0
        self.mana_awarded = False

        # Superficie de seguridad por defecto para evitar referencias None al instanciar
        self.image = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def take_damage(self, amount: float):
        """Aplica daño, activa parpadeo blanco y verifica condición de muerte."""
        self.current_hp -= amount
        self.hit_flash_timer = 0.09
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False

    def apply_difficulty_scaling(self, mult: float):
        """
        Escala matemáticamente la salud, el daño y ligeramente la velocidad
        según el nivel alcanzado en la mazmorra (+3.5% por nivel).
        """
        self.max_hp = round(self.max_hp * mult, 1)
        self.current_hp = self.max_hp
        self.damage = round(self.damage * mult, 1)
        speed_bonus = 1.0 + (mult - 1.0) * 0.12
        self.speed = min(self.speed * speed_bonus, 260.0)

    def update_base(self, dt: float):
        """Actualiza temporizadores compartidos (Hit Flash) y confina la entidad dentro de los muros de la arena."""
        if self.hit_flash_timer > 0:
            self.hit_flash_timer = max(0.0, self.hit_flash_timer - dt)

        # Confinamiento estricto dentro de los muros perimetrales de la arena (Grosor de muro: 36px)
        wall_margin = 38.0
        min_x = wall_margin + self.radius
        max_x = SCREEN_WIDTH - wall_margin - self.radius
        min_y = wall_margin + self.radius
        max_y = SCREEN_HEIGHT - wall_margin - self.radius
        self.pos.x = max(min_x, min(self.pos.x, max_x))
        self.pos.y = max(min_y, min(self.pos.y, max_y))

    def separate_from_others(self, others, min_dist=30.0) -> pygame.math.Vector2:
        """Fuerza de repulsión respecto a otros enemigos para evitar solapamiento (Boids)."""
        steer = pygame.math.Vector2(0, 0)
        count = 0
        for other in others:
            if other is not self and other.is_alive:
                dist = (self.pos - other.pos).length()
                if 0 < dist < min_dist:
                    diff = (self.pos - other.pos).normalize() / dist
                    steer += diff
                    count += 1
        if count > 0 and steer.length_squared() > 0:
            steer = steer.normalize() * 38.0
        return steer

    def draw_sprite_with_flash(self, surface: pygame.Surface, sprite: pygame.Surface, rect: pygame.Rect):
        """Renderiza sombra en el suelo y sprite con parpadeo blanco brillante de impacto (Hit-Flash)."""
        # Sombra suave bajo el enemigo
        sh_rx = max(10, int(self.radius * 0.95))
        sh_ry = max(4, int(self.radius * 0.40))
        shadow = AssetLoader.get_shadow_sprite(rx=sh_rx, ry=sh_ry)
        sh_y = int(self.pos.y + self.radius * 0.65)
        surface.blit(shadow, (int(self.pos.x - shadow.get_width() // 2), int(sh_y - shadow.get_height() // 2)))

        if self.hit_flash_timer > 0:
            mask = pygame.mask.from_surface(sprite)
            flash_surf = mask.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
            surface.blit(flash_surf, rect)
        else:
            surface.blit(sprite, rect)

    def draw_health_bar(self, surface: pygame.Surface):
        """Dibuja una barra de salud estilizada encima del enemigo si está herido."""
        if self.current_hp < self.max_hp and self.is_alive:
            bar_w = max(24, int(self.radius * 2.2))
            bar_h = 5
            x = int(self.pos.x - bar_w / 2)
            y = int(self.pos.y - self.radius - 10)

            # Marco de fondo
            pygame.draw.rect(surface, (12, 14, 18), (x - 1, y - 1, bar_w + 2, bar_h + 2), border_radius=2)
            pygame.draw.rect(surface, (45, 48, 56), (x, y, bar_w, bar_h), border_radius=1)
            ratio = max(0.0, self.current_hp / self.max_hp)
            fill_w = int(bar_w * ratio)
            if fill_w > 0:
                bar_col = COLOR_RED_HEALTH if ratio > 0.30 else (231, 76, 60)
                pygame.draw.rect(surface, bar_col, (x, y, fill_w, bar_h), border_radius=1)
                # Resplandor superior
                pygame.draw.line(surface, (255, 140, 140), (x, y), (x + fill_w - 1, y), 1)


# =============================================================================
# SECCIÓN 1: ENEMIGOS COMUNES (AUTÓMATAS Y MONSTRUOS MEDIEVALES)
# =============================================================================

class SteamMiner(Enemy):
    """Enemigo común estándar: Autómata Minero Medieval de combate cuerpo a cuerpo."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, COMMON_MINER_HP, COMMON_MINER_DAMAGE,
                         COMMON_MINER_SPEED + random.uniform(-10, 10), radius=18)
        self.image = AssetLoader.get_miner_sprite(0)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def update(self, dt: float, player, enemies, combat_system):
        self.update_base(dt)
        if not self.is_alive:
            return

        to_player = player.pos - self.pos
        dist = to_player.length()

        if dist > 0:
            direction = to_player.normalize()
            self.facing_angle = math.degrees(math.atan2(to_player.y, to_player.x))
            repulsion = self.separate_from_others(enemies, min_dist=30.0)
            self.pos += (direction * self.speed + repulsion) * dt

            if dist <= self.radius + player.radius:
                if self.attack_timer <= 0:
                    if player.take_damage(self.damage):
                        combat_system.create_damage_text(player.pos.x, player.pos.y - 15,
                                                         self.damage, color=COLOR_RED_HEALTH)
                        combat_system.emit_impact_particles(player.pos.x, player.pos.y, count=8,
                                                            color=COLOR_RED_HEALTH)
                    self.attack_timer = self.attack_cooldown

        if self.attack_timer > 0:
            self.attack_timer -= dt

        # Asegurar confinamiento y actualización de rectángulo
        self.update_base(dt)
        self.image = AssetLoader.get_miner_sprite(self.facing_angle)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def draw(self, surface: pygame.Surface):
        if self.is_alive:
            self.draw_sprite_with_flash(surface, self.image, self.rect)
            self.draw_health_bar(surface)


# Alias para compatibilidad con código existente
CommonMonster = SteamMiner


class SteamPistonCharger(Enemy):
    """
    Autómata Embestidor:
    - Se detiene 0.7s para silbar vapor y calentarse (telegrafiado).
    - Carga en línea recta a 380 px/s.
    - Si falla, queda aturdido 1 segundo para ser castigado con la espada.
    """

    STATE_CHASE = "CHASE"
    STATE_WINDUP = "WINDUP"
    STATE_CHARGE = "CHARGE"
    STATE_STUNNED = "STUNNED"

    def __init__(self, x: float, y: float):
        super().__init__(x, y, COMMON_CHARGER_HP, COMMON_CHARGER_DAMAGE,
                         COMMON_CHARGER_SPEED, radius=20)
        self.state = self.STATE_CHASE
        self.state_timer = 0.0
        self.charge_dir = pygame.math.Vector2(1, 0)
        self.charge_duration = 0.65
        self.charge_cooldown = 1.6
        self.cooldown_timer = random.uniform(0.5, 1.4)
        self.knockback_resistance = 0.65  # Resistencia al empuje
        self.image = AssetLoader.get_charger_sprite(0, False)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def update(self, dt: float, player, enemies, combat_system):
        self.update_base(dt)
        if not self.is_alive:
            return

        to_player = player.pos - self.pos
        dist = to_player.length()

        if self.state == self.STATE_CHASE:
            self.cooldown_timer -= dt
            if dist > 0:
                direction = to_player.normalize()
                self.facing_angle = math.degrees(math.atan2(to_player.y, to_player.x))
                repulsion = self.separate_from_others(enemies, min_dist=35.0)
                self.pos += (direction * self.speed + repulsion) * dt

                # Daño si entra en contacto
                if dist <= self.radius + player.radius:
                    if self.attack_timer <= 0:
                        player.take_damage(self.damage * 0.7)
                        self.attack_timer = 0.7

            # Iniciar preparación de carga si está a media distancia
            if self.cooldown_timer <= 0 and 100 < dist < 420:
                self.state = self.STATE_WINDUP
                self.state_timer = 0.42
                self.charge_dir = (player.pos - self.pos).normalize()
                combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=12, color=COLOR_STEAM)

        elif self.state == self.STATE_WINDUP:
            # Inmóvil telegrafiando vapor
            self.state_timer -= dt
            if dist > 0:
                self.facing_angle = math.degrees(math.atan2(self.charge_dir.y, self.charge_dir.x))
            if self.state_timer <= 0:
                self.state = self.STATE_CHARGE
                self.state_timer = self.charge_duration
                combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=16, color=(255, 80, 50))

        elif self.state == self.STATE_CHARGE:
            # Embestida veloz
            self.state_timer -= dt
            self.pos += self.charge_dir * COMMON_CHARGER_BURST * dt

            # Colisión destructiva contra el jugador durante la carga
            if dist <= self.radius + player.radius:
                if player.take_damage(self.damage):
                    combat_system.create_damage_text(player.pos.x, player.pos.y - 15,
                                                     self.damage, color=(255, 60, 60), is_critical=True)
                    combat_system.emit_impact_particles(player.pos.x, player.pos.y, count=15, color=COLOR_RED_HEALTH)
                # Terminar carga y quedar aturdido
                self.state = self.STATE_STUNNED
                self.state_timer = 0.85

            elif self.state_timer <= 0:
                # Falló la carga -> Aturdido y libera onda de choque corta
                self.state = self.STATE_STUNNED
                self.state_timer = 0.95
                combat_system.spawn_shockwave(
                    self.pos.x, self.pos.y, max_radius=120.0, speed=240.0,
                    damage=35.0, color=(240, 140, 40), is_player=False
                )

        elif self.state == self.STATE_STUNNED:
            # Aturdido, vulnerable total
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = self.STATE_CHASE
                self.cooldown_timer = self.charge_cooldown

        if self.attack_timer > 0:
            self.attack_timer -= dt

        self.update_base(dt)
        is_charging = (self.state == self.STATE_CHARGE or self.state == self.STATE_WINDUP)
        self.image = AssetLoader.get_charger_sprite(self.facing_angle, is_charging)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def draw(self, surface: pygame.Surface):
        if self.is_alive:
            if self.state == self.STATE_STUNNED:
                pygame.draw.circle(surface, COLOR_GOLD, (int(self.pos.x), int(self.pos.y - self.radius - 12)), 4)
            self.draw_sprite_with_flash(surface, self.image, self.rect)
            self.draw_health_bar(surface)


class SteamSharpshooter(Enemy):
    """Tirador de Vapor / Ballestero: Ataca a distancia disparando saetas veloces."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, COMMON_SNIPER_HP, COMMON_SNIPER_DAMAGE,
                         COMMON_SNIPER_SPEED, radius=16)
        self.shoot_cooldown = 1.15
        self.shoot_timer = random.uniform(0.4, 1.0)
        self.image = AssetLoader.get_sniper_sprite(0)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def update(self, dt: float, player, enemies, combat_system):
        self.update_base(dt)
        if not self.is_alive:
            return

        to_player = player.pos - self.pos
        dist = to_player.length()

        if dist > 0:
            direction = to_player.normalize()
            self.facing_angle = math.degrees(math.atan2(to_player.y, to_player.x))

            # Mantiene distancia táctica (~220-320px)
            if dist < 200:
                self.pos -= direction * (self.speed * 0.95) * dt
            elif dist > 320:
                self.pos += direction * self.speed * dt

            repulsion = self.separate_from_others(enemies, min_dist=35.0)
            self.pos += repulsion * dt

        self.shoot_timer -= dt
        if self.shoot_timer <= 0 and 0 < dist < 650:
            self.shoot_timer = self.shoot_cooldown
            dir_bolt = (player.pos - self.pos).normalize()
            base_ang = math.atan2(dir_bolt.y, dir_bolt.x)
            # Ráfaga triple veloz en abanico
            for ang_off in [-0.16, 0.0, 0.16]:
                rad = base_ang + ang_off
                combat_system.spawn_projectile(
                    x=self.pos.x, y=self.pos.y,
                    dir_x=math.cos(rad), dir_y=math.sin(rad),
                    damage=self.damage * 0.75, speed=400.0,
                    element="Metal", is_player=False, radius=8
                )
            combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=8, color=COLOR_BRASS)

        self.update_base(dt)
        self.image = AssetLoader.get_sniper_sprite(self.facing_angle)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def draw(self, surface: pygame.Surface):
        if self.is_alive:
            self.draw_sprite_with_flash(surface, self.image, self.rect)
            self.draw_health_bar(surface)


class SteamDrone(Enemy):
    """Dron Volador de Vapor: Hostigador rápido que sobrevuela en ráfagas sinodales."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, COMMON_DRONE_HP, COMMON_DRONE_DAMAGE,
                         COMMON_DRONE_SPEED, radius=14)
        self.pulse = random.uniform(0, 10)
        self.image = AssetLoader.get_drone_sprite(0)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def update(self, dt: float, player, enemies, combat_system):
        self.update_base(dt)
        if not self.is_alive:
            return

        self.pulse += dt * 8.0
        to_player = player.pos - self.pos
        dist = to_player.length()

        if dist > 0:
            direction = to_player.normalize()
            self.facing_angle = math.degrees(math.atan2(to_player.y, to_player.x))
            repulsion = self.separate_from_others(enemies, min_dist=24.0)
            # Desplazamiento lateral sinodal para dificultar el esquive
            perp = pygame.math.Vector2(-direction.y, direction.x) * math.sin(self.pulse * 3.0) * 45.0
            self.pos += (direction * self.speed + repulsion + perp) * dt

            if dist <= self.radius + player.radius:
                if self.attack_timer <= 0:
                    player.take_damage(self.damage)
                    self.attack_timer = self.attack_cooldown

        if self.attack_timer > 0:
            self.attack_timer -= dt

        self.update_base(dt)
        self.image = AssetLoader.get_drone_sprite(self.pulse)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def draw(self, surface: pygame.Surface):
        if self.is_alive:
            self.draw_sprite_with_flash(surface, self.image, self.rect)
            self.draw_health_bar(surface)


class DemolitionTank(Enemy):
    """Autómata Demoledor Pesado: Tanque acorazado con martillazo sísmico y súper-armadura."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, COMMON_TANK_HP, COMMON_TANK_DAMAGE,
                         COMMON_TANK_SPEED, radius=24)
        self.slam_timer = 2.0
        self.knockback_resistance = 0.85  # Casi inmune a retroceso
        self.image = AssetLoader.get_tank_sprite(0)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def update(self, dt: float, player, enemies, combat_system):
        self.update_base(dt)
        if not self.is_alive:
            return

        to_player = player.pos - self.pos
        dist = to_player.length()

        if dist > 0:
            direction = to_player.normalize()
            self.facing_angle = math.degrees(math.atan2(to_player.y, to_player.x))
            repulsion = self.separate_from_others(enemies, min_dist=42.0)
            self.pos += (direction * self.speed + repulsion) * dt

            if dist <= self.radius + player.radius + 18:
                self.slam_timer -= dt
                if self.slam_timer <= 0:
                    self.slam_timer = 1.9
                    if player.take_damage(self.damage):
                        combat_system.create_damage_text(player.pos.x, player.pos.y - 15,
                                                         self.damage, color=(255, 100, 100), is_critical=True)
                        combat_system.emit_impact_particles(player.pos.x, player.pos.y, count=18,
                                                            color=COLOR_BRASS)
                    # Desatar onda sísmica de área al golpear el suelo con el martillo
                    combat_system.spawn_shockwave(
                        self.pos.x, self.pos.y, max_radius=85.0, speed=260.0,
                        damage=38.0, color=(212, 160, 23), is_player=False
                    )

        self.update_base(dt)
        self.image = AssetLoader.get_tank_sprite(self.facing_angle)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def draw(self, surface: pygame.Surface):
        if self.is_alive:
            self.draw_sprite_with_flash(surface, self.image, self.rect)
            self.draw_health_bar(surface)


class MiniMinion(Enemy):
    """Mini-Autómata invocado por el Nigromante: Hostigador veloz."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, hp=35, damage=18, speed=190.0, radius=10)
        self.image = AssetLoader.get_minion_sprite(0)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def update(self, dt: float, player, enemies, combat_system):
        self.update_base(dt)
        if not self.is_alive:
            return

        to_player = player.pos - self.pos
        dist = to_player.length()
        if dist > 0:
            direction = to_player.normalize()
            self.facing_angle = math.degrees(math.atan2(to_player.y, to_player.x))
            self.pos += direction * self.speed * dt

            if dist <= self.radius + player.radius:
                if self.attack_timer <= 0:
                    player.take_damage(self.damage)
                    self.attack_timer = 0.65

        if self.attack_timer > 0:
            self.attack_timer -= dt

        self.update_base(dt)
        self.image = AssetLoader.get_minion_sprite(self.facing_angle)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def draw(self, surface: pygame.Surface):
        if self.is_alive:
            self.draw_sprite_with_flash(surface, self.image, self.rect)


# =============================================================================
# =============================================================================
# SECCIÓN 1.5: 5 NUEVAS VARIANTES DE ENEMIGOS COMUNES Y TÁCTICOS
# =============================================================================

class ClockworkBomb:
    """Bomba de relojería arrojada por el Artificiero de Relojería."""

    def __init__(self, start_x: float, start_y: float, target_x: float, target_y: float, damage: float):
        self.start_pos = pygame.math.Vector2(start_x, start_y)
        self.pos = pygame.math.Vector2(start_x, start_y)
        self.target_pos = pygame.math.Vector2(target_x, target_y)
        self.damage = damage
        self.flight_timer = 0.0
        self.flight_duration = 0.60
        self.fuse_timer = 0.95
        self.is_exploded = False
        self.radius = 9

    def update(self, dt: float, combat_system) -> bool:
        """Retorna True si sigue activa, False si ya detonó y debe eliminarse."""
        if self.is_exploded:
            return False

        if self.flight_timer < self.flight_duration:
            self.flight_timer += dt
            t = min(1.0, self.flight_timer / self.flight_duration)
            self.pos = self.start_pos.lerp(self.target_pos, t)
        else:
            self.pos = self.target_pos
            self.fuse_timer -= dt
            if self.fuse_timer <= 0:
                self.explode(combat_system)
                return False
        return True

    def explode(self, combat_system):
        self.is_exploded = True
        # Onda de choque expansiva de vapor candente
        combat_system.spawn_shockwave(
            self.pos.x, self.pos.y, max_radius=100.0, speed=260.0,
            damage=self.damage, color=(240, 140, 30), is_player=False
        )
        # Metralla de 4 esquirlas metálicas diagonales
        angles = [math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4]
        for ang in angles:
            combat_system.spawn_projectile(
                self.pos.x, self.pos.y, math.cos(ang), math.sin(ang),
                damage=self.damage * 0.45, speed=300.0,
                element="Metal", is_player=False, radius=7
            )
        combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=16, color=(255, 120, 20))

    def draw(self, surface: pygame.Surface):
        if self.is_exploded:
            return
        t = min(1.0, self.flight_timer / self.flight_duration) if self.flight_duration > 0 else 1.0
        arc_offset = math.sin(t * math.pi) * 36.0
        draw_x = int(self.pos.x)
        draw_y = int(self.pos.y - arc_offset)

        # Sombra en el suelo
        sh_surf = AssetLoader.get_shadow_sprite(rx=10, ry=5)
        surface.blit(sh_surf, (int(self.pos.x - sh_surf.get_width() // 2), int(self.pos.y - sh_surf.get_height() // 2)))

        # Cuerpo esférico de latón con remaches
        pygame.draw.circle(surface, (45, 40, 35), (draw_x, draw_y), self.radius + 1)
        pygame.draw.circle(surface, COLOR_BRASS, (draw_x, draw_y), self.radius)
        pygame.draw.circle(surface, COLOR_COPPER, (draw_x, draw_y), self.radius - 2)

        # Mecha encendida con chispas parpadeantes
        fuse_x = draw_x + 3
        fuse_y = draw_y - self.radius
        pygame.draw.line(surface, (120, 100, 70), (draw_x, draw_y - 2), (fuse_x, fuse_y), 2)
        spark_col = (255, 230, 80) if (int(self.fuse_timer * 12) % 2 == 0) else (255, 60, 20)
        pygame.draw.circle(surface, spark_col, (fuse_x, fuse_y), 3)

        # Círculo de aviso telegrafiado cuando está en el suelo antes de estallar
        if self.flight_timer >= self.flight_duration:
            ratio = max(0.1, self.fuse_timer / 0.95)
            warn_rad = int(100.0 * (1.0 - ratio * 0.3))
            pygame.draw.circle(surface, (240, 100, 30), (int(self.pos.x), int(self.pos.y)), warn_rad, 1)


class ClockworkBombardier(Enemy):
    """Artificiero de Relojería / Bombardero de Vapor: Lanza bombas de tiempo con onda expansiva y metralla."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, COMMON_BOMBARDIER_HP, COMMON_BOMBARDIER_DAMAGE,
                         COMMON_BOMBARDIER_SPEED, radius=19)
        self.bombs = []
        self.bomb_cooldown = 2.6
        self.bomb_timer = random.uniform(0.6, 1.8)
        self.windup_timer = 0.0
        self.image = AssetLoader.get_bombardier_sprite(0)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def update(self, dt: float, player, enemies, combat_system):
        self.update_base(dt)

        # Actualizar bombas activas lanzadas
        self.bombs = [b for b in self.bombs if b.update(dt, combat_system)]

        if not self.is_alive:
            return

        to_player = player.pos - self.pos
        dist = to_player.length()

        if dist > 0:
            direction = to_player.normalize()
            self.facing_angle = math.degrees(math.atan2(to_player.y, to_player.x))

            # Posicionamiento táctico: retiene distancia prudente (230-360px)
            if self.windup_timer <= 0:
                if dist < 220:
                    self.pos -= direction * (self.speed * 0.9) * dt
                elif dist > 350:
                    self.pos += direction * self.speed * dt

                repulsion = self.separate_from_others(enemies, min_dist=35.0)
                self.pos += repulsion * dt

        if self.windup_timer > 0:
            self.windup_timer -= dt
            if self.windup_timer <= 0 and dist > 0:
                # Lanzar bomba hacia la posición del jugador con pequeña anticipación
                lead_pos = player.pos + player.vel * 0.3 if hasattr(player, 'vel') else player.pos
                lead_x = max(60, min(SCREEN_WIDTH - 60, lead_pos.x))
                lead_y = max(60, min(SCREEN_HEIGHT - 60, lead_pos.y))
                self.bombs.append(ClockworkBomb(self.pos.x, self.pos.y, lead_x, lead_y, self.damage))
                combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=10, color=COLOR_BRASS)
        else:
            self.bomb_timer -= dt
            if self.bomb_timer <= 0 and 0 < dist < 580:
                self.bomb_timer = self.bomb_cooldown
                self.windup_timer = 0.40  # Pausa de preparación telegrafiada con silbato
                combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=6, color=COLOR_STEAM)

        # Daño por contacto si el jugador se acerca
        if dist <= self.radius + player.radius:
            if self.attack_timer <= 0:
                player.take_damage(self.damage * 0.5)
                self.attack_timer = self.attack_cooldown
        if self.attack_timer > 0:
            self.attack_timer -= dt

        self.update_base(dt)
        self.image = AssetLoader.get_bombardier_sprite(self.facing_angle)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def draw(self, surface: pygame.Surface):
        # Dibujar bombas en vuelo o suelo
        for b in self.bombs:
            b.draw(surface)

        if self.is_alive:
            self.draw_sprite_with_flash(surface, self.image, self.rect)
            self.draw_health_bar(surface)
            if self.windup_timer > 0:
                pygame.draw.circle(surface, (255, 140, 0), (int(self.pos.x), int(self.pos.y - self.radius - 8)), 3)


class AlchemicalPlagueDoctor(Enemy):
    """Médico de la Peste Alquímico: Emite miasma tóxico, lanza charcos de ácido y cura a sus aliados."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, COMMON_PLAGUE_DOCTOR_HP, COMMON_PLAGUE_DOCTOR_DAMAGE,
                         COMMON_PLAGUE_DOCTOR_SPEED, radius=20)
        self.acid_cooldown = 3.6
        self.acid_timer = random.uniform(1.0, 2.2)
        self.heal_cooldown = 4.8
        self.heal_timer = random.uniform(2.5, 4.0)
        self.miasma_radius = 55.0
        self.pulse = random.uniform(0, 10)
        self.image = AssetLoader.get_plague_doctor_sprite(0)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def update(self, dt: float, player, enemies, combat_system):
        self.update_base(dt)
        if not self.is_alive:
            return

        self.pulse += dt * 4.0
        to_player = player.pos - self.pos
        dist = to_player.length()

        if dist > 0:
            direction = to_player.normalize()
            self.facing_angle = math.degrees(math.atan2(to_player.y, to_player.x))

            # Se desplaza a media distancia (~180-280px)
            if dist < 170:
                self.pos -= direction * (self.speed * 0.8) * dt
            elif dist > 260:
                self.pos += direction * self.speed * dt

            repulsion = self.separate_from_others(enemies, min_dist=38.0)
            self.pos += repulsion * dt

        # Pasiva de Miasma Tóxico: Daña al jugador si está dentro del aura corrosiva (y no está en dash)
        if dist <= self.miasma_radius + player.radius and not player.is_dashing:
            if player.take_damage(16.0 * dt):
                if random.random() < 0.2:
                    combat_system.create_damage_text(player.pos.x, player.pos.y - 12, 5.0, color=(46, 204, 113))

        # Habilidad 1: Arrojar Frasco de Ácido Alquímico
        self.acid_timer -= dt
        if self.acid_timer <= 0 and 0 < dist < 500:
            self.acid_timer = self.acid_cooldown
            target_x = player.pos.x + random.uniform(-15, 15)
            target_y = player.pos.y + random.uniform(-15, 15)
            combat_system.spawn_ground_hazard(
                target_x, target_y, "Ácido Alquímico", radius=52.0, duration=3.2,
                damage_per_sec=36.0, color=(46, 204, 113), is_player=False
            )
            combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=10, color=(46, 204, 113))

        # Habilidad 2: Vapor Restaurador Alquímico (Cura a aliados cercanos)
        self.heal_timer -= dt
        if self.heal_timer <= 0:
            self.heal_timer = self.heal_cooldown
            healed_any = False
            for other in enemies:
                if other is not self and getattr(other, 'is_alive', False):
                    d_ally = (self.pos - other.pos).length()
                    if d_ally <= 160.0 and other.current_hp < other.max_hp:
                        other.current_hp = min(other.max_hp, other.current_hp + 28.0)
                        combat_system.create_damage_text(other.pos.x, other.pos.y - 15,
                                                         28.0, color=(46, 204, 113))
                        combat_system.emit_impact_particles(other.pos.x, other.pos.y, count=8, color=(46, 204, 113))
                        healed_any = True
            if healed_any:
                combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=16, color=(80, 240, 140))

        # Daño por contacto físico
        if dist <= self.radius + player.radius:
            if self.attack_timer <= 0:
                player.take_damage(self.damage)
                self.attack_timer = self.attack_cooldown
        if self.attack_timer > 0:
            self.attack_timer -= dt

        self.update_base(dt)
        self.image = AssetLoader.get_plague_doctor_sprite(self.facing_angle)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def draw(self, surface: pygame.Surface):
        if self.is_alive:
            # Aura de miasma tóxico giratoria
            aura_rad = int(self.miasma_radius + 4 * math.sin(self.pulse * 1.5))
            aura_surf = pygame.Surface((aura_rad * 2 + 4, aura_rad * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (46, 204, 113, 35), (aura_rad + 2, aura_rad + 2), aura_rad)
            pygame.draw.circle(aura_surf, (39, 174, 96, 75), (aura_rad + 2, aura_rad + 2), aura_rad, 1)
            surface.blit(aura_surf, (int(self.pos.x - aura_rad - 2), int(self.pos.y - aura_rad - 2)))

            self.draw_sprite_with_flash(surface, self.image, self.rect)
            self.draw_health_bar(surface)


class BrassShieldGuardian(Enemy):
    """Guardián de Escudo de Latón: Escudo torre que bloquea 75% del daño frontal, golpe de escudo sísmico."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, COMMON_SHIELD_GUARDIAN_HP, COMMON_SHIELD_GUARDIAN_DAMAGE,
                         COMMON_SHIELD_GUARDIAN_SPEED, radius=23)
        self.knockback_resistance = 0.82  # Súper-armadura pesada
        self.bash_cooldown = 2.0
        self.bash_timer = random.uniform(0.5, 1.2)
        self.is_blocking_flash = 0.0
        self.last_player_pos = pygame.math.Vector2(x + 100, y)
        self.image = AssetLoader.get_shield_guardian_sprite(0)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def take_damage(self, amount: float, attacker_pos=None):
        # Determinar si el impacto proviene del arco frontal del escudo (+/- 65 grados)
        check_pos = attacker_pos if attacker_pos is not None else self.last_player_pos
        to_attacker = check_pos - self.pos
        if to_attacker.length_squared() > 0:
            ang_to_atk = math.degrees(math.atan2(to_attacker.y, to_attacker.x))
            angle_diff = abs((self.facing_angle - ang_to_atk + 180) % 360 - 180)
            if angle_diff < 68.0:
                # Bloqueo frontal con escudo: -75% de daño
                amount *= 0.25
                self.is_blocking_flash = 0.20

        super().take_damage(amount)

    def update(self, dt: float, player, enemies, combat_system):
        self.update_base(dt)
        if not self.is_alive:
            return

        self.last_player_pos = pygame.math.Vector2(player.pos.x, player.pos.y)
        to_player = player.pos - self.pos
        dist = to_player.length()

        if self.is_blocking_flash > 0:
            self.is_blocking_flash -= dt

        if dist > 0:
            direction = to_player.normalize()
            self.facing_angle = math.degrees(math.atan2(to_player.y, to_player.x))

            # Avanza con determinación hacia el jugador
            repulsion = self.separate_from_others(enemies, min_dist=42.0)
            self.pos += (direction * self.speed + repulsion) * dt

            # Ataque de Embestida con Escudo (Shield Bash) a corta distancia
            self.bash_timer -= dt
            if dist <= self.radius + player.radius + 20 and self.bash_timer <= 0:
                self.bash_timer = self.bash_cooldown
                if player.take_damage(self.damage):
                    combat_system.create_damage_text(player.pos.x, player.pos.y - 15,
                                                     self.damage, color=COLOR_BRASS, is_critical=True)
                    combat_system.emit_impact_particles(player.pos.x, player.pos.y, count=14, color=COLOR_BRASS)
                # Onda de choque frontal de escudo
                combat_system.spawn_shockwave(
                    self.pos.x, self.pos.y, max_radius=80.0, speed=260.0,
                    damage=self.damage * 0.65, color=COLOR_BRASS, is_player=False
                )

        self.update_base(dt)
        self.image = AssetLoader.get_shield_guardian_sprite(self.facing_angle)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def draw(self, surface: pygame.Surface):
        if self.is_alive:
            # Resplandor de bloqueo cuando rechaza un impacto frontal
            if self.is_blocking_flash > 0:
                rad_f = math.radians(self.facing_angle)
                shield_x = int(self.pos.x + math.cos(rad_f) * (self.radius + 6))
                shield_y = int(self.pos.y + math.sin(rad_f) * (self.radius + 6))
                pygame.draw.circle(surface, COLOR_GOLD, (shield_x, shield_y), 12, 3)
                pygame.draw.circle(surface, COLOR_WHITE, (shield_x, shield_y), 6)

            self.draw_sprite_with_flash(surface, self.image, self.rect)
            self.draw_health_bar(surface)


class ArcaneCultist(Enemy):
    """Cultista de la Forja Arcana: Canaliza ataques rúnicos con láser guía y desata andanadas de orbes arcanos."""

    STATE_MOVE = "MOVE"
    STATE_CHANNEL = "CHANNEL"
    STATE_RECOVER = "RECOVER"

    def __init__(self, x: float, y: float):
        super().__init__(x, y, COMMON_ARCANE_CULTIST_HP, COMMON_ARCANE_CULTIST_DAMAGE,
                         COMMON_ARCANE_CULTIST_SPEED, radius=17)
        self.state = self.STATE_MOVE
        self.channel_timer = 0.0
        self.recover_timer = 0.0
        self.attack_cooldown_timer = random.uniform(1.2, 2.5)
        self.pulse = random.uniform(0, 10)
        self.laser_target = None
        self.image = AssetLoader.get_cultist_sprite(0, 0)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def update(self, dt: float, player, enemies, combat_system):
        self.update_base(dt)
        if not self.is_alive:
            return

        self.pulse += dt * 5.0
        to_player = player.pos - self.pos
        dist = to_player.length()

        if dist > 0:
            self.facing_angle = math.degrees(math.atan2(to_player.y, to_player.x))

        if self.state == self.STATE_MOVE:
            self.attack_cooldown_timer -= dt
            if dist > 0:
                direction = to_player.normalize()
                if dist < 210:
                    self.pos -= direction * (self.speed * 0.9) * dt
                elif dist > 340:
                    self.pos += direction * self.speed * dt

                repulsion = self.separate_from_others(enemies, min_dist=32.0)
                self.pos += repulsion * dt

            # Iniciar canalización rúnica
            if self.attack_cooldown_timer <= 0 and 0 < dist < 580:
                self.state = self.STATE_CHANNEL
                self.channel_timer = 1.10  # 1.1s de telegrafía con láser
                self.laser_target = pygame.math.Vector2(player.pos.x, player.pos.y)

        elif self.state == self.STATE_CHANNEL:
            self.channel_timer -= dt
            # El láser guía sigue suavemente al jugador
            if self.laser_target and dist > 0:
                self.laser_target = self.laser_target.lerp(player.pos, dt * 6.0)

            combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=1, color=(170, 80, 255))

            if self.channel_timer <= 0:
                # Disparar andanada triple de orbes arcanos
                if self.laser_target:
                    dir_aim = (self.laser_target - self.pos).normalize()
                    base_ang = math.atan2(dir_aim.y, dir_aim.x)
                    for ang_off in [-0.22, 0.0, 0.22]:
                        rad = base_ang + ang_off
                        combat_system.spawn_projectile(
                            self.pos.x, self.pos.y, math.cos(rad), math.sin(rad),
                            damage=self.damage * 0.70, speed=260.0,
                            element="Oscuridad", is_player=False, radius=9
                        )
                combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=14, color=(170, 80, 255))

                # Entra en estado de recuperación/exhausto (ventana de vulnerabilidad para el jugador)
                self.state = self.STATE_RECOVER
                self.recover_timer = 0.85
                self.laser_target = None

        elif self.state == self.STATE_RECOVER:
            self.recover_timer -= dt
            if self.recover_timer <= 0:
                self.state = self.STATE_MOVE
                self.attack_cooldown_timer = 2.4

        # Daño por contacto si el jugador choca
        if dist <= self.radius + player.radius:
            if self.attack_timer <= 0:
                player.take_damage(self.damage * 0.5)
                self.attack_timer = self.attack_cooldown
        if self.attack_timer > 0:
            self.attack_timer -= dt

        self.update_base(dt)
        self.image = AssetLoader.get_cultist_sprite(self.facing_angle, self.pulse)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def draw(self, surface: pygame.Surface):
        if self.is_alive:
            # Si está canalizando, dibujar círculo rúnico en el suelo y haz láser guía telegrafiado
            if self.state == self.STATE_CHANNEL and self.laser_target:
                rune_rad = 26
                pygame.draw.circle(surface, (170, 80, 255), (int(self.pos.x), int(self.pos.y)), rune_rad, 2)
                pygame.draw.line(surface, (170, 80, 255), (int(self.pos.x), int(self.pos.y)),
                                 (int(self.laser_target.x), int(self.laser_target.y)), 1)
                pygame.draw.circle(surface, (230, 150, 255), (int(self.laser_target.x), int(self.laser_target.y)), 5, 1)

            self.draw_sprite_with_flash(surface, self.image, self.rect)
            self.draw_health_bar(surface)


class CursedReaper(Enemy):
    """Segador Mecánico de Cadena: Asesino veloz con arpón de cadena de vapor y torbellino de guadaña en 360°."""

    STATE_STALK = "STALK"
    STATE_HOOK_WINDUP = "HOOK_WINDUP"
    STATE_HOOK_PULL = "HOOK_PULL"
    STATE_WHIRLWIND_WINDUP = "WHIRLWIND_WINDUP"
    STATE_WHIRLWIND = "WHIRLWIND"

    def __init__(self, x: float, y: float):
        super().__init__(x, y, COMMON_REAPER_HP, COMMON_REAPER_DAMAGE,
                         COMMON_REAPER_SPEED, radius=19)
        self.state = self.STATE_STALK
        self.state_timer = 0.0
        self.hook_cooldown = 3.6
        self.hook_cooldown_timer = random.uniform(1.0, 2.5)
        self.hook_target = None
        self.whirlwind_cooldown = 1.6
        self.whirlwind_timer = 0.0
        self.whirlwind_radius = 68.0
        self.image = AssetLoader.get_reaper_sprite(0)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def update(self, dt: float, player, enemies, combat_system):
        self.update_base(dt)
        if not self.is_alive:
            return

        to_player = player.pos - self.pos
        dist = to_player.length()

        if dist > 0:
            self.facing_angle = math.degrees(math.atan2(to_player.y, to_player.x))

        if self.state == self.STATE_STALK:
            self.hook_cooldown_timer -= dt
            self.whirlwind_timer -= dt

            if dist > 0:
                direction = to_player.normalize()
                repulsion = self.separate_from_others(enemies, min_dist=32.0)
                self.pos += (direction * self.speed + repulsion) * dt

            # Si está muy cerca, preparar torbellino de guadaña
            if dist <= self.radius + player.radius + 18 and self.whirlwind_timer <= 0:
                self.state = self.STATE_WHIRLWIND_WINDUP
                self.state_timer = 0.32  # 0.32s de preparación telegrafiada
                combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=6, color=(220, 40, 40))

            # Si está a media distancia, lanzar arpón de cadena
            elif self.hook_cooldown_timer <= 0 and 150 < dist < 360:
                self.state = self.STATE_HOOK_WINDUP
                self.state_timer = 0.30
                self.hook_target = pygame.math.Vector2(player.pos.x, player.pos.y)

        elif self.state == self.STATE_HOOK_WINDUP:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = self.STATE_HOOK_PULL
                self.state_timer = 0.28
                combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=8, color=COLOR_STEAM)

        elif self.state == self.STATE_HOOK_PULL:
            self.state_timer -= dt
            # Tirón veloz hacia la posición del anzuelo
            if self.hook_target:
                to_hook = self.hook_target - self.pos
                if to_hook.length() > 20:
                    self.pos += to_hook.normalize() * 520.0 * dt
                else:
                    self.state = self.STATE_STALK
                    self.hook_cooldown_timer = self.hook_cooldown
                    self.hook_target = None
            if self.state_timer <= 0:
                self.state = self.STATE_STALK
                self.hook_cooldown_timer = self.hook_cooldown
                self.hook_target = None

        elif self.state == self.STATE_WHIRLWIND_WINDUP:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = self.STATE_WHIRLWIND
                self.state_timer = 0.22
                # Ejecutar torbellino de 360°
                if dist <= self.whirlwind_radius + player.radius:
                    if player.take_damage(self.damage):
                        combat_system.create_damage_text(player.pos.x, player.pos.y - 15,
                                                         self.damage, color=(230, 45, 45), is_critical=True)
                        combat_system.emit_impact_particles(player.pos.x, player.pos.y, count=16, color=(230, 45, 45))
                combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=18, color=COLOR_BRASS)

        elif self.state == self.STATE_WHIRLWIND:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = self.STATE_STALK
                self.whirlwind_timer = self.whirlwind_cooldown

        self.update_base(dt)
        self.image = AssetLoader.get_reaper_sprite(self.facing_angle)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def draw(self, surface: pygame.Surface):
        if self.is_alive:
            # Dibujar cadena de arpón si está enganchando o tirando
            if (self.state in (self.STATE_HOOK_WINDUP, self.STATE_HOOK_PULL)) and self.hook_target:
                pygame.draw.line(surface, COLOR_BRASS, (int(self.pos.x), int(self.pos.y)),
                                 (int(self.hook_target.x), int(self.hook_target.y)), 3)
                pygame.draw.circle(surface, (220, 40, 40), (int(self.hook_target.x), int(self.hook_target.y)), 6)

            # Dibujar aviso de preparación de torbellino
            if self.state == self.STATE_WHIRLWIND_WINDUP:
                pygame.draw.circle(surface, (230, 45, 45), (int(self.pos.x), int(self.pos.y)),
                                   int(self.whirlwind_radius), 2)
            elif self.state == self.STATE_WHIRLWIND:
                pygame.draw.circle(surface, (255, 80, 80), (int(self.pos.x), int(self.pos.y)),
                                   int(self.whirlwind_radius), 4)

            self.draw_sprite_with_flash(surface, self.image, self.rect)
            self.draw_health_bar(surface)


# SECCIÓN 2: ESPÍRITUS MALIGNOS (ÉLITES CON 5 VARIANTES BALANCEADAS)
# =============================================================================

class EvilSpirit(Enemy):
    """Clase base para las 5 variantes de Espíritus Malignos."""

    def __init__(self, x: float, y: float, variant_name: str = "Penumbra"):
        super().__init__(x, y, ELITE_SPIRIT_HP, ELITE_SPIRIT_DAMAGE,
                         ELITE_SPIRIT_SPEED, radius=22)
        self.variant = variant_name
        self.pulse = 0.0
        self.cast_timer = 2.0
        self.is_vulnerable = False
        self.vulnerable_timer = 0.0
        self.image = AssetLoader.get_spirit_variant_sprite(self.variant, 0)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def draw(self, surface: pygame.Surface):
        if self.is_alive:
            # Aura rúnica pulsante de espíritu élite en el suelo
            aura_rad = int(24 + 4 * math.sin(self.pulse * 2.0))
            aura_surf = pygame.Surface((aura_rad * 2 + 4, aura_rad * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (241, 196, 15, 60), (aura_rad + 2, aura_rad + 2), aura_rad, 2)
            surface.blit(aura_surf, (int(self.pos.x - aura_rad - 2), int(self.pos.y - aura_rad - 2)))

            sprite = AssetLoader.get_spirit_variant_sprite(self.variant, self.pulse)
            rect = sprite.get_rect(center=(int(self.pos.x), int(self.pos.y)))
            self.draw_sprite_with_flash(surface, sprite, rect)
            self.draw_health_bar(surface)


class ShadowSpirit(EvilSpirit):
    """Variante 1: Espectro de Penumbra. Dispara orbe sombrío, deja un señuelo y se teletransporta."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, "Penumbra")
        self.decoy_pos = None
        self.decoy_timer = 0.0

    def update(self, dt: float, player, enemies, combat_system):
        self.update_base(dt)
        if not self.is_alive:
            return

        self.pulse += dt * 5.0
        to_player = player.pos - self.pos
        dist = to_player.length()

        if self.decoy_timer > 0:
            self.decoy_timer -= dt
            if self.decoy_timer <= 0:
                self.decoy_pos = None

        if self.vulnerable_timer > 0:
            self.vulnerable_timer -= dt
            return

        if dist > 0:
            self.facing_angle = math.degrees(math.atan2(to_player.y, to_player.x))
            repulsion = self.separate_from_others(enemies, min_dist=35.0)
            self.pos += ((to_player.normalize() * (self.speed * 0.4)) + repulsion) * dt

        self.cast_timer -= dt
        if self.cast_timer <= 0:
            self.cast_timer = 3.6
            dir_p = (player.pos - self.pos).normalize() if dist > 0 else pygame.math.Vector2(1, 0)
            combat_system.spawn_projectile(
                self.pos.x, self.pos.y, dir_p.x, dir_p.y,
                damage=30.0, speed=230.0, element="Oscuridad", is_player=False
            )
            # Deja un señuelo en su posición previa
            self.decoy_pos = pygame.math.Vector2(self.pos.x, self.pos.y)
            self.decoy_timer = 1.4

            # Teletransporte a posición segura telegrafiada
            angle = random.uniform(0, 2 * math.pi)
            tele_dist = 200.0
            new_x = max(80, min(SCREEN_WIDTH - 80, player.pos.x + math.cos(angle) * tele_dist))
            new_y = max(80, min(SCREEN_HEIGHT - 80, player.pos.y + math.sin(angle) * tele_dist))
            combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=15, color=(138, 43, 226))
            self.pos.x = new_x
            self.pos.y = new_y
            combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=15, color=(138, 43, 226))
            self.vulnerable_timer = 1.4

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        # Dibujar señuelo ilusorio semi-transparente
        if self.is_alive and self.decoy_pos and self.decoy_timer > 0:
            decoy_surf = AssetLoader.get_spirit_variant_sprite("Penumbra", self.pulse).copy()
            decoy_surf.set_alpha(int(110 * (self.decoy_timer / 1.4)))
            d_rect = decoy_surf.get_rect(center=(int(self.decoy_pos.x), int(self.decoy_pos.y)))
            surface.blit(decoy_surf, d_rect)


class FlameSpirit(EvilSpirit):
    """Variante 2: Llama Fatua. Escudo ígneo orbital que se dispara secuencialmente en proyectiles telegrafiados."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, "Llama Fatua")
        self.orbit_angle = 0.0

    def update(self, dt: float, player, enemies, combat_system):
        self.update_base(dt)
        if not self.is_alive:
            return

        self.pulse += dt * 6.0
        self.orbit_angle += dt * 4.0
        to_player = player.pos - self.pos
        dist = to_player.length()

        if self.vulnerable_timer > 0:
            self.vulnerable_timer -= dt
            return

        if dist > 0:
            self.pos += to_player.normalize() * (self.speed * 0.5) * dt

        self.cast_timer -= dt
        if self.cast_timer <= 0:
            self.cast_timer = 3.2
            base_dir = (player.pos - self.pos).normalize() if dist > 0 else pygame.math.Vector2(1, 0)
            base_ang = math.atan2(base_dir.y, base_dir.x)
            for offset in [-0.30, 0.0, 0.30]:
                rad = base_ang + offset
                def on_flame_hit(pos):
                    combat_system.spawn_ground_hazard(
                        pos.x, pos.y, "Lava", radius=45.0, duration=2.0,
                        damage_per_sec=40.0, color=(231, 76, 60), is_player=False
                    )
                combat_system.spawn_projectile(
                    self.pos.x, self.pos.y, math.cos(rad), math.sin(rad),
                    damage=self.damage * 0.7, speed=230.0, element="Fuego",
                    is_player=False, on_hit_effect=on_flame_hit
                )
            self.vulnerable_timer = 1.3

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        if self.is_alive and self.vulnerable_timer <= 0:
            # Dibujar 3 orbes ígneos orbitales
            for i in range(3):
                theta = self.orbit_angle + (2 * math.pi / 3) * i
                ox = self.pos.x + math.cos(theta) * 30.0
                oy = self.pos.y + math.sin(theta) * 30.0
                pygame.draw.circle(surface, (255, 140, 0), (int(ox), int(oy)), 5)


class FrostSpirit(EvilSpirit):
    """Variante 3: Espectro Glacial. Siembra 3 cristales de hielo en el suelo con 1.8s de aviso antes de estallar."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, "Glacial")
        self.crystals = []

    def update(self, dt: float, player, enemies, combat_system):
        self.update_base(dt)
        if not self.is_alive:
            return

        self.pulse += dt * 4.0
        to_player = player.pos - self.pos
        dist = to_player.length()

        # Actualizar cristales de escarcha
        alive_crystals = []
        for cr in self.crystals:
            cr["timer"] -= dt
            if cr["timer"] <= 0:
                # Estallar en 6 esquirlas gélidas
                for i in range(6):
                    theta = (2 * math.pi / 6) * i
                    combat_system.spawn_projectile(
                        cr["x"], cr["y"], math.cos(theta), math.sin(theta),
                        damage=22.0, speed=200.0, element="Agua", is_player=False, radius=8
                    )
                combat_system.emit_impact_particles(cr["x"], cr["y"], count=15, color=(175, 238, 238))
            else:
                alive_crystals.append(cr)
        self.crystals = alive_crystals

        if self.vulnerable_timer > 0:
            self.vulnerable_timer -= dt
            return

        if dist > 0:
            self.facing_angle = math.degrees(math.atan2(to_player.y, to_player.x))
            self.pos += to_player.normalize() * (self.speed * 0.5) * dt

        self.cast_timer -= dt
        if self.cast_timer <= 0 and dist < 320:
            self.cast_timer = 4.0
            # Colocar 3 cristales de escarcha alrededor del jugador
            for offset_ang in [-0.5, 0.0, 0.5]:
                cx = player.pos.x + math.cos(math.radians(self.facing_angle) + offset_ang) * 90.0
                cy = player.pos.y + math.sin(math.radians(self.facing_angle) + offset_ang) * 90.0
                self.crystals.append({"x": cx, "y": cy, "timer": 1.8})
            self.vulnerable_timer = 1.3

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        if self.is_alive:
            for cr in self.crystals:
                # Círculo de aviso telegrafiado que se reduce
                pygame.draw.circle(surface, (0, 206, 209), (int(cr["x"]), int(cr["y"])), 35, 2)
                pygame.draw.circle(surface, COLOR_WHITE, (int(cr["x"]), int(cr["y"])), 6)


class StormSpirit(EvilSpirit):
    """Variante 4: Espíritu de Tormenta. Vínculo eléctrico telegrafiado; se rompe usando el Dash o alejándose."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, "Tormenta")
        self.tether_active = False
        self.tether_timer = 0.0

    def update(self, dt: float, player, enemies, combat_system):
        self.update_base(dt)
        if not self.is_alive:
            return

        self.pulse += dt * 7.0
        to_player = player.pos - self.pos
        dist = to_player.length()

        # Mecánica de vínculo eléctrico
        if self.tether_active:
            self.tether_timer -= dt
            self.tether_player_pos = (int(player.pos.x), int(player.pos.y))
            combat_system.emit_impact_particles(self.pos.x, self.pos.y, count=1, color=COLOR_GOLD)

            # Si el jugador se aleja más de 240px o usa el Dash -> El cable se rompe
            if dist > 240 or player.is_dashing:
                self.tether_active = False
                self.vulnerable_timer = 1.4  # Espíritu queda aturdido al romperse el vínculo
                combat_system.emit_impact_particles((self.pos.x + player.pos.x) / 2,
                                                    (self.pos.y + player.pos.y) / 2,
                                                    count=15, color=COLOR_GOLD)
            elif self.tether_timer <= 0:
                # Descarga fulgurante
                self.tether_active = False
                player.take_damage(45.0)
                combat_system.create_damage_text(player.pos.x, player.pos.y - 15, 45.0,
                                                 color=COLOR_GOLD, is_critical=True)
                combat_system.emit_impact_particles(player.pos.x, player.pos.y, count=20, color=COLOR_GOLD)
                self.vulnerable_timer = 1.2
            return

        if self.vulnerable_timer > 0:
            self.vulnerable_timer -= dt
            return

        if dist > 0:
            self.pos += to_player.normalize() * (self.speed * 0.5) * dt

        self.cast_timer -= dt
        if self.cast_timer <= 0 and dist < 220:
            self.cast_timer = 4.2
            self.tether_active = True
            self.tether_timer = 1.1  # 1.1s para dashear o correr

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        if self.is_alive and self.tether_active and hasattr(self, 'tether_player_pos'):
            # Línea de rayo telegrafiada entre espíritu y jugador
            pygame.draw.line(surface, COLOR_GOLD, (int(self.pos.x), int(self.pos.y)),
                             self.tether_player_pos, 2)
            pygame.draw.line(surface, COLOR_WHITE, (int(self.pos.x), int(self.pos.y)),
                             self.tether_player_pos, 1)


class NecroSpirit(EvilSpirit):
    """Variante 5: Espíritu Nigromante. Invoca mini-autómatas y maldice el suelo con círculos de aviso."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, "Nigromante")
        self.pending_curse = None
        self.curse_timer = 0.0

    def update(self, dt: float, player, enemies, combat_system):
        self.update_base(dt)
        if not self.is_alive:
            return

        self.pulse += dt * 4.0
        to_player = player.pos - self.pos
        dist = to_player.length()

        if self.pending_curse:
            self.curse_timer -= dt
            if self.curse_timer <= 0:
                combat_system.spawn_ground_hazard(
                    self.pending_curse[0], self.pending_curse[1], "Zarzas", radius=65.0,
                    duration=2.2, damage_per_sec=50.0, color=(40, 180, 60), is_player=False
                )
                self.pending_curse = None

        if self.vulnerable_timer > 0:
            self.vulnerable_timer -= dt
            return

        if dist > 0:
            self.pos += to_player.normalize() * (self.speed * 0.4) * dt

        self.cast_timer -= dt
        if self.cast_timer <= 0:
            self.cast_timer = 4.8
            # Marcar zona de maldición bajo el jugador con 1.2s de aviso
            self.pending_curse = (player.pos.x, player.pos.y)
            self.curse_timer = 1.2

            # Invocar 2 mini-autómatas frágiles
            for offset_x in [-25, 25]:
                minion = MiniMinion(self.pos.x + offset_x, self.pos.y)
                enemies.append(minion)
                combat_system.emit_impact_particles(minion.pos.x, minion.pos.y, count=8, color=(40, 200, 80))
            self.vulnerable_timer = 1.4

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        if self.is_alive and self.pending_curse:
            pygame.draw.circle(surface, (40, 180, 60), (int(self.pending_curse[0]), int(self.pending_curse[1])), 65, 2)


def create_random_spirit(x: float, y: float, difficulty_mult: float = 1.0) -> EvilSpirit:
    """Fábrica que genera aleatoriamente una de las 5 variantes únicas de Espíritus Malignos."""
    variants = [ShadowSpirit, FlameSpirit, FrostSpirit, StormSpirit, NecroSpirit]
    chosen_cls = random.choice(variants)
    spirit = chosen_cls(x, y)
    if difficulty_mult != 1.0:
        spirit.apply_difficulty_scaling(difficulty_mult)
    return spirit
