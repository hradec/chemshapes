import pyglet
from pyglet.gl import *
from gletools import CubeMap, Projection, DepthTest
from contextlib import nested

class Bunny(object):
    def __init__(self):
        v3f = map(float, open('../meshes/bunny/vertices').read().strip().split())
        n3f = map(float, open('../meshes/bunny/normals').read().strip().split())
        indices = map(int, open('../meshes/bunny/faces').read().strip().split())
        count = len(v3f)/3
        self.display = pyglet.graphics.vertex_list_indexed(count, indices,
            ('v3f', v3f),
            ('n3f', n3f),
            ('t3f', n3f), #sets up texturing using the cubemap
        )

    def draw(self):
        self.display.draw(GL_TRIANGLES)

def simulate(delta, _):
    global rotation
    #rotation += 40.0 * delta

if __name__ == '__main__':
    cubemap = CubeMap.open('irradiance.png')
    pyglet.clock.schedule(simulate, 0.03)
    bunny = Bunny()
    rotation = 20.0
    config = Config(buffers=2, samples=4)
    window = pyglet.window.Window(config=config)
    projection = Projection(0, 0, window.width, window.height)

    @window.event
    def on_draw():
        glClearColor(1.0, 1.0, 1.0, 1.0)
        window.clear()
        glColor4f(1.0, 1.0, 1.0, 1.0)
        with nested(projection, cubemap, DepthTest):
            glPushMatrix()
            glTranslatef(0, 0, -10)
            glRotatef(20, 1, 0, 0)
            glRotatef(rotation, 0.0, 1.0, 0.0)
            glScalef(0.04, 0.04, 0.04)
            bunny.draw()
            glPopMatrix()

    pyglet.app.run()
