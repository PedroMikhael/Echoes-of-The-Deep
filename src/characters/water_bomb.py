import math
import random
from primitives import drawPolygon, drawCircle, DrawLineBresenham, drawEllipse, scanline_fill
from transforms import get_rotation_matrix, get_translation_matrix, mat_mul, apply_transform
from characters.explosion import ExplosionParticle, ExplosionFragment



def create_water_bomb(x, y, scale=1.0):
    return {
        'x': x,
        'y': y,
        'speed_y': 0.8,
        'time': random.uniform(0, math.pi * 2),
        'wobble_phase': random.uniform(0, math.pi * 2),
        'rotation': 0,
        'rotation_speed': random.uniform(-1, 1),
        'active': True,
        'scale': scale
    }


def update_water_bomb(bomb, bounds_height, is_in_map_func=None):
    if not bomb['active']:
        return
    
    bomb['time'] += 0.03
    bomb['wobble_phase'] += 0.05
    bomb['rotation'] += bomb['rotation_speed']
    
    new_x = bomb['x'] + math.sin(bomb['wobble_phase']) * 0.5
    
    new_y = bomb['y'] + math.sin(bomb['time']) * 0.8
    
    if is_in_map_func is None or is_in_map_func(new_x, new_y):
        bomb['x'] = new_x
        bomb['y'] = new_y
    elif is_in_map_func is not None:
        if is_in_map_func(new_x, bomb['y']):
            bomb['x'] = new_x
        if is_in_map_func(bomb['x'], new_y):
            bomb['y'] = new_y

def create_explosion(x, y):
    return {
        'x': x,
        'y': y,
        'frame': 0,
        'particles': [ExplosionParticle(x, y) for _ in range(25)],
        'fragments': [ExplosionFragment(x, y) for _ in range(6)]
    }


def get_bomb_body_points(bomb):
    scale = bomb.get('scale', 1.0)
    radius = 28 * scale
    points = []
    num_points = 32

    for i in range(num_points):
        angle = (i / num_points) * math.pi * 2
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        points.append((x, y))

    return points


def draw_metal_shading(surface, center, radius, base_color):
    cx, cy = center

    for r in range(radius, 0, -2):
        factor = r / radius
        shade = (
            min(255, int(base_color[0] * factor)),
            min(255, int(base_color[1] * factor)),
            min(255, int(base_color[2] * factor))
        )
        drawCircle(surface, cx, cy, r, shade)



def get_bomb_spikes(bomb):
    spikes = []
    scale = bomb.get('scale', 1.0)
    num_spikes = 6
    base_radius = 28 * scale
    spike_length = 10 * scale
    spike_width = 6 * scale

    for i in range(num_spikes):
        angle = (i / num_spikes) * math.pi * 2

        base_x = base_radius * math.cos(angle)
        base_y = base_radius * math.sin(angle)

        tip_x = (base_radius + spike_length) * math.cos(angle)
        tip_y = (base_radius + spike_length) * math.sin(angle)

        left_x = base_x + spike_width * math.cos(angle + math.pi/2)
        left_y = base_y + spike_width * math.sin(angle + math.pi/2)
        right_x = base_x + spike_width * math.cos(angle - math.pi/2)
        right_y = base_y + spike_width * math.sin(angle - math.pi/2)

        spikes.append([(left_x, left_y), (tip_x, tip_y), (right_x, right_y)])

    return spikes

def get_bomb_rivets(bomb):
    rivets = []
    scale = bomb.get('scale', 1.0)
    radius = 20 * scale
    num = 8

    for i in range(num):
        angle = (i / num) * math.pi * 2
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        rivets.append((x, y))

    return rivets



def get_bomb_bubbles(bomb):
    bubbles = []
    num_bubbles = 5
    
    for i in range(num_bubbles):
        phase = bomb['time'] + i * 0.8
        offset_x = math.sin(phase * 2) * 10
        offset_y = -40 - (phase % 3) * 15
        radius = 3 + math.sin(phase) * 2
        
        bubbles.append({
            'x': offset_x,
            'y': offset_y,
            'radius': max(2, int(radius))
        })
    
    return bubbles


def draw_water_bomb(surface, bomb, body_color, spike_color, highlight_color):
    if not bomb['active']:
        return
    
    x = int(bomb['x'])
    y = int(bomb['y'])
    
    rotation_matrix = get_rotation_matrix(bomb['rotation'])
    translation_matrix = get_translation_matrix(x, y)
    matrix = mat_mul(translation_matrix, rotation_matrix)
    
    radius = int(28 * bomb.get('scale', 1.0))
    center = apply_transform([(0, 0)], matrix)[0]
    draw_metal_shading(surface, (int(center[0]), int(center[1])), radius, body_color)

    
    spikes = get_bomb_spikes(bomb)
    for spike in spikes:
        transformed = apply_transform(spike, matrix)
        drawPolygon(surface, transformed, spike_color)
        scanline_fill(surface, transformed, spike_color)

    rivets = get_bomb_rivets(bomb)
    for r in rivets:
        pos = apply_transform([r], matrix)[0]
        drawCircle(surface, int(pos[0]), int(pos[1]), 3, (80, 80, 80))

    highlight = apply_transform([(-10, -10)], matrix)[0]
    drawCircle(surface, int(highlight[0]), int(highlight[1]), 6, highlight_color)

    
    bubbles = get_bomb_bubbles(bomb)
    for bubble in bubbles:
        bubble_pos = apply_transform([(bubble['x'], bubble['y'])], matrix)[0]
        drawCircle(surface, int(bubble_pos[0]), int(bubble_pos[1]), int(bubble['radius']), highlight_color)
    
    center_points = []
    for i in range(6):
        angle = (i / 6) * math.pi * 2
        px = 8 * math.cos(angle)
        py = 8 * math.sin(angle)
        center_points.append((px, py))
    
    transformed_center = apply_transform(center_points, matrix)
    drawPolygon(surface, transformed_center, highlight_color)
