import pygame, sys, random

pygame.init()
WIDTH, HEIGHT = 1200, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mars Escape")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Load images
bg_img = pygame.image.load("assets/background.png").convert()
bg_img = pygame.transform.scale(bg_img, (2000, HEIGHT))

player_img = pygame.image.load("assets/player.png")
player_img = pygame.transform.scale(player_img, (40, 50))

alien_img = pygame.image.load("assets/alien.png").convert_alpha()
alien_img = pygame.transform.scale(alien_img, (60, 60))

water_img = pygame.image.load("assets/water.png")
water_img = pygame.transform.scale(water_img, (60, 50))

volcano_img = pygame.image.load("assets/volcano.png")
volcano_img = pygame.transform.scale(volcano_img, (80, 60))

fireball_img = pygame.image.load("assets/fireball.png")
fireball_img = pygame.transform.scale(fireball_img, (20, 20))

alien2_image = pygame.image.load("assets/alien2.png").convert_alpha()
alien2_image = pygame.transform.scale(alien2_image, (65, 70))

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
jump_sound = pygame.mixer.Sound('audio/jump.mp3')
jump_sound.set_volume(0.1)


# Level setup
platforms = [
    pygame.Rect(0, 580, 4000, 20),
    pygame.Rect(200, 450, 150, 20),
    pygame.Rect(500, 400, 300, 20),
    pygame.Rect(900, 350, 150, 20),
    pygame.Rect(1200, 300, 150, 20),
    pygame.Rect(1500, 250, 300, 20),
    pygame.Rect(1900, 300, 300, 20),
    pygame.Rect(2300, 250, 300, 20),
    pygame.Rect(2300, 20, 300, 20),
    pygame.Rect(2700, 250, 400, 20),
    pygame.Rect(3200, 350, 500, 20),
]

spikes = [
    [(2000, 300), (2020, 260), (2040, 300)],
    [(2040, 300), (2060, 260), (2080, 300)],
    [(2080, 300), (2100, 260), (2120, 300)],
    [(2800, 250), (2820, 210), (2840, 250)],
    [(2840, 250), (2860, 210), (2880, 250)],
    [(2880, 250), (2900, 210), (2920, 250)],
    [(3020, 250), (3040, 210), (3060, 250)],
]
spike_rects = [pygame.Rect(2000, 260, 120, 40),pygame.Rect(2800, 210, 120, 40),pygame.Rect(3020, 210, 40, 40),]

# Falling spikes
falling_spikes = [
    {"points": [(2400, 40), (2420, 80), (2440, 40)], "trigger_x": 2400, "falling": False, "dy": 0},
    {"points": [(2440, 40), (2460, 80), (2480, 40)], "trigger_x": 2440, "falling": False, "dy": 0},
    {"points": [(2480, 40), (2500, 80), (2520, 40)], "trigger_x": 2480, "falling": False, "dy": 0},
]

spike_color = (125, 106, 74)

water = pygame.Rect(3650, 300, 60, 50)
alien = pygame.Rect(300, 390, 60, 60)
alien2 = pygame.Rect(1600, 180, 65, 70)
alien2_direction = 1
alien3 = pygame.Rect(3550, 290, 60, 60)
alien3_direction = 1
ok = 0   
volcano = pygame.Rect(1250, 240, 80, 60)
fireballs = []

camera_x = 0

def reset_game():
    global player, velocity_y, oxygen, game_over, game_win, fireballs, ok
    player.x, player.y = 100, 500
    velocity_y = 0
    oxygen = 100
    game_over = False
    game_win = False
    fireballs.clear()
    for spike in falling_spikes:
        spike["falling"] = False
        spike["dy"] = 0
    falling_spikes[0]["points"] = [(2400, 40), (2420, 80), (2440, 40)]
    falling_spikes[1]["points"] = [(2440, 40), (2460, 80), (2480, 40)]
    falling_spikes[2]["points"] = [(2480, 40), (2500, 80), (2520, 40)]
    alien3.x, alien3.y = 3550, 290
    ok = 0



def spawn_fireball():
    fireballs.append(pygame.Rect(volcano.x, volcano.y + 20, 20, 20))

spawn_timer = 0

# Main loop
while True:
    screen.blit(bg_img, (-camera_x * 0.2, 0))

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

        for rect in spike_rects:
            if player.colliderect(rect):
                game_over = True

        # Falling spikes logic
        for spike in falling_spikes:
            if not spike["falling"] and player.x >= spike["trigger_x"]-40:
                spike["falling"] = True
            if spike["falling"]:
                spike["dy"] += 1.5
                spike["points"] = [(x, y + spike["dy"]) for (x, y) in spike["points"]]

                spike_rect = pygame.Rect(
                    min(p[0] for p in spike["points"]),
                    min(p[1] for p in spike["points"]),
                    max(p[0] for p in spike["points"]) - min(p[0] for p in spike["points"]),
                    max(p[1] for p in spike["points"]) - min(p[1] for p in spike["points"])
                )
                if player.colliderect(spike_rect):
                    game_over = True

        oxygen -= OXYGEN_DECREASE
        if oxygen <= 0 or player.colliderect(alien) or player.colliderect(alien2) or player.colliderect(alien3):
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
        if (player.x>= 3150 and player.y>= 300) or ok==1:
            ok = 1
            if alien3.x<=3200:
                ok = 2
            elif (alien3.x<=3550  or alien3.x >= 3200) and ok == 1:
                alien3.x += alien3_direction*10
                if alien3.x<3200 or alien3.x>3550:
                    alien3_direction *= -1



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

    # Draw
    for plat in platforms:
        pygame.draw.rect(screen, (50, 50, 50), (plat.x - camera_x, plat.y, plat.width, plat.height))
    for spike in spikes:
        pygame.draw.polygon(screen, spike_color, [(x - camera_x, y) for (x, y) in spike])
    for spike in falling_spikes:
        pygame.draw.polygon(screen, spike_color, [(x - camera_x, y) for (x, y) in spike["points"]])

    screen.blit(alien_img, (alien.x - camera_x, alien.y))
    if ok >= 1:
            screen.blit(alien2_image, (alien3.x - camera_x, alien3.y-10))
    else:
        screen.blit(alien_img, (alien3.x - camera_x, alien3.y))

    screen.blit(player_img, (player.x - camera_x, player.y))
    screen.blit(alien2_image, (alien2.x - camera_x, alien2.y))

    screen.blit(water_img, (water.x - camera_x, water.y))
    screen.blit(volcano_img, (volcano.x - camera_x, volcano.y))

    for fb in fireballs:
        screen.blit(fireball_img, (fb.x - camera_x, fb.y))

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
