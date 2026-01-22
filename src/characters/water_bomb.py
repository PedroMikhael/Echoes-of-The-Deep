import math
import random
from primitives import drawPolygon, drawCircle, DrawLineBresenham, drawEllipse, scanline_fill
from transforms import get_rotation_matrix, get_translation_matrix, mat_mul, apply_transform


def create_water_bomb(x, y):
    return {
        'x': x,
        'y': y,
        'speed_y': 0.8,
        'time': random.uniform(0, math.pi * 2),
        'wobble_phase': random.uniform(0, math.pi * 2),
        'rotation': 0,
        'rotation_speed': random.uniform(-1, 1),
        'active': True
    }


def update_water_bomb(bomb, bounds_height):
    if not bomb['active']:
        return
    
    bomb['time'] += 0.03
    bomb['wobble_phase'] += 0.05
    bomb['rotation'] += bomb['rotation_speed']
    
    bomb['y'] += bomb['speed_y']
    bomb['x'] += math.sin(bomb['wobble_phase']) * 0.5
    
    if bomb['y'] > bounds_height:
        bomb['y'] = -50
        bomb['x'] = random.randint(100, 1800)


def get_bomb_body_points(bomb):
    pulse = 1 + math.sin(bomb['time'] * 2) * 0.03
    
    points = []
    num_points = 24
    width = 25 * pulse
    height = 35 * pulse
    
    for i in range(num_points):
        angle = (i / num_points) * math.pi * 2
        px = width * math.cos(angle)
        py = height * math.sin(angle)
        points.append((px, py))
    
    return points


def get_bomb_spikes(bomb):
    spikes = []
    num_spikes = 8
    pulse = 1 + math.sin(bomb['time'] * 2) * 0.03
    base_radius = 30 * pulse
    spike_length = 15 * pulse
    
    for i in range(num_spikes):
        angle = (i / num_spikes) * math.pi * 2
        
        base_x = base_radius * math.cos(angle)
        base_y = base_radius * math.sin(angle)
        
        tip_x = (base_radius + spike_length) * math.cos(angle)
        tip_y = (base_radius + spike_length) * math.sin(angle)
        
        side_angle = math.pi / 12
        left_x = base_radius * math.cos(angle - side_angle)
        left_y = base_radius * math.sin(angle - side_angle)
        right_x = base_radius * math.cos(angle + side_angle)
        right_y = base_radius * math.sin(angle + side_angle)
        
        spikes.append({
            'tip': (tip_x, tip_y),
            'left': (left_x, left_y),
            'right': (right_x, right_y)
        })
    
    return spikes


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
    
    body_points = get_bomb_body_points(bomb)
    transformed_body = apply_transform(body_points, matrix)
    drawPolygon(surface, transformed_body, body_color)
    scanline_fill(surface, transformed_body, body_color)
    
    spikes = get_bomb_spikes(bomb)
    for spike in spikes:
        spike_points = [spike['left'], spike['tip'], spike['right']]
        transformed_spike = apply_transform(spike_points, matrix)
        drawPolygon(surface, transformed_spike, spike_color)
        scanline_fill(surface, transformed_spike, spike_color)
    
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
