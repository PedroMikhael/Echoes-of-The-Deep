import pygame
import sys
import math
import random
import primitives
from primitives import drawCircle
import time

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

from characters.research_capsule import (
    create_research_capsule,
    update_research_capsule,
    draw_research_capsule,
    check_capsule_collision,
    collect_capsule
)

import menu
import map
from map import get_spawn_position, is_point_in_map, get_all_map_zones
import minimap

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

WIDTH = 1280
HEIGHT = 720

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Echoes of the Deep")
clock = pygame.time.Clock()

pygame.mixer.music.load("sounds/underwater_sound.mp3")
pygame.mixer.music.set_volume(0.75)
pygame.mixer.music.play(-1)

sonar_sound = pygame.mixer.Sound("sounds/submarine_sonar.mp3")
sonar_sound.set_volume(0.7)

# Adicionar depois que tiver a animação de dano em personagens
impact_sound = pygame.mixer.Sound("sounds/impact_submarine.mp3")
impact_sound.set_volume(0.3)

SHOW_FPS = True

title_font = pygame.font.Font(None, 64)
button_font = pygame.font.Font(None, 36)

menu.init_menu(WIDTH, HEIGHT)
menu.init_instructions(WIDTH, HEIGHT)
menu.init_credits(WIDTH, HEIGHT)

GAME_STATE_MENU = "menu"
GAME_STATE_PLAYING = "playing"
GAME_STATE_INSTRUCTIONS = "instructions"
GAME_STATE_CREDITS = "credits"
GAME_STATE_VICTORY = "victory"
GAME_STATE_GAMEOVER = "gameover"
GAME_STATE_PAUSED = "paused"

game_state = GAME_STATE_MENU
menu_time = 0

sub_x = WIDTH // 2
sub_y = HEIGHT // 2
sub_angle = 0
sub_speed = 3
rotation_speed = 4
propeller_angle = 0
propeller_speed = 15
SUB_SCALE = 0.5

camera_x = 0
camera_y = 0

bubbles = []
bubble_timer = 0
MAX_BUBBLES = 120

jellyfishes = []
water_bombs = []
giant_tentacles = None
sonar = None
battery = None
research_capsules = [] 
MAP_WIDTH = 2000
MAP_HEIGHT = 1200
map_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
map_surface.fill((0, 0, 0))
map.drawMap(map_surface)

BASE_POS = get_spawn_position()
BASE_RADIUS = 90

mission_start_time = 0
SHOW_MISSION_DURATION_MS = 4500

victory_start_time = 0
VICTORY_DURATION_MS = 2500

gameover_start_time = 0
GAMEOVER_DURATION_MS = 3000
gameover_big_font = pygame.font.Font(None, 96)
gameover_mid_font = pygame.font.Font(None, 40)

hud_font = pygame.font.Font(None, 28)
mission_big_font = pygame.font.Font(None, 64)
mission_small_font = pygame.font.Font(None, 28)
victory_big_font = pygame.font.Font(None, 96)
victory_mid_font = pygame.font.Font(None, 40)
pause_big_font = pygame.font.Font(None, 72)
pause_button_font = pygame.font.Font(None, 36)


pause_buttons = []

def init_pause_menu():
    global pause_buttons
    button_width = 280
    button_height = 55
    button_x = (WIDTH - button_width) // 2
    start_y = HEIGHT // 2
    spacing = 70
    
    pause_buttons = [
        {'x': button_x, 'y': start_y, 'w': button_width, 'h': button_height, 'text': "CONTINUAR", 'hovered': False},
        {'x': button_x, 'y': start_y + spacing, 'w': button_width, 'h': button_height, 'text': "MENU PRINCIPAL", 'hovered': False},
    ]

def update_pause_menu(mouse_x, mouse_y):
    for btn in pause_buttons:
        btn['hovered'] = btn['x'] <= mouse_x <= btn['x'] + btn['w'] and btn['y'] <= mouse_y <= btn['y'] + btn['h']

def draw_pause_menu(surface):
    
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    
    
    title = pause_big_font.render("PAUSADO", True, (180, 200, 220))
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
    surface.blit(title, title_rect)
    
    
    for btn in pause_buttons:
        
        btn_color = (30, 45, 60) if not btn['hovered'] else (50, 70, 90)
        border_color = (60, 90, 110) if not btn['hovered'] else (80, 140, 150)
        
        pygame.draw.rect(surface, btn_color, (btn['x'], btn['y'], btn['w'], btn['h']))
        pygame.draw.rect(surface, border_color, (btn['x'], btn['y'], btn['w'], btn['h']), 2)
        
        text = pause_button_font.render(btn['text'], True, (200, 210, 220))
        text_rect = text.get_rect(center=(btn['x'] + btn['w'] // 2, btn['y'] + btn['h'] // 2))
        surface.blit(text, text_rect)

def handle_pause_click(mouse_x, mouse_y):
    for btn in pause_buttons:
        if btn['x'] <= mouse_x <= btn['x'] + btn['w'] and btn['y'] <= mouse_y <= btn['y'] + btn['h']:
            return btn['text']
    return None

init_pause_menu()

def is_in_base(px, py):
    dx = px - BASE_POS[0]
    dy = py - BASE_POS[1]
    return (dx * dx + dy * dy) <= (BASE_RADIUS * BASE_RADIUS)

def draw_center_overlay(surface, lines, big_font, small_font, elapsed_ms, duration_ms):
    t = max(0.0, min(1.0, 1.0 - (elapsed_ms / duration_ms)))
    bg_alpha = int(220 * t)
    text_alpha = int(255 * t)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, bg_alpha))
    surface.blit(overlay, (0, 0))

    y = HEIGHT // 2 - 70
    for text, is_big in lines:
        font = big_font if is_big else small_font
        rendered = font.render(text, True, (255, 255, 255))
        rendered.set_alpha(text_alpha)
        rect = rendered.get_rect(center=(WIDTH // 2, y))
        surface.blit(rendered, rect)
        y += 60 if is_big else 35

def draw_base_marker(surface, base_x, base_y, camera_x, camera_y):
    sx = base_x - camera_x
    sy = base_y - camera_y
    pulse = abs(math.sin(pygame.time.get_ticks() * 0.004))
    r = int(BASE_RADIUS + 10 * pulse)
    col = (int(120 + 80 * pulse), int(200 + 30 * pulse), int(255))
    primitives.drawCircle(surface, int(sx), int(sy), r, col)
    primitives.drawCircle(surface, int(sx), int(sy), 6, (255, 255, 255))

def is_visible(x, y, margin=200):
    return -margin < x < WIDTH + margin and -margin < y < HEIGHT + margin

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
                    mission_start_time = pygame.time.get_ticks()

                    jellyfishes = [
                        create_jellyfish(450, 780, 0.3),
                        create_jellyfish(600, 700, 0.3),
                        create_jellyfish(850, 250, 0.25),
                        create_jellyfish(1000, 250, 0.25),
                        create_jellyfish(1100, 820, 0.3),
                        create_jellyfish(1250, 850, 0.3),
                    ]

                    water_bombs = [
                        create_water_bomb(550, 750, 0.35),
                        create_water_bomb(800, 250, 0.35),
                        create_water_bomb(950, 270, 0.35),
                        create_water_bomb(1650, 850, 0.35),
                        create_water_bomb(100, 700, 0.35),
                        create_water_bomb(150, 200, 0.35),
                        create_water_bomb(250, 200, 0.35),
                        create_water_bomb(300, 700, 0.35),
                    ]

                    giant_tentacles = create_giant_tentacles(1100, 900, 0.5)
                    sonar = init_sonar()
                    battery = submarine_battery()
                    
                    # Duas cápsulas de pesquisa
                    research_capsules = [
                        create_research_capsule(1750, 850, 0.4),   # Cápsula no corredor final
                        create_research_capsule(450, 200, 0.4),    # Cápsula no topo do arco
                    ]

                elif action == "INSTRUCOES":
                    game_state = GAME_STATE_INSTRUCTIONS
                elif action == "CREDITOS":
                    game_state = GAME_STATE_CREDITS
                elif action == "SAIR":
                    pygame.quit()
                    sys.exit()

            elif game_state in (GAME_STATE_INSTRUCTIONS, GAME_STATE_CREDITS):
                game_state = GAME_STATE_MENU

            elif game_state == GAME_STATE_VICTORY:
                game_state = GAME_STATE_MENU

            elif game_state == GAME_STATE_GAMEOVER:
                game_state = GAME_STATE_MENU
            
            elif game_state == GAME_STATE_PAUSED:
                action = handle_pause_click(mouse_x, mouse_y)
                if action == "CONTINUAR":
                    game_state = GAME_STATE_PLAYING
                elif action == "MENU PRINCIPAL":
                    game_state = GAME_STATE_MENU

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == GAME_STATE_PLAYING:
                    game_state = GAME_STATE_PAUSED
                elif game_state == GAME_STATE_PAUSED:
                    game_state = GAME_STATE_PLAYING
                else:
                    game_state = GAME_STATE_MENU
            if event.key == pygame.K_SPACE and game_state == GAME_STATE_PLAYING:
                if battery['charge'] >= 3:
                    activate_sonar(sonar)
                    use_sonar_battery(battery)
                    sonar_sound.play()

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

    elif game_state == GAME_STATE_VICTORY:
        screen.fill((0, 0, 0))

        elapsed = pygame.time.get_ticks() - victory_start_time

        bg = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 200))
        screen.blit(bg, (0, 0))

        title = victory_big_font.render("VOCÊ VENCEU!", True, (255, 230, 120))
        subtitle = victory_mid_font.render("Cápsulas recuperadas e entregue na base.", True, (230, 230, 230))

        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
        screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))

        if elapsed >= VICTORY_DURATION_MS:
            game_state = GAME_STATE_MENU

    elif game_state == GAME_STATE_GAMEOVER:
        screen.fill((0, 0, 0))

        elapsed = pygame.time.get_ticks() - gameover_start_time

        bg = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        bg.fill((30, 0, 0, 200))
        screen.blit(bg, (0, 0))

        title = gameover_big_font.render("GAME OVER", True, (255, 80, 80))
        subtitle = gameover_mid_font.render("A bateria do submarino acabou...", True, (200, 200, 200))

        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
        screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))

        if elapsed >= GAMEOVER_DURATION_MS:
            game_state = GAME_STATE_MENU

    elif game_state == GAME_STATE_PAUSED:
        
        screen.fill((0, 0, 0))
        screen.blit(map_surface, (-camera_x, -camera_y))
        
        
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
        
        update_pause_menu(mouse_x, mouse_y)
        draw_pause_menu(screen)

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
            if is_point_in_map(new_x, new_y):
                sub_x = new_x
                sub_y = new_y
                is_moving = True
        if keys[pygame.K_DOWN]:
            rad = math.radians(sub_angle)
            new_x = sub_x - math.cos(rad) * sub_speed
            new_y = sub_y - math.sin(rad) * sub_speed
            if is_point_in_map(new_x, new_y):
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

        camera_x = sub_x - WIDTH // 2
        camera_y = sub_y - HEIGHT // 2

        
        cycle_time = pygame.time.get_ticks() % 20000  
        is_shaking = cycle_time >= 15000  
        
        if is_shaking:
            shake_intensity = 4
            shake_x = random.randint(-shake_intensity, shake_intensity)
            shake_y = random.randint(-shake_intensity, shake_intensity)
            camera_x += shake_x
            camera_y += shake_y

        screen.fill((0, 0, 0))
        screen.blit(map_surface, (-camera_x, -camera_y))

        draw_base_marker(screen, BASE_POS[0], BASE_POS[1], camera_x, camera_y)

        for jf in jellyfishes:
            jf_screen_x = jf['x'] - camera_x
            jf_screen_y = jf['y'] - camera_y
            if is_visible(jf_screen_x, jf_screen_y):
                update_jellyfish(jf, MAP_WIDTH, MAP_HEIGHT, is_point_in_map)
                jf_copy = jf.copy()
                jf_copy['x'] = jf_screen_x
                jf_copy['y'] = jf_screen_y
                draw_jellyfish_bioluminescent(screen, jf_copy)

        for bomb in water_bombs:
            bomb_screen_x = bomb['x'] - camera_x
            bomb_screen_y = bomb['y'] - camera_y
            if is_visible(bomb_screen_x, bomb_screen_y):
                update_water_bomb(bomb, MAP_HEIGHT, is_point_in_map)
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

        # Cápsulas de pesquisa
        for capsule in research_capsules:
            if not capsule['collected']:
                update_research_capsule(capsule)
                capsule_screen_x = capsule['x'] - camera_x
                capsule_screen_y = capsule['y'] - camera_y
                if is_visible(capsule_screen_x, capsule_screen_y, 150):
                    capsule_copy = capsule.copy()
                    capsule_copy['x'] = capsule_screen_x
                    capsule_copy['y'] = capsule_screen_y
                    draw_research_capsule(screen, capsule_copy)

                if check_capsule_collision(sub_x, sub_y, capsule):
                    collect_capsule(capsule)

        update_sonar(sonar, sub_x, sub_y)
        draw_sonar(screen, sonar, SONAR_COLOR,camera_x,camera_y)

        for b in bubbles:
            b_draw = b.copy()
            b_draw['x'] = b['x'] - camera_x
            b_draw['y'] = b['y'] - camera_y
            draw_bubble(screen, b_draw)

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

        
        update_battery(battery)
        battery_height = draw_battery(screen, battery, 20, 20)

        if battery['charge'] <= 0:
            game_state = GAME_STATE_GAMEOVER
            gameover_start_time = pygame.time.get_ticks()

        depth = sub_y
        draw_depth(screen, depth, 20, 20 + battery_height + 10)

        # Contagem de cápsulas
        collected_count = sum(1 for cap in research_capsules if cap['collected'])
        total_capsules = len(research_capsules)
        
        if collected_count < total_capsules:
            obj_text = f"Objetivo: Coletar cápsulas ({collected_count}/{total_capsules})"
        else:
            obj_text = "TODAS AS CÁPSULAS COLETADAS!"
        obj_render = hud_font.render(obj_text, True, (230, 230, 230))
        screen.blit(obj_render, (20, 20 + battery_height + 70))

        ## minimapa
        minimap_x = WIDTH - 250
        minimap_y = 20
        minimap_w = 230
        minimap_h = 160
        
        # Passar apenas cápsulas não coletadas para o minimapa
        uncollected_capsules = [cap for cap in research_capsules if not cap['collected']]
        objects_to_draw = {
            'base': BASE_POS,
            'capsules': uncollected_capsules,
            'sonar': sonar
        }
        
        minimap.draw_minimap(
            screen, 
            minimap_x, minimap_y, minimap_w, minimap_h,
            get_all_map_zones(),
            (sub_x, sub_y),
            MAP_WIDTH, MAP_HEIGHT,
            objects_to_draw
        )

        # Mostrar progresso quando há cápsulas coletadas
        if collected_count > 0 and collected_count < total_capsules:
            status_font = pygame.font.Font(None, 24)
            status_text = status_font.render(f"CÁPSULA {collected_count}/{total_capsules} COLETADA", True, (0, 255, 100))
            screen.blit(status_text, (20, 20 + battery_height + 40))

            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005))
            icon_color = (int(100 + 155 * pulse), int(200 + 55 * pulse), int(80 + 100 * pulse))
            primitives.drawCircle(screen, 10, 20 + battery_height + 48, 4, icon_color)

            center_font = pygame.font.Font(None, 48)
            remaining = total_capsules - collected_count
            find_text = center_font.render(f"ENCONTRE MAIS {remaining} CÁPSULA(S)!", True, (255, 200, 50))
            text_rect = find_text.get_rect(center=(WIDTH // 2, 60))

            bg_rect = text_rect.inflate(20, 10)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.fill((20, 30, 50))
            bg_surface.set_alpha(int(180 + 50 * pulse))
            screen.blit(bg_surface, bg_rect.topleft)
            screen.blit(find_text, text_rect)

        # Vitória quando todas as cápsulas são coletadas
        if collected_count == total_capsules:
            game_state = GAME_STATE_VICTORY
            victory_start_time = pygame.time.get_ticks()

        elapsed = pygame.time.get_ticks() - mission_start_time
        if elapsed < SHOW_MISSION_DURATION_MS:
            draw_center_overlay(
                screen,
                [
                    ("OBJETIVO", True),
                    ("ENCONTRE AS 2 CÁPSULAS DE PESQUISA", True),
                    ("Setas: mover | ESPAÇO: sonar", False),
                ],
                mission_big_font,
                mission_small_font,
                elapsed,
                SHOW_MISSION_DURATION_MS
            )

    if SHOW_FPS:
        pygame.display.set_caption(f"Echoes of the Deep | FPS: {int(clock.get_fps())}")

    pygame.display.flip()
    clock.tick(60)
