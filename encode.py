test_rom = bytes([
    0x00, 0xE0,       # CLS : Clear screen (at start)
    0x60, 0x00,       # LD V0, 0 : X
    0x61, 0x00,       # LD V1, 0 : Y

    # loop:
    0x00, 0xE0,       # CLS each iteration
    0xF0, 0x0A,       # LD V0, K : wait for key
    0xD0, 0x15,       # DRW V0,V1,5 : draw sprite
    0x12, 0x06        # JP 0x206 : jump back to loop
])

with open("test_keys.ch8", "wb") as f:
    f.write(test_rom)

print("✅ Saved as test_keys.ch8")
