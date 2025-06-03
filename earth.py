import pygame, sys, random, math

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Mars Escape")
clock = pygame.time.Clock()

font_size = int(HEIGHT * 0.05)
font = pygame.font.SysFont("arial", font_size, bold=True)
main_font = pygame.font.SysFont("arial", 40)
skip_font = pygame.font.SysFont("arial", 20)
PLATFORM_OFFSET_Y = HEIGHT - 600

bg_img = pygame.image.load("assets/earth_background.png").convert()
bg_img = pygame.transform.scale(bg_img, (WIDTH + PLATFORM_OFFSET_Y, HEIGHT))
BG_WIDTH = WIDTH + PLATFORM_OFFSET_Y

zombie_img = pygame.image.load("assets/zombie1.png").convert_alpha()
zombie_img = pygame.transform.scale(zombie_img, (60, 60))
rocket_img = pygame.image.load("assets/rocket2.png")
rocket_img = pygame.transform.scale(rocket_img, (60, 70))
player_stand = pygame.image.load("assets/player_stand.png").convert_alpha()
player_walk_1 = pygame.image.load("assets/player_walk_1.png").convert_alpha()
player_walk_2 = pygame.image.load("assets/player_walk_2.png").convert_alpha()
player_jump = pygame.image.load("assets/jump.png").convert_alpha()

player_stand = pygame.transform.scale(player_stand, (40, 50))
player_walk_1 = pygame.transform.scale(player_walk_1, (40, 50))
player_walk_2 = pygame.transform.scale(player_walk_2, (40, 50))
player_jump = pygame.transform.scale(player_jump, (40, 50))
walk_images = [player_walk_1, player_walk_2]

PLAYER_SPEED = 5
GRAVITY = 0.5
JUMP_STRENGTH = -10
OXYGEN_DECREASE = 0

player = pygame.Rect(250, -370 + PLATFORM_OFFSET_Y, 40, 50)
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
pygame.mixer.init()
pygame.mixer.music.load("audio/fast_earth.mp3")
pygame.mixer.music.play(-1)  # Loop indefinitely
pygame.mixer.music.set_volume(0.3)


win_fade_active = False
win_fade_alpha = 0

paused = False
pause_options = ["Continue", "Restart Level", "Main Menu"]
pause_choice = 1

death_options = ["Restart Level", "Return to Main Menu"]
death_choice = 1


platforms = [
    pygame.Rect(0, 580 + PLATFORM_OFFSET_Y, 4000, 20),
    pygame.Rect(200, -320 + PLATFORM_OFFSET_Y, 150, 20),
    pygame.Rect(570, -280 + PLATFORM_OFFSET_Y, 100, 20),
    pygame.Rect(1570, -280 + PLATFORM_OFFSET_Y, 100, 20),
    pygame.Rect(1770, -200 + PLATFORM_OFFSET_Y, 100, 20),


]
rectdirection = 1
messages = [
    ("You have finally reached the Earth.", (255, 255, 255)),      
    ("You were away for over 40 years now.", (17, 35, 128)),     
    ("Earth is under apocalypse though.", (79, 23, 110)),          
    ("You don't have much time...", (255, 80, 80)),                
]


rocket = pygame.Rect(3650, 270 + PLATFORM_OFFSET_Y, 60, 50)
zombie = pygame.Rect(300, 390 + PLATFORM_OFFSET_Y, 60, 60)
ok = 0

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

    # 3) Ran out of oxygen?
    if oxygen <= 0:
        death_cause = "Ran Out of Oxygen"
        return

    # 4) Alien collisions:
    if player.colliderect(zombie):
        death_cause = "Alien 1"
        return

    # 5) Fell off bottom of the map:
    if player.y > HEIGHT:
        death_cause = "Fell Off the Map"
        return


    # (If nothing else matched, you could set a default cause here.)
    death_cause = "Unknown"


def reset_game():
    global player, velocity_y, oxygen, game_over, game_win
    player.x, player.y = 250, -360 + PLATFORM_OFFSET_Y
    velocity_y = 0
    oxygen = 100
    game_over = False
    game_win = False
    

def render_and_fade(screen, text, color, font, skip_text, skip_rect, start_time):
    bg = pygame.Surface((WIDTH, HEIGHT))
    bg.fill((0, 0, 0))

    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    blink_interval = 400  # ms
    skip_display_time = 6000  # ms (stop showing skip text after 4 sec)

    for alpha in range(0, 256, 5):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return True
            elif event.type == pygame.QUIT:
                pygame.quit()
                exit()

        screen.fill((0, 0, 0))
        text_surf.set_alpha(alpha)
        screen.blit(text_surf, text_rect)

        elapsed = pygame.time.get_ticks() - start_time
        if elapsed < skip_display_time and (elapsed // blink_interval) % 2 == 0:
            screen.blit(skip_text, skip_rect)

        pygame.display.update()
        pygame.time.delay(30)

    pygame.time.delay(1500)

    for alpha in range(255, -1, -5):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return True
            elif event.type == pygame.QUIT:
                pygame.quit()
                exit()

        screen.fill((0, 0, 0))
        text_surf.set_alpha(alpha)
        screen.blit(text_surf, text_rect)

        elapsed = pygame.time.get_ticks() - start_time
        if elapsed < skip_display_time and (elapsed // blink_interval) % 2 == 0:
            screen.blit(skip_text, skip_rect)

        pygame.display.update()
        pygame.time.delay(30)

    return False


def show_intro(screen, messages, font, skip_font):
    screen.fill((0, 0, 0))
    pygame.display.update()

    skip_text = skip_font.render("Press ENTER to skip", True, (200, 200, 200))
    skip_rect = skip_text.get_rect(bottomright=(WIDTH - 20, HEIGHT - 20))

    start_time = pygame.time.get_ticks()
    skip_visible = True

    for text, color in messages:
        elapsed = pygame.time.get_ticks() - start_time
        skipped = render_and_fade(screen, text, color, font, skip_text, skip_rect, start_time)
        if skipped:
            break


spawn_timer = 0
show_intro(screen, messages, font, skip_font)
pygame.mixer.music.fadeout(2000)  # 2 second fadeout

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

        # 7) Decrease oxygen each frame:
        oxygen -= OXYGEN_DECREASE
        if oxygen <= 0:
            game_over = True
            game_over_cause()

        # 8) Check alien collisions:
        if player.colliderect(zombie):
            game_over = True
            game_over_cause()

        # 9) Check rocket win:
        if player.colliderect(rocket):
            game_win = True
            win_fade_active = True
            win_fade_alpha = 0

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
        if plat.x > 460 and plat.x < 1500:
            plat.x += rectdirection * 3
            if plat.x < 470 or plat.x > 1400:
                rectdirection *= -1
    screen.blit(zombie_img, (zombie.x - camera_x, zombie.y))
    screen.blit(rocket_img, (rocket.x - camera_x, rocket.y))
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

    screen.blit(current_img, (player.x - camera_x, player.y))

    # ─── OXYGEN BAR ─────────────────────────────────────────────────────────────────
    pygame.draw.rect(screen, (255, 255, 255), (20, 20, 200, 20))
    pygame.draw.rect(screen, (0, 100, 255), (20, 20, max(0, int(oxygen * 2)), 20))
    screen.blit(font.render("Oxygen", True, (0, 0, 0)), (230, 17))
    
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
        win_msg = font.render("YOU WON! Onto the next level...", True, (0, 255, 0))
        rect = win_msg.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(win_msg, rect)

        # Clamp alpha between 0 and 255
        win_fade_alpha = min(max(int(win_fade_alpha), 0), 255)

        # Create fade overlay with alpha support
        fade_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        fade_surface.fill((0, 0, 0, win_fade_alpha))
        screen.blit(fade_surface, (0, 0))

        if win_fade_alpha < 255:
            win_fade_alpha += 2  # Or your chosen step
        else:
            import moon
            moon.menu()
            break  # or return or sys.exit() as needed



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
