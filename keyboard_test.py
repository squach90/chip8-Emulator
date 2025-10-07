import pygame
from main import Chip8  # ton émulateur

# Mappage des touches clavier vers le clavier CHIP-8
KEY_MAP = {
    pygame.K_x: 0x0,
    pygame.K_1: 0x1,
    pygame.K_2: 0x2,
    pygame.K_3: 0x3,
    pygame.K_q: 0x4,
    pygame.K_w: 0x5,
    pygame.K_e: 0x6,
    pygame.K_a: 0x7,
    pygame.K_s: 0x8,
    pygame.K_d: 0x9,
    pygame.K_z: 0xA,
    pygame.K_c: 0xB,
    pygame.K_4: 0xC,
    pygame.K_r: 0xD,
    pygame.K_f: 0xE,
    pygame.K_v: 0xF,
}

# Initialisation
pygame.init()
WIDTH, HEIGHT = 64 * 10, 32 * 10  # écran grossi pour voir les pixels
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CHIP-8 Keyboard Test")
clock = pygame.time.Clock()

chip8 = Chip8()
chip8.initialize()

running = True
while running:
    screen.fill((0, 0, 0))  # fond noir

    # Gère les événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key in KEY_MAP:
                key = KEY_MAP[event.key]
                chip8.key[key] = 1
                print(f"Touche pressée: {key:X}")

        elif event.type == pygame.KEYUP:
            if event.key in KEY_MAP:
                key = KEY_MAP[event.key]
                chip8.key[key] = 0
                print(f"Touche relâchée: {key:X}")

    # Dessine les pixels
    for y in range(32):
        for x in range(64):
            if chip8.gfx[x + y * 64]:
                pygame.draw.rect(screen, (255, 255, 255),
                                 (x*10, y*10, 10, 10))

    pygame.display.flip()
    clock.tick(60)  # limite à 60 FPS

pygame.quit()
