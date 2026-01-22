import math
import random
import pygame
from primitives import drawPolygon, drawCircle, DrawLineBresenham, scanline_fill, drawEllipse, flood_fill_iterativo, scanline_fill_gradient
from characters.submarine import drawSubmarine

ABYSS_BLACK = (5, 8, 12)
DARK_CHARCOAL = (15, 20, 28)
GHOSTLY_TEAL = (40, 80, 85)
GHOSTLY_TEAL_BRIGHT = (80, 140, 150)
DIM_WHITE = (180, 185, 190)
BUTTON_BG = (20, 28, 35)
BUTTON_BORDER = (50, 70, 80)
BUTTON_HOVER_BORDER = (80, 140, 150)

particles = []
buttons = []

def init_menu(width, height):
    global particles, buttons
    
    particles = []
    for _ in range(30):
        p = {
            'x': random.randint(0, width),
            'y': random.randint(0, height),
            'radius': random.randint(1, 3),
            'speed_y': random.uniform(-0.3, -0.1),
            'speed_x': random.uniform(-0.1, 0.1),
            'brightness': random.randint(30, 80),
            'pulse_speed': random.uniform(0.02, 0.05),
            'pulse_offset': random.uniform(0, math.pi * 2),
            'width': width,
            'height': height
        }
        particles.append(p)
    
    button_width = 250
    button_height = 45
    button_x = (width - button_width) // 2
    
   
    total_buttons_height = (4 * 45) + (3 * 60)
    center_y_available = height * 0.6  
    start_y = int(center_y_available - total_buttons_height / 2 + height * 0.1)
    
    spacing = 60
    
    buttons = [
        {'x': button_x, 'y': start_y, 'w': button_width, 'h': button_height, 'text': "NOVO JOGO", 'hovered': False},
        {'x': button_x, 'y': start_y + spacing, 'w': button_width, 'h': button_height, 'text': "INSTRUCOES", 'hovered': False},
        {'x': button_x, 'y': start_y + spacing * 2, 'w': button_width, 'h': button_height, 'text': "CREDITOS", 'hovered': False},
        {'x': button_x, 'y': start_y + spacing * 3, 'w': button_width, 'h': button_height, 'text': "SAIR", 'hovered': False},
    ]


def update_particle(p, time):
    p['y'] += p['speed_y']
    p['x'] += p['speed_x']
    
    if p['y'] < -10:
        p['y'] = p['height'] + 10
        p['x'] = random.randint(0, p['width'])
    
    pulse = math.sin(time * p['pulse_speed'] + p['pulse_offset'])
    p['current_brightness'] = int(p['brightness'] + pulse * 20)


def draw_particle(surface, p):
    b = p['current_brightness']
    color = (b // 3, b, b)
    drawCircle(surface, int(p['x']), int(p['y']), p['radius'], color)


def is_mouse_over_button(btn, mx, my):
    return btn['x'] <= mx <= btn['x'] + btn['w'] and btn['y'] <= my <= btn['y'] + btn['h']


def draw_button(surface, btn, font):
    points = [
        (btn['x'], btn['y']),
        (btn['x'] + btn['w'], btn['y']),
        (btn['x'] + btn['w'], btn['y'] + btn['h']),
        (btn['x'], btn['y'] + btn['h'])
    ]
    points_int = [(int(p[0]), int(p[1])) for p in points]
    
    scanline_fill(surface, points_int, BUTTON_BG)
    
    border_color = BUTTON_HOVER_BORDER if btn['hovered'] else BUTTON_BORDER
    drawPolygon(surface, points, border_color)
    
    if btn['hovered']:
        inner = [
            (btn['x'] + 2, btn['y'] + 2),
            (btn['x'] + btn['w'] - 2, btn['y'] + 2),
            (btn['x'] + btn['w'] - 2, btn['y'] + btn['h'] - 2),
            (btn['x'] + 2, btn['y'] + btn['h'] - 2)
        ]
        drawPolygon(surface, inner, GHOSTLY_TEAL)
    
    text_surface = font.render(btn['text'], True, DIM_WHITE)
    text_rect = text_surface.get_rect(center=(btn['x'] + btn['w'] // 2, btn['y'] + btn['h'] // 2))
    surface.blit(text_surface, text_rect)


def update_menu(time, mouse_x, mouse_y):
    for p in particles:
        update_particle(p, time)
    
    for btn in buttons:
        btn['hovered'] = is_mouse_over_button(btn, mouse_x, mouse_y)


def draw_menu_decorations(surface, width, height):
    decor_color = (25, 35, 45)
    fill_color = (18, 28, 38)
    
    drawEllipse(surface, 150, 300, 60, 30, decor_color)
    flood_fill_iterativo(surface, 150, 300, fill_color, decor_color)
    
    drawEllipse(surface, width - 150, 350, 50, 25, decor_color)
    flood_fill_iterativo(surface, width - 150, 350, fill_color, decor_color)
    
    drawEllipse(surface, 100, height - 200, 40, 20, decor_color)
    flood_fill_iterativo(surface, 100, height - 200, fill_color, decor_color)
    
    drawEllipse(surface, width - 100, height - 180, 45, 22, decor_color)
    flood_fill_iterativo(surface, width - 100, height - 180, fill_color, decor_color)
    
    drawCircle(surface, 80, 250, 15, decor_color)
    flood_fill_iterativo(surface, 80, 250, fill_color, decor_color)
    
    drawCircle(surface, width - 80, 280, 12, decor_color)
    flood_fill_iterativo(surface, width - 80, 280, fill_color, decor_color)
    
    drawCircle(surface, 120, height - 150, 10, decor_color)
    flood_fill_iterativo(surface, 120, height - 150, fill_color, decor_color)
    
    DrawLineBresenham(surface, 50, 350, 100, 400, decor_color)
    DrawLineBresenham(surface, 100, 400, 80, 450, decor_color)
    DrawLineBresenham(surface, width - 50, 370, width - 100, 420, decor_color)
    DrawLineBresenham(surface, width - 100, 420, width - 70, 470, decor_color)


def draw_title_gradient(surface, text, x, y, font, color_top, color_bottom):
    title_surface = font.render(text, True, (255, 255, 255))
    title_rect = title_surface.get_rect(center=(x, y))
    
    width = title_surface.get_width()
    height = title_surface.get_height()
    
    for py in range(height):
        t = py / height
        
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * t)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * t)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * t)
        
        gradient_color = (r, g, b)
        
        for px in range(width):
            pixel_color = title_surface.get_at((px, py))
            if pixel_color[3] > 0:
                title_surface.set_at((px, py), gradient_color)
    
    surface.blit(title_surface, title_rect)


def draw_menu(surface, width, height, title_font, button_font):
    draw_menu_decorations(surface, width, height)
    
    for p in particles:
        draw_particle(surface, p)
    
    title_y = int(height * 0.2)
    gradient_top = (100, 200, 255)
    gradient_bottom = (50, 100, 150)
    draw_title_gradient(surface, "ECHOES OF THE DEEP", width // 2, title_y, title_font, gradient_top, gradient_bottom)
    
    subtitle_font = pygame.font.Font(None, 28)
    subtitle = subtitle_font.render("Uma jornada nas profundezas", True, GHOSTLY_TEAL)
    subtitle_rect = subtitle.get_rect(center=(width // 2, title_y + 50))
    surface.blit(subtitle, subtitle_rect)
    
    for btn in buttons:
        draw_button(surface, btn, button_font)
    
    sub_color = (30, 40, 50)
    sub_detail = (20, 30, 40)
    drawSubmarine(surface, width // 2, height - 100, 0, sub_color, sub_detail)


def handle_menu_click(mouse_x, mouse_y):
    for btn in buttons:
        if is_mouse_over_button(btn, mouse_x, mouse_y):
            return btn['text']
    return None


instructions_back_btn = None
credits_back_btn = None

def init_instructions(width, height):
    global instructions_back_btn
    button_width = 150
    button_height = 40
    instructions_back_btn = {
        'x': (width - button_width) // 2,
        'y': height - 80,
        'w': button_width,
        'h': button_height,
        'text': "VOLTAR",
        'hovered': False
    }


def init_credits(width, height):
    global credits_back_btn
    button_width = 150
    button_height = 40
    credits_back_btn = {
        'x': (width - button_width) // 2,
        'y': height - 80,
        'w': button_width,
        'h': button_height,
        'text': "VOLTAR",
        'hovered': False
    }


def update_instructions(mouse_x, mouse_y):
    if instructions_back_btn:
        instructions_back_btn['hovered'] = is_mouse_over_button(instructions_back_btn, mouse_x, mouse_y)


def update_credits(mouse_x, mouse_y):
    if credits_back_btn:
        credits_back_btn['hovered'] = is_mouse_over_button(credits_back_btn, mouse_x, mouse_y)


def draw_instructions(surface, width, height, title_font, button_font):
    title = title_font.render("INSTRUCOES", True, DIM_WHITE)
    title_rect = title.get_rect(center=(width // 2, 80))
    surface.blit(title, title_rect)
    
    info_font = pygame.font.Font(None, 32)
    instructions = [
        "SETAS DIRECIONAIS - Mover submarino",
        "CIMA - Acelerar para frente",
        "BAIXO - Acelerar para tras",
        "ESQUERDA/DIREITA - Girar",
        "ESC - Voltar ao menu"
    ]
    
    y_pos = 180
    for line in instructions:
        text = info_font.render(line, True, GHOSTLY_TEAL_BRIGHT)
        text_rect = text.get_rect(center=(width // 2, y_pos))
        surface.blit(text, text_rect)
        y_pos += 45
    
    if instructions_back_btn:
        draw_button(surface, instructions_back_btn, button_font)


def draw_credits(surface, width, height, title_font, button_font):
    title = title_font.render("CREDITOS", True, DIM_WHITE)
    title_rect = title.get_rect(center=(width // 2, 80))
    surface.blit(title, title_rect)
    
    info_font = pygame.font.Font(None, 32)
    credits_list = [
        "Jogo desenvolvido para a disciplina de Computação Gráfica por:",
        "Pedro Mikhael",
        "João Victor",
        "Rian Vilanova",
        "Bianca Leão",
        "Fabio Stahl",
        
    ]
    
    y_pos = 180
    for line in credits_list:
        color = GHOSTLY_TEAL_BRIGHT if line else DIM_WHITE
        text = info_font.render(line, True, color)
        text_rect = text.get_rect(center=(width // 2, y_pos))
        surface.blit(text, text_rect)
        y_pos += 40
    
    if credits_back_btn:
        draw_button(surface, credits_back_btn, button_font)


def handle_instructions_click(mouse_x, mouse_y):
    if instructions_back_btn and is_mouse_over_button(instructions_back_btn, mouse_x, mouse_y):
        return "VOLTAR"
    return None


def handle_credits_click(mouse_x, mouse_y):
    if credits_back_btn and is_mouse_over_button(credits_back_btn, mouse_x, mouse_y):
        return "VOLTAR"
    return None
