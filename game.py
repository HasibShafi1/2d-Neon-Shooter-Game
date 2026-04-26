import pygame
import OpenGL.GL as gl
import numpy as np
import math
import random
from shader import Shader
from entity import Player, Projectile, Particle, Enemy, check_collision
from ui import TextRenderer
from sound import SoundManager

def ortho_matrix(left, right, bottom, top, near=-1.0, far=1.0):
    return np.array([
        [2.0/(right-left), 0, 0, -(right+left)/(right-left)],
        [0, 2.0/(top-bottom), 0, -(top+bottom)/(top-bottom)],
        [0, 0, -2.0/(far-near), -(far+near)/(far-near)],
        [0, 0, 0, 1]
    ], dtype=np.float32)

class GameState:
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2

class Game:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE)
        gl.glClearColor(0.05, 0.0, 0.1, 1.0)
        gl.glLineWidth(2.0)
        
        self.shader = Shader("shaders/neon.vert", "shaders/neon.frag")
        
        projection = ortho_matrix(0, self.width, self.height, 0)
        self.shader.use()
        self.shader.set_mat4("projection", projection)
        
        self.text_renderer = TextRenderer(projection)
        self.sound_manager = SoundManager()
        
        self.state = GameState.MENU
        self.score = 0
        
        self.mouse_x = width / 2
        self.mouse_y = height / 2

        self.reset_game()

    def reset_game(self):
        self.player = Player(self.width / 2, self.height / 2)
        self.projectiles = []
        self.particles = []
        self.enemies = []
        self.shoot_cooldown = 0.0
        self.enemy_spawn_timer = 2.0
        self.score = 0
        self.lives = 3
        self.invulnerable_timer = 0.0

    def process_input(self, dt):
        keys = pygame.key.get_pressed()
        
        if self.state == GameState.MENU:
            if keys[pygame.K_SPACE]:
                self.state = GameState.PLAYING
                self.reset_game()
        
        elif self.state == GameState.GAME_OVER:
            if keys[pygame.K_SPACE]:
                self.state = GameState.PLAYING
                self.reset_game()
                
        elif self.state == GameState.PLAYING:
            dx, dy = 0.0, 0.0
            if keys[pygame.K_w]: dy -= 1.0
            if keys[pygame.K_s]: dy += 1.0
            if keys[pygame.K_a]: dx -= 1.0
            if keys[pygame.K_d]: dx += 1.0
            
            if dx != 0 or dy != 0:
                length = math.hypot(dx, dy)
                self.player.apply_thrust(dx/length, dy/length, dt)
                self.spawn_thruster_particles()
            else:
                self.player.apply_friction(dt)

            # Mouse Aiming
            self.player.angle = math.atan2(self.mouse_y - self.player.y, self.mouse_x - self.player.x)

            if self.shoot_cooldown > 0:
                self.shoot_cooldown -= dt
                
            if keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]:
                if self.shoot_cooldown <= 0:
                    self.shoot()
                    self.shoot_cooldown = 0.15

    def shoot(self):
        tip_x = self.player.x + math.cos(self.player.angle) * 15.0
        tip_y = self.player.y + math.sin(self.player.angle) * 15.0
        proj = Projectile(tip_x, tip_y, self.player.angle)
        self.projectiles.append(proj)
        self.sound_manager.play_shoot()

    def spawn_thruster_particles(self):
        # Particles go away from movement direction
        if math.hypot(self.player.vx, self.player.vy) > 10:
            mov_angle = math.atan2(self.player.vy, self.player.vx)
            back_x = self.player.x - math.cos(mov_angle) * 10.0
            back_y = self.player.y - math.sin(mov_angle) * 10.0
            
            spread = math.radians(random.uniform(-30, 30))
            p_angle = mov_angle + math.pi + spread
            speed = random.uniform(50, 150)
            vx = math.cos(p_angle) * speed
            vy = math.sin(p_angle) * speed
            
            p = Particle(back_x, back_y, vx, vy, (0.0, 1.0, 0.0), random.uniform(0.2, 0.5))
            self.particles.append(p)

    def spawn_explosion(self, x, y, color):
        for _ in range(15):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(100, 300)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            p = Particle(x, y, vx, vy, color, random.uniform(0.3, 0.8))
            self.particles.append(p)

    def spawn_enemy(self):
        # Spawn outside the screen
        side = random.randint(0, 3)
        if side == 0: # Top
            x, y = random.uniform(0, self.width), -20
        elif side == 1: # Right
            x, y = self.width + 20, random.uniform(0, self.height)
        elif side == 2: # Bottom
            x, y = random.uniform(0, self.width), self.height + 20
        else: # Left
            x, y = -20, random.uniform(0, self.height)
            
        self.enemies.append(Enemy(x, y))

    def update(self, dt):
        if self.state != GameState.PLAYING:
            return
            
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
            
        self.player.update(dt, self.width, self.height)
        
        # Enemy Spawning
        self.enemy_spawn_timer -= dt
        if self.enemy_spawn_timer <= 0:
            self.spawn_enemy()
            self.enemy_spawn_timer = max(0.5, 2.0 - (self.score * 0.05)) # Gets faster
        
        for p in self.projectiles:
            p.update(dt, self.width, self.height)
            
        for e in self.enemies:
            e.update(dt, self.width, self.height, self.player.x, self.player.y)
            
        for p in self.particles:
            p.update(dt, self.width, self.height)
            
        # Collisions
        for e in self.enemies:
            if not e.active: continue
            
            # Player hits enemy
            if self.invulnerable_timer <= 0 and check_collision(self.player, e):
                self.sound_manager.play_explosion()
                self.spawn_explosion(self.player.x, self.player.y, self.player.color)
                e.active = False
                self.lives -= 1
                if self.lives <= 0:
                    self.state = GameState.GAME_OVER
                else:
                    self.invulnerable_timer = 2.0
                break
                
            # Projectiles hit enemy
            for p in self.projectiles:
                if p.active and check_collision(p, e):
                    p.active = False
                    e.active = False
                    self.score += 10
                    self.sound_manager.play_enemy_hit()
                    self.spawn_explosion(e.x, e.y, e.color)
                    break
            
        # Clean up
        self.projectiles = [p for p in self.projectiles if p.active]
        self.enemies = [e for e in self.enemies if e.active]
        self.particles = [p for p in self.particles if p.active]

    def render(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        
        if self.state == GameState.PLAYING or self.state == GameState.GAME_OVER:
            self.shader.use()
            for p in self.particles: p.render(self.shader)
            for p in self.projectiles: p.render(self.shader)
            for e in self.enemies: e.render(self.shader)
            if self.state == GameState.PLAYING:
                if self.invulnerable_timer <= 0 or int(self.invulnerable_timer * 10) % 2 == 0:
                    self.player.render(self.shader)
                
            self.text_renderer.render_text(f"Score: {self.score}", 100, 30, color=(1.0, 1.0, 0.0), center=True)
            self.text_renderer.render_text(f"Lives: {self.lives}", 100, 70, color=(1.0, 0.2, 0.2), center=True)

        if self.state == GameState.MENU:
            self.text_renderer.render_text("NEON SPACE SHOOTER", self.width/2, self.height/2 - 50, color=(0.0, 1.0, 1.0))
            self.text_renderer.render_text("Press SPACE to Start", self.width/2, self.height/2 + 50, color=(1.0, 1.0, 1.0))
            
        elif self.state == GameState.GAME_OVER:
            self.text_renderer.render_text("GAME OVER", self.width/2, self.height/2 - 50, color=(1.0, 0.0, 0.0))
            self.text_renderer.render_text(f"Final Score: {self.score}", self.width/2, self.height/2 + 10, color=(1.0, 1.0, 0.0))
            self.text_renderer.render_text("Press SPACE to Restart", self.width/2, self.height/2 + 70, color=(1.0, 1.0, 1.0))
