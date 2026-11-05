"""
================================================================================
MÓDULO: systems/role_system.py
RESPONSABILIDAD: Catálogo y orquestación de Roles y Clases Medievales seleccionables.
CONCEPTO ACADÉMICO: Patrón Strategy (Estrategias de atributos) y Polimorfismo.
================================================================================
Permite al jugador elegir entre 3 roles sorteados o continuar como Aventurero Medieval (Sin Rol):
1. Berserker Bárbaro: 1250 HP, Gran Hacha Bárbara (+30 DMG en arco amplio), robo de vida balanceado (+5 HP).
2. Paladín Templario: 1150 HP, Maza Sagrada de Guerra (+26 DMG), 25% mitigación, regeneración pasiva y ondas de choque.
3. Pícaro Sombrío: 900 HP, Dagas Gemelas de Asesino (+16 DMG), 50% críticos (x2.2), ultra veloz y dash rápido.
4. Mago Arcano: 900 HP, 800 MP, Bastón Rúnico de Éter, +35% daño mágico y regeneración pasiva (+25 MP/s).
5. Cazador Real (NUEVO): 950 HP, Ballesta Pesada de Repetición (+38 DMG), saetas penetrantes a larga distancia.
6. Nigromante Abisal (NUEVO): 850 HP, Guadaña Espectral (+28 DMG, 140°), cosecha de almas (+8 HP y +20 MP por baja) y magia sombría.
7. Aventurero Medieval (Sin Rol): 1000 HP, 500 MP, Espada de Acero Templado (+20 DMG, 70 total).
"""

import random
from settings import (
    PLAYER_BASE_HP, PLAYER_BASE_MANA, PLAYER_BASE_DAMAGE, PLAYER_WEAPON_DAMAGE,
    PLAYER_INITIAL_WEAPON, COLOR_BRASS, COLOR_GOLD, COLOR_RED_HEALTH,
    COLOR_WHITE, COLOR_STEAM
)


class Role:
    """Clase base de un Rol / Especialización de combate medieval."""

    def __init__(self, role_id: str, name: str, icon: str, tagline: str,
                 pros: list, cons: list, color, apply_callback, weapon_type: str = "sword"):
        self.role_id = role_id
        self.name = name
        self.icon = icon
        self.tagline = tagline
        self.pros = pros
        self.cons = cons
        self.color = color
        self.apply_callback = apply_callback
        self.weapon_type = weapon_type

    def apply(self, player):
        """Aplica las modificaciones al jugador."""
        player.character_id = self.role_id
        self.apply_callback(player)


class RoleSystem:
    """Administrador y catálogo de roles medievales seleccionables."""

    def __init__(self):
        # 1. BERSERKER BÁRBARO (Nerfeado y balanceado)
        def apply_berserker(p):
            p.role_name = "Berserker"
            p.weapon_type = "axe"
            p.has_melee_weapon = True
            p.max_hp = 1250.0                  # Nerfeado de 1500 a 1250 HP
            p.current_hp = 1250.0
            p.max_mana = 500.0
            p.current_mana = 500.0
            p.active_magic_elements = ["Fuego"]  # Magia de Furia Ígnea
            p.life_steal = 5.0                 # Nerfeado de 15 a 5 HP por golpe
            p.speed_mult = 0.85                # Más ágil que antes (0.75 -> 0.85)
            p.weapon_name = "Gran Hacha Bárbara"
            p.weapon_damage = 30.0
            p.radius = 24
            p.attack_cooldown_max = 0.40       # Tajo pesado

        role_berserker = Role(
            role_id="berserker",
            name="Berserker Bárbaro",
            icon="[🪓]",
            tagline="Guerrero salvaje de las tierras del norte con furia sangrienta y gran hacha.",
            pros=[
                "+250 HP Máximo (1250 HP totales)",
                "Robo de Sangre: +5 HP por impacto acertado (+8 en crítico)",
                "Gran Hacha Bárbara: Daño contundente en arco amplio de 135°",
                "Comienza imbuido con Magia de Fuego (Meteorito Ígneo)"
            ],
            cons=[
                "Velocidad -15% (Movimiento pesado)",
                "Ataques más lentos (0.40s de enfriamiento)"
            ],
            color=(214, 48, 49),
            apply_callback=apply_berserker,
            weapon_type="axe"
        )

        # 2. PALADÍN TEMPLARIO (Bufeado)
        def apply_paladin(p):
            p.role_name = "Paladín"
            p.weapon_type = "mace"
            p.has_melee_weapon = True
            p.max_hp = 1150.0                  # Bufeado a 1150 HP
            p.current_hp = 1150.0
            p.max_mana = 600.0
            p.current_mana = 600.0
            p.active_magic_elements = ["Luz"]  # Magia de Luz Sagrada Celestial
            p.damage_reduction = 0.25          # Mitigación del 25% de todo el daño
            p.passive_regen = 14.0             # Bufeado: +14 HP cada 2 segundos
            p.attack_cooldown_max = 0.36
            p.weapon_name = "Maza Sagrada de Guerra"
            p.weapon_damage = 26.0
            p.holy_shockwave = True            # Onda bendecida al impactar

        role_paladin = Role(
            role_id="paladin",
            name="Paladín Templario",
            icon="[🛡️]",
            tagline="Guardián de la fe inquebrantable, bendecido con armadura pesada y luz divina.",
            pros=[
                "+150 HP Máximo (1150 HP) y 25% Reducción de todo el daño",
                "Bendición Sagrada: Regenera +14 HP pasivamente cada 2s",
                "Comienza imbuido con Magia de Luz Celestial y 600 MP",
                "Maza de Guerra: Desata micro-ondas doradas al golpear"
            ],
            cons=[
                "Alcance concentrado de golpe",
                "Menor daño en golpes críticos"
            ],
            color=(241, 196, 15),
            apply_callback=apply_paladin,
            weapon_type="mace"
        )

        # 3. PÍCARO SOMBRÍO (Bufeado)
        def apply_rogue(p):
            p.role_name = "Pícaro"
            p.weapon_type = "daggers"
            p.has_melee_weapon = True
            p.max_hp = 900.0                   # Bufeado de 800 a 900 HP
            p.current_hp = 900.0
            p.max_mana = 550.0
            p.current_mana = 550.0
            p.active_magic_elements = ["Viento"]  # Magia de Viento cortante
            p.speed_mult = 1.30
            p.crit_chance = 0.50               # 50% de probabilidad de crítico
            p.crit_multiplier = 2.2            # Daño crítico aumentado a x2.2
            p.dash_cooldown_max = 0.45         # Dash ágil y veloz
            p.attack_cooldown_max = 0.20       # Doble estocada ultra rápida
            p.weapon_name = "Dagas Gemelas de Asesino"
            p.weapon_damage = 16.0

        role_rogue = Role(
            role_id="rogue",
            name="Pícaro Sombrío",
            icon="[🗡️]",
            tagline="Asesino sigiloso entrenado en cortes rápidos envenenados y evasión acrobática.",
            pros=[
                "50% Probabilidad de Golpe Crítico con daño devastador (x2.2)",
                "Doble Estocada Veloz: Cooldown de ataque mínimo de 0.20s",
                "Comienza imbuido con Magia de Viento (Búmeran Ciclónico) y 550 MP",
                "Evasión Superior: +30% Velocidad y Dash recarga en 0.45s"
            ],
            cons=[
                "Constitución ligera (-100 HP: 900 HP totales)",
                "Alcance corto cuerpo a cuerpo"
            ],
            color=(46, 204, 113),
            apply_callback=apply_rogue,
            weapon_type="daggers"
        )

        # 4. MAGO ARCANO (Bufeado)
        def apply_mage(p):
            p.role_name = "Mago Arcano"
            p.weapon_type = "staff"
            p.has_melee_weapon = False         # Ataca con proyectiles arcanos
            p.weapon_name = "Bastón Rúnico de Éter"
            p.weapon_damage = 0.0
            p.max_hp = 900.0
            p.current_hp = 900.0
            p.max_mana = 800.0
            p.current_mana = 800.0
            p.active_magic_elements = ["Fuego", "Trueno"]
            p.bonus_damage_mult = 1.35         # Bufeado a +35% daño mágico
            p.passive_mana_regen = 25.0        # Bufeado a +25 MP/s
            p.basic_shot_cooldown_max = 0.25   # Dardo veloz de 0 MP

        role_mage = Role(
            role_id="mage",
            name="Mago Arcano",
            icon="[🔮]",
            tagline="Erudito de la alta torre arcana, señor del fuego, relámpagos y éter puro.",
            pros=[
                "Clic Izquierdo: Dardo Arcano (0 MP, genera +18 MP al impactar)",
                "Canalización Infinita: Regenera +25 MP/s pasivamente",
                "Poder Arcano: +35% Daño Mágico, 800 MP y 2 Magias Activas"
            ],
            cons=[
                "Sin ataques cuerpo a cuerpo con espada o corte físico",
                "Requiere apuntado continuo a distancia"
            ],
            color=(155, 89, 182),
            apply_callback=apply_mage,
            weapon_type="staff"
        )

        # 5. CAZADOR REAL (NUEVO ROL MEDIEVAL)
        def apply_hunter(p):
            p.role_name = "Cazador"
            p.weapon_type = "crossbow"
            p.has_melee_weapon = True          # Posee arma principal a distancia
            p.max_hp = 950.0
            p.current_hp = 950.0
            p.max_mana = 600.0
            p.current_mana = 600.0
            p.active_magic_elements = ["Naturaleza"]  # Magia de Bosques y Esporas
            p.speed_mult = 1.15
            p.weapon_name = "Ballesta Pesada de Repetición"
            p.weapon_damage = 38.0
            p.attack_cooldown_max = 0.30

        role_hunter = Role(
            role_id="hunter",
            name="Cazador Real",
            icon="[🏹]",
            tagline="Tirador de élite de la guardia de los bosques con ballesta pesada mecanizada.",
            pros=[
                "Ballesta de Repetición: Dispara saetas veloces a pantalla completa",
                "Perforación de Acero: Las saetas atraviesan hasta 2 enemigos",
                "+15% Velocidad, 600 MP y Magia de Naturaleza (Zarzas y Esporas)"
            ],
            cons=[
                "Ataque lineal directo (sin barrido circular melee)",
                "Constitución moderada (950 HP)"
            ],
            color=(230, 126, 34),
            apply_callback=apply_hunter,
            weapon_type="crossbow"
        )

        # 6. NIGROMANTE ABISAL (NUEVO ROL MEDIEVAL)
        def apply_necromancer(p):
            p.role_name = "Nigromante"
            p.weapon_type = "scythe"
            p.has_melee_weapon = True
            p.max_hp = 850.0
            p.current_hp = 850.0
            p.max_mana = 750.0
            p.current_mana = 750.0
            p.soul_harvest = True              # Cosecha almas: +8 HP y +20 MP al matar
            p.active_magic_elements = ["Oscuridad"]  # Acceso único a magia de Oscuridad
            p.weapon_name = "Guadaña Espectral de Almas"
            p.weapon_damage = 28.0
            p.attack_cooldown_max = 0.36

        role_necromancer = Role(
            role_id="necromancer",
            name="Nigromante Abisal",
            icon="[💀]",
            tagline="Maestro de las artes oscuras que cosecha las almas de sus víctimas.",
            pros=[
                "Cosecha de Almas: Recupera +8 HP y +20 MP por cada enemigo eliminado",
                "Guadaña Espectral: Barrido colosal en media luna con 145° de amplitud",
                "Comienza imbuido con la temible Magia de Oscuridad Abisal"
            ],
            cons=[
                "Baja constitución física (850 HP iniciales)",
                "Requiere ritmo constante de bajas enemigas"
            ],
            color=(108, 92, 231),
            apply_callback=apply_necromancer,
            weapon_type="scythe"
        )

        # 7. CABALLERO RÚNICO (NUEVO)
        def apply_runeknight(p):
            p.role_name = "Caballero Rúnico"
            p.weapon_type = "greatsword"
            p.has_melee_weapon = True
            p.max_hp = 1200.0
            p.current_hp = 1200.0
            p.max_mana = 650.0
            p.current_mana = 650.0
            p.damage_reduction = 0.15          # Escudo rúnico pasivo 15%
            p.weapon_name = "Espadón Rúnico Ancestral"
            p.weapon_damage = 32.0
            p.attack_cooldown_max = 0.42
            p.active_magic_elements = ["Metal"]

        role_runeknight = Role(
            role_id="runeknight",
            name="Caballero Rúnico",
            icon="[⚔️]",
            tagline="Guardián ancestral con espadón rúnico pesado que desata esquirlas cortantes.",
            pros=[
                "Espadón Rúnico: Gran alcance y libera esquirlas cortantes de luz al impactar",
                "Armadura Rúnica: 1200 HP y 15% de reducción permanente de daño recibido",
                "Comienza imbuido con Magia de Metal y 650 MP de reserva"
            ],
            cons=[
                "Ataques contundentes pero pausados (0.42s cooldown)",
                "Velocidad de movimiento pesada"
            ],
            color=(52, 152, 219),
            apply_callback=apply_runeknight,
            weapon_type="greatsword"
        )

        # 8. ALQUIMISTA DE PLAGA (NUEVO)
        def apply_alchemist(p):
            p.role_name = "Alquimista"
            p.weapon_type = "flask"
            p.has_melee_weapon = True
            p.max_hp = 920.0
            p.current_hp = 920.0
            p.max_mana = 750.0
            p.current_mana = 750.0
            p.speed_mult = 1.10
            p.weapon_name = "Frascos Alquímicos Volátiles"
            p.weapon_damage = 30.0
            p.attack_cooldown_max = 0.32
            p.active_magic_elements = ["Naturaleza"]

        role_alchemist = Role(
            role_id="alchemist",
            name="Alquimista de Plaga",
            icon="[⚗️]",
            tagline="Erudito de pociones que arroja frascos volátiles creando charcos de ácido y fuego.",
            pros=[
                "Frascos Alquímicos: Ataque a distancia que estalla en charcos ácidos de área",
                "Reserva Erudita: 750 MP y +10% velocidad de movimiento",
                "Comienza imbuido con Magia de Naturaleza regenerativa"
            ],
            cons=[
                "Sin corte directo cuerpo a cuerpo",
                "Constitución moderada (920 HP)"
            ],
            color=(46, 204, 113),
            apply_callback=apply_alchemist,
            weapon_type="flask"
        )

        # 9. MONJE ASCETA (NUEVO)
        def apply_monk(p):
            p.role_name = "Monje Asceta"
            p.weapon_type = "fists"
            p.has_melee_weapon = True
            p.max_hp = 1050.0
            p.current_hp = 1050.0
            p.max_mana = 650.0
            p.current_mana = 650.0
            p.active_magic_elements = ["Trueno"]  # Magia de Relámpago y Ki Eléctrico
            p.speed_mult = 1.25
            p.crit_chance = 0.40               # 40% críticos
            p.crit_multiplier = 2.1
            p.dash_cooldown_max = 0.50
            p.weapon_name = "Guanteletes del Loto de Acero"
            p.weapon_damage = 18.0
            p.attack_cooldown_max = 0.18       # Ráfaga ultrarrápida

        role_monk = Role(
            role_id="monk",
            name="Monje Asceta",
            icon="[🥋]",
            tagline="Maestro marcial de ráfagas de puños de Ki, impactos sónicos y agilidad extrema.",
            pros=[
                "Ráfaga de Loto: Cooldown de ataque mínimo de 0.18s con ondas sónicas de Ki",
                "40% de probabilidad de crítico y Dash con recarga rápida de 0.50s",
                "Comienza imbuido con Magia de Trueno (Descarga de Ki) y 650 MP",
                "+25% Velocidad de movimiento y equilibrio perfecto de 1050 HP"
            ],
            cons=[
                "Alcance corto cuerpo a cuerpo (requiere combate a quemarropa)",
                "Menor daño individual por golpe"
            ],
            color=(241, 196, 15),
            apply_callback=apply_monk,
            weapon_type="fists"
        )

        # 10. ARTIFICIERO STEAMPUNK (NUEVO)
        def apply_artificer(p):
            p.role_name = "Artificiero"
            p.weapon_type = "cannon"
            p.has_melee_weapon = True
            p.max_hp = 1100.0
            p.current_hp = 1100.0
            p.max_mana = 600.0
            p.current_mana = 600.0
            p.damage_reduction = 0.18          # Blindaje de latón 18%
            p.weapon_name = "Cañón Portátil de Vapor y Metralla"
            p.weapon_damage = 44.0
            p.attack_cooldown_max = 0.44
            p.active_magic_elements = ["Vapor"]

        role_artificer = Role(
            role_id="artificer",
            name="Artificiero Steampunk",
            icon="[⚙️]",
            tagline="Ingeniero de combate con cañón de vapor que dispara proyectiles de metralla expansiva.",
            pros=[
                "Cañón de Vapor: Dispara obuses explosivos con onda de choque y calderas de vapor",
                "Blindaje de Latón: 1100 HP y 18% de reducción de daño permanente",
                "Comienza imbuido con Magia de Vapor (Steampunk)"
            ],
            cons=[
                "Disparos pesados con enfriamiento pausado (0.44s)",
                "Retroceso físico en cada disparo"
            ],
            color=(230, 126, 34),
            apply_callback=apply_artificer,
            weapon_type="cannon"
        )

        # 11. CHAMÁN DE LAS BESTIAS (NUEVO)
        def apply_shaman(p):
            p.role_name = "Chamán"
            p.weapon_type = "totem"
            p.has_melee_weapon = True
            p.max_hp = 1000.0
            p.current_hp = 1000.0
            p.max_mana = 800.0
            p.current_mana = 800.0
            p.passive_regen = 10.0             # +10 HP cada 2s
            p.weapon_name = "Tótem Espiritual Primordial"
            p.weapon_damage = 26.0
            p.attack_cooldown_max = 0.34
            p.active_magic_elements = ["Tierra", "Naturaleza"]

        role_shaman = Role(
            role_id="shaman",
            name="Chamán de las Bestias",
            icon="[🐺]",
            tagline="Místico de la tierra que sana al golpear con su tótem y comanda fuerzas primordiales.",
            pros=[
                "Tótem Espiritual: Sana +4 HP al jugador por cada enemigo impactado",
                "Vínculo Primitivo: 800 MP, regeneración pasiva y 2 magias activas (Tierra y Naturaleza)",
                "Barrido amplio de 120° con impactos contundentes"
            ],
            cons=[
                "Velocidad de movimiento estándar",
                "Daño moderado de arma"
            ],
            color=(26, 188, 156),
            apply_callback=apply_shaman,
            weapon_type="totem"
        )

        # 12. INQUISIDOR DE SANGRE (NUEVO)
        def apply_inquisitor(p):
            p.role_name = "Inquisidor"
            p.weapon_type = "flail"
            p.has_melee_weapon = True
            p.max_hp = 980.0
            p.current_hp = 980.0
            p.max_mana = 700.0
            p.current_mana = 700.0
            p.weapon_name = "Mangual de la Penitencia Carmesí"
            p.weapon_damage = 28.0
            p.attack_cooldown_max = 0.38
            p.active_magic_elements = ["Fuego"]

        role_inquisitor = Role(
            role_id="inquisitor",
            name="Inquisidor de Sangre",
            icon="[⛓️]",
            tagline="Fanático sagrado que blande un mangual dentado en rotación 360° desatando penitencia.",
            pros=[
                "Mangual Giratorio: Ataque en área completa de 360° que barre a todos los enemigos cercanos",
                "Penitencia Carmesí: Desata chispas sagradas continuas al impactar múltiples objetivos",
                "Comienza imbuido con Magia de Fuego y 700 MP de reserva"
            ],
            cons=[
                "Requiere adentrarse entre hordas para maximizar el daño de 360°",
                "Constitución media (980 HP)"
            ],
            color=(192, 57, 43),
            apply_callback=apply_inquisitor,
            weapon_type="flail"
        )

        self.characters = [
            role_berserker,
            role_paladin,
            role_rogue,
            role_mage,
            role_hunter,
            role_necromancer,
            role_runeknight,
            role_alchemist,
            role_monk,
            role_artificer,
            role_shaman,
            role_inquisitor
        ]
        # Compatibilidad con variables previas
        self.special_roles = self.characters
        self.none_role = None

    def get_all_characters(self) -> list:
        """Retorna los 12 personajes disponibles para la selección estilo Slay the Spire 2."""
        return self.characters

    def get_character(self, role_id: str):
        """Retorna la instancia del personaje por su role_id o el primero por defecto."""
        for c in self.characters:
            if c.role_id == role_id or c.name.lower() == str(role_id).lower():
                return c
        return self.characters[0] if self.characters else None

    def get_selection_offer(self, count=12) -> list:
        """Retorna los personajes disponibles para elegir."""
        return self.characters[:count]
