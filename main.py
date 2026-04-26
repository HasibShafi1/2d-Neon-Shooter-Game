import pygame
from pygame.locals import *
from game import Game

# Window dimensions
WIDTH, HEIGHT = 1280, 720

def main():
    pygame.init()
    
    # Set OpenGL attributes for Core Profile
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
    
    # Create an OpenGL window
    screen = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("2D Space Neon Shooter")
    
    clock = pygame.time.Clock()
    game = Game(WIDTH, HEIGHT)
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0 # Delta time in seconds
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEMOTION:
                game.mouse_x, game.mouse_y = event.pos
                    
        game.process_input(dt)
        game.update(dt)
        game.render()
        
        pygame.display.flip()
        
    pygame.quit()

if __name__ == "__main__":
    main()
