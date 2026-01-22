"""
Módulo de Primitivas Gráficas
Funções para desenho de formas usando setPixel.
"""

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

def DrawLineBresenham(surface, x0, y0, x1, y1, color):
    # Converte para inteiros
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    
    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1

    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = y1 - y0

    ystep = 1 if dy >= 0 else -1
    dy = abs(dy)

    d = 2 * dy - dx
    incE = 2 * dy
    incNE = 2 * (dy - dx)

    y = y0
    for x in range(x0, x1 + 1):
        if steep:
            setPixel(surface, y, x, color)
        else:
            setPixel(surface, x, y, color)

        if d > 0:
            y += ystep
            d += incNE
        else:
            d += incE


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

def flood_fill_iterativo(superficie, x, y, cor_preenchimento, cor_borda):
    largura = superficie.get_width()
    altura = superficie.get_height()

    pilha = [(x, y)]

    while pilha:
        x, y = pilha.pop()

        if not (0 <= x < largura and 0 <= y < altura):
            continue

        cor_atual = superficie.get_at((x, y))[:3]

        if cor_atual == cor_borda or cor_atual == cor_preenchimento:
            continue

        setPixel(superficie, x, y, cor_preenchimento)

        pilha.append((x + 1, y))
        pilha.append((x - 1, y))
        pilha.append((x, y + 1))
        pilha.append((x, y - 1))

def drawTriangle(surface, point1, point2, point3, color):
    DrawLineBresenham(surface, point1[0], point1[1], point2[0], point2[1], color)
    DrawLineBresenham(surface, point2[0], point2[1], point3[0], point3[1], color)
    DrawLineBresenham(surface, point3[0], point3[1], point1[0], point1[1], color)

def drawPolygon(surface, points, color):
    n = len(points)
    for i in range(n):
        x0, y0 = points[i]
        x1, y1 = points[(i + 1) % n]
        DrawLineBresenham(surface, x0, y0, x1, y1, color)

def scanline_fill(surface, points, fill_color):
    ys = [p[1] for p in points]
    y_min = min(ys)
    y_max = max(ys)

    n = len(points)

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
                x_start = int(round(intersections_x[i]))
                x_end = int(round(intersections_x[i + 1]))

                for x in range(x_start, x_end + 1):
                    setPixel(surface, x, y, fill_color)

def drawRect(surface, top_left_x, top_left_y, width, height, color):
    points = [
        (top_left_x, top_left_y),
        (top_left_x + width, top_left_y),
        (top_left_x + width, top_left_y + height),
        (top_left_x, top_left_y + height)
    ]
    drawPolygon(surface, points, color)


def scanline_fill_gradient(surface, points, color_top, color_bottom):
    if not points:
        return
    
    ys = [p[1] for p in points]
    y_min = int(min(ys))
    y_max = int(max(ys))
    
    if y_max == y_min:
        return
    
    n = len(points)
    
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
        
        t = (y - y_min) / (y_max - y_min)
        
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * t)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * t)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * t)
        
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        
        gradient_color = (r, g, b)
        
        for i in range(0, len(intersections_x), 2):
            if i + 1 < len(intersections_x):
                x_start = int(round(intersections_x[i]))
                x_end = int(round(intersections_x[i + 1]))
                
                for x in range(x_start, x_end + 1):
                    setPixel(surface, x, y, gradient_color)
