import pygame

SCALE = 10
WIDTH, HEIGHT = 64, 32

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

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True
