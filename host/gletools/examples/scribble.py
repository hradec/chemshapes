# -*- coding: utf-8 -*-
from __future__ import with_statement

import pyglet
from gletools import (
    Projection, Framebuffer, Texture,
    interval, quad, Group, Matrix,
)
from gletools.gl import *

window = pyglet.window.Window()
projection = Projection(0, 0, window.width, window.height)
fbo = Framebuffer(
    Texture(window.width, window.height,
        data = [100,100,100,255]*(window.width*window.height)
    )
)

@window.event
def on_mouse_drag(x, y, rx, ry, button, modifier):
    if pyglet.window.mouse.LEFT == button:
        glColor4f(1,1,1,1)
        glLineWidth(3)
        with fbo:
            glBegin(GL_LINES)
            glVertex3f(x, y, 0)
            glVertex3f(x-rx, y-ry, 0)
            glEnd()

rotation = 0.0
@interval(0.03)
def simulate(delta):
    global rotation
    rotation += 40.0 * delta
    
@window.event
def on_draw():
    window.clear()
    with Group(fbo.textures[0], projection, Matrix):
        glTranslatef(0, 0, -3)
        glRotatef(-45, 1, 0, 0)
        glRotatef(rotation, 0.0, 0.0, 1.0)
        quad(scale=2)

if __name__ == '__main__':
    glEnable(GL_LINE_SMOOTH)
    pyglet.app.run()
