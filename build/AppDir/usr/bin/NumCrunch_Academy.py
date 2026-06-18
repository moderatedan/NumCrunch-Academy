import pygame
import random
import sys
import math
from pathlib import Path

# Initialize pygame
pygame.init()
try:
    pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
    pygame.mixer.init()
except Exception:
    print('Audio not available - continuing without sound')

# Game constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 5
CELL_SIZE = 80
GRID_OFFSET_X = (WIDTH - GRID_SIZE * CELL_SIZE) // 2
GRID_OFFSET_Y = (HEIGHT - GRID_SIZE * CELL_SIZE) // 2
WIN_SCORE = 1000

# Colors
WHITE = (255, 255, 255, 128)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)
ORANGE = (255, 140, 0)
MAGENTA = (255, 0, 255)
CYAN = (0, 255, 255)
DARK_RED = (139, 0, 0)
GOLD = (255, 215, 0)
PURPLE = (148, 0, 211)

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NumCrunch Academy")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont('Arial', 32)
small_font = pygame.font.SysFont('Arial', 24)
title_font = pygame.font.SysFont('Arial', 48)
level_up_font = pygame.font.SysFont('Arial', 48, bold=True)
big_font = pygame.font.SysFont('Arial', 80, bold=True)
boom_font = pygame.font.SysFont('Arial', 64, bold=True)

# ============================================================================
# DIFFICULTY & STAGE SYSTEM
# ============================================================================
# Base stages
BASE_STAGES = [
    {'threshold': 0,   'enemy_speed': 1500, 'name': "Neon Classroom",      'operations': ['addition', 'subtraction'],                                       'bomb_count': 0},
    {'threshold': 50,  'enemy_speed': 1200, 'name': "Chalkboard Challenge", 'operations': ['addition', 'subtraction', 'multiplication'],                     'bomb_count': 2},
    {'threshold': 100, 'enemy_speed': 900,  'name': "Venice Voyage",        'operations': ['addition', 'subtraction', 'multiplication', 'division'],          'bomb_count': 3},
    {'threshold': 220, 'enemy_speed': 700,  'name': "Gothic Gauntlet",      'operations': ['addition', 'subtraction', 'multiplication', 'division'],          'bomb_count': 4},
    {'threshold': 350, 'enemy_speed': 550,  'name': "Steampunk Mayhem",     'operations': ['addition', 'subtraction', 'multiplication', 'division'],          'bomb_count': 5},
    {'threshold': 500, 'enemy_speed': 400,  'name': "Ironclad Abyss",       'operations': ['addition', 'subtraction', 'multiplication', 'division'],          'bomb_count': 6},
    {'threshold': 700, 'enemy_speed': 280,  'name': "Drowned Citadel",      'operations': ['addition', 'subtraction', 'multiplication', 'division'],          'bomb_count': 7},
]

difficulty = "normal"  # "easy", "normal", "hard"
STAGES = BASE_STAGES[:]

def apply_difficulty():
    global STAGES
    STAGES = []
    for st in BASE_STAGES:
        s = dict(st)
        if difficulty == "easy":
            s['enemy_speed'] = int(st['enemy_speed'] * 1.3)
            s['bomb_count'] = max(0, st['bomb_count'] - 1)
            s['threshold'] = int(st['threshold'] * 1.4)
        elif difficulty == "hard":
            s['enemy_speed'] = int(st['enemy_speed'] * 0.7)
            s['bomb_count'] = st['bomb_count'] + 1
            s['threshold'] = int(st['threshold'] * 0.7)
        STAGES.append(s)
    STAGES[0]['threshold'] = 0  # Always start at 0

def get_stage_for_score(s):
    stage = 0
    for i, st in enumerate(STAGES):
        if s >= st['threshold']:
            stage = i
    return stage

def get_enemy_speed():
    return STAGES[get_stage_for_score(score)]['enemy_speed']


# ============================================================================
# PARTICLE / CONFETTI SYSTEM
# ============================================================================
class Particle:
    def __init__(self, x, y, color=None, vx=None, vy=None, size=None, life=None, gravity=0.15):
        self.x = x
        self.y = y
        self.vx = vx if vx is not None else random.uniform(-6, 6)
        self.vy = vy if vy is not None else random.uniform(-14, -4)
        self.color = color or random.choice([RED, GREEN, BLUE, YELLOW, ORANGE, MAGENTA, CYAN, WHITE[:3]])
        self.size = size or random.randint(4, 10)
        self.life = life or random.randint(60, 120)
        self.max_life = self.life
        self.gravity = gravity
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-8, 8)

    def update(self):
        self.x += self.vx
        self.vy += self.gravity
        self.y += self.vy
        self.life -= 1
        self.rotation += self.rot_speed

    def draw(self, surface):
        if self.life <= 0: return
        alpha = max(0, min(255, int(255 * (self.life / self.max_life))))
        s = max(1, self.size)
        piece = pygame.Surface((s, s), pygame.SRCALPHA)
        piece.fill((min(255, self.color[0]), min(255, self.color[1]), min(255, self.color[2]), alpha))
        rotated = pygame.transform.rotate(piece, self.rotation)
        surface.blit(rotated, rotated.get_rect(center=(int(self.x), int(self.y))))

    def is_alive(self):
        return self.life > 0 and self.y < HEIGHT + 50

particles = []

def spawn_confetti(x, y, count=80):
    for _ in range(count):
        particles.append(Particle(
            x + random.randint(-50, 50),
            y + random.randint(-20, 20),
            vx=random.uniform(-8, 8),
            vy=random.uniform(-16, -5),
            size=random.randint(5, 12),
            life=random.randint(80, 160),
            gravity=0.12
        ))

def spawn_explosion(x, y, count=30):
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(3, 10)
        particles.append(Particle(
            x, y,
            color=random.choice([RED, ORANGE, YELLOW, (255, 80, 0)]),
            vx=math.cos(angle) * speed,
            vy=math.sin(angle) * speed - 3,
            size=random.randint(3, 8),
            life=random.randint(20, 50),
            gravity=0.2
        ))

def spawn_win_confetti():
    for _ in range(200):
        particles.append(Particle(
            random.randint(0, WIDTH),
            random.randint(-50, 0),
            vx=random.uniform(-4, 4),
            vy=random.uniform(2, 8),
            size=random.randint(6, 14),
            life=random.randint(120, 240),
            gravity=0.05
        ))

def update_and_draw_particles(surface):
    global particles
    for p in particles:
        p.update()
        p.draw(surface)
    particles = [p for p in particles if p.is_alive()]


# ============================================================================
# SKULL GAME OVER ANIMATION
# ============================================================================
game_over_animating = False
game_over_anim_timer = 0
GAME_OVER_ANIM_DURATION = 120
screen_shake_amount = 0

def draw_skull(surface, cx, cy, size):
    s = max(1, int(size))
    half = s // 2
    pygame.draw.ellipse(surface, (240, 230, 210), (cx - half, cy - half, s, int(s * 1.1)))
    pygame.draw.ellipse(surface, BLACK, (cx - half, cy - half, s, int(s * 1.1)), max(1, s // 20))
    eye_size = max(2, s // 4)
    eye_y = cy - half // 5
    left_eye_x = cx - half // 3
    right_eye_x = cx + half // 3
    pygame.draw.ellipse(surface, BLACK, (left_eye_x - eye_size//2, eye_y - eye_size//2, eye_size, int(eye_size * 1.2)))
    pygame.draw.ellipse(surface, BLACK, (right_eye_x - eye_size//2, eye_y - eye_size//2, eye_size, int(eye_size * 1.2)))
    glow_size = max(1, eye_size // 3)
    pygame.draw.circle(surface, RED, (left_eye_x, eye_y), glow_size)
    pygame.draw.circle(surface, RED, (right_eye_x, eye_y), glow_size)
    nose_size = max(1, s // 10)
    nose_y = cy + half // 6
    pygame.draw.polygon(surface, BLACK, [
        (cx, nose_y - nose_size),
        (cx - nose_size // 2, nose_y + nose_size // 2),
        (cx + nose_size // 2, nose_y + nose_size // 2)
    ])
    mouth_y = cy + half // 2
    mouth_w = max(2, s // 2)
    mouth_h = max(1, s // 8)
    teeth_count = max(2, s // 15)
    tooth_w = max(1, mouth_w // teeth_count)
    for i in range(teeth_count):
        tx = cx - mouth_w // 2 + i * tooth_w
        pygame.draw.rect(surface, (240, 230, 210) if i % 2 == 0 else BLACK, (tx, mouth_y, tooth_w, mouth_h))
    pygame.draw.rect(surface, BLACK, (cx - mouth_w // 2, mouth_y, mouth_w, mouth_h), max(1, s // 30))


# ============================================================================
# BOMB SYSTEM
# ============================================================================
bomb_positions = []
bomb_hit_timer = 0

def draw_bomb(surface, x, y, cell_size):
    cx = x + cell_size // 2
    cy = y + cell_size // 2
    bomb_r = cell_size // 4
    pygame.draw.circle(surface, BLACK, (cx, cy + 4), bomb_r)
    pygame.draw.circle(surface, (40, 40, 40), (cx, cy + 4), bomb_r - 2)
    pygame.draw.circle(surface, (80, 80, 80), (cx - bomb_r // 3, cy - bomb_r // 4 + 4), bomb_r // 4)
    fuse_points = [(cx, cy + 4 - bomb_r), (cx + 4, cy - bomb_r - 4), (cx + 8, cy - bomb_r - 2), (cx + 10, cy - bomb_r - 8)]
    pygame.draw.lines(surface, (139, 90, 43), False, fuse_points, 2)
    spark_color = YELLOW if pygame.time.get_ticks() % 300 < 150 else ORANGE
    pygame.draw.circle(surface, spark_color, (cx + 10, cy - bomb_r - 8), 3)
    pygame.draw.circle(surface, RED, (cx + 10, cy - bomb_r - 8), 2)


# ============================================================================
# ASSET LOADING
# ============================================================================
def load_assets():
    assets = {
        'images': {},
        'backgrounds': [],
        'sounds': {'hurt': None, 'click': None, 'correct': None, 'munch': None, 'victory': None},
        'music': None
    }
    base_path = Path(__file__).parent

    sound_files = {
        'hurt': '386893__samueleunimancer__ouch-screem.wav',
        'click': 'click.wav',
        'correct': 'correct.wav',
        'munch': 'munch.wav',
        'victory': 'victory.flac'
    }
    for sound_name, filename in sound_files.items():
        try:
            path = base_path / 'assets' / 'sounds' / filename
            assets['sounds'][sound_name] = pygame.mixer.Sound(path)
            if sound_name == 'hurt': assets['sounds'][sound_name].set_volume(0.8)
            elif sound_name in ['victory', 'correct', 'munch']: assets['sounds'][sound_name].set_volume(1.0)
            else: assets['sounds'][sound_name].set_volume(0.7)
        except: pass

    try:
        pygame.mixer.music.load(str(base_path / 'assets' / 'sounds' / 'background.wav'))
        pygame.mixer.music.set_volume(0.4)
        assets['music'] = True
    except: pass

    for img_name in ['player', 'enemy']:
        try:
            img = pygame.image.load(str(base_path / 'assets' / 'images' / f'{img_name}.png')).convert_alpha()
            assets['images'][img_name] = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
        except:
            surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            surf.fill(BLUE if img_name == 'player' else RED)
            assets['images'][img_name] = surf

    bg_candidates = [
        ['background.png'],
        ['background2.jpg', 'background2.png'],
        ['background3.jpg', 'background3.png'],
        ['background4.jpg', 'background4.png'],
        ['background5.jpg', 'background5.png'],
        ['background6.jpg', 'background6.png'],
        ['background7.jpg', 'background7.png'],
    ]
    for level_idx, filenames in enumerate(bg_candidates):
        loaded = False
        for fname in filenames:
            for search_dir in [base_path / 'assets' / 'images', base_path]:
                try:
                    path = search_dir / fname
                    if path.exists():
                        img = pygame.image.load(str(path)).convert()
                        assets['backgrounds'].append(pygame.transform.scale(img, (WIDTH, HEIGHT)))
                        print(f"Background stage {level_idx} ({BASE_STAGES[level_idx]['name']}) loaded: {path}")
                        loaded = True
                        break
                except: pass
            if loaded: break
        if not loaded:
            surf = pygame.Surface((WIDTH, HEIGHT))
            surf.fill(GRAY)
            assets['backgrounds'].append(surf)

    assets['images']['background'] = assets['backgrounds'][0]
    return assets

assets = load_assets()

# Game variables
player_pos = [GRID_SIZE // 2, GRID_SIZE // 2]
enemy_pos = [0, 0]
grid_values = []
current_problem = ""
correct_answer = 0
score = 0
lives = 3
game_active = False
game_won = False
feedback_text = None
feedback_time = 0
last_enemy_move = 0
current_stage = 0
level_up_timer = 0
hit_shake_timer = 0
player_flash_timer = 0
win_anim_timer = 0
WIN_ANIM_DURATION = 300  # 5 seconds of celebration


# ============================================================================
# MENU BUTTONS
# ============================================================================
def draw_menu():
    screen.blit(assets['images']['background'], (0, 0))
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    screen.blit(overlay, (0, 0))

    title = title_font.render("NumCrunch Academy", True, GOLD)
    screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//4)))

    # Difficulty buttons
    buttons = [
        ("EASY", (WIDTH//2 - 220, HEIGHT//2 - 20, 120, 60), GREEN,   "easy"),
        ("NORMAL", (WIDTH//2 - 60,  HEIGHT//2 - 20, 120, 60), YELLOW, "normal"),
        ("HARD",   (WIDTH//2 + 100, HEIGHT//2 - 20, 120, 60), RED,    "hard"),
    ]

    diff_label = font.render("Select Difficulty:", True, WHITE)
    screen.blit(diff_label, diff_label.get_rect(center=(WIDTH//2, HEIGHT//2 - 55)))

    mx, my = pygame.mouse.get_pos()
    for label, rect, color, mode in buttons:
        r = pygame.Rect(rect)
        hover = r.collidepoint(mx, my)
        border = 4 if mode == difficulty else 2
        alpha = 220 if hover else 180
        btn_surf = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
        btn_surf.fill((*color, alpha))
        screen.blit(btn_surf, r)
        pygame.draw.rect(screen, WHITE if mode == difficulty else GRAY, r, border, border_radius=8)
        btn_text = font.render(label, True, BLACK)
        screen.blit(btn_text, btn_text.get_rect(center=r.center))

    start_text = font.render("Press any key or click to Start", True, WHITE)
    screen.blit(start_text, start_text.get_rect(center=(WIDTH//2, HEIGHT*3//4)))

    hint = small_font.render("Easy: slower enemy, fewer bombs  |  Hard: faster enemy, more bombs", True, GRAY)
    screen.blit(hint, hint.get_rect(center=(WIDTH//2, HEIGHT*3//4 + 40)))

    return buttons


# ============================================================================
# GAME LOGIC
# ============================================================================
def generate_problem():
    op = random.choice(STAGES[get_stage_for_score(score)]['operations'])
    if op == 'addition':
        a, b = random.randint(1, 20), random.randint(1, 20)
        return f"{a} + {b} = ?", a + b
    elif op == 'subtraction':
        a = random.randint(1, 20)
        b = random.randint(1, a)
        return f"{a} - {b} = ?", a - b
    elif op == 'multiplication':
        a, b = random.randint(2, 12), random.randint(2, 12)
        return f"{a} × {b} = ?", a * b
    elif op == 'division':
        b = random.randint(2, 12)
        answer = random.randint(2, 12)
        return f"{b * answer} ÷ {b} = ?", answer

def generate_grid():
    global grid_values, current_problem, correct_answer, bomb_positions
    grid_values = []
    bomb_positions = []
    current_problem, correct_answer = generate_problem()
    occupied = {(player_pos[1], player_pos[0]), (enemy_pos[1], enemy_pos[0])}
    empty = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if (r, c) not in occupied]
    correct_row, correct_col = random.choice(empty)
    occupied.add((correct_row, correct_col))
    stage = get_stage_for_score(score)
    available = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if (r, c) not in occupied]
    random.shuffle(available)
    for i in range(min(STAGES[stage]['bomb_count'], len(available))):
        bomb_positions.append(available[i])
        occupied.add(available[i])
    for i in range(GRID_SIZE * GRID_SIZE):
        if i == correct_row * GRID_SIZE + correct_col:
            grid_values.append(correct_answer)
        else:
            wrong = correct_answer + random.randint(-5, 5)
            while wrong == correct_answer or wrong <= 0:
                wrong = correct_answer + random.randint(-5, 5)
            grid_values.append(wrong)

def move_enemy():
    global enemy_pos, lives, player_pos, hit_shake_timer, player_flash_timer
    possible_moves = []
    if enemy_pos[0] < player_pos[0]: possible_moves.append((1, 0))
    elif enemy_pos[0] > player_pos[0]: possible_moves.append((-1, 0))
    if enemy_pos[1] < player_pos[1]: possible_moves.append((0, 1))
    elif enemy_pos[1] > player_pos[1]: possible_moves.append((0, -1))
    if possible_moves:
        dx, dy = random.choice(possible_moves)
        nx, ny = enemy_pos[0] + dx, enemy_pos[1] + dy
        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
            enemy_pos = [nx, ny]
    if enemy_pos == player_pos:
        lives -= 1
        hit_shake_timer = 30
        player_flash_timer = 60
        show_feedback("OUCH! -1 Life", RED)
        if assets['sounds']['hurt']: assets['sounds']['hurt'].play()
        spawn_explosion(GRID_OFFSET_X + player_pos[0] * CELL_SIZE + CELL_SIZE // 2,
                       GRID_OFFSET_Y + player_pos[1] * CELL_SIZE + CELL_SIZE // 2, 20)
        player_pos = [GRID_SIZE // 2, GRID_SIZE // 2]
        if lives <= 0: trigger_game_over()

def show_feedback(message, color):
    global feedback_text, feedback_time
    feedback_text = (message, color)
    feedback_time = pygame.time.get_ticks() + 1000

def trigger_game_over():
    global game_over_animating, game_over_anim_timer, screen_shake_amount
    game_over_animating = True
    game_over_anim_timer = GAME_OVER_ANIM_DURATION
    screen_shake_amount = 0
    pygame.mixer.music.stop()

def trigger_win():
    global game_won, win_anim_timer, game_active
    game_won = True
    game_active = False
    win_anim_timer = WIN_ANIM_DURATION
    pygame.mixer.music.stop()
    if assets['sounds']['victory']: assets['sounds']['victory'].play()
    spawn_win_confetti()

def end_game():
    global game_active
    game_active = False
    if assets['sounds']['victory']: assets['sounds']['victory'].play()

def start_game():
    global player_pos, enemy_pos, score, lives, game_active, last_enemy_move
    global current_stage, level_up_timer, game_over_animating, game_over_anim_timer
    global bomb_hit_timer, particles, hit_shake_timer, player_flash_timer, feedback_text
    global game_won, win_anim_timer
    apply_difficulty()
    player_pos = [GRID_SIZE // 2, GRID_SIZE // 2]
    enemy_pos = [0, 0]
    score = 0
    lives = 3
    game_active = True
    game_won = False
    win_anim_timer = 0
    current_stage = 0
    level_up_timer = 0
    game_over_animating = False
    game_over_anim_timer = 0
    bomb_hit_timer = 0
    hit_shake_timer = 0
    player_flash_timer = 0
    feedback_text = None
    particles = []
    last_enemy_move = pygame.time.get_ticks()
    generate_grid()
    if assets['music']: pygame.mixer.music.play(-1)

def get_current_background():
    idx = min(current_stage, len(assets['backgrounds']) - 1)
    return assets['backgrounds'][idx]

def check_bomb_hit():
    global lives, bomb_hit_timer
    player_grid = (player_pos[1], player_pos[0])
    if player_grid in bomb_positions:
        bomb_positions.remove(player_grid)
        lives -= 1
        bomb_hit_timer = 60
        spawn_explosion(GRID_OFFSET_X + player_pos[0] * CELL_SIZE + CELL_SIZE // 2,
                       GRID_OFFSET_Y + player_pos[1] * CELL_SIZE + CELL_SIZE // 2, 40)
        show_feedback("BOOM! -1 Life", ORANGE)
        if assets['sounds']['hurt']: assets['sounds']['hurt'].play()
        if lives <= 0: trigger_game_over()
        return True
    return False


# ============================================================================
# DRAWING
# ============================================================================
def draw_grid():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = GRID_OFFSET_X + col * CELL_SIZE
            y = GRID_OFFSET_Y + row * CELL_SIZE
            is_bomb = (row, col) in bomb_positions
            cell = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            cell.fill((255, 200, 200, 140) if is_bomb else WHITE)
            screen.blit(cell, (x, y))
            pygame.draw.rect(screen, DARK_RED if is_bomb else BLACK, (x, y, CELL_SIZE, CELL_SIZE), 2)
            if is_bomb:
                draw_bomb(screen, x, y, CELL_SIZE)
            else:
                value = grid_values[row * GRID_SIZE + col]
                num_text = font.render(str(value), True, GREEN if value == correct_answer else BLACK)
                screen.blit(num_text, (x + CELL_SIZE//2 - num_text.get_width()//2,
                                       y + CELL_SIZE//2 - num_text.get_height()//2))

def draw_entities():
    global player_flash_timer
    px = GRID_OFFSET_X + player_pos[0] * CELL_SIZE
    py = GRID_OFFSET_Y + player_pos[1] * CELL_SIZE
    ex = GRID_OFFSET_X + enemy_pos[0] * CELL_SIZE
    ey = GRID_OFFSET_Y + enemy_pos[1] * CELL_SIZE
    if player_flash_timer > 0:
        player_flash_timer -= 1
        py += int(math.sin(player_flash_timer * 0.8) * 6)
        if (player_flash_timer // 4) % 2 == 0:
            screen.blit(assets['images']['player'], (px, py))
            tint = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            tint.fill((255, 0, 0, 80))
            screen.blit(tint, (px, py))
    else:
        screen.blit(assets['images']['player'], (px, py))
    screen.blit(assets['images']['enemy'], (ex, ey))

def draw_ui():
    screen.blit(small_font.render(f"Score: {score}/{WIN_SCORE}", True, BLACK), (20, 20))
    screen.blit(small_font.render(f"Lives: {lives}", True, BLACK), (20, 50))
    diff_color = GREEN if difficulty == "easy" else YELLOW if difficulty == "normal" else RED
    screen.blit(small_font.render(difficulty.upper(), True, diff_color), (20, 75))
    screen.blit(font.render(current_problem, True, BLACK),
                (WIDTH//2 - font.size(current_problem)[0]//2, 20))
    hint = small_font.render("Move to the correct answer to munch it!", True, BLACK)
    screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 80))
    if current_stage < len(STAGES):
        stage_label = small_font.render(f"Stage: {STAGES[current_stage]['name']}", True, WHITE)
        stage_shadow = small_font.render(f"Stage: {STAGES[current_stage]['name']}", True, BLACK)
        screen.blit(stage_shadow, (WIDTH - stage_label.get_width() - 9, HEIGHT - 29))
        screen.blit(stage_label, (WIDTH - stage_label.get_width() - 10, HEIGHT - 30))
    if feedback_text and pygame.time.get_ticks() < feedback_time:
        msg, color = feedback_text
        fb = font.render(msg, True, color)
        screen.blit(fb, (WIDTH//2 - fb.get_width()//2, HEIGHT - 50))

def draw_bomb_hit():
    global bomb_hit_timer
    if bomb_hit_timer <= 0: return
    bomb_hit_timer -= 1
    size = int(64 * (1.0 + (60 - bomb_hit_timer) * 0.02))
    boom_f = pygame.font.SysFont('Arial', size, bold=True)
    boom_text = boom_f.render("BOOM!", True, ORANGE)
    boom_shadow = boom_f.render("BOOM!", True, DARK_RED)
    rect = boom_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(boom_shadow, (rect.x + 3, rect.y + 3))
    screen.blit(boom_text, rect)

def draw_level_up():
    global level_up_timer
    if level_up_timer <= 0: return
    level_up_timer -= 1
    alpha = min(255, level_up_timer * 3)
    overlay_band = pygame.Surface((WIDTH, 120), pygame.SRCALPHA)
    overlay_band.fill((0, 0, 0, min(160, alpha)))
    screen.blit(overlay_band, (0, HEIGHT // 2 - 60))
    lu_text = level_up_font.render("LEVEL UP!", True, YELLOW)
    lu_shadow = level_up_font.render("LEVEL UP!", True, BLACK)
    lu_rect = lu_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 15))
    screen.blit(lu_shadow, (lu_rect.x + 2, lu_rect.y + 2))
    screen.blit(lu_text, lu_rect)
    if current_stage < len(STAGES):
        stage_text = font.render(STAGES[current_stage]['name'], True, GREEN)
        screen.blit(stage_text, stage_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 25)))

def draw_win_screen():
    global win_anim_timer
    screen.blit(get_current_background(), (0, 0))
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    # Spawn more confetti periodically
    if win_anim_timer % 20 == 0:
        spawn_win_confetti()

    update_and_draw_particles(screen)

    # Pulsing YOU WIN text
    pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 0.2 + 0.9
    win_size = int(80 * pulse)
    win_f = pygame.font.SysFont('Arial', win_size, bold=True)
    win_text = win_f.render("YOU WIN!", True, GOLD)
    win_shadow = win_f.render("YOU WIN!", True, ORANGE)
    win_rect = win_text.get_rect(center=(WIDTH//2, HEIGHT//3))
    screen.blit(win_shadow, (win_rect.x + 3, win_rect.y + 3))
    screen.blit(win_text, win_rect)

    score_text = font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(score_text, score_text.get_rect(center=(WIDTH//2, HEIGHT//2)))

    diff_text = font.render(f"Difficulty: {difficulty.upper()}", True,
                            GREEN if difficulty == "easy" else YELLOW if difficulty == "normal" else RED)
    screen.blit(diff_text, diff_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50)))

    play_again = font.render("Press any key to Play Again", True, GREEN)
    screen.blit(play_again, play_again.get_rect(center=(WIDTH//2, HEIGHT*2//3 + 20)))

    if win_anim_timer > 0:
        win_anim_timer -= 1

def draw_game_over_animation():
    global game_over_anim_timer, game_over_animating, screen_shake_amount
    if not game_over_animating: return False
    game_over_anim_timer -= 1
    progress = 1.0 - (game_over_anim_timer / GAME_OVER_ANIM_DURATION)
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, min(220, int(progress * 280))))
    screen.blit(overlay, (0, 0))
    if progress > 0.3:
        screen_shake_amount = min(15, int((progress - 0.3) * 30))
    if progress < 0.85:
        if progress > 0.2:
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 0, 0, min(80, int((progress - 0.2) * 120))))
            screen.blit(flash, (0, 0))
        draw_skull(screen, WIDTH // 2, HEIGHT // 2, int(20 + progress * 250))
    else:
        draw_skull(screen, WIDTH // 2, HEIGHT // 2 - 40, 200)
        go_text = title_font.render("GAME OVER", True, RED)
        go_shadow = title_font.render("GAME OVER", True, BLACK)
        go_rect = go_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
        screen.blit(go_shadow, (go_rect.x + 3, go_rect.y + 3))
        screen.blit(go_text, go_rect)
    if game_over_anim_timer <= 0:
        game_over_animating = False
        screen_shake_amount = 0
        end_game()
    return True

def draw_game_over():
    screen.blit(get_current_background(), (0, 0))
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    draw_skull(screen, WIDTH // 2, HEIGHT // 3 - 20, 100)
    screen.blit(font.render(f"Final Score: {score}", True, WHITE),
                (WIDTH//2 - font.size(f"Final Score: {score}")[0]//2, HEIGHT//2))
    screen.blit(font.render("Press any key to Play Again", True, GREEN),
                (WIDTH//2 - font.size("Press any key to Play Again")[0]//2, HEIGHT*2//3))


# ============================================================================
# MAIN GAME LOOP
# ============================================================================
apply_difficulty()
running = True
render_surface = pygame.Surface((WIDTH, HEIGHT))
menu_buttons = []

while running:
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and not game_active and not game_won:
            mx, my = pygame.mouse.get_pos()
            for label, rect, color, mode in menu_buttons:
                if pygame.Rect(rect).collidepoint(mx, my):
                    difficulty = mode
                    break
            else:
                start_game()

        if event.type == pygame.KEYDOWN:
            if game_over_animating: continue
            if not game_active:
                start_game()
                continue
            new_pos = list(player_pos)
            if event.key == pygame.K_LEFT and player_pos[0] > 0: new_pos[0] -= 1
            elif event.key == pygame.K_RIGHT and player_pos[0] < GRID_SIZE - 1: new_pos[0] += 1
            elif event.key == pygame.K_UP and player_pos[1] > 0: new_pos[1] -= 1
            elif event.key == pygame.K_DOWN and player_pos[1] < GRID_SIZE - 1: new_pos[1] += 1
            if new_pos != player_pos:
                player_pos = new_pos
                if assets['sounds']['click']: assets['sounds']['click'].play()
                if not check_bomb_hit():
                    selected_index = player_pos[1] * GRID_SIZE + player_pos[0]
                    if grid_values[selected_index] == correct_answer:
                        old_stage = get_stage_for_score(score)
                        score += 10
                        # Check win
                        if score >= WIN_SCORE:
                            trigger_win()
                            continue
                        new_stage = get_stage_for_score(score)
                        if new_stage > old_stage and new_stage < len(STAGES):
                            current_stage = new_stage
                            level_up_timer = 180
                            lives += 1
                            spawn_confetti(WIDTH // 2, HEIGHT // 3, 100)
                            print(f"Stage up! {STAGES[new_stage]['name']} | +1 life ({lives}) | Enemy speed: {STAGES[new_stage]['enemy_speed']}ms")
                        feedback_text = ("Correct! +10", GREEN)
                        if assets['sounds']['munch']: assets['sounds']['munch'].play()
                        generate_grid()
                feedback_time = current_time + 1000

    if game_active and not game_over_animating and current_time - last_enemy_move > get_enemy_speed():
        move_enemy()
        last_enemy_move = current_time

    # ---- RENDER ----
    if game_won:
        draw_win_screen()
    elif game_active or game_over_animating:
        screen.blit(get_current_background(), (0, 0))
        draw_grid()
        draw_entities()
        draw_ui()
        draw_bomb_hit()
        update_and_draw_particles(screen)
        draw_level_up()
        if game_over_animating:
            draw_game_over_animation()
    else:
        if lives <= 0:
            screen.blit(get_current_background(), (0, 0))
            draw_game_over()
            update_and_draw_particles(screen)
        else:
            menu_buttons = draw_menu()
            update_and_draw_particles(screen)

    if hit_shake_timer > 0:
        hit_shake_timer -= 1
    total_shake = screen_shake_amount
    if hit_shake_timer > 0:
        total_shake = max(total_shake, min(10, hit_shake_timer // 2))
    if total_shake > 0:
        shake_x = random.randint(-total_shake, total_shake)
        shake_y = random.randint(-total_shake, total_shake)
        render_surface.blit(screen, (0, 0))
        screen.fill(BLACK)
        screen.blit(render_surface, (shake_x, shake_y))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
