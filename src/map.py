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
        # Começa no canto inferior esquerdo
        (100, 900),
        # Lado esquerdo para cima
        (100, 700),
        # Topo da safe zone
        (300, 700),
        # Sobe na inclinação
        (700, 550),
        #sobrena vertical
        (700,200),
        #topo do mapa em direção ao magma
        (1100,200 ),
        #fecha o corredor horizontal
        (1100,300),
        #volta para 
        (800, 300),
        # Desce do outro lado?
        (800, 650),
        # Volta para base
        (500, 850),
        # Retorna ao início
        (300, 850),
        (100, 900)  # Fecha o polígono
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
        # topo
        (1000,700),(800,800),(1000,900),(1400,900),(1400,800),(1200,700),
    ]
    return arena



def gerar_CorredorArenaParaObjeto():
    zone = [
        # saída da arena
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
    caminho = [(100, 700),(100,200),(0,200),(0,0),(300,0),(300,200),(300, 700),]

    return caminho

 
def drawMap(screen):
    textura_lava = pygame.image.load('imagens/lava.jfif').convert()

    #primeiro percurso errado
    caminho_errado = caminhoerrado_inicial()
    primitives.drawPolygon(screen, caminho_errado, OCEAN_DEEP)
    primitives.scanline_fill(screen, caminho_errado, OCEAN_DEEP)

    #primeiro percurso
    primitives.drawPolygon(screen, gerar_contorno_completo(), OCEAN_DEEP)
    primitives.scanline_fill(screen, gerar_contorno_completo(), OCEAN_DEEP)

    #gerar poligono lava
    primitives.drawPolygon(screen, gerar_magmaZone(), OCEAN_DEEP)
    primitives.scanline_fill(screen, gerar_magmaZone(), OCEAN_DEEP)

    #segundo percurso
    primitives.drawPolygon(screen, gerar_SegundoPercurso(), OCEAN_DEEP)
    primitives.scanline_fill(screen, gerar_SegundoPercurso(), OCEAN_DEEP)

    #arena inimigos
    primitives.drawPolygon(screen, gerar_ArenaInimigos(), (50,50,50))
    primitives.scanline_fill(screen, gerar_ArenaInimigos(), (50,50,50))

    #corredor para pegar objeto
    primitives.drawPolygon(screen, gerar_CorredorArenaParaObjeto(), OCEAN_DEEP)
    primitives.scanline_fill(screen, gerar_CorredorArenaParaObjeto(), OCEAN_DEEP)

    #caminho errado
    caminho_errado = gerar_caminho_errado()
    primitives.drawPolygon(screen, caminho_errado, OCEAN_DEEP)
    primitives.scanline_fill(screen, caminho_errado, OCEAN_DEEP)

    #ESPINHOS CAVERNA
    fazer_espinhos(screen, 700,550 , 300, 700, -1, tamanho=20, espacamento=30, cor=(0,0,0))
    fazer_espinhos(screen, 500, 850, 800, 650 , -1, tamanho=15, espacamento=30, cor=(0,0,0))

    #MAGMA textura
    fazer_magma([(1100,200 ),(1200,150 ),(1300,100 ),(1400,200 )],screen,textura_lava)
    fazer_magma([(1400, 300),(1200,400),(1150,350),(1100,300 )],screen,textura_lava)





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
