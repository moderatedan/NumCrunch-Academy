import pygame
import random
import sys
import os

pygame.init()

WIDTH, HEIGHT = 800, 600
GRID_SIZE = 5
CELL_SIZE = 80
GRID_OFFSET_X = (WIDTH - GRID_SIZE * CELL_SIZE) // 2
GRID_OFFSET_Y = (HEIGHT - GRID_SIZE * CELL_SIZE) // 2

WHITE = (255, 255, 255, 200)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)
GOLD = (255, 215, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NumCrunch Academy")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 32)
small_font = pygame.font.SysFont('Arial', 24)
big_font = pygame.font.SysFont('Arial', 64, bold=True)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
os.makedirs(SPRITES_DIR, exist_ok=True)
os.makedirs(SOUNDS_DIR, exist_ok=True)

# Level config: (score_threshold, ops_allowed, troggle_move_chance, bg_filename, label)
LEVEL_CONFIG = [
    (0,   ["addition"],                              0.012, "background.png",  "Level 1: Addition"),
    (50,  ["addition", "subtraction"],               0.018, "bg_level2.jpg",   "Level 2: Subtraction"),
    (120, ["addition", "subtraction", "multiplication"], 0.025, "bg_level3.jpg", "Level 3: Multiplication"),
    (220, ["addition", "subtraction", "multiplication", "division"], 0.033, "bg_level4.jpg", "Level 4: Division"),
    (350, ["addition", "subtraction", "multiplication", "division"], 0.042, "bg_level5.jpg", "Level 5: Mixed Mayhem"),
]

# Sound setup
sound_enabled = False
crunch_sound = None
victory_sound = None

try:
    pygame.mixer.init()
    pygame.mixer.set_num_channels(8)
    for sound_file in ["crunch.wav", "munch.wav", "bite.wav"]:
        sound_path = os.path.join(SOUNDS_DIR, sound_file)
        if os.path.exists(sound_path):
            try:
                crunch_sound = pygame.mixer.Sound(sound_path)
                crunch_sound.set_volume(0.7)
                break
            except Exception: pass
    for sound_file in ["victory.flac", "success.wav", "win.flac", "celebration.wav"]:
        sound_path = os.path.join(SOUNDS_DIR, sound_file)
        if os.path.exists(sound_path):
            try:
                victory_sound = pygame.mixer.Sound(sound_path)
                victory_sound.set_volume(0.7)
                break
            except Exception: pass
    for music_file in ["background.wav", "background_music.wav", "music.mp3"]:
        music_path = os.path.join(SOUNDS_DIR, music_file)
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.4)
                sound_enabled = True
                break
            except Exception: pass
except Exception as e:
    print(f"Sound initialization failed: {e}")
    sound_enabled = False

def load_background(filename):
    for ext_try in [filename]:
        path = os.path.join(SPRITES_DIR, ext_try)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path)
                return pygame.transform.scale(img, (WIDTH, HEIGHT))
            except Exception as e:
                print(f"Couldn't load {path}: {e}")
    return None

# Load all level backgrounds upfront
level_backgrounds = [load_background(cfg[3]) for cfg in LEVEL_CONFIG]

# Fallback solid color surfaces if images missing
fallback_colors = [(30,30,60), (40,20,40), (20,40,20), (50,30,10), (10,10,50)]
for i, bg in enumerate(level_backgrounds):
    if bg is None:
        surf = pygame.Surface((WIDTH, HEIGHT))
        surf.fill(fallback_colors[i])
        level_backgrounds[i] = surf

# Load player sprite
player_sprite = None
for player_file in ["player.png", "cruncher.png"]:
    player_path = os.path.join(SPRITES_DIR, player_file)
    if os.path.exists(player_path):
        try:
            player_sprite = pygame.image.load(player_path)
            player_sprite = pygame.transform.scale(player_sprite, (CELL_SIZE, CELL_SIZE))
            break
        except Exception: pass

# Load enemy sprite
enemy_sprite = None
for enemy_file in ["enemy.png", "troublemaker.png"]:
    enemy_path = os.path.join(SPRITES_DIR, enemy_file)
    if os.path.exists(enemy_path):
        try:
            enemy_sprite = pygame.image.load(enemy_path)
            enemy_sprite = pygame.transform.scale(enemy_sprite, (CELL_SIZE, CELL_SIZE))
            break
        except Exception: pass

# Game variables
player_pos = [2, 2]
score = 0
lives = 3
current_problem = ""
correct_answer = 0
grid_values = []
game_state = "playing"  # "playing", "game_over", "levelup"
troggle_pos = [random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)]
current_level = 0
levelup_timer = 0
LEVELUP_DURATION = 2000  # ms

def get_level_for_score(s):
    lvl = 0
    for i, cfg in enumerate(LEVEL_CONFIG):
        if s >= cfg[0]:
            lvl = i
    return lvl

def generate_problem():
    ops = LEVEL_CONFIG[current_level][1]
    problem_type = random.choice(ops)
    if problem_type == "addition":
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        return f"{a} + {b}", a + b
    elif problem_type == "subtraction":
        a = random.randint(1, 20)
        b = random.randint(1, a)
        return f"{a} - {b}", a - b
    elif problem_type == "multiplication":
        a = random.randint(1, 12)
        b = random.randint(1, 12)
        return f"{a} × {b}", a * b
    elif problem_type == "division":
        b = random.randint(1, 12)
        answer = random.randint(1, 12)
        return f"{b * answer} ÷ {b}", answer

def generate_grid():
    global grid_values, correct_answer, current_problem
    current_problem, correct_answer = generate_problem()
    grid_values = []
    distances = []
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            distances.append((abs(col - player_pos[0]) + abs(row - player_pos[1]), row, col))
    distances.sort()
    _, correct_row, correct_col = random.choice(distances[:3])
    correct_pos = correct_row * GRID_SIZE + correct_col
    for i in range(GRID_SIZE * GRID_SIZE):
        if i == correct_pos:
            grid_values.append(correct_answer)
        else:
            offset = random.randint(-3, 3)
            while offset == 0:
                offset = random.randint(-3, 3)
            grid_values.append(correct_answer + offset)

def check_level_up():
    global current_level, game_state, levelup_timer
    new_level = get_level_for_score(score)
    if new_level > current_level:
        current_level = new_level
        game_state = "levelup"
        levelup_timer = pygame.time.get_ticks()

def draw_grid():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = GRID_OFFSET_X + col * CELL_SIZE
            y = GRID_OFFSET_Y + row * CELL_SIZE
            cell_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            cell_surface.fill(WHITE)
            screen.blit(cell_surface, (x, y))
            pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 2)
            index = row * GRID_SIZE + col
            text = font.render(str(grid_values[index]), True, BLACK)
            text_rect = text.get_rect(center=(x + CELL_SIZE//2, y + CELL_SIZE//2))
            screen.blit(text, text_rect)

def draw_player():
    x = GRID_OFFSET_X + player_pos[0] * CELL_SIZE
    y = GRID_OFFSET_Y + player_pos[1] * CELL_SIZE
    if player_sprite:
        screen.blit(player_sprite, player_sprite.get_rect(center=(x + CELL_SIZE//2, y + CELL_SIZE//2)))
    else:
        pygame.draw.circle(screen, GREEN, (x + CELL_SIZE//2, y + CELL_SIZE//2), CELL_SIZE//3)
        for ox in [-10, 10]:
            pygame.draw.circle(screen, (255,255,255), (x + CELL_SIZE//2 + ox, y + CELL_SIZE//2 - 5), CELL_SIZE//10)
            pygame.draw.circle(screen, BLACK, (x + CELL_SIZE//2 + ox, y + CELL_SIZE//2 - 5), CELL_SIZE//20)

def draw_troggle():
    x = GRID_OFFSET_X + troggle_pos[0] * CELL_SIZE
    y = GRID_OFFSET_Y + troggle_pos[1] * CELL_SIZE
    if enemy_sprite:
        screen.blit(enemy_sprite, enemy_sprite.get_rect(center=(x + CELL_SIZE//2, y + CELL_SIZE//2)))
    else:
        pygame.draw.circle(screen, RED, (x + CELL_SIZE//2, y + CELL_SIZE//2), CELL_SIZE//3)

def draw_hud():
    hud_bg = pygame.Surface((WIDTH, 80), pygame.SRCALPHA)
    hud_bg.fill((200, 200, 200, 150))
    screen.blit(hud_bg, (0, 0))
    screen.blit(small_font.render(f"Score: {score}", True, BLACK), (20, 10))
    screen.blit(small_font.render(f"Lives: {lives}", True, BLACK), (20, 40))
    screen.blit(small_font.render(LEVEL_CONFIG[current_level][4], True, GOLD), (WIDTH - 220, 10))
    problem_text = font.render(f"Find: {current_problem} = ?", True, BLUE)
    screen.blit(problem_text, problem_text.get_rect(center=(WIDTH//2, 50)))

def draw_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    screen.blit(font.render("GAME OVER", True, RED),
                font.render("GAME OVER", True, RED).get_rect(center=(WIDTH//2, HEIGHT//2 - 50)))
    screen.blit(font.render(f"Final Score: {score}", True, WHITE),
                font.render(f"Final Score: {score}", True, WHITE).get_rect(center=(WIDTH//2, HEIGHT//2)))
    screen.blit(small_font.render("Press R to restart", True, WHITE),
                small_font.render("Press R to restart", True, WHITE).get_rect(center=(WIDTH//2, HEIGHT//2 + 50)))

def draw_levelup():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))
    label = LEVEL_CONFIG[current_level][4]
    txt1 = big_font.render("LEVEL UP!", True, GOLD)
    txt2 = font.render(label, True, WHITE)
    screen.blit(txt1, txt1.get_rect(center=(WIDTH//2, HEIGHT//2 - 40)))
    screen.blit(txt2, txt2.get_rect(center=(WIDTH//2, HEIGHT//2 + 30)))

def check_answer():
    global score, lives, game_state
    index = player_pos[1] * GRID_SIZE + player_pos[0]
    if grid_values[index] == correct_answer:
        score += 10
        if sound_enabled and crunch_sound:
            try: crunch_sound.play()
            except Exception: pass
        check_level_up()
        if game_state == "playing":
            generate_grid()
        if score % 50 == 0 and sound_enabled and victory_sound:
            try: victory_sound.play()
            except Exception: pass
    else:
        lives -= 1
        if lives <= 0:
            game_state = "game_over"

def move_troggle():
    move_chance = LEVEL_CONFIG[current_level][2]
    if random.random() < move_chance:
        direction = random.choice(["left", "right", "up", "down"])
        if direction == "left" and troggle_pos[0] > 0: troggle_pos[0] -= 1
        elif direction == "right" and troggle_pos[0] < GRID_SIZE-1: troggle_pos[0] += 1
        elif direction == "up" and troggle_pos[1] > 0: troggle_pos[1] -= 1
        elif direction == "down" and troggle_pos[1] < GRID_SIZE-1: troggle_pos[1] += 1

def check_troggle_collision():
    global lives, game_state
    if player_pos == troggle_pos and game_state == "playing":
        lives -= 1
        if lives <= 0:
            game_state = "game_over"
        else:
            troggle_pos[0] = random.randint(0, GRID_SIZE-1)
            troggle_pos[1] = random.randint(0, GRID_SIZE-1)
            while troggle_pos == player_pos:
                troggle_pos[0] = random.randint(0, GRID_SIZE-1)
                troggle_pos[1] = random.randint(0, GRID_SIZE-1)

def reset_game():
    global player_pos, troggle_pos, score, lives, game_state, current_level
    player_pos[:] = [2, 2]
    troggle_pos[:] = [random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)]
    score = 0
    lives = 3
    current_level = 0
    game_state = "playing"
    generate_grid()
    if sound_enabled:
        pygame.mixer.music.play(-1)

generate_grid()
if sound_enabled:
    pygame.mixer.music.play(-1)

running = True
while running:
    now = pygame.time.get_ticks()

    # Draw background for current level
    screen.blit(level_backgrounds[current_level], (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == "playing":
            if event.type == pygame.KEYDOWN:
                moved = False
                if event.key == pygame.K_LEFT and player_pos[0] > 0:
                    player_pos[0] -= 1; moved = True
                elif event.key == pygame.K_RIGHT and player_pos[0] < GRID_SIZE - 1:
                    player_pos[0] += 1; moved = True
                elif event.key == pygame.K_UP and player_pos[1] > 0:
                    player_pos[1] -= 1; moved = True
                elif event.key == pygame.K_DOWN and player_pos[1] < GRID_SIZE - 1:
                    player_pos[1] += 1; moved = True
                elif event.key == pygame.K_m and sound_enabled:
                    if pygame.mixer.music.get_busy(): pygame.mixer.music.pause()
                    else: pygame.mixer.music.unpause()
                if moved:
                    check_answer()
                    check_troggle_collision()

        elif game_state == "levelup":
            # Auto-resume after LEVELUP_DURATION
            if now - levelup_timer >= LEVELUP_DURATION:
                game_state = "playing"
                generate_grid()

        elif game_state == "game_over":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                reset_game()

    if game_state == "playing":
        move_troggle()
        check_troggle_collision()

    draw_grid()
    draw_player()
    draw_troggle()
    draw_hud()

    if game_state == "game_over":
        draw_game_over()
    elif game_state == "levelup":
        draw_levelup()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
if sound_enabled:
    pygame.mixer.quit()
sys.exit()
