import numpy as np
import OpenGL.GL as gl
import math

def translation_matrix(tx, ty):
    return np.array([
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)

def rotation_matrix(angle_rad):
    c = np.cos(angle_rad)
    s = np.sin(angle_rad)
    return np.array([
        [c, -s, 0, 0],
        [s,  c, 0, 0],
        [0,  0, 1, 0],
        [0,  0, 0, 1]
    ], dtype=np.float32)

def check_collision(e1, e2):
    # Simple circle-based collision
    dist = math.hypot(e1.x - e2.x, e1.y - e2.y)
    return dist < (e1.radius + e2.radius)

class Entity:
    def __init__(self, x, y, vertices, color, radius):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.angle = 0.0
        self.color = color # tuple (r,g,b)
        self.fill_color = (color[0]*0.1, color[1]*0.1, color[2]*0.1) # Dark version of neon color
        self.radius = radius
        self.vertices = np.array(vertices, dtype=np.float32)
        self.active = True
        
        self.vao = gl.glGenVertexArrays(1)
        self.vbo = gl.glGenBuffers(1)
        
        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, gl.GL_STATIC_DRAW)
        
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 2 * 4, gl.ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(0)
        
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)

    def update(self, dt, width, height):
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Screen wrapping with margin
        margin = 30.0
        if self.x > width + margin: self.x = -margin
        if self.x < -margin: self.x = width + margin
        if self.y > height + margin: self.y = -margin
        if self.y < -margin: self.y = height + margin

    def render(self, shader, draw_mode=gl.GL_LINE_LOOP):
        model = translation_matrix(self.x, self.y) @ rotation_matrix(self.angle)
        
        shader.set_mat4("model", model)
        
        # First draw filled center
        shader.set_vec3("neonColor", *self.fill_color)
        shader.set_float("intensity", 1.0)
        
        gl.glBindVertexArray(self.vao)
        if draw_mode != gl.GL_LINES: # Don't fill particles or projectiles
            gl.glDrawArrays(gl.GL_TRIANGLE_FAN, 0, len(self.vertices) // 2)
            
        # Then draw neon outline
        shader.set_vec3("neonColor", *self.color)
        shader.set_float("intensity", 1.5)
        gl.glDrawArrays(draw_mode, 0, len(self.vertices) // 2)
        
        gl.glBindVertexArray(0)
        
    def destroy(self):
        gl.glDeleteVertexArrays(1, [self.vao])
        gl.glDeleteBuffers(1, [self.vbo])

class Player(Entity):
    def __init__(self, x, y):
        # Center the triangle better around (0,0) for proper rotation
        vertices = [
            15.0, 0.0,
            -10.0, 10.0,
            -10.0, -10.0
        ]
        super().__init__(x, y, vertices, (0.0, 1.0, 1.0), 12.0) # Cyan, radius 12
        self.max_speed = 300.0
        self.acceleration = 600.0
        self.friction = 200.0

    def apply_thrust(self, dx, dy, dt):
        # Absolute directional thrust (WASD)
        self.vx += dx * self.acceleration * dt
        self.vy += dy * self.acceleration * dt
        
        # Cap speed
        speed = math.hypot(self.vx, self.vy)
        if speed > self.max_speed:
            self.vx = (self.vx / speed) * self.max_speed
            self.vy = (self.vy / speed) * self.max_speed

    def apply_friction(self, dt):
        speed = math.hypot(self.vx, self.vy)
        if speed > 0:
            drop = self.friction * dt
            new_speed = max(speed - drop, 0)
            self.vx = (self.vx / speed) * new_speed
            self.vy = (self.vy / speed) * new_speed

class Enemy(Entity):
    def __init__(self, x, y):
        # Octagon
        vertices = []
        for i in range(8):
            ang = i * (math.pi * 2 / 8)
            vertices.extend([math.cos(ang) * 15.0, math.sin(ang) * 15.0])
            
        super().__init__(x, y, vertices, (1.0, 0.5, 0.0), 15.0) # Orange, radius 15
        self.speed = 100.0
        
    def update(self, dt, width, height, player_x, player_y):
        # Chase player
        angle = math.atan2(player_y - self.y, player_x - self.x)
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed
        
        self.angle += dt * 2.0 # Spin
        super().update(dt, width, height)

class Projectile(Entity):
    def __init__(self, x, y, angle):
        vertices = [
            8.0, 0.0,
            -8.0, 0.0
        ]
        super().__init__(x, y, vertices, (1.0, 0.0, 1.0), 5.0) # Magenta, radius 5
        self.angle = angle
        speed = 800.0
        self.vx = math.cos(self.angle) * speed
        self.vy = math.sin(self.angle) * speed
        self.lifetime = 1.5
        self.age = 0.0

    def update(self, dt, width, height):
        super().update(dt, width, height)
        self.age += dt
        if self.age >= self.lifetime:
            self.active = False
            
    def render(self, shader):
        super().render(shader, draw_mode=gl.GL_LINES)

class Particle(Entity):
    def __init__(self, x, y, vx, vy, color, lifetime):
        vertices = [
            1.0, 1.0,
            -1.0, -1.0,
            1.0, -1.0,
            -1.0, 1.0
        ]
        super().__init__(x, y, vertices, color, 1.0)
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.age = 0.0

    def update(self, dt, width, height):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.age += dt
        if self.age >= self.lifetime:
            self.active = False
            
    def render(self, shader):
        model = translation_matrix(self.x, self.y)
        shader.set_mat4("model", model)
        shader.set_vec3("neonColor", *self.color)
        
        intensity = 1.0 - (self.age / self.lifetime)
        shader.set_float("intensity", intensity)
        
        gl.glBindVertexArray(self.vao)
        gl.glDrawArrays(gl.GL_LINES, 0, 4)
        gl.glBindVertexArray(0)
