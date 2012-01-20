
import sys, os
import math
try:
    from PySide import QtCore, QtGui, QtOpenGL
except:
    from PyQt4 import QtCore, QtGui, QtOpenGL
    
sys.path.append( '%s/gletools' % os.path.dirname( os.path.dirname( __file__ )) )


from ctypes import util
try:
    from OpenGL.platform import win32
except AttributeError:
    pass

try:
    from OpenGL import GL
    from OpenGL import GLU as glu
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "OpenGL hellogl",
                            "PyOpenGL must be installed to run this example.",
                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
                            QtGui.QMessageBox.NoButton)
    sys.exit(1)


from mesh import *
import stl, obj

import pyglet_shaders 
import gletools
import prefs
        

class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        QtOpenGL.QGLWidget.__init__(self, parent)

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
            
        
    def resetCamera(self):
#        self.xRot = 0
#        self.yRot = 0
#        self.zRot = 0
#        self.zoom = -10.0
        self.xPos = 0
        self.yPos = 0

    def xRotation(self):
        return self.xRot

    def yRotation(self):
        return self.yRot

    def zRotation(self):
        return self.zRot

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    def setXRotation(self, angle):
        angle = self.normalizeAngle(angle)
#        if angle != self.xRot:
        self.xRot = angle
        self.emit(QtCore.SIGNAL("xRotationChanged(int)"), angle)
        self.updateGL()

    def setYRotation(self, angle):
        angle = self.normalizeAngle(angle)
#        if angle != self.yRot:
        self.yRot = angle
        self.emit(QtCore.SIGNAL("yRotationChanged(int)"), angle)
        self.updateGL()

    def setZRotation(self, angle):
        angle = self.normalizeAngle(angle)
#        if angle != self.zRot:
        self.zRot = angle
        self.emit(QtCore.SIGNAL("zRotationChanged(int)"), angle)
        self.updateGL()

    def addMesh( self, mesh ):
        while len(self.meshs)>0:
            for each in range(len(self.meshs)):
                del self.meshs[each]
            
        self.meshs = []
        self.meshs.append(mesh)
        #self.zoom = mesh.bboxMin[2] * (mesh.bboxMax[2] - mesh.bboxMin[2]) * 2
        self.center = [0,0,0] 
        self.vec = [0,0,0]
        self.lenght = 0
        for i in range(3):
            x = float(mesh.bboxMax[i] - mesh.bboxMin[i])
            self.center[i] = mesh.bboxMin[i] + (x/2.0)
            self.vec[i] = x
            self.lenght += self.vec[i]*self.vec[i]
        self.lenght = math.sqrt(self.lenght)
        self.resizeLength = 10/self.lenght
            
        #self.yPos = (mesh.bboxMin[1] - mesh.bboxMax[1])/2.0
#        self.zCamera = ((self.vec[1]*self.resizeLength)/2.0)+((self.lenght*self.resizeLength)*2)
        self.resetCamera()
        self.updateGL()
        
    def install_shaders(self):
        def read_source(fname):
            f = open(fname)
            try:
                src = f.read()
            finally:
                f.close()
            return src

        f=__file__
        if hasattr(sys,'frozen'):
            f = './.'
    
        self.s = {}
        self.fshader = {}
        self.vshader = {}
        for each in ['slicer', 'normal']:
            fragment = '%s/%s.frag' % (os.path.dirname( f ), each)
            vertex = '%s/%s.vert' % (os.path.dirname( f ), each)

            fsrc = read_source(fragment)
            self.fshader[each] = pyglet_shaders.FragmentShader([fsrc])

            vsrc = read_source(vertex)
            self.vshader[each] = pyglet_shaders.VertexShader([vsrc])

            self.s[each] = pyglet_shaders.ShaderProgram(self.fshader[each], self.vshader[each])

            self.s[each].use()
        self.shader = self.s['slicer']


    def initializeGL(self):
#        self.qglClearColor(self.trolltechPurple.darker())
        #self.object = self.makeObject()
        
        self.clearColor = [0.3,0.3,0.5,1]
        GL.glClearColor(*self.clearColor)

        GL.glShadeModel(GL.GL_FLAT)
#        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LEQUAL)
        
        GL.glEnable(GL.GL_BLEND)        
        

        GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, (5.0, 15.0, 10.0, 1.0))
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_LIGHT0)
        
        GL.glEnable(GL.GL_NORMALIZE)
        
        self.install_shaders()
        self.makeObject()
        self.resizeGL()


    def paintGL(self):
        GL.glColor4f(0.3,0.3,0.7,1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        if self.zCamera <= -25:
            self.zCamera = -25.0

        GL.glLoadIdentity()
#        glu.gluLookAt (0,5, self.zCamera , self.center[0]*self.resizeLength, self.center[1]*self.resizeLength, self.center[2]*self.resizeLength, 0.0, 1.0, 0.0);
        glu.gluLookAt ( 0, 5, 30+self.zCamera, 0, 3.0+self.zCamera/20.0, 0, 0.0, 1.0, 0.0 );
        
        GL.glTranslated(self.xPos, self.yPos, 0 )
        GL.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        GL.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        GL.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)



#        self.qglColor(self.trolltechGreen)
#        GL.glScale( self.resizeLength, self.resizeLength, self.resizeLength )

        GL.glBlendFunc( GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA  )
#        GL.glBlendFunc( GL.GL_ONE, GL.GL_ONE )
            
            
        GL.glPushMatrix()
        self.s['slicer'].bind()
        self.shader.uniformf( 'clearColor', *self.clearColor )
        self.shader.uniformf( 'transform', self.moveOBJ[0], self.moveOBJ[1], self.moveOBJ[2], 0.0 )
        self.shader.uniformf( 'rotateAngles', self.rotateOBJ[0], self.rotateOBJ[1], self.rotateOBJ[2], 0.0 )
        self.shader.uniformf( 'scale', self.scaleOBJ[0]*self.unit , self.scaleOBJ[1]*self.unit , self.scaleOBJ[2]*self.unit , 1.0 )
        
#        GL.glTranslated( self.moveOBJ[0], self.moveOBJ[1], self.moveOBJ[2] )
#        GL.glRotated(self.rotateOBJ[0], 1.0, 0.0, 0.0)
#        GL.glRotated(self.rotateOBJ[1], 0.0, 1.0, 0.0)
#        GL.glRotated(self.rotateOBJ[2], 0.0, 0.0, 1.0)
#        GL.glScale( self.scaleOBJ[0]*self.unit , self.scaleOBJ[1]*self.unit , self.scaleOBJ[2]*self.unit  )
        for mesh in self.meshs:
            self.shader.uniformf( 'front', 0.0 )
            mesh.render()
            self.shader.uniformf( 'front', 1.0 )
            mesh.render()
        self.s['slicer'].unbind()
        GL.glPopMatrix()
        
        GL.glBlendFunc( GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA )
        self.s['normal'].bind()
        GL.glCallList(1)
        self.s['normal'].unbind()
                    
        self.s['slicer'].bind()

    def resizeGL(self, width=0, height=0):
        self.__cacheNonFullScreen()
        width = float(self.parent.width())
        height = float(self.parent.height())
        side = min(width, height)
        if side == width:
            side2 = height
        else:
            side2 = width
#        GL.glViewport((width - side) / 2, (height - side) / 2, side, side)
        w = width*(height/width)
        h = height*(width/height)
#        GL.glViewport(int((width-w)/2), 0, int(w), int(height))
        GL.glViewport(0, 0, int(width), int(height) )

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        #aspect1 = float(height)/float(width)
        #aspect2 = float(width)/float(height)
        #GL.glOrtho(-0.5, +0.5, +0.5, -0.5, -1500.0, 1500.0)
        glu.gluPerspective (50.0, width/height, 2.0, 600.0);
        #GL.glFrustum(-1 , 1 , -1 , 1 , 2, 6000.0)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        
    def keyPressEvent (self, event):
        print event.key()
        sys.stdout.flush()
        self.fullScreen(False)

    def mousePressEvent(self, event):
        self.lastPos = QtCore.QPoint(event.pos())

    def mouseMoveEvent(self, event):
        dx = float( event.x() - self.lastPos.x() )
        dy = float( event.y() - self.lastPos.y() )

        if event.buttons() & QtCore.Qt.LeftButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setYRotation(self.yRot + 8 * dx)
        elif event.buttons() & QtCore.Qt.RightButton:
            self.zCamera += dx*(0.5)
            self.updateGL()
        elif event.buttons() & QtCore.Qt.MiddleButton:
            self.xyPosZoom  = ((self.zCamera+50.0)/1000.0)
            self.xPos += dx*self.xyPosZoom  
            self.yPos -= dy*self.xyPosZoom  
            self.updateGL()

        self.lastPos = QtCore.QPoint(event.pos())
        
    def wheelEvent(self, event):
        self.zCamera += event.delta()*0.05
        event.accept()
        self.updateGL()
        print self.zCamera

    def makeObject(self):
        genList = GL.glGenLists(1)
        GL.glNewList(genList, GL.GL_COMPILE)

        GL.glLineWidth(3.0)

        planeSizeX = prefs.current.printArea_mm.x

        GL.glBegin(GL.GL_QUADS)
        self.quad(
            -prefs.current.printArea_mm.x/2.0, -0.1, -prefs.current.printArea_mm.y/2.0, 
            -prefs.current.printArea_mm.x/2.0, -0.1,  prefs.current.printArea_mm.y/2.0, 
             prefs.current.printArea_mm.x/2.0, -0.1,  prefs.current.printArea_mm.y/2.0, 
             prefs.current.printArea_mm.x/2.0, -0.1, -prefs.current.printArea_mm.y/2.0,
             prefs.current.printArea_mm.x/100.0, prefs.current.printArea_mm.y/100.0)
        self.quad(
            -prefs.current.printArea_mm.x/2.0, prefs.current.printArea_mm.z, -prefs.current.printArea_mm.y/2.0, 
            -prefs.current.printArea_mm.x/2.0, prefs.current.printArea_mm.z,  prefs.current.printArea_mm.y/2.0, 
             prefs.current.printArea_mm.x/2.0, prefs.current.printArea_mm.z,  prefs.current.printArea_mm.y/2.0, 
             prefs.current.printArea_mm.x/2.0, prefs.current.printArea_mm.z, -prefs.current.printArea_mm.y/2.0,
             prefs.current.printArea_mm.x/100.0, prefs.current.printArea_mm.y/100.0)
        GL.glEnd()
        
        GL.glBegin(GL.GL_LINES)
        GL.glVertex3d(prefs.cm(prefs.mm(-prefs.current.printArea_mm.x/2.0)), -0.001, prefs.cm(prefs.mm(-prefs.current.printArea_mm.y/2.0)))
        GL.glVertex3d(prefs.cm(prefs.mm(-prefs.current.printArea_mm.x/2.0)), prefs.cm(prefs.current.printArea_mm.z), prefs.cm(prefs.mm(-prefs.current.printArea_mm.y/2.0)))

        GL.glVertex3d(prefs.cm(prefs.mm(-prefs.current.printArea_mm.x/2.0)), -0.001, prefs.cm(prefs.mm(prefs.current.printArea_mm.y/2.0)))
        GL.glVertex3d(prefs.cm(prefs.mm(-prefs.current.printArea_mm.x/2.0)), prefs.cm(prefs.current.printArea_mm.z), prefs.cm(prefs.mm(prefs.current.printArea_mm.y/2.0)))

        GL.glVertex3d(prefs.cm(prefs.mm(prefs.current.printArea_mm.x/2.0)), -0.001, prefs.cm(prefs.mm(prefs.current.printArea_mm.y/2.0)))
        GL.glVertex3d(prefs.cm(prefs.mm(prefs.current.printArea_mm.x/2.0)), prefs.cm(prefs.current.printArea_mm.z), prefs.cm(prefs.mm(prefs.current.printArea_mm.y/2.0)))

        GL.glVertex3d(prefs.cm(prefs.mm(prefs.current.printArea_mm.x/2.0)), -0.001, prefs.cm(prefs.mm(-prefs.current.printArea_mm.y/2.0)))
        GL.glVertex3d(prefs.cm(prefs.mm(prefs.current.printArea_mm.x/2.0)), prefs.cm(prefs.current.printArea_mm.z), prefs.cm(prefs.mm(-prefs.current.printArea_mm.y/2.0)))
        GL.glEnd()
        


#        self.extrude(x1, y1, x2, y2)
#        self.extrude(x2, y2, y2, x2)
#        self.extrude(y2, x2, y1, x1)
#        self.extrude(y1, x1, x1, y1)
#        self.extrude(x3, y3, x4, y4)
#        self.extrude(x4, y4, y4, x4)
#        self.extrude(y4, x4, y3, x3)

#        Pi = 3.14159265358979323846
#        NumSectors = 200

#        for i in range(NumSectors):
#            angle1 = (i * 2 * Pi) / NumSectors
#            x5 = 0.30 * math.sin(angle1)
#            y5 = 0.30 * math.cos(angle1)
#            x6 = 0.20 * math.sin(angle1)
#            y6 = 0.20 * math.cos(angle1)

#            angle2 = ((i + 1) * 2 * Pi) / NumSectors
#            x7 = 0.20 * math.sin(angle2)
#            y7 = 0.20 * math.cos(angle2)
#            x8 = 0.30 * math.sin(angle2)
#            y8 = 0.30 * math.cos(angle2)

#            self.quad(x5, y5, x6, y6, x7, y7, x8, y8)

#            self.extrude(x6, y6, x7, y7)
#            self.extrude(x8, y8, x5, y5)

#        GL.glEnd()
        GL.glEndList()

        return genList

    def quad(self, x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4, maxU, maxV):
        GL.glTexCoord2d(maxU, 0);
        GL.glVertex3d(prefs.cm(prefs.mm(x1)), prefs.cm(prefs.mm(y1)), prefs.cm(prefs.mm(z1)))
        GL.glTexCoord2d(maxU, maxV);
        GL.glVertex3d(prefs.cm(prefs.mm(x2)), prefs.cm(prefs.mm(y2)), prefs.cm(prefs.mm(z2)))
        GL.glTexCoord2d(0, maxV);
        GL.glVertex3d(prefs.cm(prefs.mm(x3)), prefs.cm(prefs.mm(y3)), prefs.cm(prefs.mm(z3)))
        GL.glTexCoord2d(0, 0);
        GL.glVertex3d(prefs.cm(prefs.mm(x4)), prefs.cm(prefs.mm(y4)), prefs.cm(prefs.mm(z4)))


    def extrude(self, x1, y1, x2, y2):
        self.qglColor(self.trolltechGreen.darker(250 + int(100 * x1)))

        GL.glVertex3d(x1, y1, +0.05)
        GL.glVertex3d(x2, y2, +0.05)
        GL.glVertex3d(x2, y2, -0.05)
        GL.glVertex3d(x1, y1, -0.05)

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle
    
    
    
