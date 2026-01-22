import math
from primitives import (
    drawPolygon, drawCircle, DrawLineBresenham, 
    scanline_fill, drawEllipse
)
from transforms import get_rotation_matrix, get_translation_matrix, mat_mul, apply_transform


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


def get_transform_matrix(x, y, angle):
    rotation = get_rotation_matrix(angle)
    translation = get_translation_matrix(x, y)
    return mat_mul(translation, rotation)


def transform_point(cx, cy, matrix):
    points = [(cx, cy)]
    transformed = apply_transform(points, matrix)
    return transformed[0]


def drawSubmarine(surface, x, y, angle, body_color, detail_color, propeller_angle=0):
    parts = get_submarine_parts()
    matrix = get_transform_matrix(x, y, angle)
    
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
        
        drawCircle(surface, final_x, final_y, radius, color)


def drawSubmarineFilled(surface, x, y, angle, body_color, detail_color, fill_color, propeller_angle=0):
    parts = get_submarine_parts()
    matrix = get_transform_matrix(x, y, angle)
    
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
    
    drawSubmarine(surface, x, y, angle, body_color, detail_color, propeller_angle)


def get_bubble_spawn_position(sub_x, sub_y, sub_angle):
    rad = math.radians(sub_angle)
    spawn_x = sub_x - math.cos(rad) * 85
    spawn_y = sub_y - math.sin(rad) * 85
    return spawn_x, spawn_y
