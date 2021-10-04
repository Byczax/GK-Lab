#!/usr/bin/env python3
'''
Click `R` for Rotation mode
Click `C` for Camera mode
There is no mode for free movement (for now)
Program on 4.5 only :/
'''
import sys
from glfw.GLFW import *

from OpenGL.GL import *
from OpenGL.GLU import *

import math
from enum import Enum
viewer = [0.0, 0.0, 10.0]

theta = 0.0
phi = 0.0
pix2angle = 1.0
left_mouse_button_pressed = 0
right_mouse_button_pressed = 0
mouse_x_pos_old = 0
delta_x = 0
mouse_y_pos_old = 0
delta_y = 0
scale = 1.0

render_mode = 0


class Mode(Enum):
    DEFAULT = 0
    ROTATE = 1
    MOVE_CAM = 2


def startup():
    update_viewport(None, 400, 400)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)


def shutdown():
    pass


def axes():
    glBegin(GL_LINES)

    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-5.0, 0.0, 0.0)
    glVertex3f(5.0, 0.0, 0.0)

    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, -5.0, 0.0)
    glVertex3f(0.0, 5.0, 0.0)

    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, -5.0)
    glVertex3f(0.0, 0.0, 5.0)

    glEnd()


def example_object():
    glColor3f(1.0, 1.0, 1.0)

    quadric = gluNewQuadric()
    gluQuadricDrawStyle(quadric, GLU_LINE)
    glRotatef(90, 1.0, 0.0, 0.0)
    glRotatef(-90, 0.0, 1.0, 0.0)

    gluSphere(quadric, 1.5, 10, 10)

    glTranslatef(0.0, 0.0, 1.1)
    gluCylinder(quadric, 1.0, 1.5, 1.5, 10, 5)
    glTranslatef(0.0, 0.0, -1.1)

    glTranslatef(0.0, 0.0, -2.6)
    gluCylinder(quadric, 0.0, 1.0, 1.5, 10, 5)
    glTranslatef(0.0, 0.0, 2.6)

    glRotatef(90, 1.0, 0.0, 1.0)
    glTranslatef(0.0, 0.0, 1.5)
    gluCylinder(quadric, 0.1, 0.0, 1.0, 5, 5)
    glTranslatef(0.0, 0.0, -1.5)
    glRotatef(-90, 1.0, 0.0, 1.0)

    glRotatef(-90, 1.0, 0.0, 1.0)
    glTranslatef(0.0, 0.0, 1.5)
    gluCylinder(quadric, 0.1, 0.0, 1.0, 5, 5)
    glTranslatef(0.0, 0.0, -1.5)
    glRotatef(90, 1.0, 0.0, 1.0)

    glRotatef(90, 0.0, 1.0, 0.0)
    glRotatef(-90, 1.0, 0.0, 0.0)
    gluDeleteQuadric(quadric)


def eye(R, phi, theta):

    def x_eye(R, phi, theta):
        return R * math.cos(theta) * math.cos(phi)

    def y_eye(R, phi, theta):
        return R * math.sin(phi)

    def z_eye(R, phi, theta):
        return R * math.sin(theta) * math.cos(phi)

    return x_eye(R, phi, theta), y_eye(R, phi, theta), z_eye(R, phi, theta)


def instruction():
    def letter_r(x, y, width, height):
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y - height)
        glVertex2f(x, y + height)
        glVertex2f(x + width, y + height)
        glVertex2f(x + width, y)
        glVertex2f(x, y)
        glVertex2f(x + width, y - height)
        glVertex2f(x, y)
        glEnd()
        return x + width + 1

    def letter_c(x, y, width, height):
        glBegin(GL_LINE_LOOP)
        glVertex2f(x + width, y - height)
        glVertex2f(x, y - height)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x, y)
        glVertex2f(x, y - height)
        glEnd()
        return x + width + 1

    def letter_l(x, y, width, height):
        glBegin(GL_LINE_LOOP)
        glVertex2f(x + width, y - height)
        glVertex2f(x, y - height)
        glVertex2f(x, y)
        glVertex2f(x, y - height)
        glEnd()
        return x + width + 1

    def letter_i(x, y, height):
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y - 1/4*height)
        glVertex2f(x, y - height)
        glEnd()
        return x + 1

    def letter_k(x, y, width, height):
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y - height)
        glVertex2f(x, y - 1/2*height)
        glVertex2f(x + width, y - height)
        glVertex2f(x, y - 1/2*height)
        glVertex2f(x + width, y)
        glVertex2f(x, y - 1/2*height)
        glVertex2f(x, y)
        glEnd()
        return x + width + 1

    def separator_line(x, y, height):
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y + height)
        glVertex2f(x, y - height)
        glEnd()
        return x + 1

    glColor3f(1, 1, 1)
    # set letter position and size
    pos_x = -7
    pos_y = -1
    width = 5
    height = 4

    pos_x = letter_r(pos_x, pos_y, width,  height)
    pos_x = separator_line(pos_x, pos_y, height)
    pos_x = separator_line(pos_x, pos_y, height)
    pos_x = letter_c(pos_x, pos_y, width, height)

    glColor(1, 0, 0)
    # new letter position and size
    pos_x = -6.5
    pos_y = 6
    width = 2
    height = 2

    pos_x = letter_c(pos_x, pos_y, width, height)
    pos_x = letter_l(pos_x, pos_y, width, height)
    pos_x = letter_i(pos_x, pos_y, height)
    pos_x = letter_c(pos_x, pos_y, width, height)
    pos_x = letter_k(pos_x, pos_y, width, height)

    glFlush()  # send to display


def render(time):
    global theta
    global phi
    global scale
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    gluLookAt(viewer[0], viewer[1], viewer[2],
              0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    if render_mode == Mode.ROTATE:
        if left_mouse_button_pressed:
            theta += delta_x * pix2angle
            phi += delta_y * pix2angle
        if right_mouse_button_pressed:
            scale -= delta_x * pix2angle

        theta %= 360
        phi %= 360

        if scale < 0.5:
            scale = 0.5
        elif scale > 3:
            scale = 3

        glRotatef(theta, 0.0, 1.0, 0.0)
        glRotatef(phi, 1.0, 0.0, 0.0)
        glScalef(scale, scale, scale)

    elif render_mode == Mode.MOVE_CAM:
        if left_mouse_button_pressed:
            theta += delta_x * pix2radian
            phi += delta_y * pix2radian
        if right_mouse_button_pressed:
            scale += delta_x * pix2radian

        phi %= (2 * math.pi)
        theta %= (2 * math.pi)
        if scale < 0.01:
            scale = 0.01
        elif scale > 10:
            scale = 10

        x, y, z = eye(scale, phi, theta)
        top = -1
        if math.pi / 2 < phi < 3 * math.pi / 2:
            top = -1
        else:
            top = 1
        gluLookAt(x, y, z, 0, 0, 0, 0, top, 0)

    if render_mode == 0:
        instruction()
    else:
        axes()
        example_object()

    glFlush()


def update_viewport(window, width, height):
    global pix2angle
    global pix2radian
    pix2angle = 360.0 / width
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


def keyboard_key_callback(window, key, scancode, action, mods):
    global render_mode
    if key == GLFW_KEY_ESCAPE and action == GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE)
    elif key == GLFW_KEY_R and action == GLFW_PRESS:
        render_mode = Mode.ROTATE
    elif key == GLFW_KEY_C and action == GLFW_PRESS:
        render_mode = Mode.MOVE_CAM


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
        left_mouse_button_pressed = 1
    else:
        left_mouse_button_pressed = 0

    if button == GLFW_MOUSE_BUTTON_RIGHT and action == GLFW_PRESS:
        right_mouse_button_pressed = 1
    else:
        right_mouse_button_pressed = 0


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

    startup()
    while not glfwWindowShouldClose(window):
        render(glfwGetTime())
        glfwSwapBuffers(window)
        glfwPollEvents()
    shutdown()

    glfwTerminate()


if __name__ == '__main__':
    main()
