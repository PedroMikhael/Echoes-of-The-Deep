import math
import random
from primitives import drawPolygon, drawCircle, DrawLineBresenham, drawEllipse, scanline_fill
from transforms import get_rotation_matrix, get_translation_matrix, mat_mul, apply_transform


def create_jellyfish(x, y):
    return {
        'x': x,
        'y': y,
        'target_x': x,
        'target_y': y,
        'speed': 0.5,
        'time': random.uniform(0, math.pi * 2),
        'pulse': 0,
        'pulse_speed': 0.08,
        'tentacle_phase': random.uniform(0, math.pi * 2),
        'direction_timer': 0,
        'direction_interval': random.randint(120, 240)
    }


def update_jellyfish(jf, bounds_width, bounds_height):
    jf['time'] += 0.02
    jf['pulse'] += jf['pulse_speed']
    jf['tentacle_phase'] += 0.05
    
    jf['direction_timer'] += 1
    if jf['direction_timer'] >= jf['direction_interval']:
        jf['direction_timer'] = 0
        jf['direction_interval'] = random.randint(120, 240)
        margin = 100
        jf['target_x'] = random.randint(margin, bounds_width - margin)
        jf['target_y'] = random.randint(margin, bounds_height - margin)
    
    dx = jf['target_x'] - jf['x']
    dy = jf['target_y'] - jf['y']
    dist = math.sqrt(dx * dx + dy * dy)
    
    if dist > 5:
        jf['x'] += (dx / dist) * jf['speed']
        jf['y'] += (dy / dist) * jf['speed']
    
    jf['y'] += math.sin(jf['time']) * 0.3


def get_dome_outline(jf):
    pulse_scale = 1 + math.sin(jf['pulse']) * 0.08
    
    points = []
    dome_width = 50 * pulse_scale
    dome_height = 65 * pulse_scale
    
    for i in range(25):
        t = i / 24
        angle = math.pi * t
        px = dome_width * math.cos(angle)
        py = -dome_height * math.sin(angle) * 0.9
        points.append((px, py))
    
    num_waves = 8
    wave_depth = 8 * pulse_scale
    for i in range(num_waves + 1):
        t = i / num_waves
        x = dome_width - (2 * dome_width * t)
        wave = math.sin(t * math.pi * num_waves) * wave_depth
        points.append((x, wave))
    
    return points


def get_dome_ribs(jf):
    pulse_scale = 1 + math.sin(jf['pulse']) * 0.08
    dome_width = 50 * pulse_scale
    dome_height = 45 * pulse_scale
    
    ribs = []
    num_ribs = 6
    
    for rib in range(num_ribs):
        t = (rib + 1) / (num_ribs + 1)
        center_x = dome_width - (2 * dome_width * t)
        
        rib_points = []
        for i in range(10):
            s = i / 9
            y = -dome_height * 0.9 * s
            wave = math.sin(s * math.pi) * 5
            x = center_x + wave * (0.5 - abs(t - 0.5))
            rib_points.append((x, y))
        
        ribs.append(rib_points)
    
    return ribs


def get_tentacle_points(jf, tentacle_index, num_tentacles):
    pulse_scale = 1 + math.sin(jf['pulse']) * 0.08
    dome_width = 50 * pulse_scale
    
    spacing = (dome_width * 1.6) / (num_tentacles - 1) if num_tentacles > 1 else 0
    start_x = -dome_width * 0.8 + spacing * tentacle_index
    start_y = 5
    
    points = [(start_x, start_y)]
    
    num_segments = 12
    segment_length = 10
    
    phase_offset = tentacle_index * 0.7 + jf['tentacle_phase']
    base_curve = (tentacle_index - num_tentacles / 2) * 0.15
    
    current_x = start_x
    current_y = start_y
    
    for seg in range(num_segments):
        progress = seg / num_segments
        wave_amplitude = 12 * (1 - progress * 0.3)
        wave = math.sin(phase_offset + seg * 0.6) * wave_amplitude
        
        current_x += wave * 0.25 + base_curve * 2
        current_y += segment_length * (1 - progress * 0.2)
        
        points.append((current_x, current_y))
    
    return points


def draw_jellyfish(surface, jf, color):
    x = int(jf['x'])
    y = int(jf['y'])
    
    matrix = get_translation_matrix(x, y)
    
    dome_points = get_dome_outline(jf)
    transformed_dome = apply_transform(dome_points, matrix)
    drawPolygon(surface, transformed_dome, color)
    
    num_tentacles = 7
    for i in range(num_tentacles):
        tentacle_points = get_tentacle_points(jf, i, num_tentacles)
        transformed_tentacle = apply_transform(tentacle_points, matrix)
        
        for j in range(len(transformed_tentacle) - 1):
            p1 = transformed_tentacle[j]
            p2 = transformed_tentacle[j + 1]
            DrawLineBresenham(surface, int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]), color)


def get_bioluminescent_color(jf, base_intensity=1.0):
    pulse = math.sin(jf['pulse'] * 1.5) * 0.5 + 0.5
    
    r = int(255 * base_intensity)
    g = int(50 + pulse * 100 * base_intensity)
    b = int(180 + pulse * 75 * base_intensity)
    
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    
    return (r, g, b)


def draw_jellyfish_bioluminescent(surface, jf):
    x = int(jf['x'])
    y = int(jf['y'])
    
    matrix = get_translation_matrix(x, y)
    
    glow_color = get_bioluminescent_color(jf, 1.0)
    
    dome_points = get_dome_outline(jf)
    transformed_dome = apply_transform(dome_points, matrix)
    drawPolygon(surface, transformed_dome, glow_color)
    
    num_tentacles = 7
    for i in range(num_tentacles):
        tentacle_points = get_tentacle_points(jf, i, num_tentacles)
        transformed_tentacle = apply_transform(tentacle_points, matrix)
        
        num_segments = len(transformed_tentacle) - 1
        for j in range(num_segments):
            fade = 1.0 - (j / num_segments) * 0.6
            segment_color = get_bioluminescent_color(jf, fade)
            
            p1 = transformed_tentacle[j]
            p2 = transformed_tentacle[j + 1]
            DrawLineBresenham(surface, int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]), segment_color)


def check_jellyfish_collision(jf, target_x, target_y, radius):
    dx = jf['x'] - target_x
    dy = jf['y'] - target_y
    dist = math.sqrt(dx * dx + dy * dy)
    collision_radius = 60 + radius
    return dist < collision_radius


def jellyfish_detect_sound(jf, sound_x, sound_y, detection_radius):
    dx = jf['x'] - sound_x
    dy = jf['y'] - sound_y
    dist = math.sqrt(dx * dx + dy * dy)
    
    if dist < detection_radius:
        jf['target_x'] = sound_x
        jf['target_y'] = sound_y
        jf['speed'] = 1.5
        jf['direction_timer'] = 0
        jf['direction_interval'] = 180
        return True
    return False


def jellyfish_calm_down(jf):
    jf['speed'] = 0.5
