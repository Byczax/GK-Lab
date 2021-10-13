#!/usr/bin/env python3
'''
use arguments to select wanted piece, write without argument to get help menu
'''

import os
import sys

from glfw.GLFW import *

from OpenGL.GL import *
from OpenGL.GLU import *
import random as rand
import math
from enum import Enum

seed = rand.random()

selected_mode = 0
class Modes(Enum):
    TRIANGLE = 1
    RECTANGLE = 2
    DEFORMED_RECTANGLE = 3
    SIERPINSKI_CARPET = 4
    SIERPINSKI_TRIANGLE = 5
    MAZE = 6


def startup():
    update_viewport(None, 400, 400)
    glClearColor(0, 0, 0, 1.0)  # clear to color


def shutdown():
    pass


def colorful_triangle():
    glClear(GL_COLOR_BUFFER_BIT)  # clearing the frame in memory

    glColor3f(0.0, 1.0, 0.0)
    glBegin(GL_TRIANGLES)
    glVertex2f(-50.0, 0.0)
    glColor3f(0.0, 0.0, 1.0)
    glVertex2f(0.0, 50.0)
    glColor3f(1.0, 0.0, 0.0)
    glVertex2f(50.0, 0.0)
    glEnd()

    glFlush()  # send content to visualise


def simple_rectangle(x: int = 0, y: int = 0, a: int = 1, b: int = 1):
    # glColor3f(1.0, 0.5, 0.7)
    glBegin(GL_TRIANGLES)
    glVertex2f(x, y)
    glVertex2f(x, y+b)
    glVertex2f(x+a, y+b)
    glEnd()
    glBegin(GL_TRIANGLES)
    glVertex2f(x, y)
    glVertex2f(x+a, y+b)
    glVertex2f(x+a, y)
    glEnd()
    glFlush()  # send content to visualise


def deformed_rectangle(x: int = 0, y: int = 0, a: int = 1, b: int = 1, d: int = 0):
    glClear(GL_COLOR_BUFFER_BIT)  # clearing the frame in memory
    glColor3f(rand.random(), rand.random(), rand.random())
    glBegin(GL_TRIANGLES)
    glVertex2f(x-d, y-d)
    glVertex2f(x, y+a)
    glVertex2f(x+b, y)
    glEnd()
    glBegin(GL_TRIANGLES)
    glVertex2f(x+b, x)
    glVertex2f(x+b+d, y+a)
    glVertex2f(y, y+a)
    glEnd()
    glFlush()  # send content to visualise


def sierpinski_rectangle(x: int, y: int, a: int, b: int, deep: int = 5):
    glClear(GL_COLOR_BUFFER_BIT)  # clearing the frame in memory
    glColor3f(1, 1, 1)
    rectangles = [(x, y, a, b)]
    simple_rectangle(x, y, a, b)
    glColor3f(0, 0, 0)
    for _ in range(deep):
        new_rectangles = []
        for rect in rectangles:
            x, y = rect[0], rect[1]
            a = rect[2]/3
            b = rect[3]/3
            simple_rectangle(x+a, y+b, a, b)
            new_rectangles.append((x, y, a, b))
            new_rectangles.append((x+a, y, a, b))
            new_rectangles.append((x+2*a, y, a, b))
            new_rectangles.append((x, y+b, a, b))
            new_rectangles.append((x+2*a, y+b, a, b))
            new_rectangles.append((x, y+2*b, a, b))
            new_rectangles.append((x+a, y+2*b, a, b))
            new_rectangles.append((x+2*a, y+2*b, a, b))
        rectangles = new_rectangles
    glFlush()  # send content to visualise


def simple_triangle(x: int, y: int, a: int, invert: bool = False):
    glBegin(GL_TRIANGLES)
    glVertex2f(x-a/2, y)
    if invert:
        glVertex2f(x, y-(a*math.sqrt(3))/2)
    else:
        glVertex2f(x, y+(a*math.sqrt(3))/2)
    glVertex2f(x+a/2, y)
    glEnd()
    glFlush()  # send content to visualise


def sierpinski_triangle(x: int, y: int, a: int, deep: int = 5):
    glClear(GL_COLOR_BUFFER_BIT)  # clearing the frame in memory
    glColor3f(1, 1, 1)
    triangles = [(x, y, a)]
    simple_triangle(x, y, a, False)
    glColor3f(0, 0, 0)
    for _ in range(deep):
        new_triangles = []
        for tri in triangles:
            x = tri[0]
            a = tri[2]/2
            y = tri[1]+(a*math.sqrt(3))/2
            simple_triangle(x, y, a, True)
            new_triangles.append((x, y, a))
            new_triangles.append((x-a/2, y-(a*math.sqrt(3))/2, a))
            new_triangles.append((x+a/2, y-(a*math.sqrt(3))/2, a))
        triangles = new_triangles
    glFlush()  # send content to visualise


def maze(x: int, y: int, a: int, b: int, field_size: int):
    rand.seed(seed)
    max_removal = 1
    glClear(GL_COLOR_BUFFER_BIT)  # clearing the frame in memory
    glColor3f(0, 1, 1)
    simple_rectangle(x-field_size, y-field_size,
                     (a+field_size)*2, (b+field_size)*2)
    glColor3f(1, 1, 1)
    for i in range(0, a-1, field_size):
        for j in range(0, b-1, field_size):
            simple_rectangle(i*2+x, j*2+y, field_size, field_size)
    for i in range(0, a, field_size):
        for j in range(0, b-field_size, field_size):
            if not rand.randint(0, max_removal):
                simple_rectangle(i*2+x, j*2+y+field_size,
                                 field_size, field_size)
    for i in range(0, a-field_size, field_size):
        for j in range(0, b, field_size):
            if not rand.randint(0, max_removal):
                simple_rectangle(i*2+x+field_size, j*2+y,
                                 field_size, field_size)
    glFlush()  # send content to visualise


def update_viewport(window, width, height):
    if width == 0:
        width = 1
    if height == 0:
        height = 1
    aspect_ratio = width / height

    glMatrixMode(GL_PROJECTION)
    glViewport(0, 0, width, height)
    glLoadIdentity()

    if width <= height:
        glOrtho(-100.0, 100.0, -100.0 / aspect_ratio, 100.0 / aspect_ratio,
                1.0, -1.0)
    else:
        glOrtho(-100.0 * aspect_ratio, 100.0 * aspect_ratio, -100.0, 100.0,
                1.0, -1.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def render():
    global selected_mode
    '''
    Uncomment what we want, comment on the rest, otherwise it will overlap
    '''
    if selected_mode == 1:
        colorful_triangle()
    elif selected_mode == 2:
        simple_rectangle(-55, -55, 120, 100)
    elif selected_mode == 3:
        deformed_rectangle(-55, -55, 120, 100, 10)
    elif selected_mode == 4:
        sierpinski_rectangle(-95, -95, 190, 190, 5)
    elif selected_mode == 5:
        sierpinski_triangle(0, -80, 200, 8)
    elif selected_mode == 6:
        maze(-90, -90, 90, 90, 4)


def main():
    global selected_mode

    if len(sys.argv) < 2:
        print('\033[1;32m')
        print("Usage: python.exe " + sys.argv[0] + " <mode>")
        print("Select run mode with argument:\n")
        print("3.0 - Simple triangle")
        print("3.5 - Simple rectangle")
        print("4.0 - Deformed rectangle")
        print("4.5 - Sierpinski carpet")
        print("5.0 - Sierpinski triangle")
        print("Extra - Maybe maze")
        print('\033[1;m')
        sys.exit(0)
    elif sys.argv[1] == "3.0":
        selected_mode = 1
    elif sys.argv[1] == "3.5":
        selected_mode = 2
    elif sys.argv[1] == "4.0":
        selected_mode = 3
    elif sys.argv[1] == "4.5":
        selected_mode = 4
    elif sys.argv[1] == "5.0":
        selected_mode = 5
    elif sys.argv[1].lower() == "extra":
        selected_mode = 6
        
    if not glfwInit():
        sys.exit(-1)

    # create window
    window1 = glfwCreateWindow(400, 400, __file__, None, None)

    if not window1:
        glfwTerminate()
        sys.exit(-1)

    glfwMakeContextCurrent(window1)  # set active window

    glfwSetFramebufferSizeCallback(window1, update_viewport)
    glfwSwapInterval(1)
    startup()

    while not glfwWindowShouldClose(window1):
        render()
        glfwSwapBuffers(window1)
        glfwPollEvents()
    shutdown()
    glfwTerminate()


if __name__ == '__main__':
    main()
