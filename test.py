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
    subprocess.run([sys.executable, game_file])

MAX_CHOICES = 4
choice = 1 

options = ["[1] Mars", "[2] Moon", "[3] Earth", "[4] Quit"]
positions = [150, 200, 250, 300]  # y

while True:
    screen.fill((30, 30, 30))
    title = font.render("Choose your planet:", True, (255, 255, 255))

    screen.blit(title, (180, 50))

    for i, text in enumerate(options):
        y = positions[i]
        if choice == i + 1:
            pygame.draw.rect(screen, (60, 60, 60), (240, y - 5, 300, 40), border_radius=6)
        color = (255, 255, 255)
        rendered = font.render(text, True, color)
        screen.blit(rendered, (250, y))

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
                    run_game("mars.py")
                elif choice == 2:
                    run_game("moon.py")
                elif choice == 3:
                    run_game("earth.py")
                elif choice == 4:  
                    pygame.quit()
                    sys.exit()

            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    pygame.display.flip()
    clock.tick(60)
