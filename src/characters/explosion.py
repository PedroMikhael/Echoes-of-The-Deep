import math
import random
from primitives import drawCircle, drawPolygon, scanline_fill
from transforms import apply_transform, get_rotation_matrix, get_translation_matrix

class ExplosionParticle:
    def __init__(self, x, y):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 5)

        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(20, 40)
        self.radius = random.randint(2, 4)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def alive(self):
        return self.life > 0

class ExplosionFragment:
    def __init__(self, x, y):
        self.points = [
            (-12, -8),
            (12, -8),
            (0, 14)
        ]

        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.2, 2.5)

        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.rotation = random.uniform(0, 2 * math.pi)
        self.rotation_speed = random.uniform(-0.2, 0.2)
        self.life = random.randint(50, 80)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.rotation_speed
        self.life -= 1

    def alive(self):
        return self.life > 0

def draw_explosion(surface, explosion, camera_x=0, camera_y=0):
    """Desenha a explosão na tela com offset da câmera."""
    screen_x = explosion['x'] - camera_x
    screen_y = explosion['y'] - camera_y
    
    if explosion['frame'] < 8:
        drawCircle(
            surface,
            int(screen_x),
            int(screen_y),
            explosion['frame'] * 6,
            (255, 240, 200)
        )

    for p in explosion['particles']:
        px = p.x - camera_x
        py = p.y - camera_y
        drawCircle(surface, int(px), int(py), p.radius, (255, 150, 50))

    for f in explosion['fragments']:
        rotated = apply_transform(f.points, get_rotation_matrix(f.rotation))
        fx = f.x - camera_x
        fy = f.y - camera_y
        transformed = apply_transform(rotated, get_translation_matrix(fx, fy))
 
        drawPolygon(surface, transformed, (160, 160, 160))
        scanline_fill(surface, transformed, (160, 160, 160))

def create_explosion(x, y):
    return {
        'x': x,
        'y': y,
        'frame': 0,
        'particles': [ExplosionParticle(x, y) for _ in range(25)],
        'fragments': [ExplosionFragment(x, y) for _ in range(8)]
    }



def update_explosion(explosion):
    explosion['frame'] += 1

    for p in explosion['particles']:
        p.update()
    explosion['particles'] = [p for p in explosion['particles'] if p.alive()]

    for f in explosion['fragments']:
        f.update()
    explosion['fragments'] = [f for f in explosion['fragments'] if f.alive()]

    return explosion['frame'] < 60
