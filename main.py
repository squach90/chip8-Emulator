from window import Chip8Window
import time

class Chip8:
    def __init__(self):
        self.memory = [0] * 4096          # 4K memory
        self.V = [0] * 16                # 16 registers V0-VF
        self.I = 0                        # Index register
        self.pc = 0x200                   # Program counter starts at 0x200
        self.gfx = [0] * (64 * 32)       # Display (64x32 pixels)
        self.delay_timer = 0
        self.sound_timer = 0
        self.stack = []
        self.sp = 0                       # Stack pointer
        self.key = [0] * 16               # HEX based keypad

        # Load fontset or other initialization if needed
        self.initialize()

    def initialize(self):
        # Reset memory, registers, timers, etc.
        self.memory = [0] * 4096
        self.V = [0] * 16
        self.I = 0
        self.pc = 0x200
        self.gfx = [0] * (64 * 32)
        self.delay_timer = 0
        self.sound_timer = 0
        self.stack = []
        self.sp = 0
        self.key = [0] * 16

        self.memory[0x50:0xA0] = fontset
    
    def load_program(self, filename):
        with open(filename, "rb") as f:
            program = f.read()               # lit le contenu du fichier en bytes
        # copie le programme dans la mémoire à partir de 0x200
        self.memory[0x200:0x200+len(program)] = program
    
    def emulation_cycle(self):
        # Fetch
        opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]


        # Decode
        match (opcode & 0xF000):
            case (0xA000):
                self.I = opcode & 0x0FFF
                self.pc += 2
                print(f"SET I = {self.I:03X}")

            case (0x0000):
                match (opcode & 0x000F):
                    case (0x0000):
                        self.gfx = [0] * (64 * 32)
                        self.pc += 2
                    case (0x000E):
                        self.sp -= 1
                        self.pc = self.stack[self.sp]
                        self.pc += 2
                        print("RET (return from subroutine)")
                    case (_):
                        print(f"Unknown opcode [0x0000]: 0x{opcode:X}")

            case (0x2000):
                self.stack.append(self.pc)
                self.pc = opcode & 0x0FFF
            
            case (0x6000):  # 6XNN: LD Vx, NN
                x = (opcode & 0x0F00) >> 8
                nn = opcode & 0x00FF
                self.V[x] = nn
                self.pc += 2
                print(f"LD V{x:X} = {nn:02X}")
            
            case (0x7000):
                x = (opcode & 0x0F00) >> 8  # extrait X
                nn = opcode & 0x00FF        # extrait NN
                self.V[x] = (self.V[x] + nn) & 0xFF  # garde la valeur sur 8 bits
                self.pc += 2                 # avance le compteur de programme
                print(f"ADD V{x:X} += {nn:02X} → V{x:X}={self.V[x]:02X}")



            case (0x8000):  # instructions 8XY?
                match (opcode & 0x000F):
                    case (0x0004):  # ADD Vx, Vy
                        x = (opcode & 0x0F00) >> 8
                        y = (opcode & 0x00F0) >> 4

                        if self.V[y] > (0xFF - self.V[x]):
                            self.V[0xF] = 1  # carry
                        else:
                            self.V[0xF] = 0

                        self.V[x] = (self.V[x] + self.V[y]) & 0xFF
                        self.pc += 2
                        print(f"ADD V{x:X}, V{y:X} → V{x:X}={self.V[x]:02X}, VF={self.V[0xF]}")
                    case (_):
                        print(f"Unknown opcode [0x8000]: 0x{opcode:X}")

            case (0xF000):
                match (opcode & 0x00FF):
                    case (0x0033):  # FX33
                        x = (opcode & 0x0F00) >> 8
                        value = self.V[x]
                        self.memory[self.I]     = value // 100
                        self.memory[self.I + 1] = (value // 10) % 10
                        self.memory[self.I + 2] = value % 10
                        self.pc += 2
                        print(f"BCD of V{x:X}={value} stored at I={self.I:03X}")
                    case (_):
                        print(f"Unknown opcode [0xF000]: 0x{opcode:X}")
            
            case (0xD000):
                x = (opcode & 0x0F00) >> 8
                y = (opcode & 0x00F0) >> 4
                height = opcode & 0x000F
                self.V[0xF] = 0

                for yline in range(height):
                    pixel = self.memory[self.I + yline]
                    for xline in range(8):
                        if pixel & (0x80 >> xline):
                            index = (x + xline + ((y + yline) * 64)) % len(self.gfx)
                            if self.gfx[index] == 1:
                                self.V[0xF] = 1
                            self.gfx[index] ^= 1  # XOR pixel
                
                drawFlag = True
                self.pc += 2
            
            case (0xE000):
                x = (opcode & 0x0F00) >> 8
                match (opcode & 0x00FF):
                    case (0x9E):  # EX9E
                        if self.key[self.V[x]] != 0:
                            self.pc += 4  # skip next instruction
                        else:
                            self.pc += 2

            case (_):
                print(f"Unknown opcode: 0x{opcode:X}")

        # Update timers
        if self.delay_timer > 0:
            self.delay_timer -= 1

        if self.sound_timer > 0:
            if self.sound_timer == 1:
                print("BEEP!")
            self.sound_timer -= 1

# # # === TEST ===
# # Example fontset (just zeros for testing, replace with actual fontset if needed)
fontset = [0] * 80  

# # Create emulator instance
chip8 = Chip8()

# chip8.sound_timer = 2
# chip8.delay_timer = 5

# # program_bytes = bytes([
# #     0x00, 0xE0,  # Clear screen
# #     0xA3, 0x00,  # Set I = 0x300
# # ])
# # chip8.memory[0x200:0x200+len(program_bytes)] = program_bytes

# # for cycle in range(2):
# #     print(f"\nCycle {cycle+1}:")
# #     chip8.emulation_cycle()
# #     print(f"I = {chip8.I:03X}, PC = {chip8.pc:03X}")

# chip8.V[1] = 254
# chip8.I = 500
# chip8.memory[0x200] = 0xF1
# chip8.memory[0x201] = 0x33
# chip8.pc = 0x200

# chip8.emulation_cycle()

# print(chip8.memory[500:503])  # [2, 5, 4]

# === TEST EMULATEUR CHIP8 ===

# Example fontset (just zeros for testing, replace with actual fontset if needed)
fontset = [0] * 80

chip8 = Chip8()
window = Chip8Window()

# Exemple : programme test
chip8.memory[0x200:0x200+4] = bytes([0x00, 0xE0, 0xA3, 0x00])
chip8.V[1] = 254
chip8.I = 500
chip8.pc = 0x200

chip8.load_program("ibm-logo.ch8")

running = True
while running:
    chip8.emulation_cycle()
    
    # Dessine l'écran Chip8
    window.draw(chip8)
    
    # Affiche le texte dans la console
    print(f"PC={chip8.pc:03X}, I={chip8.I:03X}, V1={chip8.V[1]:02X}, VF={chip8.V[0xF]}")
    
    # Gère les événements Pygame
    running = window.handle_events()
    
    time.sleep(0.1)