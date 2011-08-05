from __future__ import with_statement

import pyglet
from gletools import Projection, Lighting, Color, VertexObject
from gletools.gl import *
from util import Mesh, gl_init, ChangeValue, nested

window = pyglet.window.Window()
projection = Projection(0, 0, window.width, window.height, near=0.1, far=10)
angle = ChangeValue()

vbo = VertexObject(
    indices = [0, 1, 2],
    v4f     = [
         0.0, -1.0, 0.0, 1.0,
         1.0,  0.0, 0.0, 1.0,
        -1.0,  0.0, 0.0, 1.0,
    ],
    n3f     = [
        0.0, 0.0, -1.0,
        0.0, 0.0, -1.0,
        0.0, 0.0, -1.0,
    ]
)
 
@window.event
def on_draw():
    window.clear()
    
    with nested(projection, Lighting):
        glClearColor(0.0,0.0,0.0,0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glPushMatrix()
        glTranslatef(0, 0, -2)
        glRotatef(angle, 0.0, 1.0, 0.0)
        vbo.draw()
        glPopMatrix()

if __name__ == '__main__':
    gl_init()
    pyglet.app.run()
