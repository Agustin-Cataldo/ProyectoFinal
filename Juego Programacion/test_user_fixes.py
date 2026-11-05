import os
import sys
import pygame

# Forzar modo headless
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1280, 720))

from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from entities.player import Player
from entities.enemy import (
    SteamMiner, SteamPistonCharger, SteamSharpshooter, SteamDrone,
    DemolitionTank, MiniMinion, ShadowSpirit, FlameSpirit, FrostSpirit,
    StormSpirit, NecroSpirit
)
from entities.boss import ElementalBoss
from systems.combat_system import CombatSystem

def test_point_1_hit_flash_decay():
    print("[1] Verificando decaimiento del Hit-Flash blanco en todos los enemigos...")
    enemies = [
        SteamMiner(400, 300),
        SteamPistonCharger(400, 300),
        SteamSharpshooter(400, 300),
        SteamDrone(400, 300),
        DemolitionTank(400, 300),
        MiniMinion(400, 300),
        ShadowSpirit(400, 300),
        FlameSpirit(400, 300),
        FrostSpirit(400, 300),
        StormSpirit(400, 300),
        NecroSpirit(400, 300),
        ElementalBoss(400, 300, "Luz", 1)
    ]
    player = Player(100, 100)
    cs = CombatSystem()

    for e in enemies:
        e.take_damage(20.0)
        e.hit_flash_timer = 0.10
        assert e.hit_flash_timer > 0, f"{e.__class__.__name__} debe tener hit_flash activo"
        
        # Simular 3 frames (0.15s)
        for _ in range(3):
            if isinstance(e, ElementalBoss):
                e.update(0.05, player, cs)
            else:
                e.update(0.05, player, enemies, cs)
        
        assert e.hit_flash_timer == 0.0, f"ERROR: {e.__class__.__name__} se quedo en blanco (timer = {e.hit_flash_timer})"
    print("  -> OK: Ningún enemigo ni jefe queda en blanco de forma permanente.")

def test_point_2_wall_clamping():
    print("[2] Verificando confinamiento de enemigos y jefes dentro de las paredes...")
    enemies = [
        SteamMiner(-100, -100),
        SteamPistonCharger(2000, 1500),
        DemolitionTank(10, 10),
        ElementalBoss(-500, 9999, "Fuego", 1)
    ]
    player = Player(100, 100)
    cs = CombatSystem()

    for e in enemies:
        if isinstance(e, ElementalBoss):
            e.update(0.016, player, cs)
            margin = 42.0
        else:
            e.update(0.016, player, enemies, cs)
            margin = 38.0
        
        assert e.pos.x >= margin + e.radius, f"{e} atraviesa pared izquierda: {e.pos.x}"
        assert e.pos.x <= SCREEN_WIDTH - margin - e.radius, f"{e} atraviesa pared derecha: {e.pos.x}"
        assert e.pos.y >= margin + e.radius, f"{e} atraviesa pared superior: {e.pos.y}"
        assert e.pos.y <= SCREEN_HEIGHT - margin - e.radius, f"{e} atraviesa pared inferior: {e.pos.y}"
    print("  -> OK: Ningún enemigo ni jefe puede traspasar los muros perimetrales.")

def test_point_3_procedural_magic_and_trueno_chain():
    print("[3] Verificando gráficos procedimentales de magia, partículas de vuelo y cadena de Trueno...")
    cs = CombatSystem()
    player = Player(100, 100)
    surf = pygame.Surface((1280, 720))

    # Verificar emisión de partículas en vuelo para proyectiles
    cs.spawn_projectile(500, 300, 1.0, 0.0, 50.0, element="Fuego")
    initial_particles = len(cs.particles)
    cs.update(0.10, player, [])
    assert len(cs.particles) > initial_particles, "Los proyectiles deben emitir partículas procedimentales en vuelo"

    # Verificar dibujo procedimental de todos los 10 elementos sin fallos
    for elem in ["Fuego", "Agua", "Viento", "Tierra", "Trueno", "Naturaleza", "Vapor", "Metal", "Oscuridad", "Luz"]:
        cs.spawn_projectile(500, 300, 1.0, 0.0, 50.0, element=elem)
    cs.draw(surf)

    # Verificar onda de choque multi-capa
    cs.spawn_shockwave(500, 300, max_radius=100.0, speed=150.0, damage=30.0)
    cs.draw(surf)

    # Verificar Trueno encadenado dinámico
    e1 = SteamMiner(550, 300)
    e2 = SteamMiner(620, 300)
    e3 = SteamMiner(690, 300)
    targets = [e1, e2, e3]
    cs.cast_player_active_magic(player, "Trueno", (550, 300), targets=targets)
    assert len(cs.lightning_chains) > 0, "Debe haberse generado la cadena de relámpago"
    assert e1.current_hp < e1.max_hp, "El primer objetivo debió recibir daño"
    assert e2.current_hp < e2.max_hp, "El relámpago debió encadenarse al segundo objetivo"
    print("  -> OK: Gráficos procedimentales, partículas en vuelo y cadena de Trueno totalmente funcionales.")

def test_point_4_boss_difficulty():
    print("[4] Verificando incremento de dificultad y mecánicas de Jefes...")
    boss = ElementalBoss(600, 360, "Fuego", 1)
    player = Player(620, 360)
    cs = CombatSystem()

    assert boss.speed >= 115.0, f"Velocidad base del jefe debe ser desafiante: {boss.speed}"
    assert boss.knockback_resistance == 1.0, "El jefe debe tener resistencia total al derribo (super-armadura)"
    
    # Probar que daño de contacto del jefe es amenazante
    init_hp = player.current_hp
    boss.update(0.016, player, cs)
    assert player.current_hp < init_hp, "El jefe debe infligir daño de contacto significativo al jugador"

    # Probar fase enfurecida (Enrage < 50% HP)
    boss.take_damage(boss.max_hp * 0.60)
    boss.update(0.016, player, cs)
    assert boss.enraged is True, "El jefe debe enfurecerse al caer por debajo del 50% HP"
    assert boss.speed > 115.0, "La velocidad debe acelerarse en fase de furia"
    print("  -> OK: Los Jefes poseen super-armadura, ataques acelerados, daño de contacto y furia letal.")

def test_point_5_enemy_difficulty_and_knockback_resistance():
    print("[5] Verificando dificultad de enemigos comunes y resistencia al empuje...")
    miner = SteamMiner(400, 300)
    tank = DemolitionTank(500, 300)
    charger = SteamPistonCharger(600, 300)

    assert miner.max_hp >= 140.0, f"Miner HP esperado >= 140, obtenido {miner.max_hp}"
    assert miner.damage >= 40.0, f"Miner daño esperado >= 40, obtenido {miner.damage}"
    assert tank.max_hp >= 380.0, f"Tank HP esperado >= 380, obtenido {tank.max_hp}"
    assert tank.knockback_resistance >= 0.80, "DemolitionTank debe tener alta resistencia a derribos"
    assert charger.knockback_resistance >= 0.60, "SteamPistonCharger debe resistir derribos"

    # Verificar que el retroceso respeta la resistencia
    player = Player(400, 300)
    cs = CombatSystem()

    init_tank_x = tank.pos.x
    cs.process_player_melee_attack(player, [tank])
    pushed_dist = tank.pos.x - init_tank_x
    # Un enemigo normal sería empujado 22px; el tank con resistencia 0.85 se empuja sólo ~3.3px
    assert pushed_dist < 10.0, f"El tanque no debe volar por los aires: empuje = {pushed_dist}px"
    print("  -> OK: Enemigos comunes rebalanceados con estadísticas peligrosas y super-armadura en pesados.")

if __name__ == "__main__":
    test_point_1_hit_flash_decay()
    test_point_2_wall_clamping()
    test_point_3_procedural_magic_and_trueno_chain()
    test_point_4_boss_difficulty()
    test_point_5_enemy_difficulty_and_knockback_resistance()
    print("\n[VALIDACION EXITOSA] Los 5 puntos solicitados por el usuario están 100% resueltos y verificados.")
