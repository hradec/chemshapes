#!/usr/bin/python

from __future__ import division

from os import listdir
from os.path import isfile, join
import sys
from random import uniform

from pyglet import app, clock
from pyglet.event import EVENT_HANDLED
from pyglet.window import key, Window
from pyglet.gl import (
    glClear, glClearColor, glLoadIdentity, glMatrixMode, gluLookAt,
    GL_COLOR_BUFFER_BIT, GL_MODELVIEW, GL_PROJECTION, GL_TRIANGLES
)
from pyglet.gl.glu import gluOrtho2D

from svgbatch import SvgBatch


class SvgFiles(object):

    def __init__(self):
        self.filenames = self.get_filenames(join('svgbatch', 'testdata'))
        if len(self.filenames) == 0:
            raise Exception('no testdata svg files found')

        self.number = -1
        self.current = None
        self.next()

    def get_filenames(self, path):
        return [
            join(path, filename)
            for filename in listdir(path)
            if filename.endswith('.svg')
        ]

    def next(self):
        self.number = (self.number + 1) % len(self.filenames)
        filename = self.filenames[self.number]
        print filename
        self.current = SvgBatch(filename)
        self.current.create_batch()

        glClearColor(
            uniform(0.0, 1.0),
            uniform(0.0, 1.0),
            uniform(0.0, 1.0),
            1.0)

    def draw(self):
        self.current.create_batch().draw()



class PygletApp(object):

    def __init__(self):
        self.window = Window(visible=False, fullscreen=False)
        self.window.on_resize = self.on_resize
        self.window.on_draw = self.on_draw
        self.window.on_key_press = self.on_key_press

        self.files = SvgFiles()

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(
            0.0, -0.0, 1.0,  # eye
            0.0, -0.0, -1.0, # lookAt
            0.0, 1.0, 0.0)  # up


    def on_draw(self):
        glClear(GL_COLOR_BUFFER_BIT)
        self.files.draw()
        return EVENT_HANDLED


    def on_resize(self, width, height):
        # scale is distance from screen centre to top or bottom, in world coords
        scale = 110
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = width / height
        gluOrtho2D(
            -scale * aspect,
            +scale * aspect,
            -scale,
            +scale)
        return EVENT_HANDLED


    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.window.close()
            return
        self.files.next()


    def run(self):
        self.window.set_visible()
        app.run()



def main():
    app = PygletApp()
    app.run()


if __name__ == '__main__':
    main()

