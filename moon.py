import pygame, sys, random, math

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Moon Path")
clock = pygame.time.Clock()
font_size = int(HEIGHT * 0.05)
font = pygame.font.SysFont("arial", font_size, bold=True)
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

rocket_img= pygame.image.load("assets/rocket1.png").convert_alpha()
rocket_img = pygame.transform.scale(rocket_img, (60, 80))

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
death_cause = ""  # === NEW ===
jump_sound = pygame.mixer.Sound('audio/jump.mp3')
jump_sound.set_volume(0.05)

walk_index = 0
walk_timer = 0
facing_right = True

fade_in_active = True
fade_in_alpha = 255

start_screen = True


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
rocket = pygame.Rect(20, 1480 + PLATFORM_OFFSET_Y, 60, 80)
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

paused = False
pause_options = ["Continue", "Restart Level", "Main Menu"]
pause_choice = 1

# === NEW: Death menu variables ===
death_options = ["Restart Level", "Return to Main Menu"]
death_choice = 1

show_mask_msg = False
mask_msg_timer = 180

# === NEW: Win fade-in variables ===
win_fade_active = False
win_fade_alpha = 0

def reset_game():
    global player, velocity_y, oxygen, game_over, game_win, lasers, mask_gotten, show_mask_msg, mask_msg_timer, meteors, meteor_active, death_cause
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
    death_cause = ""  # === NEW ===

def spawn_laser():
    lasers.append(pygame.Rect(satellite.x, satellite.y + 20, 20, 20))

def spawn_meteor():
    x_pos = random.randint(camera_x, camera_x + WIDTH)
    meteors.append(pygame.Rect(x_pos, camera_y - 100, 40, 60))

spawn_timer = 0

glow_positions = [(1750, 560), (1470,400), (1125, 240), (1525, 140), (2225, 240), (2815, 330),
(2835, 330), (2855, 330), (2875, 330), (2895, 330), (2915, 330), (2935, 330), (2955, 330), (2975, 330), 
(2995, 330), (3015, 330), (3035, 330), (3055, 330), (3075, 330), (3095, 330), (3115, 330), (3135, 330)]

# === NEW: Death cause logic ===
def get_death_cause():
    global death_cause
    # Collisions with lasers
    for laser in lasers:
        if player.colliderect(laser):
            death_cause = "Laser"
            return
    # Meteor
    for meteor in meteors:
        if player.colliderect(meteor):
            death_cause = "Meteor"
            return
    # Out of oxygen
    if oxygen <= 0:
        death_cause = "Ran Out of Oxygen"
        return
    # Fell off map
    if player.y > 1700 + PLATFORM_OFFSET_Y:
        death_cause = "Fell Off the Map"
        return
    # Meteor rain section (lose by falling)
    if meteor_active and player.y > 330 + PLATFORM_OFFSET_Y:
        death_cause = "Fell During Meteor Rain"
        return
    # Default
    death_cause = "Unknown"

landing_anim_active = True
fade_in_alpha = 255
rocket_start_y = -200  # Off screen at the top
rocket_landing_x = rocket.x - camera_x
rocket_landing_y = rocket.y - camera_y
rocket_current_y = rocket_start_y

landing_duration = 120  # frames (2 seconds at 60fps)
landing_frame = 0

# ---- MOON LANDING ANIMATION & FADE-IN ----
while landing_anim_active:
    # 1. Draw your scene (background, platforms, other objects)
    if mask_gotten:
        screen.fill((50, 50, 50))
    else:
        screen.blit(bg_img, (-camera_x * 0.2, HEIGHT - bg_img.get_height()))
    for plat in platforms:
        pygame.draw.rect(screen, (50, 50, 50), (plat.x - camera_x, plat.y - camera_y, plat.width, plat.height))
    # (Add any other scenery here, similar to your main loop)
    screen.blit(mask_img, (mask.x - camera_x, mask.y - camera_y))
    screen.blit(satellite_img, (satellite.x - camera_x, satellite.y - camera_y))
    screen.blit(rocket_img, (rocket_landing_x, rocket_current_y))
    # Draw overlays like oxygen bar, if you want
    pygame.draw.rect(screen, (255, 255, 255), (20, 20, 200, 20))
    pygame.draw.rect(screen, (0, 100, 255), (20, 20, max(0, int(oxygen * 2)), 20))
    screen.blit(font.render("Oxygen", True, (0, 0, 0)), (230, 17))

    # 2. Animate the rocket
    if landing_frame < landing_duration:
        t = landing_frame / landing_duration
        rocket_current_y = rocket_start_y + (rocket_landing_y - rocket_start_y) * t
    else:
        rocket_current_y = rocket_landing_y

    # 3. Draw fade-in overlay
    if fade_in_alpha > 0:
        fade_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        fade_surface.fill((0, 0, 0, fade_in_alpha))
        screen.blit(fade_surface, (0, 0))
        fade_in_alpha -= int(255 / landing_duration)
        if fade_in_alpha < 0:
            fade_in_alpha = 0

    pygame.display.flip()
    clock.tick(60)
    landing_frame += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    if landing_frame > landing_duration and fade_in_alpha == 0:
        landing_anim_active = False
        start_screen = True  # <-- so main loop shows start screen

while True:
    if fade_in_active:
        # --- DRAW FULL SCENE (exactly as you would on the start screen) ---
        if mask_gotten:
            screen.fill((50, 50, 50))
        else:
            screen.blit(bg_img, (-camera_x * 0.2, HEIGHT - bg_img.get_height()))
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
        # Draw the player (add your animation selection if you want)
        screen.blit(player_stand, (player.x - camera_x, player.y - camera_y))
        pygame.draw.rect(screen, (255, 255, 255), (20, 20, 200, 20))
        pygame.draw.rect(screen, (0, 100, 255), (20, 20, max(0, int(oxygen * 2)), 20))
        screen.blit(font.render("Oxygen", True, (0, 0, 0)), (230, 17))
        screen.blit(rocket_img, (rocket.x - camera_x, rocket.y - camera_y))
        # --- THEN FADE OVERLAY ---
        fade_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        fade_surface.fill((0, 0, 0, fade_in_alpha))
        screen.blit(fade_surface, (0, 0))
        fade_in_alpha -= 4
        if fade_in_alpha <= 0:
            fade_in_alpha = 0
            fade_in_active = False
            start_screen = True
        pygame.display.flip()
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        continue  # Do not run rest of loop yet

    # === START SCREEN HANDLER ===
    if start_screen:
        # --- DRAW FULL SCENE AS NORMAL ---
        if mask_gotten:
            screen.fill((50, 50, 50))
        else:
            screen.blit(bg_img, (-camera_x * 0.2, HEIGHT - bg_img.get_height()))

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
        elif 'dx' in locals() and dx != 0:
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

        # --- FLICKER TEXT ---
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            start_text = font.render("Press any key to start", True, (255,255,255))
            rect = start_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(start_text, rect)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if not fade_in_active and event.type == pygame.KEYDOWN:
                start_screen = False

            
        pygame.display.flip()
        clock.tick(60)
        continue  # Go to next frame until a key is pressed


    if mask_gotten:
        screen.fill((50, 50, 50))
        satellite.y = -999
    else:
        screen.blit(bg_img, (-camera_x * 0.2, HEIGHT - bg_img.get_height()))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # === NEW: Handle death menu navigation ===
        if game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    death_choice -= 1
                    if death_choice < 1:
                        death_choice = len(death_options)
                elif event.key == pygame.K_DOWN:
                    death_choice += 1
                    if death_choice > len(death_options):
                        death_choice = 1
                elif event.key == pygame.K_RETURN:
                    if death_choice == 1:
                        reset_game()
                    elif death_choice == 2:
                        import main
                        main.main()
            continue  # Skip rest when dead

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                paused = not paused
            elif paused:
                if event.key == pygame.K_UP:
                    pause_choice -= 1
                    if pause_choice < 1:
                        pause_choice = len(pause_options)
                elif event.key == pygame.K_DOWN:
                    pause_choice += 1
                    if pause_choice > len(pause_options):
                        pause_choice = 1
                elif event.key == pygame.K_RETURN:
                    if pause_choice == 1:
                        paused = False
                    elif pause_choice == 2:
                        reset_game()
                        paused = False
                    elif pause_choice == 3:
                        import main
                        main.main()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_r]:
        reset_game()

    if not paused and not game_over and not game_win:
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

        oxygen -= OXYGEN_DECREASE
        if oxygen <= 0:
            game_over = True
            get_death_cause()

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
            get_death_cause()

        for laser in lasers[:]:
            laser.x -= 4
            if laser.colliderect(player):
                game_over = True
                get_death_cause()
            if laser.right < 0:
                lasers.remove(laser)

        if meteor_active:
            msg = font.render("Oh no a meteor rain! Survive until we come and save you!", True, (255, 255, 255))
            screen.blit(msg, (WIDTH // 2 - 250, 100))
            meteor_timer += 1
            if player.y > 330 + PLATFORM_OFFSET_Y:
                game_over = True
                get_death_cause()
            if meteor_timer > 15:
                spawn_meteor()
                meteor_timer = 0

            for meteor in meteors[:]:
                meteor.y += 6
                if meteor.colliderect(player):
                    game_over = True
                    get_death_cause()
                if meteor.top > player.y + HEIGHT:
                    meteors.remove(meteor)
            if oxygen < 5:
                # === WIN! Trigger fade-in to next level ===
                game_win = True
                win_fade_active = True
                win_fade_alpha = 0

    for plat in platforms:
        pygame.draw.rect(screen, (50, 50, 50), (plat.x - camera_x, plat.y - camera_y, plat.width, plat.height))

    screen.blit(mask_img, (mask.x - camera_x, mask.y - camera_y))
    screen.blit(satellite_img, (satellite.x - camera_x, satellite.y - camera_y))
    screen.blit(rocket_img, (rocket.x - camera_x, rocket.y - camera_y))

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
        

    # === NEW: Death screen and overlay menu ===
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        death_title = font.render("YOU DIED", True, (255, 0, 0))
        cause_text = pygame.font.SysFont("arial", int(font_size * 0.7)).render(f"Cause: {death_cause}", True, (255, 255, 255))
        screen.blit(death_title, death_title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120)))
        screen.blit(cause_text, cause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))

        menu_font = pygame.font.SysFont("arial", font_size, bold=True)
        for i, opt in enumerate(death_options):
            y = HEIGHT // 2 + i * 80
            txt = menu_font.render(opt, True, (255, 255, 255))
            rect = txt.get_rect(center=(WIDTH // 2, y))
            if death_choice == i + 1:
                pygame.draw.rect(screen, (200, 0, 0), rect.inflate(40, 20), border_radius=12)
            screen.blit(txt, rect)

    # === NEW: Win fade overlay ===
    elif win_fade_active:
        win_msg = font.render("YOU GOT SAVED ON TIME! YOU WON!!!", True, (0, 255, 0))
        rect = win_msg.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(win_msg, rect)

        win_fade_alpha = min(max(int(win_fade_alpha), 0), 255)
        fade_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        fade_surface.fill((0, 0, 0, win_fade_alpha))
        screen.blit(fade_surface, (0, 0))

        if win_fade_alpha < 255:
            win_fade_alpha += 8
        else:
            # If you want to continue to next level, do it here!
            import main
            main.main()
            break

    if paused:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        pause_title_font = pygame.font.SysFont("arial", int(font_size * 1.2), bold=True)
        pause_help_font = pygame.font.SysFont("arial", int(font_size * 0.6))
        paused_text = pause_title_font.render("PAUSED", True, (255, 255, 255))
        paused_rect = paused_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 160))
        screen.blit(paused_text, paused_rect)

        help_lines = ["Use UP and DOWN to navigate", "Press ENTER to choose"]
        for i, line in enumerate(help_lines):
            txt = pause_help_font.render(line, True, (255, 255, 255))
            rect = txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 110 + i * 30))
            screen.blit(txt, rect)

        pause_font = pygame.font.SysFont("arial", font_size, bold=True)
        for i, opt in enumerate(pause_options):
            y = HEIGHT // 2 + i * 70
            color = (255, 255, 255)
            surf = pause_font.render(opt, True, color)
            rect = surf.get_rect(center=(WIDTH // 2, y))
            if pause_choice == i + 1:
                pulse = int(100 + 80 * math.sin(pygame.time.get_ticks() * 0.005))
                pygame.draw.rect(screen, (pulse, pulse, pulse), rect.inflate(40, 20), border_radius=12)
            screen.blit(surf, rect)
    
    # --- FADE-IN: Draw black overlay, fade out on first launch ---
    if fade_in_active:
        fade_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        fade_surface.fill((0, 0, 0, fade_in_alpha))
        screen.blit(fade_surface, (0, 0))
        fade_in_alpha -= 4  # (or 2 for slower)
        if fade_in_alpha <= 0:
            fade_in_alpha = 0
            fade_in_active = False


    pygame.display.flip()
    clock.tick(60)
