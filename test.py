import pygame
import sys
import subprocess

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)

pygame.display.set_caption("Main Menu")

font_size = int(HEIGHT * 0.05)
font = pygame.font.SysFont(None, font_size)
clock = pygame.time.Clock()

def run_game(game_file):
    subprocess.run([sys.executable, game_file], creationflags=subprocess.CREATE_NO_WINDOW)

options = ["[1] Mars", "[2] Moon", "[3] Earth", "[4] Quit"]
MAX_CHOICES = len(options)
choice = 1

title_y = int(HEIGHT * 0.1)
option_start_y = int(HEIGHT * 0.35)
option_spacing = int(HEIGHT * 0.1)
highlight_padding_x = int(WIDTH * 0.04)
highlight_padding_y = int(HEIGHT * 0.02)

while True:
    screen.fill((30, 30, 30))

    title_text = font.render("Choose your planet:", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(WIDTH // 2, title_y))
    screen.blit(title_text, title_rect)

    for i, text in enumerate(options):
        y = option_start_y + i * option_spacing
        if choice == i + 1:
            highlight_rect = pygame.Rect(
                title_rect.left - highlight_padding_x,
                y - highlight_padding_y,
                title_rect.width + highlight_padding_x * 2,
                font_size + highlight_padding_y * 2
            )
            pygame.draw.rect(screen, (60, 60, 60), highlight_rect, border_radius=10)
        rendered_text = font.render(text, True, (255, 255, 255))
        text_rect = rendered_text.get_rect(center=(WIDTH // 2, y))
        screen.blit(rendered_text, text_rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                choice += 1
                if choice > MAX_CHOICES:
                    choice = 1
            elif event.key == pygame.K_UP:
                choice -= 1
                if choice < 1:
                    choice = MAX_CHOICES
            elif event.key == pygame.K_RETURN:
                
                if choice == 1:
                    pygame.display.set_mode((WIDTH, HEIGHT))
                    pygame.quit()
                    run_game("mars.py")
                    sys.exit()
                elif choice == 2:
                    pygame.display.set_mode((WIDTH, HEIGHT))
                    pygame.quit()
                    run_game("moon.py")
                    sys.exit()
                elif choice == 3:
                    pygame.display.set_mode((WIDTH, HEIGHT))
                    pygame.quit()
                    run_game("earth.py")
                    sys.exit()
                elif choice == 4:
                    pygame.display.set_mode((WIDTH, HEIGHT))
                    pygame.quit()
                    sys.exit()

            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    pygame.display.flip()
    clock.tick(60)
