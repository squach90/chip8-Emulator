# 🕹️ CHIP-8 Emulator (Python)

A simple **CHIP-8 emulator** written in Python.

## Features
- Full CHIP-8 instruction set  
- Terminal-based file browser  
- Cross-platform (macOS, Linux, Windows)  
- Supports `.ch8`, `.c8` files  
- Pygame Required  

## Requirements
- Python 3.8 or higher  
- Pygame

## How to Run
```bash
git clone https://github.com/yourusername/chip8-emulator.git
cd chip8-emulator
pip3 install pygame
python3 main.py
```

## File Browser Controls

↑ / ↓  Move cursor  
Enter  Open folder / Select ROM  
Backspace  Go up a directory  
Esc  Quit browser

## Typical CHIP-8 Key Layout
```bash
1 2 3 4      → 1 2 3 C  
Q W E R      → 4 5 6 D  
A S D F      → 7 8 9 E  
Z X C V      → A 0 B F
```

Thank to:
https://multigesture.net/articles/how-to-write-an-emulator-chip-8-interpreter/