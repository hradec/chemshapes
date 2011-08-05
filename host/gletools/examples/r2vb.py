from __future__ import with_statement

import pyglet
from util import gl_init, ChangeValue, nested, quad, Sun
from gletools.gl import *
from gletools import (
    Screen, Projection, Lighting, Color, VertexObject, Texture, Framebuffer,
    ShaderProgram, FragmentShader,
)

class Heightmap(object):
    def __init__(self, width, height, scale=0.2):
        self.width = width
        self.height = height
        self.view = Screen(0, 0, width, height)

        self.vertex_texture = Texture(width, height, GL_RGBA32F)
        self.normal_texture = Texture(width, height, GL_RGBA32F)
        self.fbo = Framebuffer(
            self.vertex_texture,
            self.normal_texture,
        )
        self.fbo.drawto = GL_COLOR_ATTACHMENT0_EXT, GL_COLOR_ATTACHMENT1_EXT

        self.program = ShaderProgram(
            FragmentShader.open('shaders/heightmap_normal.frag'),
            offsets = (1.0/width, 1.0/height),
            scale = scale,
        )
        self.vbo = self.generate_vbo(width, height)

    def generate_vbo(self, width, height):
        v4f = []
        for z in range(height):
            for x in range(width):
                v4f.extend((x/float(width), 0, z/float(height), 1))

        n4f = []
        for z in range(height):
            for x in range(width):
                n4f.extend((0, 0, 0, 0))

        at = lambda x, y: x+y*width

        indices = []
        for z in range(height-1):
            for x in range(width-1):
                indices.extend((
                    at(x, z), at(x, z+1), at(x+1, z+1)        
                ))
                indices.extend((
                    at(x, z), at(x+1, z+1), at(x+1, z)        
                ))

        return VertexObject(
            pbo                 = True,
            indices             = indices,
            dynamic_draw_v4f    = v4f,
            dynamic_draw_n4f    = n4f,
        )
 
        pass

    def update_from(self, source):
        with nested(self.fbo, self.view, source, self.program):
            quad(self.width, self.height, 0, 0)
            self.vbo.vertices.copy_from(self.vertex_texture)
            self.vbo.normals.copy_from(self.normal_texture)

    def draw(self):
        self.vbo.draw(GL_TRIANGLES)

if __name__ == '__main__':
    window = pyglet.window.Window(fullscreen=True)
    projection = Projection(0, 0, window.width, window.height, near=0.1, far=100)
    angle = ChangeValue()
    texture = Texture.open('images/heightmap.png')
    heightmap = Heightmap(texture.width, texture.height)
    sun = Sun()

    @window.event
    def on_draw():
        window.clear()
        
        heightmap.update_from(texture)

        with nested(projection, Color, sun):
            glColor3f(0.5, 0.5, 0.5)
            glPushMatrix()
            glTranslatef(0, 0, -1)
            glRotatef(20, 1, 0, 0)
            glRotatef(angle, 0.0, 1.0, 0.0)
            glTranslatef(-0.5, 0, -0.5)
            heightmap.draw()
            glPopMatrix()

        texture.draw(10, 10)
        heightmap.vertex_texture.draw(148, 10)
        heightmap.normal_texture.draw(286, 10)

    gl_init(light=False)
    if gl_info.have_extension('ARB_color_buffer_float'):
        glClampColorARB(GL_CLAMP_VERTEX_COLOR_ARB, GL_FALSE)
        glClampColorARB(GL_CLAMP_FRAGMENT_COLOR_ARB, GL_FALSE)
        glClampColorARB(GL_CLAMP_READ_COLOR_ARB, GL_FALSE)
    pyglet.app.run()
