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
        self.memory[0x50:0x50 + len(fontset)] = fontset

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

        sprites = {
            0x0: [0xF0, 0x90, 0x90, 0x90, 0xF0],
            0x1: [0x20, 0x60, 0x20, 0x20, 0x70],
            0x2: [0xF0, 0x10, 0xF0, 0x80, 0xF0],
            0x3: [0xF0, 0x10, 0xF0, 0x10, 0xF0],
            0x4: [0x90, 0x90, 0xF0, 0x10, 0x10],
            0x5: [0xF0, 0x80, 0xF0, 0x10, 0xF0],
            0x6: [0xF0, 0x80, 0xF0, 0x90, 0xF0],
            0x7: [0xF0, 0x10, 0x20, 0x40, 0x40],
            0x8: [0xF0, 0x90, 0xF0, 0x90, 0xF0],
            0x9: [0xF0, 0x90, 0xF0, 0x10, 0xF0],
            0xA: [0xF0, 0x90, 0xF0, 0x90, 0x90],
            0xB: [0xE0, 0x90, 0xE0, 0x90, 0xE0],
            0xC: [0xF0, 0x80, 0x80, 0x80, 0xF0],
            0xD: [0xE0, 0x90, 0x90, 0x90, 0xE0],
            0xE: [0xF0, 0x80, 0xF0, 0x80, 0xF0],
            0xF: [0xF0, 0x80, 0xF0, 0x80, 0x80],
        }


        # Fetch
        opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]


        # Decode
        match (opcode & 0xF000):

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
            
            case (0x1000):
                nnn = opcode & 0x0FFF  # extrait l'adresse NNN
                self.pc = nnn           # saute à cette adresse
                print(f"JP {nnn:03X}")


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

                    case (0x000A):  # FX0A : wait for key press
                        x = (opcode & 0x0F00) >> 8
                        key_pressed = None
                        for i, k in enumerate(self.key):
                            if k != 0:
                                self.V[x] = i
                                key_pressed = i
                                break

                        if key_pressed is not None:
                            # place le sprite correspondant dans la mémoire pour DRW
                            self.I = 0x300
                            self.memory[self.I:self.I+5] = bytes(sprites[key_pressed])
                            self.pc += 2  # passe à l'instruction suivante
                        print(f"FX0A: Waiting for key, V{x:X}={self.V[x]}")


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

# # Exemple : programme test
# chip8.memory[0x200:0x200+4] = bytes([0x00, 0xE0, 0xA3, 0x00])
# chip8.V[1] = 254
# chip8.I = 500
# chip8.pc = 0x200

# chip8.load_program("ibm-logo.ch8")

# test_keys.ch8
test_rom = bytes([
    0x00, 0xE0,       # CLS : Clear screen (au début)
    0x60, 0x00,       # LD V0, 0 : X
    0x61, 0x00,       # LD V1, 0 : Y

    # boucle :
    0x00, 0xE0,       # CLS à chaque itération
    0xF0, 0x0A,       # LD V0, K : attend une touche
    0xD0, 0x15,       # DRW V0,V1,5 : dessine sprite
    0x12, 0x06        # JP 0x206 : retourne au début de la boucle (juste avant CLS)
])


chip8.memory[0x200:0x200+len(test_rom)] = test_rom
chip8.pc = 0x200

# Exemple de sprite à l'adresse 0x300 (5 lignes)
chip8.memory[0x300:0x305] = bytes([
    0b11110000,
    0b10010000,
    0b10010000,
    0b10010000,
    0b11110000,
])

running = True
while running:
    chip8.emulation_cycle()
    window.draw(chip8)
    running = window.handle_events(chip8)
    time.sleep(0.05)
