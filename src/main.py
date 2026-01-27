import pygame
import sys
import math
import random
import primitives
from primitives import drawCircle

from characters.submarine import (
    drawSubmarineFilled,
    get_bubble_spawn_position,
    init_sonar,
    activate_sonar,
    update_sonar,
    draw_sonar,
    submarine_battery,
    update_battery,
    use_sonar_battery,
    draw_battery,
    draw_depth
)

from characters.jellyfish import (
    create_jellyfish,
    update_jellyfish,
    draw_jellyfish_bioluminescent
)

from characters.tentacles import (
    create_giant_tentacles,
    update_giant_tentacles,
    draw_giant_tentacles
)

from characters.water_bomb import (
    create_water_bomb,
    update_water_bomb,
    draw_water_bomb
)

import menu
import map
from map import (
    get_spawn_position,
    is_point_in_map,
    is_circle_in_map,
    is_jellyfish_in_map
)



# ---------------- CORES ----------------
OCEAN_DEEP = (15, 40, 70)
SUBMARINE_BODY = (80, 90, 100)
SUBMARINE_DETAIL = (50, 55, 65)
SUBMARINE_FILL = (100, 110, 120)
BUBBLE_COLOR = (150, 200, 230)
TENTACLE_COLOR = (200, 80, 60)
SONAR_COLOR = (0, 255, 200)
BOMB_BODY = (60, 65, 70)
BOMB_SPIKE = (40, 45, 50)
BOMB_HIGHLIGHT = (200, 220, 255)

# ---------------- TELA ----------------
WIDTH = 1280
HEIGHT = 720


# ---------------- MINI MAPA ----------------
MINIMAP_WIDTH = 220
MINIMAP_HEIGHT = 140
MINIMAP_MARGIN = 20

MINIMAP_X = WIDTH - MINIMAP_WIDTH - MINIMAP_MARGIN
MINIMAP_Y = MINIMAP_MARGIN

MINIMAP_SCALE_X = MINIMAP_WIDTH / WIDTH
MINIMAP_SCALE_Y = MINIMAP_HEIGHT / HEIGHT


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Echoes of the Deep")
clock = pygame.time.Clock()

# DEBUG FPS
SHOW_FPS = True

title_font = pygame.font.Font(None, 64)
button_font = pygame.font.Font(None, 36)

# ---------------- MENU ----------------
menu.init_menu(WIDTH, HEIGHT)
menu.init_instructions(WIDTH, HEIGHT)
menu.init_credits(WIDTH, HEIGHT)

GAME_STATE_MENU = "menu"
GAME_STATE_PLAYING = "playing"
GAME_STATE_INSTRUCTIONS = "instructions"
GAME_STATE_CREDITS = "credits"

game_state = GAME_STATE_MENU
menu_time = 0

# ---------------- SUBMARINO ----------------
sub_x = WIDTH // 2
sub_y = HEIGHT // 2
sub_angle = 0
sub_speed = 3
rotation_speed = 4
propeller_angle = 0
propeller_speed = 15
SUB_SCALE = 0.5  # Escala do submarino (0.5 = metade do tamanho)
SUB_COLLISION_RADIUS = 40 * SUB_SCALE


# ---------------- CÂMERA ----------------
camera_x = 0
camera_y = 0

# ---------------- PARTÍCULAS ----------------
bubbles = []
bubble_timer = 0
MAX_BUBBLES = 120

# ---------------- INIMIGOS ----------------
jellyfishes = []
water_bombs = []
giant_tentacles = None
sonar = None
battery = None

# ---------------- MAPA (CACHE) ----------------
MAP_WIDTH = 2000
MAP_HEIGHT = 1200
map_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
map_surface.fill((0, 0, 0))
map.drawMap(map_surface)

# ---------------- UTIL ----------------
def is_visible(x, y, margin=200):
    return -margin < x < WIDTH + margin and -margin < y < HEIGHT + margin

# ---------------- MINI MAPA ----------------
def world_to_minimap(x, y):
    mini_x = MINIMAP_X + x * MINIMAP_SCALE_X
    mini_y = MINIMAP_Y + y * MINIMAP_SCALE_Y
    return int(mini_x), int(mini_y)


# ---------------- BOLHAS ----------------
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

# ================= LOOP PRINCIPAL =================
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
                    sub_x, sub_y = get_spawn_position()
                    sub_angle = 0
                    bubbles.clear()

                    # Águas-vivas em pontos estratégicos (escala 0.3 - bem menores)
                    jellyfishes = [
                        # No corredor inclinado - bloqueiam passagem
                        create_jellyfish(450, 780, 0.3),
                        create_jellyfish(600, 700, 0.3),
                        # No corredor superior perto do magma
                        create_jellyfish(850, 250, 0.25),
                        create_jellyfish(1000, 250, 0.25),
                        # Na arena de inimigos
                        create_jellyfish(1100, 820, 0.3),
                        create_jellyfish(1250, 850, 0.3),
                    ]

                    # Bombas de água em pontos de passagem (escala 0.35)
                    water_bombs = [
                        # Corredor inclinado
                        create_water_bomb(550, 750, 0.35),
                        # Corredor superior
                        create_water_bomb(800, 250, 0.35),
                        create_water_bomb(950, 270, 0.35),
                        # No corredor final
                        create_water_bomb(1650, 850, 0.35),
                    ]

                    # Tentáculos na arena de inimigos (escala 0.35, posição ajustada)
                    giant_tentacles = create_giant_tentacles(1100, 900, 0.35)
                    sonar = init_sonar()
                    battery = submarine_battery()

                elif action == "INSTRUCOES":
                    game_state = GAME_STATE_INSTRUCTIONS
                elif action == "CREDITOS":
                    game_state = GAME_STATE_CREDITS
                elif action == "SAIR":
                    pygame.quit()
                    sys.exit()

            elif game_state in (GAME_STATE_INSTRUCTIONS, GAME_STATE_CREDITS):
                game_state = GAME_STATE_MENU

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_state = GAME_STATE_MENU
            if event.key == pygame.K_SPACE and game_state == GAME_STATE_PLAYING:
                if battery['charge'] >= 3:  # Só ativa se tiver bateria suficiente
                    activate_sonar(sonar)
                    use_sonar_battery(battery)

    # ================= ESTADOS =================
    if game_state == GAME_STATE_MENU:
        menu_time += 1
        menu.update_menu(menu_time, mouse_x, mouse_y)
        screen.fill(menu.ABYSS_BLACK)
        menu.draw_menu(screen, WIDTH, HEIGHT, title_font, button_font)

    elif game_state == GAME_STATE_INSTRUCTIONS:
        screen.fill(menu.ABYSS_BLACK)
        menu.draw_instructions(screen, WIDTH, HEIGHT, title_font, button_font)

    elif game_state == GAME_STATE_CREDITS:
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
            new_x = sub_x + math.cos(rad) * sub_speed
            new_y = sub_y + math.sin(rad) * sub_speed

            if is_circle_in_map(new_x, new_y, SUB_COLLISION_RADIUS):
                sub_x = new_x
                sub_y = new_y
                is_moving = True

        if keys[pygame.K_DOWN]:
            rad = math.radians(sub_angle)
            new_x = sub_x - math.cos(rad) * sub_speed
            new_y = sub_y - math.sin(rad) * sub_speed

            if is_circle_in_map(new_x, new_y, SUB_COLLISION_RADIUS):
                sub_x = new_x
                sub_y = new_y
                is_moving = True

        


        if is_moving:
            propeller_angle += propeller_speed
            bubble_timer += 1
            if bubble_timer >= 8:
                bubble_timer = 0
                if len(bubbles) < MAX_BUBBLES:
                    bx, by = get_bubble_spawn_position(sub_x, sub_y, sub_angle)
                    bubbles.append(create_bubble(bx, by))
        else:
            propeller_angle += propeller_speed * 0.2

        bubbles[:] = [b for b in bubbles if update_bubble(b)]

        # Calcula offset da câmera (submarino no centro)
        camera_x = sub_x - WIDTH // 2
        camera_y = sub_y - HEIGHT // 2

        # Desenha o mapa com offset da câmera
        screen.fill((0, 0, 0))
        screen.blit(map_surface, (-camera_x, -camera_y))

        # ---------- MINI MAPA ----------
        pygame.draw.rect(
            screen,
            (10, 20, 35),
            (MINIMAP_X, MINIMAP_Y, MINIMAP_WIDTH, MINIMAP_HEIGHT)
        )

        pygame.draw.rect(
            screen,
            (80, 120, 180),
            (MINIMAP_X, MINIMAP_Y, MINIMAP_WIDTH, MINIMAP_HEIGHT),
            2
        )
        # ---------- SUBMARINO NO MINI MAPA ----------
        mini_sub_x, mini_sub_y = world_to_minimap(sub_x, sub_y)

        pygame.draw.circle(
            screen,
            (255, 255, 0),
            (mini_sub_x, mini_sub_y),
            4
        )



        for jf in jellyfishes:
            jf_screen_x = jf['x'] - camera_x
            jf_screen_y = jf['y'] - camera_y
            if is_visible(jf_screen_x, jf_screen_y):
                update_jellyfish(jf, MAP_WIDTH, MAP_HEIGHT, is_jellyfish_in_map)
                # Desenha com offset
                jf_copy = jf.copy()
                jf_copy['x'] = jf_screen_x
                jf_copy['y'] = jf_screen_y
                draw_jellyfish_bioluminescent(screen, jf_copy)

                

        for bomb in water_bombs:
            bomb_screen_x = bomb['x'] - camera_x
            bomb_screen_y = bomb['y'] - camera_y
            if is_visible(bomb_screen_x, bomb_screen_y):
                update_water_bomb(bomb, MAP_HEIGHT, is_circle_in_map)
                bomb_copy = bomb.copy()
                bomb_copy['x'] = bomb_screen_x
                bomb_copy['y'] = bomb_screen_y
                draw_water_bomb(screen, bomb_copy, BOMB_BODY, BOMB_SPIKE, BOMB_HIGHLIGHT)

        update_giant_tentacles(giant_tentacles)
        tentacles_copy = {
            'x': giant_tentacles['x'] - camera_x,
            'y': giant_tentacles['y'] - camera_y,
            'time': giant_tentacles['time'],
            'wave_speed': giant_tentacles['wave_speed'],
            'num_tentacles': giant_tentacles['num_tentacles'],
            'scale': giant_tentacles.get('scale', 1.0)
        }
        draw_giant_tentacles(screen, tentacles_copy, TENTACLE_COLOR)

        # Sonar na posição do submarino (centro da tela)
        update_sonar(sonar, WIDTH // 2, HEIGHT // 2)
        draw_sonar(screen, sonar, SONAR_COLOR)

        for b in bubbles:
            b_screen = b.copy()
            b_screen['x'] = b['x'] - camera_x
            b_screen['y'] = b['y'] - camera_y
            draw_bubble(screen, b_screen)

        # Submarino sempre no centro da tela
        drawSubmarineFilled(
            screen,
            WIDTH // 2,
            HEIGHT // 2,
            sub_angle,
            SUBMARINE_BODY,
            SUBMARINE_DETAIL,
            SUBMARINE_FILL,
            propeller_angle,
            SUB_SCALE
        )

        # Atualiza e desenha a bateria (por último para ficar por cima)
        update_battery(battery)
        battery_height = draw_battery(screen, battery, 20, 20)
        
        # Desenha a profundidade embaixo da bateria
        depth = sub_y
        draw_depth(screen, depth, 20, 20 + battery_height + 10)

    if SHOW_FPS:
        pygame.display.set_caption(f"Echoes of the Deep | FPS: {int(clock.get_fps())}")

    pygame.display.flip()
    clock.tick(60)