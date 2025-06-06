import pygame
import sys
import subprocess
import random
import math

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Main Menu")

try:
    pygame.mixer.init()
except pygame.error:
    print("Warning: Mixer failed to initialize.")

target_volume = 0.07
current_volume = 0.0
fade_in_speed = 0.0005 
music_started = False

jump_sound = pygame.mixer.Sound("audio/jump.mp3")
jump_sound.set_volume(0.05)
jump_sound.play()

pygame.time.set_timer(pygame.USEREVENT, int(jump_sound.get_length() * 1000))


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

random.seed(42)
NUM_STARS = 420
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

fade_surface = pygame.Surface((WIDTH, HEIGHT))
fade_surface.fill((0, 0, 0))
fade_alpha = 255
fade_speed = 4

def fade_out(screen, clock, fade_speed):
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill((0, 0, 0))
    alpha = 0

    while alpha < 255:
        screen.fill((10, 10, 30))

        # Redraw all game elements (background, stars, etc.)
        for star in stars:
            pygame.draw.circle(screen, (255, 255, 255), star, 1)
        screen.blit(alien_img, alien_rect)
        screen.blit(satellite_img, satellite_rect)
        screen.blit(alien2_img, alien2_rect)
        screen.blit(jump_img, jump_rect)
        screen.blit(meteor_img, meteor_rect)
        screen.blit(player_img, player_rect)

        # Redraw the menu text
        for i, line in enumerate(title_lines):
            text = font.render(line, True, (255, 255, 255))
            shadow = font.render(line, True, (0, 0, 0))
            text_rect = text.get_rect(center=(WIDTH // 2, title_y + i * (font_size + 10)))
            screen.blit(shadow, text_rect.move(2, 2))
            screen.blit(text, text_rect)

        for i, (text, color) in enumerate(options):
            y = option_start_y + i * option_spacing
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, y))

            if choice == i + 1:
                rect_x = (WIDTH - rect_width) // 2
                rect_y = y - rect_height // 2
                highlight_rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)
                pulse = int(60 + 40 * math.sin(pygame.time.get_ticks() * 0.005))
                color = (pulse, pulse, pulse)
                pygame.draw.rect(screen, color, highlight_rect, border_radius=14)

            screen.blit(text_surface, text_rect)

        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        alpha += fade_speed
        clock.tick(60)

while True:
    screen.fill((10, 10, 30))

    for star in stars:
        pygame.draw.circle(screen, (255, 255, 255), star, 1)

    screen.blit(alien_img, alien_rect)
    screen.blit(satellite_img, satellite_rect)
    screen.blit(alien2_img, alien2_rect)
    screen.blit(jump_img, jump_rect)
    screen.blit(meteor_img, meteor_rect)
    screen.blit(player_img, player_rect)

    title_lines = [
        "Navigate With UP and DOWN",
        "And Choose An Option with ENTER"
    ]

    for i, line in enumerate(title_lines):
        text = font.render(line, True, (255, 255, 255))
        shadow = font.render(line, True, (0, 0, 0))
        text_rect = text.get_rect(center=(WIDTH // 2, title_y + i * (font_size + 10)))
        screen.blit(shadow, text_rect.move(2, 2))
        screen.blit(text, text_rect)

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
            pulse = int(60 + 40 * math.sin(pygame.time.get_ticks() * 0.005))
            color = (pulse, pulse, pulse)
            pygame.draw.rect(screen, color, highlight_rect, border_radius=14)

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
                if choice == 1:
                    next_game = "mars.py"
                elif choice == 2:
                    next_game = "moon.py"
                elif choice == 3:
                    next_game = "earth.py"
                elif choice == 4:
                    pygame.quit()
                    sys.exit()

                fade_out(screen, clock, fade_speed=4)
                if choice == 1:
                    pygame.mixer.music.stop()  # Stop any current music
                    import mars
                    mars.main()
                elif choice == 2:
                    pygame.mixer.music.stop()
                    import moon
                    moon.menu()
                elif choice == 3:
                    pygame.mixer.music.stop()
                    import earth
                    earth.menu()

            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        elif event.type == pygame.USEREVENT and not music_started:
            pygame.mixer.music.load("audio/title.wav")
            pygame.mixer.music.set_volume(0.0)
            pygame.mixer.music.play(-1)
            music_started = True

    if music_started and current_volume < target_volume:
        current_volume = min(current_volume + fade_in_speed, target_volume)
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(current_volume)

    if fade_alpha > 0:
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0, 0))
        fade_alpha -= fade_speed

    pygame.display.flip()
    clock.tick(60)
