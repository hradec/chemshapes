
from glViewport import *    

class GLWidget(context, QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        QtOpenGL.QGLWidget.__init__(self, parent)
        context.__init__(self, parent)

        self.meshs = []
        self.parent = parent

        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        self.zoom = -10.0

        self.object = 0
        
        self.lastPos = QtCore.QPoint()

        self.trolltechGreen = QtGui.QColor.fromCmykF(0.40, 0.0, 1.0, 0.0)
        self.trolltechPurple = QtGui.QColor.fromCmykF(0.39, 0.39, 0.0, 0.0)
        self.resetCamera()
        self.zCamera = 0
        self.setFocusPolicy( QtCore.Qt.StrongFocus )
        self.__fullScreen = False
        self.xyPosZoom = 100.0
        
        self.moveOBJ = [0,0,0]
        self.rotateOBJ = [0,0,0]
        self.scaleOBJ = [1,1,1]
        
        self.unit = 1.0
        self.center = [0,0,0] 
        self.vec = [0,0,0]
        self.lenght = 0
        
            
    def __cacheNonFullScreen(self):    
        if not self.__fullScreen:
            self.nonFullScreenRect  = self.size()
            self.nonFullScreenFlags = self.windowFlags()
                
    def fullScreen(self, putInFull=True):
        self.__cacheNonFullScreen()
        if putInFull:
            self.__fullScreen = True
            # Make our window without panels
            self.setWindowFlags( QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint )

            # Resize refer to desktop
            print QtGui.QApplication.desktop().size() 
            self.resize( QtGui.QApplication.desktop().size() )
            
            self.setAttribute(QtCore.Qt.WA_QuitOnClose, True)

            
#            self.showFullScreen()
        else:
            self.__fullScreen = False
            self.setWindowFlags( self.nonFullScreenFlags )
            self.resize( self.nonFullScreenRect  )
            self.setAttribute(QtCore.Qt.WA_QuitOnClose, True)
            
        self.app.processEvents()
        self.show()
        self.setFocus()
            
