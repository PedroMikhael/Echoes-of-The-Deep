import pygame
import primitives
import transforms
import math
import sys

BLUE_DARK = (10, 30, 60)
WHITE = (255, 255, 255)
OCEAN_DEEP = (15, 40, 70)

def gerar_uvs(poligono, escala=200):
    uvs = []
    for x, y in poligono:
        u = x / escala
        v = y / escala
        uvs.append((u % 1, v % 1))
    return uvs



def gerar_contorno_completo():
    pontos = [
        (100, 900),
        (100, 700),
        (300, 700),
        (700, 550),
        (700,200),
        (1100,200 ),
        (1100,300),
        (800, 300),
        (800, 650),
        (500, 850),
        (300, 850),
        (100, 900)
    ]
    return pontos



def gerar_magmaZone():
    zone = [(1100,200 ),(1200,150 ),(1300,100 ),(1400,200 ),(1400, 300),(1200,400),(1150,350),(1100,300 ),
            ]
    return zone

def gerar_SegundoPercurso():
    zone = [(1400,200),(1800, 200),(1200, 700),(1000,700),(1500,300),(1400,300)
            ]
    return zone

def gerar_ArenaInimigos():
    arena = [
        (1000,700),(800,800),(1000,900),(1400,900),(1400,800),(1200,700),
    ]
    return arena



def gerar_CorredorArenaParaObjeto():
    zone = [
        (1400, 900),(1600,900),(1600,1000),(1800,1000),(1800,700),(1600,700),(1600,800),(1400, 800),

       
    ]
    return zone

def fazer_espinhos(screen, x0, y0, x1, y1, lado,tamanho=20, espacamento=25, cor=(200, 200, 200)):

    dx = x1 - x0
    dy = y1 - y0
    comprimento = math.hypot(dx, dy)
    

    if comprimento == 0:
        return

    ux = dx / comprimento
    uy = dy / comprimento

    nx = -uy * lado
    ny = ux * lado

    quantidade = int(comprimento // espacamento)

    for i in range(quantidade):
        px = x0 + ux * i * espacamento
        py = y0 + uy * i * espacamento

        base1 = (
            px - ux * espacamento / 2,
            py - uy * espacamento / 2
        )
        base2 = (
            px + ux * espacamento / 2,
            py + uy * espacamento / 2
        )

        ponta = (
            px + nx * tamanho,
            py + ny * tamanho
        )

        primitives.drawPolygon(screen,[base1, base2, ponta],cor)
        primitives.scanline_fill(screen,[base1, base2, ponta],cor)

def gerar_caminho_errado():
    caminho = [
        (800,800),(400,900),(550,1000),(1000,900)
    ]
    return caminho
        
def fazer_magma(poligono, screen, textura):
    uvs = gerar_uvs(poligono, escala=150)
    primitives.scanline_texture(screen, poligono, uvs, textura)

def caminhoerrado_inicial():
    caminho = [(100, 700), (100, 200), (0, 200), (0, 0), (300, 0), (300, 200), (300, 700)]
    return caminho

def gerar_bifurcacao_direita():
    bifurcacao = [
        (300, 450),
        (500, 450),
        (550, 450),
        (550, 200),
        (500, 150),
        (400, 150),
        (350, 200),
        (350, 350),
        (300, 350),
    ]
    return bifurcacao

 
def drawMap(screen):
    textura_lava = pygame.image.load('imagens/lava.jfif').convert()

    caminho_errado = caminhoerrado_inicial()
    primitives.drawPolygon(screen, caminho_errado, OCEAN_DEEP)
    primitives.scanline_fill(screen, caminho_errado, OCEAN_DEEP)

    primitives.drawPolygon(screen, gerar_contorno_completo(), OCEAN_DEEP)
    primitives.scanline_fill(screen, gerar_contorno_completo(), OCEAN_DEEP)

    primitives.drawPolygon(screen, gerar_magmaZone(), OCEAN_DEEP)
    primitives.scanline_fill(screen, gerar_magmaZone(), OCEAN_DEEP)

    primitives.drawPolygon(screen, gerar_SegundoPercurso(), OCEAN_DEEP)
    primitives.scanline_fill(screen, gerar_SegundoPercurso(), OCEAN_DEEP)

    primitives.drawPolygon(screen, gerar_ArenaInimigos(), (50,50,50))
    primitives.scanline_fill(screen, gerar_ArenaInimigos(), (50,50,50))

    primitives.drawPolygon(screen, gerar_CorredorArenaParaObjeto(), OCEAN_DEEP)
    primitives.scanline_fill(screen, gerar_CorredorArenaParaObjeto(), OCEAN_DEEP)

    caminho_errado = gerar_caminho_errado()
    primitives.drawPolygon(screen, caminho_errado, OCEAN_DEEP)
    primitives.scanline_fill(screen, caminho_errado, OCEAN_DEEP)

    fazer_espinhos(screen, 700,550 , 300, 700, -1, tamanho=20, espacamento=30, cor=(0,0,0))
    fazer_espinhos(screen, 500, 850, 800, 650 , -1, tamanho=15, espacamento=30, cor=(0,0,0))

    fazer_magma([(1100,200 ),(1200,150 ),(1300,100 ),(1400,200 )],screen,textura_lava)
    fazer_magma([(1400, 300),(1200,400),(1150,350),(1100,300 )],screen,textura_lava)
    
    bifurc_dir = gerar_bifurcacao_direita()
    primitives.drawPolygon(screen, bifurc_dir, OCEAN_DEEP)
    primitives.scanline_fill(screen, bifurc_dir, OCEAN_DEEP)





def get_spawn_position():
    """Retorna a posição inicial do submarino (dentro da safe zone)"""
    return (200, 800)


def get_all_map_zones():
    """Retorna todos os polígonos do mapa para verificação de colisão"""
    return [
        gerar_contorno_completo(),
        gerar_magmaZone(),
        gerar_SegundoPercurso(),
        gerar_ArenaInimigos(),
        gerar_CorredorArenaParaObjeto(),
        caminhoerrado_inicial(),
        gerar_caminho_errado(),
        gerar_bifurcacao_direita(),
    ]


def point_in_polygon(x, y, polygon):
    """Verifica se um ponto está dentro de um polígono usando ray casting"""
    n = len(polygon)
    inside = False
    
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    
    return inside


def is_point_in_map(x, y):
    """Verifica se um ponto está dentro de qualquer zona do mapa"""
    zones = get_all_map_zones()
    for zone in zones:
        if point_in_polygon(x, y, zone):
            return True
    return False
