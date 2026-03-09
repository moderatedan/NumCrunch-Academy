import pygame
import random
import sys
import math
from pathlib import Path

# Initialize pygame
pygame.init()
pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
pygame.mixer.init()

# Game constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 5
CELL_SIZE = 80
GRID_OFFSET_X = (WIDTH - GRID_SIZE * CELL_SIZE) // 2
GRID_OFFSET_Y = (HEIGHT - GRID_SIZE * CELL_SIZE) // 2

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

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NumCrunch Academy")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont('Arial', 32)
small_font = pygame.font.SysFont('Arial', 24)
title_font = pygame.font.SysFont('Arial', 48)
level_up_font = pygame.font.SysFont('Arial', 48, bold=True)
skull_font = pygame.font.SysFont('Arial', 120, bold=True)
boom_font = pygame.font.SysFont('Arial', 64, bold=True)

# ============================================================================
# STAGE PROGRESSION SYSTEM
# ============================================================================
STAGES = [
    {
        'threshold': 0,
        'enemy_speed': 1500,
        'name': "Neon Classroom",
        'operations': ['addition', 'subtraction'],
        'bomb_count': 0,
    },
    {
        'threshold': 50,
        'enemy_speed': 1200,
        'name': "Chalkboard Challenge",
        'operations': ['addition', 'subtraction', 'multiplication'],
        'bomb_count': 2,
    },
    {
        'threshold': 100,
        'enemy_speed': 900,
        'name': "Venice Voyage",
        'operations': ['addition', 'subtraction', 'multiplication', 'division'],
        'bomb_count': 3,
    },
]

def get_stage_for_score(s):
    stage = 0
    for i, st in enumerate(STAGES):
        if s >= st['threshold']:
            stage = i
    return stage

def get_enemy_speed():
    stage = get_stage_for_score(score)
    return STAGES[stage]['enemy_speed']


# ============================================================================
# PARTICLE / CONFETTI SYSTEM
# ============================================================================
class Particle:
    def __init__(self, x, y, color=None, vx=None, vy=None, size=None, life=None, gravity=0.15):
        self.x = x
        self.y = y
        self.vx = vx if vx is not None else random.uniform(-6, 6)
        self.vy = vy if vy is not None else random.uniform(-14, -4)
        self.color = color or random.choice([RED, GREEN, BLUE, YELLOW, ORANGE, MAGENTA, CYAN, (255, 255, 255)])
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
        if self.life <= 0:
            return
        alpha = max(0, min(255, int(255 * (self.life / self.max_life))))
        # Draw as a small rotated rectangle (confetti piece)
        s = max(1, self.size)
        piece = pygame.Surface((s, s), pygame.SRCALPHA)
        r = min(255, self.color[0])
        g = min(255, self.color[1])
        b = min(255, self.color[2])
        piece.fill((r, g, b, alpha))
        rotated = pygame.transform.rotate(piece, self.rotation)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated, rect)
    
    def is_alive(self):
        return self.life > 0 and self.y < HEIGHT + 50

particles = []

def spawn_confetti(x, y, count=80):
    """Spawn confetti particles at a position"""
    for _ in range(count):
        p = Particle(
            x + random.randint(-50, 50),
            y + random.randint(-20, 20),
            vx=random.uniform(-8, 8),
            vy=random.uniform(-16, -5),
            size=random.randint(5, 12),
            life=random.randint(80, 160),
            gravity=0.12
        )
        particles.append(p)

def spawn_explosion(x, y, count=30):
    """Spawn explosion particles (for bombs)"""
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(3, 10)
        p = Particle(
            x, y,
            color=random.choice([RED, ORANGE, YELLOW, (255, 80, 0)]),
            vx=math.cos(angle) * speed,
            vy=math.sin(angle) * speed - 3,
            size=random.randint(3, 8),
            life=random.randint(20, 50),
            gravity=0.2
        )
        particles.append(p)

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
GAME_OVER_ANIM_DURATION = 120  # 2 seconds at 60fps
screen_shake_amount = 0

def draw_skull(surface, cx, cy, size):
    """Draw a skull using pygame primitives"""
    s = max(1, int(size))
    half = s // 2
    
    # Skull shape (main head - slightly oval)
    pygame.draw.ellipse(surface, (240, 230, 210), (cx - half, cy - half, s, int(s * 1.1)))
    pygame.draw.ellipse(surface, BLACK, (cx - half, cy - half, s, int(s * 1.1)), max(1, s // 20))
    
    # Eye sockets
    eye_size = max(2, s // 4)
    eye_y = cy - half // 5
    left_eye_x = cx - half // 3
    right_eye_x = cx + half // 3
    pygame.draw.ellipse(surface, BLACK, (left_eye_x - eye_size//2, eye_y - eye_size//2, eye_size, int(eye_size * 1.2)))
    pygame.draw.ellipse(surface, BLACK, (right_eye_x - eye_size//2, eye_y - eye_size//2, eye_size, int(eye_size * 1.2)))
    
    # Red glow in eyes
    glow_size = max(1, eye_size // 3)
    pygame.draw.circle(surface, RED, (left_eye_x, eye_y), glow_size)
    pygame.draw.circle(surface, RED, (right_eye_x, eye_y), glow_size)
    
    # Nose
    nose_size = max(1, s // 10)
    nose_y = cy + half // 6
    pygame.draw.polygon(surface, BLACK, [
        (cx, nose_y - nose_size),
        (cx - nose_size // 2, nose_y + nose_size // 2),
        (cx + nose_size // 2, nose_y + nose_size // 2)
    ])
    
    # Mouth / teeth
    mouth_y = cy + half // 2
    mouth_w = max(2, s // 2)
    mouth_h = max(1, s // 8)
    teeth_count = max(2, s // 15)
    tooth_w = max(1, mouth_w // teeth_count)
    
    for i in range(teeth_count):
        tx = cx - mouth_w // 2 + i * tooth_w
        color = (240, 230, 210) if i % 2 == 0 else BLACK
        pygame.draw.rect(surface, color, (tx, mouth_y, tooth_w, mouth_h))
    pygame.draw.rect(surface, BLACK, (cx - mouth_w // 2, mouth_y, mouth_w, mouth_h), max(1, s // 30))


# ============================================================================
# BOMB SYSTEM
# ============================================================================
bomb_positions = []  # List of (row, col)
bomb_anim_timer = 0
bomb_hit_timer = 0  # For "BOOM!" text display

def draw_bomb(surface, x, y, cell_size):
    """Draw a bomb icon in a grid cell"""
    cx = x + cell_size // 2
    cy = y + cell_size // 2
    bomb_r = cell_size // 4
    
    # Bomb body
    pygame.draw.circle(surface, BLACK, (cx, cy + 4), bomb_r)
    pygame.draw.circle(surface, (40, 40, 40), (cx, cy + 4), bomb_r - 2)
    
    # Highlight
    pygame.draw.circle(surface, (80, 80, 80), (cx - bomb_r // 3, cy - bomb_r // 4 + 4), bomb_r // 4)
    
    # Fuse
    fuse_points = [
        (cx, cy + 4 - bomb_r),
        (cx + 4, cy - bomb_r - 4),
        (cx + 8, cy - bomb_r - 2),
        (cx + 10, cy - bomb_r - 8),
    ]
    if len(fuse_points) > 1:
        pygame.draw.lines(surface, (139, 90, 43), False, fuse_points, 2)
    
    # Spark at fuse tip (animated flicker)
    tick = pygame.time.get_ticks()
    if tick % 300 < 150:
        spark_color = YELLOW
    else:
        spark_color = ORANGE
    pygame.draw.circle(surface, spark_color, (cx + 10, cy - bomb_r - 8), 3)
    pygame.draw.circle(surface, RED, (cx + 10, cy - bomb_r - 8), 2)


# ============================================================================
# ASSET LOADING
# ============================================================================
def load_assets():
    assets = {
        'images': {},
        'backgrounds': [],
        'sounds': {
            'hurt': None,
            'click': None,
            'correct': None,
            'munch': None,
            'victory': None
        },
        'music': None
    }
    base_path = Path(__file__).parent
    
    # Load sounds
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
            elif sound_name in ['victory', 'correct']: assets['sounds'][sound_name].set_volume(1.0)
            else: assets['sounds'][sound_name].set_volume(0.7)
        except: pass
    
    # Load music
    try:
        music_path = base_path / 'assets' / 'sounds' / 'background.wav'
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.4)
        assets['music'] = True
    except: pass
    
    # Load player and enemy images
    for img_name in ['player', 'enemy']:
        try:
            path = base_path / 'assets' / 'images' / f'{img_name}.png'
            img = pygame.image.load(path).convert_alpha()
            assets['images'][img_name] = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
        except:
            color = BLUE if img_name == 'player' else RED
            surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            surf.fill(color)
            assets['images'][img_name] = surf
    
    # Load backgrounds for stage progression
    bg_candidates = [
        ['background.png'],
        ['background2.jpg', 'background2.png'],
        ['background3.jpg', 'background3.png'],
    ]
    
    for level_idx, filenames in enumerate(bg_candidates):
        loaded = False
        for fname in filenames:
            for search_dir in [base_path / 'assets' / 'images', base_path]:
                try:
                    path = search_dir / fname
                    if path.exists():
                        img = pygame.image.load(str(path)).convert()
                        img = pygame.transform.scale(img, (WIDTH, HEIGHT))
                        assets['backgrounds'].append(img)
                        print(f"Background stage {level_idx} ({STAGES[level_idx]['name']}) loaded: {path}")
                        loaded = True
                        break
                except Exception as e:
                    print(f"Couldn't load {fname} from {search_dir}: {e}")
            if loaded:
                break
        if not loaded:
            fallback = pygame.Surface((WIDTH, HEIGHT))
            fallback.fill(GRAY)
            assets['backgrounds'].append(fallback)
            print(f"Using fallback background for stage {level_idx}")
    
    assets['images']['background'] = assets['backgrounds'][0] if assets['backgrounds'] else pygame.Surface((WIDTH, HEIGHT))
    
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
feedback_text = None
feedback_time = 0
last_enemy_move = 0
current_stage = 0
level_up_timer = 0
hit_shake_timer = 0       # Screen shake on enemy hit
player_flash_timer = 0    # Player flashes when hit


# ============================================================================
# GAME LOGIC
# ============================================================================
def generate_problem():
    stage = get_stage_for_score(score)
    operations = STAGES[stage]['operations']
    op = random.choice(operations)
    
    if op == 'addition':
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        return f"{a} + {b} = ?", a + b
    elif op == 'subtraction':
        a = random.randint(1, 20)
        b = random.randint(1, a)
        return f"{a} - {b} = ?", a - b
    elif op == 'multiplication':
        a = random.randint(2, 12)
        b = random.randint(2, 12)
        return f"{a} × {b} = ?", a * b
    elif op == 'division':
        b = random.randint(2, 12)
        answer = random.randint(2, 12)
        a = b * answer
        return f"{a} ÷ {b} = ?", answer

def generate_grid():
    global grid_values, current_problem, correct_answer, bomb_positions
    grid_values = []
    bomb_positions = []
    current_problem, correct_answer = generate_problem()
    
    # Positions not available for correct answer or bombs
    occupied = set()
    occupied.add((player_pos[1], player_pos[0]))
    occupied.add((enemy_pos[1], enemy_pos[0]))
    
    # Pick correct answer position
    empty_positions = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)
                      if (r, c) not in occupied]
    correct_row, correct_col = random.choice(empty_positions)
    occupied.add((correct_row, correct_col))
    
    # Place bombs based on stage
    stage = get_stage_for_score(score)
    num_bombs = STAGES[stage]['bomb_count']
    available_for_bombs = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)
                           if (r, c) not in occupied]
    random.shuffle(available_for_bombs)
    for i in range(min(num_bombs, len(available_for_bombs))):
        bomb_positions.append(available_for_bombs[i])
        occupied.add(available_for_bombs[i])
    
    # Fill grid values
    for i in range(GRID_SIZE * GRID_SIZE):
        if i == correct_row * GRID_SIZE + correct_col:
            grid_values.append(correct_answer)
        else:
            wrong = correct_answer + random.randint(-5, 5)
            while wrong == correct_answer or wrong <= 0:
                wrong = correct_answer + random.randint(-5, 5)
            grid_values.append(wrong)

def move_enemy():
    global enemy_pos, lives, last_enemy_move, player_pos
    possible_moves = []
    if enemy_pos[0] < player_pos[0]: possible_moves.append((1, 0))
    elif enemy_pos[0] > player_pos[0]: possible_moves.append((-1, 0))
    if enemy_pos[1] < player_pos[1]: possible_moves.append((0, 1))
    elif enemy_pos[1] > player_pos[1]: possible_moves.append((0, -1))
    
    if possible_moves:
        dx, dy = random.choice(possible_moves)
        new_x, new_y = enemy_pos[0] + dx, enemy_pos[1] + dy
        if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
            enemy_pos = [new_x, new_y]
    
    if enemy_pos == player_pos:
        global hit_shake_timer, player_flash_timer
        lives -= 1
        hit_shake_timer = 30        # Shake screen for 0.5 sec
        player_flash_timer = 60     # Flash player for 1 sec
        show_feedback("OUCH! -1 Life", RED)
        if assets['sounds']['hurt']: assets['sounds']['hurt'].play()
        # Spawn impact particles at collision point
        px = GRID_OFFSET_X + player_pos[0] * CELL_SIZE + CELL_SIZE // 2
        py = GRID_OFFSET_Y + player_pos[1] * CELL_SIZE + CELL_SIZE // 2
        spawn_explosion(px, py, 20)
        player_pos = [GRID_SIZE // 2, GRID_SIZE // 2]
        if lives <= 0: trigger_game_over()

def show_feedback(message, color):
    global feedback_text, feedback_time
    feedback_text = (message, color)
    feedback_time = pygame.time.get_ticks() + 1000

def trigger_game_over():
    """Start the skull animation instead of immediately ending"""
    global game_over_animating, game_over_anim_timer, screen_shake_amount
    game_over_animating = True
    game_over_anim_timer = GAME_OVER_ANIM_DURATION
    screen_shake_amount = 0
    pygame.mixer.music.stop()

def end_game():
    global game_active
    game_active = False
    if assets['sounds']['victory']: assets['sounds']['victory'].play()

def start_game():
    global player_pos, enemy_pos, score, lives, game_active, last_enemy_move
    global current_stage, level_up_timer, game_over_animating, game_over_anim_timer
    global bomb_hit_timer, particles, hit_shake_timer, player_flash_timer, feedback_text
    player_pos = [GRID_SIZE // 2, GRID_SIZE // 2]
    enemy_pos = [0, 0]
    score = 0
    lives = 3
    game_active = True
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
    if assets['backgrounds'] and current_stage < len(assets['backgrounds']):
        return assets['backgrounds'][current_stage]
    return assets['images']['background']

def check_bomb_hit():
    """Check if player stepped on a bomb"""
    global lives, bomb_hit_timer
    player_grid = (player_pos[1], player_pos[0])  # (row, col)
    if player_grid in bomb_positions:
        bomb_positions.remove(player_grid)
        lives -= 1
        bomb_hit_timer = 60  # Show "BOOM!" for 1 second
        
        # Explosion particles at bomb location
        bx = GRID_OFFSET_X + player_pos[0] * CELL_SIZE + CELL_SIZE // 2
        by = GRID_OFFSET_Y + player_pos[1] * CELL_SIZE + CELL_SIZE // 2
        spawn_explosion(bx, by, 40)
        
        show_feedback("BOOM! -1 Life", ORANGE)
        if assets['sounds']['hurt']: assets['sounds']['hurt'].play()
        
        if lives <= 0:
            trigger_game_over()
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
            if is_bomb:
                # Bomb cell has a reddish tint
                cell.fill((255, 200, 200, 140))
            else:
                cell.fill(WHITE)
            screen.blit(cell, (x, y))
            
            # Border
            border_color = DARK_RED if is_bomb else BLACK
            pygame.draw.rect(screen, border_color, (x, y, CELL_SIZE, CELL_SIZE), 2)
            
            if is_bomb:
                # Draw bomb icon
                draw_bomb(screen, x, y, CELL_SIZE)
            else:
                # Draw number
                value = grid_values[row * GRID_SIZE + col]
                color = GREEN if value == correct_answer else BLACK
                num_text = font.render(str(value), True, color)
                screen.blit(num_text, (x + CELL_SIZE//2 - num_text.get_width()//2, 
                                 y + CELL_SIZE//2 - num_text.get_height()//2))

def draw_entities():
    global player_flash_timer
    player_x = GRID_OFFSET_X + player_pos[0] * CELL_SIZE
    player_y = GRID_OFFSET_Y + player_pos[1] * CELL_SIZE
    enemy_x = GRID_OFFSET_X + enemy_pos[0] * CELL_SIZE
    enemy_y = GRID_OFFSET_Y + enemy_pos[1] * CELL_SIZE
    
    # Player: flash and bounce when recently hit
    if player_flash_timer > 0:
        player_flash_timer -= 1
        # Bounce offset (bounces up and down rapidly)
        bounce = int(math.sin(player_flash_timer * 0.8) * 6)
        player_y += bounce
        # Flash: blink every few frames (skip drawing on odd cycles)
        if (player_flash_timer // 4) % 2 == 0:
            screen.blit(assets['images']['player'], (player_x, player_y))
            # Red damage tint overlay
            tint = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            tint.fill((255, 0, 0, 80))
            screen.blit(tint, (player_x, player_y))
    else:
        screen.blit(assets['images']['player'], (player_x, player_y))
    
    screen.blit(assets['images']['enemy'], (enemy_x, enemy_y))

def draw_ui():
    screen.blit(small_font.render(f"Score: {score}", True, BLACK), (20, 20))
    screen.blit(small_font.render(f"Lives: {lives}", True, BLACK), (20, 50))
    screen.blit(font.render(current_problem, True, BLACK), 
               (WIDTH//2 - font.size(current_problem)[0]//2, 20))
    
    # Controls hint
    hint = small_font.render("Move to the correct answer to munch it!", True, BLACK)
    screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 80))
    
    # Stage indicator
    if current_stage < len(STAGES):
        stage_label = small_font.render(f"Stage: {STAGES[current_stage]['name']}", True, WHITE)
        stage_shadow = small_font.render(f"Stage: {STAGES[current_stage]['name']}", True, BLACK)
        screen.blit(stage_shadow, (WIDTH - stage_label.get_width() - 9, HEIGHT - 29))
        screen.blit(stage_label, (WIDTH - stage_label.get_width() - 10, HEIGHT - 30))
    
    if feedback_text and pygame.time.get_ticks() < feedback_time:
        msg, color = feedback_text
        feedback = font.render(msg, True, color)
        screen.blit(feedback, (WIDTH//2 - feedback.get_width()//2, HEIGHT - 50))

def draw_bomb_hit():
    """Draw the BOOM! text when a bomb is hit"""
    global bomb_hit_timer
    if bomb_hit_timer <= 0:
        return
    bomb_hit_timer -= 1
    
    scale = 1.0 + (60 - bomb_hit_timer) * 0.02
    size = int(64 * scale)
    boom_f = pygame.font.SysFont('Arial', size, bold=True)
    
    boom_text = boom_f.render("BOOM!", True, ORANGE)
    boom_shadow = boom_f.render("BOOM!", True, DARK_RED)
    rect = boom_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(boom_shadow, (rect.x + 3, rect.y + 3))
    screen.blit(boom_text, rect)

def draw_level_up():
    global level_up_timer
    if level_up_timer <= 0:
        return
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
        stage_rect = stage_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 25))
        screen.blit(stage_text, stage_rect)

def draw_game_over_animation():
    """Draw the skull zoom + screen shake animation"""
    global game_over_anim_timer, game_over_animating, screen_shake_amount
    
    if not game_over_animating:
        return False
    
    game_over_anim_timer -= 1
    progress = 1.0 - (game_over_anim_timer / GAME_OVER_ANIM_DURATION)
    
    # Phase 1 (0-60%): Skull zooms in from tiny to large
    # Phase 2 (60-80%): Screen shake intensifies
    # Phase 3 (80-100%): Fade to game over screen
    
    # Dark overlay gets stronger
    overlay_alpha = min(220, int(progress * 280))
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, overlay_alpha))
    screen.blit(overlay, (0, 0))
    
    # Screen shake
    if progress > 0.3:
        shake_intensity = min(15, int((progress - 0.3) * 30))
        screen_shake_amount = shake_intensity
    
    # Skull zoom
    if progress < 0.85:
        # Skull grows from small to large
        skull_size = int(20 + progress * 250)
        
        # Red flash behind skull
        if progress > 0.2:
            flash_alpha = min(80, int((progress - 0.2) * 120))
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 0, 0, flash_alpha))
            screen.blit(flash, (0, 0))
        
        draw_skull(screen, WIDTH // 2, HEIGHT // 2, skull_size)
    else:
        # Final phase: show "GAME OVER" text
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

def draw_menu():
    screen.blit(assets['images']['background'], (0, 0))
    screen.blit(title_font.render("NumCrunch Academy", True, BLUE), 
               (WIDTH//2 - title_font.size("NumCrunch Academy")[0]//2, HEIGHT//3))
    screen.blit(font.render("Solve math problems to score points", True, BLACK),
               (WIDTH//2 - font.size("Solve math problems to score points")[0]//2, HEIGHT//2))
    screen.blit(font.render("Press any key to Start", True, GREEN),
               (WIDTH//2 - font.size("Press any key to Start")[0]//2, HEIGHT*2//3))

def draw_game_over():
    screen.blit(get_current_background(), (0, 0))
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    # Draw a smaller skull above the text
    draw_skull(screen, WIDTH // 2, HEIGHT // 3 - 20, 100)
    
    screen.blit(font.render(f"Final Score: {score}", True, WHITE),
               (WIDTH//2 - font.size(f"Final Score: {score}")[0]//2, HEIGHT//2))
    screen.blit(font.render("Press any key to Play Again", True, GREEN),
               (WIDTH//2 - font.size("Press any key to Play Again")[0]//2, HEIGHT*2//3))


# ============================================================================
# MAIN GAME LOOP
# ============================================================================
running = True
render_surface = pygame.Surface((WIDTH, HEIGHT))

while running:
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            # Don't accept input during game over animation
            if game_over_animating:
                continue
            
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
                
                # Check bomb first
                if not check_bomb_hit():
                    # Auto-eat: if you land on the correct answer, munch it
                    selected_index = player_pos[1] * GRID_SIZE + player_pos[0]
                    if grid_values[selected_index] == correct_answer:
                        old_stage = get_stage_for_score(score)
                        score += 10
                        new_stage = get_stage_for_score(score)
                        
                        if new_stage > old_stage and new_stage < len(STAGES):
                            current_stage = new_stage
                            level_up_timer = 180
                            lives += 1
                            spawn_confetti(WIDTH // 2, HEIGHT // 3, 100)
                            print(f"Stage up! {STAGES[new_stage]['name']} | +1 life ({lives}) | Enemy speed: {STAGES[new_stage]['enemy_speed']}ms")
                        
                        feedback_text = ("Correct! +10", GREEN)
                        # Play munch sound (the crunch)
                        if assets['sounds']['munch']: assets['sounds']['munch'].play()
                        generate_grid()
                    # Wrong answer: nothing happens, just move through
                
                feedback_time = current_time + 1000

    # Enemy movement (not during game over animation)
    if game_active and not game_over_animating and current_time - last_enemy_move > get_enemy_speed():
        move_enemy()
        last_enemy_move = current_time

    # ========================================================================
    # RENDERING
    # ========================================================================
    screen.blit(get_current_background(), (0, 0))
    
    if game_active or game_over_animating:
        draw_grid()
        draw_entities()
        draw_ui()
        draw_bomb_hit()
        update_and_draw_particles(screen)
        draw_level_up()
        
        # Draw game over animation on top of everything
        if game_over_animating:
            draw_game_over_animation()
    else:
        if lives <= 0:
            draw_game_over()
        else:
            draw_menu()
        update_and_draw_particles(screen)
    
    # Tick down hit shake timer
    if hit_shake_timer > 0:
        hit_shake_timer -= 1
    
    # Apply screen shake (from enemy hit or game over animation)
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
sys.exit()
