import pygame, sys, random

pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moon Escape")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Load images
bg_img = pygame.image.load("assets/moon_background.png").convert()
bg_img = pygame.transform.scale(bg_img, (2000, 1200))

player_img = pygame.image.load("assets/player.png")
player_img = pygame.transform.scale(player_img, (40, 50))

satellite_img = pygame.image.load("assets/satellite.png")
satellite_img = pygame.transform.scale(satellite_img, (60, 80))

laser_img = pygame.image.load("assets/laser.png")
laser_img = pygame.transform.scale(laser_img, (50, 15))

# Game constants
PLAYER_SPEED = 5
GRAVITY = 0.1
JUMP_STRENGTH = -6
OXYGEN_DECREASE = 0.1

# Player
player = pygame.Rect(100, 1500, 40, 50)
velocity_y = 0
on_ground = False
oxygen = 100
game_over = False
game_win = False
jump_sound = pygame.mixer.Sound('audio/jump.mp3')
jump_sound.set_volume(0.1)

# Level setup
platforms = [
    pygame.Rect(0, 1560, 4000, 20),
    pygame.Rect(200, 1370, 100, 20),
    pygame.Rect(500, 1190, 100, 20),
    pygame.Rect(200, 1000, 100, 20),
    pygame.Rect(500, 820, 200, 20),
    pygame.Rect(1050, 630, 20, 20),
    pygame.Rect(1750, 580, 20, 20),
    pygame.Rect(2150, 580, 200, 20),
]

satellite = pygame.Rect(1450, 770, 80, 60)
lasers = []

camera_x = 0
camera_y = 0

def reset_game():
    global player, velocity_y, oxygen, game_over, game_win, lasers
    player.x, player.y = 100, 1500
    velocity_y = 0
    oxygen = 100
    game_over = False
    game_win = False
    lasers.clear()

def spawn_laser():
    lasers.append(pygame.Rect(satellite.x, satellite.y + 20, 20, 20))

spawn_timer = 0

# Main loop
while True:
    screen.blit(bg_img, (-camera_x * 0.2, -camera_y * 0.2))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        import menu
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
            jump_sound.play()

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
            if player.colliderect(satellite):
                if velocity_y > 0 and player.bottom <= satellite.bottom:
                    player.bottom = satellite.top
                    velocity_y = 0
                    on_ground = True

        if oxygen <= 0:
            game_over = True
        oxygen -= OXYGEN_DECREASE

        # Camera follows player
        camera_x = max(0, player.x - WIDTH // 2)
        camera_y = max(0, player.y - HEIGHT // 2)

        spawn_timer += 1
        if spawn_timer > 110:
            spawn_laser()
            spawn_timer = 0
        if player.y> 1700:
            game_over = True
        for laser in lasers[:]:
            laser.x -= 4
            if laser.colliderect(player):
                game_over = True
            if laser.right < 0:
                lasers.remove(laser) 

    # Draw
    for plat in platforms:
        pygame.draw.rect(screen, (50, 50, 50), (plat.x - camera_x, plat.y - camera_y, plat.width, plat.height))
    screen.blit(player_img, (player.x - camera_x, player.y - camera_y))
    screen.blit(satellite_img, (satellite.x - camera_x, satellite.y - camera_y))

    for l in lasers:
        screen.blit(laser_img, (l.x - camera_x, l.y - camera_y))

    # Oxygen bar
    pygame.draw.rect(screen, (255, 255, 255), (20, 20, 200, 20))
    pygame.draw.rect(screen, (0, 100, 255), (20, 20, max(0, int(oxygen * 2)), 20))
    screen.blit(font.render("Oxygen", True, (0, 0, 0)), (230, 17))

    if game_over:
        msg = font.render("Game Over!", True, (255, 0, 0))
        screen.blit(msg, (WIDTH // 2 - 100, HEIGHT // 2))
    elif game_win:
        msg = font.render("YOU WON!!!!", True, (0, 255, 0))
        screen.blit(msg, (WIDTH // 2 - 100, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(60)
