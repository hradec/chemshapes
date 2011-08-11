import pyglet
from pyglet.gl import *

from gletools import ShaderProgram, VertexObject, Matrix, VBO

window = pyglet.window.Window()
rotation = 0.0

vbo = VBO(
    count       = 6,
    indices     = [0, 1, 2, 0, 2, 3],
    position_4  = [
        +1, +1, 0, 1,
        +1, -1, 0, 1,
        -1, -1, 0, 1,
        -1, +1, 0, 1,
    ],
)

program = ShaderProgram.open('triangles.shader',
    inner_level = 8.0,
    outer_level = 8.0,
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
        vbo.draw(GL_PATCHES)

if __name__ == '__main__':
    pyglet.app.run()
