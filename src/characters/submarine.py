import math
from primitives import (
    drawPolygon, drawCircle, DrawLineBresenham, 
    scanline_fill, drawEllipse
)
from transforms import get_rotation_matrix, get_translation_matrix, mat_mul, apply_transform, get_scale_matrix


def init_sonar():
    return {
        'active': False,
        'timer': 0,
        'waves': []
    }


def activate_sonar(sonar):
    if not sonar['active']:
        sonar['active'] = True
        sonar['timer'] = 180  


def update_sonar(sonar, x, y):
    if sonar['active']:
        sonar['timer'] -= 1
        if sonar['timer'] % 15 == 0: 
            sonar['waves'].append({
                'scale': 0.1,
                'alpha': 1.0,
                'x': x,
                'y': y
            })
        
        if sonar['timer'] <= 0:
            sonar['active'] = False
    
    for wave in sonar['waves']:
        wave['scale'] += 0.04
        wave['alpha'] -= 0.012
    
    sonar['waves'] = [w for w in sonar['waves'] if w['alpha'] > 0]


def draw_sonar(surface, sonar, color, camera_x, camera_y):
    for wave in sonar['waves']:
        sx = wave['x'] - camera_x
        sy = wave['y'] - camera_y

        radius = int(50 * wave['scale'])
        alpha = max(0, min(1, wave['alpha']))

        wave_color = (
            int(color[0] * alpha),
            int(color[1] * alpha),
            int(color[2] * alpha)
        )

        if radius > 0:
            drawCircle(surface, int(sx), int(sy), radius, wave_color)


def get_submarine_parts():
    body = []
    for i in range(20):
        angle = math.pi + (math.pi * i / 19)
        x = int(50 * math.cos(angle))
        y = int(30 * math.sin(angle))
        body.append((x, y))
    for i in range(20):
        angle = (math.pi * i / 19)
        x = int(50 * math.cos(angle))
        y = int(30 * math.sin(angle))
        body.append((x, y))
    
    tail = [
        (-50, -10),
        (-70, 0),
        (-50, 10),
    ]
    
    tower_base = [
        (-15, -30),
        (-15, -45),
        (15, -45),
        (15, -30),
    ]
    
    periscope = [
        (5, -45),
        (5, -65),
        (15, -65),
        (15, -60),
        (10, -60),
        (10, -45),
    ]
    
    tower_lines = [
        [(-15, -35), (15, -35)],
        [(-15, -40), (15, -40)],
    ]
    
    stripe_left = [
        (-20, -28),
        (-15, -28),
        (-15, 28),
        (-20, 28),
    ]
    
    stripe_right = [
        (20, -28),
        (25, -28),
        (25, 28),
        (20, 28),
    ]
    
    fin_top = [
        (-55, -10),
        (-45, -25),
        (-35, -10),
    ]
    
    fin_bottom = [
        (-55, 10),
        (-45, 25),
        (-35, 10),
    ]
    
    circles = {
        'window_left': (-10, 0, 10),
        'window_left_inner': (-10, 0, 7),
        'window_right': (20, 0, 10),
        'window_right_inner': (20, 0, 7),
        'propeller_center': (-70, 0, 4),
        'rivet_1': (-10, -20, 2),
        'rivet_2': (-10, 20, 2),
        'rivet_3': (20, -20, 2),
        'rivet_4': (20, 20, 2),
        'rivet_5': (35, -15, 2),
        'rivet_6': (35, 15, 2),
        'rivet_7': (40, 0, 2),
    }
    
    return {
        'body': body,
        'tail': tail,
        'tower_base': tower_base,
        'periscope': periscope,
        'tower_lines': tower_lines,
        'stripe_left': stripe_left,
        'stripe_right': stripe_right,
        'fin_top': fin_top,
        'fin_bottom': fin_bottom,
        'circles': circles
    }


def get_propeller_blades(propeller_angle):
    blades = []
    for i in range(4):
        blade_angle = propeller_angle + (i * 90)
        rad = math.radians(blade_angle)
        end_x = -70 + math.cos(rad) * 15
        end_y = 0 + math.sin(rad) * 15
        blades.append([(-70, 0), (end_x, end_y)])
    return blades


def get_transform_matrix(x, y, angle, scale=1.0):
    from transforms import get_scale_matrix
    scale_mat = get_scale_matrix(scale, scale)
    rotation = get_rotation_matrix(angle)
    translation = get_translation_matrix(x, y)
    temp = mat_mul(rotation, scale_mat)
    return mat_mul(translation, temp)


def transform_point(cx, cy, matrix):
    points = [(cx, cy)]
    transformed = apply_transform(points, matrix)
    return transformed[0]


def drawSubmarine(surface, x, y, angle, body_color, detail_color, propeller_angle=0, scale=1.0):
    parts = get_submarine_parts()
    matrix = get_transform_matrix(x, y, angle, scale)
    
    body = apply_transform(parts['body'], matrix)
    drawPolygon(surface, body, body_color)
    
    tail = apply_transform(parts['tail'], matrix)
    drawPolygon(surface, tail, body_color)
    
    tower_base = apply_transform(parts['tower_base'], matrix)
    drawPolygon(surface, tower_base, body_color)
    
    periscope = apply_transform(parts['periscope'], matrix)
    drawPolygon(surface, periscope, body_color)
    
    for line in parts['tower_lines']:
        translated = apply_transform(line, matrix)
        p1, p2 = translated[0], translated[1]
        DrawLineBresenham(surface, int(p1[0]), int(p1[1]), 
                         int(p2[0]), int(p2[1]), detail_color)
    
    for stripe_name in ['stripe_left', 'stripe_right']:
        stripe = apply_transform(parts[stripe_name], matrix)
        drawPolygon(surface, stripe, detail_color)
    
    propeller_blades = get_propeller_blades(propeller_angle)
    for blade in propeller_blades:
        translated = apply_transform(blade, matrix)
        p1, p2 = translated[0], translated[1]
        DrawLineBresenham(surface, int(p1[0]), int(p1[1]), 
                         int(p2[0]), int(p2[1]), body_color)
    
    fin_top = apply_transform(parts['fin_top'], matrix)
    drawPolygon(surface, fin_top, body_color)
    
    fin_bottom = apply_transform(parts['fin_bottom'], matrix)
    drawPolygon(surface, fin_bottom, body_color)
    
    circles = parts['circles']
    
    for name, (cx, cy, radius) in circles.items():
        final_x, final_y = transform_point(cx, cy, matrix)
        final_x, final_y = int(final_x), int(final_y)
        scaled_radius = int(radius * scale)
        
        if 'window' in name:
            if 'inner' in name:
                color = body_color
            else:
                color = detail_color
        elif 'propeller' in name:
            color = detail_color
        elif 'rivet' in name:
            color = detail_color
        else:
            color = detail_color
        
        drawCircle(surface, final_x, final_y, scaled_radius, color)


def drawSubmarineFilled(surface, x, y, angle, body_color, detail_color, fill_color, propeller_angle=0, scale=1.0):
    parts = get_submarine_parts()
    matrix = get_transform_matrix(x, y, angle, scale)
    
    body = apply_transform(parts['body'], matrix)
    body_int = [(int(px), int(py)) for px, py in body]
    scanline_fill(surface, body_int, fill_color)
    
    tail = apply_transform(parts['tail'], matrix)
    tail_int = [(int(px), int(py)) for px, py in tail]
    scanline_fill(surface, tail_int, fill_color)
    
    tower_base = apply_transform(parts['tower_base'], matrix)
    tower_int = [(int(px), int(py)) for px, py in tower_base]
    scanline_fill(surface, tower_int, fill_color)
    
    periscope = apply_transform(parts['periscope'], matrix)
    periscope_int = [(int(px), int(py)) for px, py in periscope]
    scanline_fill(surface, periscope_int, fill_color)
    
    fin_top = apply_transform(parts['fin_top'], matrix)
    fin_top_int = [(int(px), int(py)) for px, py in fin_top]
    scanline_fill(surface, fin_top_int, fill_color)
    
    fin_bottom = apply_transform(parts['fin_bottom'], matrix)
    fin_bottom_int = [(int(px), int(py)) for px, py in fin_bottom]
    scanline_fill(surface, fin_bottom_int, fill_color)
    
    drawSubmarine(surface, x, y, angle, body_color, detail_color, propeller_angle, scale)


def get_bubble_spawn_position(sub_x, sub_y, sub_angle):
    rad = math.radians(sub_angle)
    spawn_x = sub_x - math.cos(rad) * 85
    spawn_y = sub_y - math.sin(rad) * 85
    return spawn_x, spawn_y

def submarine_battery():
    return {
        'x': 0,
        'y': 0,
        'width': 100,
        'height': 10,
        'charge': 100,
        'timer': 0,  
    }


def update_battery(battery):
    """Atualiza a bateria - descarga 1% a cada 1.5 segundos (90 frames a 60fps)"""
    battery['timer'] += 1
    if battery['timer'] >= 90: 
        battery['timer'] = 0
        battery['charge'] = max(0, battery['charge'] - 1)
    return battery['charge'] > 0 

def use_sonar_battery(battery):
    """Desconta 5% da bateria ao usar o sonar"""
    battery['charge'] = max(0, battery['charge'] - 5)
    return battery['charge'] > 0 

def draw_battery(surface, battery, x, y):
    """Desenha a bateria vertical estilo ícone"""
    from primitives import drawPolygon, scanline_fill
    import pygame
    
    bar_width = 40
    bar_height = 80
    terminal_width = 16
    terminal_height = 8
    border_thickness = 4
    terminal_x = x + (bar_width - terminal_width) // 2
    terminal = [
        (terminal_x, y),
        (terminal_x + terminal_width, y),
        (terminal_x + terminal_width, y + terminal_height),
        (terminal_x, y + terminal_height)
    ]
    drawPolygon(surface, terminal, (60, 60, 60))
    scanline_fill(surface, terminal, (60, 60, 60))
    
    body_y = y + terminal_height
    body = [
        (x, body_y),
        (x + bar_width, body_y),
        (x + bar_width, body_y + bar_height),
        (x, body_y + bar_height)
    ]
    drawPolygon(surface, body, (40, 40, 40))
    scanline_fill(surface, body, (40, 40, 40))
    
    inner_margin = border_thickness
    inner = [
        (x + inner_margin, body_y + inner_margin),
        (x + bar_width - inner_margin, body_y + inner_margin),
        (x + bar_width - inner_margin, body_y + bar_height - inner_margin),
        (x + inner_margin, body_y + bar_height - inner_margin)
    ]
    drawPolygon(surface, inner, (200, 200, 200))
    scanline_fill(surface, inner, (200, 200, 200))
    
    num_segments = 4
    segment_gap = 3
    inner_height = bar_height - (2 * inner_margin)
    segment_height = (inner_height - (num_segments - 1) * segment_gap) // num_segments
    
    segments_on = int((battery['charge'] / 100) * num_segments + 0.5)
    
    if battery['charge'] > 50:
        color = (0, 180, 80)
    elif battery['charge'] > 25:
        color = (220, 180, 0)
    else:
        color = (200, 50, 50)
    
    for i in range(num_segments):
        segment_index = num_segments - 1 - i 
        seg_y = body_y + inner_margin + i * (segment_height + segment_gap)
        
        if segment_index < segments_on:
            seg = [
                (x + inner_margin + 2, seg_y),
                (x + bar_width - inner_margin - 2, seg_y),
                (x + bar_width - inner_margin - 2, seg_y + segment_height),
                (x + inner_margin + 2, seg_y + segment_height)
            ]
            drawPolygon(surface, seg, color)
            scanline_fill(surface, seg, color)
    
    drawPolygon(surface, body, (60, 60, 60))
    
    font = pygame.font.Font(None, 32)
    percent_text = f"{int(battery['charge'])}%"
    text_surface = font.render(percent_text, True, color)
    surface.blit(text_surface, (x + bar_width + 8, y + terminal_height + bar_height // 2 - 10))
    
    return terminal_height + bar_height


def draw_depth(surface, depth, x, y):
    """Desenha o indicador de profundidade"""
    import pygame
    
    font = pygame.font.Font(None, 28)
    depth_text = f"{int(depth)}m"
    text_surface = font.render(depth_text, True, (200, 200, 200))
    surface.blit(text_surface, (x, y))

def apply_damage(battery, damage_amount):
    """Aplica dano à bateria do submarino."""
    battery['charge'] = max(0, battery['charge'] - damage_amount)
    return battery['charge'] > 0