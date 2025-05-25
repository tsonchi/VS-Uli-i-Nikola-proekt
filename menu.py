import pygame
import sys
import subprocess

pygame.init()
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Main Menu")
font = pygame.font.SysFont(None, 40)
clock = pygame.time.Clock()

def run_game(game_file):
    # Стартира друг python файл (играта)
    subprocess.run([sys.executable, game_file])

while True:
    screen.fill((30, 30, 30))
    title = font.render("Choose your planet:", True, (255, 255, 255))
    mars = font.render("[1] Mars", True, (255, 0, 0))
    moon = font.render("[2] Moon", True, (200, 200, 200))
    earth = font.render("[3] Earth", True, (0, 255, 0))
    quit_text = font.render("Press ESC to Quit", True, (180, 180, 180))

    screen.blit(title, (180, 50))
    screen.blit(mars, (250, 150))
    screen.blit(moon, (250, 200))
    screen.blit(earth, (250, 250))
    screen.blit(quit_text, (180, 350))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        pygame.quit()
        sys.exit()
    if keys[pygame.K_1]:
        run_game("mars.py")
    if keys[pygame.K_2]:
        run_game("moon.py")
    if keys[pygame.K_3]:
        run_game("earth.py")

    pygame.display.flip()
    clock.tick(60)
