import pygame
import sys

pygame.init()
WIDTH, HEIGHT = 1200, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mars Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

PLAYER_SPEED = 5
GRAVITY = 0.3
JUMP_STRENGTH = -9
OXYGEN_DECREASE_RATE = 0.1

player = pygame.Rect(100, 500, 40, 50)
velocity_y = 0
on_ground = False
oxygen = 100
game_over = False
game_win = False

platforms = [
    pygame.Rect(0, 580, 4000, 20),
    pygame.Rect(200, 450, 150, 20),
    pygame.Rect(450, 350, 150, 20),
    pygame.Rect(900, 300, 150, 20),
    pygame.Rect(1300, 250, 150, 20),
    pygame.Rect(1600, 200, 150, 20),
]

water = pygame.Rect(1650, 160, 30, 40)
alien = pygame.Rect(300, 400, 40, 50)

alien_image = pygame.image.load("image.png").convert_alpha()
alien_image = pygame.transform.scale(alien_image, (50, 50))
camera_x = 0

def reset_game():
    global player, velocity_y, oxygen, game_over, game_win, camera_x
    player.x, player.y = 100, 500
    velocity_y = 0
    oxygen = 100
    game_over = False
    game_win = False
    camera_x = 0

while True:
    screen.fill((153, 76, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    if keys[pygame.K_ESCAPE]:
        pygame.quit()
        sys.exit()

    if not game_over and not game_win:
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = PLAYER_SPEED
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and on_ground:
            velocity_y = JUMP_STRENGTH
            on_ground = False
        if keys[pygame.K_r]:
            reset_game()


        velocity_y += GRAVITY
        player.y += velocity_y
        player.x += dx

        on_ground = False
        for platform in platforms:
            if player.colliderect(platform):
                if velocity_y > 0 and player.bottom <= platform.bottom:
                    player.bottom = platform.top
                    velocity_y = 0
                    on_ground = True

        oxygen -= OXYGEN_DECREASE_RATE
        if oxygen <= 0:
            game_over = True

        if player.colliderect(alien):
            game_over = True
        if player.colliderect(water):
            game_win = True

        if player.x > WIDTH // 2:
            camera_x = player.x - WIDTH // 2
        else:
            camera_x = 0

    for platform in platforms:
        pygame.draw.rect(screen, (50, 50, 50), (platform.x - camera_x, platform.y, platform.width, platform.height))

    pygame.draw.rect(screen, (0, 0, 0), (player.x - camera_x, player.y, player.width, player.height))
    screen.blit(alien_image, (alien.x - camera_x, alien.y))
    pygame.draw.rect(screen, (0, 100, 255), (water.x - camera_x, water.y, water.width, water.height))

    pygame.draw.rect(screen, (255, 255, 255), (20, 20, 200, 20))
    pygame.draw.rect(screen, (0, 100, 255), (20, 20, max(0, int(oxygen * 2)), 20))
    oxy_text = font.render("Oxygen", True, (0, 0, 0))
    screen.blit(oxy_text, (230, 17))

    if game_over:
        msg = font.render("Game Over!", True, (255, 255, 255))
        screen.blit(msg, (WIDTH // 2 - 100, HEIGHT // 2))
    elif game_win:
        msg = font.render("You Win!", True, (255, 255, 255))
        screen.blit(msg, (WIDTH // 2 - 100, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(60)
