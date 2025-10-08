from window import Chip8Window
import time
import pygame
from file_browser import select_rom_file
import random


# Chip-8 fontset (0-F)
fontset = [
    0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
    0x20, 0x60, 0x20, 0x20, 0x70,  # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
    0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
    0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
    0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
    0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
    0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
    0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
    0xF0, 0x80, 0xF0, 0x80, 0x80   # F
]


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
        self.draw_flag = False

        # Load fontset
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
        self.draw_flag = False

        # Load fontset into memory at 0x50
        self.memory[0x50:0x50 + len(fontset)] = fontset
    
    def load_program(self, filename):
        with open(filename, "rb") as f:
            program = f.read()
        self.memory[0x200:0x200+len(program)] = program
    
    def update_timers(self):
        """Decrement timers at 60Hz"""
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1
    
    def emulation_cycle(self):
        # Fetch
        opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]

        # Decode and Execute
        match (opcode & 0xF000):

            case (0x0000):
                match (opcode & 0x00FF):
                    case (0x00E0):  # CLS
                        self.gfx = [0] * (64 * 32)
                        self.draw_flag = True
                        self.pc += 2
                    case (0x00EE):  # RET
                        if len(self.stack) == 0:
                            print("⚠️ Stack underflow: RET without CALL")
                            self.pc += 2
                            return
                        self.pc = self.stack.pop()
                        print(f"RET → PC={self.pc:03X}")
                    case (_):
                        print(f"Unknown opcode [0x0000]: 0x{opcode:X}")
                        self.pc += 2
            
            case (0x1000):  # JP addr
                nnn = opcode & 0x0FFF
                self.pc = nnn
                print(f"JP {nnn:03X}")

            case (0x2000):  # CALL addr
                nnn = opcode & 0x0FFF
                self.stack.append(self.pc + 2)
                self.pc = nnn
                print(f"CALL {nnn:03X} (return address = {self.pc - 2 + 2:03X})")
            
            case (0x3000):  # SE Vx, byte
                x = (opcode & 0x0F00) >> 8
                nn = opcode & 0x00FF
                if self.V[x] == nn:
                    self.pc += 4
                else:
                    self.pc += 2
                print(f"SE V{x:X}, {nn:02X} → {'skip' if self.V[x] == nn else 'no skip'}")
            
            case (0x4000):  # SNE Vx, byte
                x = (opcode & 0x0F00) >> 8
                nn = opcode & 0x00FF
                if self.V[x] != nn:
                    self.pc += 4
                    skipped = True
                else:
                    self.pc += 2
                    skipped = False
                print(f"SNE V{x:X}, {nn:02X} → {'skip' if skipped else 'no skip'}")
            
            case (0x5000):  # SE Vx, Vy
                x = (opcode & 0x0F00) >> 8
                y = (opcode & 0x00F0) >> 4
                if self.V[x] == self.V[y]:
                    self.pc += 4
                    skipped = True
                else:
                    self.pc += 2
                    skipped = False
                print(f"SE V{x:X}, V{y:X} → {'skip' if skipped else 'no skip'}")

            case (0x6000):  # LD Vx, byte
                x = (opcode & 0x0F00) >> 8
                nn = opcode & 0x00FF
                self.V[x] = nn
                self.pc += 2
                print(f"LD V{x:X} = {nn:02X}")
            
            case (0x7000):  # ADD Vx, byte
                x = (opcode & 0x0F00) >> 8
                nn = opcode & 0x00FF
                self.V[x] = (self.V[x] + nn) & 0xFF
                self.pc += 2
                print(f"ADD V{x:X} += {nn:02X} → V{x:X}={self.V[x]:02X}")

            case (0x8000):
                x = (opcode & 0x0F00) >> 8
                y = (opcode & 0x00F0) >> 4
                match (opcode & 0x000F):
                    case (0x0000):  # LD Vx, Vy
                        self.V[x] = self.V[y]
                        self.pc += 2
                    
                    case (0x0001):  # OR Vx, Vy
                        self.V[x] |= self.V[y]
                        self.pc += 2
                        print(f"OR V{x:X}, V{y:X} → V{x:X}={self.V[x]:02X}")

                    case (0x0002):  # AND Vx, Vy
                        self.V[x] &= self.V[y]
                        self.pc += 2
                        print(f"AND V{x:X}, V{y:X} → V{x:X}={self.V[x]:02X}")

                    case (0x0003):  # XOR Vx, Vy
                        self.V[x] ^= self.V[y]
                        self.pc += 2
                        print(f"XOR V{x:X}, V{y:X} → V{x:X}={self.V[x]:02X}")
                    
                    case (0x0004):  # ADD Vx, Vy
                        result = self.V[x] + self.V[y]
                        self.V[0xF] = 1 if result > 0xFF else 0
                        self.V[x] = result & 0xFF
                        self.pc += 2
                        print(f"ADD V{x:X}, V{y:X} → V{x:X}={self.V[x]:02X}, VF={self.V[0xF]}")

                    case (0x0005):  # SUB Vx, Vy
                        self.V[0xF] = 1 if self.V[x] >= self.V[y] else 0
                        self.V[x] = (self.V[x] - self.V[y]) & 0xFF
                        self.pc += 2
                        print(f"SUB V{x:X}, V{y:X} → V{x:X}={self.V[x]:02X}, VF={self.V[0xF]}")
                    
                    case (0x0006):  # SHR Vx {, Vy}
                        self.V[0xF] = self.V[x] & 0x1
                        self.V[x] >>= 1
                        self.pc += 2
                    
                    case (0x0007):  # SUBN Vx, Vy
                        self.V[0xF] = 1 if self.V[y] >= self.V[x] else 0
                        self.V[x] = (self.V[y] - self.V[x]) & 0xFF
                        self.pc += 2
                        print(f"SUBN V{x:X}, V{y:X} → V{x:X}={self.V[x]:02X}, VF={self.V[0xF]}")
                    
                    case (0x000E):  # SHL Vx {, Vy}
                        self.V[0xF] = (self.V[x] & 0x80) >> 7
                        self.V[x] = (self.V[x] << 1) & 0xFF
                        self.pc += 2
                        print(f"SHL V{x:X} → V{x:X}={self.V[x]:02X}, VF={self.V[0xF]}")

                    case (_):
                        print(f"Unknown opcode [0x8000]: 0x{opcode:X}")
                        self.pc += 2
            
            case (0x9000):  # SNE Vx, Vy
                x = (opcode & 0x0F00) >> 8
                y = (opcode & 0x00F0) >> 4
                if self.V[x] != self.V[y]:
                    self.pc += 4
                    skipped = True
                else:
                    self.pc += 2
                    skipped = False
                print(f"SNE V{x:X}, V{y:X} → {'skip' if skipped else 'no skip'}")
                    
            case (0xA000):  # LD I, addr
                nnn = opcode & 0x0FFF
                self.I = nnn
                self.pc += 2
                print(f"LD I = {nnn:03X}")
            
            case (0xC000):  # RND Vx, byte
                x = (opcode & 0x0F00) >> 8
                nn = opcode & 0x00FF
                rnd = random.randint(0, 255)
                self.V[x] = rnd & nn
                print(f"RND V{x:X} = {rnd} & {nn:02X} → {self.V[x]}")
                self.pc += 2
            
            case (0xD000):  # DRW Vx, Vy, nibble
                x = self.V[(opcode & 0x0F00) >> 8] % 64
                y = self.V[(opcode & 0x00F0) >> 4] % 32
                height = opcode & 0x000F
                self.V[0xF] = 0

                for yline in range(height):
                    pixel = self.memory[self.I + yline]
                    for xline in range(8):
                        if pixel & (0x80 >> xline):
                            index = (x + xline + ((y + yline) * 64)) % len(self.gfx)
                            if self.gfx[index] == 1:
                                self.V[0xF] = 1
                            self.gfx[index] ^= 1
                
                self.draw_flag = True
                self.pc += 2
            
            case (0xE000):
                x = (opcode & 0x0F00) >> 8
                match (opcode & 0x00FF):
                    case (0x009E):  # SKP Vx
                        if self.key[self.V[x]]:
                            self.pc += 4
                        else:
                            self.pc += 2
                        print(f"SKP V{x:X} (key={self.V[x]:X}) → {'skip' if self.key[self.V[x]] else 'no skip'}")
                    
                    case (0x00A1):  # SKNP Vx
                        if not self.key[self.V[x]]:
                            self.pc += 4
                        else:
                            self.pc += 2
                        print(f"SKNP V{x:X} (key={self.V[x]:X}) → {'skip' if not self.key[self.V[x]] else 'no skip'}")
                    
                    case (_):
                        print(f"Unknown opcode [0xE000]: 0x{opcode:X}")
                        self.pc += 2
            
            case (0xF000):
                x = (opcode & 0x0F00) >> 8
                match (opcode & 0x00FF):
                    case (0x0007):  # LD Vx, DT
                        self.V[x] = self.delay_timer
                        print(f"LD V{x:X}, DT ({self.delay_timer})")
                        self.pc += 2
                    
                    case (0x000A):  # LD Vx, K (wait for key)
                        key_pressed = None
                        for i in range(16):
                            if self.key[i] != 0:
                                self.V[x] = i
                                key_pressed = i
                                break

                        if key_pressed is None:
                            return  # Don't increment PC, wait for key
                        else:
                            print(f"LD V{x:X}, K → key {key_pressed:X}")
                            self.pc += 2
                    
                    case (0x0015):  # LD DT, Vx
                        self.delay_timer = self.V[x]
                        print(f"LD DT, V{x:X} ({self.V[x]})")
                        self.pc += 2
                    
                    case (0x0018):  # LD ST, Vx
                        self.sound_timer = self.V[x]
                        print(f"LD ST, V{x:X} ({self.V[x]})")
                        self.pc += 2
                    
                    case (0x001E):  # ADD I, Vx
                        self.I += self.V[x]
                        self.pc += 2
                        print(f"ADD I, V{x:X} → I={self.I:03X}")
                    
                    case (0x0029):  # LD F, Vx
                        self.I = 0x50 + (self.V[x] * 5)
                        self.pc += 2
                        print(f"LD F, V{x:X} → I={self.I:03X}")
                    
                    case (0x0033):  # LD B, Vx (BCD)
                        value = self.V[x]
                        self.memory[self.I]     = value // 100
                        self.memory[self.I + 1] = (value // 10) % 10
                        self.memory[self.I + 2] = value % 10
                        self.pc += 2
                        print(f"LD B, V{x:X} ({value}) → [{self.I:03X}]")

                    case (0x0055):  # LD [I], Vx
                        for i in range(x + 1):
                            self.memory[self.I + i] = self.V[i]
                        self.pc += 2
                        print(f"LD [I], V{x:X}")

                    case (0x0065):  # LD Vx, [I]
                        for i in range(x + 1):
                            self.V[i] = self.memory[self.I + i]
                        self.pc += 2
                        print(f"LD V{x:X}, [I]")

                    case (_):
                        print(f"Unknown opcode [0xF000]: 0x{opcode:X}")
                        self.pc += 2

            case (_):
                print(f"Unknown opcode: 0x{opcode:X}")
                self.pc += 2


def main():
    print("🎮 Chip-8 Emulator")
    print("Select a ROM...")
    
    rom_file = select_rom_file()
    
    if rom_file is None:
        print("❌ No file has been selected. Closing...")
        sys.exit(0)
    
    print(f"✅ Chargement de: {rom_file}")
    
    chip8 = Chip8()
    
    try:
        chip8.load_program(rom_file)
    except Exception as e:
        print(f"❌ Error when loading ROM: {e}")
        sys.exit(1)
    
    window = Chip8Window()
    
    running = True
    timer_counter = 0
    
    print("🚀 Emulation Start")
    print("Press Ctrl+C or Close the window for quit")
    
    while running:
        running = window.handle_events(chip8)
        chip8.emulation_cycle()
        
        timer_counter += 1
        if timer_counter >= 10:
            chip8.update_timers()
            timer_counter = 0
        
        if chip8.draw_flag:
            window.draw(chip8)
            chip8.draw_flag = False
        
        time.sleep(0.001)
    
    print("👋 Closing of the emulator...")
    pygame.quit()


if __name__ == "__main__":
    main()