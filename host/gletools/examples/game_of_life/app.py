from __future__ import with_statement

import sys
import re
import random
from contextlib import nested

import pyglet
from gletools import ShaderProgram, FragmentShader, Texture, Framebuffer, Sampler2D
from gletools.gl import *

from lif_parser import LifParser

window = pyglet.window.Window(fullscreen=True, vsync=False)

framebuffer = Framebuffer()
front = Texture(window.width, window.height, format=GL_RGB, filter=GL_NEAREST)
back = Texture(window.width, window.height, format=GL_RGB, filter=GL_NEAREST)
framebuffer.textures[0] = front

program = ShaderProgram(
    FragmentShader.open('shader.frag'),
)
program.vars.width = float(front.width)
program.vars.height = float(front.height)
program.vars.texture = Sampler2D(GL_TEXTURE0)

def quad():
    glBegin(GL_QUADS)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(window.width, window.height, 0.0)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(window.width, 0.0, 0.0)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(0.0, 0.0, 0.0)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(0.0, window.height, 0.0)
    glEnd()

pyglet.clock.schedule(lambda delta:None)
fps = pyglet.clock.ClockDisplay()

@window.event
def on_draw():
    global front, back

    framebuffer.textures[0] = front

    window.clear()
    with nested(framebuffer, program, back):
        quad()
   
    with front:
        quad()

    fps.draw()

    front, back = back, front

def spawn_random(x, y):
    xoff, yoff, pattern = random.choice(catalogue)
    xpos, ypos = x + xoff, y + yoff
    
    back.retrieve()
    for px, py in pattern:
        back[xpos+px, ypos+py] = 255, 255, 255
    back.update()

def spawn_whole(x, y):
    back.retrieve()
    for xoff, yoff, pattern in catalogue:
        xpos, ypos = x + xoff, y + yoff
        for px, py in pattern:
            back[xpos+px, ypos+py] = 255, 255, 255
    back.update()

@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == pyglet.window.mouse.LEFT:
        spawn_whole(x, y)
    else:
        spawn_random(x, y)

@window.event
def on_mouse_drag(x, y, dx, dy, button, modifiers):
    if button == pyglet.window.mouse.LEFT:
        spawn_whole(x, y)
    else:
        spawn_random(x, y)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        ruleset, catalogue = LifParser.parse(sys.argv[1])
    else:
        ruleset, catalogue = LifParser.parse('patterns/gliders.lif')
    pyglet.app.run()
