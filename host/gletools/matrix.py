from math import sin, cos, tan, pi
tau = 2*pi #http://tauday.com/ ffs
from shader import Variable

from pyglet.gl import *
from pyglet.gl.glext_arb import *

from ctypes import c_float

__all__ = 'Matrix', 'Vector'

class Vector(object):
    def __init__(self, x=0.0, y=0.0, z=0.0, w=1.0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def __repr__(self):
        return '<Vector %4.2f %4.2f %4.2f %4.2f>' % (
            self.x, self.y, self.z, self.w
        )

    def __mul__(self, scalar):
        return Vector(
            self.x * scalar,
            self.y * scalar,
            self.z * scalar,
            1.0,
        )

    def __add__(self, other):
        return Vector(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z,
            1.0,
        )
    
    def __sub__(self, other):
        return Vector(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z,
            1.0,
        )

    def __call__(self, other):
        return (
            self.x * other.x +
            self.y * other.y +
            self.z * other.z +
            self.w * other.w
        )

    def __div__(self, scalar):
        return Vector(self.x/scalar, self.y/scalar, self.z/scalar, self.w/scalar)

    def matrix_multiply(self, matrix):
        return Vector(
            self(matrix.col(0)),
            self(matrix.col(1)),
            self(matrix.col(2)),
            self(matrix.col(3)),
        )

class Matrix(Variable):
    def __init__(self, *values):
        if values:
            assert len(values) == 16
            self.values = (c_float*16)(*values)
 
        else:
            self.values = (c_float*16)(
                1.0, 0.0, 0.0, 0.0,
                0.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
                0.0, 0.0, 0.0, 1.0,
            )
    
    def __getitem__(self, i):
        return self.values[i]
    
    def __repr__(self):
        return (
            '<Matrix\n'
            '  %04.2f %04.2f %04.2f %04.2f\n'
            '  %04.2f %04.2f %04.2f %04.2f\n'
            '  %04.2f %04.2f %04.2f %04.2f\n'
            '  %04.2f %04.2f %04.2f %04.2f\n' 
            '>'
        ) % tuple(self.values)
    
    def translate(self, x, y, z):
        return self * Matrix(
            1.0, 0.0, 0.0, x,
            0.0, 1.0, 0.0, y,
            0.0, 0.0, 1.0, z,
            0.0, 0.0, 0.0, 1.0,
        )
    
    def col(self, i):
        return Vector(
            self[i],
            self[i+4],
            self[i+8],
            self[i+12],
        )

    def row(self, i):
        return Vector(*self[i*4:i*4+4])


    def __mul__(self, other):
        return other.matrix_multiply(self)

    def matrix_multiply(self, other):
        col0, col1, col2, col3 = self.col(0), self.col(1), self.col(2), self.col(3)
        row0, row1, row2, row3 = other.row(0), other.row(1), other.row(2), other.row(3)

        return Matrix(
            row0(col0), row0(col1), row0(col2), row0(col3),
            row1(col0), row1(col1), row1(col2), row1(col3),
            row2(col0), row2(col1), row2(col2), row2(col3),
            row3(col0), row3(col1), row3(col2), row3(col3),
        )

    def rotatex(self, angle):
        s = sin(angle*tau)
        c = cos(angle*tau)

        return self * Matrix(
            1.0, 0.0, 0.0, 0.0,
            0.0,   c,  -s, 0.0,
            0.0,   s,   c, 0.0,
            0.0, 0.0, 0.0, 1.0,
        )
    
    def rotatey(self, angle):
        s = sin(angle*tau)
        c = cos(angle*tau)

        return self * Matrix(
              c, 0.0,   s, 0.0,
            0.0, 1.0, 0.0, 0.0,
             -s, 0.0,   c, 0.0,
            0.0, 0.0, 0.0, 1.0,
        )
    
    def rotatez(self, angle):
        s = sin(angle*tau)
        c = cos(angle*tau)

        return self * Matrix(
              c,  -s, 0.0, 0.0,
              s,   c, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0,
        )

    def transpose(self):
        col0 = self.col(0)
        col1 = self.col(1)
        col2 = self.col(2)
        col3 = self.col(3)

        return Matrix(
            col0.x, col0.y, col0.z, col0.w,
            col1.x, col1.y, col1.z, col1.w,
            col2.x, col2.y, col2.z, col2.w,
            col3.x, col3.y, col3.z, col3.w,
        )

    @classmethod
    def perspective(cls, width, height, fov, n, f):
        aspect = float(width)/float(height)
        y = n * tan((fov*pi)/360.0)
        x = y * aspect
        
        l = -x
        r = x
        t = y
        b = -y
        
        return cls(
            (2.0*n)/(r-l),  0.0,            (r+l)/(r-l),    0.0,
            0.0,            (2.0*n)/(t-b),  (t+b)/(t-b),    0.0,
            0.0,            0.0,            -(f+n)/(f-n),   (-2.0*f*n)/(f-n),
            0.0,            0.0,            -1.0,           0.0,
        )

    @classmethod
    def inverse_perspective(cls, width, height, fov, n, f):
        aspect = float(width)/float(height)
        y = n * tan((fov*pi)/360.0)
        x = y * aspect
        
        l = -x
        r = x
        t = y
        b = -y
        
        return cls(
            (r-l)/(2.0*n),  0.0,            0.0,                (r+l)/(2*n),
            0.0,            (t-b)/(2.0*n),  0.0,                (t+b)/(2*n),
            0.0,            0.0,            0.0,                -1.0,
            0.0,            0.0,            -(f-n)/(2.0*f*n),   (f+n)/(2.0*f*n),
        )

    def do_set(self, location):
        glUniformMatrix4fv(location, 1, GL_TRUE, self.values)

    @property
    def mat3(self):
        row0 = self.row(0)
        row1 = self.row(1)
        row2 = self.row(2)

        return Matrix3(
            row0.x, row0.y, row0.z, 
            row1.x, row1.y, row1.z,
            row2.x, row2.y, row2.z,
        )

class Matrix3(Variable):
    def __init__(self, *values):
        self.values = (c_float*9)(*values)
    
    def do_set(self, location):
        glUniformMatrix3fv(location, 1, GL_TRUE, self.values)
