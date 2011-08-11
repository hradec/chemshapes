from __future__ import with_statement
from math import e, pow, sqrt
from gletools import Framebuffer, Depthbuffer, Screen, Texture, UniformArray, VertexObject, ShaderProgram, VertexShader, FragmentShader
from gletools.gl import *
from contextlib import nested

def gl_init(light=True):
    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    glShadeModel(GL_SMOOTH)

    if light:
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_AMBIENT, (GLfloat*4)(0.1, 0.1, 0.1, 0.2))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (GLfloat*4)(0.5, 0.5, 0.5, 0.8))
        glLightfv(GL_LIGHT0, GL_SPECULAR, (GLfloat*4)(0.3, 0.3, 0.3, 0.5))
        glLightfv(GL_LIGHT0, GL_POSITION, (GLfloat*4)(0, 30, 0, 1))

def gauss(x, height=1.0, width=1.0, position=0.0):
    return height*pow(e, - pow(x-position, 2) / (2*pow(width*0.308, 2)))

class Kernel(object):
    def __init__(self, size, values=None):
        self.size = size
        if values:
            self.values = map(float, values)
        else:
            self.values = [0.0] * size**2

    def __getitem__(self, (x,y)):
        return self.values[x+y*self.size]

    def __setitem__(self, (x,y), value):
        self.values[x+y*self.size] = value
    
    def __iter__(self):
        return iter(self.values)

    def __len__(self):
        return len(self.values)
    
    def __repr__(self):
        return 'Kernel(\n%s\n)' % '\n'.join(
            '    %s' % ', '.join(
                '%6.2f' % self[x,y] for x in range(self.size)
            )
            for y in range(self.size)
        )

    def normalize(self):
        kernel = self.copy()
        s = sum(kernel.values)
        if s:
            kernel.values = [value/s for value in kernel.values]
        return kernel

    def invert(self):
        kernel = self.copy()
        kernel.values = [1.0-value for value in kernel.values]
        return kernel

    def gauss(self, width=1.0):
        kernel = self.copy()
        max_distance = sqrt(2*pow(kernel.size/2, 2))
        for x in range(kernel.size):
            xoff = x - kernel.size/2
            for y in range(kernel.size):
                yoff = y - kernel.size/2
                distance = sqrt(xoff**2+yoff**2)
                kernel[x,y] = gauss(distance, width=max_distance*width)
        return kernel

    def copy(self):
        kernel = Kernel(self.size)
        kernel.values = list(self.values)
        return kernel

def quad(top, right, bottom, left):
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(bottom, right, 0.0)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(bottom, left, 0.0)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(top, left, 0.0)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(top, right, 0.0)
    glEnd()

class Processor(object):
    def __init__(self, ref):
        self.temp = Texture(
            width       = ref.width,
            height      = ref.height,
            format      = ref.format,
            filter      = ref.filter,
            mipmap      = ref.mipmap,
        )
        self.width = ref.width
        self.height = ref.height
        self.fbo = Framebuffer(self.temp)
        self.view = Screen(0, 0, self.width, self.height)
        
        self.render_target = Framebuffer(self.temp)
        self.render_target.depth = Depthbuffer(self.width, self.height)
    
    def filter(self, texture, effect):
        self.fbo.textures[0] = self.temp
        with nested(self.fbo, texture, self.view, effect):
            quad(self.width, self.height, 0, 0)
        glFinish()
        self.copy(self.temp, texture)

    def quad(self):
        quad(self.width, self.height, 0, 0)

    def copy(self, source, target):
        self.fbo.textures[0] = target
        with nested(self.fbo, source, self.view):
            self.quad()
        glFinish()

    def blit(self, texture):
        with nested(texture, self.view):
            self.quad()

    def renderto(self, output):
        self.render_target.textures[0] = output
        return self.render_target

class Mesh(object):
    def __init__(self, path):
        v3f = [float(c)*0.2 for c in open('%s/vertices' % path).read().strip().split()]
        n3f = map(float, open('%s/normals' % path).read().strip().split())
        faces = map(int, open('%s/faces' % path).read().strip().split())
        self.vbo = VertexObject(
            indices = faces,
            n3f = n3f,
            v3f = v3f,
        )

    def draw(self):
        self.vbo.draw()

def offsets(min, max, window):
    result = []
    for x in range(min, max+1):
        for y in range(min, max+1):
            xoff = float(x)/float(window.width)
            yoff = float(y)/float(window.height)
            result.append(xoff)
            result.append(yoff)
    return UniformArray(float, 2, result)

class ChangeValue(object):
    def __init__(self, start=0.0, change=10.0, rate=0.02):
        self.value = start
        self.change = change
        pyglet.clock.schedule_interval(self.simulate, rate)
       
    def simulate(self, delta):
        self.value += self.change * delta

    def __float__(self):
        return self.value

    def __mul__(self, other):
        return float(self) * other

def Sun(color=(1.0, 1.0, 1.0), direction=(0.5,-0.5,0.0), ambient=(0.1, 0.1, 0.1)):
    return ShaderProgram(
        VertexShader.open('shaders/sun.vert'),
        FragmentShader.open('shaders/sun.frag'),
        color = color,
        direction = direction,
        ambient = ambient,
    )
