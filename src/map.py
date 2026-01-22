import pygame
import primitives
import transforms
import math
import sys

BLUE_DARK = (10, 30, 60)
WHITE = (255, 255, 255)



def gerar_contorno_completo():
    pontos = [
        # Começa no canto inferior esquerdo
        (100, 900),
        # Lado esquerdo para cima
        (100, 700),
        # Topo da safe zone
        (300, 700),
        # Conecta ao corredor
        (300, 750),
        # Continua para direita
        (500, 750),
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

def fazer_espinhos():
    ...



def drawMap(screen):
    primitives.drawPolygon(screen, gerar_contorno_completo(), (0,0,0))
    primitives.scanline_fill(screen, gerar_contorno_completo(), (0,0,0))
    primitives.drawPolygon(screen, gerar_magmaZone(), (255,0,0))
    primitives.scanline_fill(screen, gerar_magmaZone(), (255,0,0))
    primitives.drawPolygon(screen, gerar_SegundoPercurso(), (0,0,0))
    primitives.scanline_fill(screen, gerar_SegundoPercurso(), (0,0,0))
    primitives.drawPolygon(screen, gerar_ArenaInimigos(), (50,50,50))
    primitives.scanline_fill(screen, gerar_ArenaInimigos(), (50,50,50))
    primitives.drawPolygon(screen, gerar_CorredorArenaParaObjeto(), (0,0,0))
    primitives.scanline_fill(screen, gerar_CorredorArenaParaObjeto(), (0,0,0))
    

def spawn_zone():
    return (250, 100)   #coordenadas x e y do centro da zona de spawn


# Definição das zonas do mapa
def getZone():
    return {
        "safe": SAFE_ZONE,
        "magma": MAGMA_ZONE,
        "nest": NEST_ZONE,
        "goal": GOAL_ZONE
    }


def getGoalZone():
    return GOAL_ZONE

def getMagmaZone():
    return MAGMA_ZONE

def getSafeZone():
    return SAFE_ZONE

def getNestZone(): 
    return NEST_ZONE