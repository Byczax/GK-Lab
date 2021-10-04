#!/usr/bin/env python3
'''
Everything is in the GUI
'''
import sys
from tkinter.constants import HORIZONTAL

from glfw.GLFW import *

from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random

import tkinter as tk

root = tk.Tk()  # declaration where is gui ?maybe?
vertices = []  # an array for model vertices
colors = []  # an array of random colors
samples = 15  # how many points per plane
parting = 11  # zoom, the larger the value, the further away
rotation = 50  # the speed of rotation of the model, the higher the faster
drawing_selection = ""
render_selection = ""
# !========================================! #


class app(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        root.geometry("500x300")  # setting the gui size
        self.create_widgets()

    def create_widgets(self):
        def exit():
            sys.exit(0)

        def when_click():
            global drawing_selection
            global render_selection
            global samples
            global rotation
            drawing_selection = selected_drawing_type.get()
            render_selection = selected_render.get()
            samples = self.detail_slider.get()
            rotation = self.rotation_speed.get()
            root.destroy()
        self.label = tk.Label(
            self, text="Hello there, general kenobi, select your desire options")
        self.label.pack()

        selected_drawing_type = tk.StringVar()
        selected_drawing_type.set("Dots")  # set default value
        self.option_menu = tk.OptionMenu(
            self, selected_drawing_type, "Dots", "Lines", "Triangles", "Triangle strips")
        self.option_menu.pack()

        selected_render = tk.StringVar()
        selected_render.set("Egg")
        self.render_menu = tk.OptionMenu(
            self, selected_render, "Egg", "Torus")
        self.render_menu.pack()

        self.detail_slider = tk.Scale(
            self, from_=1, to=50, label="details?", orient=HORIZONTAL)
        self.detail_slider.set(15)
        self.detail_slider.pack()

        self.rotation_speed = tk.Scale(
            self, from_=0, to=100, label="how faaaaaast?", orient=HORIZONTAL)
        self.rotation_speed.set(20)
        self.rotation_speed.pack()
        # buttons
        self.button = tk.Button(
            self, text="Accept selected values", command=when_click, fg="Green")
        self.button.pack()
        self.button = tk.Button(
            self, text="Exit", command=exit, fg="Red")
        self.button.pack()
# !========================================! #


def startup():
    update_viewport(None, 400, 400)
    glClearColor(0, 0, 0, 0)
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


def spin(angle):
    glRotatef(angle, 1.0, 0.0, 0.0)
    glRotatef(angle, 0.0, 5.0, 0.0)
    glRotatef(angle, 0.0, 0.0, -5.0)


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
        glOrtho(-parting, parting, -parting / aspect_ratio,
                parting / aspect_ratio, parting, -parting)
    else:
        glOrtho(-parting * aspect_ratio, parting *
                aspect_ratio, -parting, parting, parting, -parting)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

# !========================================! #


def egg_calc(u: int, v: int):
    def egg_calc_x(u, v):
        return (-90 * u ** 5 + 225 * u ** 4 - 270 * u ** 3 + 180 * u ** 2 - 45 * u) * math.cos(math.pi * v)

    def egg_calc_y(u):
        return 160 * u ** 4 - 320 * u ** 3 + 160 * u ** 2

    def egg_calc_z(u, v):
        return (-90 * u ** 5 + 225 * u ** 4 - 270 * u ** 3 + 180 * u ** 2 - 45 * u) * math.sin(math.pi * v)

    return [egg_calc_x(u, v), egg_calc_y(u), egg_calc_z(u, v)]


def torus_calc(u: int, v: int):
    R = 5
    r = 2

    def torus_calc_x(u, v):
        return (R + r * math.cos(2*math.pi*v)) * math.cos(2*math.pi*u)

    def torus_calc_y(u, v):
        return (R + r * math.cos(2*math.pi*v)) * math.sin(2*math.pi*u)

    def torus_calc_z(u, v):
        return r * math.sin(2*math.pi*v)

    return [torus_calc_x(u, v), torus_calc_y(u, v), torus_calc_z(u, v)]


def egg_render():
    for v in range(samples - 1):
        new_vertices = []
        new_colors = []
        for u in range(samples):
            new_u = u / (samples - 1)
            new_v = v / (samples - 1)
            new_vertices.append(egg_calc(new_u, new_v))
            new_colors.append(
                [random.random(), random.random(), random.random()])
        vertices.append(new_vertices)
        colors.append(new_colors)
    new_vertices = []
    new_colors = []
    # joining the last edge to the first so that there are no join artifacts
    for u in range(samples):
        new_u = u / (samples - 1)
        new_v = 1
        new_vertices.append(egg_calc(new_u, new_v))
        new_colors.append(colors[0][samples-1-u])
    vertices.append(new_vertices)
    colors.append(new_colors)


def torus_render():
    for v in range(samples - 1):
        new_vertices = []
        new_colors = []
        for u in range(samples):
            new_u = u / (samples - 1)
            new_v = v / (samples - 1)
            new_vertices.append(torus_calc(new_u, new_v))

            # repair of the vertical connection of the torus
            if u == samples-1:
                new_colors.append(new_colors[0])
            else:
                new_colors.append(
                    [random.random(), random.random(), random.random()])
        vertices.append(new_vertices)

        colors.append(new_colors)

    new_vertices = []
    new_colors = []
    # repair of the horizontal connection of the torus
    for u in range(samples):
        new_u = u / (samples - 1)
        new_v = 1
        new_vertices.append(torus_calc(new_u, new_v))
        new_colors.append(colors[0][u])
    vertices.append(new_vertices)
    colors.append(new_colors)


# !========================================! #

def draw_points():
    glBegin(GL_POINTS)
    for i in range(samples):
        for j in range(samples):
            glVertex3fv(vertices[i][j])
    glEnd()


def draw_lines():
    glBegin(GL_LINES)
    for i in range(samples - 1):
        for j in range(samples - 1):
            # vertical lines
            glVertex3fv(vertices[i][j])
            glVertex3fv(vertices[i+1][j])
            # horizontal lines
            glVertex3fv(vertices[i][j])
            glVertex3fv(vertices[i][j + 1])
    glEnd()


def draw_triangles():
    glBegin(GL_TRIANGLES)
    for i in range(samples - 1):
        for j in range(samples - 1):

            glColor(colors[i][j])
            glVertex3fv(vertices[i][j])
            glColor(colors[i+1][j])
            glVertex3fv(vertices[i+1][j])
            glColor(colors[i][j+1])
            glVertex3fv(vertices[i][j+1])

            glColor(colors[i][j+1])
            glVertex3fv(vertices[i][j+1])
            glColor(colors[i+1][j+1])
            glVertex3fv(vertices[i+1][j+1])
            glColor(colors[i+1][j])
            glVertex3fv(vertices[i+1][j])
    glEnd()


def draw_triangle_strips():
    glBegin(GL_TRIANGLE_STRIP)
    for i in range(samples - 1):
        glColor(colors[i][0])
        glVertex3fv(vertices[i][0])
        glColor(colors[i+1][0])
        glVertex3fv(vertices[i+1][0])
        for j in range(1, samples):
            glColor(colors[i][j])
            glVertex3fv(vertices[i][j])
            glColor(colors[i+1][j])
            glVertex3fv(vertices[i+1][j])
    glEnd()

# !========================================! #


def render(time):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    spin(time*rotation)
    axes()
    glColor(1, 1, 1)

    if drawing_selection == "Dots":
        draw_points()
    elif drawing_selection == "Lines":
        draw_lines()
    elif drawing_selection == "Triangles":
        draw_triangles()
    else:
        draw_triangle_strips()
    glFlush()


def main():
    app(master=root).mainloop()
    if not glfwInit():
        sys.exit(-1)

    window = glfwCreateWindow(400, 400, __file__, None, None)
    if not window:
        glfwTerminate()
        sys.exit(-1)

    glfwMakeContextCurrent(window)
    glfwSetFramebufferSizeCallback(window, update_viewport)
    glfwSwapInterval(1)

    if render_selection == "Egg":
        egg_render()
    elif render_selection == "Torus":
        torus_render()
    else:
        return
    startup()
    while not glfwWindowShouldClose(window):
        render(glfwGetTime())
        glfwSwapBuffers(window)
        glfwPollEvents()
    shutdown()

    glfwTerminate()


if __name__ == '__main__':
    main()
