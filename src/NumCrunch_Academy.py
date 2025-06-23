import pygame
import random
import sys
import os

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 5
CELL_SIZE = 80
GRID_OFFSET_X = (WIDTH - GRID_SIZE * CELL_SIZE) // 2
GRID_OFFSET_Y = (HEIGHT - GRID_SIZE * CELL_SIZE) // 2

# Colors
WHITE = (255, 255, 255, 200)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NumCrunch Academy")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 32)
small_font = pygame.font.SysFont('Arial', 24)

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Asset paths - now using relative paths
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")

# Create directories if they don't exist
os.makedirs(SPRITES_DIR, exist_ok=True)
os.makedirs(SOUNDS_DIR, exist_ok=True)

print(f"Looking for assets in: {ASSETS_DIR}")

# Sound setup - IMPROVED VERSION
sound_enabled = False
crunch_sound = None
victory_sound = None

try:
    pygame.mixer.init()
    pygame.mixer.set_num_channels(8)  # Increase audio channels
    
    # Try loading crunch sound (multiple possible names)
    for sound_file in ["crunch.wav", "munch.wav", "bite.wav"]:
        sound_path = os.path.join(SOUNDS_DIR, sound_file)
        if os.path.exists(sound_path):
            try:
                crunch_sound = pygame.mixer.Sound(sound_path)
                crunch_sound.set_volume(0.7)  # Set appropriate volume
                print(f"Loaded crunch sound from: {sound_path}")
                break
            except Exception as e:
                print(f"Couldn't load {sound_file}: {e}")

    # Try loading victory sound (multiple possible names and formats)
    for sound_file in ["victory.flac", "success.wav", "win.flac", "celebration.wav"]:
        sound_path = os.path.join(SOUNDS_DIR, sound_file)
        if os.path.exists(sound_path):
            try:
                victory_sound = pygame.mixer.Sound(sound_path)
                victory_sound.set_volume(0.7)
                print(f"Loaded victory sound from: {sound_path}")
                break
            except Exception as e:
                print(f"Couldn't load {sound_file}: {e}")

    # Load background music
    for music_file in ["background.wav", "background_music.wav", "music.mp3"]:
        music_path = os.path.join(SOUNDS_DIR, music_file)
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.4)
                sound_enabled = True
                print(f"Loaded background music from: {music_path}")
                break
            except Exception as e:
                print(f"Couldn't load {music_file}: {e}")

except Exception as e:
    print(f"Sound initialization failed: {e}")
    sound_enabled = False

# Load background
background = None
background_files = ["background.png", "classroom.png"]
for bg_file in background_files:
    try:
        bg_path = os.path.join(SPRITES_DIR, bg_file)
        if os.path.exists(bg_path):
            background = pygame.image.load(bg_path)
            background = pygame.transform.scale(background, (WIDTH, HEIGHT))
            print(f"Background loaded from: {bg_path}")
            break
    except Exception as e:
        print(f"Couldn't load background: {e}")

# Load player sprite
player_sprite = None
player_files = ["player.png", "cruncher.png"]
for player_file in player_files:
    try:
        player_path = os.path.join(SPRITES_DIR, player_file)
        if os.path.exists(player_path):
            player_sprite = pygame.image.load(player_path)
            player_sprite = pygame.transform.scale(player_sprite, (CELL_SIZE, CELL_SIZE))
            print(f"Player sprite loaded from: {player_path}")
            break
    except Exception as e:
        print(f"Couldn't load player sprite: {e}")

# Load enemy sprite
enemy_sprite = None
enemy_files = ["enemy.png", "troublemaker.png"]
for enemy_file in enemy_files:
    try:
        enemy_path = os.path.join(SPRITES_DIR, enemy_file)
        if os.path.exists(enemy_path):
            enemy_sprite = pygame.image.load(enemy_path)
            enemy_sprite = pygame.transform.scale(enemy_sprite, (CELL_SIZE, CELL_SIZE))
            print(f"Enemy sprite loaded from: {enemy_path}")
            break
    except Exception as e:
        print(f"Couldn't load enemy sprite: {e}")

# Game variables
player_pos = [2, 2]  # Start in the center
score = 0
lives = 3
current_problem = ""
correct_answer = 0
grid_values = []
game_state = "playing"  # "playing", "game_over"
troggle_pos = [random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)]  # Enemy position

def generate_problem():
    """Generate a random math problem and its correct answer"""
    problem_types = ["addition", "subtraction", "multiplication", "division"]
    problem_type = random.choice(problem_types)
    
    if problem_type == "addition":
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        return f"{a} + {b}", a + b
    elif problem_type == "subtraction":
        a = random.randint(1, 20)
        b = random.randint(1, a)  # Ensure no negative answers
        return f"{a} - {b}", a - b
    elif problem_type == "multiplication":
        a = random.randint(1, 12)
        b = random.randint(1, 12)
        return f"{a} × {b}", a * b
    elif problem_type == "division":
        b = random.randint(1, 12)
        answer = random.randint(1, 12)
        a = b * answer
        return f"{a} ÷ {b}", answer

def generate_grid():
    """Generate a grid with correct answer placed near the player"""
    global grid_values, correct_answer, current_problem
    
    current_problem, correct_answer = generate_problem()
    grid_values = []
    
    # Calculate distances from player position
    distances = []
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            distance = abs(col - player_pos[0]) + abs(row - player_pos[1])  # Manhattan distance
            distances.append((distance, row, col))
    
    # Sort positions by distance (closest first)
    distances.sort()
    
    # Select one of the 3 closest positions for correct answer
    closest_positions = distances[:3]
    chosen_distance, correct_row, correct_col = random.choice(closest_positions)
    correct_pos = correct_row * GRID_SIZE + correct_col
    
    # Fill the grid
    for i in range(GRID_SIZE * GRID_SIZE):
        if i == correct_pos:
            grid_values.append(correct_answer)
        else:
            # Generate wrong answers that are somewhat close to the correct one
            offset = random.randint(-3, 3)
            while offset == 0:  # Ensure wrong answers are actually wrong
                offset = random.randint(-3, 3)
            wrong_answer = correct_answer + offset
            grid_values.append(wrong_answer)

def draw_grid():
    """Draw the game grid with numbers"""
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = GRID_OFFSET_X + col * CELL_SIZE
            y = GRID_OFFSET_Y + row * CELL_SIZE
            
            # Draw semi-transparent cell background
            cell_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            cell_surface.fill(WHITE)
            screen.blit(cell_surface, (x, y))
            pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 2)
            
            # Draw cell value
            index = row * GRID_SIZE + col
            value = grid_values[index]
            text = font.render(str(value), True, BLACK)
            text_rect = text.get_rect(center=(x + CELL_SIZE//2, y + CELL_SIZE//2))
            screen.blit(text, text_rect)

def draw_player():
    """Draw the player character using custom sprite or default"""
    x = GRID_OFFSET_X + player_pos[0] * CELL_SIZE
    y = GRID_OFFSET_Y + player_pos[1] * CELL_SIZE
    
    if player_sprite:
        sprite_rect = player_sprite.get_rect(center=(x + CELL_SIZE//2, y + CELL_SIZE//2))
        screen.blit(player_sprite, sprite_rect)
    else:
        # Fallback: Draw the original green circle
        pygame.draw.circle(screen, GREEN, (x + CELL_SIZE//2, y + CELL_SIZE//2), CELL_SIZE//3)
        # Eyes
        eye_size = CELL_SIZE//10
        pygame.draw.circle(screen, WHITE, (x + CELL_SIZE//2 - 10, y + CELL_SIZE//2 - 5), eye_size)
        pygame.draw.circle(screen, WHITE, (x + CELL_SIZE//2 + 10, y + CELL_SIZE//2 - 5), eye_size)
        pygame.draw.circle(screen, BLACK, (x + CELL_SIZE//2 - 10, y + CELL_SIZE//2 - 5), eye_size//2)
        pygame.draw.circle(screen, BLACK, (x + CELL_SIZE//2 + 10, y + CELL_SIZE//2 - 5), eye_size//2)

def draw_troggle():
    """Draw the enemy using custom sprite or default"""
    x = GRID_OFFSET_X + troggle_pos[0] * CELL_SIZE
    y = GRID_OFFSET_Y + troggle_pos[1] * CELL_SIZE
    
    if enemy_sprite:
        sprite_rect = enemy_sprite.get_rect(center=(x + CELL_SIZE//2, y + CELL_SIZE//2))
        screen.blit(enemy_sprite, sprite_rect)
    else:
        # Fallback: Draw a red circle
        pygame.draw.circle(screen, RED, (x + CELL_SIZE//2, y + CELL_SIZE//2), CELL_SIZE//3)

def draw_hud():
    """Draw the score, lives, and current problem"""
    # Create semi-transparent background for HUD
    hud_bg = pygame.Surface((WIDTH, 80), pygame.SRCALPHA)
    hud_bg.fill((200, 200, 200, 150))
    screen.blit(hud_bg, (0, 0))
    
    # Score
    score_text = small_font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (20, 20))
    
    # Lives
    lives_text = small_font.render(f"Lives: {lives}", True, BLACK)
    screen.blit(lives_text, (20, 50))
    
    # Current problem
    problem_text = font.render(f"Find: {current_problem} = ?", True, BLUE)
    problem_rect = problem_text.get_rect(center=(WIDTH//2, 50))
    screen.blit(problem_text, problem_rect)

def draw_game_over():
    """Draw the game over screen"""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    game_over_text = font.render("GAME OVER", True, RED)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    restart_text = small_font.render("Press R to restart", True, WHITE)
    
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))

def check_answer():
    """Check if the player is on the correct answer"""
    global score, lives
    
    index = player_pos[1] * GRID_SIZE + player_pos[0]
    if grid_values[index] == correct_answer:
        score += 10
        
        # Play crunch sound if available - UPDATED
        if sound_enabled and crunch_sound:
            try:
                crunch_sound.play()
            except Exception as e:
                print(f"Couldn't play crunch sound: {e}")
        
        generate_grid()
        
        # Play victory sound every 50 points if available - UPDATED
        if score % 50 == 0 and sound_enabled and victory_sound:
            try:
                victory_sound.play()
            except Exception as e:
                print(f"Couldn't play victory sound: {e}")
    else:
        lives -= 1
        if lives <= 0:
            global game_state
            game_state = "game_over"

def move_troggle():
    """Move the enemy randomly"""
    if random.random() < 0.02:  # 2% chance per frame to move
        direction = random.choice(["left", "right", "up", "down"])
        if direction == "left" and troggle_pos[0] > 0:
            troggle_pos[0] -= 1
        elif direction == "right" and troggle_pos[0] < GRID_SIZE-1:
            troggle_pos[0] += 1
        elif direction == "up" and troggle_pos[1] > 0:
            troggle_pos[1] -= 1
        elif direction == "down" and troggle_pos[1] < GRID_SIZE-1:
            troggle_pos[1] += 1

def check_troggle_collision():
    """Check if player collides with enemy"""
    global lives, game_state
    
    if player_pos == troggle_pos and game_state == "playing":
        lives -= 1
        if lives <= 0:
            game_state = "game_over"
        else:
            # Respawn troggle away from player
            troggle_pos[0] = random.randint(0, GRID_SIZE-1)
            troggle_pos[1] = random.randint(0, GRID_SIZE-1)
            while troggle_pos == player_pos:
                troggle_pos[0] = random.randint(0, GRID_SIZE-1)
                troggle_pos[1] = random.randint(0, GRID_SIZE-1)

# Initialize the game
generate_grid()

# Start background music
if sound_enabled:
    pygame.mixer.music.play(-1)

# Main game loop
running = True
while running:
    # Draw background first
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(GRAY)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if game_state == "playing":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and player_pos[0] > 0:
                    player_pos[0] -= 1
                    check_answer()
                    check_troggle_collision()
                elif event.key == pygame.K_RIGHT and player_pos[0] < GRID_SIZE - 1:
                    player_pos[0] += 1
                    check_answer()
                    check_troggle_collision()
                elif event.key == pygame.K_UP and player_pos[1] > 0:
                    player_pos[1] -= 1
                    check_answer()
                    check_troggle_collision()
                elif event.key == pygame.K_DOWN and player_pos[1] < GRID_SIZE - 1:
                    player_pos[1] += 1
                    check_answer()
                    check_troggle_collision()
                elif event.key == pygame.K_m:  # M key toggles music
                    if sound_enabled:
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.pause()
                        else:
                            pygame.mixer.music.unpause()
        elif game_state == "game_over":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                # Reset the game
                player_pos = [2, 2]
                troggle_pos = [random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)]
                score = 0
                lives = 3
                game_state = "playing"
                generate_grid()
                if sound_enabled:
                    pygame.mixer.music.play(-1)
    
    # Game logic
    if game_state == "playing":
        move_troggle()
        check_troggle_collision()
    
    # Drawing
    draw_grid()
    draw_player()
    draw_troggle()
    draw_hud()
    
    if game_state == "game_over":
        draw_game_over()
    
    pygame.display.flip()
    clock.tick(60)

# Clean up
pygame.quit()
if sound_enabled:
    pygame.mixer.quit()
sys.exit()