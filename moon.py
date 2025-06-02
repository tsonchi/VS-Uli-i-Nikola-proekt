import pygame, sys, random

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Moon Path")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

PLATFORM_OFFSET_Y = HEIGHT

bg_img = pygame.image.load("assets/moon_background.png").convert()
bg_img = pygame.transform.scale(bg_img, (WIDTH + PLATFORM_OFFSET_Y, HEIGHT))

dark_bg_img = bg_img.copy()
dark_bg_img.fill((50, 50, 50), special_flags=pygame.BLEND_RGB_MULT)

player_stand = pygame.image.load("assets/player_stand.png").convert_alpha()
player_walk_1 = pygame.image.load("assets/player_walk_1.png").convert_alpha()
player_walk_2 = pygame.image.load("assets/player_walk_2.png").convert_alpha()
player_jump = pygame.image.load("assets/jump.png").convert_alpha()

player_stand = pygame.transform.scale(player_stand, (40, 50))
player_walk_1 = pygame.transform.scale(player_walk_1, (40, 50))
player_walk_2 = pygame.transform.scale(player_walk_2, (40, 50))
player_jump = pygame.transform.scale(player_jump, (40, 50))
walk_images = [player_walk_1, player_walk_2]

satellite_img = pygame.image.load("assets/satellite.png")
satellite_img = pygame.transform.scale(satellite_img, (60, 80))

laser_img = pygame.image.load("assets/laser.png")
laser_img = pygame.transform.scale(laser_img, (50, 15))

mask_img = pygame.image.load("assets/mask.png")
mask_img = pygame.transform.scale(mask_img, (50, 50))

meteor_img = pygame.image.load("assets/meteor.png").convert_alpha()
meteor_img = pygame.transform.scale(meteor_img, (40, 60))

PLAYER_SPEED = 5
GRAVITY = 0.1
JUMP_STRENGTH = -6
OXYGEN_DECREASE = 0.1

player = pygame.Rect(100, 1510 + PLATFORM_OFFSET_Y, 40, 50)
velocity_y = 0
on_ground = False
oxygen = 100
game_over = False
game_win = False
jump_sound = pygame.mixer.Sound('audio/jump.mp3')
jump_sound.set_volume(0.05)

walk_index = 0
walk_timer = 0
facing_right = True

platforms = [
    pygame.Rect(0, 1560 + PLATFORM_OFFSET_Y, 4000, 20),
    pygame.Rect(200, 1370 + PLATFORM_OFFSET_Y, 100, 20),
    pygame.Rect(500, 1190 + PLATFORM_OFFSET_Y, 100, 20),
    pygame.Rect(200, 1000 + PLATFORM_OFFSET_Y, 100, 20),
    pygame.Rect(500, 820 + PLATFORM_OFFSET_Y, 200, 20),
    pygame.Rect(1050, 630 + PLATFORM_OFFSET_Y, 20, 20),
    pygame.Rect(1750, 580 + PLATFORM_OFFSET_Y, 20, 20),
    pygame.Rect(2150, 580 + PLATFORM_OFFSET_Y, 200, 20),
    pygame.Rect(1450, 420 + PLATFORM_OFFSET_Y, 100, 20),
    pygame.Rect(1100, 260 + PLATFORM_OFFSET_Y, 50, 20),
    pygame.Rect(1500, 160 + PLATFORM_OFFSET_Y, 50, 20),
    pygame.Rect(2200, 260 + PLATFORM_OFFSET_Y, 50, 20),
    pygame.Rect(2800, 350 + PLATFORM_OFFSET_Y, 355, 20),
]

satellite = pygame.Rect(1450, 770 + PLATFORM_OFFSET_Y, 80, 60)
mask = pygame.Rect(2200, 530 + PLATFORM_OFFSET_Y, 50, 50)
mask_gotten = False
lasers = []
meteors = []
meteor_timer = 0
meteor_active = False

camera_x = 0
min_camera_y = 1560 + PLATFORM_OFFSET_Y - HEIGHT
first_platform_y = 1560 + PLATFORM_OFFSET_Y  # first platform’s Y position

target_camera_y = player.y - HEIGHT // 2
lowest_allowed_y = first_platform_y - HEIGHT  # Bottom limit (don't see below 1st platform)
camera_y = min(target_camera_y, lowest_allowed_y)


show_mask_msg = False
mask_msg_timer = 180

def reset_game():
    global player, velocity_y, oxygen, game_over, game_win, lasers, mask_gotten, show_mask_msg, mask_msg_timer, meteors, meteor_active
    player.x, player.y = 100, 1510 + PLATFORM_OFFSET_Y
    satellite.y = 770 + PLATFORM_OFFSET_Y
    velocity_y = 0
    oxygen = 100
    game_over = False
    game_win = False
    mask_gotten = False
    show_mask_msg = False
    mask_msg_timer = 180
    mask.x = 2200
    mask.y = 530 + PLATFORM_OFFSET_Y
    lasers.clear()
    meteors.clear()
    meteor_active = False

def spawn_laser():
    lasers.append(pygame.Rect(satellite.x, satellite.y + 20, 20, 20))

def spawn_meteor():
    x_pos = random.randint(camera_x, camera_x + WIDTH)
    meteors.append(pygame.Rect(x_pos, camera_y - 100, 40, 60))

spawn_timer = 0

glow_positions = [(1750, 560), (1470,400), (1125, 240), (1525, 140), (2225, 240), (2815, 330),
(2835, 330), (2855, 330), (2875, 330), (2895, 330), (2915, 330), (2935, 330), (2955, 330), (2975, 330), 
(2995, 330), (3015, 330), (3035, 330), (3055, 330), (3075, 330), (3095, 330), (3115, 330), (3135, 330)]

while True:
    if mask_gotten:
        screen.fill((50, 50, 50))
        satellite.y = -999
    else:
        screen.blit(bg_img, (-camera_x * 0.2, HEIGHT - bg_img.get_height()))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        import main
        main.main()
    if keys[pygame.K_r]:
        reset_game()

    if not game_over and not game_win:
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -PLAYER_SPEED
            facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = PLAYER_SPEED
            facing_right = True
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
                    if plat.x == 2800 and plat.y == 350 + PLATFORM_OFFSET_Y and not meteor_active:
                        oxygen = 100
                        meteor_active = True

        if player.colliderect(satellite):
            if velocity_y > 0 and player.bottom <= satellite.bottom:
                player.bottom = satellite.top
                velocity_y = 0
                on_ground = True

        if player.colliderect(mask) and not mask_gotten:
            oxygen = 100
            mask_gotten = True
            mask.x = -9999
            show_mask_msg = True
            mask_msg_timer = 180

        if oxygen <= 0:
            game_over = True
        oxygen -= OXYGEN_DECREASE

        camera_x = max(0, player.x - WIDTH // 2)
        min_camera_y = 1560 + PLATFORM_OFFSET_Y - HEIGHT
        first_platform_y = 1560 + PLATFORM_OFFSET_Y  # first platform’s Y position

        target_camera_y = player.y - HEIGHT // 2
        lowest_allowed_y = first_platform_y - HEIGHT  # Bottom limit (don't see below 1st platform)
        camera_y = min(target_camera_y, lowest_allowed_y)


        spawn_timer += 1
        if spawn_timer > 110:
            spawn_laser()
            spawn_timer = 0

        if player.y > 1700 + PLATFORM_OFFSET_Y:
            game_over = True

        for laser in lasers[:]:
            laser.x -= 4
            if laser.colliderect(player):
                game_over = True
            if laser.right < 0:
                lasers.remove(laser)

        if meteor_active:
            msg = font.render("Oh no a meteor rain! Survive until we come and save you!", True, (255, 255, 255))
            screen.blit(msg, (WIDTH // 2 - 250, 100))
            meteor_timer += 1
            if player.y > 330 + PLATFORM_OFFSET_Y:
                game_over = True
            if meteor_timer > 15:
                spawn_meteor()
                meteor_timer = 0

            for meteor in meteors[:]:
                meteor.y += 6
                if meteor.colliderect(player):
                    game_over = True
                if meteor.top > player.y + HEIGHT:
                    meteors.remove(meteor)
            if oxygen < 5:
                game_win = True

    for plat in platforms:
        pygame.draw.rect(screen, (50, 50, 50), (plat.x - camera_x, plat.y - camera_y, plat.width, plat.height))

    screen.blit(mask_img, (mask.x - camera_x, mask.y - camera_y))
    screen.blit(satellite_img, (satellite.x - camera_x, satellite.y - camera_y))

    for l in lasers:
        screen.blit(laser_img, (l.x - camera_x, l.y - camera_y))

    for m in meteors:
        screen.blit(meteor_img, (m.x - camera_x, m.y - camera_y))

    if mask_gotten:
        for gx, gy in glow_positions:
            pygame.draw.circle(screen, (100, 255, 255), (gx - camera_x, gy + PLATFORM_OFFSET_Y - camera_y), 8)

    is_jumping = velocity_y < -1
    is_falling = velocity_y > 1
    if is_falling or is_jumping:
        current_img = player_jump
    elif dx != 0:
        walk_timer += 1
        if walk_timer >= 10:
            walk_timer = 0
            walk_index = (walk_index + 1) % len(walk_images)
        current_img = walk_images[walk_index]
    else:
        current_img = player_stand

    if not facing_right:
        current_img = pygame.transform.flip(current_img, True, False)

    screen.blit(current_img, (player.x - camera_x, player.y - camera_y))

    pygame.draw.rect(screen, (255, 255, 255), (20, 20, 200, 20))
    pygame.draw.rect(screen, (0, 100, 255), (20, 20, max(0, int(oxygen * 2)), 20))
    screen.blit(font.render("Oxygen", True, (0, 0, 0)), (230, 17))

    if show_mask_msg and mask_msg_timer > 0:
        msg = font.render("You got the mask! But it's harder to see...", True, (255, 255, 255))
        screen.blit(msg, (WIDTH // 2 - 250, 100))
        msg2 = font.render("Follow the glowy things!", True, (0, 255, 200))
        screen.blit(msg2, (WIDTH // 2 - 180, 140))
        mask_msg_timer -= 1

    if game_over:
        msg = font.render("Game Over!", True, (255, 0, 0))
        screen.blit(msg, (WIDTH // 2 - 100, HEIGHT // 2))
    elif game_win:
        msg = font.render("YOU GOT SAVED ON TIME THANK GOD! YOU WON!!!", True, (0, 255, 0))
        screen.blit(msg, (WIDTH // 2 - 300, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(60)
