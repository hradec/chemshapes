from os.path import exists
from pickle import dump, load
from ctypes import c_float, c_uint

from pyglet.window import key
from pyglet.input.evdev import get_devices
from pyglet.clock import schedule

from gletools import Matrix, Vector, VertexObject, VBO

class Navigator(object):
    def __init__(self):
        device = None
        for d in get_devices():
            if d.name == '3Dconnexion SpaceNavigator':
                device = d

        if device:
            self.device = device
            device.open()
            self.axes = {
                'x' : self.get('x'),
                'y' : self.get('y'),
                'z' : self.get('z'),
                'rx' : self.get('rx'),
                'ry' : self.get('ry'),
                'rz' : self.get('rz'),
            }
        else:
            raise Exception('no space navigator found')

    def get(self, name):
        for control in self.device.controls:
            if control.name == name:
                return control

    def __getattr__(self, name):
        value = self.axes[name].value/255.0 
        if value > 0.0:
            return value*value
        else:
            return -value*value

class View(object):
    def __init__(self, window):
        if exists('saved.view'):
            data = load(open('saved.view'))
            self.rotation = Vector(data['rx'], data['ry'])
            self.position = Vector(data['x'], data['y'], data['z'])
        else:
            self.rotation = Vector()
            self.position = Vector(0, 0, -1)

        self.rotspeed = Vector()
        self.speed = Vector()
        self.keys = key.KeyStateHandler()
        self.navigator = Navigator()
        schedule(self.update)
        window.push_handlers(self.on_key_press)


    def update(self, delta):
        delta = min(delta, 0.03)
        rotmatrix = Matrix().rotatex(self.rotation.y).rotatey(self.rotation.x)
        front =  rotmatrix * Vector(0.0, 0.0, 1.0, 1.0)
        right =  rotmatrix * Vector(1.0, 0.0, 0.0, 1.0)
        up =  rotmatrix * Vector(0.0, 1.0, 0.0, 1.0)

        factor = 0.5 * delta

        self.speed += right * -self.navigator.x * factor * 0.5
        self.speed += up * self.navigator.z * factor * 0.5
        self.speed += front * -self.navigator.y * factor * 0.5
        self.rotspeed += Vector(self.navigator.rz * factor, -self.navigator.rx * factor)

        self.rotspeed -= self.rotspeed * 1.0 * delta
        self.speed -= self.speed * 1.0 * delta

        self.rotation += self.rotspeed * delta;
        self.position += self.speed * delta

        self.matrix = rotmatrix * Matrix().translate(self.position.x,self.position.y,self.position.z)

    def on_key_press(self, code, modifiers):
        if code == key.S:
            self.save()

    def save(self):
        data = {
            'x': self.position.x,
            'y': self.position.y,
            'z': self.position.z,
            'rx': self.rotation.x,
            'ry': self.rotation.y,
        }
        dump(data, open('saved.view', 'wb'))

def make_plane(width, height):
    v4f = (c_float*(width*height*4))()
    width_factor, height_factor = 1.0/float(width), 1.0/float(height)
    for y in xrange(height):
        for x in xrange(width):
            offset = (x+y*width)*4
            v4f[offset:offset+4] = x*width_factor, y*height_factor, -3, 1

    i_width, i_height = width-1, height-1
    indices = (c_uint*(i_width*i_height*4))()
    for y in xrange(i_height):
        for x in xrange(i_width):
            offset = (x+y*i_width)*4
            p1 = x+y*width
            p2 = p1+width
            p4 = p1+1
            p3 = p2+1
            indices[offset:offset+4] = p1, p2, p3, p4

    return VertexObject(
        indices = indices,
        v4f     = v4f,
    )

class Point(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def cross(self, other):
        return Point(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def normalize(self):
        length = (self.x*self.x + self.y*self.y + self.z*self.z)**0.5
        return Point(
            self.x / length,
            self.y / length,
            self.z / length,
        )

    def __add__(self, other):
        return Point(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z,
        )

    def __repr__(self):
        return str((self.x, self.y, self.z))
    
def make_triangles(width, height, terrain=None):
    position = (c_float*(width*height*4))()

    s_factor = 1.0/float(width-1)
    t_factor = 1.0/float(height-1)
    for y in range(height):
        for x in range(width):
            offset = (y*width+x) * 4
            s = float(x) * s_factor
            t = float(y) * t_factor
            if terrain:
                x_tex = int(round(s * float(terrain.width-1)))
                y_tex = int(round(t * float(terrain.height-1)))
                h = terrain[x_tex, y_tex][3]
            else:
                h = 0

            position[offset:offset+4] = s, t, h, 1

    normals = (c_float*(width*height*3))()

    if terrain:
        for y in range(height):
            for x in range(width):
                offset = (y*width+x) * 3
                s = float(x)*s_factor
                t = float(y)*t_factor

                x_tex = int(round(s * float(terrain.width-1)))
                y_tex = int(round(t * float(terrain.height-1)))
                x_shift = int(round(s_factor * float(terrain.width-1))) 
                y_shift = int(round(t_factor * float(terrain.height-1))) 

                up = Point(0.0, 0.0, 1.0)
                h = terrain[x_tex,y_tex][3]

                l = Point(-s_factor, 0.0, terrain[x_tex-x_shift,y_tex][3]-h)
                r = Point(+s_factor, 0.0, terrain[x_tex+x_shift,y_tex][3]-h)
                t = Point(0.0, -t_factor, terrain[x_tex,y_tex-y_shift][3]-h)
                b = Point(0.0, +t_factor, terrain[x_tex,y_tex+y_shift][3]-h)

                normal = (
                    l.cross(Point(0.0, -1.0, 0.0)).normalize() +
                    r.cross(Point(0.0, 1.0, 0.0)).normalize() +
                    t.cross(Point(1.0, 0.0, 0.0)).normalize() +
                    b.cross(Point(-1.0, 0.0, 0.0)).normalize()
                ).normalize()

                normals[offset:offset+3] = normal.x, normal.y, normal.z
            
    i_width, i_height = width-1, height-1
    indices = (c_uint*(i_width*i_height*6))()
    for y in range(i_height):
        for x in range(i_width):
            offset = (x+y*i_width)*6
            p1 = x+y*width
            p2 = p1+width
            p4 = p1+1
            p3 = p2+1
            indices[offset:offset+6] = p1, p2, p3, p1, p3, p4

    return VBO(
        count       = len(indices),
        indices     = indices,
        position_4  = position,
        normal_3    = normals,
    )
