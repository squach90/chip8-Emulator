import sys

# --- Table de décodage simple ---
def decode_opcode(opcode):
    nnn = opcode & 0x0FFF
    n   = opcode & 0x000F
    x   = (opcode & 0x0F00) >> 8
    y   = (opcode & 0x00F0) >> 4
    nn  = opcode & 0x00FF

    if opcode == 0x00E0:
        return "CLS"
    elif opcode == 0x00EE:
        return "RET"
    elif opcode & 0xF000 == 0x1000:
        return f"JP {nnn:03X}"
    elif opcode & 0xF000 == 0x2000:
        return f"CALL {nnn:03X}"
    elif opcode & 0xF000 == 0x3000:
        return f"SE V{x:X}, {nn:02X}"
    elif opcode & 0xF000 == 0x4000:
        return f"SNE V{x:X}, {nn:02X}"
    elif opcode & 0xF000 == 0x5000:
        return f"SE V{x:X}, V{y:X}"
    elif opcode & 0xF000 == 0x6000:
        return f"LD V{x:X}, {nn:02X}"
    elif opcode & 0xF000 == 0x7000:
        return f"ADD V{x:X}, {nn:02X}"
    elif opcode & 0xF000 == 0x8000:
        last_nibble = opcode & 0x000F
        if last_nibble == 0x0:
            return f"LD V{x:X}, V{y:X}"
        elif last_nibble == 0x4:
            return f"ADD V{x:X}, V{y:X}"
        else:
            return f"UNKNOWN 8XY{last_nibble:X}"
    elif opcode & 0xF000 == 0xA000:
        return f"LD I, {nnn:03X}"
    elif opcode & 0xF000 == 0xD000:
        height = opcode & 0x000F
        return f"DRW V{x:X}, V{y:X}, {height:X}"
    elif opcode & 0xF000 == 0xF000:
        if nn == 0x33:
            return f"LD B, V{x:X}"
        else:
            return f"UNKNOWN FX{nn:02X}"
    else:
        return f"UNKNOWN {opcode:04X}"

# --- Script principal ---
if len(sys.argv) != 3:
    print("Usage: python3 decoder_ch8.py input.ch8 output.txt")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, "rb") as f:
    rom = f.read()

opcodes = []
for i in range(0, len(rom), 2):
    opcode = (rom[i] << 8) | rom[i + 1]
    opcodes.append(opcode)

with open(output_file, "w") as f:
    for pc, opcode in enumerate(opcodes):
        addr = 0x200 + pc*2
        decoded = decode_opcode(opcode)
        f.write(f"{addr:03X}: {opcode:04X}  {decoded}\n")

print(f"Decoded {len(opcodes)} instructions into {output_file}")
