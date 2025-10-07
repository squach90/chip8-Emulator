import sys

from main import Chip8
from window import Chip8Window
import time

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Usage: python chip8.py <rom.ch8>")
        sys.exit(1)

    rom_path = sys.argv[1]

    # Crée les instances
    chip8 = Chip8()
    window = Chip8Window()

    # Charge le fichier ROM
    try:
        chip8.load_program(rom_path)
        print(f"🎮 Loaded ROM: {rom_path}")
    except FileNotFoundError:
        print(f"❌ ROM not found: {rom_path}")
        sys.exit(1)

    # Boucle principale de l’émulateur
    running = True
    while running:
        chip8.emulation_cycle()
        window.draw(chip8)
        running = window.handle_events(chip8)
        time.sleep(0.01)
