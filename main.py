import pygame
import sys
import subprocess
import random

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Main Menu")

font_size = int(HEIGHT * 0.05)
font = pygame.font.SysFont("arial", font_size, bold=True)
clock = pygame.time.Clock()

def run_game(game_file):
    subprocess.run([sys.executable, game_file], creationflags=subprocess.CREATE_NO_WINDOW)

options = [
    ("Mars Level", (255, 100, 100)),
    ("Moon Level", (200, 200, 255)),
    ("Earth Level", (100, 255, 100)),
    ("Quit", (180, 180, 180))
]

MAX_CHOICES = len(options)
choice = 1

title_y = int(HEIGHT * 0.1)
option_start_y = int(HEIGHT * 0.35)
option_spacing = int(HEIGHT * 0.1)
highlight_padding_x = int(WIDTH * 0.035)
highlight_padding_y = int(HEIGHT * 0.02)

# Lock star layout to be consistent every run
random.seed(42)
NUM_STARS = 200
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(NUM_STARS)]

alien_img = pygame.image.load("assets/alien.png").convert_alpha()
alien_img = pygame.transform.scale(alien_img, (60, 60))
alien_rect = alien_img.get_rect(topleft=(60, 60))
alien_rect.center = (WIDTH*0.05, HEIGHT*0.1)

satellite_img = pygame.image.load("assets/satellite.png").convert_alpha()
satellite_img = pygame.transform.scale(satellite_img, (120, 140))
satellite_rect = satellite_img.get_rect()
satellite_rect.center = (WIDTH*0.9, HEIGHT*0.2)

alien2_img = pygame.image.load("assets/alien2.png").convert_alpha()
alien2_img = pygame.transform.scale(alien2_img, (60, 60))
alien2_rect = alien2_img.get_rect()
alien2_rect.center = (WIDTH * 0.15, HEIGHT * 0.75)

jump_img = pygame.image.load("assets/jump.png").convert_alpha()
jump_img = pygame.transform.scale(jump_img, (70, 70))
jump_rect = jump_img.get_rect()
jump_rect.center = (WIDTH * 0.4, HEIGHT * 0.8)

meteor_img = pygame.image.load("assets/meteor.png").convert_alpha()
meteor_img = pygame.transform.scale(meteor_img, (100, 200))
meteor_rect = meteor_img.get_rect()
meteor_rect.center = (WIDTH*0.04, HEIGHT * 0.4)

player_img = pygame.image.load("assets/player.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (20, 20))
player_rect = player_img.get_rect()
player_rect.center = (WIDTH * 0.95, HEIGHT * 0.95)

while True:
    screen.fill((10, 10, 30))  # Night sky background

    for star in stars:
        pygame.draw.circle(screen, (255, 255, 255), star, 1)

    screen.blit(alien_img, alien_rect)
    screen.blit(satellite_img, satellite_rect)
    screen.blit(alien2_img, alien2_rect)
    screen.blit(jump_img, jump_rect)
    screen.blit(meteor_img, meteor_rect)
    screen.blit(player_img, player_rect)
    
    title_text = font.render("Choose an Option", True, (255, 255, 255))
    title_shadow = font.render("Choose an Option", True, (0, 0, 0))
    title_rect = title_text.get_rect(center=(WIDTH // 2, title_y))
    screen.blit(title_shadow, title_rect.move(2, 2))
    screen.blit(title_text, title_rect)

    max_text_width = max(font.render(text, True, color).get_width() for text, color in options)
    rect_width = max_text_width + highlight_padding_x * 2
    rect_height = font_size + highlight_padding_y * 2

    for i, (text, color) in enumerate(options):
        y = option_start_y + i * option_spacing
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, y))

        if choice == i + 1:
            rect_x = (WIDTH - rect_width) // 2
            rect_y = y - rect_height // 2
            highlight_rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)
            pygame.draw.rect(screen, (80, 80, 80), highlight_rect, border_radius=14)

        screen.blit(text_surface, text_rect)

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
                pygame.display.set_mode((WIDTH, HEIGHT))  
                pygame.quit()
                if choice == 1:
                    run_game("mars.py")
                elif choice == 2:
                    run_game("moon.py")
                elif choice == 3:
                    run_game("earth.py")
                elif choice == 4:
                    sys.exit()
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    pygame.display.flip()
    clock.tick(60)
