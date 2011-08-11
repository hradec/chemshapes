# -*- coding: utf-8 -*-

"""
    :copyright: 2009 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""
from __future__ import with_statement
from ctypes import byref, c_uint

from gletools.gl import *

_get_type_map = {
    int: (GLint, glGetIntegerv),
    float: (GLfloat, glGetFloatv),
}

def get(enum, size=1, type=int):
    type, accessor = _get_type_map[type]
    values = (type*size)()
    accessor(enum, values)
    if size == 1:
        return values[0]
    else:
        return values[:]

def enabled(enum):
    return glIsEnabled(enum)

class Context(object):
    current = None
    previous = []

    def __init__(self):
        self.stack = list()

    def __enter__(self):
        self._enter()
        self.stack.append(get(self._get))
        cls = self.__class__
        cls.previous.append(cls.current)
        cls.current = self
        self.bind(self.id)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.check()
        id = self.stack.pop(-1)
        cls = self.__class__
        cls.current = cls.previous.pop(-1)
        self.bind(id)
        self._exit()

    def _enter(self):
        pass

    def _exit(self):
        pass

    def check(self):
        pass

class Group(object):
    def __init__(self, *members, **named_members):
        self.__dict__.update(named_members)
        self._members = list(members) + named_members.values()
    
    def __enter__(self):
        for member in self._members:
            member.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        for member in reversed(self._members):
            member.__exit__(exc_type, exc_val, exc_tb)

class MatrixMode(object):
    def __init__(self, mode):
        self.mode = mode

    def __enter__(self):
        glPushAttrib(GL_TRANSFORM_BIT)
        glMatrixMode(self.mode)

    def __exit__(self, exc_type, exc_val, exc_tb):
        glPopAttrib()

class SphereMapping(object):
    @staticmethod
    def __enter__():
        glPushAttrib(GL_ENABLE_BIT | GL_TEXTURE_BIT)
        glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
        glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
        glEnable(GL_TEXTURE_GEN_S)
        glEnable(GL_TEXTURE_GEN_T)
    @staticmethod
    def __exit__(exc_type, exc_val, exc_tb):
        glPopAttrib()

class DepthTest(object):
    @staticmethod
    def __enter__():
        glPushAttrib(GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
    @staticmethod
    def __exit__(exc_type, exc_val, exc_tb):
        glPopAttrib()

class Lighting(object):
    @staticmethod
    def __enter__():
        glPushAttrib(GL_LIGHTING_BIT)
        glEnable(GL_LIGHTING)
    @staticmethod
    def __exit__(exc_type, exc_val, exc_tb):
        glPopAttrib()

class Color(object):
    @staticmethod
    def __enter__():
        glPushAttrib(GL_CURRENT_BIT)
    @staticmethod
    def __exit__(exc_type, exc_val, exc_tb):
        glPopAttrib()

class Matrix(object):
    @staticmethod
    def __enter__():
        glPushMatrix()

    @staticmethod
    def __exit__(exc_type, exc_val, exc_tb):
        glPopMatrix()

class Projection(object):
    def __init__(self, x, y, width, height, fov=55, near=0.1, far=100.0):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.fov = fov
        self.near, self.far = near, far

    def __enter__(self):
        glPushAttrib(GL_VIEWPORT_BIT)
        glViewport(self.x, self.y, self.width, self.height)
       
        with MatrixMode(GL_PROJECTION):
            glPushMatrix()
            glLoadIdentity()
            gluPerspective(self.fov, self.width / float(self.height), self.near, self.far)

    def __exit__(self, exc_type, exc_val, exc_tb):
        with MatrixMode(GL_PROJECTION):
            glPopMatrix()

        glPopAttrib()

class Viewport(object):
    def __init__(self, x, y, width, height):
        self.x, self.y = x, y
        self.width, self.height = width, height

    def __enter__(self):
        glPushAttrib(GL_VIEWPORT_BIT)
        glViewport(self.x, self.y, self.width, self.height)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        glPopAttrib()

class Screen(object):
    def __init__(self, x, y, width, height):
        self.x, self.y = x, y
        self.width, self.height = width, height

    def __enter__(self):
        glPushAttrib(GL_VIEWPORT_BIT)
        glViewport(self.x, self.y, self.width, self.height)

        with MatrixMode(GL_PROJECTION):
            glPushMatrix()
            glLoadIdentity()
            gluOrtho2D(self.x, self.width, self.y, self.height)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        with MatrixMode(GL_PROJECTION):
            glPopMatrix()

        glPopAttrib()

class Ortho(object):
    def __init__(self, left, right, top, bottom, near, far):
        self.left, self.right = left, right 
        self.top, self.bottom = top, bottom 
        self.near, self.far = near, far

    def __enter__(self):
        with MatrixMode(GL_PROJECTION):
            glPushMatrix()
            glLoadIdentity()
            glOrtho(self.left, self.right, self.bottom, self.top, self.near, self.far)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        with MatrixMode(GL_PROJECTION):
            glPopMatrix()

def interval(time):
    def _interval(fun):
        pyglet.clock.schedule_interval(fun, time)
        return fun
    return _interval

def quad(left=-0.5, top=-0.5, right=0.5, bottom=0.5, scale=1.0):
    left *= scale
    right *= scale
    top *= scale
    bottom *= scale
    glBegin(GL_QUADS)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(right, bottom, 0.0)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(right, top, 0.0)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(left, top, 0.0)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(left, bottom, 0.0)
    glEnd()

class DependencyException(Exception): pass
class ExtensionMissing(Exception): pass

def gen_buffers(amount=1):
    ids = (c_uint*amount)()
    glGenBuffers(amount, ids)
    if amount == 1:
        return ids[0]
    else:
        return ids
