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
        match(opcode & 0xF000):
            case (0xA000):
                self.I = opcode & 0x0FFF
                self.pc += 2  # avance le compteur de programme
            case (_):  # équivalent du "default"
                print(f"Unknown opcode: 0x{opcode:X}")

        # Update timers
        if self.delay_timer > 0:
            self.delay_timer -= 1

        if self.sound_timer > 0:
            if self.sound_timer == 1:
                print("BEEP!")
            self.sound_timer -= 1

# # === TEST ===   
# # Example fontset (just zeros for testing, replace with actual fontset if needed)
# fontset = [0] * 80  

# # Create emulator instance
# chip8 = Chip8()

# # Example program: sets I to 0x300 (opcode A300) then 0x500 (opcode A500)
# program_bytes = bytes([
#     0xA3, 0x00,   # Set I = 0x300
#     0xA5, 0x00    # Set I = 0x500
# ])

# # Load the program into memory
# chip8.memory[0x200:0x200+len(program_bytes)] = program_bytes

# # Check initial state
# print(f"Initial I: {chip8.I}, PC: {chip8.pc}")

# # Run multiple emulation cycles and print state each time
# for cycle in range(4):
#     print(f"\nCycle {cycle+1}:")
#     chip8.emulation_cycle()
#     print(f"I = {chip8.I:03X}, PC = {chip8.pc:03X}")
