import asyncio
import pygame
import random
import math
pygame.init()
WIDTH = 900
HEIGHT = 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()
BLACK = (5, 8, 20)
WHITE = (255, 255, 255)

BLUE = (60, 180, 255)
LIGHT_BLUE = (170, 235, 255)

GREEN = (50, 255, 130)

RED = (255, 70, 80)
DARK_RED = (140, 20, 30)

YELLOW = (255, 230, 50)
ORANGE = (255, 150, 40)

PURPLE = (180, 80, 255)

CYAN = (50, 240, 255)

font_small = pygame.font.Font(None, 26)
font = pygame.font.Font(None, 38)
font_big = pygame.font.Font(None, 72)
sound_enabled = False
MENU = "menu"
PLAYING = "playing"
PAUSED = "paused"
GAME_OVER = "game_over"
game_state = MENU
player_width = 60
player_height = 55
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - 90
player_speed = 7
lives = 3
bullets = []
bullet_width = 6
bullet_height = 18
bullet_speed = 11
normal_cooldown = 220
rapid_cooldown = 80
last_shot = 0
rapid_fire = False
rapid_fire_end = 0
shield = False
shield_end = 0
enemies = []
enemy_width = 55
enemy_height = 45
score = 0
level = 1
powerups = []
powerup_width = 28
powerup_height = 28
powerup_speed = 3
explosions = []
stars = []
for i in range(120):
    stars.append([
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.randint(1, 3)
    ])
def create_enemy():
    speed = random.uniform(
        1.0 + level * 0.15,
        1.8 + level * 0.20
    )
    enemy = {
        "x": random.randint(
            20,
            WIDTH - enemy_width - 20
        ),
        "y": random.randint(
            -150,
            -50
        ),
        "speed": speed
    }
    enemies.append(enemy)
def create_powerup(x, y):
    power_type = random.choice([
        "rapid",
        "shield",
        "life"
    ])
    powerups.append({
        "x": x,
        "y": y,
        "type": power_type
    })
def reset_game():
    global player_x
    global player_y
    global lives
    global score
    global level
    global bullets
    global enemies
    global powerups
    global explosions
    global rapid_fire
    global shield
    global game_state
    global last_shot
    player_x = WIDTH // 2 - player_width // 2
    player_y = HEIGHT - 90
    lives = 3
    score = 0
    level = 1
    bullets = []
    enemies = []
    powerups = []
    explosions = []
    rapid_fire = False
    shield = False
    last_shot = 0
    game_state = PLAYING
    for i in range(3):
        create_enemy()
def update_level():
    global level
    new_level = 1 + score // 10
    if new_level > level:
        level = new_level
def draw_player():
    x = player_x
    y = player_y
    if shield:
        pygame.draw.circle(
            screen,
            CYAN,
            (
                x + player_width // 2,
                y + player_height // 2
            ),
            42,
            3
        )
    points = [
        (x + player_width // 2, y),
        (x + player_width, y + player_height),
        (
            x + player_width // 2,
            y + player_height - 12
        ),
        (x, y + player_height)
    ]
    pygame.draw.polygon(
        screen,
        BLUE,
        points
    )
    pygame.draw.ellipse(
        screen,
        LIGHT_BLUE,
        (
            x + 20,
            y + 10,
            20,
            22
        )
    )
    pygame.draw.polygon(
        screen,
        PURPLE,
        [
            (x + 5, y + 42),
            (x + 23, y + 28),
            (x + 22, y + 52)
        ]
    )
    pygame.draw.polygon(
        screen,
        PURPLE,
        [
            (x + 55, y + 42),
            (x + 37, y + 28),
            (x + 38, y + 52)
        ]
    )
    pygame.draw.polygon(
        screen,
        ORANGE,
        [
            (x + 25, y + 47),
            (x + 35, y + 47),
            (x + 30, y + 62)
        ]
    )
def draw_enemy(enemy):
    x = enemy["x"]
    y = enemy["y"]
    pygame.draw.ellipse(
        screen,
        RED,
        (
            x,
            y + 8,
            enemy_width,
            enemy_height - 8
        )
    )
    pygame.draw.circle(
        screen,
        YELLOW,
        (x + 18, y + 22),
        6
    )
    pygame.draw.circle(
        screen,
        YELLOW,
        (x + 37, y + 22),
        6
    )
    pygame.draw.circle(
        screen,
        DARK_RED,
        (x + 18, y + 22),
        2
    )
    pygame.draw.circle(
        screen,
        DARK_RED,
        (x + 37, y + 22),
        2
    )
    pygame.draw.line(
        screen,
        DARK_RED,
        (x + 18, y + 35),
        (x + 37, y + 35),
        3
    )
    pygame.draw.line(
        screen,
        RED,
        (x + 15, y + 12),
        (x + 8, y),
        3
    )
    pygame.draw.line(
        screen,
        RED,
        (x + 40, y + 12),
        (x + 47, y),
        3
    )
def draw_powerup(powerup):
    x = powerup["x"]
    y = powerup["y"]
    if powerup["type"] == "rapid":
        color = YELLOW
        text = "R"
    elif powerup["type"] == "shield":
        color = CYAN
        text = "S"
    else:
        color = GREEN
        text = "+"
    pygame.draw.circle(
        screen,
        color,
        (
            int(x + powerup_width / 2),
            int(y + powerup_height / 2)
        ),
        14
    )
    power_text = font_small.render(
        text,
        True,
        BLACK
    )
    rect = power_text.get_rect(
        center=(
            int(x + powerup_width / 2),
            int(y + powerup_height / 2)
        )
    )
    screen.blit(
        power_text,
        rect
    )
def create_explosion(x, y):
    explosions.append({
        "x": x,
        "y": y,
        "size": 5,
        "life": 15
    })
def update_explosions():
    for explosion in explosions[:]:
        explosion["size"] += 3
        explosion["life"] -= 1
        if explosion["life"] <= 0:
            explosions.remove(explosion)
def draw_explosions():
    for explosion in explosions:
        pygame.draw.circle(
            screen,
            ORANGE,
            (
                int(explosion["x"]),
                int(explosion["y"])
            ),
            explosion["size"],
            3
        )
def update_stars():
    for star in stars:
        star[1] += star[2]
        if star[1] > HEIGHT:
            star[1] = 0
            star[0] = random.randint(
                0,
                WIDTH
            )
def draw_stars():
    for star in stars:
        pygame.draw.circle(
            screen,
            WHITE,
            (
                star[0],
                star[1]
            ),
            1
        )
def draw_menu():
    screen.fill(BLACK)
    draw_stars()
    title = font_big.render(
        "SPACE SHOOTER",
        True,
        BLUE
    )
    screen.blit(
        title,
        title.get_rect(
            center=(WIDTH // 2, 180)
        )
    )
    start = font.render(
        "PRESS SPACE TO PLAY",
        True,
        WHITE
    )
    screen.blit(
        start,
        start.get_rect(
            center=(WIDTH // 2, 300)
        )
    )
    controls = font_small.render(
        "LEFT / RIGHT = Move",
        True,
        GREEN
    )
    screen.blit(
        controls,
        controls.get_rect(
            center=(WIDTH // 2, 360)
        )
    )
    controls2 = font_small.render(
        "SPACE = Shoot     P = Pause     ESC = Quit",
        True,
        GREEN
    )
    screen.blit(
        controls2,
        controls2.get_rect(
            center=(WIDTH // 2, 395)
        )
    )
    power = font_small.render(
        "Collect R = Rapid Fire   S = Shield   + = Life",
        True,
        YELLOW
    )
    screen.blit(
        power,
        power.get_rect(
            center=(WIDTH // 2, 440)
        )
    )
def draw_pause():
    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )
    overlay.fill(
        (0, 0, 0, 170)
    )
    screen.blit(
        overlay,
        (0, 0)
    )
    text = font_big.render(
        "PAUSED",
        True,
        WHITE
    )
    screen.blit(
        text,
        text.get_rect(
            center=(WIDTH // 2, 280)
        )
    )
    resume = font.render(
        "Press P to Continue",
        True,
        GREEN
    )
    screen.blit(
        resume,
        resume.get_rect(
            center=(WIDTH // 2, 350)
        )
    )
def draw_game_over():
    screen.fill(BLACK)
    draw_stars()
    title = font_big.render(
        "GAME OVER",
        True,
        RED
    )
    screen.blit(
        title,
        title.get_rect(
            center=(WIDTH // 2, 220)
        )
    )
    score_text = font.render(
        "Score: " + str(score),
        True,
        WHITE
    )
    screen.blit(
        score_text,
        score_text.get_rect(
            center=(WIDTH // 2, 310)
        )
    )
    level_text = font.render(
        "Level: " + str(level),
        True,
        YELLOW
    )
    screen.blit(
        level_text,
        level_text.get_rect(
            center=(WIDTH // 2, 350)
        )
    )
    restart = font.render(
        "Press R to Restart",
        True,
        GREEN
    )
    screen.blit(
        restart,
        restart.get_rect(
            center=(WIDTH // 2, 420)
        )
    )
def draw_game():
    screen.fill(BLACK)
    draw_stars()
    draw_player()
    for enemy in enemies:
        draw_enemy(enemy)
    for bullet in bullets:
        pygame.draw.rect(
            screen,
            YELLOW,
            (
                int(bullet[0]),
                int(bullet[1]),
                bullet_width,
                bullet_height
            )
        )
    for powerup in powerups:
        draw_powerup(powerup)
    draw_explosions()
    score_text = font.render(
        "Score: " + str(score),
        True,
        WHITE
    )
    screen.blit(
        score_text,
        (20, 15)
    )
    level_text = font.render(
        "Level: " + str(level),
        True,
        YELLOW
    )
    screen.blit(
        level_text,
        (20, 52)
    )
    lives_text = font.render(
        "Lives: " + str(lives),
        True,
        GREEN
    )
    screen.blit(
        lives_text,
        (WIDTH - 150, 15)
    )
    if rapid_fire:
        rapid_text = font_small.render(
            "RAPID FIRE",
            True,
            YELLOW
        )
        screen.blit(
            rapid_text,
            (WIDTH - 180, 55)
        )
    if shield:
        shield_text = font_small.render(
            "SHIELD",
            True,
            CYAN
        )
        screen.blit(
            shield_text,
            (WIDTH - 180, 80)
        )
def update_game(current_time):
    global rapid_fire_end
    global shield_end
    global player_x
    global rapid_fire
    global shield
    global bullets
    global enemies
    global powerups
    global lives
    global score
    global game_state
    global last_shot
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed
    if player_x < 0:
        player_x = 0
    if player_x > WIDTH - player_width:
        player_x = WIDTH - player_width
    if rapid_fire:
        if current_time > rapid_fire_end:
            rapid_fire = False
    if shield:
        if current_time > shield_end:
            shield = False
    cooldown = (
        rapid_cooldown
        if rapid_fire
        else normal_cooldown
    )
    if keys[pygame.K_SPACE]:
        if current_time - last_shot > cooldown:
            bullet_x = (
                player_x
                + player_width // 2
                - bullet_width // 2
            )
            bullet_y = player_y
            bullets.append([
                bullet_x,
                bullet_y
            ])
            last_shot = current_time
    for bullet in bullets:
        bullet[1] -= bullet_speed
    bullets = [
        bullet
        for bullet in bullets
        if bullet[1] > -bullet_height
    ]
    for enemy in enemies:
        enemy["y"] += enemy["speed"]
    max_enemies = min(
        3 + level,
        8
    )
    while len(enemies) < max_enemies:
        create_enemy()
    for bullet in bullets[:]:
        bullet_rect = pygame.Rect(
            int(bullet[0]),
            int(bullet[1]),
            bullet_width,
            bullet_height
        )
        for enemy in enemies[:]:
            enemy_rect = pygame.Rect(
                int(enemy["x"]),
                int(enemy["y"]),
                enemy_width,
                enemy_height
            )
            if bullet_rect.colliderect(enemy_rect):
                if bullet in bullets:
                    bullets.remove(bullet)
                if enemy in enemies:
                    enemies.remove(enemy)
                score += 1
                create_explosion(
                    enemy["x"] + enemy_width // 2,
                    enemy["y"] + enemy_height // 2
                )
                if random.random() < 0.15:
                    create_powerup(
                        enemy["x"],
                        enemy["y"]
                    )
                break
    player_rect = pygame.Rect(
        int(player_x),
        int(player_y),
        player_width,
        player_height
    )
    for enemy in enemies[:]:
        enemy_rect = pygame.Rect(
            int(enemy["x"]),
            int(enemy["y"]),
            enemy_width,
            enemy_height
        )
        if enemy_rect.colliderect(player_rect):
            enemies.remove(enemy)
            if shield:
                create_explosion(
                    enemy["x"],
                    enemy["y"]
                )
            else:
                lives -= 1
                create_explosion(
                    player_x + player_width // 2,
                    player_y + player_height // 2
                )
    for enemy in enemies[:]:
        if enemy["y"] > HEIGHT:
            enemies.remove(enemy)
            if not shield:
                lives -= 1
    for powerup in powerups:
        powerup["y"] += powerup_speed
    for powerup in powerups[:]:
        powerup_rect = pygame.Rect(
            int(powerup["x"]),
            int(powerup["y"]),
            powerup_width,
            powerup_height
        )
        if powerup_rect.colliderect(player_rect):
            power_type = powerup["type"]
            if power_type == "rapid":
                rapid_fire = True
                rapid_fire_end = (
                    current_time + 7000
                )
            elif power_type == "shield":
                shield = True
                shield_end = (
                    current_time + 7000
                )
            elif power_type == "life":
                lives = min(
                    lives + 1,
                    5
                )
            powerups.remove(powerup)
    powerups = [
        powerup
        for powerup in powerups
        if powerup["y"] < HEIGHT
    ]
    update_level()
    if lives <= 0:
        game_state = GAME_OVER
    update_stars()
    update_explosions()
async def main():
    global game_state
    running = True
    game_state = MENU
    while running:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if game_state == MENU:
                    if event.key == pygame.K_SPACE:
                        reset_game()
                elif game_state == PLAYING:
                    if event.key == pygame.K_p:
                        game_state = PAUSED
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                elif game_state == PAUSED:
                    if event.key == pygame.K_p:
                        game_state = PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                elif game_state == GAME_OVER:
                    if event.key == pygame.K_r:
                        reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
        if game_state == MENU:
            update_stars()
            draw_menu()
        elif game_state == PLAYING:
            update_game(current_time)
            draw_game()
        elif game_state == PAUSED:
            draw_game()
            draw_pause()
        elif game_state == GAME_OVER:
            update_stars()
            draw_game_over()
        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(60)
    pygame.quit()
asyncio.run(main())