"""
================================================================================
MÓDULO: entities/weapons.py
RESPONSABILIDAD: Catálogo y definición física de las Armas Medievales por Rol.
CONCEPTO ACADÉMICO: Patrón Flyweight / Data Transfer Object para armas y estilos de combate.
================================================================================
Define los arquetipos de armas medievales para cada clase:
- Espada de Acero Templado (Aventurero)
- Gran Hacha Bárbara (Berserker)
- Maza Sagrada de Guerra (Paladín)
- Dagas Gemelas de Asesino (Pícaro)
- Ballesta Pesada de Repetición (Cazador)
- Guadaña Espectral de Almas (Nigromante)
- Bastón Rúnico de Éter (Mago)
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class WeaponConfig:
    """Configuración física, matemática y visual de un arma medieval."""
    weapon_id: str
    name: str
    weapon_type: str            # 'sword', 'axe', 'mace', 'daggers', 'crossbow', 'scythe', 'staff'
    damage_bonus: float         # Daño suplementario al daño base
    attack_range: float         # Alcance en píxeles
    attack_arc_deg: float       # Amplitud angular del barrido
    cooldown: float             # Tiempo de recarga entre ataques (segundos)
    swing_duration: float       # Duración de la animación de swing
    is_ranged: bool             # True si dispara proyectil en lugar de corte físico
    projectile_speed: float     # Velocidad del proyectil si es a distancia
    slash_color: Tuple[int, int, int]      # Color de la estela / efecto de corte
    hit_particles_color: Tuple[int, int, int]
    tagline: str


# Catálogo oficial de Armas Medievales
MEDIEVAL_WEAPONS = {
    # 1. AVENTURERO (Espada Medieval)
    "sword": WeaponConfig(
        weapon_id="sword",
        name="Espada de Acero Templado",
        weapon_type="sword",
        damage_bonus=20.0,
        attack_range=82.0,
        attack_arc_deg=110.0,
        cooldown=0.32,
        swing_duration=0.14,
        is_ranged=False,
        projectile_speed=0.0,
        slash_color=(230, 240, 255),
        hit_particles_color=(212, 160, 23),
        tagline="Tajo equilibrado y fluido con acero de alta calidad."
    ),

    # 2. BERSERKER (Gran Hacha Bárbara)
    "axe": WeaponConfig(
        weapon_id="axe",
        name="Gran Hacha Bárbara",
        weapon_type="axe",
        damage_bonus=30.0,
        attack_range=95.0,
        attack_arc_deg=135.0,
        cooldown=0.42,
        swing_duration=0.18,
        is_ranged=False,
        projectile_speed=0.0,
        slash_color=(220, 40, 40),
        hit_particles_color=(180, 20, 20),
        tagline="Devastador barrido en arco amplio impregnado en furia."
    ),

    # 3. PALADÍN (Maza Sagrada de Guerra)
    "mace": WeaponConfig(
        weapon_id="mace",
        name="Maza Sagrada de Guerra",
        weapon_type="mace",
        damage_bonus=26.0,
        attack_range=78.0,
        attack_arc_deg=90.0,
        cooldown=0.38,
        swing_duration=0.16,
        is_ranged=False,
        projectile_speed=0.0,
        slash_color=(255, 220, 90),
        hit_particles_color=(254, 249, 231),
        tagline="Aplastamiento contundente que levanta ondas de luz sagrada."
    ),

    # 4. PÍCARO (Dagas Gemelas de Asesino)
    "daggers": WeaponConfig(
        weapon_id="daggers",
        name="Dagas Gemelas de Asesino",
        weapon_type="daggers",
        damage_bonus=16.0,
        attack_range=70.0,
        attack_arc_deg=80.0,
        cooldown=0.20,
        swing_duration=0.10,
        is_ranged=False,
        projectile_speed=0.0,
        slash_color=(46, 204, 113),
        hit_particles_color=(39, 174, 96),
        tagline="Cortes ultra rápidos de doble estocada letal en puntos ciegos."
    ),

    # 5. CAZADOR (Ballesta Pesada de Repetición)
    "crossbow": WeaponConfig(
        weapon_id="crossbow",
        name="Ballesta Pesada de Repetición",
        weapon_type="crossbow",
        damage_bonus=38.0,
        attack_range=650.0,
        attack_arc_deg=15.0,
        cooldown=0.30,
        swing_duration=0.12,
        is_ranged=True,
        projectile_speed=680.0,
        slash_color=(212, 160, 23),
        hit_particles_color=(200, 195, 185),
        tagline="Disparo certero de saetas de acero que perforan objetivos a distancia."
    ),

    # 6. NIGROMANTE (Guadaña Espectral de Almas)
    "scythe": WeaponConfig(
        weapon_id="scythe",
        name="Guadaña Espectral de Almas",
        weapon_type="scythe",
        damage_bonus=28.0,
        attack_range=105.0,
        attack_arc_deg=145.0,
        cooldown=0.36,
        swing_duration=0.17,
        is_ranged=False,
        projectile_speed=0.0,
        slash_color=(155, 89, 182),
        hit_particles_color=(142, 68, 173),
        tagline="Tajo espectral en media luna que cosecha la esencia vital enemiga."
    ),

    # 7. MAGO (Bastón Rúnico de Éter)
    "staff": WeaponConfig(
        weapon_id="staff",
        name="Bastón Rúnico de Éter",
        weapon_type="staff",
        damage_bonus=0.0,
        attack_range=580.0,
        attack_arc_deg=20.0,
        cooldown=0.25,
        swing_duration=0.14,
        is_ranged=True,
        projectile_speed=580.0,
        slash_color=(52, 152, 219),
        hit_particles_color=(155, 89, 182),
        tagline="Canalización mágica con esferas arcanas y regeneración infinita."
    ),

    # 8. CABALLERO RÚNICO (Espadón Rúnico Ancestral)
    "greatsword": WeaponConfig(
        weapon_id="greatsword",
        name="Espadón Rúnico Ancestral",
        weapon_type="greatsword",
        damage_bonus=32.0,
        attack_range=115.0,
        attack_arc_deg=130.0,
        cooldown=0.42,
        swing_duration=0.18,
        is_ranged=False,
        projectile_speed=0.0,
        slash_color=(52, 152, 219),
        hit_particles_color=(174, 214, 241),
        tagline="Hendidura rúnica colosal que desata esquirlas cortantes de luz."
    ),

    # 9. ALQUIMISTA (Frascos Alquímicos Volátiles)
    "flask": WeaponConfig(
        weapon_id="flask",
        name="Frascos Alquímicos Volátiles",
        weapon_type="flask",
        damage_bonus=30.0,
        attack_range=480.0,
        attack_arc_deg=25.0,
        cooldown=0.32,
        swing_duration=0.13,
        is_ranged=True,
        projectile_speed=480.0,
        slash_color=(46, 204, 113),
        hit_particles_color=(39, 174, 96),
        tagline="Arroja frascos volátiles que estallan en calderas de miasma ácido."
    ),

    # 10. MONJE (Guanteletes del Loto de Acero)
    "fists": WeaponConfig(
        weapon_id="fists",
        name="Guanteletes del Loto de Acero",
        weapon_type="fists",
        damage_bonus=18.0,
        attack_range=68.0,
        attack_arc_deg=70.0,
        cooldown=0.18,
        swing_duration=0.09,
        is_ranged=False,
        projectile_speed=0.0,
        slash_color=(241, 196, 15),
        hit_particles_color=(243, 156, 18),
        tagline="Ráfaga ultrarrápida de puñetazos de Ki con ondas de choque sónicas."
    ),

    # 11. ARTIFICIERO (Cañón Portátil de Vapor y Metralla)
    "cannon": WeaponConfig(
        weapon_id="cannon",
        name="Cañón Portátil de Vapor y Metralla",
        weapon_type="cannon",
        damage_bonus=44.0,
        attack_range=560.0,
        attack_arc_deg=25.0,
        cooldown=0.44,
        swing_duration=0.16,
        is_ranged=True,
        projectile_speed=560.0,
        slash_color=(230, 126, 34),
        hit_particles_color=(211, 84, 0),
        tagline="Dispara proyectiles explosivos de vapor con metralla y retroceso masivo."
    ),

    # 12. CHAMÁN (Tótem Espiritual Primordial)
    "totem": WeaponConfig(
        weapon_id="totem",
        name="Tótem Espiritual Primordial",
        weapon_type="totem",
        damage_bonus=26.0,
        attack_range=95.0,
        attack_arc_deg=120.0,
        cooldown=0.34,
        swing_duration=0.15,
        is_ranged=False,
        projectile_speed=0.0,
        slash_color=(26, 188, 156),
        hit_particles_color=(22, 160, 133),
        tagline="Aplastamiento chamánico que restaura vida al héroe por cada impacto."
    ),

    # 13. INQUISIDOR (Mangual de la Penitencia Carmesí)
    "flail": WeaponConfig(
        weapon_id="flail",
        name="Mangual de la Penitencia Carmesí",
        weapon_type="flail",
        damage_bonus=28.0,
        attack_range=92.0,
        attack_arc_deg=360.0,
        cooldown=0.38,
        swing_duration=0.16,
        is_ranged=False,
        projectile_speed=0.0,
        slash_color=(192, 57, 43),
        hit_particles_color=(231, 76, 60),
        tagline="Barrido penitente continuo en rotación 360° que diezma grupos."
    ),
}


def get_weapon_config(weapon_type: str) -> WeaponConfig:
    """Retorna la configuración del arma solicitada o la espada por defecto."""
    return MEDIEVAL_WEAPONS.get(weapon_type, MEDIEVAL_WEAPONS["sword"])
