import pygame, sys, random, math

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Mars Escape")
clock = pygame.time.Clock()

font_size = int(HEIGHT * 0.05)
font = pygame.font.SysFont("arial", font_size, bold=True)

PLATFORM_OFFSET_Y = HEIGHT - 600

bg_img = pygame.image.load("assets/background.png").convert()
bg_img = pygame.transform.scale(bg_img, (WIDTH + PLATFORM_OFFSET_Y, HEIGHT))
BG_WIDTH = WIDTH + PLATFORM_OFFSET_Y

alien_img = pygame.image.load("assets/alien.png").convert_alpha()
alien_img = pygame.transform.scale(alien_img, (60, 60))
rocket_img = pygame.image.load("assets/rocket1.png")
rocket_img = pygame.transform.scale(rocket_img, (60, 80))
volcano_img = pygame.image.load("assets/volcano.png")
volcano_img = pygame.transform.scale(volcano_img, (80, 60))
fireball_img = pygame.image.load("assets/fireball.png")
fireball_img = pygame.transform.scale(fireball_img, (20, 20))
alien2_image = pygame.image.load("assets/alien2.png").convert_alpha()
alien2_image = pygame.transform.scale(alien2_image, (65, 70))
player_stand = pygame.image.load("assets/player_stand.png").convert_alpha()
player_walk_1 = pygame.image.load("assets/player_walk_1.png").convert_alpha()
player_walk_2 = pygame.image.load("assets/player_walk_2.png").convert_alpha()
player_jump = pygame.image.load("assets/jump.png").convert_alpha()
base_img = pygame.image.load("assets/newrocket.png")
base_img = pygame.transform.scale(base_img, (400, 400))
meteor1_img = pygame.image.load("assets/meteor.png")
meteor1_img = pygame.transform.scale(meteor1_img, (40, 80))

player_stand = pygame.transform.scale(player_stand, (40, 50))
player_walk_1 = pygame.transform.scale(player_walk_1, (40, 50))
player_walk_2 = pygame.transform.scale(player_walk_2, (40, 50))
player_jump = pygame.transform.scale(player_jump, (40, 50))
walk_images = [player_walk_1, player_walk_2]

PLAYER_SPEED = 5
GRAVITY = 0.3
JUMP_STRENGTH = -9
OXYGEN_DECREASE = 0.1

player = pygame.Rect(100, 500 + PLATFORM_OFFSET_Y, 40, 50)
velocity_y = 0
on_ground = False
oxygen = 110
game_over = False
death_cause = "" 
game_win = False
jump_sound = pygame.mixer.Sound('audio/jump.mp3')
jump_sound.set_volume(0.05)
walk_index = 0
walk_timer = 0
facing_right = True

start_screen = True
countdown_active = False
countdown_value = 3
countdown_last_tick = 0  # for timing
fade_in_active = True
fade_in_alpha = 255


player_entered_rocket = False
rocket_takeoff_y = 0  # Y offset for rocket flight animation


win_fade_active = False
win_fade_alpha = 0

paused = False
pause_options = ["Continue", "Restart Level", "Main Menu"]
pause_choice = 1

death_options = ["Restart Level", "Return to Main Menu"]
death_choice = 1


platforms = [
    pygame.Rect(0, 580 + PLATFORM_OFFSET_Y, 4000, 20),
    pygame.Rect(200, 450 + PLATFORM_OFFSET_Y, 150, 20),
    pygame.Rect(500, 400 + PLATFORM_OFFSET_Y, 300, 20),
    pygame.Rect(900, 350 + PLATFORM_OFFSET_Y, 150, 20),
    pygame.Rect(1200, 300 + PLATFORM_OFFSET_Y, 150, 20),
    pygame.Rect(1500, 250 + PLATFORM_OFFSET_Y, 300, 20),
    pygame.Rect(1900, 300 + PLATFORM_OFFSET_Y, 300, 20),
    pygame.Rect(2300, 250 + PLATFORM_OFFSET_Y, 300, 20),
    pygame.Rect(2300, 20 + PLATFORM_OFFSET_Y, 300, 20),
    pygame.Rect(2700, 250 + PLATFORM_OFFSET_Y, 400, 20),
    pygame.Rect(3200, 350 + PLATFORM_OFFSET_Y, 500, 20),
]

spikes = [
    [(2000, 300 + PLATFORM_OFFSET_Y), (2020, 260 + PLATFORM_OFFSET_Y), (2040, 300 + PLATFORM_OFFSET_Y)],
    [(2040, 300 + PLATFORM_OFFSET_Y), (2060, 260 + PLATFORM_OFFSET_Y), (2080, 300 + PLATFORM_OFFSET_Y)],
    [(2080, 300 + PLATFORM_OFFSET_Y), (2100, 260 + PLATFORM_OFFSET_Y), (2120, 300 + PLATFORM_OFFSET_Y)],
    [(2800, 250 + PLATFORM_OFFSET_Y), (2820, 210 + PLATFORM_OFFSET_Y), (2840, 250 + PLATFORM_OFFSET_Y)],
    [(2840, 250 + PLATFORM_OFFSET_Y), (2860, 210 + PLATFORM_OFFSET_Y), (2880, 250 + PLATFORM_OFFSET_Y)],
    [(2880, 250 + PLATFORM_OFFSET_Y), (2900, 210 + PLATFORM_OFFSET_Y), (2920, 250 + PLATFORM_OFFSET_Y)],
    [(3020, 250 + PLATFORM_OFFSET_Y), (3040, 210 + PLATFORM_OFFSET_Y), (3060, 250 + PLATFORM_OFFSET_Y)],
]
spike_rects = [
    pygame.Rect(2000, 260 + PLATFORM_OFFSET_Y, 120, 40),
    pygame.Rect(2800, 210 + PLATFORM_OFFSET_Y, 120, 40),
    pygame.Rect(3020, 210 + PLATFORM_OFFSET_Y, 40, 40),
]

falling_spikes = [
    {"points": [(2400, 40 + PLATFORM_OFFSET_Y), (2420, 80 + PLATFORM_OFFSET_Y), (2440, 40 + PLATFORM_OFFSET_Y)], "trigger_x": 2400, "falling": False, "dy": 0},
    {"points": [(2440, 40 + PLATFORM_OFFSET_Y), (2460, 80 + PLATFORM_OFFSET_Y), (2480, 40 + PLATFORM_OFFSET_Y)], "trigger_x": 2440, "falling": False, "dy": 0},
    {"points": [(2480, 40 + PLATFORM_OFFSET_Y), (2500, 80 + PLATFORM_OFFSET_Y), (2520, 40 + PLATFORM_OFFSET_Y)], "trigger_x": 2480, "falling": False, "dy": 0},
]

spike_color = (125, 106, 74)

rocket = pygame.Rect(3650, 270 + PLATFORM_OFFSET_Y, 60, 50)
new_rocket = pygame.Rect(-100, 240 + PLATFORM_OFFSET_Y, 100,100)
alien = pygame.Rect(300, 390 + PLATFORM_OFFSET_Y, 60, 60)
alien2 = pygame.Rect(1600, 180 + PLATFORM_OFFSET_Y, 65, 70)
alien2_direction = 1
alien3 = pygame.Rect(3550, 290 + PLATFORM_OFFSET_Y, 60, 60)
alien3_direction = 1
ok = 0
volcano = pygame.Rect(1250, 240 + PLATFORM_OFFSET_Y, 80, 60)
fireballs = []
meteor1 = pygame.Rect(100, 300 + PLATFORM_OFFSET_Y, 100,100)
meteor2 = pygame.Rect(70, 200 + PLATFORM_OFFSET_Y, 100,100)
meteor3 = pygame.Rect(82, 420 + PLATFORM_OFFSET_Y, 100,100)
camera_x = 0

# Level ends at the farthest platform or rocket edge
last_platform_right = max(p.right for p in platforms)
level_end_x = max(last_platform_right, rocket.right)
max_camera_x_level = level_end_x - WIDTH
max_camera_x_bg = int((BG_WIDTH - WIDTH) / 0.2)
final_max_camera_x = min(max_camera_x_level, max_camera_x_bg)
ground_right = platforms[0].right  

def game_over_cause():
    global death_cause

    # 1) Check stationary spikes:
    for rect in spike_rects:
        if player.colliderect(rect):
            death_cause = "Spikes"
            return

    # 2) Check any currently-falling spike polygons:
    for spike in falling_spikes:
        # Reconstruct its bounding Rect from spike["points"]:
        spike_rect = pygame.Rect(
            min(p[0] for p in spike["points"]),
            min(p[1] for p in spike["points"]),
            max(p[0] for p in spike["points"]) - min(p[0] for p in spike["points"]),
            max(p[1] for p in spike["points"]) - min(p[1] for p in spike["points"])
        )
        if player.colliderect(spike_rect):
            death_cause = "Falling Spike"
            return

    # 3) Ran out of oxygen?
    if oxygen <= 0:
        death_cause = "Ran Out of Oxygen"
        return

    # 4) Alien collisions:
    if player.colliderect(alien):
        death_cause = "Alien 1"
        return
    if player.colliderect(alien2):
        death_cause = "Alien 2"
        return
    if player.colliderect(alien3):
        death_cause = "Alien 3"
        return

    # 5) Fell off bottom of the map:
    if player.y > HEIGHT:
        death_cause = "Fell Off the Map"
        return

    # 6) Fireball collisions:
    for fb in fireballs:
        if fb.colliderect(player):
            death_cause = "Fireball"
            return

    # (If nothing else matched, you could set a default cause here.)
    death_cause = "Unknown"


def reset_game():
    global player, velocity_y, oxygen, game_over, game_win, fireballs, ok
    player.x, player.y = 100, 500 + PLATFORM_OFFSET_Y
    velocity_y = 0
    oxygen = 100
    game_over = False
    game_win = False
    fireballs.clear()

    for spike in falling_spikes:
        spike["falling"] = False
        spike["dy"] = 0
    falling_spikes[0]["points"] = [(2400, 40 + PLATFORM_OFFSET_Y), (2420, 80 + PLATFORM_OFFSET_Y), (2440, 40 + PLATFORM_OFFSET_Y)]
    falling_spikes[1]["points"] = [(2440, 40 + PLATFORM_OFFSET_Y), (2460, 80 + PLATFORM_OFFSET_Y), (2480, 40 + PLATFORM_OFFSET_Y)]
    falling_spikes[2]["points"] = [(2480, 40 + PLATFORM_OFFSET_Y), (2500, 80 + PLATFORM_OFFSET_Y), (2520, 40 + PLATFORM_OFFSET_Y)]
    alien3.x, alien3.y = 3550, 290 + PLATFORM_OFFSET_Y
    ok = 0

def spawn_fireball():
    fireballs.append(pygame.Rect(volcano.x, volcano.y + 20, 20, 20))

spawn_timer = 0

# … (everything up through event handling stays the same) …

while True:
    screen.blit(bg_img, (-camera_x * 0.2, 0))
    parallax_x = -camera_x * 0.2
    bg_right_on_screen = parallax_x + bg_img.get_width()
    if bg_right_on_screen < WIDTH:
        parallax_x = WIDTH - bg_img.get_width()
    screen.blit(bg_img, (parallax_x, 0))


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        
        if start_screen:
            if event.type == pygame.KEYDOWN:
                start_screen = False
                countdown_active = True
                countdown_value = 3
                countdown_last_tick = pygame.time.get_ticks()
            continue

        if countdown_active:
            # Ignore inputs during countdown
            continue

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
                        import menu
                        menu.main()
            continue  # Important! Skip all other event handling when dead

        if paused:
            if event.type == pygame.KEYDOWN:
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
                        import menu
                        menu.main()
            continue

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            paused = not paused

        if not paused and not game_win and not game_over:
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_SPACE or event.key == pygame.K_w or event.key == pygame.K_UP) and on_ground:
                    velocity_y = JUMP_STRENGTH
                    on_ground = False
                    jump_sound.play()


    if countdown_active:
        now = pygame.time.get_ticks()
        if now - countdown_last_tick >= 1000:  # 1 second passed
            countdown_value -= 1
            countdown_last_tick = now
            if countdown_value <= 0:
                countdown_active = False  # Start the game!

    keys = pygame.key.get_pressed()

    # ─── Normal gameplay: movement, physics, oxygen, collisions, camera, enemy AI ───
    if not paused and not game_over and not game_win and not start_screen and not countdown_active:
        # 1) Figure out horizontal input:
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -PLAYER_SPEED
            facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx =  PLAYER_SPEED
            facing_right = True

        # 2) Jump:
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and on_ground:
            velocity_y = JUMP_STRENGTH
            on_ground = False
            jump_sound.play()

        # 3) Apply gravity to vertical velocity:
        velocity_y += GRAVITY
        player.y   += velocity_y

        # 4) Move horizontally:
        player.x += dx

        # 5) Ground‐check & platform collisions:
        on_ground = False
        for plat in platforms:
            if player.colliderect(plat):
                # Only land if we were falling onto it:
                if velocity_y > 0 and player.bottom <= plat.bottom:
                    player.bottom   = plat.top
                    velocity_y      = 0
                    on_ground       = True

        # 6) Trigger falling spikes and check for collisions:
        for spike in falling_spikes:
            if not spike["falling"] and player.x >= spike["trigger_x"] - 40:
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
                    game_over_cause()

        # 7) Decrease oxygen each frame:
        oxygen -= OXYGEN_DECREASE
        if oxygen <= 0:
            game_over = True
            game_over_cause()

        # 8) Check alien collisions:
        if player.colliderect(alien) or player.colliderect(alien2) or player.colliderect(alien3):
            game_over = True
            game_over_cause()

        # 9) Check rocket win:
        if player.colliderect(rocket) and not player_entered_rocket:
            game_win = True
            win_fade_active = True
            win_fade_alpha = 0
            player_entered_rocket = True
            # Move player to align with rocket visually (optional, for effect)
            player.centerx = rocket.centerx
            player.bottom = rocket.bottom
            rocket_takeoff_y = 0


        # 10) If the player falls off the bottom of the screen:
        if player.y > HEIGHT:
            game_over = True
            game_over_cause()

        # 11) Move camera so player stays near center:
        if player.x > WIDTH // 2:
            camera_x = player.x - WIDTH // 2
            max_camera_x = ground_right - WIDTH
            if camera_x > max_camera_x:
                camera_x = max_camera_x
        else:
            camera_x = 0
            
        # Clamp player to never leave level bounds
        if player.x < 0:
            player.x = 0
        if player.x + player.width > ground_right:
            player.x = ground_right - player.width

        # 12) Alien #2 patrol logic:
        alien2.x += alien2_direction * 2
        if alien2.x < 1500 or alien2.x > 1750:
            alien2_direction *= -1

        # 13) Alien #3 activation:
        if (player.x >= 3150 and player.y >= 300 + PLATFORM_OFFSET_Y) or ok == 1:
            ok = 1
            if alien3.x <= 3200:
                ok = 2
            elif (alien3.x <= 3550 or alien3.x >= 3200) and ok == 1:
                alien3.x += alien3_direction * 10
                if alien3.x < 3200 or alien3.x > 3550:
                    alien3_direction *= -1

        # 14) Volcano spawns fireballs periodically:
        spawn_timer += 1
        if spawn_timer > 120:
            spawn_fireball()
            spawn_timer = 0

        for fireball in fireballs[:]:
            fireball.x -= 4
            if fireball.colliderect(player):
                game_over = True
                game_over_cause()
            if fireball.right < 0:
                fireballs.remove(fireball)

    # ─── HANDLE INPUT / MOTION WHEN game_over IS TRUE ─────────────────────────────────
    elif game_over:
        for event in pygame.event.get():
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
                        import menu
                        menu.main()


    # ─── DRAW EVERYTHING ───────────────────────────────────────────────────────────────
    
    for plat in platforms:
        pygame.draw.rect(screen, (50, 50, 50), (plat.x - camera_x, plat.y, plat.width, plat.height))
    for spike in spikes:
        pygame.draw.polygon(screen, spike_color, [(x - camera_x, y) for (x, y) in spike])
    for spike in falling_spikes:
        pygame.draw.polygon(screen, spike_color, [(x - camera_x, y) for (x, y) in spike["points"]])

    screen.blit(alien_img, (alien.x - camera_x, alien.y))
    if ok >= 1:
        screen.blit(alien2_image, (alien3.x - camera_x, alien3.y - 10))
    else:
        screen.blit(alien_img, (alien3.x - camera_x, alien3.y))
    screen.blit(alien2_image, (alien2.x - camera_x, alien2.y))
    rocket_draw_y = rocket.y - rocket_takeoff_y
    screen.blit(rocket_img, (rocket.x - camera_x, rocket_draw_y))

    screen.blit(volcano_img, (volcano.x - camera_x, volcano.y))
    for fb in fireballs:
        screen.blit(fireball_img, (fb.x - camera_x, fb.y))
    
    screen.blit(meteor1_img, (meteor1.x - camera_x, meteor1.y))
    screen.blit(meteor1_img, (meteor2.x - camera_x, meteor2.y))
    screen.blit(base_img, (new_rocket.x - camera_x, new_rocket.y))
    screen.blit(meteor1_img, (meteor3.x - camera_x, meteor3.y))
    # ─── PLAYER ANIMATION & DRAW ────────────────────────────────────────────────────
    is_jumping = velocity_y < -1
    is_falling = velocity_y > 1
    if is_falling or is_jumping:
        current_img = player_jump
    elif 'dx' in locals() and dx != 0:   # make sure dx exists
        walk_timer += 1
        if walk_timer >= 10:
            walk_timer = 0
            walk_index = (walk_index + 1) % len(walk_images)
        current_img = walk_images[walk_index]
    else:
        current_img = player_stand

    if not facing_right:
        current_img = pygame.transform.flip(current_img, True, False)

    if not (win_fade_active and player_entered_rocket):
        screen.blit(current_img, (player.x - camera_x, player.y))


    # ─── OXYGEN BAR ─────────────────────────────────────────────────────────────────
    pygame.draw.rect(screen, (255, 255, 255), (20, 20, 200, 20))
    pygame.draw.rect(screen, (0, 100, 255), (20, 20, max(0, int(oxygen * 2)), 20))
    screen.blit(font.render("Oxygen", True, (0, 0, 0)), (230, 17))
    
    # FADE IN at startup (before countdown and start screen)
    if fade_in_active:
        fade_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        fade_surface.fill((0, 0, 0, fade_in_alpha))
        screen.blit(fade_surface, (0, 0))
        fade_in_alpha -= 4  # Lower for slower fade, higher for faster
        if fade_in_alpha <= 0:
            fade_in_active = False
            fade_in_alpha = 0
        pygame.display.flip()
        clock.tick(60)
        continue  # Skip the rest until fade-in is done

    # Start Screen
    if start_screen:
        # Flicker "Press any key" every 500ms
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            start_text = font.render("Press any key to start", True, (255, 255, 255))
            rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(start_text, rect)
        pygame.display.flip()
        clock.tick(60)
        continue  # skip rest of loop until started

    if countdown_active:
        if countdown_value > 0:
            countdown_str = str(countdown_value)
        else:
            countdown_str = "GO!"

        # Render text in black (for the outline)
        countdown_font = pygame.font.SysFont("arial", int(font_size * 2), bold=True)
        text_black = countdown_font.render(countdown_str, True, (0, 0, 0))
        text_white = countdown_font.render(countdown_str, True, (255, 255, 255))

        rect = text_black.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        # Blit black outline in 8 directions (up, down, left, right, and diagonals)
        for dx in [-2, 0, 2]:
            for dy in [-2, 0, 2]:
                if dx != 0 or dy != 0:
                    screen.blit(text_black, rect.move(dx, dy))

        # Blit white text in center
        screen.blit(text_white, rect)

        pygame.display.flip()
        clock.tick(60)
        continue  # skip rest of loop during countdown


    # ─── IF GAME OVER: DRAW DEATH OVERLAY & MENU ─────────────────────────────────────
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

    # ─── IF GAME WIN: TRIGGER NEXT LEVEL ────────────────────────────────────────────
    elif win_fade_active:
        # Make rocket fly up
        if rocket_takeoff_y < HEIGHT:
            rocket_takeoff_y += 7  # Speed of takeoff
        # Optionally, move the player with the rocket for realism
        rocket_draw_y = rocket.y - rocket_takeoff_y
        if player_entered_rocket:
            player.y = rocket_draw_y + rocket.height - player.height // 2  # Stay inside rocket

        win_msg = font.render("YOU WON! Onto the next level...", True, (0, 255, 0))
        rect = win_msg.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(win_msg, rect)

        # Clamp alpha between 0 and 255
        win_fade_alpha = min(max(int(win_fade_alpha), 0), 255)
        fade_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        fade_surface.fill((0, 0, 0, win_fade_alpha))
        screen.blit(fade_surface, (0, 0))

        if win_fade_alpha < 255:
            win_fade_alpha += 2
        else:
            import moon
            moon.menu()
            break



    # ─── IF PAUSED: DRAW PAUSE OVERLAY & MENU ───────────────────────────────────────
    if paused:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        pause_title_font = pygame.font.SysFont("arial", int(font_size * 1.2), bold=True)
        pause_help_font  = pygame.font.SysFont("arial", int(font_size * 0.6))
        paused_text      = pause_title_font.render("PAUSED", True, (255, 255, 255))
        paused_rect      = paused_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 160))
        screen.blit(paused_text, paused_rect)

        help_lines = ["Use UP and DOWN to navigate", "Press ENTER to choose"]
        for i, line in enumerate(help_lines):
            txt  = pause_help_font.render(line, True, (255, 255, 255))
            rect = txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 110 + i * 30))
            screen.blit(txt, rect)

        pause_font = pygame.font.SysFont("arial", font_size, bold=True)
        for i, opt in enumerate(pause_options):
            y    = HEIGHT // 2 + i * 70
            surf = pause_font.render(opt, True, (255, 255, 255))
            rect = surf.get_rect(center=(WIDTH // 2, y))
            if pause_choice == i + 1:
                pulse = int(100 + 80 * math.sin(pygame.time.get_ticks() * 0.005))
                pygame.draw.rect(screen, (pulse, pulse, pulse), rect.inflate(40, 20), border_radius=12)
            screen.blit(surf, rect)

    pygame.display.flip()
    clock.tick(60)
