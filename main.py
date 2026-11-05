"""
================================================================================
MÓDULO: main.py
RESPONSABILIDAD: Punto de entrada principal del videojuego.
CONCEPTO ACADÉMICO: Inicialización del Entorno, Configuración de Ventana
                    y Encapsulamiento del Game Loop.
================================================================================
Proyecto Final Universitario: Videojuego Hack & Slash en 2D Retro Pixel Art
Estudiante: Agustín Cataldo
Tecnologías: Python 3.1x / Pygame (Pygame-CE)
================================================================================
"""

import sys
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_TITLE
from game_engine import GameEngine


def main():
    """
    Función de arranque del sistema:
    1. Inicializa el subsistema gráfico y de eventos de Pygame.
    2. Configura la ventana a 1280x720 con doble búfer (Double Buffering) para evitar tearing.
    3. Inicializa el reloj interno calibrado a 60 FPS.
    4. Cede el control al GameEngine para ejecutar el ciclo de vida del juego.
    """
    # Inicialización de subsistemas de Pygame
    pygame.init()

    # Intentar inicializar el mezclador de audio con manejo resiliente
    try:
        pygame.mixer.init()
    except Exception as audio_err:
        print(f"[Aviso] No se detectó dispositivo de audio activo: {audio_err}")

    # Configuración de ventana con aceleración por doble búfer
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption(GAME_TITLE)

    # Reloj para control preciso de 60 cuadros por segundo
    clock = pygame.time.Clock()

    print("=" * 70)
    print(" INICIANDO VIDEOJUEGO: CLOCKWORK REQUIEM")
    print(" Hack and Slash Roguelike 2D - Dark Steampunk")
    print(f" Resolución: {SCREEN_WIDTH}x{SCREEN_HEIGHT} | Tasa de Refresco: {FPS} FPS")
    print(" Arquitectura: Modular Orientada a Objetos (SOLID / Patrón State)")
    print("=" * 70)

    # Instanciación y ejecución del motor
    engine = GameEngine(screen, clock)
    engine.run()


if __name__ == "__main__":
    main()
