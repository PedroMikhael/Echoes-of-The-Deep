"""
Módulo de Lanterna do Submarino
Sistema de iluminação com cone de luz usando Cohen-Sutherland para clipping.
"""
import math
import pygame
from primitives import scanline_fill, drawPolygon, cohen_sutherland, DrawLineBresenham


def get_flashlight_cone(sub_x, sub_y, angle, length=230, spread=30):
    """
    Calcula os 3 pontos do triângulo de luz da lanterna.
    
    Args:
        sub_x, sub_y: Posição do submarino (centro da tela)
        angle: Ângulo do submarino em graus
        length: Comprimento do cone de luz (reduzido para 200)
        spread: Ângulo de abertura do cone (reduzido para 25)
    
    Returns:
        Lista com 3 pontos [(x1,y1), (x2,y2), (x3,y3)]
    """
    rad = math.radians(angle)
    
    origin_x = sub_x
    origin_y = sub_y
    
    left_angle = rad - math.radians(spread)
    right_angle = rad + math.radians(spread)
    
    left_x = origin_x + math.cos(left_angle) * length
    left_y = origin_y + math.sin(left_angle) * length
    
    right_x = origin_x + math.cos(right_angle) * length
    right_y = origin_y + math.sin(right_angle) * length
    
    return [(origin_x, origin_y), (left_x, left_y), (right_x, right_y)]


def get_flashlight_window(cone_points):
    """
    Retorna a bounding box do cone para uso com Cohen-Sutherland.
    
    Returns:
        (xmin, ymin, xmax, ymax)
    """
    xs = [p[0] for p in cone_points]
    ys = [p[1] for p in cone_points]
    return (min(xs), min(ys), max(xs), max(ys))


def apply_darkness_overlay(screen, cone_points, width, height, darkness_alpha=230):
    """
    Aplica uma camada de escuridão na tela, deixando apenas o cone visível.
    Usa setPixel para preencher o cone com transparência.
    
    Args:
        screen: Surface do pygame
        cone_points: 3 pontos do triângulo de luz
        width, height: Dimensões da tela
        darkness_alpha: Opacidade da escuridão (0-255)
    """
    darkness = pygame.Surface((width, height), pygame.SRCALPHA)
    darkness.fill((0, 0, 0, darkness_alpha))
    
    cone_int = [(int(p[0]), int(p[1])) for p in cone_points]
    
    points = cone_int
    ys = [p[1] for p in points]
    y_min = max(0, int(min(ys)))
    y_max = min(height, int(max(ys)))
    
    n = len(points)
    transparent = (0, 0, 0, 0)
    
    for y in range(y_min, y_max):
        intersections_x = []
        
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            
            if y0 == y1:
                continue
            
            if y0 > y1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            
            if y < y0 or y >= y1:
                continue
            
            x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
            intersections_x.append(x)
        
        intersections_x.sort()
        
        for i in range(0, len(intersections_x), 2):
            if i + 1 < len(intersections_x):
                x_start = max(0, int(round(intersections_x[i])))
                x_end = min(width - 1, int(round(intersections_x[i + 1])))
                
                for x in range(x_start, x_end + 1):
                    darkness.set_at((x, y), transparent)
    
    screen.blit(darkness, (0, 0))


def draw_flashlight_border(screen, cone_points, color=(100, 150, 200)):
    """
    Desenha a borda do cone de luz usando Cohen-Sutherland para clipping.
    """
    drawPolygon(screen, cone_points, color)


def draw_flashlight_with_clipping(screen, objects_to_draw, cone_points, width, height):
    """
    Desenha objetos apenas dentro do cone de luz usando Cohen-Sutherland.
    
    Esta função demonstra o uso do algoritmo para recortar as linhas
    dos polígonos contra a área visível definida pelo cone.
    
    Args:
        screen: Surface do pygame
        objects_to_draw: Lista de dicionários com 'points' e 'color'
        cone_points: 3 pontos do triângulo de luz
        width, height: Dimensões da tela
    """
    window = get_flashlight_window(cone_points)
    
    for obj in objects_to_draw:
        points = obj.get('points', [])
        color = obj.get('color', (255, 255, 255))
        
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            
            visible, rx0, ry0, rx1, ry1 = cohen_sutherland(
                x0, y0, x1, y1,
                window[0], window[1], window[2], window[3]
            )
            
            if visible:
                DrawLineBresenham(screen, int(rx0), int(ry0), int(rx1), int(ry1), color)
