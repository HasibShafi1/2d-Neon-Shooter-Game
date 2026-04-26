import OpenGL.GL as gl

class Shader:
    def __init__(self, vertex_filepath, fragment_filepath):
        self.program = self._compile_program(vertex_filepath, fragment_filepath)

    def _read_source(self, filepath):
        with open(filepath, 'r') as f:
            return f.read()

    def _compile_shader(self, source, shader_type):
        shader = gl.glCreateShader(shader_type)
        gl.glShaderSource(shader, source)
        gl.glCompileShader(shader)

        # Check for compilation errors
        success = gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS)
        if not success:
            info_log = gl.glGetShaderInfoLog(shader)
            print(f"ERROR::SHADER::COMPILATION_FAILED\n{info_log.decode('utf-8')}")
        
        return shader

    def _compile_program(self, vertex_filepath, fragment_filepath):
        vertex_source = self._read_source(vertex_filepath)
        fragment_source = self._read_source(fragment_filepath)

        vertex_shader = self._compile_shader(vertex_source, gl.GL_VERTEX_SHADER)
        fragment_shader = self._compile_shader(fragment_source, gl.GL_FRAGMENT_SHADER)

        program = gl.glCreateProgram()
        gl.glAttachShader(program, vertex_shader)
        gl.glAttachShader(program, fragment_shader)
        gl.glLinkProgram(program)

        # Check for linking errors
        success = gl.glGetProgramiv(program, gl.GL_LINK_STATUS)
        if not success:
            info_log = gl.glGetProgramInfoLog(program)
            print(f"ERROR::SHADER::PROGRAM::LINKING_FAILED\n{info_log.decode('utf-8')}")

        gl.glDeleteShader(vertex_shader)
        gl.glDeleteShader(fragment_shader)

        return program

    def use(self):
        gl.glUseProgram(self.program)

    def set_mat4(self, name, mat):
        location = gl.glGetUniformLocation(self.program, name)
        gl.glUniformMatrix4fv(location, 1, gl.GL_TRUE, mat)
        
    def set_vec3(self, name, x, y, z):
        location = gl.glGetUniformLocation(self.program, name)
        gl.glUniform3f(location, x, y, z)

    def set_float(self, name, value):
        location = gl.glGetUniformLocation(self.program, name)
        gl.glUniform1f(location, value)
