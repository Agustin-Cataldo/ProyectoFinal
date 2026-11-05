"""
================================================================================
MÓDULO: systems/card_system.py
RESPONSABILIDAD: Gestión del sistema de progresión por cartas y magia elemental.
CONCEPTO ACADÉMICO: Algoritmos de Selección Ponderada, Reglas de Exclusión Estricta
                    y Patrón Strategy para la aplicación de efectos.
================================================================================
Gestiona:
1. Pool de 32 Cartas Estándar (Daño, Vida, Velocidad, Magia estándar).
2. Pool de 16 Cartas Doradas (Combinadas o Habilidades Nuevas Únicas).
3. REGLA ESTRICTA: Las magias de OSCURIDAD y LUZ son 100% EXCLUSIVAS de las Cartas Doradas.
4. Selección de 3 cartas cada 3 niveles, con probabilidad dorada cada 5 rondas.
"""

import random
from typing import List, Dict, Any, Optional
from settings import (
    STANDARD_CARDS_POOL_SIZE, GOLDEN_CARDS_POOL_SIZE,
    MAGIC_ELEMENTS_STANDARD, MAGIC_ELEMENTS_EXCLUSIVE,
    GOLDEN_CARD_INTERVAL, GOLDEN_CARD_CHANCE
)
from systems.character_cards_database import (
    CharacterCard, CHARACTER_DECKS, get_deck_for_character
)


class Card:
    """Clase que representa una carta coleccionable de mejora."""

    def __init__(self, card_id: str, name: str, category: str, description: str,
                 is_golden: bool, effect_fn, exclusive_element: str = None):
        self.card_id = card_id
        self.name = name
        self.category = category            # 'Daño', 'Vida', 'Velocidad', 'Magia', 'Dorada'
        self.description = description
        self.is_golden = is_golden
        self.effect_fn = effect_fn          # Función lambda/callback que modifica al Player
        self.exclusive_element = exclusive_element
        self.rarity = "Rara" if is_golden else "Común"

    def apply(self, player):
        """Aplica las mejoras de la carta directamente al objeto Player.
        Si la carta otorga un elemento mágico exclusivo y el jugador ya tiene la capacidad máxima
        (2 elementos activos), señaliza que se necesita intercambio via SpellSwapMenu.
        """
        if self.effect_fn:
            self.effect_fn(player)
        # Gestionar elementos mágicos exclusivos
        if self.exclusive_element:
            # Evitar duplicados
            if self.exclusive_element in player.active_magic_elements:
                return
            # Si hay espacio libre, asignar directamente
            max_elements = 2
            if len(player.active_magic_elements) < max_elements:
                player.active_magic_elements.append(self.exclusive_element)
            else:
                # Señalizar al engine que debe abrir el SpellSwapMenu
                # El engine revisará este atributo tras aplicar la carta
                player._pending_spell_swap = self.exclusive_element


class CardSystem:
    """Administrador central de barajas y probabilidades de aparición."""

    def __init__(self):
        self.standard_pool: List[Card] = []
        self.golden_pool: List[Card] = []
        self._build_card_pools()
        self._verify_academic_integrity()

    def _build_card_pools(self):
        """
        Construye con precisión matemática:
        - Exactamente 32 cartas estándar (Categorías: Daño, Vida, Velocidad, Magia Base).
        - Exactamente 16 cartas doradas (Combinaciones dobles y magias exclusivas Luz/Oscuridad).
        """
        # =====================================================================
        # 1. RESERVA DE 32 CARTAS ESTÁNDAR (Sin Luz ni Oscuridad)
        # =====================================================================

        # --- CATEGORÍA 1: DAÑO (8 cartas) ---
        damage_cards = [
            Card("D1", "Filo de Piedra Tallado", "Daño", "+15% al daño total de la espada.", False,
                 lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.15)),
            Card("D2", "Empuñadura de Cuero y Cobre", "Daño", "+10 puntos de daño fijo a la espada.", False,
                 lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 10)),
            Card("D3", "Temple al Carbón Forjado", "Daño", "+20% al daño total de combate.", False,
                 lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.20)),
            Card("D4", "Remaches de Acero Pesado", "Daño", "+15 puntos de daño base al héroe.", False,
                 lambda p: setattr(p, 'base_damage', p.base_damage + 15)),
            Card("D5", "Punta Biselada de Obsidiana", "Daño", "+18% al daño total de la espada.", False,
                 lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.18)),
            Card("D6", "Fuelle de Combustión", "Daño", "+12 puntos de daño fijo adicional.", False,
                 lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 12)),
            Card("D7", "Presión de Vapor Ofensiva", "Daño", "+25% daño total a cambio de técnica.", False,
                 lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.25)),
            Card("D8", "Martilleo Rúnico de Enano", "Daño", "+20 puntos de daño fijo.", False,
                 lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 20)),
        ]

        # --- CATEGORÍA 2: VIDA (8 cartas) ---
        health_cards = [
            Card("V1", "Caldera de Latón Reforzada", "Vida", "+100 HP Máximos y cura 100 HP.", False,
                 lambda p: (setattr(p, 'max_hp', p.max_hp + 100), p.heal(100))),
            Card("V2", "Poción de Alquimista de Vapor", "Vida", "Restaura 200 HP de salud inmediatamente.", False,
                 lambda p: p.heal(200)),
            Card("V3", "Placas de Cobre Torácicas", "Vida", "+150 HP Máximos.", False,
                 lambda p: (setattr(p, 'max_hp', p.max_hp + 150), p.heal(50))),
            Card("V4", "Válvula de Seguridad de Presión", "Vida", "Reduce todo el daño recibido en un 12%.", False,
                 lambda p: setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.12))),
            Card("V5", "Tónico de Sales Medievales", "Vida", "Restaura 300 HP inmediatamente.", False,
                 lambda p: p.heal(300)),
            Card("V6", "Coraza de Bronce Templado", "Vida", "+120 HP Máximos y reduce daño en 8%.", False,
                 lambda p: (setattr(p, 'max_hp', p.max_hp + 120), p.heal(60),
                            setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.08)))),
            Card("V7", "Filtro Regenerador de Vapor", "Vida", "+80 HP Máximos y cura 150 HP.", False,
                 lambda p: (setattr(p, 'max_hp', p.max_hp + 80), p.heal(150))),
            Card("V8", "Bastión de Piedra Gigante", "Vida", "+200 HP Máximos pero reduce velocidad 5%.", False,
                 lambda p: (setattr(p, 'max_hp', p.max_hp + 200), p.heal(100),
                            setattr(p, 'speed_mult', max(0.6, p.speed_mult - 0.05)))),
        ]

        # --- CATEGORÍA 3: VELOCIDAD (8 cartas) ---
        speed_cards = [
            Card("S1", "Pistones de Botas de Vapor", "Velocidad", "+15% de velocidad de movimiento.", False,
                 lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.15)),
            Card("S2", "Engranajes Ligeros de Precisión", "Velocidad", "+20% de velocidad de movimiento.", False,
                 lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.20)),
            Card("S3", "Válvula de Escape Rápido", "Velocidad", "+25% de velocidad y reduce cooldown de espada.", False,
                 lambda p: (setattr(p, 'speed_mult', p.speed_mult + 0.25),
                            setattr(p, 'attack_cooldown_max', max(0.18, p.attack_cooldown_max - 0.05)))),
            Card("S4", "Grasa Mecánica Especial", "Velocidad", "+12% velocidad y movimiento más ágil.", False,
                 lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.12)),
            Card("S5", "Amortiguadores Hidráulicos", "Velocidad", "+18% velocidad de traslación.", False,
                 lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.18)),
            Card("S6", "Zancada del Caballero Alado", "Velocidad", "+22% velocidad de movimiento.", False,
                 lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.22)),
            Card("S7", "Circuito de Sobremarcha", "Velocidad", "+30% velocidad temporal de carrera.", False,
                 lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.30)),
            Card("S8", "Celeridad de Relojería", "Velocidad", "+15% velocidad y +10% daño.", False,
                 lambda p: (setattr(p, 'speed_mult', p.speed_mult + 0.15),
                            setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.10))),
        ]

        # --- CATEGORÍA 4: MAGIA ESTÁNDAR (8 cartas: 6 elementos base + 2 mejoras mágicas) ---
        # NOTA VITAL: Oscuridad y Luz NO forman parte de esta reserva.
        magic_cards = [
            Card("M1", "Pacto de Fuego Elemental", "Magia", "Imbuye la espada con llamas que queman al golpear.", False,
                 None, exclusive_element="Fuego"),
            Card("M2", "Torrente de Agua a Presión", "Magia", "Imbuye la espada con hidro-impacto ralentizador.", False,
                 None, exclusive_element="Agua"),
            Card("M3", "Tajo del Viento Tempestuoso", "Magia", "La espada corta con ráfagas afiladas de viento.", False,
                 None, exclusive_element="Viento"),
            Card("M4", "Fuerza Sísmica de la Tierra", "Magia", "Los golpes provocan temblores y empuje masivo.", False,
                 None, exclusive_element="Tierra"),
            Card("M5", "Chispa del Trueno Ancestral", "Magia", "Descargas eléctricas encadenadas al impactar.", False,
                 None, exclusive_element="Trueno"),
            Card("M6", "Raíces de la Naturaleza Salvaje", "Magia", "Espinas orgánicas que dañan a los enemigos.", False,
                 None, exclusive_element="Naturaleza"),
            Card("M7", "Resonancia de Vapor Mágico", "Magia", "+20% al alcance del corte de espada.", False,
                 lambda p: setattr(p, 'radius', p.radius + 4)),
            Card("M8", "Canalizador de Eter Elemental", "Magia", "+25% al daño de todos los efectos mágicos.", False,
                 lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.25)),
        ]

        # Consolidación de las 32 cartas estándar
        self.standard_pool = damage_cards + health_cards + speed_cards + magic_cards

        # =====================================================================
        # 2. RESERVA DE 16 CARTAS DORADAS (Con Luz, Oscuridad y Dobles Poderes)
        # =====================================================================

        # --- A. HABILIDADES NUEVAS Y EXCLUSIVAS (4 cartas) ---
        exclusive_golden = [
            # EXCLUSIVIDAD 1: LUZ
            Card("G_LUZ", "⭐ Magia de Luz Celestial (EXCLUSIVA)", "Dorada",
                 "PODER DIVINO: Golpea con rayos sagrados y regenera vida del héroe.", True,
                 lambda p: (p.heal(150), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.30)),
                 exclusive_element="Luz"),

            # EXCLUSIVIDAD 2: OSCURIDAD
            Card("G_OSC", "⭐ Magia de Oscuridad Abisal (EXCLUSIVA)", "Dorada",
                 "PODER SOMBRÍO: Drena el alma de los enemigos e inflige daño devastador.", True,
                 lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.40),
                            setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.15))),
                 exclusive_element="Oscuridad"),

            # HABILIDADES NUEVAS TOTALMENTE ÚNICAS
            Card("G_STEAM", "⭐ Núcleo de Fusión Hiper-Vapor", "Dorada",
                 "+300 HP Máximos, +35% Daño y +20% Velocidad simultáneamente.", True,
                 lambda p: (setattr(p, 'max_hp', p.max_hp + 300), p.heal(300),
                            setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.35),
                            setattr(p, 'speed_mult', p.speed_mult + 0.20))),

            Card("G_TITAN", "⭐ Hoja Colosal de los Fundadores", "Dorada",
                 "+50 daño directo al arma y duplica la velocidad de ataque de la espada.", True,
                 lambda p: (setattr(p, 'weapon_damage', p.weapon_damage + 50),
                            setattr(p, 'attack_cooldown_max', max(0.15, p.attack_cooldown_max * 0.65)))),
        ]

        # --- B. COMBINACIÓN DE 2 HABILIDADES ALEATORIAS EN UNA (12 cartas) ---
        combo_golden = [
            Card("G_C1", "⭐ Vigor Titánico y Furia Ígnea", "Dorada",
                 "Combina +200 HP Máximos y desata la Magia de Fuego.", True,
                 lambda p: (setattr(p, 'max_hp', p.max_hp + 200), p.heal(200)),
                 exclusive_element="Fuego"),

            Card("G_C2", "⭐ Botas de Rayo y Torbellino", "Dorada",
                 "Combina +30% Velocidad y Magia de Viento cortante.", True,
                 lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.30),
                 exclusive_element="Viento"),

            Card("G_C3", "⭐ Bastión Pétreo y Choque de Trueno", "Dorada",
                 "Combina 20% Reducción de Daño y Magia de Trueno.", True,
                 lambda p: setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.20)),
                 exclusive_element="Trueno"),

            Card("G_C4", "⭐ Armadura de Caldera y Tónico Vital", "Dorada",
                 "Combina +250 HP Máximos y +30% Daño de combate.", True,
                 lambda p: (setattr(p, 'max_hp', p.max_hp + 250), p.heal(250),
                            setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.30))),

            Card("G_C5", "⭐ Marea Abisal y Sobremarcha", "Dorada",
                 "Combina Magia de Agua a presión y +25% Velocidad.", True,
                 lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.25),
                 exclusive_element="Agua"),

            Card("G_C6", "⭐ Cosecha Ancestral y Regeneración", "Dorada",
                 "Combina Magia de Naturaleza y Cura el 100% de la vida actual.", True,
                 lambda p: p.heal(p.max_hp),
                 exclusive_element="Naturaleza"),

            Card("G_C7", "⭐ Puño Sísmico y Temple de Acero", "Dorada",
                 "Combina Magia de Tierra y +40 puntos de daño fijo.", True,
                 lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 40),
                 exclusive_element="Tierra"),

            Card("G_C8", "⭐ Danza de las Aspas de Vapor", "Dorada",
                 "Combina +30% Daño y +25% Velocidad de movimiento.", True,
                 lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.30),
                            setattr(p, 'speed_mult', p.speed_mult + 0.25))),

            Card("G_C9", "⭐ Corazón Mecánico Indestructible", "Dorada",
                 "Combina +250 HP Máximos y 25% Reducción de Daño.", True,
                 lambda p: (setattr(p, 'max_hp', p.max_hp + 250), p.heal(250),
                            setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.25)))),

            Card("G_C10", "⭐ Furia Doble: Fuego y Chispa", "Dorada",
                 "Combina +35% Daño y activa Magia de Trueno.", True,
                 lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.35),
                 exclusive_element="Trueno"),

            Card("G_C11", "⭐ Escudo de Titanio y Torrente", "Dorada",
                 "Combina +150 HP, +15% Daño y Magia de Agua.", True,
                 lambda p: (setattr(p, 'max_hp', p.max_hp + 150), p.heal(150),
                            setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.15)),
                 exclusive_element="Agua"),

            Card("G_C12", "⭐ Frenesí de Relojero Legendario", "Dorada",
                 "Combina +40% Velocidad y -40% Cooldown de espada.", True,
                 lambda p: (setattr(p, 'speed_mult', p.speed_mult + 0.40),
                            setattr(p, 'attack_cooldown_max', max(0.14, p.attack_cooldown_max * 0.60)))),
        ]

        # Consolidación de las 16 cartas doradas
        self.golden_pool = exclusive_golden + combo_golden

    def _verify_academic_integrity(self):
        """
        Método de verificación y validación formal de requerimientos para el tribunal.
        Lanza excepción si las cantidades o reglas no coinciden exactamente.
        """
        assert len(self.standard_pool) == STANDARD_CARDS_POOL_SIZE, \
            f"Error: Deben existir exactamente {STANDARD_CARDS_POOL_SIZE} cartas estándar (Hay {len(self.standard_pool)})."
        assert len(self.golden_pool) == GOLDEN_CARDS_POOL_SIZE, \
            f"Error: Deben existir exactamente {GOLDEN_CARDS_POOL_SIZE} cartas doradas (Hay {len(self.golden_pool)})."

        # Regla Crítica: Luz y Oscuridad no pueden estar en cartas estándar
        for c in self.standard_pool:
            assert c.exclusive_element not in MAGIC_ELEMENTS_EXCLUSIVE, \
                f"Violación de Regla: Elemento exclusivo {c.exclusive_element} detectado en carta estándar {c.name}."

    def get_selection_offer(self, level_completed: int, player=None) -> List[Any]:
        """
        Genera una oferta de 3 cartas únicas inspirada en Slay the Spire 2:
        - Si se provee al Player, selecciona cartas 100% EXCLUSIVAS de su baraja de 50 cartas.
        - Cada 5 rondas completadas, existe alta probabilidad de que aparezca una carta Dorada/Rara del personaje.
        """
        if player is not None:
            # Obtener la baraja especializada de 50 cartas del personaje
            char_identifier = getattr(player, 'character_id', getattr(player, 'role_name', 'berserker'))
            deck = get_deck_for_character(char_identifier)

            regular_cards = [c for c in deck if not c.is_golden]
            golden_cards = [c for c in deck if c.is_golden]

            is_golden_round = (level_completed % GOLDEN_CARD_INTERVAL == 0)
            spawn_golden = is_golden_round and (random.random() < GOLDEN_CARD_CHANCE)

            chosen = []
            if spawn_golden and golden_cards:
                chosen.append(random.choice(golden_cards))
                sample_count = min(2, len(regular_cards))
                chosen.extend(random.sample(regular_cards, sample_count))
            else:
                sample_count = min(3, len(regular_cards))
                chosen.extend(random.sample(regular_cards, sample_count))

            random.shuffle(chosen)
            return chosen

        # Modo fallback genérico
        cards_to_return = []
        is_golden_round = (level_completed % GOLDEN_CARD_INTERVAL == 0)
        spawn_golden = is_golden_round and (random.random() < GOLDEN_CARD_CHANCE)

        if spawn_golden:
            golden_card = random.choice(self.golden_pool)
            cards_to_return.append(golden_card)
            standards = random.sample(self.standard_pool, 2)
            cards_to_return.extend(standards)
        else:
            cards_to_return = random.sample(self.standard_pool, 3)

        random.shuffle(cards_to_return)
        return cards_to_return
