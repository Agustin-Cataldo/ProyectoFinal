"""
================================================================================
MÓDULO: systems/character_cards_database.py
RESPONSABILIDAD: Catálogo exhaustivo de 50 cartas de mejora únicas por Personaje
                 inspirado en Slay the Spire 2 (300 cartas de mejora únicas en total).
CONCEPTO ACADÉMICO: Patrón Flyweight / Card Database con barajas especializadas.
================================================================================
Cada uno de los 6 Personajes Legendarios posee su propia baraja de 50 cartas exclusivas:
1. Berserker Bárbaro: Cartas Rojas (Furia, Daño colosal, Sed de sangre, Sacrificio, Armadura pesada).
2. Paladín Templario: Cartas Doradas (Luz divina, Mitigación, Curación, Ondas sagradas, Escudos).
3. Pícaro Sombrío: Cartas Verdes (Veneno, Críticos extremos, Agilidad, Dagas veloces, Sigilo).
4. Mago Arcano: Cartas Azules (Éter, Sobrecarga de maná, Elementos, Resonancia, Orbes).
5. Cazador Real: Cartas Naranjas (Puntería, Saetas perforantes, Trampas, Perforación, Agilidad).
6. Nigromante Abisal: Cartas Púrpuras (Cosecha de almas, Maldiciones, Drenaje vital, Miasma, Sombras).
"""

from typing import List, Callable, Optional


class CharacterCard:
    """Representa una carta de mejora exclusiva de un Personaje."""

    def __init__(self, card_id: str, character_id: str, name: str, category: str,
                 rarity: str, description: str, effect_fn: Callable,
                 exclusive_element: Optional[str] = None):
        self.card_id = card_id
        self.character_id = character_id    # 'berserker', 'paladin', 'rogue', 'mage', 'hunter', 'necromancer'
        self.name = name
        self.category = category            # 'Ataque', 'Defensa', 'Habilidad', 'Poder'
        self.rarity = rarity                # 'Común', 'Poco Común', 'Rara' (Dorada)
        self.description = description
        self.effect_fn = effect_fn
        self.exclusive_element = exclusive_element
        self.is_golden = (rarity == "Rara")

    def apply(self, player):
        """Aplica los efectos de la carta sobre el jugador."""
        if self.effect_fn:
            self.effect_fn(player)
        if self.exclusive_element:
            if self.exclusive_element in player.active_magic_elements:
                return
            # Si hay espacio libre, asignar directamente
            if len(player.active_magic_elements) < 2:
                player.active_magic_elements.append(self.exclusive_element)
            else:
                # Señalizar al engine que debe abrir el SpellSwapMenu
                player._pending_spell_swap = self.exclusive_element


def _build_berserker_deck() -> List[CharacterCard]:
    cards = []
    c = "berserker"
    # 50 Cartas Rojas de Furia & Sangre
    b_data = [
        ("B01", "Furia Ciega", "Ataque", "Común", "+18% daño de hacha pero -3% velocidad.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.18), setattr(p, 'speed_mult', max(0.6, p.speed_mult - 0.03)))),
        ("B02", "Golpe Rompehuesos", "Ataque", "Común", "+15 daño fijo al hacha.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 15)),
        ("B03", "Sed de Sangre", "Poder", "Común", "+2 HP extra de robo de vida por impacto.", lambda p: setattr(p, 'life_steal', p.life_steal + 2.0)),
        ("B04", "Piel de Hierro", "Defensa", "Común", "+100 HP máximos y cura 100 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 100), p.heal(100))),
        ("B05", "Tajo Desgarrador", "Ataque", "Común", "+12% daño total de combate.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.12)),
        ("B06", "Grito de Guerra", "Habilidad", "Común", "+10% velocidad de movimiento.", lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.10)),
        ("B07", "Coraza de Espinas", "Defensa", "Común", "Reduce todo el daño recibido en un 8%.", lambda p: setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.08))),
        ("B08", "Hacha Enloquecida", "Ataque", "Común", "Reduce el cooldown de swing del hacha en 0.04s.", lambda p: setattr(p, 'attack_cooldown_max', max(0.18, p.attack_cooldown_max - 0.04))),
        ("B09", "Frenesí Brutal", "Poder", "Común", "+10% daño y cura 50 HP.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.10), p.heal(50))),
        ("B10", "Tendones de Acero", "Defensa", "Común", "+120 HP máximos.", lambda p: (setattr(p, 'max_hp', p.max_hp + 120), p.heal(60))),
        ("B11", "Tajo Pesado", "Ataque", "Común", "+18 daño de arma.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 18)),
        ("B12", "Furia de Batalla", "Habilidad", "Común", "+15% daño durante toda la partida.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.15)),
        ("B13", "Bravura Bárbara", "Defensa", "Común", "+80 HP y reduce daño en 5%.", lambda p: (setattr(p, 'max_hp', p.max_hp + 80), p.heal(80), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.05)))),
        ("B14", "Embate Salvaje", "Ataque", "Común", "+20% daño de corte.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.20)),
        ("B15", "Rabia Creciente", "Poder", "Común", "+3 HP robo de sangre por corte.", lambda p: setattr(p, 'life_steal', p.life_steal + 3.0)),
        ("B16", "Aplastamiento", "Ataque", "Común", "+16 daño fijo de hacha.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 16)),
        ("B17", "Fuerza Primitiva", "Poder", "Común", "+22% daño de ataque.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.22)),
        ("B18", "Instinto Asesino", "Habilidad", "Común", "+10% crítico y +5% velocidad.", lambda p: (setattr(p, 'crit_chance', p.crit_chance + 0.10), setattr(p, 'speed_mult', p.speed_mult + 0.05))),
        ("B19", "Corte en Remolino", "Ataque", "Común", "+25 daño de arma.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 25)),
        ("B20", "Pacto Ígneo", "Habilidad", "Común", "Desata Magia de Fuego en tu hacha.", None, "Fuego"),
        # Poco Comunes (20)
        ("B21", "Ira Inmortal", "Poder", "Poco Común", "+200 HP Máximos y cura 150 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 200), p.heal(150))),
        ("B22", "Vórtice Carmesí", "Ataque", "Poco Común", "+30% daño de combate total.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.30)),
        ("B23", "Sed Voraz", "Poder", "Poco Común", "+4 HP robo de vida y cura 100 HP.", lambda p: (setattr(p, 'life_steal', p.life_steal + 4.0), p.heal(100))),
        ("B24", "Golpe Sísmico", "Ataque", "Poco Común", "+35 daño de hacha.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 35)),
        ("B25", "Sacrificio de Sangre", "Poder", "Poco Común", "+35% daño total pero reduce 50 HP máx.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.35), setattr(p, 'max_hp', max(400.0, p.max_hp - 50)))),
        ("B26", "Imparable", "Defensa", "Poco Común", "+15% velocidad y 10% reducción de daño.", lambda p: (setattr(p, 'speed_mult', p.speed_mult + 0.15), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.10)))),
        ("B27", "Armadura de Huesos", "Defensa", "Poco Común", "+150 HP máximos y +8% mitigación.", lambda p: (setattr(p, 'max_hp', p.max_hp + 150), p.heal(100), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.08)))),
        ("B28", "Furia Destructiva", "Ataque", "Poco Común", "+28% daño y reduce cooldown de hacha.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.28), setattr(p, 'attack_cooldown_max', max(0.18, p.attack_cooldown_max - 0.05)))),
        ("B29", "Sed de Venganza", "Poder", "Poco Común", "+5 HP robo de vida adicional.", lambda p: setattr(p, 'life_steal', p.life_steal + 5.0)),
        ("B30", "Furia de la Tierra", "Habilidad", "Poco Común", "Imbuye golpes con Magia de Tierra.", None, "Tierra"),
        ("B31", "Rugido Aterrador", "Habilidad", "Poco Común", "+20% velocidad y empuje masivo.", lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.20)),
        ("B32", "Herida Abierta", "Ataque", "Poco Común", "+40 daño fijo suplementario.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 40)),
        ("B33", "Furia Roja", "Poder", "Poco Común", "+25% daño y cura 150 HP.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.25), p.heal(150))),
        ("B34", "Golpe Rompearmaduras", "Ataque", "Poco Común", "+32% daño de impacto directo.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.32)),
        ("B35", "Corazón de Hierro", "Defensa", "Poco Común", "+220 HP máximos.", lambda p: (setattr(p, 'max_hp', p.max_hp + 220), p.heal(150))),
        ("B36", "Furia del Trueno", "Habilidad", "Poco Común", "Desata arcos voltaicos con Magia de Trueno.", None, "Trueno"),
        ("B37", "Furia Espartana", "Poder", "Poco Común", "+20% daño y +15% velocidad.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.20), setattr(p, 'speed_mult', p.speed_mult + 0.15))),
        ("B38", "Golpe Decapitador", "Ataque", "Poco Común", "+45 daño de hacha.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 45)),
        ("B39", "Resistencia Inhumana", "Defensa", "Poco Común", "Reduce daño recibido en un 15%.", lambda p: setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.15))),
        ("B40", "Furia Berserk", "Poder", "Poco Común", "+35% daño total de combate.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.35)),
        # Raras / Doradas (10)
        ("B41", "⭐ Sed del Dragón Carmesí", "Poder", "Rara", "+300 HP Máximos, +40% Daño y +6 HP robo de vida.", lambda p: (setattr(p, 'max_hp', p.max_hp + 300), p.heal(300), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.40), setattr(p, 'life_steal', p.life_steal + 6.0))),
        ("B42", "⭐ Hacha Titánica de los Ancestros", "Ataque", "Rara", "+60 daño de arma y acelera el corte un 30%.", lambda p: (setattr(p, 'weapon_damage', p.weapon_damage + 60), setattr(p, 'attack_cooldown_max', max(0.16, p.attack_cooldown_max * 0.70)))),
        ("B43", "⭐ Furia de la Oscuridad Eterna", "Poder", "Rara", "Otorga la mística Magia de Oscuridad Abisal y +35% daño.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.35), "Oscuridad"),
        ("B44", "⭐ Inmortalidad Sangrienta", "Defensa", "Rara", "+400 HP Máximos y cura el 100% de la vida.", lambda p: (setattr(p, 'max_hp', p.max_hp + 400), p.heal(p.max_hp))),
        ("B45", "⭐ Vórtice de Sangre y Fuego", "Habilidad", "Rara", "Combina +45% Daño y Magia de Fuego destructor.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.45), "Fuego"),
        ("B46", "⭐ Coloso Imparable de la Niebla", "Defensa", "Rara", "Reduce todo el daño en un 22% y otorga +250 HP.", lambda p: (setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.22)), setattr(p, 'max_hp', p.max_hp + 250), p.heal(250))),
        ("B47", "⭐ Golpe de Mil Mundos", "Ataque", "Rara", "+70 daño directo al arma.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 70)),
        ("B48", "⭐ Furia de los Dioses Antiguos", "Poder", "Rara", "+50% daño de ataque total.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.50)),
        ("B49", "⭐ Cólera Radiante de Odín", "Habilidad", "Rara", "Desata la Magia de Luz Celestial y sana 200 HP.", lambda p: p.heal(200), "Luz"),
        ("B50", "⭐ Apocalipsis Bárbaro", "Poder", "Rara", "+40% Daño, +25% Velocidad y +8 HP robo de vida.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.40), setattr(p, 'speed_mult', p.speed_mult + 0.25), setattr(p, 'life_steal', p.life_steal + 8.0))),
    ]
    for row in b_data:
        cid, name, cat, rar, desc, fn = row[:6]
        elem = row[6] if len(row) > 6 else None
        cards.append(CharacterCard(cid, c, name, cat, rar, desc, fn, elem))
    return cards


def _build_paladin_deck() -> List[CharacterCard]:
    cards = []
    c = "paladin"
    p_data = [
        ("P01", "Bendición del Sol", "Habilidad", "Común", "+80 HP Máximos y regeneración pasiva +3 HP/2s.", lambda p: (setattr(p, 'max_hp', p.max_hp + 80), p.heal(80), setattr(p, 'passive_regen', p.passive_regen + 3.0))),
        ("P02", "Juicio Recto", "Ataque", "Común", "+14 daño fijo a la maza sagrada.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 14)),
        ("P03", "Escudo Celestial", "Defensa", "Común", "Mitiga un 8% adicional de todo el daño.", lambda p: setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.08))),
        ("P04", "Aura de Paz", "Defensa", "Común", "Restaura 180 HP inmediatamente.", lambda p: p.heal(180)),
        ("P05", "Onda de Penitencia", "Ataque", "Común", "+16% daño total de combate.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.16)),
        ("P06", "Maza Consagrada", "Ataque", "Común", "+18 daño al arma sagrada.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 18)),
        ("P07", "Martirio Sagrado", "Poder", "Común", "+100 HP máximos y +10% daño.", lambda p: (setattr(p, 'max_hp', p.max_hp + 100), p.heal(100), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.10))),
        ("P08", "Luz Eterna", "Habilidad", "Común", "Regeneración pasiva +4 HP cada 2 segundos.", lambda p: setattr(p, 'passive_regen', p.passive_regen + 4.0)),
        ("P09", "Pacto Sagrado", "Defensa", "Común", "+120 HP máximos y cura 80 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 120), p.heal(80))),
        ("P10", "Fortaleza Divina", "Defensa", "Común", "Reduce daño en 6% y añade 50 HP.", lambda p: (setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.06)), setattr(p, 'max_hp', p.max_hp + 50), p.heal(50))),
        ("P11", "Gracia Divina", "Habilidad", "Común", "+8% velocidad y cura 100 HP.", lambda p: (setattr(p, 'speed_mult', p.speed_mult + 0.08), p.heal(100))),
        ("P12", "Castigo Celestial", "Ataque", "Común", "+20% daño a la maza.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.20)),
        ("P13", "Escudo Radiante", "Defensa", "Común", "Mitiga un 7% de daño y añade 60 HP.", lambda p: (setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.07)), setattr(p, 'max_hp', p.max_hp + 60), p.heal(60))),
        ("P14", "Toque Sanador", "Habilidad", "Común", "Restaura 250 HP de salud.", lambda p: p.heal(250)),
        ("P15", "Cólera de la Fe", "Ataque", "Común", "+22 daño fijo de maza.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 22)),
        ("P16", "Alabanza Solar", "Poder", "Común", "+15% daño y regenera +3 HP/2s.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.15), setattr(p, 'passive_regen', p.passive_regen + 3.0))),
        ("P17", "Armadura Sagrada", "Defensa", "Común", "+140 HP máximos.", lambda p: (setattr(p, 'max_hp', p.max_hp + 140), p.heal(100))),
        ("P18", "Protección Angelical", "Defensa", "Común", "Reduce todo el daño en 9%.", lambda p: setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.09))),
        ("P19", "Rayo Purificador", "Ataque", "Común", "+25% daño de maza.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.25)),
        ("P20", "Pacto con el Fuego Divino", "Habilidad", "Común", "Imbuye la maza con Magia de Fuego.", None, "Fuego"),
        # Poco Comunes (20)
        ("P21", "Baluarte Inquebrantable", "Defensa", "Poco Común", "+200 HP Máximos y 12% mitigación.", lambda p: (setattr(p, 'max_hp', p.max_hp + 200), p.heal(200), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.12)))),
        ("P22", "Maza del Arconte", "Ataque", "Poco Común", "+35 daño de maza y reduce cooldown.", lambda p: (setattr(p, 'weapon_damage', p.weapon_damage + 35), setattr(p, 'attack_cooldown_max', max(0.18, p.attack_cooldown_max - 0.04)))),
        ("P23", "Fervor Sagrado", "Poder", "Poco Común", "Regeneración pasiva +6 HP/2s y +20% daño.", lambda p: (setattr(p, 'passive_regen', p.passive_regen + 6.0), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.20))),
        ("P24", "Cruzada Implacable", "Ataque", "Poco Común", "+30% daño total de combate.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.30)),
        ("P25", "Sanación Milagrosa", "Habilidad", "Poco Común", "Cura 350 HP y añade 100 HP máx.", lambda p: (setattr(p, 'max_hp', p.max_hp + 100), p.heal(350))),
        ("P26", "Sentencia de Acero", "Ataque", "Poco Común", "+40 daño fijo suplementario.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 40)),
        ("P27", "Vigilia Eterna", "Defensa", "Poco Común", "Mitiga un 14% de daño y añade 120 HP.", lambda p: (setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.14)), setattr(p, 'max_hp', p.max_hp + 120), p.heal(120))),
        ("P28", "Bendición de la Tierra", "Habilidad", "Poco Común", "Activa Magia de Tierra en impactos.", None, "Tierra"),
        ("P29", "Aura del Alba", "Poder", "Poco Común", "Regenera +8 HP/2s y +10% velocidad.", lambda p: (setattr(p, 'passive_regen', p.passive_regen + 8.0), setattr(p, 'speed_mult', p.speed_mult + 0.10))),
        ("P30", "Misericordia Templaria", "Defensa", "Poco Común", "Cura el 50% de la vida máxima.", lambda p: p.heal(p.max_hp * 0.5)),
        ("P31", "Golpe Justiciero", "Ataque", "Poco Común", "+35% daño de maza.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.35)),
        ("P32", "Escudo del Bastión", "Defensa", "Poco Común", "+220 HP y 10% reducción de daño.", lambda p: (setattr(p, 'max_hp', p.max_hp + 220), p.heal(150), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.10)))),
        ("P33", "Runa del Rayo Divino", "Habilidad", "Poco Común", "Desata Magia de Trueno santificado.", None, "Trueno"),
        ("P34", "Purificación Total", "Habilidad", "Poco Común", "Cura 400 HP de salud.", lambda p: p.heal(400)),
        ("P35", "Voto de Castidad", "Defensa", "Poco Común", "+160 HP y +15% mitigación de daño.", lambda p: (setattr(p, 'max_hp', p.max_hp + 160), p.heal(160), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.15)))),
        ("P36", "Fuerza de la Fe", "Poder", "Poco Común", "+28% daño y regenera +5 HP/2s.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.28), setattr(p, 'passive_regen', p.passive_regen + 5.0))),
        ("P37", "Luz Restauradora", "Habilidad", "Poco Común", "+150 HP máx y cura 200 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 150), p.heal(200))),
        ("P38", "Maza de los Justos", "Ataque", "Poco Común", "+42 daño de maza.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 42)),
        ("P39", "Armadura de Luz", "Defensa", "Poco Común", "+250 HP máximos.", lambda p: (setattr(p, 'max_hp', p.max_hp + 250), p.heal(200))),
        ("P40", "Sello de Luz Solar", "Poder", "Poco Común", "+30% daño de ataque.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.30)),
        # Raras / Doradas (10)
        ("P41", "⭐ Juicio Divino Celestial", "Poder", "Rara", "Otorga la sagrada Magia de Luz Celestial y +35% daño.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.35), p.heal(200)), "Luz"),
        ("P42", "⭐ Corona del Rey Sol", "Defensa", "Rara", "+350 HP Máximos y regeneración pasiva +15 HP/2s.", lambda p: (setattr(p, 'max_hp', p.max_hp + 350), p.heal(350), setattr(p, 'passive_regen', p.passive_regen + 15.0))),
        ("P43", "⭐ Martillo del Fin de los Tiempos", "Ataque", "Rara", "+65 daño directo de maza y +30% daño.", lambda p: (setattr(p, 'weapon_damage', p.weapon_damage + 65), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.30))),
        ("P44", "⭐ Fortaleza Inviolable de Dios", "Defensa", "Rara", "Mitiga un 25% de todo el daño y añade 300 HP.", lambda p: (setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.25)), setattr(p, 'max_hp', p.max_hp + 300), p.heal(300))),
        ("P45", "⭐ Bendición de la Trinidad", "Poder", "Rara", "+35% Daño, +200 HP y cura el 100% de la vida.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.35), setattr(p, 'max_hp', p.max_hp + 200), p.heal(p.max_hp))),
        ("P46", "⭐ Cólera del Serafín", "Ataque", "Rara", "+50% daño de maza sagrada.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.50)),
        ("P47", "⭐ Juicio de Sombras y Luz", "Habilidad", "Rara", "Otorga Magia de Oscuridad Abisal y +40% daño.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.40), "Oscuridad"),
        ("P48", "⭐ Milagro de Resurrección", "Defensa", "Rara", "+400 HP máximos y sana 400 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 400), p.heal(400))),
        ("P49", "⭐ Maza de los Doce Apóstoles", "Ataque", "Rara", "+70 daño de arma y -25% cooldown de ataque.", lambda p: (setattr(p, 'weapon_damage', p.weapon_damage + 70), setattr(p, 'attack_cooldown_max', max(0.16, p.attack_cooldown_max * 0.75)))),
        ("P50", "⭐ Avatar de la Luz Sagrada", "Poder", "Rara", "+300 HP, +40% Daño, 20% Mitigación y +12 HP/2s.", lambda p: (setattr(p, 'max_hp', p.max_hp + 300), p.heal(300), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.40), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.20)), setattr(p, 'passive_regen', p.passive_regen + 12.0))),
    ]
    for row in p_data:
        cid, name, cat, rar, desc, fn = row[:6]
        elem = row[6] if len(row) > 6 else None
        cards.append(CharacterCard(cid, c, name, cat, rar, desc, fn, elem))
    return cards


def _build_rogue_deck() -> List[CharacterCard]:
    cards = []
    c = "rogue"
    r_data = [
        ("R01", "Veneno Concentrado", "Habilidad", "Común", "+10% crítico y +10% daño.", lambda p: (setattr(p, 'crit_chance', min(0.95, p.crit_chance + 0.10)), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.10))),
        ("R02", "Estocada Furtiva", "Ataque", "Común", "+12 daño de dagas.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 12)),
        ("R03", "Paso de Sombras", "Defensa", "Común", "+15% velocidad de movimiento.", lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.15)),
        ("R04", "Reflejos Fantasma", "Habilidad", "Común", "Reduce el cooldown del Dash en 0.08s.", lambda p: setattr(p, 'dash_cooldown_max', max(0.20, getattr(p, 'dash_cooldown_max', 0.45) - 0.08))),
        ("R05", "Doble Filo", "Ataque", "Común", "+15% daño y reduce cooldown de dagas a 0.18s.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.15), setattr(p, 'attack_cooldown_max', max(0.12, p.attack_cooldown_max - 0.02)))),
        ("R06", "Frasco Tóxico", "Habilidad", "Común", "+8% crítico y +80 HP.", lambda p: (setattr(p, 'crit_chance', min(0.95, p.crit_chance + 0.08)), setattr(p, 'max_hp', p.max_hp + 80), p.heal(80))),
        ("R07", "Punto Vital", "Poder", "Común", "Multiplicador de crítico aumenta a x2.4.", lambda p: setattr(p, 'crit_multiplier', getattr(p, 'crit_multiplier', 2.2) + 0.2)),
        ("R08", "Acrobacia Mortal", "Defensa", "Común", "+12% velocidad y +60 HP.", lambda p: (setattr(p, 'speed_mult', p.speed_mult + 0.12), setattr(p, 'max_hp', p.max_hp + 60), p.heal(60))),
        ("R09", "Corte Preciso", "Ataque", "Común", "+15 daño fijo de dagas.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 15)),
        ("R10", "Hoja Asesina", "Ataque", "Común", "+18% daño de combate.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.18)),
        ("R11", "Toxina Pariparia", "Habilidad", "Común", "+10% crítico.", lambda p: setattr(p, 'crit_chance', min(0.95, p.crit_chance + 0.10))),
        ("R12", "Daga Oculta", "Ataque", "Común", "+14 daño suplementario.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 14)),
        ("R13", "Bruma Tóxica", "Habilidad", "Común", "Imbuye dagas con Magia de Naturaleza.", None, "Naturaleza"),
        ("R14", "Agilidad Felina", "Defensa", "Común", "+18% velocidad de carrera.", lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.18)),
        ("R15", "Celeridad Mortal", "Poder", "Común", "+15% daño y +10% velocidad.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.15), setattr(p, 'speed_mult', p.speed_mult + 0.10))),
        ("R16", "Veneno de Escorpión", "Habilidad", "Común", "+12% crítico y cura 70 HP.", lambda p: (setattr(p, 'crit_chance', min(0.95, p.crit_chance + 0.12)), p.heal(70))),
        ("R17", "Capa de Sombras", "Defensa", "Común", "Mitiga un 8% de daño y +70 HP.", lambda p: (setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.08)), setattr(p, 'max_hp', p.max_hp + 70), p.heal(70))),
        ("R18", "Tajo Certero", "Ataque", "Común", "+18 daño de dagas.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 18)),
        ("R19", "Evasión Rápida", "Defensa", "Común", "+14% velocidad de movimiento.", lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.14)),
        ("R20", "Pacto del Viento Veloz", "Habilidad", "Común", "Imbuye cortes con Magia de Viento cortante.", None, "Viento"),
        # Poco Comunes (20)
        ("R21", "Danza de Dagas", "Ataque", "Poco Común", "+25 daño de dagas y -0.03s cooldown.", lambda p: (setattr(p, 'weapon_damage', p.weapon_damage + 25), setattr(p, 'attack_cooldown_max', max(0.10, p.attack_cooldown_max - 0.03)))),
        ("R22", "Veneno Fulminante", "Poder", "Poco Común", "+15% crítico y multiplicador sube a x2.6.", lambda p: (setattr(p, 'crit_chance', min(0.95, p.crit_chance + 0.15)), setattr(p, 'crit_multiplier', getattr(p, 'crit_multiplier', 2.2) + 0.4))),
        ("R23", "Golpe en la Nuca", "Ataque", "Poco Común", "+30% daño de ataque crítico.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.30)),
        ("R24", "Sombra Fugaz", "Defensa", "Poco Común", "Dash se recarga en 0.30s y otorga +20% velocidad.", lambda p: (setattr(p, 'dash_cooldown_max', 0.30), setattr(p, 'speed_mult', p.speed_mult + 0.20))),
        ("R25", "Hemorragia", "Ataque", "Poco Común", "+32 daño fijo al arma.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 32)),
        ("R26", "Toxina Corrosiva", "Habilidad", "Poco Común", "+20% daño y +10% crítico.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.20), setattr(p, 'crit_chance', min(0.95, p.crit_chance + 0.10)))),
        ("R27", "Lluvia de Agujas", "Ataque", "Poco Común", "+28% daño total de combate.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.28)),
        ("R28", "Filo Venenoso", "Habilidad", "Poco Común", "+15% crítico y cura 120 HP.", lambda p: (setattr(p, 'crit_chance', min(0.95, p.crit_chance + 0.15)), p.heal(120))),
        ("R29", "Punción Renal", "Ataque", "Poco Común", "+35 daño de dagas.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 35)),
        ("R30", "Rayo Asesino", "Habilidad", "Poco Común", "Imbuye dagas con Magia de Trueno.", None, "Trueno"),
        ("R31", "Asalto Rápido", "Ataque", "Poco Común", "+25% velocidad y +20% daño.", lambda p: (setattr(p, 'speed_mult', p.speed_mult + 0.25), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.20))),
        ("R32", "Navaja de Asesino", "Ataque", "Poco Común", "+38 daño de arma.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 38)),
        ("R33", "Sombras Sigilosas", "Defensa", "Poco Común", "+150 HP y 12% mitigación de daño.", lambda p: (setattr(p, 'max_hp', p.max_hp + 150), p.heal(150), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.12)))),
        ("R34", "Veneno Negro", "Poder", "Poco Común", "+18% crítico y +22% daño.", lambda p: (setattr(p, 'crit_chance', min(0.95, p.crit_chance + 0.18)), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.22))),
        ("R35", "Embosca Letal", "Ataque", "Poco Común", "+35% daño total de golpe.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.35)),
        ("R36", "Corte al Cuello", "Ataque", "Poco Común", "+42 daño de arma.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 42)),
        ("R37", "Veneno Paralizante", "Habilidad", "Poco Común", "+15% crítico y +15% velocidad.", lambda p: (setattr(p, 'crit_chance', min(0.95, p.crit_chance + 0.15)), setattr(p, 'speed_mult', p.speed_mult + 0.15))),
        ("R38", "Doble Tajo Mortal", "Ataque", "Poco Común", "+40 daño de dagas.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 40)),
        ("R39", "Fuga Rápida", "Defensa", "Poco Común", "+30% velocidad y cura 150 HP.", lambda p: (setattr(p, 'speed_mult', p.speed_mult + 0.30), p.heal(150))),
        ("R40", "Toxina Mortal", "Poder", "Poco Común", "Crítico aumenta a x2.8 de daño.", lambda p: setattr(p, 'crit_multiplier', getattr(p, 'crit_multiplier', 2.2) + 0.6)),
        # Raras / Doradas (10)
        ("R41", "⭐ Danza de las Mil Sombras", "Poder", "Rara", "+25% Crítico, multiplicador x3.2 y +30% velocidad.", lambda p: (setattr(p, 'crit_chance', min(0.95, p.crit_chance + 0.25)), setattr(p, 'crit_multiplier', 3.2), setattr(p, 'speed_mult', p.speed_mult + 0.30))),
        ("R42", "⭐ Veneno del Rey de la Noche", "Habilidad", "Rara", "Desata la Magia de Oscuridad Abisal y +40% daño.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.40), "Oscuridad"),
        ("R43", "⭐ Dagas Fantasma de la Corona", "Ataque", "Rara", "+55 daño al arma y cadencia de ataque a 0.12s.", lambda p: (setattr(p, 'weapon_damage', p.weapon_damage + 55), setattr(p, 'attack_cooldown_max', 0.12))),
        ("R44", "⭐ Sentencia del Verdugo", "Ataque", "Rara", "+60% daño en todos los ataques.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.60)),
        ("R45", "⭐ Velo de la Muerte Silenciosa", "Defensa", "Rara", "+250 HP, 15% Mitigación y Dash recarga en 0.25s.", lambda p: (setattr(p, 'max_hp', p.max_hp + 250), p.heal(250), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.15)), setattr(p, 'dash_cooldown_max', 0.25))),
        ("R46", "⭐ Filo de Luz Celestial", "Habilidad", "Rara", "Otorga la Magia de Luz Celestial y sana 200 HP.", lambda p: p.heal(200), "Luz"),
        ("R47", "⭐ Loto de la Muerte Negra", "Poder", "Rara", "+30% crítico y cura el 100% de la salud.", lambda p: (setattr(p, 'crit_chance', min(0.95, p.crit_chance + 0.30)), p.heal(p.max_hp))),
        ("R48", "⭐ Torbellino de Dagas Gemelas", "Ataque", "Rara", "+65 daño directo de dagas.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 65)),
        ("R49", "⭐ Acróbata del Más Allá", "Defensa", "Rara", "+40% velocidad y Dash invulnerable por más tiempo.", lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.40)),
        ("R50", "⭐ Maestro Supremo de Asesinos", "Poder", "Rara", "+30% Crítico, x3.0 Multiplicador, +45% Daño y +25% Vel.", lambda p: (setattr(p, 'crit_chance', min(0.95, p.crit_chance + 0.30)), setattr(p, 'crit_multiplier', 3.0), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.45), setattr(p, 'speed_mult', p.speed_mult + 0.25))),
    ]
    for row in r_data:
        cid, name, cat, rar, desc, fn = row[:6]
        elem = row[6] if len(row) > 6 else None
        cards.append(CharacterCard(cid, c, name, cat, rar, desc, fn, elem))
    return cards


def _build_mage_deck() -> List[CharacterCard]:
    cards = []
    c = "mage"
    m_data = [
        ("M01", "Sobrecarga de Maná", "Habilidad", "Común", "+100 Maná Máximo y cura 50 MP.", lambda p: (setattr(p, 'max_mana', p.max_mana + 100), p.restore_mana(100))),
        ("M02", "Eco Elemental", "Poder", "Común", "+15% daño a todos los hechizos mágicos.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.15)),
        ("M03", "Núcleo Arcano", "Poder", "Común", "Regeneración de maná pasiva +5 MP/s.", lambda p: setattr(p, 'passive_mana_regen', p.passive_mana_regen + 5.0)),
        ("M04", "Ráfaga de Éter", "Ataque", "Común", "+18% daño de dardo arcano.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.18)),
        ("M05", "Canalizador Cristalino", "Habilidad", "Común", "+80 Maná Máximo y +10% daño mágico.", lambda p: (setattr(p, 'max_mana', p.max_mana + 80), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.10))),
        ("M06", "Chispa Primordial", "Ataque", "Común", "Dardo Arcano recarga +5 MP extra al impactar.", lambda p: setattr(p, 'passive_mana_regen', p.passive_mana_regen + 3.0)),
        ("M07", "Mente Brillante", "Habilidad", "Común", "Regeneración de maná pasiva +6 MP/s.", lambda p: setattr(p, 'passive_mana_regen', p.passive_mana_regen + 6.0)),
        ("M08", "Resonancia Arcana", "Poder", "Común", "+16% daño elemental.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.16)),
        ("M09", "Dardo Fulminante", "Ataque", "Común", "Dardo básico dispara un 15% más rápido.", lambda p: setattr(p, 'basic_shot_cooldown_max', max(0.12, p.basic_shot_cooldown_max - 0.04))),
        ("M10", "Prisma de Maná", "Defensa", "Común", "+80 HP y +80 MP máximos.", lambda p: (setattr(p, 'max_hp', p.max_hp + 80), p.heal(80), setattr(p, 'max_mana', p.max_mana + 80), p.restore_mana(80))),
        ("M11", "Ignición de Fuego", "Habilidad", "Común", "Refuerza Magia de Fuego y añade 50 MP.", lambda p: p.restore_mana(50), "Fuego"),
        ("M12", "Manto de Hielo", "Defensa", "Común", "Mitiga un 8% de daño y otorga Magia de Agua.", lambda p: setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.08)), "Agua"),
        ("M13", "Tormenta Estática", "Habilidad", "Común", "Refuerza Magia de Trueno y +12% daño.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.12), "Trueno"),
        ("M14", "Vórtice Elemental", "Ataque", "Común", "Otorga Magia de Viento cortante.", None, "Viento"),
        ("M15", "Sifón de Maná", "Habilidad", "Común", "Restaura 200 MP de inmediato.", lambda p: p.restore_mana(200)),
        ("M16", "Flujo Arcano", "Poder", "Común", "Regenera +5 MP/s y +8% velocidad.", lambda p: (setattr(p, 'passive_mana_regen', p.passive_mana_regen + 5.0), setattr(p, 'speed_mult', p.speed_mult + 0.08))),
        ("M17", "Orbe de Éter", "Habilidad", "Común", "+120 Maná Máximo.", lambda p: (setattr(p, 'max_mana', p.max_mana + 120), p.restore_mana(120))),
        ("M18", "Foco Mágico", "Poder", "Común", "+20% daño mágico.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.20)),
        ("M19", "Estallido Arcano", "Ataque", "Común", "+22% daño de proyectiles mágicos.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.22)),
        ("M20", "Zarzas de Gaia", "Habilidad", "Común", "Otorga Magia de Naturaleza.", None, "Naturaleza"),
        # Poco Comunes (20)
        ("M21", "Sobrecarga de Éter", "Poder", "Poco Común", "+25% daño mágico y +150 MP máx.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.25), setattr(p, 'max_mana', p.max_mana + 150), p.restore_mana(150))),
        ("M22", "Maná Infinito de Archicanciller", "Poder", "Poco Común", "Regeneración pasiva +10 MP/s.", lambda p: setattr(p, 'passive_mana_regen', p.passive_mana_regen + 10.0)),
        ("M23", "Escudo de Maná", "Defensa", "Poco Común", "Mitiga 12% de daño y +100 HP.", lambda p: (setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.12)), setattr(p, 'max_hp', p.max_hp + 100), p.heal(100))),
        ("M24", "Ráfaga Quíntuple", "Ataque", "Poco Común", "+30% daño de hechizos.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.30)),
        ("M25", "Batería de Éter de Cristal", "Habilidad", "Poco Común", "+200 Maná Máximo y cura 200 MP.", lambda p: (setattr(p, 'max_mana', p.max_mana + 200), p.restore_mana(200))),
        ("M26", "Catalizador Rúnico", "Poder", "Poco Común", "+28% daño y regenera +6 MP/s.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.28), setattr(p, 'passive_mana_regen', p.passive_mana_regen + 6.0))),
        ("M27", "Transmutación de Vapor", "Habilidad", "Poco Común", "Desata Magia de Vapor a presión.", None, "Vapor (Steampunk)"),
        ("M28", "Convergencia Arcana", "Ataque", "Poco Común", "+35% daño mágico total.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.35)),
        ("M29", "Descarga de Vacío", "Ataque", "Poco Común", "+32% daño de proyectiles.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.32)),
        ("M30", "Maelstrom de Hojas", "Habilidad", "Poco Común", "Desata Magia de Metal cortante.", None, "Metal"),
        ("M31", "Pulso de Éter Puro", "Poder", "Poco Común", "Regenera +8 MP/s y +12% velocidad.", lambda p: (setattr(p, 'passive_mana_regen', p.passive_mana_regen + 8.0), setattr(p, 'speed_mult', p.speed_mult + 0.12))),
        ("M32", "Concentración Pura", "Habilidad", "Poco Común", "Restaura 350 MP de inmediato.", lambda p: p.restore_mana(350)),
        ("M33", "Bucle de Maná", "Poder", "Poco Común", "+150 MP máx y +8 MP/s regeneración.", lambda p: (setattr(p, 'max_mana', p.max_mana + 150), setattr(p, 'passive_mana_regen', p.passive_mana_regen + 8.0))),
        ("M34", "Dominio Arcano", "Poder", "Poco Común", "+30% daño elemental.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.30)),
        ("M35", "Runa de Lava Ardiente", "Habilidad", "Poco Común", "Magia de Fuego y +15% daño.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.15), "Fuego"),
        ("M36", "Sello Arcano Protector", "Defensa", "Poco Común", "+150 HP y 10% mitigación de daño.", lambda p: (setattr(p, 'max_hp', p.max_hp + 150), p.heal(150), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.10)))),
        ("M37", "Expansión Mágica", "Poder", "Poco Común", "+200 MP Máximos.", lambda p: (setattr(p, 'max_mana', p.max_mana + 200), p.restore_mana(200))),
        ("M38", "Rayo Concentrado", "Ataque", "Poco Común", "+38% daño a distancia.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.38)),
        ("M39", "Cascada de Éter", "Habilidad", "Poco Común", "+10 MP/s regeneración de maná.", lambda p: setattr(p, 'passive_mana_regen', p.passive_mana_regen + 10.0)),
        ("M40", "Mente Despierta de Sabio", "Poder", "Poco Común", "+25% daño y +100 HP.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.25), setattr(p, 'max_hp', p.max_hp + 100), p.heal(100))),
        # Raras / Doradas (10)
        ("M41", "⭐ Singularidad Cósmica Abisal", "Poder", "Rara", "Desata la Magia de Oscuridad Abisal y +40% daño.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.40), "Oscuridad"),
        ("M42", "⭐ Estrella de la Creación Sagrada", "Habilidad", "Rara", "Desata la Magia de Luz Celestial y sana 250 HP.", lambda p: p.heal(250), "Luz"),
        ("M43", "⭐ Maná Infinito Primigenio", "Poder", "Rara", "+300 MP Máximo y +20 MP/s de regeneración continua.", lambda p: (setattr(p, 'max_mana', p.max_mana + 300), p.restore_mana(300), setattr(p, 'passive_mana_regen', p.passive_mana_regen + 20.0))),
        ("M44", "⭐ Omnisciencia Arcana", "Poder", "Rara", "+60% daño a todos los hechizos mágicos.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.60)),
        ("M45", "⭐ Báculo del Archicanciller", "Ataque", "Rara", "Dardo Arcano hace +50% daño y recarga +25 MP por impacto.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.50)),
        ("M46", "⭐ Tormenta de los Mil Soles", "Habilidad", "Rara", "Combina Magia de Fuego y Magia de Trueno con +45% daño.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.45), "Fuego"),
        ("M47", "⭐ Manto de Invisibilidad de Éter", "Defensa", "Rara", "+200 HP, 15% Mitigación y Dash recarga en 0.35s.", lambda p: (setattr(p, 'max_hp', p.max_hp + 200), p.heal(200), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.15)), setattr(p, 'dash_cooldown_max', 0.35))),
        ("M48", "⭐ Fuente Eterna de la Juventud", "Habilidad", "Rara", "Restaura el 100% de la Vida y del Maná.", lambda p: (p.heal(p.max_hp), p.restore_mana(p.max_mana))),
        ("M49", "⭐ Prisma de los Elementos Supremos", "Poder", "Rara", "+50% daño elemental y +15% velocidad.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.50), setattr(p, 'speed_mult', p.speed_mult + 0.15))),
        ("M50", "⭐ Apoteosis Arcana", "Poder", "Rara", "+400 MP, +50% Daño, +15 MP/s regeneración y +200 HP.", lambda p: (setattr(p, 'max_mana', p.max_mana + 400), p.restore_mana(400), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.50), setattr(p, 'passive_mana_regen', p.passive_mana_regen + 15.0), setattr(p, 'max_hp', p.max_hp + 200), p.heal(200))),
    ]
    for row in m_data:
        cid, name, cat, rar, desc, fn = row[:6]
        elem = row[6] if len(row) > 6 else None
        cards.append(CharacterCard(cid, c, name, cat, rar, desc, fn, elem))
    return cards


def _build_hunter_deck() -> List[CharacterCard]:
    cards = []
    c = "hunter"
    h_data = [
        ("H01", "Saeta Perforante", "Ataque", "Común", "+16 daño fijo a la ballesta.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 16)),
        ("H02", "Ojo de Halcón", "Poder", "Común", "+10% crítico y +10% daño.", lambda p: (setattr(p, 'crit_chance', min(0.95, p.crit_chance + 0.10)), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.10))),
        ("H03", "Trampa de Abrojos", "Habilidad", "Común", "+15% daño a distancia.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.15)),
        ("H04", "Perno de Fósforo", "Ataque", "Común", "+14 daño de saeta y activa Magia de Fuego.", None, "Fuego"),
        ("H05", "Disparo Rápido", "Ataque", "Común", "Reduce el cooldown de la ballesta en 0.04s.", lambda p: setattr(p, 'attack_cooldown_max', max(0.14, p.attack_cooldown_max - 0.04))),
        ("H06", "Tiro a la Cabeza", "Poder", "Común", "+12% crítico y multiplicador sube a x2.3.", lambda p: (setattr(p, 'crit_chance', min(0.95, p.crit_chance + 0.12)), setattr(p, 'crit_multiplier', getattr(p, 'crit_multiplier', 2.0) + 0.3))),
        ("H07", "Cuerda Reforzada", "Ataque", "Común", "+18 daño de ballesta.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 18)),
        ("H08", "Camuflaje de Bosque", "Defensa", "Común", "+15% velocidad y +60 HP.", lambda p: (setattr(p, 'speed_mult', p.speed_mult + 0.15), setattr(p, 'max_hp', p.max_hp + 60), p.heal(60))),
        ("H09", "Recarga Rápida", "Habilidad", "Común", "+12% velocidad y acelera disparo.", lambda p: (setattr(p, 'speed_mult', p.speed_mult + 0.12), setattr(p, 'attack_cooldown_max', max(0.14, p.attack_cooldown_max - 0.03)))),
        ("H10", "Flecha Pesada", "Ataque", "Común", "+20 daño directo de saeta.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 20)),
        ("H11", "Disparo Doble", "Ataque", "Común", "+18% daño de proyectil.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.18)),
        ("H12", "Tiro Parabólico", "Ataque", "Común", "+15 daño al arma.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 15)),
        ("H13", "Virote de Espinas", "Habilidad", "Común", "Otorga Magia de Naturaleza.", None, "Naturaleza"),
        ("H14", "Puntería Fina", "Poder", "Común", "+15% daño y +8% crítico.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.15), setattr(p, 'crit_chance', min(0.95, p.crit_chance + 0.08)))),
        ("H15", "Red de Contención", "Defensa", "Común", "Mitiga un 8% de daño y +70 HP.", lambda p: (setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.08)), setattr(p, 'max_hp', p.max_hp + 70), p.heal(70))),
        ("H16", "Saeta Incendiaria", "Ataque", "Común", "+22% daño de saeta.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.22)),
        ("H17", "Flecha de Acero Templado", "Ataque", "Común", "+22 daño de saeta.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 22)),
        ("H18", "Emplumado Ágil", "Defensa", "Común", "+16% velocidad de movimiento.", lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.16)),
        ("H19", "Caza Mayor", "Poder", "Común", "+20% daño a distancia.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.20)),
        ("H20", "Saeta de Rayo", "Habilidad", "Común", "Otorga Magia de Trueno a las saetas.", None, "Trueno"),
        # Poco Comunes (20)
        ("H21", "Tiro de Francotirador", "Ataque", "Poco Común", "+35 daño de ballesta y +15% crítico.", lambda p: (setattr(p, 'weapon_damage', p.weapon_damage + 35), setattr(p, 'crit_chance', min(0.95, p.crit_chance + 0.15)))),
        ("H22", "Perno Explosivo", "Ataque", "Poco Común", "+30% daño de saeta.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.30)),
        ("H23", "Disparo Penetrante", "Poder", "Poco Común", "+32% daño y saetas atraviesan más enemigos.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.32)),
        ("H24", "Miras de Precisión", "Poder", "Poco Común", "+20% crítico y multiplicador x2.5.", lambda p: (setattr(p, 'crit_chance', min(0.95, p.crit_chance + 0.20)), setattr(p, 'crit_multiplier', 2.5))),
        ("H25", "Ballesta Mecánica Pesada", "Ataque", "Poco Común", "+40 daño de arma.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 40)),
        ("H26", "Trampa de Osos", "Defensa", "Poco Común", "+150 HP y 10% mitigación de daño.", lambda p: (setattr(p, 'max_hp', p.max_hp + 150), p.heal(150), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.10)))),
        ("H27", "Virote de Caza Mayor", "Ataque", "Poco Común", "+35% daño a distancia.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.35)),
        ("H28", "Instinto de Supervivencia", "Defensa", "Poco Común", "Cura 250 HP y +10% velocidad.", lambda p: (p.heal(250), setattr(p, 'speed_mult', p.speed_mult + 0.10))),
        ("H29", "Disparo Certero", "Ataque", "Poco Común", "+42 daño al arma.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 42)),
        ("H30", "Virote de Viento Cortante", "Habilidad", "Poco Común", "Otorga Magia de Viento a los proyectiles.", None, "Viento"),
        ("H31", "Puntería Milimétrica", "Poder", "Poco Común", "+25% crítico y +15% daño.", lambda p: (setattr(p, 'crit_chance', min(0.95, p.crit_chance + 0.25)), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.15))),
        ("H32", "Carcaj Reforzado", "Habilidad", "Poco Común", "Acelera la cadencia y +20% velocidad.", lambda p: (setattr(p, 'attack_cooldown_max', max(0.12, p.attack_cooldown_max - 0.05)), setattr(p, 'speed_mult', p.speed_mult + 0.20))),
        ("H33", "Perforador de Blindajes", "Ataque", "Poco Común", "+38% daño directo de proyectiles.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.38)),
        ("H34", "Tiro de Cazador Real", "Ataque", "Poco Común", "+45 daño fijo de saeta.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 45)),
        ("H35", "Disparo en Ráfaga", "Ataque", "Poco Común", "+30% daño de saeta y cura 100 HP.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.30), p.heal(100))),
        ("H36", "Saeta de Metal Giratorio", "Habilidad", "Poco Común", "Otorga Magia de Metal a los disparos.", None, "Metal"),
        ("H37", "Flecha Rompearmaduras", "Ataque", "Poco Común", "+48 daño de arma.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 48)),
        ("H38", "Cazador Furtivo", "Defensa", "Poco Común", "+180 HP y +20% velocidad.", lambda p: (setattr(p, 'max_hp', p.max_hp + 180), p.heal(180), setattr(p, 'speed_mult', p.speed_mult + 0.20))),
        ("H39", "Tiro a Quemarropa", "Ataque", "Poco Común", "+40% daño total.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.40)),
        ("H40", "Tiro de Alta Distancia", "Poder", "Poco Común", "+35% daño y +10% crítico.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.35), setattr(p, 'crit_chance', min(0.95, p.crit_chance + 0.10)))),
        # Raras / Doradas (10)
        ("H41", "⭐ Ballesta de los Reyes Antiguos", "Ataque", "Rara", "+65 daño de saeta y -30% cooldown de disparo.", lambda p: (setattr(p, 'weapon_damage', p.weapon_damage + 65), setattr(p, 'attack_cooldown_max', max(0.12, p.attack_cooldown_max * 0.70)))),
        ("H42", "⭐ Saeta de la Oscuridad Abisal", "Habilidad", "Rara", "Desata Magia de Oscuridad Abisal y +40% daño.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.40), "Oscuridad"),
        ("H43", "⭐ Flecha del Juicio Sagrado", "Habilidad", "Rara", "Desata Magia de Luz Celestial y sana 200 HP.", lambda p: p.heal(200), "Luz"),
        ("H44", "⭐ Ojo de Águila Primigenio", "Poder", "Rara", "+30% Crítico con multiplicador demoledor x3.0.", lambda p: (setattr(p, 'crit_chance', min(0.95, p.crit_chance + 0.30)), setattr(p, 'crit_multiplier', 3.0))),
        ("H45", "⭐ Saeta del Trueno de Odín", "Ataque", "Rara", "+50% daño y saetas electrificadas.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.50)),
        ("H46", "⭐ Manto del Señor del Bosque", "Defensa", "Rara", "+250 HP, 15% Mitigación y +30% Velocidad.", lambda p: (setattr(p, 'max_hp', p.max_hp + 250), p.heal(250), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.15)), setattr(p, 'speed_mult', p.speed_mult + 0.30))),
        ("H47", "⭐ Lluvia de Saetas Devastadora", "Ataque", "Rara", "+70 daño directo de ballesta.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 70)),
        ("H48", "⭐ Cazador Legendario del Alba", "Poder", "Rara", "+45% Daño, +200 HP y cura el 100% de la vida.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.45), setattr(p, 'max_hp', p.max_hp + 200), p.heal(p.max_hp))),
        ("H49", "⭐ Perno Nuclear de Vapor", "Habilidad", "Rara", "Otorga Magia de Vapor y +35% daño.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.35), "Vapor (Steampunk)"),
        ("H50", "⭐ Francotirador Supremo", "Poder", "Rara", "+35% Crítico, x3.2 Daño crítico, +45% Daño y +25% Vel.", lambda p: (setattr(p, 'crit_chance', min(0.95, p.crit_chance + 0.35)), setattr(p, 'crit_multiplier', 3.2), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.45), setattr(p, 'speed_mult', p.speed_mult + 0.25))),
    ]
    for row in h_data:
        cid, name, cat, rar, desc, fn = row[:6]
        elem = row[6] if len(row) > 6 else None
        cards.append(CharacterCard(cid, c, name, cat, rar, desc, fn, elem))
    return cards


def _build_necromancer_deck() -> List[CharacterCard]:
    cards = []
    c = "necromancer"
    n_data = [
        ("N01", "Cosecha Eterna", "Poder", "Común", "Cosecha de Almas otorga +4 HP y +10 MP extra por baja.", lambda p: setattr(p, 'soul_harvest', True)),
        ("N02", "Toque de la Muerte", "Ataque", "Común", "+16 daño fijo a la guadaña espectral.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 16)),
        ("N03", "Maldición Debilitante", "Habilidad", "Común", "+15% daño y reduce daño recibido en 5%.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.15), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.05)))),
        ("N04", "Frasco de Almas", "Habilidad", "Común", "+100 Maná Máximo y cura 100 MP.", lambda p: (setattr(p, 'max_mana', p.max_mana + 100), p.restore_mana(100))),
        ("N05", "Drenaje Espectral", "Poder", "Común", "+3 HP robo de vida por corte.", lambda p: setattr(p, 'life_steal', p.life_steal + 3.0)),
        ("N06", "Miasma Púrpura", "Ataque", "Común", "+18% daño de guadaña.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.18)),
        ("N07", "Guadaña Voraz", "Ataque", "Común", "+18 daño de arma y cura 50 HP.", lambda p: (setattr(p, 'weapon_damage', p.weapon_damage + 18), p.heal(50))),
        ("N08", "Pacto de Tumba", "Defensa", "Común", "+90 HP Máximos y cura 90 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 90), p.heal(90))),
        ("N09", "Sombras Acechantes", "Defensa", "Común", "+14% velocidad de movimiento.", lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.14)),
        ("N10", "Rigor Mortis", "Defensa", "Común", "Mitiga un 8% de daño y +60 HP.", lambda p: (setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.08)), setattr(p, 'max_hp', p.max_hp + 60), p.heal(60))),
        ("N11", "Cosecha Sanguínea", "Poder", "Común", "Cosecha restaura +5 HP adicionales por baja.", lambda p: p.heal(50)),
        ("N12", "Maldición del Ocaso", "Ataque", "Común", "+20% daño de corte en media luna.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.20)),
        ("N13", "Festín de Almas", "Habilidad", "Común", "Restaura 200 MP de inmediato.", lambda p: p.restore_mana(200)),
        ("N14", "Guadaña Segadora", "Ataque", "Común", "+20 daño de guadaña.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 20)),
        ("N15", "Esencia Fantasma", "Defensa", "Común", "Reduce cooldown de dash en 0.08s.", lambda p: setattr(p, 'dash_cooldown_max', max(0.25, getattr(p, 'dash_cooldown_max', 0.95) - 0.08))),
        ("N16", "Pacto Oscuro", "Poder", "Común", "+22% daño pero -30 HP máx.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.22), setattr(p, 'max_hp', max(400.0, p.max_hp - 30)))),
        ("N17", "Fuego de Fatuo", "Habilidad", "Común", "Imbuye la guadaña con Magia de Fuego.", None, "Fuego"),
        ("N18", "Espíritu Vengativo", "Poder", "Común", "+10% crítico y +10% daño.", lambda p: (setattr(p, 'crit_chance', min(0.95, p.crit_chance + 0.10)), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.10))),
        ("N19", "Terror Abisal", "Ataque", "Común", "+22 daño fijo al arma.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 22)),
        ("N20", "Espinas de Ultratumba", "Habilidad", "Común", "Otorga Magia de Naturaleza venenosa.", None, "Naturaleza"),
        # Poco Comunes (20)
        ("N21", "Drenaje Masivo de Almas", "Poder", "Poco Común", "Cosecha otorga +8 HP y +25 MP extra por baja.", lambda p: (p.heal(100), p.restore_mana(100))),
        ("N22", "Huesos Malditos", "Defensa", "Poco Común", "+180 HP Máximos y 10% mitigación.", lambda p: (setattr(p, 'max_hp', p.max_hp + 180), p.heal(180), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.10)))),
        ("N23", "Toque Decrépito", "Ataque", "Poco Común", "+32% daño de guadaña.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.32)),
        ("N24", "Cosecha Oscura", "Poder", "Poco Común", "+4 HP robo de vida y +150 MP máx.", lambda p: (setattr(p, 'life_steal', p.life_steal + 4.0), setattr(p, 'max_mana', p.max_mana + 150), p.restore_mana(150))),
        ("N25", "Vórtice Sombrío", "Ataque", "Poco Común", "+35 daño al arma y reduce cooldown.", lambda p: (setattr(p, 'weapon_damage', p.weapon_damage + 35), setattr(p, 'attack_cooldown_max', max(0.18, p.attack_cooldown_max - 0.05)))),
        ("N26", "Guadaña de la Parca", "Ataque", "Poco Común", "+40 daño de arma.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 40)),
        ("N27", "Comunión con la Muerte", "Habilidad", "Poco Común", "Cura 300 HP y 200 MP.", lambda p: (p.heal(300), p.restore_mana(200))),
        ("N28", "Manto Espectral", "Defensa", "Poco Común", "+160 HP y +20% velocidad.", lambda p: (setattr(p, 'max_hp', p.max_hp + 160), p.heal(160), setattr(p, 'speed_mult', p.speed_mult + 0.20))),
        ("N29", "Aliento de Tumba", "Poder", "Poco Común", "+28% daño total de combate.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.28)),
        ("N30", "Rayo de la Tormenta Oscura", "Habilidad", "Poco Común", "Imbuye guadaña con Magia de Trueno.", None, "Trueno"),
        ("N31", "Condena Eterna", "Ataque", "Poco Común", "+35% daño de guadaña.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.35)),
        ("N32", "Pesadilla Viviente", "Poder", "Poco Común", "+15% crítico y +25% daño.", lambda p: (setattr(p, 'crit_chance', min(0.95, p.crit_chance + 0.15)), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.25))),
        ("N33", "Cosecha Rápida", "Habilidad", "Poco Común", "Acelera el corte de guadaña un 25%.", lambda p: setattr(p, 'attack_cooldown_max', max(0.16, p.attack_cooldown_max * 0.75))),
        ("N34", "Espectro Errante", "Defensa", "Poco Común", "+200 HP Máximos.", lambda p: (setattr(p, 'max_hp', p.max_hp + 200), p.heal(200))),
        ("N35", "Sombras Devoradoras", "Ataque", "Poco Común", "+44 daño fijo al arma.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 44)),
        ("N36", "Viento de las Catacumbas", "Habilidad", "Poco Común", "Otorga Magia de Viento cortante.", None, "Viento"),
        ("N37", "Fuerza Cadavérica", "Poder", "Poco Común", "+30% daño y 10% mitigación de daño.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.30), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.10)))),
        ("N38", "Guadaña Mortal", "Ataque", "Poco Común", "+48 daño de guadaña.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 48)),
        ("N39", "Abismo Sin Fin", "Poder", "Poco Común", "+200 MP máx y regenera +6 MP/s.", lambda p: (setattr(p, 'max_mana', p.max_mana + 200), setattr(p, 'passive_mana_regen', p.passive_mana_regen + 6.0))),
        ("N40", "Miasma Venenoso", "Poder", "Poco Común", "+35% daño total de combate.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.35)),
        # Raras / Doradas (10)
        ("N41", "⭐ Singularidad del Rey Liche", "Poder", "Rara", "Poder de Oscuridad Abisal al máximo y +45% daño.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.45), "Oscuridad"),
        ("N42", "⭐ Luz de la Tumba Celestial", "Habilidad", "Rara", "Otorga la Magia de Luz Celestial y sana 250 HP.", lambda p: p.heal(250), "Luz"),
        ("N43", "⭐ Guadaña de la Muerte Misma", "Ataque", "Rara", "+65 daño al arma y cosecha otorga +15 HP por muerte.", lambda p: (setattr(p, 'weapon_damage', p.weapon_damage + 65), p.heal(150))),
        ("N44", "⭐ Pacto con el Diablo", "Poder", "Rara", "+60% daño total de combate.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.60)),
        ("N45", "⭐ Resurrección Oscura", "Defensa", "Rara", "+350 HP Máximos y restaura el 100% de la vida.", lambda p: (setattr(p, 'max_hp', p.max_hp + 350), p.heal(p.max_hp))),
        ("N46", "⭐ Manto del Señor del Abismo", "Defensa", "Rara", "Mitiga un 20% de daño, +250 HP y +25% velocidad.", lambda p: (setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.20)), setattr(p, 'max_hp', p.max_hp + 250), p.heal(250), setattr(p, 'speed_mult', p.speed_mult + 0.25))),
        ("N47", "⭐ Cosecha del Fin de los Mundos", "Ataque", "Rara", "+70 daño directo de guadaña espectral.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 70)),
        ("N48", "⭐ Trascendencia Nigromántica", "Poder", "Rara", "+300 MP, +40% Daño, +8 HP robo de sangre.", lambda p: (setattr(p, 'max_mana', p.max_mana + 300), p.restore_mana(300), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.40), setattr(p, 'life_steal', p.life_steal + 8.0))),
        ("N49", "⭐ Invocador Supremo de Almas", "Habilidad", "Rara", "Restaura 400 HP y 400 MP al instante.", lambda p: (p.heal(400), p.restore_mana(400))),
        ("N50", "⭐ Segador Supremo del Apocalipsis", "Poder", "Rara", "+50% Daño, +250 HP, +200 MP, 15% Mitigación y +8 HP/muerte.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.50), setattr(p, 'max_hp', p.max_hp + 250), p.heal(250), setattr(p, 'max_mana', p.max_mana + 200), p.restore_mana(200), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.15)))),
    ]
    for row in n_data:
        cid, name, cat, rar, desc, fn = row[:6]
        elem = row[6] if len(row) > 6 else None
        cards.append(CharacterCard(cid, c, name, cat, rar, desc, fn, elem))
    return cards


def _build_runeknight_deck() -> List[CharacterCard]:
    cards = []
    c = "runeknight"
    rk_data = [
        ("RK01", "Corte Rúnico", "Ataque", "Común", "+16% daño de espadón.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.16)),
        ("RK02", "Temple de Zafiro", "Defensa", "Común", "+120 HP y +6% mitigación.", lambda p: (setattr(p, 'max_hp', p.max_hp + 120), p.heal(120), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.06)))),
        ("RK03", "Filo Ancestral", "Ataque", "Común", "+18 daño directo de espadón.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 18)),
        ("RK04", "Escudo de Éter Rúnico", "Defensa", "Común", "+100 MP y +80 HP.", lambda p: (setattr(p, 'max_mana', p.max_mana + 100), p.restore_mana(100), setattr(p, 'max_hp', p.max_hp + 80), p.heal(80))),
        ("RK05", "Tajo Estelar", "Ataque", "Común", "+20% daño de corte frontal.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.20)),
        ("RK06", "Guardia de Piedra Rúnica", "Defensa", "Común", "Mitiga un 8% de todo el daño.", lambda p: setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.08))),
        ("RK07", "Canalización Rúnica", "Habilidad", "Común", "+15 MP/s regeneración pasiva de maná.", lambda p: setattr(p, 'passive_mana_regen', p.passive_mana_regen + 15.0)),
        ("RK08", "Peso de Titán", "Ataque", "Común", "+22 daño fijo de espadón.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 22)),
        ("RK09", "Paso Acorazado", "Habilidad", "Común", "+12% velocidad de movimiento.", lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.12)),
        ("RK10", "Resonancia Metálica", "Poder", "Común", "+10% daño y +50 HP.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.10), setattr(p, 'max_hp', p.max_hp + 50), p.heal(50))),
        ("RK11", "Marca del Guardián", "Defensa", "Común", "+140 HP máximos y sana 100 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 140), p.heal(100))),
        ("RK12", "Estocada Sísmica", "Ataque", "Común", "+15% daño y +10 daño de arma.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.15), setattr(p, 'weapon_damage', p.weapon_damage + 10))),
        ("RK13", "Armadura Forjada en Runas", "Defensa", "Común", "+10% mitigación de daño.", lambda p: setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.10))),
        ("RK14", "Cadencia de Acero", "Habilidad", "Común", "Reduce cooldown de espadón en 0.05s.", lambda p: setattr(p, 'attack_cooldown_max', max(0.20, p.attack_cooldown_max - 0.05))),
        ("RK15", "Concentración Arcana", "Poder", "Común", "+150 MP de reserva.", lambda p: (setattr(p, 'max_mana', p.max_mana + 150), p.restore_mana(150))),
        ("RK16", "Golpe Rompearmaduras", "Ataque", "Común", "+25 daño fijo de espadón.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 25)),
        ("RK17", "Firmeza Inquebrantable", "Defensa", "Común", "+160 HP máximos.", lambda p: (setattr(p, 'max_hp', p.max_hp + 160), p.heal(100))),
        ("RK18", "Runa de Precisión", "Habilidad", "Común", "+12% probabilidad de golpe crítico.", lambda p: setattr(p, 'crit_chance', p.crit_chance + 0.12)),
        ("RK19", "Corte Arcano", "Ataque", "Común", "+18% daño de espadón y +50 MP.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.18), p.restore_mana(50))),
        ("RK20", "Pacto de Metal Rúnico", "Habilidad", "Común", "Desata Magia de Metal en tu espadón.", None, "Metal"),
        ("RK21", "Bastión de Zafiro", "Defensa", "Poco Común", "+220 HP y +12% mitigación.", lambda p: (setattr(p, 'max_hp', p.max_hp + 220), p.heal(180), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.12)))),
        ("RK22", "Tormenta de Esquirlas", "Ataque", "Poco Común", "+35% daño total de combate.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.35)),
        ("RK23", "Sobrecarga de Runas", "Poder", "Poco Común", "+200 MP y +25 MP/s regeneración.", lambda p: (setattr(p, 'max_mana', p.max_mana + 200), p.restore_mana(200), setattr(p, 'passive_mana_regen', p.passive_mana_regen + 25.0))),
        ("RK24", "Tajo Colosal Ancestral", "Ataque", "Poco Común", "+40 daño fijo de espadón.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 40)),
        ("RK25", "Barrera Inflexible", "Defensa", "Poco Común", "+15% mitigación de todo daño.", lambda p: setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.15))),
        ("RK26", "Acometida Rúnica", "Habilidad", "Poco Común", "+20% velocidad y -0.06s cooldown de ataque.", lambda p: (setattr(p, 'speed_mult', p.speed_mult + 0.20), setattr(p, 'attack_cooldown_max', max(0.20, p.attack_cooldown_max - 0.06)))),
        ("RK27", "Vínculo de Mithril", "Defensa", "Poco Común", "+250 HP máximos y cura 200 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 250), p.heal(200))),
        ("RK28", "Filo del Destino", "Ataque", "Poco Común", "+25% crítico y x2.3 daño crítico.", lambda p: (setattr(p, 'crit_chance', p.crit_chance + 0.25), setattr(p, 'crit_multiplier', 2.3))),
        ("RK29", "Regeneración Rúnica", "Poder", "Poco Común", "+12 HP/s regeneración pasiva.", lambda p: setattr(p, 'passive_regen', p.passive_regen + 12.0)),
        ("RK30", "Embate de Titanes", "Ataque", "Poco Común", "+30% daño y +20 daño de arma.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.30), setattr(p, 'weapon_damage', p.weapon_damage + 20))),
        ("RK31", "Armadura de Éter Cristalino", "Defensa", "Poco Común", "+180 HP y +100 MP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 180), p.heal(150), setattr(p, 'max_mana', p.max_mana + 100), p.restore_mana(100))),
        ("RK32", "Tajo Divisor del Vacío", "Ataque", "Poco Común", "+45 daño directo de espadón.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 45)),
        ("RK33", "Fortaleza Mental", "Poder", "Poco Común", "+250 MP y sana 150 HP.", lambda p: (setattr(p, 'max_mana', p.max_mana + 250), p.restore_mana(250), p.heal(150))),
        ("RK34", "Celeridad de Batalla", "Habilidad", "Poco Común", "+25% velocidad de movimiento.", lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.25)),
        ("RK35", "Muro Rúnico Impenetrable", "Defensa", "Poco Común", "Mitiga un 14% de daño y +100 HP.", lambda p: (setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.14)), setattr(p, 'max_hp', p.max_hp + 100), p.heal(100))),
        ("RK36", "Corte Relámpago", "Ataque", "Poco Común", "+28% daño y -0.05s cooldown de espadón.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.28), setattr(p, 'attack_cooldown_max', max(0.20, p.attack_cooldown_max - 0.05)))),
        ("RK37", "Voluntad de Hierro", "Defensa", "Poco Común", "+200 HP máximos y cura 150 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 200), p.heal(150))),
        ("RK38", "Maestría en Espadón", "Ataque", "Poco Común", "+35 daño de arma y +15% daño.", lambda p: (setattr(p, 'weapon_damage', p.weapon_damage + 35), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.15))),
        ("RK39", "Pacto de la Luz Solar", "Habilidad", "Poco Común", "Desata Magia de Luz celestial.", None, "Luz"),
        ("RK40", "Resonancia de Tierra", "Poder", "Poco Común", "Desata Magia de Tierra y +100 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 100), p.heal(100)), "Tierra"),
        ("RK41", "⭐ Espadón del Monarca Celestial", "Ataque", "Rara", "+75 daño de arma y +30% daño total.", lambda p: (setattr(p, 'weapon_damage', p.weapon_damage + 75), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.30))),
        ("RK42", "⭐ Coraza Rúnica Impenetrable", "Defensa", "Rara", "+350 HP Máximos y 22% Reducción de Daño.", lambda p: (setattr(p, 'max_hp', p.max_hp + 350), p.heal(350), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.22)))),
        ("RK43", "⭐ Trascendencia Rúnica", "Poder", "Rara", "+40% Daño, +300 MP y +30 MP/s regeneración.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.40), setattr(p, 'max_mana', p.max_mana + 300), p.restore_mana(300), setattr(p, 'passive_mana_regen', p.passive_mana_regen + 30.0))),
        ("RK44", "⭐ Ira del Caballero de las Estrellas", "Ataque", "Rara", "50% Críticos (x2.5 daño) y +30% Velocidad.", lambda p: (setattr(p, 'crit_chance', 0.50), setattr(p, 'crit_multiplier', 2.5), setattr(p, 'speed_mult', p.speed_mult + 0.30))),
        ("RK45", "⭐ Santuario Rúnico Inmortal", "Defensa", "Rara", "+300 HP, +20 HP/s pasiva y cura 300 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 300), p.heal(300), setattr(p, 'passive_regen', p.passive_regen + 20.0))),
        ("RK46", "⭐ Filo Cósmico de Luz Pura", "Ataque", "Rara", "+50% Daño, Magia de Luz y +50 daño de espada.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.50), setattr(p, 'weapon_damage', p.weapon_damage + 50)), "Luz"),
        ("RK47", "⭐ Fortaleza del Titán Arcano", "Defensa", "Rara", "+400 HP, 25% Mitigación y +200 MP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 400), p.heal(400), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.25)), setattr(p, 'max_mana', p.max_mana + 200), p.restore_mana(200))),
        ("RK48", "⭐ Juicio del Trueno Rúnico", "Poder", "Rara", "+45% Daño, Magia de Trueno y +20% Velocidad.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.45), setattr(p, 'speed_mult', p.speed_mult + 0.20)), "Trueno"),
        ("RK49", "⭐ Fusión de Alma y Acero", "Habilidad", "Rara", "Restaura 500 HP y 500 MP instantáneamente.", lambda p: (p.heal(500), p.restore_mana(500))),
        ("RK50", "⭐ Avatar del Rey Rúnico", "Poder", "Rara", "+60% Daño, +300 HP, 20% Mitigación y -0.10s Cooldown.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.60), setattr(p, 'max_hp', p.max_hp + 300), p.heal(300), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.20)), setattr(p, 'attack_cooldown_max', max(0.18, p.attack_cooldown_max - 0.10)))),
    ]
    for row in rk_data:
        cid, name, cat, rar, desc, fn = row[:6]
        elem = row[6] if len(row) > 6 else None
        cards.append(CharacterCard(cid, c, name, cat, rar, desc, fn, elem))
    return cards

def _build_alchemist_deck() -> List[CharacterCard]:
    cards = []
    c = "alchemist"
    al_data = [
        ("AL01", "Matraz Cáustico", "Ataque", "Común", "+15% daño de frascos químicos.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.15)),
        ("AL02", "Tónico Fortificante", "Defensa", "Común", "+90 HP y cura 80 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 90), p.heal(80))),
        ("AL03", "Fuego Griego Concentrado", "Ataque", "Común", "+16 daño de frasco alquímico.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 16)),
        ("AL04", "Frasco de Éter Puro", "Poder", "Común", "+120 MP máximos.", lambda p: (setattr(p, 'max_mana', p.max_mana + 120), p.restore_mana(120))),
        ("AL05", "Vapor Tóxico", "Ataque", "Común", "+18% daño de área química.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.18)),
        ("AL06", "Ungüento Cicatrizante", "Defensa", "Común", "Regenera +8 HP/s pasivamente.", lambda p: setattr(p, 'passive_regen', p.passive_regen + 8.0)),
        ("AL07", "Solución Volátil", "Habilidad", "Común", "Reduce cooldown de frasco en 0.04s.", lambda p: setattr(p, 'attack_cooldown_max', max(0.16, p.attack_cooldown_max - 0.04))),
        ("AL08", "Infusión de Mercurio", "Habilidad", "Común", "+14% velocidad de movimiento.", lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.14)),
        ("AL09", "Ácido Corrosivo", "Ataque", "Común", "+20 daño fijo de frascos.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 20)),
        ("AL10", "Capa Antisalpicaduras", "Defensa", "Común", "Reduce daño recibido en un 7%.", lambda p: setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.07))),
        ("AL11", "Catalizador de Maná", "Poder", "Común", "+18 MP/s regeneración de maná.", lambda p: setattr(p, 'passive_mana_regen', p.passive_mana_regen + 18.0)),
        ("AL12", "Polvo Cegador", "Habilidad", "Común", "+12% probabilidad de golpe crítico.", lambda p: setattr(p, 'crit_chance', p.crit_chance + 0.12)),
        ("AL13", "Elixir Revitalizante", "Defensa", "Común", "+110 HP y cura 100 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 110), p.heal(100))),
        ("AL14", "Reactivo Explosivo", "Ataque", "Común", "+22% daño de ataque.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.22)),
        ("AL15", "Destilación Rápida", "Habilidad", "Común", "+10% velocidad y -0.03s cooldown.", lambda p: (setattr(p, 'speed_mult', p.speed_mult + 0.10), setattr(p, 'attack_cooldown_max', max(0.16, p.attack_cooldown_max - 0.03)))),
        ("AL16", "Frasco de Sales Ácidas", "Ataque", "Común", "+24 daño de arma.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 24)),
        ("AL17", "Bálsamo Purificador", "Defensa", "Común", "+130 HP máximos.", lambda p: (setattr(p, 'max_hp', p.max_hp + 130), p.heal(80))),
        ("AL18", "Tónico de Celeridad", "Habilidad", "Común", "+18% velocidad de traslación.", lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.18)),
        ("AL19", "Mezcla Flamígera", "Ataque", "Común", "+16% daño y desata Fuego.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.16), "Fuego"),
        ("AL20", "Poción de la Espora", "Habilidad", "Común", "Desata Magia de Naturaleza.", None, "Naturaleza"),
        ("AL21", "Miasma Pútrido Mortal", "Ataque", "Poco Común", "+32% daño de veneno y fuego químico.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.32)),
        ("AL22", "Elixir de Gran Robustez", "Defensa", "Poco Común", "+200 HP Máximos y cura 180 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 200), p.heal(180))),
        ("AL23", "Destilado de Peste", "Ataque", "Poco Común", "+38 daño de frasco químico.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 38)),
        ("AL24", "Frasco de Éter Hiperconcentrado", "Poder", "Poco Común", "+220 MP y +22 MP/s regeneración.", lambda p: (setattr(p, 'max_mana', p.max_mana + 220), p.restore_mana(220), setattr(p, 'passive_mana_regen', p.passive_mana_regen + 22.0))),
        ("AL25", "Armadura Transmutada", "Defensa", "Poco Común", "+14% mitigación de todo daño.", lambda p: setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.14))),
        ("AL26", "Combustión Espontánea", "Ataque", "Poco Común", "+25% crítico y x2.3 daño crítico.", lambda p: (setattr(p, 'crit_chance', p.crit_chance + 0.25), setattr(p, 'crit_multiplier', 2.3))),
        ("AL27", "Aceite de Deslizamiento", "Habilidad", "Poco Común", "+24% velocidad y Dash en 0.40s.", lambda p: (setattr(p, 'speed_mult', p.speed_mult + 0.24), setattr(p, 'dash_cooldown_max', 0.40))),
        ("AL28", "Regeneración Celular", "Defensa", "Poco Común", "+14 HP/s regeneración pasiva constante.", lambda p: setattr(p, 'passive_regen', p.passive_regen + 14.0)),
        ("AL29", "Nube Corrosiva de Plaga", "Ataque", "Poco Común", "+35% daño total de combate.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.35)),
        ("AL30", "Fórmula del Homúnculo", "Defensa", "Poco Común", "+180 HP, +120 MP y cura 150 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 180), p.heal(150), setattr(p, 'max_mana', p.max_mana + 120), p.restore_mana(120))),
        ("AL31", "Ácido Sulfúrico Hirviente", "Ataque", "Poco Común", "+42 daño fijo de frascos.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 42)),
        ("AL32", "Inmunidad Alquímica", "Defensa", "Poco Común", "+12% mitigación y +140 HP.", lambda p: (setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.12)), setattr(p, 'max_hp', p.max_hp + 140), p.heal(100))),
        ("AL33", "Ráfaga de Frascos", "Habilidad", "Poco Común", "Reduce cooldown de tiro en 0.08s.", lambda p: setattr(p, 'attack_cooldown_max', max(0.15, p.attack_cooldown_max - 0.08))),
        ("AL34", "Infusión de Vapor Cáustico", "Ataque", "Poco Común", "Desata Magia de Vapor y +20% daño.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.20), "Vapor"),
        ("AL35", "Tónico de Sangre Viva", "Defensa", "Poco Común", "+220 HP máximos y cura 150 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 220), p.heal(150))),
        ("AL36", "Disolvente Universal", "Ataque", "Poco Común", "+30% daño y +25 daño de frasco.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.30), setattr(p, 'weapon_damage', p.weapon_damage + 25))),
        ("AL37", "Esencia Volátil", "Habilidad", "Poco Común", "+20% velocidad y +100 MP.", lambda p: (setattr(p, 'speed_mult', p.speed_mult + 0.20), setattr(p, 'max_mana', p.max_mana + 100), p.restore_mana(100))),
        ("AL38", "Caldo Nigromántico", "Poder", "Poco Común", "+5 HP robo de vida por impacto.", lambda p: setattr(p, 'life_steal', p.life_steal + 5.0)),
        ("AL39", "Pacto de Fuego Alquímico", "Ataque", "Poco Común", "Desata Magia de Fuego y +25% daño.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.25), "Fuego"),
        ("AL40", "Elixir de Agua Bendita", "Defensa", "Poco Común", "Desata Magia de Agua y cura 150 HP.", lambda p: p.heal(150), "Agua"),
        ("AL41", "⭐ Piedra Filosofal", "Poder", "Rara", "+50% Daño, +300 MP y +35 MP/s regeneración.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.50), setattr(p, 'max_mana', p.max_mana + 300), p.restore_mana(300), setattr(p, 'passive_mana_regen', p.passive_mana_regen + 35.0))),
        ("AL42", "⭐ Gran Elixir de Inmortalidad", "Defensa", "Rara", "+380 HP Máximos, cura 380 HP y 18% mitigación.", lambda p: (setattr(p, 'max_hp', p.max_hp + 380), p.heal(380), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.18)))),
        ("AL43", "⭐ Magnum Opus Alquímico", "Ataque", "Rara", "+70 daño de frascos y +35% daño total.", lambda p: (setattr(p, 'weapon_damage', p.weapon_damage + 70), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.35))),
        ("AL44", "⭐ Peste Negra Apocalíptica", "Ataque", "Rara", "+45% Daño, Magia de Oscuridad y +8 HP robo.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.45), setattr(p, 'life_steal', p.life_steal + 8.0)), "Oscuridad"),
        ("AL45", "⭐ Crisol Solar Celestial", "Poder", "Rara", "+40% Daño, Magia de Luz y cura 250 HP.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.40), p.heal(250)), "Luz"),
        ("AL46", "⭐ Transmutación de Sangre y Oro", "Habilidad", "Rara", "Restaura 500 HP y 500 MP inmediatamente.", lambda p: (p.heal(500), p.restore_mana(500))),
        ("AL47", "⭐ Matraz de Fusión Nuclear Medieval", "Ataque", "Rara", "+65% Daño de combate total.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.65)),
        ("AL48", "⭐ Quintaesencia Vital", "Defensa", "Rara", "+300 HP, +25 HP/s pasiva y 15% reducción.", lambda p: (setattr(p, 'max_hp', p.max_hp + 300), p.heal(300), setattr(p, 'passive_regen', p.passive_regen + 25.0), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.15)))),
        ("AL49", "⭐ Fuego de Prometeo", "Ataque", "Rara", "+50 daño arma, 40% Críticos (x2.4 daño).", lambda p: (setattr(p, 'weapon_damage', p.weapon_damage + 50), setattr(p, 'crit_chance', 0.40), setattr(p, 'crit_multiplier', 2.4))),
        ("AL50", "⭐ Maestro Supremo de la Alquimia", "Poder", "Rara", "+50% Daño, +250 HP, +250 MP, 15% Mitigación y +30% Velocidad.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.50), setattr(p, 'max_hp', p.max_hp + 250), p.heal(250), setattr(p, 'max_mana', p.max_mana + 250), p.restore_mana(250), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.15)), setattr(p, 'speed_mult', p.speed_mult + 0.30))),
    ]
    for row in al_data:
        cid, name, cat, rar, desc, fn = row[:6]
        elem = row[6] if len(row) > 6 else None
        cards.append(CharacterCard(cid, c, name, cat, rar, desc, fn, elem))
    return cards

def _build_monk_deck() -> List[CharacterCard]:
    cards = []
    c = "monk"
    mo_data = [
        ("MO01", "Palma de Hierro", "Ataque", "Común", "+16% daño de golpes marciales.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.16)),
        ("MO02", "Respiración Serena", "Defensa", "Común", "+100 HP y cura 80 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 100), p.heal(80))),
        ("MO03", "Puño de Dragón", "Ataque", "Común", "+14 daño fijo de guanteletes.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 14)),
        ("MO04", "Flujo de Ki Interior", "Poder", "Común", "+100 MP y +12 MP/s regeneración.", lambda p: (setattr(p, 'max_mana', p.max_mana + 100), p.restore_mana(100), setattr(p, 'passive_mana_regen', p.passive_mana_regen + 12.0))),
        ("MO05", "Paso del Viento Ligero", "Habilidad", "Común", "+16% velocidad de movimiento.", lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.16)),
        ("MO06", "Cuerpo de Diamante", "Defensa", "Común", "Reduce todo el daño recibido en un 8%.", lambda p: setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.08))),
        ("MO07", "Ráfaga de Cien Nudillos", "Ataque", "Común", "Reduce cooldown de ataque en 0.03s.", lambda p: setattr(p, 'attack_cooldown_max', max(0.10, p.attack_cooldown_max - 0.03))),
        ("MO08", "Impacto de Punto Vital", "Habilidad", "Común", "+14% probabilidad de crítico.", lambda p: setattr(p, 'crit_chance', p.crit_chance + 0.14)),
        ("MO09", "Puño de Avalancha", "Ataque", "Común", "+18 daño de guantelete.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 18)),
        ("MO10", "Paz Mental", "Defensa", "Común", "+120 HP máximos.", lambda p: (setattr(p, 'max_hp', p.max_hp + 120), p.heal(70))),
        ("MO11", "Desvío de Proyectil", "Defensa", "Común", "+6% mitigación y +5% velocidad.", lambda p: (setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.06)), setattr(p, 'speed_mult', p.speed_mult + 0.05))),
        ("MO12", "Estallido de Ki Sónico", "Ataque", "Común", "+20% daño de impacto marcial.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.20)),
        ("MO13", "Meditación del Amanecer", "Poder", "Común", "+8 HP/s regeneración pasiva.", lambda p: setattr(p, 'passive_regen', p.passive_regen + 8.0)),
        ("MO14", "Doble Patada Voladora", "Ataque", "Común", "+20 daño de guantelete.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 20)),
        ("MO15", "Evasión del Bambú", "Habilidad", "Común", "Dash recarga 0.06s más rápido.", lambda p: setattr(p, 'dash_cooldown_max', max(0.30, p.dash_cooldown_max - 0.06))),
        ("MO16", "Postura del Tigre", "Ataque", "Común", "+18% daño y +10% crítico.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.18), setattr(p, 'crit_chance', p.crit_chance + 0.10))),
        ("MO17", "Fuerza Sin Límites", "Poder", "Común", "+130 HP y +80 MP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 130), p.heal(100), setattr(p, 'max_mana', p.max_mana + 80), p.restore_mana(80))),
        ("MO18", "Celeridad Marcial", "Habilidad", "Común", "+15% velocidad y -0.02s cooldown.", lambda p: (setattr(p, 'speed_mult', p.speed_mult + 0.15), setattr(p, 'attack_cooldown_max', max(0.10, p.attack_cooldown_max - 0.02)))),
        ("MO19", "Puño de Fuego Ardiente", "Ataque", "Común", "Desata Magia de Fuego marcial.", None, "Fuego"),
        ("MO20", "Espíritu de Trueno", "Habilidad", "Común", "Desata Magia de Trueno.", None, "Trueno"),
        ("MO21", "Danza de las Mil Palmas", "Ataque", "Poco Común", "+35% daño total de combate.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.35)),
        ("MO22", "Iluminación Serena", "Defensa", "Poco Común", "+220 HP Máximos y cura 180 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 220), p.heal(180))),
        ("MO23", "Golpe Devastador del Vacío", "Ataque", "Poco Común", "+35 daño de guantelete de hierro.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 35)),
        ("MO24", "Chakra del Corazón", "Poder", "Poco Común", "+200 MP y +12 HP/s regeneración.", lambda p: (setattr(p, 'max_mana', p.max_mana + 200), p.restore_mana(200), setattr(p, 'passive_regen', p.passive_regen + 12.0))),
        ("MO25", "Campana Dorada Inmune", "Defensa", "Poco Común", "+15% mitigación de daño.", lambda p: setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.15))),
        ("MO26", "Velocidad del Rayo Divino", "Habilidad", "Poco Común", "+25% velocidad y Dash en 0.35s.", lambda p: (setattr(p, 'speed_mult', p.speed_mult + 0.25), setattr(p, 'dash_cooldown_max', 0.35))),
        ("MO27", "Golpes Críticos Devastadores", "Ataque", "Poco Común", "50% Crítico con x2.4 multiplicador.", lambda p: (setattr(p, 'crit_chance', 0.50), setattr(p, 'crit_multiplier', 2.4))),
        ("MO28", "Transcendencia Zen", "Defensa", "Poco Común", "+180 HP, +150 MP y cura 150 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 180), p.heal(150), setattr(p, 'max_mana', p.max_mana + 150), p.restore_mana(150))),
        ("MO29", "Puño Sísmico Ancestral", "Ataque", "Poco Común", "+40 daño fijo de arma.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 40)),
        ("MO30", "Armonía Elemental", "Poder", "Poco Común", "+25 MP/s regeneración de maná.", lambda p: setattr(p, 'passive_mana_regen', p.passive_mana_regen + 25.0)),
        ("MO31", "Esquiva Acrobática", "Habilidad", "Poco Común", "+20% velocidad y +8% mitigación.", lambda p: (setattr(p, 'speed_mult', p.speed_mult + 0.20), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.08)))),
        ("MO32", "Cascada de Puños de Acero", "Ataque", "Poco Común", "Reduce cooldown a 0.12s y +15% daño.", lambda p: (setattr(p, 'attack_cooldown_max', 0.12), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.15))),
        ("MO33", "Vitalidad del Monje", "Defensa", "Poco Común", "+200 HP máximos y cura 120 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 200), p.heal(120))),
        ("MO34", "Ki Vampírico", "Poder", "Poco Común", "+4 HP robo de vida por golpe.", lambda p: setattr(p, 'life_steal', p.life_steal + 4.0)),
        ("MO35", "Tsunami Interior", "Ataque", "Poco Común", "Desata Magia de Agua y +22% daño.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.22), "Agua"),
        ("MO36", "Torbellino de Arena", "Habilidad", "Poco Común", "Desata Magia de Viento y +15% velocidad.", lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.15), "Viento"),
        ("MO37", "Firmeza de la Montaña", "Defensa", "Poco Común", "+160 HP y 10% mitigación.", lambda p: (setattr(p, 'max_hp', p.max_hp + 160), p.heal(100), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.10)))),
        ("MO38", "Golpe al Corazón de Acero", "Ataque", "Poco Común", "+30% daño y +25 daño de arma.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.30), setattr(p, 'weapon_damage', p.weapon_damage + 25))),
        ("MO39", "Pacto de la Lanza Solar", "Poder", "Poco Común", "Desata Magia de Luz celestial.", None, "Luz"),
        ("MO40", "Manto de Sombras del Monje", "Defensa", "Poco Común", "Desata Magia de Oscuridad.", None, "Oscuridad"),
        ("MO41", "⭐ Iluminación del Loto Dorado", "Poder", "Rara", "+50% Daño, +300 HP y +20 HP/s pasiva.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.50), setattr(p, 'max_hp', p.max_hp + 300), p.heal(300), setattr(p, 'passive_regen', p.passive_regen + 20.0))),
        ("MO42", "⭐ Furia Divina de Asura", "Ataque", "Rara", "+65 daño arma, 60% Críticos (x2.6 daño).", lambda p: (setattr(p, 'weapon_damage', p.weapon_damage + 65), setattr(p, 'crit_chance', 0.60), setattr(p, 'crit_multiplier', 2.6))),
        ("MO43", "⭐ Cuerpo Indestructible de Vajra", "Defensa", "Rara", "+400 HP Máximos y 24% Reducción de Daño.", lambda p: (setattr(p, 'max_hp', p.max_hp + 400), p.heal(400), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.24)))),
        ("MO44", "⭐ Torbellino de Dios del Viento", "Habilidad", "Rara", "+40% Velocidad, Dash en 0.25s y +30% Daño.", lambda p: (setattr(p, 'speed_mult', p.speed_mult + 0.40), setattr(p, 'dash_cooldown_max', 0.25), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.30))),
        ("MO45", "⭐ Ráfaga de Ki Cósmico Infinito", "Ataque", "Rara", "Cooldown de ataque a 0.10s y +40% Daño.", lambda p: (setattr(p, 'attack_cooldown_max', 0.10), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.40))),
        ("MO46", "⭐ Puño de Luz Trascendente", "Ataque", "Rara", "+50% Daño, Magia de Luz y +50 daño de guantelete.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.50), setattr(p, 'weapon_damage', p.weapon_damage + 50)), "Luz"),
        ("MO47", "⭐ Despertar del Dragón Oscuro", "Poder", "Rara", "+45% Daño, Magia de Oscuridad y +8 HP robo.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.45), setattr(p, 'life_steal', p.life_steal + 8.0)), "Oscuridad"),
        ("MO48", "⭐ Fuente Eterna de Ki", "Habilidad", "Rara", "Restaura 500 HP y 500 MP instantáneamente.", lambda p: (p.heal(500), p.restore_mana(500))),
        ("MO49", "⭐ Puño Rompedor de Montañas", "Ataque", "Rara", "+80 daño de guantelete directo.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 80)),
        ("MO50", "⭐ Ascensión del Gran Maestro", "Poder", "Rara", "+60% Daño, +300 HP, +300 MP, 18% Mitigación y +35% Velocidad.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.60), setattr(p, 'max_hp', p.max_hp + 300), p.heal(300), setattr(p, 'max_mana', p.max_mana + 300), p.restore_mana(300), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.18)), setattr(p, 'speed_mult', p.speed_mult + 0.35))),
    ]
    for row in mo_data:
        cid, name, cat, rar, desc, fn = row[:6]
        elem = row[6] if len(row) > 6 else None
        cards.append(CharacterCard(cid, c, name, cat, rar, desc, fn, elem))
    return cards

def _build_artificer_deck() -> List[CharacterCard]:
    cards = []
    c = "artificer"
    ar_data = [
        ("AR01", "Calibre Pesado de Latón", "Ataque", "Común", "+16% daño de cañón de vapor.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.16)),
        ("AR02", "Placas de Cobre Reforzadas", "Defensa", "Común", "+120 HP y +6% mitigación.", lambda p: (setattr(p, 'max_hp', p.max_hp + 120), p.heal(120), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.06)))),
        ("AR03", "Obús de Metralla", "Ataque", "Común", "+22 daño directo de cañón.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 22)),
        ("AR04", "Caldera de Éter Presurizada", "Poder", "Común", "+120 MP y +15 MP/s regeneración.", lambda p: (setattr(p, 'max_mana', p.max_mana + 120), p.restore_mana(120), setattr(p, 'passive_mana_regen', p.passive_mana_regen + 15.0))),
        ("AR05", "Válvula de Purga Rápida", "Habilidad", "Común", "Reduce cooldown de cañón en 0.05s.", lambda p: setattr(p, 'attack_cooldown_max', max(0.22, p.attack_cooldown_max - 0.05))),
        ("AR06", "Chasis Blindado", "Defensa", "Común", "Mitiga un 8% de todo el daño.", lambda p: setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.08))),
        ("AR07", "Engranajes de Celeridad", "Habilidad", "Común", "+12% velocidad de movimiento.", lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.12)),
        ("AR08", "Carga de Pólvora Alquímica", "Ataque", "Común", "+26 daño de cañón.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 26)),
        ("AR09", "Pistón Hidráulico de Retroceso", "Defensa", "Común", "+100 HP y sana 60 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 100), p.heal(60))),
        ("AR10", "Propulsión a Vapor", "Habilidad", "Común", "+15% velocidad de movimiento.", lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.15)),
        ("AR11", "Ignición a Presión", "Ataque", "Común", "+20% daño de combate total.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.20)),
        ("AR12", "Filtro de Condensación", "Poder", "Común", "+100 MP de reserva.", lambda p: (setattr(p, 'max_mana', p.max_mana + 100), p.restore_mana(100))),
        ("AR13", "Maza de Engranajes", "Defensa", "Común", "+130 HP máximos y +5% armadura.", lambda p: (setattr(p, 'max_hp', p.max_hp + 130), p.heal(80), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.05)))),
        ("AR14", "Metralla Expandida", "Ataque", "Común", "+18% daño de área explosiva.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.18)),
        ("AR15", "Refrigeración Líquida", "Habilidad", "Común", "Reduce cooldown de cañón en 0.04s.", lambda p: setattr(p, 'attack_cooldown_max', max(0.22, p.attack_cooldown_max - 0.04))),
        ("AR16", "Blindaje de Hierro Fundido", "Defensa", "Común", "+150 HP máximos.", lambda p: (setattr(p, 'max_hp', p.max_hp + 150), p.heal(90))),
        ("AR17", "Mira Telescópica de Latón", "Habilidad", "Común", "+12% probabilidad de golpe crítico.", lambda p: setattr(p, 'crit_chance', p.crit_chance + 0.12)),
        ("AR18", "Obús Incendiario", "Ataque", "Común", "+20 daño de cañón y +10% daño.", lambda p: (setattr(p, 'weapon_damage', p.weapon_damage + 20), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.10))),
        ("AR19", "Pacto de Vapor Vivo", "Habilidad", "Común", "Desata Magia de Vapor (Steampunk).", None, "Vapor"),
        ("AR20", "Pólvora de Fuego Griego", "Ataque", "Común", "Desata Magia de Fuego.", None, "Fuego"),
        ("AR21", "Cañón Automático de Vapor", "Ataque", "Poco Común", "+35% daño total de combate.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.35)),
        ("AR22", "Búnker de Titanio Portátil", "Defensa", "Poco Común", "+250 HP Máximos y +12% mitigación.", lambda p: (setattr(p, 'max_hp', p.max_hp + 250), p.heal(200), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.12)))),
        ("AR23", "Obús de Racimo Devastador", "Ataque", "Poco Común", "+45 daño directo de cañón.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 45)),
        ("AR24", "Generador de Plasma Steampunk", "Poder", "Poco Común", "+220 MP y +25 MP/s regeneración.", lambda p: (setattr(p, 'max_mana', p.max_mana + 220), p.restore_mana(220), setattr(p, 'passive_mana_regen', p.passive_mana_regen + 25.0))),
        ("AR25", "Coraza de Plomo y Bronce", "Defensa", "Poco Común", "+16% mitigación de todo daño.", lambda p: setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.16))),
        ("AR26", "Sobrecarga Neumática", "Habilidad", "Poco Común", "+22% velocidad y -0.08s cooldown de cañón.", lambda p: (setattr(p, 'speed_mult', p.speed_mult + 0.22), setattr(p, 'attack_cooldown_max', max(0.20, p.attack_cooldown_max - 0.08)))),
        ("AR27", "Blindaje Reactivo a Presión", "Defensa", "Poco Común", "+200 HP y cura 150 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 200), p.heal(150))),
        ("AR28", "Cadencia de Fuego Continuo", "Ataque", "Poco Común", "35% Críticos con x2.2 multiplicador.", lambda p: (setattr(p, 'crit_chance', p.crit_chance + 0.35), setattr(p, 'crit_multiplier', 2.2))),
        ("AR29", "Inyector de Nanovapor", "Poder", "Poco Común", "+12 HP/s regeneración pasiva.", lambda p: setattr(p, 'passive_regen', p.passive_regen + 12.0)),
        ("AR30", "Detonación en Cadena", "Ataque", "Poco Común", "+30% daño y +25 daño de arma.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.30), setattr(p, 'weapon_damage', p.weapon_damage + 25))),
        ("AR31", "Batería de Descarga Eléctrica", "Poder", "Poco Común", "Desata Magia de Trueno y +150 MP.", lambda p: (setattr(p, 'max_mana', p.max_mana + 150), p.restore_mana(150)), "Trueno"),
        ("AR32", "Metralla Perforante de Acero", "Ataque", "Poco Común", "+50 daño fijo de cañón.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 50)),
        ("AR33", "Exoesqueleto Mecánico", "Defensa", "Poco Común", "+180 HP, 10% Mitigación y +10% Velocidad.", lambda p: (setattr(p, 'max_hp', p.max_hp + 180), p.heal(120), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.10)), setattr(p, 'speed_mult', p.speed_mult + 0.10))),
        ("AR34", "Cámara de Alta Presión", "Habilidad", "Poco Común", "Dash en 0.40s y +18% velocidad.", lambda p: (setattr(p, 'dash_cooldown_max', 0.40), setattr(p, 'speed_mult', p.speed_mult + 0.18))),
        ("AR35", "Muro de Vapor Blindado", "Defensa", "Poco Común", "+14% mitigación y cura 150 HP.", lambda p: (setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.14)), p.heal(150))),
        ("AR36", "Proyectil Pesado Perforante", "Ataque", "Poco Común", "+28% daño y +30 daño de cañón.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.28), setattr(p, 'weapon_damage', p.weapon_damage + 30))),
        ("AR37", "Tanque de Reparación Automática", "Defensa", "Poco Común", "+220 HP máximos y cura 180 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 220), p.heal(180))),
        ("AR38", "Obús de Metal Líquido", "Ataque", "Poco Común", "Desata Magia de Metal y +20% daño.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.20), "Metal"),
        ("AR39", "Propulsión Sísmica", "Poder", "Poco Común", "Desata Magia de Tierra y +100 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 100), p.heal(100)), "Tierra"),
        ("AR40", "Mortero de Tormenta", "Ataque", "Poco Común", "Desata Magia de Viento y +25% daño.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.25), "Viento"),
        ("AR41", "⭐ Núcleo de Fusión Steampunk", "Poder", "Rara", "+50% Daño, +300 MP y +35 MP/s regeneración.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.50), setattr(p, 'max_mana', p.max_mana + 300), p.restore_mana(300), setattr(p, 'passive_mana_regen', p.passive_mana_regen + 35.0))),
        ("AR42", "⭐ Cañón Titánico del Apocalipsis", "Ataque", "Rara", "+80 daño de cañón y +35% daño total.", lambda p: (setattr(p, 'weapon_damage', p.weapon_damage + 80), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.35))),
        ("AR43", "⭐ Fortaleza Móvil Indestructible", "Defensa", "Rara", "+400 HP Máximos y 25% Reducción de Daño.", lambda p: (setattr(p, 'max_hp', p.max_hp + 400), p.heal(400), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.25)))),
        ("AR44", "⭐ Cañón de Rayos Solares", "Ataque", "Rara", "+45% Daño, Magia de Luz y +50 daño de cañón.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.45), setattr(p, 'weapon_damage', p.weapon_damage + 50)), "Luz"),
        ("AR45", "⭐ Obús de Materia Oscura", "Ataque", "Rara", "+50% Daño, Magia de Oscuridad y +8 HP robo.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.50), setattr(p, 'life_steal', p.life_steal + 8.0)), "Oscuridad"),
        ("AR46", "⭐ Sistema de Reparación de Emergencia", "Habilidad", "Rara", "Restaura 500 HP y 500 MP inmediatamente.", lambda p: (p.heal(500), p.restore_mana(500))),
        ("AR47", "⭐ Sobrecarga de Vapor Cataclísmica", "Ataque", "Rara", "+65% Daño total de combate.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.65)),
        ("AR48", "⭐ Blindaje de Diamante y Vapor", "Defensa", "Rara", "+320 HP, 20% Mitigación y +18 HP/s pasiva.", lambda p: (setattr(p, 'max_hp', p.max_hp + 320), p.heal(320), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.20)), setattr(p, 'passive_regen', p.passive_regen + 18.0))),
        ("AR49", "⭐ Cadencia de Asedio Automático", "Habilidad", "Rara", "Reduce cooldown a 0.22s, +40 daño arma y +25% velocidad.", lambda p: (setattr(p, 'attack_cooldown_max', 0.22), setattr(p, 'weapon_damage', p.weapon_damage + 40), setattr(p, 'speed_mult', p.speed_mult + 0.25))),
        ("AR50", "⭐ Gran Mariscal del Engranaje", "Poder", "Rara", "+60% Daño, +300 HP, +250 MP, 20% Mitigación y +30% Velocidad.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.60), setattr(p, 'max_hp', p.max_hp + 300), p.heal(300), setattr(p, 'max_mana', p.max_mana + 250), p.restore_mana(250), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.20)), setattr(p, 'speed_mult', p.speed_mult + 0.30))),
    ]
    for row in ar_data:
        cid, name, cat, rar, desc, fn = row[:6]
        elem = row[6] if len(row) > 6 else None
        cards.append(CharacterCard(cid, c, name, cat, rar, desc, fn, elem))
    return cards

def _build_shaman_deck() -> List[CharacterCard]:
    cards = []
    c = "shaman"
    sh_data = [
        ("SH01", "Golpe Totémico", "Ataque", "Común", "+15% daño de tótem espiritual.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.15)),
        ("SH02", "Bendición de Gaia", "Defensa", "Común", "+100 HP y regenera +6 HP/s.", lambda p: (setattr(p, 'max_hp', p.max_hp + 100), p.heal(100), setattr(p, 'passive_regen', p.passive_regen + 6.0))),
        ("SH03", "Astil Ancestral Tallado", "Ataque", "Común", "+16 daño fijo de tótem.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 16)),
        ("SH04", "Comunión con los Espíritus", "Poder", "Común", "+120 MP y +15 MP/s regeneración.", lambda p: (setattr(p, 'max_mana', p.max_mana + 120), p.restore_mana(120), setattr(p, 'passive_mana_regen', p.passive_mana_regen + 15.0))),
        ("SH05", "Zarpazo de Oso Primordial", "Ataque", "Común", "+18% daño de barrido.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.18)),
        ("SH06", "Piel de Corteza Viva", "Defensa", "Común", "Mitiga un 8% de todo el daño.", lambda p: setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.08))),
        ("SH07", "Paso del Ciervo Blanco", "Habilidad", "Común", "+15% velocidad de movimiento.", lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.15)),
        ("SH08", "Tótem de Piedra Imponente", "Defensa", "Común", "+120 HP máximos y cura 80 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 120), p.heal(80))),
        ("SH09", "Furia de las Bestias", "Ataque", "Común", "+20 daño directo de tótem.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 20)),
        ("SH10", "Raíces Reparadoras", "Defensa", "Común", "+8 HP/s regeneración pasiva constante.", lambda p: setattr(p, 'passive_regen', p.passive_regen + 8.0)),
        ("SH11", "Cadencia Tribal", "Habilidad", "Común", "Reduce cooldown de tótem en 0.04s.", lambda p: setattr(p, 'attack_cooldown_max', max(0.18, p.attack_cooldown_max - 0.04))),
        ("SH12", "Aullido del Lobo", "Ataque", "Común", "+20% daño y +10% crítico.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.20), setattr(p, 'crit_chance', p.crit_chance + 0.10))),
        ("SH13", "Espíritu Protector", "Defensa", "Común", "+140 HP máximos.", lambda p: (setattr(p, 'max_hp', p.max_hp + 140), p.heal(80))),
        ("SH14", "Impacto Sísmico Tribal", "Ataque", "Común", "+22 daño fijo de tótem.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 22)),
        ("SH15", "Ojo de Halcón", "Habilidad", "Común", "+14% probabilidad de crítico.", lambda p: setattr(p, 'crit_chance', p.crit_chance + 0.14)),
        ("SH16", "Vigor Salvaje", "Defensa", "Común", "+100 HP y +6% mitigación.", lambda p: (setattr(p, 'max_hp', p.max_hp + 100), p.heal(70), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.06)))),
        ("SH17", "Fuerza del Jabalí", "Ataque", "Común", "+18% daño y +10 daño de arma.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.18), setattr(p, 'weapon_damage', p.weapon_damage + 10))),
        ("SH18", "Canto de la Selva", "Poder", "Común", "+150 MP de reserva.", lambda p: (setattr(p, 'max_mana', p.max_mana + 150), p.restore_mana(150))),
        ("SH19", "Pacto de la Madre Tierra", "Habilidad", "Común", "Desata Magia de Tierra primordial.", None, "Tierra"),
        ("SH20", "Esporas de la Floresta", "Ataque", "Común", "Desata Magia de Naturaleza.", None, "Naturaleza"),
        ("SH21", "Despertar del Bosque Profundo", "Ataque", "Poco Común", "+35% daño total de combate.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.35)),
        ("SH22", "Abrazo de la Madre Naturaleza", "Defensa", "Poco Común", "+240 HP Máximos y cura 200 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 240), p.heal(200))),
        ("SH23", "Tótem del Rayo Ancestral", "Ataque", "Poco Común", "+35 daño de tótem y desata Trueno.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 35), "Trueno"),
        ("SH24", "Torrente de Vida Primitiva", "Poder", "Poco Común", "+220 MP y +15 HP/s regeneración.", lambda p: (setattr(p, 'max_mana', p.max_mana + 220), p.restore_mana(220), setattr(p, 'passive_regen', p.passive_regen + 15.0))),
        ("SH25", "Coraza de Roble Milenario", "Defensa", "Poco Común", "+15% mitigación de todo daño.", lambda p: setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.15))),
        ("SH26", "Aullido de la Manada Alfa", "Habilidad", "Poco Común", "+22% velocidad y +20% daño.", lambda p: (setattr(p, 'speed_mult', p.speed_mult + 0.22), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.20))),
        ("SH27", "Vínculo Sangriento del Tótem", "Poder", "Poco Común", "+5 HP robo de vida por golpe.", lambda p: setattr(p, 'life_steal', p.life_steal + 5.0)),
        ("SH28", "Tótem Sísmico del Terremoto", "Ataque", "Poco Común", "+42 daño directo de tótem.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 42)),
        ("SH29", "Regeneración Fotosintética", "Defensa", "Poco Común", "+18 HP/s regeneración pasiva.", lambda p: setattr(p, 'passive_regen', p.passive_regen + 18.0)),
        ("SH30", "Frenesí de la Bestia Colosal", "Ataque", "Poco Común", "40% Críticos con x2.3 multiplicador.", lambda p: (setattr(p, 'crit_chance', p.crit_chance + 0.40), setattr(p, 'crit_multiplier', 2.3))),
        ("SH31", "Santuario de los Espíritus", "Defensa", "Poco Común", "+200 HP, +150 MP y cura 150 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 200), p.heal(150), setattr(p, 'max_mana', p.max_mana + 150), p.restore_mana(150))),
        ("SH32", "Invocación de la Tormenta", "Ataque", "Poco Común", "Desata Magia de Viento y +25% daño.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.25), "Viento"),
        ("SH33", "Barrera Espiritual Viviente", "Defensa", "Poco Común", "+12% mitigación y +120 HP.", lambda p: (setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.12)), setattr(p, 'max_hp', p.max_hp + 120), p.heal(100))),
        ("SH34", "Celeridad de la Pantera", "Habilidad", "Poco Común", "+25% velocidad y Dash en 0.40s.", lambda p: (setattr(p, 'speed_mult', p.speed_mult + 0.25), setattr(p, 'dash_cooldown_max', 0.40))),
        ("SH35", "Manantial Sagrado", "Poder", "Poco Común", "Desata Magia de Agua y cura 200 HP.", lambda p: p.heal(200), "Agua"),
        ("SH36", "Tótem del Fuego Chamánico", "Ataque", "Poco Común", "Desata Magia de Fuego y +22% daño.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.22), "Fuego"),
        ("SH37", "Firmeza de la Raíz Ancestral", "Defensa", "Poco Común", "+200 HP máximos y cura 150 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 200), p.heal(150))),
        ("SH38", "Golpe Rompecolmillos", "Ataque", "Poco Común", "+35 daño de arma y +15% daño.", lambda p: (setattr(p, 'weapon_damage', p.weapon_damage + 35), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.15))),
        ("SH39", "Pacto del Sol Radiante", "Poder", "Poco Común", "Desata Magia de Luz celestial.", None, "Luz"),
        ("SH40", "Manto de Sombras Primordial", "Defensa", "Poco Común", "Desata Magia de Oscuridad.", None, "Oscuridad"),
        ("SH41", "⭐ Despertar del Titán de la Naturaleza", "Poder", "Rara", "+50% Daño, +350 HP y +25 HP/s pasiva.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.50), setattr(p, 'max_hp', p.max_hp + 350), p.heal(350), setattr(p, 'passive_regen', p.passive_regen + 25.0))),
        ("SH42", "⭐ Tótem del Fin de los Tiempos", "Ataque", "Rara", "+75 daño de tótem y +35% daño total.", lambda p: (setattr(p, 'weapon_damage', p.weapon_damage + 75), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.35))),
        ("SH43", "⭐ Avatar Espiritual Ancestral", "Poder", "Rara", "+40% Daño, +300 MP y +35 MP/s regeneración.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.40), setattr(p, 'max_mana', p.max_mana + 300), p.restore_mana(300), setattr(p, 'passive_mana_regen', p.passive_mana_regen + 35.0))),
        ("SH44", "⭐ Coraza del Árbol del Mundo (Yggdrasil)", "Defensa", "Rara", "+420 HP Máximos y 24% Reducción de Daño.", lambda p: (setattr(p, 'max_hp', p.max_hp + 420), p.heal(420), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.24)))),
        ("SH45", "⭐ Danza Chamánica del Vórtice Solar", "Ataque", "Rara", "+50% Daño, Magia de Luz y +50 daño de tótem.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.50), setattr(p, 'weapon_damage', p.weapon_damage + 50)), "Luz"),
        ("SH46", "⭐ Maldición del Espíritu Sombrío", "Ataque", "Rara", "+45% Daño, Magia de Oscuridad y +8 HP robo.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.45), setattr(p, 'life_steal', p.life_steal + 8.0)), "Oscuridad"),
        ("SH47", "⭐ Resurrección Primordial de Gaia", "Habilidad", "Rara", "Restaura 500 HP y 500 MP inmediatamente.", lambda p: (p.heal(500), p.restore_mana(500))),
        ("SH48", "⭐ Furia Salvaje del Depredador Ápice", "Ataque", "Rara", "55% Críticos (x2.5 daño) y +30% Velocidad.", lambda p: (setattr(p, 'crit_chance', 0.55), setattr(p, 'crit_multiplier', 2.5), setattr(p, 'speed_mult', p.speed_mult + 0.30))),
        ("SH49", "⭐ Tótem Inmortal de Piedra de Trueno", "Defensa", "Rara", "+300 HP, 18% Mitigación y +15 HP/muerte.", lambda p: (setattr(p, 'max_hp', p.max_hp + 300), p.heal(300), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.18)))),
        ("SH50", "⭐ Gran Señor de las Tierras Salvajes", "Poder", "Rara", "+60% Daño, +300 HP, +300 MP, 18% Mitigación y +30% Velocidad.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.60), setattr(p, 'max_hp', p.max_hp + 300), p.heal(300), setattr(p, 'max_mana', p.max_mana + 300), p.restore_mana(300), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.18)), setattr(p, 'speed_mult', p.speed_mult + 0.30))),
    ]
    for row in sh_data:
        cid, name, cat, rar, desc, fn = row[:6]
        elem = row[6] if len(row) > 6 else None
        cards.append(CharacterCard(cid, c, name, cat, rar, desc, fn, elem))
    return cards

def _build_inquisitor_deck() -> List[CharacterCard]:
    cards = []
    c = "inquisitor"
    in_data = [
        ("IN01", "Azote de la Penitencia", "Ataque", "Común", "+16% daño de mangual giratorio.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.16)),
        ("IN02", "Cilicio Sagrado", "Defensa", "Común", "+100 HP y +6% mitigación.", lambda p: (setattr(p, 'max_hp', p.max_hp + 100), p.heal(100), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.06)))),
        ("IN03", "Cadenas Dentadas de Hierro", "Ataque", "Común", "+16 daño fijo de mangual.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 16)),
        ("IN04", "Fervor Fanático", "Poder", "Común", "+110 MP y +14 MP/s regeneración.", lambda p: (setattr(p, 'max_mana', p.max_mana + 110), p.restore_mana(110), setattr(p, 'passive_mana_regen', p.passive_mana_regen + 14.0))),
        ("IN05", "Vórtice Carmesí de 360°", "Ataque", "Común", "+20% daño de barrido circular.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.20)),
        ("IN06", "Hábito del Purificador", "Defensa", "Común", "Mitiga un 8% de todo el daño.", lambda p: setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.08))),
        ("IN07", "Zelo Inquebrantable", "Habilidad", "Común", "+12% velocidad de movimiento.", lambda p: setattr(p, 'speed_mult', p.speed_mult + 0.12)),
        ("IN08", "Púas Ensangrentadas", "Ataque", "Común", "+20 daño de arma y sangrado.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 20)),
        ("IN09", "Sangre del Mártir", "Poder", "Común", "+3 HP robo de sangre por impacto.", lambda p: setattr(p, 'life_steal', p.life_steal + 3.0)),
        ("IN10", "Coraza de la Fe Inquebrantable", "Defensa", "Común", "+120 HP máximos.", lambda p: (setattr(p, 'max_hp', p.max_hp + 120), p.heal(80))),
        ("IN11", "Cadencia de Castigo", "Habilidad", "Común", "Reduce cooldown de mangual en 0.04s.", lambda p: setattr(p, 'attack_cooldown_max', max(0.18, p.attack_cooldown_max - 0.04))),
        ("IN12", "Juicio del Hereje", "Ataque", "Común", "+22% daño de combate.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.22)),
        ("IN13", "Purificación por Fuego", "Ataque", "Común", "+15% daño y desata Fuego.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.15), "Fuego"),
        ("IN14", "Oración de Resistencia", "Defensa", "Común", "+140 HP y cura 80 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 140), p.heal(80))),
        ("IN15", "Ojo Inquisitorial", "Habilidad", "Común", "+12% probabilidad de golpe crítico.", lambda p: setattr(p, 'crit_chance', p.crit_chance + 0.12)),
        ("IN16", "Bola de Hierro Incandescente", "Ataque", "Común", "+24 daño de mangual.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 24)),
        ("IN17", "Penitencia Silente", "Defensa", "Común", "+8 HP/s regeneración pasiva.", lambda p: setattr(p, 'passive_regen', p.passive_regen + 8.0)),
        ("IN18", "Celeridad Fanática", "Habilidad", "Común", "+15% velocidad y -0.03s cooldown.", lambda p: (setattr(p, 'speed_mult', p.speed_mult + 0.15), setattr(p, 'attack_cooldown_max', max(0.18, p.attack_cooldown_max - 0.03)))),
        ("IN19", "Cántico de la Hoguera", "Poder", "Común", "+120 MP y cura 60 HP.", lambda p: (setattr(p, 'max_mana', p.max_mana + 120), p.restore_mana(120), p.heal(60))),
        ("IN20", "Pacto del Fuego Sagrado", "Habilidad", "Común", "Desata Magia de Fuego ardiente.", None, "Fuego"),
        ("IN21", "Frenesí de la Penitencia Carmesí", "Ataque", "Poco Común", "+35% daño total en 360°.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.35)),
        ("IN22", "Manto del Gran Inquisidor", "Defensa", "Poco Común", "+220 HP Máximos y +12% mitigación.", lambda p: (setattr(p, 'max_hp', p.max_hp + 220), p.heal(180), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.12)))),
        ("IN23", "Flagelo de Acero Sagrado", "Ataque", "Poco Común", "+40 daño directo de mangual.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 40)),
        ("IN24", "Éxtasis del Martirio", "Poder", "Poco Común", "+220 MP y +5 HP robo de sangre.", lambda p: (setattr(p, 'max_mana', p.max_mana + 220), p.restore_mana(220), setattr(p, 'life_steal', p.life_steal + 5.0))),
        ("IN25", "Armadura de Penitente de Bronce", "Defensa", "Poco Común", "+15% mitigación de todo daño.", lambda p: setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.15))),
        ("IN26", "Giro Devastador Incesante", "Habilidad", "Poco Común", "Reduce cooldown a 0.24s y +18% velocidad.", lambda p: (setattr(p, 'attack_cooldown_max', 0.24), setattr(p, 'speed_mult', p.speed_mult + 0.18))),
        ("IN27", "Sangre Sagrada Incorruptible", "Defensa", "Poco Común", "+200 HP y cura 160 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 200), p.heal(160))),
        ("IN28", "Sentencia de Muerte Hereje", "Ataque", "Poco Común", "40% Críticos con x2.4 multiplicador.", lambda p: (setattr(p, 'crit_chance', p.crit_chance + 0.40), setattr(p, 'crit_multiplier', 2.4))),
        ("IN29", "Gracia Redentora", "Poder", "Poco Común", "+14 HP/s regeneración pasiva.", lambda p: setattr(p, 'passive_regen', p.passive_regen + 14.0)),
        ("IN30", "Fuego de Purificación Masiva", "Ataque", "Poco Común", "+30% daño y +25 daño de arma.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.30), setattr(p, 'weapon_damage', p.weapon_damage + 25))),
        ("IN31", "Cáliz de la Devoción", "Poder", "Poco Común", "+200 MP y cura 150 HP.", lambda p: (setattr(p, 'max_mana', p.max_mana + 200), p.restore_mana(200), p.heal(150))),
        ("IN32", "Cadenas del Purgatorio", "Ataque", "Poco Común", "Desata Magia de Metal y +20% daño.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.20), "Metal"),
        ("IN33", "Escudo de la Verdad Inmortal", "Defensa", "Poco Común", "+14% mitigación y +140 HP.", lambda p: (setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.14)), setattr(p, 'max_hp', p.max_hp + 140), p.heal(100))),
        ("IN34", "Paso del Cazador de Brujas", "Habilidad", "Poco Común", "+24% velocidad y Dash en 0.40s.", lambda p: (setattr(p, 'speed_mult', p.speed_mult + 0.24), setattr(p, 'dash_cooldown_max', 0.40))),
        ("IN35", "Vigor Inquisitorial", "Defensa", "Poco Común", "+220 HP máximos y cura 150 HP.", lambda p: (setattr(p, 'max_hp', p.max_hp + 220), p.heal(150))),
        ("IN36", "Mangual de la Ira Divina", "Ataque", "Poco Común", "+45 daño fijo de arma.", lambda p: setattr(p, 'weapon_damage', p.weapon_damage + 45)),
        ("IN37", "Excomunión fulminante", "Ataque", "Poco Común", "Desata Magia de Trueno y +25% daño.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.25), "Trueno"),
        ("IN38", "Sello de los Siete Dolores", "Poder", "Poco Común", "+6 HP robo de sangre por impacto.", lambda p: setattr(p, 'life_steal', p.life_steal + 6.0)),
        ("IN39", "Pacto de la Luz Purificadora", "Habilidad", "Poco Común", "Desata Magia de Luz celestial.", None, "Luz"),
        ("IN40", "Abrazo de la Sombra Penitencial", "Defensa", "Poco Común", "Desata Magia de Oscuridad.", None, "Oscuridad"),
        ("IN41", "⭐ Gran Auto de Fe Sagrado", "Ataque", "Rara", "+80 daño de mangual y +35% daño total.", lambda p: (setattr(p, 'weapon_damage', p.weapon_damage + 80), setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.35))),
        ("IN42", "⭐ Coraza del Santo Martirio", "Defensa", "Rara", "+380 HP Máximos y 24% Reducción de Daño.", lambda p: (setattr(p, 'max_hp', p.max_hp + 380), p.heal(380), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.24)))),
        ("IN43", "⭐ Fuego Purificador de la Herejía", "Poder", "Rara", "+50% Daño, Magia de Fuego y +300 MP.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.50), setattr(p, 'max_mana', p.max_mana + 300), p.restore_mana(300)), "Fuego"),
        ("IN44", "⭐ Sentencia del Tribunal Celestial", "Ataque", "Rara", "55% Críticos (x2.6 daño) y +30% Velocidad.", lambda p: (setattr(p, 'crit_chance', 0.55), setattr(p, 'crit_multiplier', 2.6), setattr(p, 'speed_mult', p.speed_mult + 0.30))),
        ("IN45", "⭐ Corona de Espinas Inmortal", "Defensa", "Rara", "+320 HP, 18% Mitigación y +20 HP/s pasiva.", lambda p: (setattr(p, 'max_hp', p.max_hp + 320), p.heal(320), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.18)), setattr(p, 'passive_regen', p.passive_regen + 20.0))),
        ("IN46", "⭐ Mangual de la Luz Divina", "Ataque", "Rara", "+50% Daño, Magia de Luz y +50 daño de mangual.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.50), setattr(p, 'weapon_damage', p.weapon_damage + 50)), "Luz"),
        ("IN47", "⭐ Cosecha del Inquisidor Carmesí", "Ataque", "Rara", "+45% Daño, Magia de Oscuridad y +8 HP robo.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.45), setattr(p, 'life_steal', p.life_steal + 8.0)), "Oscuridad"),
        ("IN48", "⭐ Absolución Total de los Pecados", "Habilidad", "Rara", "Restaura 500 HP y 500 MP inmediatamente.", lambda p: (p.heal(500), p.restore_mana(500))),
        ("IN49", "⭐ Cólera Inquisitorial Suprema", "Ataque", "Rara", "+65% Daño total en área de 360°.", lambda p: setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.65)),
        ("IN50", "⭐ Sumo Inquisidor de la Sagrada Orden", "Poder", "Rara", "+60% Daño, +300 HP, +300 MP, 18% Mitigación y +30% Velocidad.", lambda p: (setattr(p, 'bonus_damage_mult', p.bonus_damage_mult + 0.60), setattr(p, 'max_hp', p.max_hp + 300), p.heal(300), setattr(p, 'max_mana', p.max_mana + 300), p.restore_mana(300), setattr(p, 'damage_reduction', min(0.60, p.damage_reduction + 0.18)), setattr(p, 'speed_mult', p.speed_mult + 0.30))),
    ]
    for row in in_data:
        cid, name, cat, rar, desc, fn = row[:6]
        elem = row[6] if len(row) > 6 else None
        cards.append(CharacterCard(cid, c, name, cat, rar, desc, fn, elem))
    return cards

# Base de datos global de 50 cartas por personaje (600 cartas de mejora únicas en total)
CHARACTER_DECKS = {
    "berserker": _build_berserker_deck(),
    "paladin": _build_paladin_deck(),
    "rogue": _build_rogue_deck(),
    "mage": _build_mage_deck(),
    "hunter": _build_hunter_deck(),
    "necromancer": _build_necromancer_deck(),
    "runeknight": _build_runeknight_deck(),
    "alchemist": _build_alchemist_deck(),
    "monk": _build_monk_deck(),
    "artificer": _build_artificer_deck(),
    "shaman": _build_shaman_deck(),
    "inquisitor": _build_inquisitor_deck()
}


def get_deck_for_character(character_id: str) -> List[CharacterCard]:
    """Retorna la baraja completa de 50 cartas únicas del personaje seleccionado (12 arquetipos)."""
    cid = str(character_id).lower()
    if "berserk" in cid:
        return CHARACTER_DECKS["berserker"]
    elif "palad" in cid:
        return CHARACTER_DECKS["paladin"]
    elif "pícar" in cid or "picar" in cid or "rogue" in cid:
        return CHARACTER_DECKS["rogue"]
    elif "mag" in cid:
        return CHARACTER_DECKS["mage"]
    elif "cazad" in cid or "hunter" in cid:
        return CHARACTER_DECKS["hunter"]
    elif "necro" in cid or "nigrom" in cid:
        return CHARACTER_DECKS["necromancer"]
    elif "rune" in cid or "rúnic" in cid or "runic" in cid:
        return CHARACTER_DECKS["runeknight"]
    elif "alchem" in cid or "alquim" in cid:
        return CHARACTER_DECKS["alchemist"]
    elif "monk" in cid or "monje" in cid:
        return CHARACTER_DECKS["monk"]
    elif "artific" in cid:
        return CHARACTER_DECKS["artificer"]
    elif "shaman" in cid or "cham" in cid:
        return CHARACTER_DECKS["shaman"]
    elif "inquis" in cid:
        return CHARACTER_DECKS["inquisitor"]
    return CHARACTER_DECKS["berserker"]
