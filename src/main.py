import pygame
import sys
import math
import transforms
import primitives
from drone import drawDrone, drawDroneFilled
import map

BLUE_DARK = (10, 30, 60)
WHITE = (255, 255, 255)
CYAN = (0, 200, 255)
YELLOW = (255, 220, 50)
ORANGE = (255, 150, 50)

WIDTH = 1800
HEIGHT = 1000   

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Drone Submarino - Busca da Caixa Preta")
clock = pygame.time.Clock()

drone_x = WIDTH // 2
drone_y = HEIGHT // 2
drone_angle = 0
drone_speed = 3
rotation_speed = 4

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_LEFT]:
        drone_angle -= rotation_speed
    if keys[pygame.K_RIGHT]:
        drone_angle += rotation_speed
    
    if keys[pygame.K_UP]:
        rad = math.radians(drone_angle - 90)
        drone_x += math.cos(rad) * drone_speed
        drone_y += math.sin(rad) * drone_speed
    
    if keys[pygame.K_DOWN]:
        rad = math.radians(drone_angle - 90)
        drone_x -= math.cos(rad) * drone_speed
        drone_y -= math.sin(rad) * drone_speed
    
    drone_x = max(60, min(WIDTH - 60, drone_x))
    drone_y = max(60, min(HEIGHT - 60, drone_y))
    
    screen.fill(BLUE_DARK)
    
    drawDroneFilled(screen, int(drone_x), int(drone_y), drone_angle, YELLOW, CYAN, ORANGE)
    map.drawMap(screen)
    
    pygame.display.flip()
    clock.tick(60)
