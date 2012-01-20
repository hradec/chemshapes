
from prefs import mm

class cs1:
    class printArea_mm:
        x = mm(225.0)
        y = mm(160.0)
        z = mm(300.0)
        
    def __init__(self):
        self.__printAreaAspect = self.printArea_mm.x/self.printArea_mm.y
                    
    def printerAspect(self):
        return self.__printAreaAspect 
        
    
