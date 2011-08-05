import pyglet
from pyglet.gl import *
from ctypes import c_float, c_uint
import math

from gletools import ShaderProgram, VertexObject, Matrix
            
def simulate(delta, _):
    global rotation, zoom
    rotation += 0.1 * delta
    zoom = (math.sin(rotation*6)+1)*25+1
pyglet.clock.schedule(simulate, 0.03)

def make_plane(width, height):
    v4f = (c_float*(width*height*4))()
    width_factor, height_factor = 30.0/float(width), 30.0/float(height)
    for y in xrange(height):
        for x in xrange(width):
            offset = (x+y*width)*4
            v4f[offset:offset+4] = x*width_factor-15, y*height_factor-15, 0, 1

    i_width, i_height = width-1, height-1
    indices = (c_uint*(i_width*i_height*4))()
    for y in xrange(i_height):
        for x in xrange(i_width):
            offset = (x+y*i_width)*4
            p1 = x+y*width
            p2 = p1+width
            p4 = p1+1
            p3 = p2+1
            indices[offset:offset+4] = p1, p2, p3, p4

    return VertexObject(
        indices = indices,
        v4f     = v4f,
    )

window = pyglet.window.Window(vsync=False)
rotation = 0.0
vbo = make_plane(32, 32)

linear = ShaderProgram.open('quads.shader',
    inner_level = 16.0,
    outer_level = 16.0,
    simple      = True,
)

lod = ShaderProgram.open('lod.shader',
    pixels_per_division = 15.0,
    projected = False,
)

fps = pyglet.clock.ClockDisplay(color=(1,0,0,0.5))

@window.event
def on_draw():
    window.clear()

    program = lod
    program.vars.modelview = Matrix().translate(0,0,-zoom).rotatex(-0.14).rotatez(rotation)
    program.vars.projection = Matrix.perspective(window.width, window.height, 60, 0.1, 200.0)
    program.vars.screen_size = float(window.width), float(window.height)

    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    with program:
        glPatchParameteri(GL_PATCH_VERTICES, 4);
        vbo.draw(GL_PATCHES)
        #vbo.draw(GL_QUADS)

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    fps.draw()

if __name__ == '__main__':
    pyglet.app.run()
