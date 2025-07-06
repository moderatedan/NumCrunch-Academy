import pygame
import random
import sys
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
ENEMY_SPEED = 1500

# Colors
WHITE = (255, 255, 255, 128)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NumCrunch Academy")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont('Arial', 32)
small_font = pygame.font.SysFont('Arial', 24)
title_font = pygame.font.SysFont('Arial', 48)

def load_assets():
    assets = {
        'images': {},
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
    
    # Load images
    for img_name in ['player', 'enemy', 'background']:
        try:
            path = base_path / 'assets' / 'images' / f'{img_name}.png'
            img = pygame.image.load(path).convert_alpha()
            assets['images'][img_name] = pygame.transform.scale(
                img, (WIDTH, HEIGHT) if img_name == 'background' else (CELL_SIZE, CELL_SIZE))
        except:
            if img_name == 'player': color = BLUE
            elif img_name == 'enemy': color = RED
            else: color = GRAY
            size = (WIDTH, HEIGHT) if img_name == 'background' else (CELL_SIZE, CELL_SIZE)
            surf = pygame.Surface(size, pygame.SRCALPHA)
            surf.fill(color)
            assets['images'][img_name] = surf
    
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
feedback_text = ""
feedback_time = 0
last_enemy_move = 0

def generate_problem():
    b = random.randint(2, 12)
    answer = random.randint(2, 12)
    return f"{b * answer} ÷ {b} = ?", answer

def generate_grid():
    global grid_values, current_problem, correct_answer
    grid_values = []
    current_problem, correct_answer = generate_problem()
    empty_positions = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)
                      if not (r == player_pos[1] and c == player_pos[0])
                      and not (r == enemy_pos[1] and c == enemy_pos[0])]
    
    correct_row, correct_col = random.choice(empty_positions)
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
        lives -= 1
        show_feedback("OUCH! -1 Life", RED)
        if assets['sounds']['hurt']: assets['sounds']['hurt'].play()
        player_pos = [GRID_SIZE // 2, GRID_SIZE // 2]
        if lives <= 0: end_game()

def show_feedback(message, color):
    global feedback_text, feedback_time
    feedback_text = (message, color)
    feedback_time = pygame.time.get_ticks() + 1000

def end_game():
    global game_active
    game_active = False
    pygame.mixer.music.stop()
    if assets['sounds']['victory']: assets['sounds']['victory'].play()

def start_game():
    global player_pos, enemy_pos, score, lives, game_active, last_enemy_move
    player_pos = [GRID_SIZE // 2, GRID_SIZE // 2]
    enemy_pos = [0, 0]
    score = 0
    lives = 3
    game_active = True
    last_enemy_move = pygame.time.get_ticks()
    generate_grid()
    if assets['music']: pygame.mixer.music.play(-1)

def draw_grid():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = GRID_OFFSET_X + col * CELL_SIZE
            y = GRID_OFFSET_Y + row * CELL_SIZE
            cell = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            cell.fill(WHITE)
            screen.blit(cell, (x, y))
            pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 2)
            value = grid_values[row * GRID_SIZE + col]
            color = GREEN if value == correct_answer else BLACK
            num_text = font.render(str(value), True, color)
            screen.blit(num_text, (x + CELL_SIZE//2 - num_text.get_width()//2, 
                             y + CELL_SIZE//2 - num_text.get_height()//2))

def draw_entities():
    player_x = GRID_OFFSET_X + player_pos[0] * CELL_SIZE
    player_y = GRID_OFFSET_Y + player_pos[1] * CELL_SIZE
    enemy_x = GRID_OFFSET_X + enemy_pos[0] * CELL_SIZE
    enemy_y = GRID_OFFSET_Y + enemy_pos[1] * CELL_SIZE
    screen.blit(assets['images']['player'], (player_x, player_y))
    screen.blit(assets['images']['enemy'], (enemy_x, enemy_y))

def draw_ui():
    screen.blit(small_font.render(f"Score: {score}", True, BLACK), (20, 20))
    screen.blit(small_font.render(f"Lives: {lives}", True, BLACK), (20, 50))
    screen.blit(font.render(current_problem, True, BLACK), 
               (WIDTH//2 - font.size(current_problem)[0]//2, 20))
    if pygame.time.get_ticks() < feedback_time:
        msg, color = feedback_text
        feedback = font.render(msg, True, color)
        screen.blit(feedback, (WIDTH//2 - feedback.get_width()//2, HEIGHT - 50))

def draw_menu():
    screen.blit(assets['images']['background'], (0, 0))
    screen.blit(title_font.render("NumCrunch Academy", True, BLUE), 
               (WIDTH//2 - title_font.size("NumCrunch Academy")[0]//2, HEIGHT//3))
    screen.blit(font.render("Solve math problems to score points", True, BLACK),
               (WIDTH//2 - font.size("Solve math problems to score points")[0]//2, HEIGHT//2))
    screen.blit(font.render("Press any key to Start", True, GREEN),
               (WIDTH//2 - font.size("Press any key to Start")[0]//2, HEIGHT*2//3))

def draw_game_over():
    screen.blit(assets['images']['background'], (0, 0))
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    screen.blit(title_font.render("Game Over!", True, RED),
               (WIDTH//2 - title_font.size("Game Over!")[0]//2, HEIGHT//3))
    screen.blit(font.render(f"Final Score: {score}", True, WHITE),
               (WIDTH//2 - font.size(f"Final Score: {score}")[0]//2, HEIGHT//2))
    screen.blit(font.render("Press any key to Play Again", True, GREEN),
               (WIDTH//2 - font.size("Press any key to Play Again")[0]//2, HEIGHT*2//3))

# Main game loop
running = True
while running:
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
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
                
                selected_index = player_pos[1] * GRID_SIZE + player_pos[0]
                if grid_values[selected_index] == correct_answer:
                    score += 10
                    feedback_text = ("Correct! +10", GREEN)
                    if assets['sounds']['correct']: assets['sounds']['correct'].play()
                    generate_grid()
                else:
                    score = max(0, score - 5)
                    feedback_text = ("Wrong! -5", RED)
                    if assets['sounds']['munch']: assets['sounds']['munch'].play()
                
                feedback_time = current_time + 1000

    if game_active and current_time - last_enemy_move > ENEMY_SPEED:
        move_enemy()
        last_enemy_move = current_time

    screen.blit(assets['images']['background'], (0, 0))
    if game_active:
        draw_grid()
        draw_entities()
        draw_ui()
    else:
        draw_game_over() if lives <= 0 else draw_menu()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()