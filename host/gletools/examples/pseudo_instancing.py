from __future__ import with_statement

import pyglet
from gletools import Projection, Lighting, Color, VertexObject
from gletools.gl import *
from util import Mesh, gl_init, ChangeValue, nested
from random import random

if __name__ == '__main__':
    window = pyglet.window.Window(vsync=False)
    projection = Projection(0, 0, window.width, window.height, near=100, far=700)
    angle = ChangeValue()
    bunny = Mesh('meshes/bunny')
    positions = [(random()*300-150, random()*300-150, random()*300-150) for _ in range(500)]

    fps = pyglet.clock.ClockDisplay()
 
    @window.event
    def on_draw():
        window.clear()
        
        with nested(projection, Lighting, bunny.vbo):
            glClearColor(0.0,0.0,0.0,0.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
           
            glPushMatrix()
            glTranslatef(0, 0, -400)
            glRotatef(angle, 0.0, 1.0, 0.0)
            for x, y, z in positions:
                glPushMatrix()
                glTranslatef(x, y, z)
                bunny.vbo.draw(bind=False)
                glPopMatrix()
            glPopMatrix()

        fps.draw()

    gl_init()
    pyglet.app.run()
