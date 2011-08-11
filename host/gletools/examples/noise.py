from __future__ import with_statement
from contextlib import nested

import pyglet
from gletools import ShaderProgram, FragmentShader, Texture, Framebuffer, Projection, Screen
from gletools.gl import *

window = pyglet.window.Window()
texture = Texture(256, 256, filter=GL_LINEAR)
framebuffer = Framebuffer()
framebuffer.textures[0] = texture
screen = Screen(0, 0, texture.width, texture.height)
projection = Projection(0, 0, window.width, window.height)
program = ShaderProgram(
    FragmentShader('''
    uniform vec3 seed_vector;
    float nice_noise1(vec2 co){
        return fract(sin(dot(co.xy, vec2(12.9898, 78.233))) * 43758.5453);
    }
    void main(){
        gl_FragColor = vec4(
            nice_noise1(gl_TexCoord[0].xy * seed_vector.x),
            nice_noise1(gl_TexCoord[0].xy * seed_vector.y),
            nice_noise1(gl_TexCoord[0].xy * seed_vector.z),
            0
        );
    }''')
)
from random import random
program.vars.seed_vector = [random() for _ in xrange(3)]
rotation = 0.0

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

pyglet.clock.schedule(simulate, 0.03)
    
@window.event
def on_draw():
    window.clear()
    #program.vars.seed_vector = [random() for _ in xrange(3)]
    program.vars.seed_vector = [0.5 for _ in xrange(3)]
    with nested(framebuffer, program, screen):
        quad(0.0, texture.width)
  
    with nested(texture, projection):
        glPushMatrix()
        glTranslatef(0, 0, -3)
        glRotatef(-45, 1, 0, 0)
        glRotatef(rotation, 0.0, 0.0, 1.0)
        quad(-1, 1)
        glPopMatrix()

if __name__ == '__main__':
    pyglet.app.run()

