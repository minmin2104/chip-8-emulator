import pygame
from chip8 import Chip8
import sys


CHIP_8_DISPLAY = (64, 32)
SCALE = 16
KEYMAP = [
    pygame.K_x,  # 0
    pygame.K_1,  # 1
    pygame.K_2,  # 2
    pygame.K_3,  # 3
    pygame.K_q,  # 4
    pygame.K_w,  # 5
    pygame.K_e,  # 6
    pygame.K_a,  # 7
    pygame.K_s,  # 8
    pygame.K_d,  # 9
    pygame.K_z,  # A
    pygame.K_c,  # B
    pygame.K_4,  # C
    pygame.K_r,  # D
    pygame.K_f,  # E
    pygame.K_v,  # F
]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: chip8 <rom file>")
        sys.exit(1)
    pygame.init()
    win_size = (CHIP_8_DISPLAY[0] * SCALE, CHIP_8_DISPLAY[1] * SCALE)
    screen = pygame.display.set_mode(win_size)
    clock = pygame.time.Clock()

    chip_8 = Chip8()
    try:
        chip_8.load_ROM(sys.argv[1])
    except Exception as e:
        print(f"Failed to load ROM: {e}")
        sys.exit(1)

    running = True
    while running:
        chip_8.emulate_cycle()

        if chip_8.draw_flag:
            screen.fill((0, 0, 0))
            for i in range(2048):
                x = i % 64
                y = i // 64
                color = (255, 255, 255) if chip_8.gfx[i] == 1 else (0, 0, 0)
                pygame.draw.rect(screen, color, (x * SCALE, y * SCALE, SCALE,
                                                 SCALE))
            pygame.display.flip()
            chip_8.draw_flag = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                for i, key_code in enumerate(KEYMAP):
                    if event.key == key_code:
                        chip_8.key[i] = 1
            elif event.type == pygame.KEYUP:
                for i, key_code in enumerate(KEYMAP):
                    if event.key == key_code:
                        chip_8.key[i] = 0

        # Handle timer
        if chip_8.delay_timer > 0:
            chip_8.delay_timer -= 1
        if chip_8.sound_timer > 0:
            chip_8.sound_timer -= 1
            if chip_8.sound_timer == 0:
                print("BEEP!")
        clock.tick(833)
