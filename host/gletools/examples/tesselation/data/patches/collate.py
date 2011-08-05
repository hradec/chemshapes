from ctypes import c_ubyte, c_float, string_at, Structure

patch_width = 512
patch_height = 512
x_patches = 8
y_patches = 8

class Texel(Structure):
    _fields_ = [
        ('r', c_float),
        ('g', c_float),
        ('b', c_float),
        ('a', c_float),
    ]

def collate(name, filename):
    source_type = (Texel*(patch_width*patch_height))
    target = (Texel*(x_patches*patch_width*y_patches*patch_height))()
    for x in range(x_patches):
        for y in range(y_patches):
            source = source_type.from_buffer_copy(open('%s_%s.%s' % (x, y, name), 'rb').read())
            for row in xrange(patch_height):
                source_x = 0
                source_y = row
                target_x = patch_width * x
                target_y = patch_height * y + row

                source_offset = source_x + source_y * patch_width
                target_offset = target_x + target_y * y_patches * patch_width

                target[target_offset:target_offset+patch_width] = source[source_offset:source_offset+patch_width]

    data = string_at(target, patch_width*x_patches*patch_height*y_patches*4*4)
    open(filename, 'wb').write(data)
    return target

collate('material', 'snowy_mountains.diffuse')
collate('terrain', 'snowy_mountains.terrain')
