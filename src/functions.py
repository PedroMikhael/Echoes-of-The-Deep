import pygame
import math
import sys

def setPixel(surface, x_pos, y_pos, color):
    try:
        surface.set_at((int(x_pos), int(y_pos)), color)
    except IndexError:
        pass

def getPixel(surface, x_pos, y_pos):
    try:
        return surface.get_at((x_pos, y_pos))
    except IndexError:
        return None

def drawLine(surface, start_x, start_y, end_x, end_y, color):
    start_x, start_y = int(start_x), int(start_y)
    end_x, end_y = int(end_x), int(end_y)
    dx = abs(end_x - start_x)
    dy = abs(end_y - start_y)
    sx = 1 if start_x < end_x else -1
    sy = 1 if start_y < end_y else -1
    err = dx - dy

    x = start_x
    y = start_y

    while True:
        setPixel(surface, x, y, color)
        if x == end_x and y == end_y:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy

def drawCircle(surface, center_x, center_y, radius, color):
    x = 0
    y = radius
    d = 3 - 2 * radius
    drawCirclePixels(surface, center_x, center_y, x, y, color)
    while y >= x:
        x += 1
        if d > 0:
            y -= 1
            d = d + 4 * (x - y) + 10
        else:
            d = d + 4 * x + 6
        drawCirclePixels(surface, center_x, center_y, x, y, color)

def drawCirclePixels(surface, center_x, center_y, x_offset, y_offset, color):
    setPixel(surface, center_x + x_offset, center_y + y_offset, color)
    setPixel(surface, center_x - x_offset, center_y + y_offset, color)
    setPixel(surface, center_x + x_offset, center_y - y_offset, color)
    setPixel(surface, center_x - x_offset, center_y - y_offset, color)
    setPixel(surface, center_x + y_offset, center_y + x_offset, color)
    setPixel(surface, center_x - y_offset, center_y + x_offset, color)
    setPixel(surface, center_x + y_offset, center_y - x_offset, color)
    setPixel(surface, center_x - y_offset, center_y - x_offset, color)

def drawEllipse(surface, center_x, center_y, rx, ry, color):
    x = 0
    y = ry
    d1 = (ry * ry) - (rx * rx * ry) + (0.25 * rx * rx)
    dx = 2 * ry * ry * x
    dy = 2 * rx * rx * y

    # Region 1
    while dx < dy:
        drawEllipsePixels(surface, center_x, center_y, x, y, color)
        if d1 < 0:
            x += 1
            dx += 2 * ry * ry
            d1 += dx + (ry * ry)
        else:
            x += 1
            y -= 1
            dx += 2 * ry * ry
            dy -= 2 * rx * rx
            d1 += dx - dy + (ry * ry)

    # Region 2
    d2 = ((ry * ry) * ((x + 0.5) * (x + 0.5))) + ((rx * rx) * ((y - 1) * (y - 1))) - (rx * rx * ry * ry)
    
    while y >= 0:
        drawEllipsePixels(surface, center_x, center_y, x, y, color)
        if d2 > 0:
            y -= 1
            dy -= 2 * rx * rx
            d2 += (rx * rx) - dy
        else:
            y -= 1
            x += 1
            dx += 2 * ry * ry
            dy -= 2 * rx * rx
            d2 += dx - dy + (rx * rx)

def drawEllipsePixels(surface, center_x, center_y, x, y, color):
    setPixel(surface, center_x + x, center_y + y, color)
    setPixel(surface, center_x - x, center_y + y, color)
    setPixel(surface, center_x + x, center_y - y, color)
    setPixel(surface, center_x - x, center_y - y, color)

def floodFill(surface, start_x, start_y, target_color, replacement_color):
    try:
        current_color = surface.get_at((start_x, start_y))
    except IndexError:
        return
    
    if current_color == replacement_color:
        return
    
    if target_color is not None and current_color != target_color:
        return

    stack = [(start_x, start_y)]
    
    width, height = surface.get_size()

    while stack:
        x, y = stack.pop()
        
        try:
            if surface.get_at((x, y)) == current_color:
                setPixel(surface, x, y, replacement_color)
                
                if x + 1 < width: stack.append((x + 1, y))
                if x - 1 >= 0: stack.append((x - 1, y))
                if y + 1 < height: stack.append((x, y + 1))
                if y - 1 >= 0: stack.append((x, y - 1))
        except IndexError:
            pass

def drawTriangle(surface, point1, point2, point3, color):
    drawLine(surface, point1[0], point1[1], point2[0], point2[1], color)
    drawLine(surface, point2[0], point2[1], point3[0], point3[1], color)
    drawLine(surface, point3[0], point3[1], point1[0], point1[1], color)

def drawPolygon(surface, points_list, color):
    if len(points_list) < 2:
        return
    for i in range(len(points_list)):
        p1 = points_list[i]
        p2 = points_list[(i + 1) % len(points_list)]
        drawLine(surface, p1[0], p1[1], p2[0], p2[1], color)

def fillPolygon(surface, points_list, color):
    if not points_list:
        return

    min_y = int(min(p[1] for p in points_list))
    max_y = int(max(p[1] for p in points_list))

    for y in range(min_y, max_y + 1):
        intersections = []
        
        num_points = len(points_list)
        for i in range(num_points):
            p1 = points_list[i]
            p2 = points_list[(i + 1) % num_points]
            
            if (p1[1] <= y < p2[1]) or (p2[1] <= y < p1[1]):
                
                if p2[1] != p1[1]:
                    x_intersect = p1[0] + (y - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1])
                    intersections.append(x_intersect)
        
        intersections.sort()
        
        for i in range(0, len(intersections), 2):
            if i + 1 < len(intersections):
                x_start = int(intersections[i])
                x_end = int(intersections[i+1])
                
                for x in range(x_start, x_end + 1):
                    setPixel(surface, x, y, color)

def drawRect(surface, top_left_x, top_left_y, width, height, color):
    points = [
        (top_left_x, top_left_y),
        (top_left_x + width, top_left_y),
        (top_left_x + width, top_left_y + height),
        (top_left_x, top_left_y + height)
    ]
    drawPolygon(surface, points, color)


def mat_mul(A, B):
    """ Multiplies two 3x3 matrices. """
    C = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    for i in range(3):
        for j in range(3):
            for k in range(3):
                C[i][j] += A[i][k] * B[k][j]
    return C

def get_translation_matrix(tx, ty):
    return [
        [1, 0, tx],
        [0, 1, ty],
        [0, 0, 1]
    ]

def get_rotation_matrix(angle_degrees):
    rad = math.radians(angle_degrees)
    c = math.cos(rad)
    s = math.sin(rad)
    return [
        [c, -s, 0],
        [s, c, 0],
        [0, 0, 1]
    ]

def get_scale_matrix(sx, sy):
    return [
        [sx, 0, 0],
        [0, sy, 0],
        [0, 0, 1]
    ]

def apply_transform(points, matrix):
    """ 
    Applies a transformation matrix to a list of points.
    Returns the new list of transformed points.
    """
    new_points = []
    for x, y in points:
        vec = [x, y, 1]
        new_x = matrix[0][0]*vec[0] + matrix[0][1]*vec[1] + matrix[0][2]*vec[2]
        new_y = matrix[1][0]*vec[0] + matrix[1][1]*vec[1] + matrix[1][2]*vec[2]
        new_points.append((new_x, new_y))
    return new_points
