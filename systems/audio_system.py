"""
================================================================================
MÓDULO: systems/audio_system.py
RESPONSABILIDAD: Motor de sonido resiliente, generador procedimental de audio (SFX & BGM)
                 y administrador de canales y volumen.
CONCEPTO ACADÉMICO: Síntesis de Sonido Digital por Software (DSP), Patrón Facade
                    y Resiliencia ante ausencia de hardware de audio.
================================================================================
Garantiza que el juego cuente con una ambientación auditiva completa estilo 16-bit / Retro Arcade:
- Efectos de sonido (SFX) para todas las armas medievales, hechizos elementales, impactos,
  pasivas, pasos, dash neumático, subidas de nivel y menús.
- Pistas de música ambiental procedimental (BGM) para el Menú Principal, Mazmorras y Jefes.
- Síntesis matemática pura en PCM 16-bit (44.1kHz / 22.05kHz) guardada en caché local,
  eliminando cualquier riesgo de 'FileNotFoundError' en cualquier máquina.
- Control de volumen maestro, música, efectos y atajo de silenciado rápido [M].
"""

import os
import io
import math
import struct
import random
import wave
import pygame
from typing import Dict, Optional


class AudioSynthesizer:
    """Fábrica de audio que genera formas de onda PCM para SFX y BGM procedimentales."""

    @staticmethod
    def save_wav(path: str, samples: list, sample_rate: int = 22050):
        """Guarda una lista de muestras flotantes (-1.0 a 1.0) en formato WAV PCM 16-bit Mono."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with wave.open(path, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            raw = bytearray()
            for s in samples:
                val = int(max(-32767, min(32767, s * 32767.0)))
                raw.extend(struct.pack('<h', val))
            wav_file.writeframes(raw)

    @classmethod
    def generate_all_assets(cls, base_dir: str, sample_rate: int = 22050):
        """Genera todos los archivos WAV de SFX y Música si no existen aún en disco."""
        sfx_dir = os.path.join(base_dir, "sfx")
        music_dir = os.path.join(base_dir, "music")
        os.makedirs(sfx_dir, exist_ok=True)
        os.makedirs(music_dir, exist_ok=True)

        generators = {
            # --- ARMAS MEDIEVALES ---
            "slash_sword": lambda: cls._synth_sword(sample_rate),
            "axe_swing": lambda: cls._synth_axe(sample_rate),
            "blunt_mace": lambda: cls._synth_mace(sample_rate),
            "dagger_slice": lambda: cls._synth_daggers(sample_rate),
            "crossbow_shot": lambda: cls._synth_crossbow(sample_rate),
            "cannon_shot": lambda: cls._synth_cannon(sample_rate),
            "flask_throw": lambda: cls._synth_flask(sample_rate),
            "fist_punch": lambda: cls._synth_fist(sample_rate),
            "slash_scythe": lambda: cls._synth_scythe(sample_rate),
            "slash_greatsword": lambda: cls._synth_greatsword(sample_rate),
            "blunt_totem": lambda: cls._synth_totem(sample_rate),
            "slash_flail": lambda: cls._synth_flail(sample_rate),
            "magic_bolt": lambda: cls._synth_magic_bolt(sample_rate),

            # --- HECHIZOS ELEMENTALES ---
            "spell_fire": lambda: cls._synth_spell_fire(sample_rate),
            "spell_thunder": lambda: cls._synth_spell_thunder(sample_rate),
            "spell_water": lambda: cls._synth_spell_water(sample_rate),
            "spell_wind": lambda: cls._synth_spell_wind(sample_rate),
            "spell_earth": lambda: cls._synth_spell_earth(sample_rate),
            "spell_nature": lambda: cls._synth_spell_nature(sample_rate),
            "spell_light": lambda: cls._synth_spell_light(sample_rate),
            "spell_darkness": lambda: cls._synth_spell_darkness(sample_rate),
            "spell_steam": lambda: cls._synth_spell_steam(sample_rate),
            "spell_metal": lambda: cls._synth_spell_metal(sample_rate),

            # --- IMPACTOS, VIDA Y MOVIMIENTO ---
            "enemy_hit": lambda: cls._synth_hit(sample_rate),
            "enemy_death": lambda: cls._synth_death(sample_rate),
            "player_hurt": lambda: cls._synth_player_hurt(sample_rate),
            "dash": lambda: cls._synth_dash(sample_rate),
            "heal": lambda: cls._synth_heal(sample_rate),
            "mana": lambda: cls._synth_mana(sample_rate),
            "portal_open": lambda: cls._synth_portal_open(sample_rate),
            "portal_enter": lambda: cls._synth_portal_enter(sample_rate),
            "boss_roar": lambda: cls._synth_boss_roar(sample_rate),
            "boss_death": lambda: cls._synth_boss_death(sample_rate),

            # --- INTERFAZ DE USUARIO ---
            "ui_hover": lambda: cls._synth_ui_hover(sample_rate),
            "ui_select": lambda: cls._synth_ui_select(sample_rate),
            "ui_card": lambda: cls._synth_ui_card(sample_rate),
            "game_over": lambda: cls._synth_game_over(sample_rate),
            "victory": lambda: cls._synth_victory(sample_rate),
        }

        # Generar SFX si no existen
        for name, fn in generators.items():
            path = os.path.join(sfx_dir, f"{name}.wav")
            if not os.path.exists(path):
                samples = fn()
                cls.save_wav(path, samples, sample_rate)

        # Generar BGM Tracks si no existen
        music_generators = {
            "music_menu": lambda: cls._synth_music_menu(sample_rate),
            "music_dungeon": lambda: cls._synth_music_dungeon(sample_rate),
            "music_boss": lambda: cls._synth_music_boss(sample_rate)
        }
        for name, fn in music_generators.items():
            path = os.path.join(music_dir, f"{name}.wav")
            if not os.path.exists(path):
                samples = fn()
                cls.save_wav(path, samples, sample_rate)

    # =========================================================================
    # SÍNTESIS DE FORMAS DE ONDA (SFX)
    # =========================================================================
    @staticmethod
    def _synth_sword(sr):
        dur = 0.16
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            f = 920.0 - (720.0 * (i / n))
            env = math.exp(-t * 22.0)
            noise = random.uniform(-0.18, 0.18) * (1.0 - i / n)
            s.append((math.sin(2 * math.pi * f * t) * 0.55 + noise) * env)
        return s

    @staticmethod
    def _synth_axe(sr):
        dur = 0.22
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            f = 380.0 - (300.0 * (i / n))
            env = math.exp(-t * 14.0)
            sub = 0.4 * math.sin(2 * math.pi * 65.0 * t)
            noise = random.uniform(-0.15, 0.15) * env
            s.append((math.sin(2 * math.pi * f * t) * 0.45 + sub + noise) * env)
        return s

    @staticmethod
    def _synth_mace(sr):
        dur = 0.25
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 12.0)
            # Campana armónica metálica (Frecuencias 392Hz y 784Hz)
            ring = 0.4 * math.sin(2 * math.pi * 392.0 * t) + 0.25 * math.sin(2 * math.pi * 784.0 * t)
            thud = 0.35 * math.sin(2 * math.pi * 85.0 * (1.0 - i / n) * t)
            s.append((ring + thud) * env)
        return s

    @staticmethod
    def _synth_daggers(sr):
        dur = 0.14
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            f = 1350.0 - (900.0 * (i / n))
            env = math.exp(-t * 28.0)
            noise = random.uniform(-0.25, 0.25) * env
            s.append((math.sin(2 * math.pi * f * t) * 0.45 + noise) * env)
        return s

    @staticmethod
    def _synth_crossbow(sr):
        dur = 0.18
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 18.0)
            snap = 0.5 * math.sin(2 * math.pi * (1600.0 - 1200.0 * (i / n)) * t)
            whistle = 0.3 * math.sin(2 * math.pi * 540.0 * t)
            s.append((snap + whistle) * env)
        return s

    @staticmethod
    def _synth_cannon(sr):
        dur = 0.36
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 9.0)
            sub = 0.6 * math.sin(2 * math.pi * 55.0 * t)
            noise = random.uniform(-0.5, 0.5) * math.exp(-t * 16.0)
            hiss = random.uniform(-0.2, 0.2) * (1.0 - i / n) * 0.4
            s.append((sub + noise + hiss) * env)
        return s

    @staticmethod
    def _synth_flask(sr):
        dur = 0.22
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 15.0)
            glass = 0.35 * math.sin(2 * math.pi * 2100.0 * t) + 0.25 * math.sin(2 * math.pi * 3200.0 * t)
            liquid = random.uniform(-0.2, 0.2) * math.sin(2 * math.pi * 120.0 * t)
            s.append((glass + liquid) * env)
        return s

    @staticmethod
    def _synth_fist(sr):
        dur = 0.13
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 25.0)
            punch = 0.6 * math.sin(2 * math.pi * (220.0 - 140.0 * (i / n)) * t)
            crack = random.uniform(-0.3, 0.3) * math.exp(-t * 40.0)
            s.append((punch + crack) * env)
        return s

    @staticmethod
    def _synth_scythe(sr):
        dur = 0.20
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 14.0)
            f = 640.0 - (460.0 * (i / n))
            eerie = 0.25 * math.sin(2 * math.pi * (f * 1.5) * t)
            s.append((math.sin(2 * math.pi * f * t) * 0.5 + eerie) * env)
        return s

    @staticmethod
    def _synth_greatsword(sr):
        dur = 0.24
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 13.0)
            f = 520.0 - (380.0 * (i / n))
            steel = 0.3 * math.sin(2 * math.pi * 880.0 * t)
            s.append((math.sin(2 * math.pi * f * t) * 0.5 + steel) * env)
        return s

    @staticmethod
    def _synth_totem(sr):
        dur = 0.22
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 14.0)
            wood = 0.5 * math.sin(2 * math.pi * 210.0 * t) + 0.3 * math.sin(2 * math.pi * 315.0 * t)
            s.append(wood * env)
        return s

    @staticmethod
    def _synth_flail(sr):
        dur = 0.24
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 13.0)
            chain = random.uniform(-0.25, 0.25) * math.sin(2 * math.pi * 650.0 * t)
            impact = 0.5 * math.sin(2 * math.pi * (180.0 - 110.0 * (i / n)) * t)
            s.append((chain + impact) * env)
        return s

    @staticmethod
    def _synth_magic_bolt(sr):
        dur = 0.16
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 16.0)
            f = 880.0 - 550.0 * (i / n)
            s.append(math.sin(2 * math.pi * f * t) * 0.55 * env)
        return s

    # --- HECHIZOS ELEMENTALES ---
    @staticmethod
    def _synth_spell_fire(sr):
        dur = 0.32
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 8.0)
            roar = math.sin(2 * math.pi * 95.0 * t) * 0.4
            crackle = random.uniform(-0.4, 0.4)
            s.append((roar + crackle) * env * 0.6)
        return s

    @staticmethod
    def _synth_spell_thunder(sr):
        dur = 0.28
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 11.0)
            zap = math.sin(2 * math.pi * (1200.0 - 900.0 * (i / n)) * t) * 0.4
            thunder = math.sin(2 * math.pi * 70.0 * t) * 0.45
            crackle = random.uniform(-0.35, 0.35) if (i % 6 < 3) else 0.0
            s.append((zap + thunder + crackle) * env * 0.6)
        return s

    @staticmethod
    def _synth_spell_water(sr):
        dur = 0.28
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 10.0)
            wave_mod = math.sin(2 * math.pi * 6.0 * t)
            fluid = math.sin(2 * math.pi * (280.0 + 120.0 * wave_mod) * t) * 0.4
            splash = random.uniform(-0.25, 0.25) * 0.5
            s.append((fluid + splash) * env)
        return s

    @staticmethod
    def _synth_spell_wind(sr):
        dur = 0.28
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 9.0)
            cyclone = math.sin(2 * math.pi * (400.0 + 200.0 * math.sin(2 * math.pi * 8.0 * t)) * t) * 0.35
            gust = random.uniform(-0.3, 0.3)
            s.append((cyclone + gust) * env * 0.6)
        return s

    @staticmethod
    def _synth_spell_earth(sr):
        dur = 0.32
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 8.0)
            rumble = math.sin(2 * math.pi * 50.0 * t) * 0.55
            crumble = random.uniform(-0.3, 0.3) * math.exp(-t * 12.0)
            s.append((rumble + crumble) * env)
        return s

    @staticmethod
    def _synth_spell_nature(sr):
        dur = 0.26
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 11.0)
            bloom = 0.4 * math.sin(2 * math.pi * 330.0 * t) + 0.3 * math.sin(2 * math.pi * 495.0 * t)
            whip = random.uniform(-0.2, 0.2) * math.exp(-t * 20.0)
            s.append((bloom + whip) * env)
        return s

    @staticmethod
    def _synth_spell_light(sr):
        dur = 0.35
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 8.0)
            c1 = 0.30 * math.sin(2 * math.pi * 587.0 * t)
            c2 = 0.25 * math.sin(2 * math.pi * 880.0 * t)
            c3 = 0.20 * math.sin(2 * math.pi * 1174.0 * t)
            s.append((c1 + c2 + c3) * env)
        return s

    @staticmethod
    def _synth_spell_darkness(sr):
        dur = 0.38
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 7.0)
            void_f = 140.0 - 85.0 * (i / n)
            sub = 0.6 * math.sin(2 * math.pi * void_f * t)
            warp = 0.25 * math.sin(2 * math.pi * (void_f * 2.5) * t)
            s.append((sub + warp) * env)
        return s

    @staticmethod
    def _synth_spell_steam(sr):
        dur = 0.25
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 12.0)
            hiss = random.uniform(-0.45, 0.45) * 0.7
            valve = 0.3 * math.sin(2 * math.pi * 440.0 * t) * math.exp(-t * 30.0)
            s.append((hiss + valve) * env)
        return s

    @staticmethod
    def _synth_spell_metal(sr):
        dur = 0.28
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 10.0)
            saw = 0.4 * (2.0 * ((1200.0 * t) % 1.0) - 1.0)
            buzz = 0.3 * math.sin(2 * math.pi * 2400.0 * t)
            s.append((saw + buzz) * env * 0.5)
        return s

    # --- IMPACTOS Y ESTADOS ---
    @staticmethod
    def _synth_hit(sr):
        dur = 0.12
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 26.0)
            impact = 0.55 * math.sin(2 * math.pi * (260.0 - 180.0 * (i / n)) * t)
            crunch = random.uniform(-0.3, 0.3)
            s.append((impact + crunch) * env)
        return s

    @staticmethod
    def _synth_death(sr):
        dur = 0.28
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 10.0)
            collapse = 0.45 * math.sin(2 * math.pi * (320.0 - 240.0 * (i / n)) * t)
            debris = random.uniform(-0.35, 0.35) * env
            s.append((collapse + debris) * env)
        return s

    @staticmethod
    def _synth_player_hurt(sr):
        dur = 0.22
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 13.0)
            thud = 0.5 * math.sin(2 * math.pi * 110.0 * t)
            alarm = 0.3 * math.sin(2 * math.pi * 180.0 * t)
            s.append((thud + alarm) * env)
        return s

    @staticmethod
    def _synth_dash(sr):
        dur = 0.20
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 14.0)
            steam = random.uniform(-0.5, 0.5) * (1.0 - i / n)
            sweep = 0.3 * math.sin(2 * math.pi * (450.0 - 250.0 * (i / n)) * t)
            s.append((steam + sweep) * env)
        return s

    @staticmethod
    def _synth_heal(sr):
        dur = 0.35
        n = int(sr * dur)
        s = []
        freqs = [523.25, 659.25, 783.99, 1046.50]
        step = n // 4
        for i in range(n):
            t = i / sr
            f = freqs[min(3, i // max(1, step))]
            env = math.exp(-(t % 0.09) * 16.0)
            s.append(0.55 * math.sin(2 * math.pi * f * t) * env)
        return s

    @staticmethod
    def _synth_mana(sr):
        dur = 0.25
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 12.0)
            shimmer = 0.35 * math.sin(2 * math.pi * 880.0 * t) + 0.25 * math.sin(2 * math.pi * 1320.0 * t)
            s.append(shimmer * env)
        return s

    @staticmethod
    def _synth_portal_open(sr):
        dur = 0.35
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 7.0)
            drone = 0.5 * math.sin(2 * math.pi * (160.0 + 80.0 * math.sin(2 * math.pi * 6.0 * t)) * t)
            s.append(drone * env)
        return s

    @staticmethod
    def _synth_portal_enter(sr):
        dur = 0.40
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 6.0)
            sweep = 0.5 * math.sin(2 * math.pi * (180.0 + 600.0 * (i / n)) * t)
            s.append(sweep * env)
        return s

    @staticmethod
    def _synth_boss_roar(sr):
        dur = 0.50
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 5.0)
            mod = math.sin(2 * math.pi * 12.0 * t)
            growl = 0.55 * math.sin(2 * math.pi * (85.0 + 35.0 * mod) * t)
            noise = random.uniform(-0.25, 0.25)
            s.append((growl + noise) * env)
        return s

    @staticmethod
    def _synth_boss_death(sr):
        dur = 0.65
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t * 4.0)
            boom = 0.6 * math.sin(2 * math.pi * 48.0 * t)
            blast = random.uniform(-0.4, 0.4) * (1.0 - (i / n) * 0.7)
            s.append((boom + blast) * env)
        return s

    @staticmethod
    def _synth_ui_hover(sr):
        dur = 0.025
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = 1.0 - (i / n)
            s.append(math.sin(2 * math.pi * 920.0 * t) * 0.30 * env)
        return s

    @staticmethod
    def _synth_ui_select(sr):
        dur = 0.10
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            f = 587.0 if i < n // 2 else 880.0
            env = math.exp(-(t % 0.05) * 25.0)
            s.append(math.sin(2 * math.pi * f * t) * 0.45 * env)
        return s

    @staticmethod
    def _synth_ui_card(sr):
        dur = 0.14
        n = int(sr * dur)
        s = []
        for i in range(n):
            t = i / sr
            env = 1.0 - (i / n)
            noise = random.uniform(-0.35, 0.35)
            glide = 0.3 * math.sin(2 * math.pi * (400.0 - 200.0 * (i / n)) * t)
            s.append((noise + glide) * env * 0.5)
        return s

    @staticmethod
    def _synth_game_over(sr):
        dur = 1.2
        n = int(sr * dur)
        notes = [293.66, 261.63, 233.08, 220.00]  # D4 -> C4 -> Bb3 -> A3
        step = n // 4
        s = []
        for i in range(n):
            t = i / sr
            f = notes[min(3, i // max(1, step))]
            sub_t = t % (dur / 4.0)
            env = math.exp(-sub_t * 6.0)
            s.append(math.sin(2 * math.pi * f * t) * 0.5 * env)
        return s

    @staticmethod
    def _synth_victory(sr):
        dur = 1.4
        n = int(sr * dur)
        notes = [293.66, 369.99, 440.00, 587.33]  # D Mayor arpeggio
        step = n // 4
        s = []
        for i in range(n):
            t = i / sr
            f = notes[min(3, i // max(1, step))]
            sub_t = t % (dur / 4.0)
            env = math.exp(-sub_t * 5.5)
            s.append(math.sin(2 * math.pi * f * t) * 0.55 * env)
        return s

    # =========================================================================
    # SÍNTESIS DE MÚSICA PROCEDIMENTAL EN BUCLE (BGM)
    # =========================================================================
    @staticmethod
    def _synth_music_dungeon(sr):
        """BGM Mazmorras: 124 BPM, 8 compases en Re Menor (~8 segundos en bucle sin fisuras)."""
        bpm = 124.0
        beat_len = 60.0 / bpm
        bar_len = beat_len * 4.0
        total_time = bar_len * 2.0  # 8 compases
        total_samples = int(sr * total_time)
        samples = [0.0] * total_samples

        bass_notes = [73.42, 73.42, 87.31, 98.00, 110.00, 98.00, 87.31, 82.41]
        lead_arp = [293.66, 349.23, 440.00, 587.33, 440.00, 349.23, 293.66, 220.00]

        for i in range(total_samples):
            t = i / sr

            # 1. Batería industrial (Bombo, Caja y Platillo de vapor)
            beat_pos = (t % beat_len) / beat_len
            beat_num = int(t / beat_len) % 4

            # Bombo en tiempos 0 y 2
            kick = 0.0
            if beat_num in (0, 2) and beat_pos < 0.25:
                kick = 0.45 * math.sin(2 * math.pi * (65.0 - 40.0 * (beat_pos / 0.25)) * t)

            # Caja/Snare en tiempos 1 y 3
            snare = 0.0
            if beat_num in (1, 3) and beat_pos < 0.28:
                snare = random.uniform(-0.35, 0.35) * math.exp(-beat_pos * 14.0)

            # Reloj de vapor / Hi-hat en cada semicorchea
            sub_pos = (t % (beat_len / 2.0)) / (beat_len / 2.0)
            hihat = random.uniform(-0.15, 0.15) * math.exp(-sub_pos * 24.0)

            # 2. Línea de bajo motriz
            step_8th = int(t / (beat_len * 0.5)) % len(bass_notes)
            bfreq = bass_notes[step_8th]
            b_env = math.exp(-(t % (beat_len * 0.5)) * 9.0)
            bass = 0.40 * math.sin(2 * math.pi * bfreq * t) * b_env

            # 3. Arpegio rúnico
            step_16th = int(t / (beat_len * 0.25)) % len(lead_arp)
            lfreq = lead_arp[step_16th]
            l_env = math.exp(-(t % (beat_len * 0.25)) * 12.0)
            lead = 0.22 * math.sin(2 * math.pi * lfreq * t) * l_env

            samples[i] = (kick + snare + hihat + bass + lead) * 0.65

        return samples

    @staticmethod
    def _synth_music_menu(sr):
        """BGM Menú: 96 BPM, atmósfera misteriosa y calma mecánica con cajas de música."""
        bpm = 96.0
        beat_len = 60.0 / bpm
        total_time = beat_len * 16.0  # ~10 segundos
        total_samples = int(sr * total_time)
        samples = [0.0] * total_samples

        chords = [220.00, 261.63, 329.63, 440.00]  # La Menor

        for i in range(total_samples):
            t = i / sr
            # Caja de música mecánica
            step = int(t / (beat_len * 0.5)) % len(chords)
            freq = chords[step]
            env = math.exp(-(t % (beat_len * 0.5)) * 7.0)
            chime = 0.35 * math.sin(2 * math.pi * freq * t) * env

            # Pulso grave suave
            bass = 0.25 * math.sin(2 * math.pi * 55.0 * t) * math.exp(-(t % beat_len) * 4.0)
            # Tictac sutil
            sub_t = t % (beat_len / 2.0)
            tick = random.uniform(-0.06, 0.06) * math.exp(-sub_t * 40.0)

            samples[i] = (chime + bass + tick) * 0.6

        return samples

    @staticmethod
    def _synth_music_boss(sr):
        """BGM Jefe: 138 BPM, combate épico rápido y contundente."""
        bpm = 138.0
        beat_len = 60.0 / bpm
        total_time = beat_len * 16.0  # ~7 segundos
        total_samples = int(sr * total_time)
        samples = [0.0] * total_samples

        riff = [65.41, 65.41, 77.78, 65.41, 87.31, 82.41, 77.78, 73.42]

        for i in range(total_samples):
            t = i / sr
            # Doble bombo
            sub_beat = (t % (beat_len * 0.5)) / (beat_len * 0.5)
            kick = 0.5 * math.sin(2 * math.pi * (80.0 - 50.0 * sub_beat) * t) if sub_beat < 0.3 else 0.0

            # Caja fuerte
            beat_num = int(t / beat_len) % 2
            snare = random.uniform(-0.4, 0.4) * math.exp(-sub_beat * 15.0) if beat_num == 1 else 0.0

            # Riff de bajo agresivo
            step = int(t / (beat_len * 0.25)) % len(riff)
            f = riff[step]
            b_env = math.exp(-(t % (beat_len * 0.25)) * 10.0)
            saw = (2.0 * ((f * t) % 1.0) - 1.0) * 0.35 * b_env

            samples[i] = (kick + snare + saw) * 0.7

        return samples


class AudioSystem:
    """Administrador centralizado de audio, reproducción de efectos y música."""

    _instance = None

    def __init__(self, asset_dir: str = "assets/audio"):
        self.asset_dir = asset_dir
        self.is_initialized = False
        self.muted = False
        self.master_volume = 0.80
        self.sfx_volume = 0.85
        self.music_volume = 0.65

        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_tracks: Dict[str, pygame.mixer.Sound] = {}
        self.current_music_name: Optional[str] = None
        self.music_channel: Optional[pygame.mixer.Channel] = None

        self._init_mixer()

    def _init_mixer(self):
        """Inicializa Pygame Mixer con manejo resiliente y carga de recursos."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(32)
            self.music_channel = pygame.mixer.Channel(0)
            self.is_initialized = True
        except Exception as e:
            print(f"[AudioSystem] Aviso: No se pudo inicializar dispositivo de audio ({e}). Modo silencioso activo.")
            self.is_initialized = False
            return

        # Generar o cargar sonidos
        try:
            AudioSynthesizer.generate_all_assets(self.asset_dir, sample_rate=22050)
            self._load_sounds()
        except Exception as e:
            print(f"[AudioSystem] Aviso durante la síntesis/carga de audio: {e}")

    def _load_sounds(self):
        """Carga en memoria todos los archivos de sonido sintetizados."""
        sfx_dir = os.path.join(self.asset_dir, "sfx")
        if os.path.exists(sfx_dir):
            for file in os.listdir(sfx_dir):
                if file.endswith(".wav"):
                    name = file[:-4]
                    full_path = os.path.join(sfx_dir, file)
                    try:
                        snd = pygame.mixer.Sound(full_path)
                        snd.set_volume(self.sfx_volume * self.master_volume)
                        self.sounds[name] = snd
                    except Exception:
                        pass

        music_dir = os.path.join(self.asset_dir, "music")
        if os.path.exists(music_dir):
            for file in os.listdir(music_dir):
                if file.endswith(".wav"):
                    name = file[:-4]
                    full_path = os.path.join(music_dir, file)
                    try:
                        track = pygame.mixer.Sound(full_path)
                        track.set_volume(self.music_volume * self.master_volume)
                        self.music_tracks[name] = track
                    except Exception:
                        pass

    def play_sfx(self, name: str, volume_mult: float = 1.0):
        """Reproduce un efecto de sonido por nombre."""
        if not self.is_initialized or self.muted:
            return
        snd = self.sounds.get(name)
        if snd:
            try:
                final_vol = min(1.0, max(0.0, self.sfx_volume * self.master_volume * volume_mult))
                snd.set_volume(final_vol)
                snd.play()
            except Exception:
                pass

    def play_music(self, track_name: str, loop: bool = True):
        """Inicia una pista musical de fondo en bucle en el canal dedicado."""
        if not self.is_initialized:
            return
        if self.current_music_name == track_name and self.music_channel and self.music_channel.get_busy():
            return

        track = self.music_tracks.get(track_name)
        if track and self.music_channel:
            try:
                self.current_music_name = track_name
                vol = 0.0 if self.muted else (self.music_volume * self.master_volume)
                track.set_volume(vol)
                loops = -1 if loop else 0
                self.music_channel.play(track, loops=loops)
            except Exception:
                pass

    def stop_music(self):
        """Detiene la reproducción musical actual."""
        if self.music_channel:
            try:
                self.music_channel.stop()
            except Exception:
                pass
        self.current_music_name = None

    def toggle_mute(self) -> bool:
        """Alterna el estado de silenciado general."""
        self.muted = not self.muted
        if self.music_channel:
            vol = 0.0 if self.muted else (self.music_volume * self.master_volume)
            self.music_channel.set_volume(vol)
        return self.muted

    def set_master_volume(self, delta: float):
        """Ajusta el volumen maestro en incrementos relativos (+0.10, -0.10)."""
        self.master_volume = min(1.0, max(0.0, self.master_volume + delta))
        if self.muted and self.master_volume > 0.0:
            self.muted = False
        # Actualizar volúmenes de canales
        if self.music_channel:
            vol = 0.0 if self.muted else (self.music_volume * self.master_volume)
            self.music_channel.set_volume(vol)

    def get_status_tag(self) -> str:
        """Cadena formateada para el HUD."""
        if self.muted or self.master_volume <= 0.0:
            return "🔇 MUTE [M]"
        pct = int(self.master_volume * 100)
        return f"🔊 {pct}% [M/+-]"
