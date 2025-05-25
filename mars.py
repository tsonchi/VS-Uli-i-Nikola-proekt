import pygame, sys, random

pygame.init()
WIDTH, HEIGHT = 1200, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mars Escape")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Load images
player_img = pygame.image.load("assets/player.png")
player_img = pygame.transform.scale(player_img, (40, 50))

alien_img = pygame.image.load("assets/alien.png")
alien_img = pygame.transform.scale(alien_img, (60, 60))

water_img = pygame.image.load("assets/water.png")
water_img = pygame.transform.scale(water_img, (30, 40))

volcano_img = pygame.image.load("assets/volcano.png")
volcano_img = pygame.transform.scale(volcano_img, (80, 80))

fireball_img = pygame.image.load("assets/fireball.png")
fireball_img = pygame.transform.scale(fireball_img, (20, 20))

# Game constants
PLAYER_SPEED = 5
GRAVITY = 0.3
JUMP_STRENGTH = -9
OXYGEN_DECREASE = 0.1

# Player
player = pygame.Rect(100, 500, 40, 50)
velocity_y = 0
on_ground = False
oxygen = 100
game_over = False
game_win = False

# Level setup
platforms = [
    pygame.Rect(0, 580, 4000, 20),
    pygame.Rect(200, 450, 200, 20),
    pygame.Rect(500, 400, 300, 20),
    pygame.Rect(900, 350, 150, 20),
    pygame.Rect(1200, 300, 150, 20),
    pygame.Rect(1500, 250, 300, 20),
    pygame.Rect(1900, 300, 200, 20),
    pygame.Rect(2200, 250, 300, 20),
]

water = pygame.Rect(2450, 210, 30, 40)
alien = pygame.Rect(300, 400, 40, 50)
alien2 = pygame.Rect(1600, 180, 40, 50) 
alien2_direction = 1
volcano = pygame.Rect(1250, 220, 80, 80)
alien_image = pygame.image.load("assets/alien.png").convert_alpha()
alien_image = pygame.transform.scale(alien_image, (60, 60))
alien2_image = pygame.image.load("assets/alien2.png").convert_alpha()
alien2_image = pygame.transform.scale(alien2_image, (50, 70))
fireballs = []

camera_x = 0

def reset_game():
    global player, velocity_y, oxygen, game_over, game_win, fireballs
    player.x, player.y = 100, 500
    velocity_y = 0
    oxygen = 100
    game_over = False
    game_win = False
    fireballs.clear()

def spawn_fireball():
    fireballs.append(pygame.Rect(volcano.x, volcano.y + 20, 20, 20))

spawn_timer = 0

# Main loop
while True:
    screen.fill((153, 76, 0))  # Mars surface color

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        import menu  # if you have menu.py
        menu.main()
    if keys[pygame.K_r]: reset_game()
    if not game_over and not game_win:
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = PLAYER_SPEED
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and on_ground:
            velocity_y = JUMP_STRENGTH
            on_ground = False


        velocity_y += GRAVITY
        player.y += velocity_y
        player.x += dx

        on_ground = False
        for plat in platforms:
            if player.colliderect(plat):
                if velocity_y > 0 and player.bottom <= plat.bottom:
                    player.bottom = plat.top
                    velocity_y = 0
                    on_ground = True

        oxygen -= OXYGEN_DECREASE
        if oxygen <= 0 or player.colliderect(alien):
            game_over = True
        if player.colliderect(water):
            game_win = True

        if player.x > WIDTH // 2:
            camera_x = player.x - WIDTH // 2
        else:
            camera_x = 0
        alien2.x += alien2_direction * 2
        if alien2.x < 1500 or alien2.x > 1750:
            alien2_direction *= -1
        spawn_timer += 1
        if spawn_timer > 120:
            spawn_fireball()
            spawn_timer = 0

        for fireball in fireballs[:]:
            fireball.x -= 4
            if fireball.colliderect(player):
                game_over = True
            if fireball.right < 0:
                fireballs.remove(fireball)

    # Draw platforms
    for plat in platforms:
        pygame.draw.rect(screen, (50, 50, 50), (plat.x - camera_x, plat.y, plat.width, plat.height))

    screen.blit(player_img, (player.x - camera_x, player.y))
    screen.blit(alien_img, (alien.x - camera_x, alien.y))
    screen.blit(alien2_image, (alien2.x - camera_x, alien2.y))
    screen.blit(water_img, (water.x - camera_x, water.y))
    screen.blit(volcano_img, (volcano.x - camera_x, volcano.y))

    for fb in fireballs:
        screen.blit(fireball_img, (fb.x - camera_x, fb.y))

    # Oxygen bar
    pygame.draw.rect(screen, (255, 255, 255), (20, 20, 200, 20))
    pygame.draw.rect(screen, (0, 100, 255), (20, 20, max(0, int(oxygen * 2)), 20))
    screen.blit(font.render("Oxygen", True, (0, 0, 0)), (230, 17))

    if game_over:
        msg = font.render("Game Over!", True, (255, 0, 0))
        screen.blit(msg, (WIDTH // 2 - 100, HEIGHT // 2))
    elif game_win:
        msg = font.render("Mars: 1, Afrika: 0", True, (0, 255, 0))
        screen.blit(msg, (WIDTH // 2 - 100, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(60)
