from __future__ import with_statement
from contextlib import nested

import pyglet
from gletools import ShaderProgram, FragmentShader, Texture, Framebuffer, Projection, Screen
from gletools.gl import *

from random import random
from util import quad, Processor, ChangeValue
from gaussian import Gaussian

window = pyglet.window.Window()
projection = Projection(0, 0, window.width, window.height)
noise = ShaderProgram(
    FragmentShader.open('shaders/noise.frag'),
    seed = 0.0,
)
width, height = 64, 64 
noise_texture = Texture(width, height, format=GL_RGBA32F)
noise_processor = Processor(noise_texture)
texture = Texture(64, 64, format=GL_RGBA32F)
processor = Processor(texture)
    
noise_processor.filter(noise_texture, noise)
processor.copy(noise_texture, texture)
gaussian = Gaussian(processor)
gaussian.filter(texture, 2)

rotation = ChangeValue()
    
@window.event
def on_draw():
    window.clear()


    with nested(projection, texture):
        glPushMatrix()
        glTranslatef(0, 0, -3)
        glRotatef(-45, 1, 0, 0)
        glRotatef(rotation, 0.0, 0.0, 1.0)
        quad(-1, 1, 1, -1)
        glPopMatrix()

if __name__ == '__main__':
    pyglet.app.run()

