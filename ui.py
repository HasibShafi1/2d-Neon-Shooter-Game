import pygame
import OpenGL.GL as gl
import numpy as np
from shader import Shader

def translation_matrix(tx, ty):
    return np.array([
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)

class TextRenderer:
    def __init__(self, projection):
        pygame.font.init()
        # Default font
        self.font = pygame.font.SysFont('Arial', 32, bold=True)
        self.shader = Shader("shaders/text.vert", "shaders/text.frag")
        self.shader.use()
        self.shader.set_mat4("projection", projection)
        
        self.vao = gl.glGenVertexArrays(1)
        self.vbo = gl.glGenBuffers(1)
        
    def render_text(self, text, x, y, color=(1.0, 1.0, 1.0), center=True):
        # Render text to pygame surface
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        width = text_surface.get_width()
        height = text_surface.get_height()
        
        # Create OpenGL texture
        texture = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, text_data)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        
        # Set up quad vertices (x, y, u, v)
        # We invert the Y coordinate for OpenGL's texture mapping (or flip the surface, which we did with True in tostring)
        vertices = np.array([
            0.0,   0.0,    0.0, 1.0,
            width, 0.0,    1.0, 1.0,
            width, height, 1.0, 0.0,
            0.0,   height, 0.0, 0.0,
        ], dtype=np.float32)
        
        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)
        
        # Position attribute
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 4 * 4, gl.ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(0)
        # Texture coordinate attribute
        gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 4 * 4, gl.ctypes.c_void_p(2 * 4))
        gl.glEnableVertexAttribArray(1)
        
        self.shader.use()
        
        # Setup model matrix
        if center:
            tx = x - width / 2
            ty = y - height / 2
        else:
            tx = x
            ty = y
            
        model = translation_matrix(tx, ty)
        self.shader.set_mat4("model", model)
        self.shader.set_vec3("textColor", color[0], color[1], color[2])
        
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
        
        gl.glBindVertexArray(self.vao)
        gl.glDrawArrays(gl.GL_TRIANGLE_FAN, 0, 4)
        
        gl.glBindVertexArray(0)
        gl.glDeleteTextures(1, [texture])
