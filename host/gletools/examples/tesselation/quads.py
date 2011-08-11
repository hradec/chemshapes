import pyglet
from pyglet.gl import *

from gletools import ShaderProgram, VertexObject, Matrix

window = pyglet.window.Window()
rotation = 0.0

vbo = VertexObject(
    indices = [0, 1, 2, 3],
    v4f     = [
        +1, +1, 0, 1,
        +1, -1, 0, 1,
        -1, -1, 0, 1,
        -1, +1, 0, 1,
    ],
)

program = ShaderProgram.open('quads.shader',
    inner_level = 1.0,
    outer_level = 1.0,
    simple      = False,
)

def simulate(delta, _):
    global rotation
    rotation += 0.1 * delta

pyglet.clock.schedule(simulate, 0.03)

@window.event
def on_draw():
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    window.clear()

    program.vars.modelview = Matrix().translate(0,0,-3).rotatex(-0.175).rotatez(rotation)
    program.vars.projection = Matrix.perspective(window.width, window.height, 60, 0.1, 100.0)

    with program:
        glPatchParameteri(GL_PATCH_VERTICES, 4);
        vbo.draw(GL_PATCHES)

if __name__ == '__main__':
    pyglet.app.run()
