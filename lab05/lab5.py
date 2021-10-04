#!/usr/bin/env python3
'''
Keyboard description

Keys 1-9:
R(1), G(2), B(3) ambient
R(4), G(5), B(6) diffuse
R(7), G(8), B(9) specular
Change this values with arrows (up and down)

Key N - Toggle Normal vectors

'''
import sys
from typing import List, Union

from glfw.GLFW import *

from OpenGL.GL import *
from OpenGL.GLU import *
import math


viewer = [0.0, 0.0, 10.0]

# egg
vertices = []
normals = []
samples = 15
# ====

# mode variable for changing values for lighting
selected_mode = 0
normals_mode = False

# position calculation
theta = 0.0
phi = 0.0
pix2angle = 1.0
pix2radian = 1.0

# user input
left_mouse_button_pressed = False
right_mouse_button_pressed = False
mouse_x_pos_old = 0
mouse_y_pos_old = 0
delta_x = 0
delta_y = 0


# object light parameters
mat_ambient = [1.0, 1.0, 1.0, 1.0]
mat_diffuse = [1.0, 1.0, 1.0, 1.0]
mat_specular = [1.0, 1.0, 1.0, 1.0]
mat_shininess = 20.0

# light parameters nr.1
light_ambient = [0.1, 0.1, 0.0, 1.0]
light_diffuse = [0.8, 0.8, 0.0, 1.0]
light_specular = [1.0, 1.0, 1.0, 1.0]
light_position = [5.0, 0.0, 0.0, 1.0]

# light parameters nr.2
light_diffuse2 = [0.8, 0.0, 1.0, 1.0]


# constants
att_constant = 1.0
att_linear = 0.05
att_quadratic = 0.001


# egg
def egg_render():

    # calculate points for egg
    def egg_calc(u: int, v: int):
        def egg_calc_x(u, v):
            return (-90 * u ** 5 + 225 * u ** 4 - 270 * u ** 3 + 180 * u ** 2 - 45 * u) * math.cos(math.pi * v)

        def egg_calc_y(u):
            return 160 * u ** 4 - 320 * u ** 3 + 160 * u ** 2 - 5

        def egg_calc_z(u, v):
            return (-90 * u ** 5 + 225 * u ** 4 - 270 * u ** 3 + 180 * u ** 2 - 45 * u) * math.sin(math.pi * v)

        return [egg_calc_x(u, v), egg_calc_y(u), egg_calc_z(u, v)]

    # calculate normals for egg
    def egg_normal_calc(u: int, v: int):
        def part_x_u(u, v):
            return (-450 * u ** 4 + 900 * u ** 3 - 810 * u ** 2 + 360 * u - 45) * math.cos(math.pi * v)

        def part_x_v(u, v):
            return math.pi * (90 * u ** 5 - 225 * u ** 4 + 270 * u ** 3 - 180 * u ** 2 + 45 * u) * math.sin(math.pi * v)

        def part_y_u(u):
            return 640 * u ** 3 - 960 * u ** 2 + 320 * u

        def part_y_v():
            return 0

        def part_z_u(u, v):
            return (-450 * u ** 4 + 900 * u ** 3 - 810 * u ** 2 + 360 * u - 45) * math.sin(math.pi * v)

        def part_z_v(u, v):
            return -math.pi * (90 * u ** 5 - 225 * u ** 4 + 270 * u ** 3 - 180 * u ** 2 + 45 * u) * math.cos(math.pi * v)

        def normalize(x, y, z):
            length = math.sqrt(x * x + y * y + z * z)
            if length != 0:
                x /= length
                y /= length
                z /= length
            elif u == 0 or u == 1:
                return [0, 1, 0]
            else:
                return [0, -1, 0]
            if u <= 0.5:
                x = -x
                y = -y
                z = -z
            return [x, y, z]

        x = part_y_u(u) * part_z_v(u, v) - part_z_u(u, v) * part_y_v()
        y = part_z_u(u, v) * part_x_v(u, v) - part_x_u(u, v) * part_z_v(u, v)
        z = part_x_u(u, v) * part_y_v() - part_y_u(u) * part_x_v(u, v)
        return normalize(x, y, z)

    # calculate data for egg
    for v in range(samples):
        new_vertices = []
        new_normals = []
        for u in range(samples):
            new_u = u / (samples - 1)
            new_v = v / (samples - 1)
            new_vertices.append(egg_calc(new_u, new_v))
            new_normals.append(egg_normal_calc(new_u, new_v))
        vertices.append(new_vertices)
        normals.append(new_normals)


# draw method for egg
def draw_triangle_strips():
    glBegin(GL_TRIANGLE_STRIP)
    for i in range(samples - 1):
        glNormal3fv(normals[i][0])
        glVertex3fv(vertices[i][0])
        glNormal3fv(normals[i+1][0])
        glVertex3fv(vertices[i+1][0])
        for j in range(1, samples):
            glNormal3fv(normals[i][j])
            glVertex3fv(vertices[i][j])
            glNormal3fv(normals[i+1][j])
            glVertex3fv(vertices[i+1][j])
    glEnd()


def normal_top(point, vector):
    x = point[0] - vector[0]
    y = point[1] - vector[1]
    z = point[2] - vector[2]
    return [x, y, z]


# draw method for normals for egg
def draw_normals():
    glBegin(GL_LINES)
    for i in range(samples - 1):
        glVertex3fv(normals[i][0])
        glVertex3fv(normal_top(normals[i][0], vertices[i][0]))

        glVertex3fv(normals[i+1][0])
        glVertex3fv(normal_top(normals[i+1][0], vertices[i+1][0]))
        for j in range(1, samples):
            glVertex3fv(normals[i][j])
            glVertex3fv(normal_top(normals[i][j], vertices[i][j]))
            glVertex3fv(normals[i+1][j])
            glVertex3fv(normal_top(normals[i+1][j], vertices[i+1][j]))
    glEnd()


# draw method for light sources
def draw_light_source(position: List[int]):
    glTranslate(-position[0], -position[1], -position[2])
    quadric = gluNewQuadric()
    gluQuadricDrawStyle(quadric, GLU_LINE)
    gluSphere(quadric, 0.5, 6, 5)
    gluDeleteQuadric(quadric)
    glTranslate(position[0], position[1], position[2])


# create light in model
def create_light(name, light_ambient, light_diffuse, light_specular, light_position):
    glLightfv(name, GL_AMBIENT, light_ambient)
    glLightfv(name, GL_DIFFUSE, light_diffuse)
    glLightfv(name, GL_SPECULAR, light_specular)
    glLightfv(name, GL_POSITION, light_position)

    glLightf(name, GL_CONSTANT_ATTENUATION, att_constant)
    glLightf(name, GL_LINEAR_ATTENUATION, att_linear)
    glLightf(name, GL_QUADRATIC_ATTENUATION, att_quadratic)

    glShadeModel(GL_SMOOTH)
    glEnable(GL_LIGHTING)
    glEnable(name)


def eye(R, phi, theta):

    def x_eye(R, phi, theta):
        return R * math.cos(theta) * math.cos(phi)

    def y_eye(R, phi, theta):
        return R * math.sin(phi)

    def z_eye(R, phi, theta):
        return R * math.sin(theta) * math.cos(phi)

    return x_eye(R, phi, theta), y_eye(R, phi, theta), z_eye(R, phi, theta)


# initialization!!!
def startup():
    global light_position
    update_viewport(None, 400, 400)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
    glMaterialf(GL_FRONT, GL_SHININESS, mat_shininess)

    create_light(GL_LIGHT0, light_ambient, light_diffuse,
                 light_specular, light_position)
    light_position = [-x for x in light_position]
    create_light(GL_LIGHT1, light_ambient, light_diffuse2,
                 light_specular, light_position)


def shutdown():
    pass


def calc_light_position(position: List[int], radius, phi, theta, name):
    position[0] = radius * math.cos(theta) * math.cos(phi)
    position[1] = radius * math.sin(phi)
    position[2] = radius * math.sin(theta) * math.cos(phi)
    glLightfv(name, GL_POSITION, position)


def render(time):
    global theta
    global phi
    global light_position

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    gluLookAt(viewer[0], viewer[1], viewer[2],
              0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    if left_mouse_button_pressed or right_mouse_button_pressed:
        theta += delta_x * pix2radian
        phi += delta_y * pix2radian

    phi %= (2 * math.pi)
    theta %= (2 * math.pi)

    if left_mouse_button_pressed:
        calc_light_position(light_position, 5, phi, theta, GL_LIGHT0)
        light_position = [-x for x in light_position]
        calc_light_position(light_position, 5, phi, theta, GL_LIGHT1)

    draw_light_source(light_position)
    light_position = [-x for x in light_position]
    draw_light_source(light_position)

    draw_triangle_strips()

    if normals_mode:
        draw_normals()
    glFlush()


def update_viewport(window, width, height):
    global pix2radian
    pix2radian = 2 * math.pi / width

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(70, 1.0, 0.1, 300.0)

    if width <= height:
        glViewport(0, int((height - width) / 2), width, width)
    else:
        glViewport(int((width - height) / 2), 0, height, height)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def fix_value_0_1(value):
    if value > 1:
        return 1.0
    elif value < 0:
        return 0.0
    return round(value, 1)


def change_color(value):
    if selected_mode == 1:
        light_ambient[0] = fix_value_0_1(light_ambient[0] + value)
    elif selected_mode == 2:
        light_ambient[1] = fix_value_0_1(light_ambient[1] + value)
    elif selected_mode == 3:
        light_ambient[2] = fix_value_0_1(light_ambient[2] + value)

    elif selected_mode == 4:
        light_diffuse[0] = fix_value_0_1(light_diffuse[0] + value)
    elif selected_mode == 5:
        light_diffuse[1] = fix_value_0_1(light_diffuse[1] + value)
    elif selected_mode == 6:
        light_diffuse[2] = fix_value_0_1(light_diffuse[2] + value)

    elif selected_mode == 7:
        light_specular[0] = fix_value_0_1(light_specular[0] + value)
    elif selected_mode == 8:
        light_specular[1] = fix_value_0_1(light_specular[1] + value)
    elif selected_mode == 9:
        light_specular[2] = fix_value_0_1(light_specular[2] + value)

    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

    print("==============================")
    print("ambient:  " + str(light_ambient))
    print("diffuse:  " + str(light_diffuse))
    print("specular: " + str(light_specular))


def keyboard_key_callback(window, key, scancode, action, mods):
    global selected_mode
    global normals_mode
    if key == GLFW_KEY_ESCAPE and action == GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE)
    if key == GLFW_KEY_0 and action == GLFW_PRESS:
        selected_mode = 0
    if key == GLFW_KEY_1 and action == GLFW_PRESS:
        selected_mode = 1
    if key == GLFW_KEY_2 and action == GLFW_PRESS:
        selected_mode = 2
    if key == GLFW_KEY_3 and action == GLFW_PRESS:
        selected_mode = 3
    if key == GLFW_KEY_4 and action == GLFW_PRESS:
        selected_mode = 4
    if key == GLFW_KEY_5 and action == GLFW_PRESS:
        selected_mode = 5
    if key == GLFW_KEY_6 and action == GLFW_PRESS:
        selected_mode = 6
    if key == GLFW_KEY_7 and action == GLFW_PRESS:
        selected_mode = 7
    if key == GLFW_KEY_8 and action == GLFW_PRESS:
        selected_mode = 8
    if key == GLFW_KEY_9 and action == GLFW_PRESS:
        selected_mode = 9
    if key == GLFW_KEY_UP and action == GLFW_PRESS:
        change_color(0.1)
    if key == GLFW_KEY_DOWN and action == GLFW_PRESS:
        change_color(-0.1)
    if key == GLFW_KEY_N and action == GLFW_PRESS:
        normals_mode = not normals_mode


def mouse_motion_callback(window, x_pos, y_pos):
    global delta_x
    global mouse_x_pos_old
    global delta_y
    global mouse_y_pos_old

    delta_x = x_pos - mouse_x_pos_old
    delta_y = y_pos - mouse_y_pos_old
    mouse_x_pos_old = x_pos
    mouse_y_pos_old = y_pos


def mouse_button_callback(window, button, action, mods):
    global left_mouse_button_pressed
    global right_mouse_button_pressed
    if button == GLFW_MOUSE_BUTTON_LEFT and action == GLFW_PRESS:
        left_mouse_button_pressed = True
    else:
        left_mouse_button_pressed = False
    if button == GLFW_MOUSE_BUTTON_RIGHT and action == GLFW_PRESS:
        right_mouse_button_pressed = True
    else:
        right_mouse_button_pressed = False


def main():
    if not glfwInit():
        sys.exit(-1)

    window = glfwCreateWindow(400, 400, __file__, None, None)
    if not window:
        glfwTerminate()
        sys.exit(-1)

    glfwMakeContextCurrent(window)
    glfwSetFramebufferSizeCallback(window, update_viewport)
    glfwSetKeyCallback(window, keyboard_key_callback)
    glfwSetCursorPosCallback(window, mouse_motion_callback)
    glfwSetMouseButtonCallback(window, mouse_button_callback)
    glfwSwapInterval(1)
    egg_render()
    startup()
    while not glfwWindowShouldClose(window):
        render(glfwGetTime())
        glfwSwapBuffers(window)
        glfwPollEvents()
    shutdown()

    glfwTerminate()


if __name__ == '__main__':
    main()
