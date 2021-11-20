from ctypes import *

from pyglet.gl import *
from pyglet.window import key

from utils.euclid import *
from model.caliper import get_vertices, get_vertices_count


# Shaders (Vertex and Fragment shaders)
# vertex_shader_code = b"""
# # version 330 core
#
# layout(location=0) in vec3 position;
# layout(location=1) in vec3 normal;
#
# out vec3 vertexColor;
# out vec3 vertexNormal;
#
# uniform mat4 model;
# uniform mat4 view;
# uniform mat4 proj;
#
# void main() {
# 	vertexColor = vec3(1.0, 1.0, 1.0);
# 	vertexNormal = normal;
# 	gl_Position = proj * view * model * vec4(position, 1.0);
# }
# """
# fragment_shader_code = b"""
# # version 330 core
#
# in vec3 vertexColor;
# in vec3 vertexNormal;
#
# out vec4 fragmentColor;
#
# void main() {
# 	fragmentColor = vec4(vertexColor, 1.0);
# }
# """


def load_file(path):
    file = open(path, 'r')
    file_content = file.read()
    return file_content.encode('utf-8')


def create_shader(shader_type, path):
    shader_code = load_file(path)
    shader_code_in_c = cast(c_char_p(shader_code), POINTER(c_char))
    shader = glCreateShader(shader_type)
    glShaderSource(shader, 1, byref(shader_code_in_c), None)
    glCompileShader(shader)

    status = c_int(0)
    glGetShaderiv(shader, GL_COMPILE_STATUS, byref(status))

    if not status:
        info_log_length = c_int(0)
        glGetShaderiv(shader, GL_INFO_LOG_LENGTH, byref(info_log_length))
        program_error_message_in_c = create_string_buffer(info_log_length.value)
        glGetShaderInfoLog(shader, info_log_length, None, program_error_message_in_c)
        print(str(program_error_message_in_c.value))

    return shader


def create_shader_program():
    vertex_shader = create_shader(GL_VERTEX_SHADER, 'shaders/shader.vert')
    fragment_shader = create_shader(GL_FRAGMENT_SHADER, 'shaders/shader.frag')

    shader_program = glCreateProgram()
    glAttachShader(shader_program, vertex_shader)
    glAttachShader(shader_program, fragment_shader)
    glBindFragDataLocation(shader_program, 0, b"fragmentColor")
    glLinkProgram(shader_program)

    status = c_int(0)
    glGetProgramiv(shader_program, GL_LINK_STATUS, byref(status))

    if not status:
        info_log_length = c_int(0)
        glGetProgramiv(shader_program, GL_INFO_LOG_LENGTH, byref(info_log_length))
        program_error_message_in_c = create_string_buffer(info_log_length.value)
        glGetProgramInfoLog(shader_program, info_log_length, None, program_error_message_in_c)
        print(str(program_error_message_in_c.value))

    glUseProgram(shader_program)

    glDetachShader(shader_program, vertex_shader)
    glDetachShader(shader_program, fragment_shader)

    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)

    return shader_program


class OpenGLWindow(pyglet.window.Window):
    dt = 0

    camera_speed = 3.0
    mouse_speed = 0.00005

    camera_position = Vector3(0.0, 0.0, 5.0)
    camera_direction = Vector3(0.0, 0.0, -1.0)
    camera_up = Vector3(0.0, 1.0, 0.0)
    camera_fov = 45

    camera_pitch = 0
    camera_yaw = -90

    last_mouse_x = -1
    last_mouse_y = -1

    def __init__(self):
        super(OpenGLWindow, self).__init__(resizable=True)
        self.keyboard = key.KeyStateHandler()
        self.push_handlers(self.keyboard)
        self.initialize()

    def initialize(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POLYGON_SMOOTH)

        vao = GLuint()
        glEnableClientState(GL_VERTEX_ARRAY)
        glGenVertexArrays(1, pointer(vao))
        glBindVertexArray(vao)

        vertices = get_vertices()
        vertices_in_c = (GLfloat * len(vertices))(*vertices)

        vbo = GLuint()
        glGenBuffers(1, pointer(vbo))
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, sizeof(vertices_in_c), vertices_in_c, GL_STATIC_DRAW)

        shader_program = create_shader_program()

        # Making the link between vertex data and attributes
        position_attrib = 0
        glVertexAttribPointer(position_attrib, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(GLfloat), 0)
        glEnableVertexAttribArray(position_attrib)

        normal_attrib = 1
        glVertexAttribPointer(normal_attrib, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(GLfloat), 3 * sizeof(GLfloat))
        glEnableVertexAttribArray(normal_attrib)

        # Set up transformation matrices
        self.uniform_view = glGetUniformLocation(shader_program, b"view")
        self.uniform_projection = glGetUniformLocation(shader_program, b"proj")
        self.uniform_model = glGetUniformLocation(shader_program, b"model")

    def on_draw(self):
        glClearColor(0.3, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.handle_keyboard_inputs()

        view = Matrix4.new_look_at(
            self.camera_position,
            self.camera_position + self.camera_direction,
            self.camera_up
        )

        view = view[:]
        view_in_c = (GLfloat * len(view))(*view)
        glUniformMatrix4fv(self.uniform_view, 1, GL_FALSE, view_in_c)

        projection = Matrix4.new_perspective(math.radians(self.camera_fov), 4.0 / 3.0, 0.1, 100.0)
        projection = projection[:]
        projection_in_c = (GLfloat * len(projection))(*projection)
        glUniformMatrix4fv(self.uniform_projection, 1, GL_FALSE, projection_in_c)

        # Calculate transformation
        model = Matrix4()
        model.scale(0.02, 0.02, 0.02)
        model = model[:]
        model_in_c = (GLfloat * len(model))(*model)
        glUniformMatrix4fv(self.uniform_model, 1, GL_FALSE, model_in_c)

        glDrawArrays(GL_TRIANGLES, 0, get_vertices_count())

    def handle_keyboard_inputs(self):
        camera_speed = 4.5 * self.dt

        if self.keyboard[key.W]:
            self.camera_position += camera_speed * self.camera_direction

        if self.keyboard[key.S]:
            self.camera_position -= camera_speed * self.camera_direction

        if self.keyboard[key.A]:
            self.camera_position += camera_speed * Vector3.cross(self.camera_direction, self.camera_up).normalize()

        if self.keyboard[key.D]:
            self.camera_position -= camera_speed * Vector3.cross(self.camera_direction, self.camera_up).normalize()

    def on_mouse_motion(self, x, y, dx, dy):
        sensitivity = 0.005

        self.last_mouse_x = x if self.last_mouse_x == -1 else self.last_mouse_x
        self.last_mouse_y = y if self.last_mouse_y == -1 else self.last_mouse_y

        x_offset = sensitivity * (x - self.last_mouse_x)
        y_offset = sensitivity * (self.last_mouse_y - y)

        self.last_mouse_x = x
        self.last_mouse_y = y

        self.camera_yaw += x_offset
        self.camera_pitch += y_offset

        self.camera_pitch = min(89.0, self.camera_pitch)
        self.camera_pitch = max(-89.0, self.camera_pitch)

        self.camera_direction = Vector3(
            math.cos(math.radians(self.camera_yaw)) * math.cos(math.radians(self.camera_pitch)),
            math.sin(math.radians(self.camera_pitch)),
            math.sin(math.radians(self.camera_yaw)) * math.cos(math.radians(self.camera_pitch))
        )
        self.camera_direction.normalize()

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)

    def update(self, dt):
        self.dt = dt
        pass


if __name__ == '__main__':
    window = OpenGLWindow()
    pyglet.clock.schedule(window.update)
    pyglet.app.run()
