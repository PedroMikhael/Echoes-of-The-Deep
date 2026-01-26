import math
from primitives import (
    drawPolygon, drawCircle, DrawLineBresenham, 
    scanline_fill, drawEllipse
)
from transforms import (
    get_rotation_matrix, get_translation_matrix, 
    mat_mul, apply_transform, get_scale_matrix
)



CAPSULE_BODY = (50, 55, 65)          # Cinza escuro metálico
CAPSULE_BODY_LIGHT = (70, 75, 85)    # Cinza mais claro para detalhes
CAPSULE_ACCENT = (40, 45, 55)        # Cinza escuro para linhas
CAPSULE_LIGHT_OFF = (80, 30, 30)     # Vermelho apagado
CAPSULE_LIGHT_ON = (255, 80, 50)     # Vermelho/laranja brilhante
CAPSULE_GLOW = (255, 120, 80)        # Glow da luz
BARNACLE_COLOR = (90, 100, 80)       # Cracas/coral


def create_research_capsule(x, y, scale=0.5):
    return {
        'x': x,
        'y': y,
        'scale': scale,
        'time': 0,
        'light_phase': 0,
        'float_offset': 0,
        'collected': False
    }


def update_research_capsule(capsule):
    capsule['time'] += 1
    
    capsule['light_phase'] = (capsule['time'] % 60) / 60.0
    
    capsule['float_offset'] = math.sin(capsule['time'] * 0.03) * 3


def get_capsule_parts():
    body = []
    for i in range(24):
        angle = (2 * math.pi * i) / 24
        x = int(60 * math.cos(angle))  
        y = int(30 * math.sin(angle)) 
        body.append((x, y))
    
    cap_left = []
    for i in range(12):
        angle = math.pi/2 + (math.pi * i / 11)
        x = -55 + int(15 * math.cos(angle))
        y = int(25 * math.sin(angle))
        cap_left.append((x, y))
    
    cap_right = []
    for i in range(12):
        angle = -math.pi/2 + (math.pi * i / 11)
        x = 55 + int(15 * math.cos(angle))
        y = int(25 * math.sin(angle))
        cap_right.append((x, y))
    
    detail_lines = [
        [(-30, -28), (-30, 28)],
        [(0, -28), (0, 28)],
        [(30, -28), (30, 28)],
    ]
    
    stripe_top = [
        (-50, -10),
        (50, -10),
        (50, -5),
        (-50, -5),
    ]
    
    stripe_bottom = [
        (-50, 5),
        (50, 5),
        (50, 10),
        (-50, 10),
    ]
    
    handle = [
        (-10, -30),
        (-8, -40),
        (8, -40),
        (10, -30),
    ]
    
    lights = {
        'light_left': (-35, 0, 8),
        'light_right': (35, 0, 8),
    }
    
    barnacles = [
        (-50, -20, 4),
        (-45, 22, 3),
        (48, -18, 3),
        (52, 15, 4),
        (-55, 5, 3),
    ]
    
    rivets = [
        (-20, -25, 2),
        (20, -25, 2),
        (-20, 25, 2),
        (20, 25, 2),
    ]
    
    return {
        'body': body,
        'cap_left': cap_left,
        'cap_right': cap_right,
        'detail_lines': detail_lines,
        'stripe_top': stripe_top,
        'stripe_bottom': stripe_bottom,
        'handle': handle,
        'lights': lights,
        'barnacles': barnacles,
        'rivets': rivets,
    }


def get_transform_matrix(x, y, scale=1.0):
    scale_mat = get_scale_matrix(scale, scale)
    translation = get_translation_matrix(x, y)
    return mat_mul(translation, scale_mat)


def transform_point(cx, cy, matrix):
    points = [(cx, cy)]
    transformed = apply_transform(points, matrix)
    return transformed[0]


def draw_research_capsule(surface, capsule):
    if capsule['collected']:
        return
    
    parts = get_capsule_parts()
    
    
    draw_y = capsule['y'] + capsule['float_offset']
    matrix = get_transform_matrix(capsule['x'], draw_y, capsule['scale'])
    
   
    light_intensity = 0.5 + 0.5 * math.sin(capsule['light_phase'] * 2 * math.pi)
    
    
    if light_intensity > 0.6:
        glow_radius = int(80 * capsule['scale'] * light_intensity)
        glow_alpha = light_intensity * 0.3
        glow_color = (
            int(CAPSULE_GLOW[0] * glow_alpha),
            int(CAPSULE_GLOW[1] * glow_alpha),
            int(CAPSULE_GLOW[2] * glow_alpha),
        )
        glow_x, glow_y = transform_point(0, 0, matrix)
        drawCircle(surface, int(glow_x), int(glow_y), glow_radius, glow_color)
    
    body = apply_transform(parts['body'], matrix)
    body_int = [(int(px), int(py)) for px, py in body]
    scanline_fill(surface, body_int, CAPSULE_BODY)
    drawPolygon(surface, body_int, CAPSULE_ACCENT)
    
    cap_left = apply_transform(parts['cap_left'], matrix)
    cap_left_int = [(int(px), int(py)) for px, py in cap_left]
    scanline_fill(surface, cap_left_int, CAPSULE_BODY_LIGHT)
    drawPolygon(surface, cap_left_int, CAPSULE_ACCENT)
    
    cap_right = apply_transform(parts['cap_right'], matrix)
    cap_right_int = [(int(px), int(py)) for px, py in cap_right]
    scanline_fill(surface, cap_right_int, CAPSULE_BODY_LIGHT)
    drawPolygon(surface, cap_right_int, CAPSULE_ACCENT)
    
    stripe_top = apply_transform(parts['stripe_top'], matrix)
    stripe_top_int = [(int(px), int(py)) for px, py in stripe_top]
    scanline_fill(surface, stripe_top_int, CAPSULE_ACCENT)
    
    stripe_bottom = apply_transform(parts['stripe_bottom'], matrix)
    stripe_bottom_int = [(int(px), int(py)) for px, py in stripe_bottom]
    scanline_fill(surface, stripe_bottom_int, CAPSULE_ACCENT)
    
    handle = apply_transform(parts['handle'], matrix)
    handle_int = [(int(px), int(py)) for px, py in handle]
    scanline_fill(surface, handle_int, CAPSULE_BODY_LIGHT)
    drawPolygon(surface, handle_int, CAPSULE_ACCENT)
    
    for line in parts['detail_lines']:
        transformed = apply_transform(line, matrix)
        p1, p2 = transformed[0], transformed[1]
        DrawLineBresenham(surface, int(p1[0]), int(p1[1]), 
                         int(p2[0]), int(p2[1]), CAPSULE_ACCENT)
    
    
    for name, (cx, cy, radius) in parts['lights'].items():
        light_x, light_y = transform_point(cx, cy, matrix)
        scaled_radius = int(radius * capsule['scale'])
        
        light_color = (
            int(CAPSULE_LIGHT_OFF[0] + (CAPSULE_LIGHT_ON[0] - CAPSULE_LIGHT_OFF[0]) * light_intensity),
            int(CAPSULE_LIGHT_OFF[1] + (CAPSULE_LIGHT_ON[1] - CAPSULE_LIGHT_OFF[1]) * light_intensity),
            int(CAPSULE_LIGHT_OFF[2] + (CAPSULE_LIGHT_ON[2] - CAPSULE_LIGHT_OFF[2]) * light_intensity),
        )
        
        # Desenha a luz com borda
        drawCircle(surface, int(light_x), int(light_y), scaled_radius + 2, CAPSULE_ACCENT)
        drawCircle(surface, int(light_x), int(light_y), scaled_radius, light_color)
        
        # Brilho interno quando acesa
        if light_intensity > 0.5:
            inner_radius = max(1, int(scaled_radius * 0.5))
            drawCircle(surface, int(light_x), int(light_y), inner_radius, CAPSULE_GLOW)
    
    # Cracas
    for cx, cy, radius in parts['barnacles']:
        barnacle_x, barnacle_y = transform_point(cx, cy, matrix)
        scaled_radius = max(1, int(radius * capsule['scale']))
        drawCircle(surface, int(barnacle_x), int(barnacle_y), scaled_radius, BARNACLE_COLOR)
    
    # Rebites
    for cx, cy, radius in parts['rivets']:
        rivet_x, rivet_y = transform_point(cx, cy, matrix)
        scaled_radius = max(1, int(radius * capsule['scale']))
        drawCircle(surface, int(rivet_x), int(rivet_y), scaled_radius, CAPSULE_ACCENT)


def check_capsule_collision(sub_x, sub_y, capsule, collision_radius=50):
    """Verifica se o submarino coletou a cápsula"""
    if capsule['collected']:
        return False
    
    dx = sub_x - capsule['x']
    dy = sub_y - capsule['y']
    distance = math.sqrt(dx * dx + dy * dy)
    
    # Raio de colisão escalado
    capsule_radius = 60 * capsule['scale']
    
    return distance < (collision_radius + capsule_radius)


def collect_capsule(capsule):
    """Marca a cápsula como coletada"""
    capsule['collected'] = True
