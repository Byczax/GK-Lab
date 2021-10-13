#!/usr/bin/env python3
import sys

from glfw.GLFW import *

from OpenGL.GL import *
from OpenGL.GLU import *

from PIL import Image
import math

import beepy


# observation position
viewer = [0.0, -10.0, 10.0]

# observation variables
theta = 0.0
phi = 140.0
pix2angle = 1.0

# user input
left_mouse_button_pressed = 0
mouse_x_pos_old = 0
mouse_y_pos_old = 0
delta_x = 0
delta_y = 0

# light
mat_ambient = [1.0, 1.0, 1.0, 1.0]
mat_diffuse = [1.0, 1.0, 1.0, 1.0]
mat_specular = [1.0, 1.0, 1.0, 1.0]
mat_shininess = 20.0

light_ambient = [0.1, 0.1, 0.0, 1.0]
light_diffuse = [0.8, 0.8, 0.0, 1.0]
light_specular = [1.0, 1.0, 1.0, 1.0]
light_position = [0.0, -10.0, 0.0, 1.0]

att_constant = 1.0
att_linear = 0.05
att_quadratic = 0.001


# images
image_1 = Image.open("biernat.tga")
image_2 = Image.open("test.tga")
active_image = True
hide_wall = False
play_sound = False
active_egg = False
samples = 50
vertices = []

def load_texture(image):
    glTexImage2D(
        GL_TEXTURE_2D, 0, 3, image.size[0], image.size[1], 0,
        GL_RGB, GL_UNSIGNED_BYTE, image.tobytes("raw", "RGB", 0, -1)
    )


def startup():
    update_viewport(None, 400, 400)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
    glMaterialf(GL_FRONT, GL_SHININESS, mat_shininess)

    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, att_constant)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, att_linear)
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, att_quadratic)

    glShadeModel(GL_SMOOTH)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    glEnable(GL_TEXTURE_2D)
    glEnable(GL_CULL_FACE)
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    load_texture(image_1)


def shutdown():
    pass


def create_wall(start, end, reverse):
    if reverse:
        start, end = end, start
    glBegin(GL_TRIANGLES)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(start[0], start[1], start[2])
    glTexCoord2f(1.0, 0.0)
    glVertex3f(end[0], end[1], end[2])
    glTexCoord2f(0.5, 1.0)
    glVertex3f(0.0, 0.0, 5.0)
    glEnd()


def render(time):
    global theta
    global phi
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    gluLookAt(viewer[0], viewer[1], viewer[2],
              0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    if left_mouse_button_pressed:
        theta += delta_x * pix2angle
        phi += delta_y * pix2angle

    glRotatef(theta, 0.0, 1.0, 0.0)
    glRotatef(phi, 1.0, 0.0, 0.0)
    
    if not active_egg:
        render_pyramid()
    else:
        render_egg()
    
    glFlush()
    
def render_pyramid():
    glBegin(GL_TRIANGLE_STRIP)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-5.0, 0.0, -5.0)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(5.0, 0.0, -5.0)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-5.0, 0.0, 5.0)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(5.0, 0.0, 5.0)
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glTexCoord2f(0.5, 0.5)
    glVertex3f(0.0, 5.0, 0.0)
    
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-5.0, 0.0, 5.0)

    glTexCoord2f(1.0, 0.0)
    glVertex3f(5.0, 0.0, 5.0)

    glTexCoord2f(1.0, 1.0)
    glVertex3f(5.0, 0.0, -5.0)
    
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-5.0, 0.0, -5.0)

    if hide_wall:
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-5.0, 0.0, 5.0)
    glEnd()

def egg():
    def egg_calc(u: int, v: int):
        def egg_calc_x(u, v):
            return (-90 * u ** 5 + 225 * u ** 4 - 270 * u ** 3 + 180 * u ** 2 - 45 * u) * math.cos(math.pi * v)

        def egg_calc_y(u):
            return 160 * u ** 4 - 320 * u ** 3 + 160 * u ** 2

        def egg_calc_z(u, v):
            return (-90 * u ** 5 + 225 * u ** 4 - 270 * u ** 3 + 180 * u ** 2 - 45 * u) * math.sin(math.pi * v)
        return [egg_calc_x(u, v), egg_calc_y(u), egg_calc_z(u, v)]

    for v in range(samples):
        new_vertices = []
        for u in range(samples):
            new_u = u / (samples - 1)
            new_v = v / (samples - 1)
            new_vertices.append(egg_calc(new_u, new_v))
        vertices.append(new_vertices)

def render_egg():
    # draw method for egg
# def draw_triangle_strips():
    glBegin(GL_TRIANGLE_STRIP)
    for i in range(samples - 1):
        new_v =( i / samples + 1)
        new_v2 = ( (i+1) / samples + 1)
        # glTexCoord2f(new_v, 0)
        glVertex3fv(vertices[i][0])
        # glTexCoord2f(new_v+1, 0)
        glVertex3fv(vertices[i+1][0])
        # glTexCoord3fv(vertices[i+1][0])
        for j in range(1, samples):
            new_u =-( j / samples + 1)*2
            
            if j/samples < 0.5:
                glTexCoord2f(new_v2, new_u)
                glVertex3fv(vertices[i+1][j])
                # glTexCoord3fv(vertices[i+1][j])
                # new_v = ( (i+1) / samples + 1)
                glTexCoord2f(new_v, new_u)
                glVertex3fv(vertices[i][j])
                # glTexCoord3fv(vertices[i][j])
            else:
                # new_v = -(samples/i)
                # new_u =-( samples /j + 1)
                glTexCoord2f(new_v, new_u)
                glVertex3fv(vertices[i][j])
                # glTexCoord3fv(vertices[i][j])
                # new_v = ( (i+1) / samples + 1)
                glTexCoord2f(new_v2, new_u)
                glVertex3fv(vertices[i+1][j])
                # glTexCoord3fv(vertices[i+1][j])
    glEnd()

def update_viewport(window, width, height):
    global pix2angle
    pix2angle = 360.0 / width

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(70, 1.0, 0.1, 300.0)

    if width <= height:
        glViewport(0, int((height - width) / 2), width, width)
    else:
        glViewport(int((width - height) / 2), 0, height, height)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def keyboard_key_callback(window, key, scancode, action, mods):
    global hide_wall
    global active_image
    global play_sound
    global active_egg
    if key == GLFW_KEY_ESCAPE and action == GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE)
    if key == GLFW_KEY_W and action == GLFW_PRESS:
        hide_wall = not hide_wall
        play_sound = True
    if key == GLFW_KEY_T and action == GLFW_PRESS:
        active_image = not active_image
        if active_image:
            load_texture(image_1)
        else:
            load_texture(image_2)
    if key == GLFW_KEY_C and action == GLFW_PRESS:
        active_egg = not active_egg


def mouse_motion_callback(window, x_pos, y_pos):
    global delta_x
    global delta_y
    global mouse_x_pos_old
    global mouse_y_pos_old

    delta_x = x_pos - mouse_x_pos_old
    delta_y = y_pos - mouse_y_pos_old
    mouse_x_pos_old = x_pos
    mouse_y_pos_old = y_pos


def mouse_button_callback(window, button, action, mods):
    global left_mouse_button_pressed

    if button == GLFW_MOUSE_BUTTON_LEFT and action == GLFW_PRESS:
        left_mouse_button_pressed = 1
    else:
        left_mouse_button_pressed = 0

def make_a_sound():
    global play_sound
    if play_sound:
        beepy.beep(sound=3)
        play_sound = False

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
    egg()
    startup()
    while not glfwWindowShouldClose(window):
        render(glfwGetTime())
        glfwSwapBuffers(window)
        glfwPollEvents()
        make_a_sound()
    shutdown()

    glfwTerminate()


if __name__ == '__main__':
    main()
