import pygame

SCALE = 10
WIDTH, HEIGHT = 64, 32

key_map = {
    pygame.K_1: 0x1,
    pygame.K_2: 0x2,
    pygame.K_3: 0x3,
    pygame.K_4: 0xC,
    pygame.K_q: 0x4,
    pygame.K_w: 0x5,
    pygame.K_e: 0x6,
    pygame.K_r: 0xD,
    pygame.K_a: 0x7,
    pygame.K_s: 0x8,
    pygame.K_d: 0x9,
    pygame.K_f: 0xE,
    pygame.K_z: 0xA,
    pygame.K_x: 0x0,
    pygame.K_c: 0xB,
    pygame.K_v: 0xF,
}

class Chip8Window:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH*SCALE, HEIGHT*SCALE))
        pygame.display.set_caption("Chip8 Emulator")

    def draw(self, chip8):
        self.screen.fill((0, 0, 0))
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if chip8.gfx[x + y*WIDTH]:
                    pygame.draw.rect(self.screen, (255, 255, 255),
                                     (x*SCALE, y*SCALE, SCALE, SCALE))
        pygame.display.flip()

    def handle_events(self, chip8):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key in key_map:
                    chip8.key[key_map[event.key]] = 1
            elif event.type == pygame.KEYUP:
                if event.key in key_map:
                    chip8.key[key_map[event.key]] = 0
        return True
