class Vector(object):
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    @classmethod
    def clone(cls, other):
        return cls(other.x, other.y, other.z)

    @property
    def tuple(self):
        return self.x, self.y, self.z 

    def __sub__(self, other):
        return Vector(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z,
        )
   
    @property
    def length(self):
        return (
            self.x**2 +
            self.y**2 + 
            self.z**2
        ) ** 0.5

    @property
    def normalized(self):
        return self / self.length

    @property
    def square_length(self):
        return (
            self.x**2 +
            self.y**2 + 
            self.z**2
        )

    @property
    def reversed(self):
        return self * -1.0

    def mix(self, other, factor):
        return self + (other - self) * factor

    def max(self, other):
        return Vector(
            max(self.x, other.x),
            max(self.y, other.y),
            max(self.z, other.z),
        )

    def __add__(self, other):
        return Vector(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z,
        )

    def __div__(self, scalar):
        return Vector(
            self.x / scalar,
            self.y / scalar,
            self.z / scalar,
        )

    def __mul__(self, scalar):
        return Vector(
            self.x * scalar,
            self.y * scalar,
            self.z * scalar,
        )

    def mul(self, other):
        return Vector(
            self.x * other.x,
            self.y * other.y,
            self.z * other.z,
        )

    def __repr__(self):
        return 'Vec(%f, %f, %f)' % (self.x, self.y, self.z)
    
    def cross(self, other):
        return Vector(
            self.y * other.z - self.z * other.y,
           -self.x * other.z + self.z * other.x,
            self.x * other.y - self.y * other.x,
        )

    def dot(self, other):
        return (
            self.x * other.x + 
            self.y * other.y + 
            self.z * other.z
        )

vertices = open('vertices').read().strip().split('\n')
vertices = [tuple(map(float, v.split())) for v in vertices]
faces = open('faces').read().strip().split('\n')
faces = [tuple(map(int, f.split())) for f in faces]


vertex_faces = dict()
face_normals = list()
for i, (i1, i2, i3) in enumerate(faces):
    neighbors = vertex_faces.setdefault(i1, [])
    neighbors.append(i)
    neighbors = vertex_faces.setdefault(i2, [])
    neighbors.append(i)
    neighbors = vertex_faces.setdefault(i3, [])
    neighbors.append(i)

    vec1 = Vector(*vertices[i1])
    vec2 = Vector(*vertices[i2]) - vec1
    vec3 = Vector(*vertices[i3]) - vec1
    normal = vec2.cross(vec3).normalized
    face_normals.append(normal)

vertex_normals = list()
for i, vertex in enumerate(vertices):
    normal = Vector(0, 0, 0)
    count = 0
    for neighbor_face_index in vertex_faces[i]:
        count += 1
        normal += face_normals[neighbor_face_index]
    normal = (normal / count).normalized
    vertex_normals.append(normal)

outfile = open('normals', 'w')
for normal in vertex_normals:
    outfile.write('%f %f %f\n' % normal.tuple)
outfile.close()
