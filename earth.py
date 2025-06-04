import pygame, sys, random, math

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Mars Escape")
clock = pygame.time.Clock()

MUSIC_FILE = "audio/level3.wav"
MUSIC_FADE_IN_MS = 2500  # 2.5 seconds fade in
MUSIC_FADE_OUT_MS = 1200 

font_size = int(HEIGHT * 0.05)
font = pygame.font.SysFont("arial", font_size, bold=True)
main_font = pygame.font.SysFont("arial", 40)
skip_font = pygame.font.SysFont("arial", 20)
PLATFORM_OFFSET_Y = HEIGHT -200

bg_img = pygame.image.load("assets/earth_background.png").convert()
bg_img = pygame.transform.scale(bg_img, (WIDTH + PLATFORM_OFFSET_Y, HEIGHT))
BG_WIDTH = WIDTH + PLATFORM_OFFSET_Y
bg_glitch_intensity = 0

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
scrambled_controls = False
loop_active = True
reverted_keys = False
zombie_direction = 1
ok = 0

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
    pygame.Rect(0, 280 + PLATFORM_OFFSET_Y, 8000, 20),  # ground
    pygame.Rect(200, -320 + PLATFORM_OFFSET_Y, 150, 20),
    pygame.Rect(570, -280 + PLATFORM_OFFSET_Y, 100, 20),
    pygame.Rect(1570, -280 + PLATFORM_OFFSET_Y, 100, 20),
    pygame.Rect(1870, -200 + PLATFORM_OFFSET_Y, 100, 20),
    pygame.Rect(2170, -180 + PLATFORM_OFFSET_Y, 100, 20),
    pygame.Rect(2170, -300 + PLATFORM_OFFSET_Y, 100, 20), #facing left
    pygame.Rect(2370, -200 + PLATFORM_OFFSET_Y, 4500, 20),  # loop room
]
loop_zone_x_start = 3770
loop_zone_x_end = 5870
rectdirection = 1
bg_shake = 0
messages = [
    ("You have finally reached the Earth.", (255, 255, 255)),      
    ("You were away for over 40 years now.", (17, 35, 128)),     
    ("Earth is under apocalypse though.", (79, 23, 110)),          
    ("You don't have much time...", (255, 80, 80)),                
]


rocket = pygame.Rect(31900, -300 + PLATFORM_OFFSET_Y, 60, 50)
zombie = pygame.Rect(33000, 40 + PLATFORM_OFFSET_Y, 60, 60)
ok = 0

camera_x = 0

# Level ends at the farthest platform or rocket edge
last_platform_right = max(p.right for p in platforms)
level_end_x = max(last_platform_right, rocket.right)
max_camera_x_level = level_end_x - WIDTH
max_camera_x_bg = int((BG_WIDTH - WIDTH) / 0.2)
final_max_camera_x = min(max_camera_x_level, max_camera_x_bg)
ground_right = platforms[0].right  
show_revert_message = False
revert_msg_timer = 0

def game_over_cause():
    global death_cause
    if player.y > 500:
        death_cause = "Fell off"
    # 3) Ran out of oxygen?
    if oxygen <= 0:
        death_cause = "Ran Out of Oxygen"
        return

    # 4) Alien collisions:
    if player.colliderect(zombie):
        death_cause = "Eaten by a Zombie"
        return

    # 5) Fell off bottom of the map:
    if player.y > HEIGHT:
        death_cause = "Fell Off the Map"
        return


    # (If nothing else matched, you could set a default cause here.)
    elif death_cause == "":
        death_cause = "Unknown"


def reset_game():
    global player, velocity_y, oxygen, game_over, game_win, loop_active, reverted_keys, zombie_direction, zombie, rocket
    player.x, player.y = 250, -360 + PLATFORM_OFFSET_Y
    velocity_y = 0
    oxygen = 100
    game_over = False
    game_win = False
    platforms[2].x = 1370
    loop_active = True
    reverted_keys = False
    zombie_direction = 1
    rocket = pygame.Rect(31900, -300 + PLATFORM_OFFSET_Y, 60, 50)
    zombie = pygame.Rect(33000, 40 + PLATFORM_OFFSET_Y, 60, 60)
    loop_platform = pygame.Rect(2370, -200 + PLATFORM_OFFSET_Y, 4500, 20)
    if len(platforms) < 8:
        platforms.insert(7, loop_platform)
    
def render_glitched_background():
    shake_x = random.randint(-bg_glitch_intensity, bg_glitch_intensity)
    shake_y = random.randint(-bg_glitch_intensity, bg_glitch_intensity)
    screen.blit(bg_img, (-camera_x * 0.2 + shake_x, 0 + shake_y))

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

def show_revert_text():
    global reverted_keys

    screen.fill((0, 0, 0))
    msg1 = "You escaped the loop!"
    msg2 = "But you're now dizzy — your movement is different. Be careful!"

    text1 = font.render(msg1, True, (255, 255, 255))
    text2 = font.render(msg2, True, (255, 80, 80))

    rect1 = text1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
    rect2 = text2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))

    # Fade in
    for alpha in range(0, 256, 10):
        text1.set_alpha(alpha)
        text2.set_alpha(alpha)
        screen.fill((0, 0, 0))
        screen.blit(text1, rect1)
        screen.blit(text2, rect2)
        pygame.display.update()
        pygame.time.delay(30)

    # Pause
    pygame.time.delay(2000)

    # Fade out
    for alpha in range(255, -1, -10):
        text1.set_alpha(alpha)
        text2.set_alpha(alpha)
        screen.fill((0, 0, 0))
        screen.blit(text1, rect1)
        screen.blit(text2, rect2)
        pygame.display.update()
        pygame.time.delay(30)

    reverted_keys = True


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
changed_plats = []
def change_map():
    global loop_active, changed_plats, zombie, rocket
    if 7 < len(platforms):
        if player.y <= -320 + PLATFORM_OFFSET_Y and player.x >2170 and player.x <=2250:
            show_revert_text()
            platforms.pop(7)
            loop_active = False
            rocket = pygame.Rect(3190, -370 + PLATFORM_OFFSET_Y, 60, 80)
            zombie = pygame.Rect(3300, 40 + PLATFORM_OFFSET_Y, 60, 60)
    changed_plats = [
    pygame.Rect(2370, -300 + PLATFORM_OFFSET_Y, 100, 20), 
    pygame.Rect(2570, -200 + PLATFORM_OFFSET_Y, 100, 20),  
    pygame.Rect(2770, -100 + PLATFORM_OFFSET_Y, 100, 20), 
    pygame.Rect(2970, 100 + PLATFORM_OFFSET_Y, 400, 20),   
    pygame.Rect(3170, 0 + PLATFORM_OFFSET_Y, 50, 20),  
    pygame.Rect(3170, -100 + PLATFORM_OFFSET_Y, 50, 20), 
    pygame.Rect(3170, -200 + PLATFORM_OFFSET_Y, 50, 20), 
    pygame.Rect(3170, -300 + PLATFORM_OFFSET_Y, 100, 20),  
    ]


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
                countdown_active = False
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
                if reverted_keys == False:
                    if (event.key == pygame.K_SPACE or event.key == pygame.K_w or event.key == pygame.K_UP) and on_ground:
                        velocity_y = JUMP_STRENGTH
                        on_ground = False
                        jump_sound.play()
                else:
                    if (event.key == pygame.K_LEFT or event.key == pygame.K_a) and on_ground:
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
        if reverted_keys == False:
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
        else:
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dx = -PLAYER_SPEED
                facing_right = False
            if keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]:
                dx =  PLAYER_SPEED
                facing_right = True

            # 2) Jump:
            if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and on_ground:
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
                if plat == platforms[6] and facing_right == True:
                    continue
                # Only land if we were falling onto it:
                if velocity_y > 0 and player.bottom <= plat.bottom:
                    player.bottom = plat.top
                    velocity_y = 0
                    on_ground = True
        for plat in changed_plats:
            if loop_active == False:
                if player.colliderect(plat):
                    if velocity_y > 0 and player.bottom <= plat.bottom:
                        player.bottom = plat.top
                        velocity_y = 0
                        on_ground = True
                    if plat == changed_plats[0]:
                        reverted_keys = True


        
        
        change_map()
        
        if (player.x>2920 or ok == 1) and loop_active == False:
            ok = 1
            zombie.x += zombie_direction * 5
            if zombie.x < 2920 or zombie.x > 3350:
                zombie_direction *= -1



            # Check if zombie catches player
            if zombie.colliderect(player):
                game_over = True
                death_cause = "Caught by the zombie!"
                game_over_cause()
        if player.y >500 + PLATFORM_OFFSET_Y:
            game_over = True
            game_over_cause()

        # 7) Decrease oxygen each frame:
        oxygen -= OXYGEN_DECREASE
        if oxygen <= 0:
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
        if plat == platforms[6] and facing_right == True:
            continue
        pygame.draw.rect(screen, (50, 50, 50), (plat.x - camera_x, plat.y, plat.width, plat.height))
        if plat == platforms[2]:
            plat.x += rectdirection * 3
            if plat.x < 470 or plat.x > 1400:
                rectdirection *= -1
    for plat in changed_plats:
        if loop_active == False:
            pygame.draw.rect(screen, (50, 50, 50), (plat.x - camera_x, plat.y, plat.width, plat.height))

    if loop_active and player.x > loop_zone_x_end:
        player.x = loop_zone_x_start + 10
        bg_glitch_intensity += 1 
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
    #pygame.draw.rect(screen, (255, 255, 255), (20, 20, 200, 20))
    #pygame.draw.rect(screen, (0, 100, 255), (20, 20, max(0, int(oxygen * 2)), 20))
    #screen.blit(font.render("Oxygen", True, (0, 0, 0)), (230, 17))

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
        screen.fill(0, 0 , 0)
        msg1 = "YOU ESCAPED... now what...."
        msg2 = "Earth is gone."

        text1 = font.render(msg1, True, (0, 255, 0))
        text2 = font.render(msg2, True, (255, 0, 0))

        rect1 = text1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        rect2 = text2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))

        # Fade in msg1
        if win_fade_alpha < 255:
            text1.set_alpha(win_fade_alpha)
            screen.blit(text1, rect1)
            win_fade_alpha += 3

        # Start pause timer after msg1 is fully shown
        elif win_fade_alpha == 255:
            screen.blit(text1, rect1)
            win_pause_timer = pygame.time.get_ticks()
            win_fade_alpha += 1  # Move to next phase

        # Pause phase between messages
        elif 255 < win_fade_alpha < 500:
            screen.blit(text1, rect1)
            if pygame.time.get_ticks() - win_pause_timer > 2000:
                win_fade_alpha = 500  # Begin fading in second message

        # Fade in msg2 only
        elif 500 <= win_fade_alpha < 755:
            alpha2 = win_fade_alpha - 500
            text1.set_alpha(255)
            text2.set_alpha(alpha2)
            screen.blit(text1, rect1)
            screen.blit(text2, rect2)
            win_fade_alpha += 3

        # After both messages are fully shown — delay then exit
        else:
            screen.blit(text1, rect1)
            screen.blit(text2, rect2)
            pygame.display.update()
            pygame.time.delay(2000)
            pygame.quit()
            sys.exit()

# or return or sys.exit() as needed



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
