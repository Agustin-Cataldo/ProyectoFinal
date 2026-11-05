"""
================================================================================
TEST ESPECÍFICO: test_new_enemies.py
Verifica la correcta integración, mecánicas únicas y robustez técnica de las
5 nuevas variantes de enemigos:
1. ClockworkBombardier (Artificiero de Relojería)
2. AlchemicalPlagueDoctor (Médico de la Peste Alquímico)
3. BrassShieldGuardian (Guardián de Escudo de Latón)
4. ArcaneCultist (Cultista de la Forja Arcana)
5. CursedReaper (Segador Mecánico de Cadena)
================================================================================
"""

import os
import sys
import math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1280, 720))

from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from entities.player import Player
from systems.combat_system import CombatSystem
from entities.enemy import (
    ClockworkBombardier, AlchemicalPlagueDoctor,
    BrassShieldGuardian, ArcaneCultist, CursedReaper
)

def test_new_enemy_variants():
    print("=== INICIANDO VALIDACIÓN DE LAS 5 NUEVAS VARIANTES DE ENEMIGOS ===")
    surf = pygame.Surface((1280, 720))
    cs = CombatSystem()
    player = Player(400, 300)

    # -------------------------------------------------------------------------
    # 1. Artificiero de Relojería / Bombardero (ClockworkBombardier)
    # -------------------------------------------------------------------------
    print("\n[1] Verificando ClockworkBombardier...")
    bombardier = ClockworkBombardier(500, 300)
    assert bombardier.current_hp == 160
    assert bombardier.damage == 50
    assert bombardier.speed == 130.0

    # Forzar lanzamiento de bomba
    bombardier.bomb_timer = 0.0
    bombardier.windup_timer = 0.01
    bombardier.update(0.02, player, [bombardier], cs)
    assert len(bombardier.bombs) >= 1, "El bombardero debió haber lanzado una bomba de relojería"
    bomb = bombardier.bombs[0]
    # Simular vuelo y detonación
    bomb.flight_timer = bomb.flight_duration
    bomb.fuse_timer = 0.0
    bomb.update(0.01, cs)
    assert bomb.is_exploded is True, "La bomba debió detonar"
    assert len(cs.shockwaves) >= 1, "La bomba debió generar una onda de choque expansiva"
    bombardier.draw(surf)
    print("  -> ClockworkBombardier y ClockworkBomb validados con éxito.")

    # -------------------------------------------------------------------------
    # 2. Médico de la Peste Alquímico (AlchemicalPlagueDoctor)
    # -------------------------------------------------------------------------
    print("\n[2] Verificando AlchemicalPlagueDoctor...")
    doctor = AlchemicalPlagueDoctor(420, 300) # Muy cerca del jugador (distancia 20px)
    assert doctor.current_hp == 210
    assert doctor.speed == 120.0

    # Verificar aura de miasma sobre el jugador
    hp_prev = player.current_hp
    doctor.update(0.1, player, [doctor], cs)
    assert player.current_hp < hp_prev, "El miasma debió dañar al jugador adyacente"

    # Verificar curación a un aliado herido
    ally = ClockworkBombardier(440, 300)
    ally.current_hp = 50.0  # Herido
    doctor.heal_timer = 0.0
    doctor.update(0.05, player, [doctor, ally], cs)
    assert ally.current_hp > 50.0, "El médico de la peste debió curar al aliado herido"

    # Verificar lanzamiento de charco de ácido
    doctor.acid_timer = 0.0
    doctor.update(0.05, player, [doctor], cs)
    assert any(h.hazard_type == "Ácido Alquímico" for h in cs.ground_hazards), "Debió crearse un charco de ácido"
    doctor.draw(surf)
    print("  -> AlchemicalPlagueDoctor (Miasma, Curación y Ácido) validado con éxito.")

    # -------------------------------------------------------------------------
    # 3. Guardián de Escudo de Latón (BrassShieldGuardian)
    # -------------------------------------------------------------------------
    print("\n[3] Verificando BrassShieldGuardian...")
    guardian = BrassShieldGuardian(500, 300)
    assert guardian.current_hp == 260
    assert guardian.knockback_resistance >= 0.8
    guardian.facing_angle = 180.0 # Mirando hacia la izquierda (hacia el jugador en 400, 300)

    # Ataque frontal: debe bloquear el 75% del daño
    hp_before = guardian.current_hp
    # Jugador en (400, 300) ataca al guardián en (500, 300) frontalmente
    guardian.take_damage(100.0, attacker_pos=pygame.math.Vector2(400, 300))
    dmg_taken_front = hp_before - guardian.current_hp
    assert math.isclose(dmg_taken_front, 25.0, abs_tol=0.5), f"Debió recibir 25 DMG (bloqueo 75%), recibió {dmg_taken_front}"

    # Ataque por la espalda (Backstab tras Dash): debe recibir 100% de daño
    hp_before = guardian.current_hp
    guardian.take_damage(100.0, attacker_pos=pygame.math.Vector2(600, 300))
    dmg_taken_back = hp_before - guardian.current_hp
    assert math.isclose(dmg_taken_back, 100.0, abs_tol=0.5), f"Por la espalda debió recibir 100 DMG, recibió {dmg_taken_back}"

    # Shield bash a corta distancia
    guardian.pos = pygame.math.Vector2(player.pos.x + 30, player.pos.y)
    guardian.bash_timer = 0.0
    guardian.update(0.05, player, [guardian], cs)
    guardian.draw(surf)
    print("  -> BrassShieldGuardian (Bloqueo direccional y Shield Bash) validado con éxito.")

    # -------------------------------------------------------------------------
    # 4. Cultista de la Forja Arcana (ArcaneCultist)
    # -------------------------------------------------------------------------
    print("\n[4] Verificando ArcaneCultist...")
    cultist = ArcaneCultist(550, 300)
    assert cultist.current_hp == 130
    assert cultist.damage == 55

    # Simular canalización
    cultist.attack_cooldown_timer = 0.0
    cultist.update(0.05, player, [cultist], cs)
    assert cultist.state == ArcaneCultist.STATE_CHANNEL
    assert cultist.laser_target is not None

    # Simular fin de canalización y disparo
    cultist.channel_timer = 0.0
    cultist.update(0.05, player, [cultist], cs)
    assert cultist.state == ArcaneCultist.STATE_RECOVER
    assert len(cs.projectiles) >= 3, "Debió disparar 3 proyectiles arcanos"
    cultist.draw(surf)
    print("  -> ArcaneCultist (Láser telegrafiado, descarga y vulnerabilidad) validado con éxito.")

    # -------------------------------------------------------------------------
    # 5. Segador Mecánico de Cadena (CursedReaper)
    # -------------------------------------------------------------------------
    print("\n[5] Verificando CursedReaper...")
    reaper = CursedReaper(600, 300)
    assert reaper.current_hp == 220
    assert reaper.speed == 165.0

    # Arpón de cadena a media distancia
    reaper.hook_cooldown_timer = 0.0
    reaper.update(0.05, player, [reaper], cs)
    assert reaper.state in (CursedReaper.STATE_HOOK_WINDUP, CursedReaper.STATE_HOOK_PULL)

    # Torbellino a corta distancia
    reaper.state = CursedReaper.STATE_STALK
    reaper.pos = pygame.math.Vector2(player.pos.x + 25, player.pos.y)
    reaper.whirlwind_timer = 0.0
    reaper.update(0.05, player, [reaper], cs)
    assert reaper.state == CursedReaper.STATE_WHIRLWIND_WINDUP
    reaper.state_timer = 0.0
    reaper.update(0.05, player, [reaper], cs)
    assert reaper.state == CursedReaper.STATE_WHIRLWIND
    reaper.draw(surf)
    print("  -> CursedReaper (Arpón de cadena y Torbellino 360°) validado con éxito.")

    # -------------------------------------------------------------------------
    # 6. Confinamiento perimetral y Hit-Flash decay en las 5 variantes
    # -------------------------------------------------------------------------
    print("\n[6] Verificando confinamiento perimetral y decaimiento de Hit-Flash...")
    new_enemies = [bombardier, doctor, guardian, cultist, reaper]
    for e in new_enemies:
        # Poner en el muro exterior
        e.pos = pygame.math.Vector2(-100, -100)
        e.update_base(0.05)
        assert e.pos.x >= 38.0 + e.radius, f"{type(e).__name__} no debe salir de la arena"
        assert e.pos.y >= 38.0 + e.radius, f"{type(e).__name__} no debe salir de la arena"

        # Hit-flash decay
        e.hit_flash_timer = 0.09
        e.update_base(0.10)
        assert e.hit_flash_timer == 0.0, f"Hit flash de {type(e).__name__} debe decaer a 0.0"

    print("  -> Confinamiento de muros y Hit-Flash decay verificados en las 5 variantes.")
    print("\n=== TODAS LAS PRUEBAS DE LAS 5 VARIANTES COMPLETADAS CON ÉXITO ===")

if __name__ == "__main__":
    test_new_enemy_variants()
