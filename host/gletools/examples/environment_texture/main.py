from __future__ import with_statement
from contextlib import nested

import pyglet
from gletools import Texture, Projection, DepthTest, SphereMapping, Matrix
from gletools.gl import *

rotation = 0
background = Texture.open('background.jpg')
sphere_map = Texture.open('sphere_map.jpg')
config = Config(buffers=2, samples=4)
window = pyglet.window.Window(width=background.width, height=background.height, config=config)
projection = Projection(0, 0, window.width, window.height)

def quad(min=0.0, max=1.0):
    glBegin(GL_QUADS)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(max, max, 0.0)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(max, min, 0.0)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(min, min, 0.0)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(min, max, 0.0)
    glEnd()

def simulate(delta, _):
    global rotation
    rotation += 40.0 * delta

class Bunny(object):
    def __init__(self):
        v3f = map(float, open('../meshes/bunny/vertices').read().strip().split())
        n3f = map(float, open('../meshes/bunny/normals').read().strip().split())
        indices = map(int, open('../meshes/bunny/faces').read().strip().split())
        count = len(v3f)/3
        self.display = pyglet.graphics.vertex_list_indexed(count, indices,
            ('v3f', v3f),
            ('n3f', n3f),
        )

    def draw(self):
        self.display.draw(GL_TRIANGLES)

pyglet.clock.schedule(simulate, 0.03)
bunny = Bunny()
    
@window.event
def on_draw():
    window.clear()
    background.draw()
    with nested(projection, sphere_map, Matrix, SphereMapping, DepthTest):
        glTranslatef(0, 0, -10)
        glRotatef(20, 1, 0, 0)
        glRotatef(rotation, 0.0, 1.0, 0.0)
        glScalef(0.04, 0.04, 0.04)
        bunny.draw()

if __name__ == '__main__':
    pyglet.app.run()
