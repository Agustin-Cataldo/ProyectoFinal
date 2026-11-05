"""
================================================================================
MÓDULO: entities/player.py
RESPONSABILIDAD: Representación del héroe controlado por el jugador.
CONCEPTO ACADÉMICO: Encapsulamiento, Vectorización de Movimiento y Máquina de Estados Local.
================================================================================
Gestiona la física de traslación en 8 direcciones, normalización de vectores,
atributos oficiales (500 HP base, 50 daño base + 20 de espada de piedra mediana),
cooldowns de ataque y ventanas de invulnerabilidad temporal (i-frames).
"""

import math
import pygame
from settings import (
    PLAYER_BASE_HP, PLAYER_BASE_MANA, PLAYER_BASE_DAMAGE, PLAYER_WEAPON_DAMAGE,
    PLAYER_INITIAL_WEAPON, PLAYER_BASE_SPEED, PLAYER_RADIUS,
    PLAYER_ATTACK_COOLDOWN, PLAYER_INVULNERABILITY_TIME,
    PLAYER_DASH_SPEED, PLAYER_DASH_DURATION, PLAYER_DASH_COOLDOWN,
    MAGIC_SPELL_COOLDOWN, MANA_SPELL_COSTS, SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_WHITE
)
from utils.asset_loader import AssetLoader


class Player(pygame.sprite.Sprite):
    """
    Clase que modela al Héroe de la Era de Vapor.
    Hereda de pygame.sprite.Sprite para facilitar el renderizado y detección de grupos.
    """

    def __init__(self, x: float, y: float):
        super().__init__()

        # Posicionamiento vectorial continuo (subpíxel para suavidad a 60 FPS)
        self.pos = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = PLAYER_BASE_SPEED
        self.radius = PLAYER_RADIUS

        # Atributos de Combate y Progresión (Reglas del Proyecto)
        self.max_hp = float(PLAYER_BASE_HP)            # 1000 HP iniciales
        self.current_hp = float(PLAYER_BASE_HP)
        self.max_mana = float(PLAYER_BASE_MANA)        # 500 MP iniciales
        self.current_mana = float(PLAYER_BASE_MANA)

        self.base_damage = PLAYER_BASE_DAMAGE          # 50 daño base
        self.weapon_name = PLAYER_INITIAL_WEAPON       # Espada de piedra mediana
        self.weapon_damage = PLAYER_WEAPON_DAMAGE      # +20 daño suplementario

        # Atributos de Rol y Especialización Medieval
        self.role_name = "Aventurero"                  # Rol seleccionado
        self.weapon_type = "sword"                     # 'sword', 'axe', 'mace', 'daggers', 'crossbow', 'scythe', 'staff'
        self.has_melee_weapon = True                   # El Mago no tiene espada cuerpo a cuerpo
        self.life_steal = 0.0                          # Robo de vida por impacto (Berserker)
        self.crit_chance = 0.15                        # Probabilidad de crítico
        self.crit_multiplier = 2.0                    # Multiplicador de crítico
        self.holy_shockwave = False                    # Onda expansiva bendecida (Paladín)
        self.soul_harvest = False                      # Cosecha de almas (Nigromante)
        self.passive_regen = 0.0                       # Regeneración pasiva de vida (Paladín)
        self.passive_regen_timer = 0.0
        self.passive_mana_regen = 0.0                  # Regeneración pasiva de maná (Mago = +25 MP/s)
        self.basic_shot_timer = 0.0                    # Temporizador del dardo arcano básico (0 MP)
        self.basic_shot_cooldown_max = 0.28

        # Modificadores de Cartas (Se alteran dinámicamente con las cartas de mejora)
        self.bonus_damage_mult = 1.0
        self.speed_mult = 1.0
        self.damage_reduction = 0.0                    # 0.0 = 0%, 0.2 = 20%
        self.active_magic_elements = []                # Lista de magias adquiridas (Fuego, Luz, etc.)
        self._pending_spell_swap = None                # Hechizo pendiente de asignar via SpellSwapMenu

        # Regeneración fuera de combate (Regla: +10 HP cada 10s sin recibir daño)
        self.time_without_damage = 0.0

        # Dirección y orientación
        self.facing_angle = 0.0                        # Ángulo en grados hacia el cursor
        self.aim_vector = pygame.math.Vector2(1, 0)

        # Control de Ataque y Animación de Swing por Arma
        self.attack_cooldown_max = PLAYER_ATTACK_COOLDOWN
        self.attack_timer = 0.0                        # Tiempo restante para poder atacar
        self.is_swinging = False                       # Estado visual del tajo de espada/hacha/maza
        self.swing_duration = 0.14                     # Duración visual del corte en segundos
        self.swing_total_duration = 0.14
        self.swing_timer = 0.0

        # Control de Esquiva / Dash (Barra Espaciadora)
        self.is_dashing = False
        self.dash_timer = 0.0
        self.dash_cooldown_timer = 0.0
        self.dash_cooldown_max = PLAYER_DASH_COOLDOWN
        self.dash_vector = pygame.math.Vector2(1, 0)

        # Sistema de Animaciones Visuales
        self.walk_cycle = 0.0                          # Ciclo de pasos
        self.bob_y = 0.0                               # Bamboleo vertical de caminata
        self.tilt = 0.0                                # Inclinación dinámica del torso
        self.hit_flash_timer = 0.0                     # Parpadeo blanco al recibir daño
        self.afterimages = []                          # Sombras fantasma del Dash
        self.afterimage_spawn_timer = 0.0

        # Control de Hechizos Mágicos Activos (Clic Derecho y Q)
        self.magic_primary_cooldown = 0.0
        self.magic_secondary_cooldown = 0.0
        self.magic_cooldown_max = MAGIC_SPELL_COOLDOWN

        # Invulnerabilidad tras recibir daño (i-frames)
        self.invulnerable_timer = 0.0

        # Inicialización del sprite visual
        self.image = AssetLoader.get_player_sprite(0)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def has_mana(self, cost: float) -> bool:
        """Verifica si el jugador posee suficiente maná para un hechizo."""
        return self.current_mana >= cost

    def spend_mana(self, cost: float) -> bool:
        """Deduce maná para lanzar un hechizo si alcanza la reserva."""
        if self.current_mana >= cost:
            self.current_mana -= cost
            return True
        return False

    def restore_mana(self, amount: float):
        """Regenera maná sin superar el límite de 500 MP."""
        self.current_mana = min(self.max_mana, self.current_mana + amount)

    @property
    def total_damage(self) -> float:
        """
        Calcula el daño total aplicado por golpe de espada:
        Fórmula: (Daño Base 50 + Daño Arma 20) * Multiplicadores de Mejora
        Inicialmente: (50 + 20) * 1.0 = 70 DMG.
        """
        raw_damage = self.base_damage + self.weapon_damage
        return raw_damage * self.bonus_damage_mult

    def handle_input(self):
        """
        Captura las entradas del teclado para movimiento en 8 direcciones (WASD o Flechas).
        Aplica normalización euclidiana para evitar que el avance en diagonal sea más rápido.
        """
        keys = pygame.key.get_pressed()
        move_x = 0
        move_y = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move_y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_x += 1

        move_vec = pygame.math.Vector2(move_x, move_y)
        if move_vec.length_squared() > 0:
            self.velocity = move_vec.normalize() * (self.speed * self.speed_mult)
        else:
            self.velocity = pygame.math.Vector2(0, 0)

    def update_aim(self, target_pos: tuple):
        """
        Calcula el ángulo de apuntado continuo de 360 grados respecto al cursor del ratón.
        """
        dx = target_pos[0] - self.pos.x
        dy = target_pos[1] - self.pos.y

        if dx != 0 or dy != 0:
            rad = math.atan2(dy, dx)
            self.facing_angle = math.degrees(rad)
            self.aim_vector = pygame.math.Vector2(math.cos(rad), math.sin(rad))

    @property
    def primary_magic(self) -> str:
        """Retorna el primer elemento mágico adquirido por cartas, si existe."""
        if len(self.active_magic_elements) >= 1:
            return self.active_magic_elements[0]
        return None

    @property
    def secondary_magic(self) -> str:
        """Retorna el segundo elemento mágico adquirido por cartas, si existe."""
        if len(self.active_magic_elements) >= 2:
            return self.active_magic_elements[1]
        return None

    def trigger_dash(self) -> bool:
        """
        Activa un impulso de esquiva / Dash (Barra Espaciadora).
        Otorga invulnerabilidad (i-frames) y aceleración explosiva momentánea.
        """
        if self.dash_cooldown_timer <= 0 and not self.is_dashing:
            self.is_dashing = True
            self.dash_timer = PLAYER_DASH_DURATION
            self.dash_cooldown_timer = getattr(self, 'dash_cooldown_max', PLAYER_DASH_COOLDOWN)
            self.invulnerable_timer = PLAYER_DASH_DURATION + 0.08  # Breve ventana de invulnerabilidad

            # Si el jugador se está moviendo, dashea en esa dirección; si no, hacia donde apunta
            if self.velocity.length_squared() > 0:
                self.dash_vector = self.velocity.normalize()
            else:
                self.dash_vector = self.aim_vector.copy()
            return True
        return False

    def trigger_primary_magic(self) -> str:
        """
        Dispara el hechizo mágico principal con Clic Derecho si no está en recarga.
        Retorna el nombre del elemento o None si no tiene magia o está en cooldown.
        """
        if self.primary_magic and self.magic_primary_cooldown <= 0:
            self.magic_primary_cooldown = self.magic_cooldown_max
            return self.primary_magic
        return None

    def trigger_secondary_magic(self) -> str:
        """
        Dispara el hechizo mágico secundario con la Tecla Q si no está en recarga.
        Retorna el nombre del elemento o None si no tiene segunda magia o está en cooldown.
        """
        if self.secondary_magic and self.magic_secondary_cooldown <= 0:
            self.magic_secondary_cooldown = self.magic_cooldown_max
            return self.secondary_magic
        return None

    def trigger_attack(self) -> bool:
        """
        Dispara el ataque del arma medieval si no está en enfriamiento ni en dash.
        Retorna True si el ataque se activó con éxito.
        """
        if not getattr(self, 'has_melee_weapon', True) or self.weapon_type == "staff":
            return False  # El Mago no ataca cuerpo a cuerpo (usa su dardo arcano)

        if self.attack_timer <= 0 and not self.is_dashing:
            self.attack_timer = self.attack_cooldown_max
            self.is_swinging = True
            # Duración del swing según el arquetipo de arma (12 clases)
            durations = {
                "fists": 0.09,
                "daggers": 0.10,
                "crossbow": 0.12,
                "flask": 0.13,
                "sword": 0.14,
                "totem": 0.15,
                "mace": 0.16,
                "flail": 0.16,
                "cannon": 0.16,
                "scythe": 0.17,
                "axe": 0.18,
                "greatsword": 0.18
            }
            self.swing_duration = durations.get(self.weapon_type, 0.14)
            self.swing_total_duration = self.swing_duration
            self.swing_timer = self.swing_duration
            return True
        return False

    def trigger_basic_arcane_shot(self) -> bool:
        """
        Disparo básico a distancia para el Mago cuando no tiene arma melee.
        Costo: 0 MP. Permite atacar siempre y recargar maná con cada impacto.
        """
        if self.basic_shot_timer <= 0 and not self.is_dashing:
            self.basic_shot_timer = self.basic_shot_cooldown_max
            return True
        return False

    def take_damage(self, amount: float) -> bool:
        """
        Aplica daño al jugador considerando i-frames y reducción de daño.
        Retorna True si el jugador recibió daño efectivamente.
        """
        if self.invulnerable_timer > 0 or self.is_dashing:
            return False  # Invulnerable actualmente

        effective_damage = amount * (1.0 - self.damage_reduction)
        self.current_hp -= effective_damage
        self.invulnerable_timer = PLAYER_INVULNERABILITY_TIME
        self.hit_flash_timer = 0.09  # Efecto de impacto blanco brillante
        self.time_without_damage = 0.0  # Reiniciar temporizador de recuperación sin daño

        if self.current_hp < 0:
            self.current_hp = 0

        return True

    def heal(self, amount: float):
        """Restaura vida sin superar el límite máximo de HP."""
        self.current_hp = min(self.max_hp, self.current_hp + amount)

    def update(self, dt: float, arena_rect: pygame.Rect):
        """
        Actualiza posición física, temporizadores de cooldown y animación.
        dt: Delta Time en segundos para asegurar física independiente del framerate.
        """
        # Desplazamiento: Dash explosivo o movimiento regular
        if self.is_dashing:
            self.pos += self.dash_vector * PLAYER_DASH_SPEED * dt
            self.dash_timer -= dt

            # Generar sombras fantasma (afterimages) durante el dash
            self.afterimage_spawn_timer -= dt
            if self.afterimage_spawn_timer <= 0:
                self.afterimage_spawn_timer = 0.035
                self.afterimages.append({
                    "pos": pygame.math.Vector2(self.pos.x, self.pos.y),
                    "angle": self.facing_angle,
                    "alpha": 190.0
                })

            if self.dash_timer <= 0:
                self.is_dashing = False
        else:
            self.pos += self.velocity * dt

        # Actualizar sombras fantasma decrecientes
        alive_afterimages = []
        for img in self.afterimages:
            img["alpha"] -= dt * 700.0
            if img["alpha"] > 0:
                alive_afterimages.append(img)
        self.afterimages = alive_afterimages

        # Ciclo de animación de caminata (bamboleo y balanceo)
        if self.velocity.length_squared() > 0 and not self.is_dashing:
            self.walk_cycle += dt * 11.0
            self.bob_y = math.sin(self.walk_cycle) * 3.0
            self.tilt = math.cos(self.walk_cycle * 0.5) * 3.5
        else:
            self.bob_y = 0.0
            self.tilt = 0.0

        # Temporizador de destello por golpe
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt

        # Enfriamiento del Dash
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= dt

        # Enfriamiento de Hechizos Mágicos
        if self.magic_primary_cooldown > 0:
            self.magic_primary_cooldown -= dt
        if self.magic_secondary_cooldown > 0:
            self.magic_secondary_cooldown -= dt

        # Limitar dentro de los muros perimetrales de la arena
        min_x = arena_rect.left + self.radius + 32
        max_x = arena_rect.right - self.radius - 32
        min_y = arena_rect.top + self.radius + 32
        max_y = arena_rect.bottom - self.radius - 32

        self.pos.x = max(min_x, min(self.pos.x, max_x))
        self.pos.y = max(min_y, min(self.pos.y, max_y))

        # Actualizar temporizador de ataque
        if self.attack_timer > 0:
            self.attack_timer -= dt

        # Actualizar animación de swing
        if self.is_swinging:
            self.swing_timer -= dt
            if self.swing_timer <= 0:
                self.is_swinging = False

        # Actualizar i-frames
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt

        # Actualizar temporizador de disparo básico (Mago)
        if self.basic_shot_timer > 0:
            self.basic_shot_timer -= dt

        # Regeneración por paciencia: +10 HP tras 10 segundos sin recibir daño
        self.time_without_damage += dt
        if self.time_without_damage >= 10.0:
            self.time_without_damage = 0.0
            if self.current_hp < self.max_hp:
                self.heal(10.0)

        # Regeneración pasiva de vida si el rol lo otorga (ej. Paladín)
        if getattr(self, 'passive_regen', 0) > 0 and self.current_hp < self.max_hp:
            self.passive_regen_timer += dt
            if self.passive_regen_timer >= 2.0:
                self.passive_regen_timer = 0.0
                self.heal(self.passive_regen)

        # Regeneración pasiva de maná (Mago / Afinidad Arcana)
        if getattr(self, 'passive_mana_regen', 0) > 0 and self.current_mana < self.max_mana:
            # Si el maná es crítico (< 120), acelera a +35 MP/s para permitir combate dinámico
            regen_rate = self.passive_mana_regen if self.current_mana >= 120 else (self.passive_mana_regen + 15.0)
            self.restore_mana(regen_rate * dt)

        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y + self.bob_y)))

    def draw(self, surface: pygame.Surface):
        """Dibuja al jugador con sombra suave, estelas de dash, bamboleo y efectos de corte."""
        # 0. Sombra en el suelo para anclaje visual 2.5D
        shadow = AssetLoader.get_shadow_sprite(rx=18, ry=7)
        surface.blit(shadow, (int(self.pos.x - shadow.get_width() // 2), int(self.pos.y + 13 - shadow.get_height() // 2)))

        # 1. Dibujar estelas fantasma del dash
        for img in self.afterimages:
            ghost_surf = AssetLoader.get_player_sprite(img["angle"]).copy()
            ghost_surf.set_alpha(int(img["alpha"]))
            ghost_rect = ghost_surf.get_rect(center=(int(img["pos"].x), int(img["pos"].y)))
            surface.blit(ghost_surf, ghost_rect)

        draw_y = self.pos.y + self.bob_y
        current_angle = self.facing_angle + self.tilt

        # 2. Renderizado del héroe con Hit Flash
        if self.hit_flash_timer > 0:
            flash_surf = AssetLoader.get_player_sprite(current_angle).copy()
            flash_surf.fill((255, 255, 255, 220), special_flags=pygame.BLEND_RGBA_MULT)
            flash_rect = flash_surf.get_rect(center=(int(self.pos.x), int(draw_y)))
            surface.blit(flash_surf, flash_rect)
        elif self.invulnerable_timer > 0 and int(self.invulnerable_timer * 20) % 2 == 0:
            base_sprite = AssetLoader.get_player_sprite(current_angle).copy()
            base_sprite.set_alpha(120)
            base_rect = base_sprite.get_rect(center=(int(self.pos.x), int(draw_y)))
            surface.blit(base_sprite, base_rect)
        else:
            sprite = AssetLoader.get_player_sprite(current_angle)
            self.image = sprite
            rect = sprite.get_rect(center=(int(self.pos.x), int(draw_y)))
            surface.blit(sprite, rect)

        # 3. Dibujar Arma Medieval y Animación de Golpe según el Rol
        w_type = getattr(self, 'weapon_type', 'sword')
        weapon_surf = AssetLoader.get_weapon_sprite(w_type)

        # Configuración visual de arco y colores según el arma
        w_colors = {
            "sword": (230, 240, 255),
            "axe": (220, 45, 45),
            "mace": (255, 215, 70),
            "daggers": (46, 204, 113),
            "crossbow": (212, 160, 23),
            "scythe": (155, 89, 182),
            "staff": (52, 152, 219),
            "greatsword": (52, 152, 219),
            "flask": (46, 204, 113),
            "fists": (230, 126, 34),
            "cannon": (212, 160, 23),
            "totem": (26, 188, 156),
            "flail": (192, 57, 43)
        }
        w_color = w_colors.get(w_type, (230, 240, 255))

        w_radii = {
            "sword": 82,
            "axe": 96,
            "mace": 78,
            "daggers": 68,
            "crossbow": 65,
            "scythe": 105,
            "staff": 72,
            "greatsword": 100,
            "flask": 70,
            "fists": 62,
            "cannon": 65,
            "totem": 90,
            "flail": 95
        }
        slash_radius = w_radii.get(w_type, 82)

        w_angles = {
            "sword": 110,
            "axe": 135,
            "mace": 90,
            "daggers": 75,
            "crossbow": 20,
            "scythe": 145,
            "staff": 30,
            "greatsword": 130,
            "flask": 45,
            "fists": 70,
            "cannon": 25,
            "totem": 120,
            "flail": 360
        }
        slash_arc_deg = w_angles.get(w_type, 110)

        # Cálculo de la animación de swing
        if self.is_swinging:
            prog = 1.0 - max(0.0, min(1.0, self.swing_timer / max(0.001, self.swing_total_duration)))
            # Interpolación no lineal (rápida al inicio, desacelera al final)
            swing_curve = math.sin(prog * math.pi * 0.5)

            if w_type in ("crossbow", "cannon", "flask"):
                # Animación de retroceso (kickback) al disparar o arrojar
                recoil = math.sin(prog * math.pi) * 8.0
                dist = 22.0 - recoil
                w_x = self.pos.x + self.aim_vector.x * dist
                w_y = draw_y + self.aim_vector.y * dist
                rot_w = pygame.transform.rotate(weapon_surf, -self.facing_angle)
                w_rect = rot_w.get_rect(center=(int(w_x), int(w_y)))
                surface.blit(rot_w, w_rect)

            elif w_type in ("daggers", "fists"):
                # Doble estocada / ráfaga de golpes veloz
                thrust = math.sin(prog * math.pi) * 14.0
                dist = 20.0 + thrust
                w_x = self.pos.x + self.aim_vector.x * dist
                w_y = draw_y + self.aim_vector.y * dist
                rot_w = pygame.transform.rotate(weapon_surf, -self.facing_angle)
                w_rect = rot_w.get_rect(center=(int(w_x), int(w_y)))
                surface.blit(rot_w, w_rect)

                # Efecto de tajo cruzado o impacto
                slash_surf = AssetLoader.get_slash_arc_sprite(radius=slash_radius,
                                                              angle_span=slash_arc_deg,
                                                              color=w_color)
                rot_slash = pygame.transform.rotate(slash_surf, -self.facing_angle)
                slash_rect = rot_slash.get_rect(center=(int(self.pos.x), int(draw_y)))
                surface.blit(rot_slash, slash_rect)

            elif w_type == "flail":
                # Mangual giratorio continuo de 360 grados
                rot_angle = self.facing_angle + (prog * 360.0)
                rad = math.radians(rot_angle)
                w_dist = 28.0
                w_x = self.pos.x + math.cos(rad) * w_dist
                w_y = draw_y + math.sin(rad) * w_dist
                rot_w = pygame.transform.rotate(weapon_surf, -rot_angle)
                w_rect = rot_w.get_rect(center=(int(w_x), int(w_y)))
                surface.blit(rot_w, w_rect)

                # Estela circular roja
                pygame.draw.circle(surface, (192, 57, 43), (int(self.pos.x), int(draw_y)), int(slash_radius), 2)

            else:
                # Animación de barrido oscilante en arco real de la hoja
                half_arc = slash_arc_deg / 2.0
                dyn_angle_offset = -half_arc + (slash_arc_deg * swing_curve)
                weapon_render_angle = self.facing_angle + dyn_angle_offset

                # Posición física del arma orbitando la mano
                rad = math.radians(weapon_render_angle)
                w_dist = 25.0
                w_x = self.pos.x + math.cos(rad) * w_dist
                w_y = draw_y + math.sin(rad) * w_dist

                rot_w = pygame.transform.rotate(weapon_surf, -weapon_render_angle)
                w_rect = rot_w.get_rect(center=(int(w_x), int(w_y)))
                surface.blit(rot_w, w_rect)

                # Dibujar arco de barrido brillante personalizado
                slash_surf = AssetLoader.get_slash_arc_sprite(radius=slash_radius,
                                                              angle_span=slash_arc_deg,
                                                              color=w_color)
                rot_slash = pygame.transform.rotate(slash_surf, -self.facing_angle)
                slash_rect = rot_slash.get_rect(center=(int(self.pos.x), int(draw_y)))
                surface.blit(rot_slash, slash_rect)

                # Si es maza y está en el punto de impacto, dibujar destello en suelo
                if w_type == "mace" and prog > 0.6:
                    tip_x = self.pos.x + self.aim_vector.x * 60
                    tip_y = draw_y + self.aim_vector.y * 60
                    pygame.draw.circle(surface, (255, 230, 100), (int(tip_x), int(tip_y)), 10, 2)
                    pygame.draw.circle(surface, COLOR_WHITE, (int(tip_x), int(tip_y)), 4)
        else:
            # Posición de reposo / guardia del arma
            if w_type == "staff":
                # Bastón en reposo a 45 grados listo para canalizar
                w_dist = 22.0
                w_x = self.pos.x + self.aim_vector.x * w_dist
                w_y = draw_y + self.aim_vector.y * w_dist
                rot_w = pygame.transform.rotate(weapon_surf, -self.facing_angle)
                w_rect = rot_w.get_rect(center=(int(w_x), int(w_y)))
                surface.blit(rot_w, w_rect)
            elif getattr(self, 'has_melee_weapon', True):
                w_dist = 22.0
                guard_angle = self.facing_angle + 20.0  # Ligera inclinación marcial
                rad = math.radians(guard_angle)
                w_x = self.pos.x + math.cos(rad) * w_dist
                w_y = draw_y + math.sin(rad) * w_dist
                rot_w = pygame.transform.rotate(weapon_surf, -guard_angle)
                w_rect = rot_w.get_rect(center=(int(w_x), int(w_y)))
                surface.blit(rot_w, w_rect)
