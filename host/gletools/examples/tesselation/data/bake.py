from ctypes import c_ubyte, c_float, string_at
from math import floor

ubytes = c_ubyte*(3*2048*2048)
floats = c_float*(4*2048*2048)


material = open('mountains.material', 'rb').read()
lightmap = open('mountains.lightmap', 'rb').read()
normals = open('mountains.normals', 'rb').read()
heights = open('mountains.heights', 'rb').read()

material = ubytes.from_buffer_copy(material)
lightmap = floats.from_buffer_copy(lightmap)
heights = floats.from_buffer_copy(heights)
normals = floats.from_buffer_copy(normals)

diffuse = floats()
terrain = floats()

for i in xrange(2048*2048):
    light = lightmap[i*4]
    r = float(material[i*3])/255.0
    g = float(material[i*3+1])/255.0
    b = float(material[i*3+2])/255.0

    x = normals[i*4+0]
    y = normals[i*4+1]
    z = normals[i*4+2]

    height = heights[i*4]

    diffuse[i*4+0] = r * light
    diffuse[i*4+1] = g * light
    diffuse[i*4+2] = b * light
    diffuse[i*4+3] = 1.0
    
    terrain[i*4+0] = x
    terrain[i*4+1] = y
    terrain[i*4+2] = z
    terrain[i*4+3] = height

data = string_at(diffuse, 2048*2048*4*4)
open('mountains.diffuse', 'wb').write(data)

data = string_at(terrain, 2048*2048*4*4)
open('mountains.terrain', 'wb').write(data)
