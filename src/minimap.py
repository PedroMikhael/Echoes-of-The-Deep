import pygame
from primitives import drawPolygon, scanline_fill, drawCircle
from transforms import get_window_to_viewport_matrix_pygame, apply_transform

def draw_minimap(surface, x, y, width, height,
                 map_zones, player_pos,
                 map_width, map_height,
                 objects_dict=None):

    bg_points = [
        (x, y),
        (x + width, y),
        (x + width, y + height),
        (x, y + height)
    ]
    drawPolygon(surface, bg_points, (200, 200, 200))
    scanline_fill(surface, bg_points, (0, 0, 0))

    janela = (0, 0, map_width, map_height)
    viewport = (x, y, x + width, y + height)
    transform = get_window_to_viewport_matrix_pygame(janela, viewport)

    for zone in map_zones:
        minimap_zone = apply_transform(zone, transform)
        minimap_zone = [
            (max(x, min(x + width, int(px))),
             max(y, min(y + height, int(py))))
            for px, py in minimap_zone
        ]

        if len(minimap_zone) >= 3:
            scanline_fill(surface, minimap_zone, (40, 60, 100))

    if objects_dict and 'sonar' in objects_dict:
        sonar = objects_dict['sonar']

        player_mm = apply_transform([player_pos], transform)[0]
        pmx, pmy = int(player_mm[0]), int(player_mm[1])

        if not (x <= pmx <= x + width and y <= pmy <= y + height):
            return

        scale = min(width / map_width, height / map_height)

        base_radius = 50

        for wave in sonar.get('waves', []):
            world_radius = base_radius * wave['scale']
            radius = int(world_radius * scale)

            alpha = max(0, min(1, wave['alpha']))

            color = (
                int(0 * alpha),
                int(200 * alpha),
                int(255 * alpha)
            )

            drawCircle(surface, pmx, pmy, radius, color)


    player_transformed = apply_transform([player_pos], transform)[0]
    px, py = int(player_transformed[0]), int(player_transformed[1])

    if x <= px <= x + width and y <= py <= y + height:
        drawCircle(surface, px, py, 3, (255, 255, 0))

    if not objects_dict:
        return

    if 'base' in objects_dict:
        bx, by = objects_dict['base']
        bt = apply_transform([(bx, by)], transform)[0]
        drawCircle(surface, int(bt[0]), int(bt[1]), 4, (0, 255, 0))

    if 'capsules' in objects_dict:
        for cap in objects_dict['capsules']:
            if cap and not cap.get('collected', False):
                cx, cy = cap['x'], cap['y']
                ct = apply_transform([(cx, cy)], transform)[0]
                drawCircle(surface, int(ct[0]), int(ct[1]), 3, (255, 0, 0))

    elif 'capsule' in objects_dict:
        cap = objects_dict['capsule']
        if cap and not cap.get('collected', False):
            cx, cy = cap['x'], cap['y']
            ct = apply_transform([(cx, cy)], transform)[0]
            drawCircle(surface, int(ct[0]), int(ct[1]), 3, (255, 0, 0))
