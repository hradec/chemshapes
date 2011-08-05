from __future__ import with_statement
from contextlib import nested

import pyglet
from gletools import (
    ShaderProgram, FragmentShader, VertexShader, Depthbuffer,
    Texture, Projection, UniformArray, Lighting, Color
)
from gletools.gl import *
from util import Mesh, Processor, Kernel, offsets, gl_init

### setup ###

class Gaussian(object):
    def __init__(self, processor):
        self.processor = processor 
        off = (1.0/processor.width)*1.2, (1.0/processor.height)*1.2
        self.vertical = ShaderProgram(
            FragmentShader.open('shaders/gaussian/vertical.frag'),
            off = off,
        )

        self.horizontal = ShaderProgram(
            FragmentShader.open('shaders/gaussian/horizontal.frag'),
            off = off,
        )
    def filter(self, texture, steps=1):
        for _ in range(steps):
            self.processor.filter(texture, self.vertical)
            self.processor.filter(texture, self.horizontal)

### Application code ###

if __name__ == '__main__':
    window = pyglet.window.Window()
    projection = Projection(0, 0, window.width, window.height, near=18, far=50)
    texture = Texture(window.width, window.height, GL_RGBA32F)
    processor = Processor(texture)
    bunny = Mesh('meshes/bunny')
    gaussian = Gaussian(processor)

    angle = 0.0
    def simulate(delta):
        global angle
        angle += 10.0 * delta
    pyglet.clock.schedule_interval(simulate, 0.01)

    @window.event
    def on_draw():
        window.clear()
        
        with nested(processor.renderto(texture), projection, Lighting, Color):
            glClearColor(0.0,0.0,0.0,0.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            glPushMatrix()
            glTranslatef(0, 0, -40)
            glRotatef(-65, 1, 0, 0)
            glRotatef(angle, 0.0, 0.0, 1.0)
            glRotatef(90, 1, 0, 0)
            glColor4f(0.5, 0.0, 0.0, 1.0)
            bunny.draw()
            glPopMatrix()

        gaussian.filter(texture, 5)
        processor.blit(texture)

    gl_init()
    pyglet.app.run()
