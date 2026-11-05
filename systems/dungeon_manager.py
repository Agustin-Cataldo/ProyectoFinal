"""
================================================================================
MÓDULO: systems/dungeon_manager.py
RESPONSABILIDAD: Gestión del flujo de los 50 niveles, las 5 mazmorras y temas elementales.
CONCEPTO ACADÉMICO: Generación Procedural de Progresión y Control de Ciclo de Vida.
================================================================================
Coordina el orden aleatorio de elementos al reiniciar, la generación de oleadas
de monstruos medievales, la aparición de espíritus élite y el combate contra el
Jefe Elemental en el nivel 10 de cada una de las 5 mazmorras.
"""

import math
import random
import pygame
from settings import (
    TOTAL_DUNGEONS, LEVELS_PER_DUNGEON, TOTAL_LEVELS, BOSS_LEVEL_STEP,
    DUNGEON_ELEMENTS, ELITE_SPAWN_CHANCE, CARD_OFFER_INTERVAL,
    SCREEN_WIDTH, SCREEN_HEIGHT, ELEMENT_COLORS
)
from entities.enemy import (
    SteamMiner, SteamPistonCharger, SteamSharpshooter,
    SteamDrone, DemolitionTank, ClockworkBombardier,
    AlchemicalPlagueDoctor, BrassShieldGuardian,
    ArcaneCultist, CursedReaper, create_random_spirit
)
from entities.boss import ElementalBoss
from utils.asset_loader import AssetLoader


class DungeonManager:
    """Controlador general del mundo y avance de mazmorras."""

    def __init__(self):
        # Mapeo de elementos aleatorios para las 5 mazmorras
        self.dungeon_elements = []
        self.current_dungeon_index = 1       # 1 a 5
        self.current_level_in_dungeon = 1    # 1 a 10
        self.current_global_level = 1        # 1 a 50

        # Grupos de entidades activas en el nivel actual
        self.enemies = []
        self.active_boss = None

        # Estado del nivel actual
        self.level_cleared = False
        self.game_won = False
        self.portal_active = False
        self.portal_rect = pygame.Rect(SCREEN_WIDTH // 2 - 30, 70, 60, 60)

        # Sistema de efectos visuales y ambientales
        self.anim_time = 0.0
        self.ambient_particles = []
        wall_thick = 36
        w, h = SCREEN_WIDTH, SCREEN_HEIGHT
        self.torch_positions = [
            (w // 4, wall_thick - 4), (w // 2, wall_thick - 4), (w * 3 // 4, wall_thick - 4),
            (w // 4, h - wall_thick + 4), (w // 2, h - wall_thick + 4), (w * 3 // 4, h - wall_thick + 4),
            (wall_thick - 4, h // 3), (wall_thick - 4, h * 2 // 3),
            (w - wall_thick + 4, h // 3), (w - wall_thick + 4, h * 2 // 3)
        ]

        # Inicialización de la partida aleatoria
        self.reset_run()

    @property
    def current_element(self) -> str:
        """Retorna el elemento activo de la mazmorra actual."""
        idx = self.current_dungeon_index - 1
        if 0 <= idx < len(self.dungeon_elements):
            return self.dungeon_elements[idx]
        return "Fuego"

    def reset_run(self):
        """
        Reinicia la partida completa (por muerte o inicio nuevo):
        Aleatoriza 5 elementos únicos extraídos del pool de 10 elementos.
        """
        self.dungeon_elements = random.sample(DUNGEON_ELEMENTS, TOTAL_DUNGEONS)
        self.current_dungeon_index = 1
        self.current_level_in_dungeon = 1
        self.current_global_level = 1
        self.game_won = False
        self.load_current_level()

    def load_current_level(self):
        """
        Instancia las oleadas de enemigos según el nivel actual:
        - Si es el nivel 10 de la mazmorra: Spawnea al Jefe Elemental.
        - Si es un nivel normal (1 a 9): Spawnea monstruos comunes y espíritus malignos élite.
        """
        self.enemies.clear()
        self.active_boss = None
        self.level_cleared = False
        self.portal_active = False

        element = self.current_element

        # Multiplicador matemático de escalado de dificultad Roguelike (+4.5% de vida y daño por nivel)
        difficulty_mult = 1.0 + (self.current_global_level - 1) * 0.045

        if self.current_level_in_dungeon == BOSS_LEVEL_STEP:
            # NIVEL 10: Combate obligatorio contra Jefe Elemental
            boss_x = SCREEN_WIDTH // 2
            boss_y = SCREEN_HEIGHT // 3
            self.active_boss = ElementalBoss(boss_x, boss_y, element, self.current_dungeon_index)
            # Escalar vida y daño del jefe según el nivel global y mazmorra
            self.active_boss.max_hp = round(self.active_boss.max_hp * (1.0 + (self.current_dungeon_index - 1) * 0.22), 1)
            self.active_boss.current_hp = self.active_boss.max_hp
            self.active_boss.damage = round(self.active_boss.damage * (1.0 + (self.current_dungeon_index - 1) * 0.18), 1)
        else:
            # NIVELES 1 a 9: Oleadas estilo Roguelike pesadilla (entre 9 y 22 enemigos por sala)
            enemy_count = min(22, 9 + (self.current_global_level // 2))

            # Escalado progresivo de probabilidad de aparición de espíritus élite (hasta 50%)
            current_elite_chance = min(0.50, ELITE_SPAWN_CHANCE + (self.current_global_level * 0.005))

            for _ in range(enemy_count):
                # Generar posición en los bordes de la arena para que no aparezcan encima del jugador
                side = random.choice(["top", "bottom", "left", "right"])
                margin = 70
                if side == "top":
                    spawn_x = random.randint(margin, SCREEN_WIDTH - margin)
                    spawn_y = margin
                elif side == "bottom":
                    spawn_x = random.randint(margin, SCREEN_WIDTH - margin)
                    spawn_y = SCREEN_HEIGHT - margin
                elif side == "left":
                    spawn_x = margin
                    spawn_y = random.randint(margin, SCREEN_HEIGHT - margin)
                else:
                    spawn_x = SCREEN_WIDTH - margin
                    spawn_y = random.randint(margin, SCREEN_HEIGHT - margin)

                # Probabilidad de generar Espíritu Maligno (Élite de 5 variantes)
                if random.random() < current_elite_chance:
                    spirit = create_random_spirit(spawn_x, spawn_y, difficulty_mult)
                    self.enemies.append(spirit)
                else:
                    # Bestiario diversificado: 10 variantes de enemigos comunes y tácticos
                    roll = random.random()
                    if roll < 0.18:
                        new_enemy = SteamMiner(spawn_x, spawn_y)
                    elif roll < 0.30:
                        new_enemy = SteamPistonCharger(spawn_x, spawn_y)
                    elif roll < 0.40:
                        new_enemy = SteamSharpshooter(spawn_x, spawn_y)
                    elif roll < 0.50:
                        new_enemy = SteamDrone(spawn_x, spawn_y)
                    elif roll < 0.58:
                        new_enemy = DemolitionTank(spawn_x, spawn_y)
                    elif roll < 0.68:
                        new_enemy = ClockworkBombardier(spawn_x, spawn_y)
                    elif roll < 0.76:
                        new_enemy = AlchemicalPlagueDoctor(spawn_x, spawn_y)
                    elif roll < 0.84:
                        new_enemy = BrassShieldGuardian(spawn_x, spawn_y)
                    elif roll < 0.92:
                        new_enemy = ArcaneCultist(spawn_x, spawn_y)
                    else:
                        new_enemy = CursedReaper(spawn_x, spawn_y)

                    # Aplicar escalado progresivo de dificultad
                    new_enemy.apply_difficulty_scaling(difficulty_mult)
                    self.enemies.append(new_enemy)

    def update(self, dt: float, player, combat_system) -> tuple:
        """
        Actualiza el estado de la mazmorra y partículas ambientales.
        Retorna (should_offer_cards, is_victory)
        """
        should_offer_cards = False
        self.anim_time += dt

        # Actualizar partículas atmosféricas temáticas de la mazmorra
        if len(self.ambient_particles) < 28 and random.random() < 0.35:
            elem_col = ELEMENT_COLORS.get(self.current_element, (200, 214, 229))
            self.ambient_particles.append({
                "x": random.uniform(50, SCREEN_WIDTH - 50),
                "y": random.uniform(50, SCREEN_HEIGHT - 50),
                "vx": random.uniform(-18, 18),
                "vy": random.uniform(-25, -8),
                "life": random.uniform(2.5, 4.5),
                "max_life": 4.5,
                "size": random.uniform(1.5, 3.2),
                "color": elem_col
            })

        alive_p = []
        for p in self.ambient_particles:
            p["life"] -= dt
            p["x"] += p["vx"] * dt + math.sin(p["life"] * 2.0) * 0.4
            p["y"] += p["vy"] * dt
            if p["life"] > 0:
                alive_p.append(p)
        self.ambient_particles = alive_p

        # Si hay jefe activo
        if self.active_boss:
            self.active_boss.update(dt, player, combat_system)
            if not self.active_boss.is_alive and not self.level_cleared:
                self.level_cleared = True
                self.portal_active = True
                combat_system.emit_impact_particles(self.active_boss.pos.x, self.active_boss.pos.y,
                                                    count=50, color=(255, 215, 0))
        else:
            # Actualizar enemigos normales
            for enemy in self.enemies:
                enemy.update(dt, player, self.enemies, combat_system)

            # Filtrar enemigos vivos
            self.enemies = [e for e in self.enemies if e.is_alive]

            # Si todos los enemigos fueron eliminados
            if len(self.enemies) == 0 and not self.level_cleared:
                self.level_cleared = True
                self.portal_active = True

        # Comprobar si el jugador ingresa al portal de transición
        if self.portal_active:
            if self.portal_rect.collidepoint(player.pos.x, player.pos.y):
                # Avanzar al siguiente nivel
                should_offer_cards = self.advance_level(player)

        return should_offer_cards, self.game_won

    def advance_level(self, player) -> bool:
        """
        Avanza al siguiente nivel del juego:
        Verifica ofertas de cartas cada 3 niveles y condición de victoria en el nivel 50.
        Retorna True si corresponde abrir la selección de cartas.
        """
        # Reposicionar al jugador al inicio de la sala
        player.pos.x = SCREEN_WIDTH // 2
        player.pos.y = SCREEN_HEIGHT - 120

        # Evaluar oferta de cartas antes de incrementar
        level_just_finished = self.current_global_level
        should_offer_cards = (level_just_finished % CARD_OFFER_INTERVAL == 0)

        # Condición de Victoria Total (Nivel 50 completado)
        if self.current_global_level >= TOTAL_LEVELS:
            self.game_won = True
            return False

        # Incrementar nivel
        self.current_global_level += 1
        self.current_level_in_dungeon += 1

        # Si superó el nivel 10, pasa a la siguiente mazmorra
        if self.current_level_in_dungeon > LEVELS_PER_DUNGEON:
            self.current_dungeon_index += 1
            self.current_level_in_dungeon = 1

        self.load_current_level()
        return should_offer_cards

    def draw_arena(self, surface: pygame.Surface):
        """Dibuja el suelo, muros, antorchas parpadeantes, atmósfera elemental y portal."""
        arena_surf = AssetLoader.get_arena_surface(SCREEN_WIDTH, SCREEN_HEIGHT, self.current_element)
        surface.blit(arena_surf, (0, 0))

        # 1. Halos de luz cálida de las antorchas en los muros con parpadeo dinámico
        for idx, (tx, ty) in enumerate(self.torch_positions):
            flicker = self.anim_time * 7.0 + idx * 1.3
            glow_surf = AssetLoader.get_torch_glow_sprite(radius=62, pulse_phase=flicker)
            surface.blit(glow_surf, (tx - 62, ty - 62))

        # 2. Partículas ambientales flotantes según el elemento de la mazmorra
        for p in self.ambient_particles:
            alpha = int(140 * (p["life"] / p["max_life"]))
            if alpha > 0:
                p_surf = pygame.Surface((int(p["size"] * 2 + 2), int(p["size"] * 2 + 2)), pygame.SRCALPHA)
                pygame.draw.circle(p_surf, (*p["color"][:3], alpha), (int(p["size"] + 1), int(p["size"] + 1)), int(p["size"]))
                surface.blit(p_surf, (int(p["x"]), int(p["y"])))

        # 3. Dibujar portal de vapor al limpiar la sala con vórtice rotatorio
        if self.portal_active:
            cx, cy = self.portal_rect.centerx, self.portal_rect.centery
            rot = self.anim_time * 4.0
            elem_col = ELEMENT_COLORS.get(self.current_element, (0, 206, 209))
            portal_surf = pygame.Surface((110, 110), pygame.SRCALPHA)

            # Halo resplandeciente pulsante
            pulse_rad = int(34 + 3 * math.sin(self.anim_time * 6.0))
            pygame.draw.circle(portal_surf, (*elem_col[:3], 90), (55, 55), pulse_rad + 6)
            pygame.draw.circle(portal_surf, (*elem_col[:3], 180), (55, 55), pulse_rad, 3)
            pygame.draw.circle(portal_surf, (255, 255, 255, 230), (55, 55), pulse_rad - 12)

            # Runas orbitales giratorias
            for k in range(4):
                ang = rot + k * (math.pi / 2)
                rx = 55 + int(math.cos(ang) * (pulse_rad + 8))
                ry = 55 + int(math.sin(ang) * (pulse_rad + 8))
                pygame.draw.circle(portal_surf, (241, 196, 15, 220), (rx, ry), 3)

            surface.blit(portal_surf, (cx - 55, cy - 55))

    def draw_entities(self, surface: pygame.Surface):
        """Dibuja todos los enemigos o al jefe elemental."""
        if self.active_boss:
            self.active_boss.draw(surface)
        else:
            for enemy in self.enemies:
                enemy.draw(surface)
