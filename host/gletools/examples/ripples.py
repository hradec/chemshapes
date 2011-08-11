# -*- coding: utf-8 -*-
"""
    examples.ripples
    ~~~~~~~~~~~~~~~~

    :copyright: 2009 by Henri Tuhola <henri.tuhola@gmail.com> / Florian Boesch <pyalot@gmail.com>
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""
from __future__ import with_statement
from util import quad, nested
import random

import pyglet
from gletools import (
    ShaderProgram, FragmentShader, Texture, Framebuffer, Sampler2D, Screen, Color
)
from gletools.gl import *

class Ripples(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.framebuffer = Framebuffer()
        self.tex1 = Texture(width, height, filter=GL_NEAREST, format=GL_RGBA32F, clamp='st')
        self.tex2 = Texture(width, height, filter=GL_NEAREST, format=GL_RGBA32F, clamp='st')
        self.tex3 = Texture(width, height, filter=GL_NEAREST, format=GL_RGBA32F, clamp='st')

        self.program = ShaderProgram(
            FragmentShader.open('shaders/ripples.frag'),
            offsets = (1.0/width, 1.0/height),
            tex2 = Sampler2D(GL_TEXTURE1),
            tex3 = Sampler2D(GL_TEXTURE2),
        )

    def step(self):
        self.framebuffer.textures[0] = self.tex1
        self.tex1.unit = GL_TEXTURE0
        self.tex2.unit = GL_TEXTURE1
        self.tex3.unit = GL_TEXTURE2

        with nested(self.framebuffer, self.program, self.tex2, self.tex3):
            quad(self.width, self.height, 0, 0)

        self.tex1, self.tex2, self.tex3 = self.tex2, self.tex3, self.tex1

    @property
    def result(self):
        return self.tex3

if __name__=='__main__':
    window = pyglet.window.Window()
    ripples = Ripples(window.width, window.height)
    pyglet.clock.schedule(lambda delta: None)
   
    @window.event
    def on_mouse_motion(x, y, rx, ry):
        with nested(ripples.framebuffer, Color):
            glColor4f(0.0, 1.5, 3.0, 1.0)
            glLineWidth(1.0)
            glBegin(GL_LINES)
            glVertex3f(x, y, 0)
            glVertex3f(x+rx, y+ry, 0)
            glEnd()

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        with nested(ripples.framebuffer, Color):
            glColor4f(0.0, 1.5, 3.0, 1.0)
            glBegin(GL_QUADS)
            size = 1.0
            glVertex3f(x+size, y+size, 0)
            glVertex3f(x+size, y-size, 0)
            glVertex3f(x-size, y-size, 0)
            glVertex3f(x-size, y+size, 0)
            glEnd()
    
    def rain(delta):
        x = random.randint(0, ripples.width)
        y = random.randint(0, ripples.height)
        size = random.random() * 1.5
        with nested(ripples.framebuffer, Color):
            glBegin(GL_QUADS)
            glColor4f(0.0, size/2, size, 1.0)
            glVertex3f(x+size, y+size, 0)
            glVertex3f(x+size, y-size, 0)
            glVertex3f(x-size, y-size, 0)
            glVertex3f(x-size, y+size, 0)
            glEnd()
        
    pyglet.clock.schedule_interval(rain, 0.2)

    @window.event
    def on_draw():
        window.clear()
        ripples.step()
        ripples.result.draw()

    glEnable(GL_POINT_SMOOTH)
    glEnable(GL_LINE_SMOOTH)
    if gl_info.have_extension('ARB_color_buffer_float'):
        glClampColorARB(GL_CLAMP_VERTEX_COLOR_ARB, GL_FALSE)
        glClampColorARB(GL_CLAMP_FRAGMENT_COLOR_ARB, GL_FALSE)
        glClampColorARB(GL_CLAMP_READ_COLOR_ARB, GL_FALSE)
    pyglet.app.run()
