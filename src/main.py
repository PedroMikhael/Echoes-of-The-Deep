import pygame
import sys
import math
import random
import primitives
from primitives import drawCircle
from characters.submarine import drawSubmarine, drawSubmarineFilled, get_bubble_spawn_position
from characters.jellyfish import create_jellyfish, update_jellyfish, draw_jellyfish_bioluminescent, check_jellyfish_collision
from characters.tentacles import create_giant_tentacles, update_giant_tentacles, draw_giant_tentacles
import menu

OCEAN_DEEP = (15, 40, 70)
SUBMARINE_BODY = (80, 90, 100)
SUBMARINE_DETAIL = (50, 55, 65)
SUBMARINE_FILL = (100, 110, 120)
BUBBLE_COLOR = (150, 200, 230)
TENTACLE_COLOR = (200, 80, 60)

WIDTH = 1920
HEIGHT = 1080   

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Echoes of the Deep")
clock = pygame.time.Clock()

title_font = pygame.font.Font(None, 64)
button_font = pygame.font.Font(None, 36)

menu.init_menu(WIDTH, HEIGHT)
menu.init_instructions(WIDTH, HEIGHT)
menu.init_credits(WIDTH, HEIGHT)

GAME_STATE_MENU = "menu"
GAME_STATE_PLAYING = "playing"
GAME_STATE_INSTRUCTIONS = "instructions"
GAME_STATE_CREDITS = "credits"

game_state = GAME_STATE_MENU
menu_time = 0

sub_x = WIDTH // 2
sub_y = HEIGHT // 2
sub_angle = 0
sub_speed = 3
rotation_speed = 4
propeller_angle = 0
propeller_speed = 15

bubbles = []
bubble_timer = 0

jellyfishes = []

def create_bubble(x, y):
    return {
        'x': x + random.randint(-10, 10),
        'y': y + random.randint(-10, 10),
        'radius': random.randint(2, 6),
        'speed_y': random.uniform(-1.5, -0.5),
        'speed_x': random.uniform(-0.3, 0.3),
        'life': random.randint(60, 120),
        'alpha': 255
    }

def update_bubble(b):
    b['y'] += b['speed_y']
    b['x'] += b['speed_x']
    b['speed_x'] += random.uniform(-0.05, 0.05)
    b['life'] -= 1
    b['alpha'] = max(0, int(255 * (b['life'] / 120)))
    return b['life'] > 0

def draw_bubble(surface, b):
    ratio = b['alpha'] / 255
    color = (
        int(BUBBLE_COLOR[0] * ratio),
        int(BUBBLE_COLOR[1] * ratio),
        int(BUBBLE_COLOR[2] * ratio)
    )
    drawCircle(surface, int(b['x']), int(b['y']), b['radius'], color)

while True:
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_state == GAME_STATE_MENU:
                action = menu.handle_menu_click(mouse_x, mouse_y)
                if action == "NOVO JOGO":
                    game_state = GAME_STATE_PLAYING
                    sub_x = WIDTH // 2
                    sub_y = HEIGHT // 2
                    sub_angle = 0
                    bubbles = []
                    jellyfishes = [
                        create_jellyfish(200, 200),
                        create_jellyfish(800, 300),
                        create_jellyfish(600, 500),
                    ]
                    giant_tentacles = create_giant_tentacles(WIDTH // 2, HEIGHT)
                elif action == "INSTRUCOES":
                    game_state = GAME_STATE_INSTRUCTIONS
                elif action == "CREDITOS":
                    game_state = GAME_STATE_CREDITS
                elif action == "SAIR":
                    pygame.quit()
                    sys.exit()
            
            elif game_state == GAME_STATE_INSTRUCTIONS:
                action = menu.handle_instructions_click(mouse_x, mouse_y)
                if action == "VOLTAR":
                    game_state = GAME_STATE_MENU
            
            elif game_state == GAME_STATE_CREDITS:
                action = menu.handle_credits_click(mouse_x, mouse_y)
                if action == "VOLTAR":
                    game_state = GAME_STATE_MENU
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == GAME_STATE_PLAYING:
                    game_state = GAME_STATE_MENU
                elif game_state in [GAME_STATE_INSTRUCTIONS, GAME_STATE_CREDITS]:
                    game_state = GAME_STATE_MENU

    if game_state == GAME_STATE_MENU:
        menu_time += 1
        menu.update_menu(menu_time, mouse_x, mouse_y)
        screen.fill(menu.ABYSS_BLACK)
        menu.draw_menu(screen, WIDTH, HEIGHT, title_font, button_font)
    
    elif game_state == GAME_STATE_INSTRUCTIONS:
        menu.update_instructions(mouse_x, mouse_y)
        screen.fill(menu.ABYSS_BLACK)
        menu.draw_instructions(screen, WIDTH, HEIGHT, title_font, button_font)
    
    elif game_state == GAME_STATE_CREDITS:
        menu.update_credits(mouse_x, mouse_y)
        screen.fill(menu.ABYSS_BLACK)
        menu.draw_credits(screen, WIDTH, HEIGHT, title_font, button_font)
    
    elif game_state == GAME_STATE_PLAYING:
        keys = pygame.key.get_pressed()
        is_moving = False
        
        if keys[pygame.K_LEFT]:
            sub_angle -= rotation_speed
        if keys[pygame.K_RIGHT]:
            sub_angle += rotation_speed
        
        if keys[pygame.K_UP]:
            rad = math.radians(sub_angle)
            sub_x += math.cos(rad) * sub_speed
            sub_y += math.sin(rad) * sub_speed
            is_moving = True
        
        if keys[pygame.K_DOWN]:
            rad = math.radians(sub_angle)
            sub_x -= math.cos(rad) * sub_speed
            sub_y -= math.sin(rad) * sub_speed
            is_moving = True
        
        sub_x = max(80, min(WIDTH - 80, sub_x))
        sub_y = max(80, min(HEIGHT - 80, sub_y))
        
        if is_moving:
            propeller_angle += propeller_speed
            bubble_timer += 1
            if bubble_timer >= 5:
                bubble_timer = 0
                spawn_x, spawn_y = get_bubble_spawn_position(sub_x, sub_y, sub_angle)
                bubbles.append(create_bubble(spawn_x, spawn_y))
        else:
            propeller_angle += propeller_speed * 0.2
        
        bubbles = [b for b in bubbles if update_bubble(b)]
        
        for jf in jellyfishes:
            update_jellyfish(jf, WIDTH, HEIGHT)
        
        update_giant_tentacles(giant_tentacles)
        
        screen.fill(OCEAN_DEEP)
        
        draw_giant_tentacles(screen, giant_tentacles, TENTACLE_COLOR)
        
        for b in bubbles:
            draw_bubble(screen, b)
        
        for jf in jellyfishes:
            draw_jellyfish_bioluminescent(screen, jf)
        
        drawSubmarineFilled(screen, int(sub_x), int(sub_y), sub_angle, SUBMARINE_BODY, SUBMARINE_DETAIL, SUBMARINE_FILL, propeller_angle)
    
    pygame.display.flip()
    clock.tick(60)
