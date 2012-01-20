

class mm(float):
    def __isUnit__(self):
        # this method exists only to identify these classes as units
        pass
    def __new__(self, vv=None):
        sign = vv/abs(vv)
        v=vv
        if v:
            value_type = str(v.__class__).split("'")[1]
            if value_type not in ['float', 'int']:
                v = abs(v)
                v *= types[ value_type ]
                v /= types[ str(self).split("'")[1] ]
                v = abs(v) * sign
            return float.__new__(self, v)
        else:
            v = 0.0
            
        return float.__new__(self, v)
        
class cm(mm):
    pass

class meter(mm):
    pass

class inch(mm):
    pass        

class micron(mm):
    pass

types = {
         str(mm).split("'")[1]     : 1.0,
         str(float).split("'")[1]  : 1.0,
         str(int).split("'")[1]    : 1.0,
         str(meter).split("'")[1]  : 1000.0,
         str(cm).split("'")[1]     : 10.0,
         str(micron).split("'")[1] : 0.001,
         str(inch).split("'")[1]   : 25.4,
}
        

__units = filter( lambda x: hasattr(eval('%s' % x), '__isUnit__'), dir() )
def units():
    table = {}
    for each in __units:
        table[each] = types[ 'prefs.%s' % each ]
    return table

        
from cs1 import *

current = cs1

