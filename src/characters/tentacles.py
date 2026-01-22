import math
import random
from primitives import drawPolygon, drawCircle, DrawLineBresenham, drawEllipse, scanline_fill_gradient, scanline_fill
from transforms import get_translation_matrix, apply_transform


def create_giant_tentacles(x, y):
    return {
        'x': x,
        'y': y,
        'time': random.uniform(0, math.pi * 2),
        'wave_speed': 0.04,
        'num_tentacles': 6
    }


def update_giant_tentacles(gt):
    gt['time'] += gt['wave_speed']


def get_single_tentacle_points(gt, tentacle_index, num_tentacles):
    base_x = gt['x']
    base_y = gt['y']
    
    configs = [
        {'offset': -120, 'height': 320, 'width': 40, 'direction': 1, 'phase': 0},
        {'offset': -60, 'height': 380, 'width': 45, 'direction': -1, 'phase': 1.2},
        {'offset': 0, 'height': 420, 'width': 50, 'direction': 1, 'phase': 2.5},
        {'offset': 60, 'height': 360, 'width': 42, 'direction': -1, 'phase': 0.8},
        {'offset': 120, 'height': 300, 'width': 38, 'direction': 1, 'phase': 1.8},
        {'offset': -30, 'height': 340, 'width': 35, 'direction': -1, 'phase': 3.0},
    ]
    
    config = configs[tentacle_index % len(configs)]
    offset_x = config['offset']
    height = config['height']
    base_width = config['width']
    direction = config['direction']
    phase_offset = config['phase']
    
    left_points = []
    right_points = []
    
    num_segments = 25
    
    for i in range(num_segments + 1):
        progress = i / num_segments
        
        segment_y = base_y - (height * progress)
        
        wave1 = math.sin(gt['time'] * direction + phase_offset + progress * 4) * 50 * progress
        wave2 = math.sin(gt['time'] * 0.7 * direction + phase_offset * 1.5 + progress * 2) * 25 * progress
        
        segment_x = base_x + offset_x + wave1 + wave2
        
        width = base_width * (1 - progress * 0.8)
        width = max(width, 4)
        
        left_points.append((segment_x - width, segment_y))
        right_points.append((segment_x + width, segment_y))
    
    right_points.reverse()
    all_points = left_points + right_points
    
    return all_points


def get_sucker_positions(gt, tentacle_index, num_tentacles):
    base_x = gt['x']
    base_y = gt['y']
    
    configs = [
        {'offset': -120, 'height': 320, 'direction': 1, 'phase': 0},
        {'offset': -60, 'height': 380, 'direction': -1, 'phase': 1.2},
        {'offset': 0, 'height': 420, 'direction': 1, 'phase': 2.5},
        {'offset': 60, 'height': 360, 'direction': -1, 'phase': 0.8},
        {'offset': 120, 'height': 300, 'direction': 1, 'phase': 1.8},
        {'offset': -30, 'height': 340, 'direction': -1, 'phase': 3.0},
    ]
    
    config = configs[tentacle_index % len(configs)]
    offset_x = config['offset']
    height = config['height']
    direction = config['direction']
    phase_offset = config['phase']
    
    suckers = []
    num_suckers = 8
    
    for i in range(num_suckers):
        progress = 0.1 + (i / num_suckers) * 0.75
        
        segment_y = base_y - (height * progress)
        wave1 = math.sin(gt['time'] * direction + phase_offset + progress * 4) * 50 * progress
        wave2 = math.sin(gt['time'] * 0.7 * direction + phase_offset * 1.5 + progress * 2) * 25 * progress
        segment_x = base_x + offset_x + wave1 + wave2
        
        sucker_size = int(6 * (1 - progress * 0.6))
        sucker_size = max(sucker_size, 3)
        
        suckers.append((int(segment_x), int(segment_y), sucker_size))
    
    return suckers


def draw_giant_tentacles(surface, gt, color):
    num_tentacles = gt['num_tentacles']
    
    draw_order = [0, 5, 1, 4, 2, 3]
    
    for idx in draw_order:
        if idx < num_tentacles:
            tentacle_points = get_single_tentacle_points(gt, idx, num_tentacles)
            drawPolygon(surface, tentacle_points, color)
            
            suckers = get_sucker_positions(gt, idx, num_tentacles)
            for sx, sy, size in suckers:
                drawEllipse(surface, sx, sy, size + 3, size, color)


def draw_giant_tentacles_gradient(surface, gt, color_top, color_bottom, outline_color):
    num_tentacles = gt['num_tentacles']
    
    draw_order = [0, 5, 1, 4, 2, 3]
    
    for idx in draw_order:
        if idx < num_tentacles:
            tentacle_points = get_single_tentacle_points(gt, idx, num_tentacles)
            tentacle_int = [(int(p[0]), int(p[1])) for p in tentacle_points]
            
            scanline_fill_gradient(surface, tentacle_int, color_top, color_bottom)
            drawPolygon(surface, tentacle_points, outline_color)
            
            suckers = get_sucker_positions(gt, idx, num_tentacles)
            for sx, sy, size in suckers:
                drawEllipse(surface, sx, sy, size + 3, size, outline_color)


def check_tentacle_collision(gt, target_x, target_y, radius):
    num_tentacles = gt['num_tentacles']
    
    configs = [
        {'offset': -120, 'height': 320},
        {'offset': -60, 'height': 380},
        {'offset': 0, 'height': 420},
        {'offset': 60, 'height': 360},
        {'offset': 120, 'height': 300},
        {'offset': -30, 'height': 340},
    ]
    
    for i in range(num_tentacles):
        config = configs[i % len(configs)]
        tentacle_x = gt['x'] + config['offset']
        height = config['height']
        
        if gt['y'] - height < target_y < gt['y']:
            dx = abs(target_x - tentacle_x)
            if dx < 60:
                return True
    
    return False
