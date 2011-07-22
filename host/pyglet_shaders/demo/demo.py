#!/usr/bin/python

'''
This source draws a small (20 pixel) dark red square
The vertex shader scales and rotates it by 45 degrees to form a 300 pixel
diamond shape. The fragment shader colors it pale green.
'''

from sys import exit

from pyglet import app, gl
from pyglet.event import EVENT_HANDLED
from pyglet.window import Window

import fixpath; fixpath

from shader import FragmentShader, ShaderError, ShaderProgram, VertexShader


def read_source(fname):
    f = open(fname)
    try:
        src = f.read()
    finally:
        f.close()
    return src


def install_shaders(fragment, vertex):
    fsrc = read_source(fragment)
    fshader = FragmentShader([fsrc])

    vsrc = read_source(vertex)
    vshader = VertexShader([vsrc])

    shader = ShaderProgram(fshader, vshader)
    shader.use()


def on_resize(width, height):
    gl.glViewport(0, 0, width, height)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    gl.glOrtho(-width/2, width/2, -height/2, height/2, -1, 1)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    return EVENT_HANDLED


def draw_red_square():
    gl.glColor3ub(127, 0, 0)
    gl.glBegin(gl.GL_QUADS)
    gl.glVertex2f(-10, -10)
    gl.glVertex2f(10, -10)
    gl.glVertex2f(10, 10)
    gl.glVertex2f(-10, 10)
    gl.glEnd()


def on_draw(win):
    win.clear()
    draw_red_square()


def main():
    win = Window(fullscreen=True)
    win.on_resize = on_resize
    try:

        try:
            install_shaders('allGreen.frag', 'zoomRotate.vert')
        except ShaderError, e:
            print str(e)
            return 2
        
        win.on_draw = lambda: on_draw(win)
        app.run()
    finally:
        win.close()


if __name__ == '__main__':
    exit(main())

