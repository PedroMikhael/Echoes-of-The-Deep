import pygame
from primitives import drawPolygon, scanline_fill, drawCircle
from transforms import get_scale_matrix, get_translation_matrix, mat_mul, apply_transform

def draw_minimap(surface, x, y, width, height, map_zones, player_pos, map_width, map_height, objects_dict=None):
    bg_points = [
        (x, y),
        (x + width, y),
        (x + width, y + height),
        (x, y + height)
    ]
    drawPolygon(surface, bg_points, (200, 200, 200))
    scanline_fill(surface, bg_points, (0, 0, 0))

    scale_mat = get_scale_matrix(width / map_width, height / map_height)
    trans_mat = get_translation_matrix(x, y)
    transform = mat_mul(trans_mat, scale_mat)

    for zone in map_zones:
        minimap_zone = apply_transform(zone, transform)
        minimap_zone = [(max(x, min(x + width, int(px))), max(y, min(y + height, int(py)))) for px, py in minimap_zone]
        
        if len(minimap_zone) >= 3:
            scanline_fill(surface, minimap_zone, (40, 60, 100))

    player_transformed = apply_transform([player_pos], transform)[0]
    mx, my = int(player_transformed[0]), int(player_transformed[1])
    
    if x <= mx <= x + width and y <= my <= y + height:
        drawCircle(surface, mx, my, 3, (255, 255, 0))

    if objects_dict:
        if 'base' in objects_dict:
            bx, by = objects_dict['base']
            base_transformed = apply_transform([(bx, by)], transform)[0]
            mbx, mby = int(base_transformed[0]), int(base_transformed[1])
            drawCircle(surface, mbx, mby, 4, (0, 255, 0))

        if 'capsules' in objects_dict:
            for cap in objects_dict['capsules']:
                if cap and not cap.get('collected', False):
                    cx, cy = cap['x'], cap['y']
                    cap_transformed = apply_transform([(cx, cy)], transform)[0]
                    mcx, mcy = int(cap_transformed[0]), int(cap_transformed[1])
                    drawCircle(surface, mcx, mcy, 3, (255, 0, 0))
        
        elif 'capsule' in objects_dict:
            cap = objects_dict['capsule']
            if cap and not cap.get('collected', False):
                cx, cy = cap['x'], cap['y']
                cap_transformed = apply_transform([(cx, cy)], transform)[0]
                mcx, mcy = int(cap_transformed[0]), int(cap_transformed[1])
                drawCircle(surface, mcx, mcy, 3, (255, 0, 0))
