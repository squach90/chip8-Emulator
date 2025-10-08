import os
from pathlib import Path
import sys
import termios
import tty

# Types de fichiers acceptés
ROM_EXTENSIONS = ('.ch8', '.rom', '.bin', '.c8')

def clear():
    os.system('clear' if os.name == 'posix' else 'cls')


def get_key():
    """Lit une touche sans attendre Enter."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':  # Touche spéciale (flèche, etc.)
            ch += sys.stdin.read(2)
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def list_directory(path: Path):
    """Retourne la liste des dossiers et fichiers (ROMs uniquement)."""
    items = []
    if path.parent != path:
        items.append(("..", True))
    
    try:
        for entry in sorted(path.iterdir(), key=lambda x: x.name.lower()):
            if entry.is_dir():
                items.append((entry.name, True))
            elif entry.suffix.lower() in ROM_EXTENSIONS:
                items.append((entry.name, False))
    except PermissionError:
        pass
    
    return items


def select_rom_file():
    """Navigateur de fichiers dans le terminal"""
    current_path = Path.cwd()
    selected_index = 0

    while True:
        items = list_directory(current_path)
        clear()

        print("📂 CHIP-8 ROM SELECTOR (Terminal Edition)")
        print(f"Current path: {current_path}")
        print("-" * 70)
        print("↑/↓ = navigate | Enter = select | Backspace = parent | Esc = quit")
        print("-" * 70)

        # Affichage de la liste
        for i, (name, is_dir) in enumerate(items):
            prefix = "[DIR]" if is_dir else "[ROM]"
            if i == selected_index:
                print(f"> {prefix} {name}")
            else:
                print(f"  {prefix} {name}")

        # Lire entrée utilisateur
        key = get_key()

        if key in ('\x1b[A', 'k'):  # flèche haut ou 'k'
            selected_index = (selected_index - 1) % len(items)
        elif key in ('\x1b[B', 'j'):  # flèche bas ou 'j'
            selected_index = (selected_index + 1) % len(items)
        elif key in ('\x7f',):  # backspace
            if current_path.parent != current_path:
                current_path = current_path.parent
                selected_index = 0
        elif key == '\r':  # entrée
            name, is_dir = items[selected_index]
            if is_dir:
                if name == "..":
                    current_path = current_path.parent
                else:
                    current_path = current_path / name
                selected_index = 0
            else:
                return str(current_path / name)
        elif key == '\x1b':  # échap
            return None


# Test manuel
if __name__ == "__main__":
    rom = select_rom_file()
    if rom:
        print(f"✅ ROM sélectionnée : {rom}")
    else:
        print("❌ Aucune ROM sélectionnée.")
