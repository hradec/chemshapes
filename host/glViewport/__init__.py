
import sys, os
import math
from PySide import QtCore, QtGui, QtOpenGL

try:
    from OpenGL import GL
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "OpenGL hellogl",
                            "PyOpenGL must be installed to run this example.",
                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
                            QtGui.QMessageBox.NoButton)
    sys.exit(1)


from stl import stl

import pyglet_shaders 
import pyglet.gl.glu  as glu

def calculateNormal( face ):
    vec

class obj:
    def __init__(self, file=None):
        self.clean()
        self.read(file)

    def clean(self):
        self.vertex = []
        self.faces = []
        self.normals = []
        self.bboxMin = [999999999,999999999,999999999]
        self.bboxMax = [-999999999,-999999999,-999999999]
        try:
            del self.genList
        except:
            pass
        self.genList = None
        
    def read(self, file):
        def face(l):
            ret = []
            for each in line.split()[1:]:
                ret.append( each.split('//') )
            return ret
        
        for line in open( file, 'r'):
            tmp = line.split()
            if tmp:
                id = tmp[0].lower() 
                if id == 'v':
                    self.vertex.append( line.split()[1:] )
                    for n in range(3):
                        self.vertex[-1][n] = float(self.vertex[-1][n])
                        if self.vertex[-1][n] < self.bboxMin[n]:
                            self.bboxMin[n] = self.vertex[-1][n]
                        if self.vertex[-1][n] > self.bboxMax[n]:
                            self.bboxMax[n] = self.vertex[-1][n]
                if id == 'vn':
                    self.normals.append( line.split()[1:] )
                if id == 'f':
                    self.faces.append( face(line) )

    def render(self):
        if not self.genList:
            self.genList = GL.glGenLists(1)
            GL.glNewList(self.genList, GL.GL_COMPILE)

            GL.glBegin(GL.GL_TRIANGLES)
            
            for each in self.faces:
                for index in each:
                    if len(index)>1:
                        normal = self.normals[ int(index[0])-1 ]
                        GL.glNormal3f( float(normal[0]), float(normal[1]), float(normal[2]))
                    vertex = self.vertex[ int(index[0])-1 ]
                    GL.glVertex3f( float(vertex[0]), float(vertex[1]), float(vertex[2]))

            GL.glEnd()
            GL.glEndList()
        GL.glCallList( self.genList )
        return self.genList



class mesh:
    def __init__(self, file=None):
        self.mesh = None
        self.bboxMin = [999999999,999999999,999999999]
        self.bboxMax = [-999999999,-999999999,-999999999]
        self.clean()
        self.read(file)
        
    def clean(self):
        if self.mesh:
            if hasattr(self.mesh, 'clean'):
                self.mesh.clean()
            del self.mesh
            self.mesh = None
    
    def read(self, file):
        if file:
            if os.path.splitext( file )[1].lower() == '.obj':
                self.mesh = obj(file)
            elif os.path.splitext( file )[1].lower() == '.stl':
                self.mesh = stl(file)
        
        if self.mesh:        
            self.render = self.mesh.render
            self.bboxMin = self.mesh.bboxMin 
            self.bboxMax = self.mesh.bboxMax
            
        

class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        QtOpenGL.QGLWidget.__init__(self, parent)

        self.meshs = []
        self.parent = parent

        self.object = 0
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        self.zoom = -10.0
        self.xPos = 0
        self.yPos = 0

        self.lastPos = QtCore.QPoint()

        self.trolltechGreen = QtGui.QColor.fromCmykF(0.40, 0.0, 1.0, 0.0)
        self.trolltechPurple = QtGui.QColor.fromCmykF(0.39, 0.39, 0.0, 0.0)

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
        if angle != self.xRot:
            self.xRot = angle
            self.emit(QtCore.SIGNAL("xRotationChanged(int)"), angle)
            self.updateGL()

    def setYRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.yRot:
            self.yRot = angle
            self.emit(QtCore.SIGNAL("yRotationChanged(int)"), angle)
            self.updateGL()

    def setZRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.emit(QtCore.SIGNAL("zRotationChanged(int)"), angle)
            self.updateGL()

    def addMesh( self, mesh ):
        while len(self.meshs)>0:
            for each in range(len(self.meshs)):
                del self.meshs[each]
            
        self.meshs.append(mesh)
        self.zoom = mesh.bboxMin[2] * (mesh.bboxMax[2] - mesh.bboxMin[2]) * 2
        self.yPos = (mesh.bboxMin[1] - mesh.bboxMax[1])/2.0
        self.updateGL()
        
    def install_shaders(self):
        fragment = '%s/slicer.frag' % os.path.dirname( __file__ )
        vertex = '%s/slicer.vert' % os.path.dirname( __file__ )
        def read_source(fname):
            f = open(fname)
            try:
                src = f.read()
            finally:
                f.close()
            return src

        fsrc = read_source(fragment)
        self.fshader = pyglet_shaders.FragmentShader([fsrc])

        vsrc = read_source(vertex)
        self.vshader = pyglet_shaders.VertexShader([vsrc])

        self.shader = pyglet_shaders.ShaderProgram(self.fshader, self.vshader)
        self.shader.use()


    def initializeGL(self):
        self.qglClearColor(self.trolltechPurple.darker())
        #self.object = self.makeObject()

        GL.glShadeModel(GL.GL_FLAT)
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_BLEND)
        
        GL.glBlendFunc( GL.GL_SRC_ALPHA, GL.GL_DST_ALPHA )
        
        GL.glDisable(GL.GL_CULL_FACE)

        GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, (5.0, 15.0, 10.0, 1.0))
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_LIGHT0)
        
        GL.glEnable(GL.GL_NORMALIZE)
        
        self.install_shaders()

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        for mesh in self.meshs:
            GL.glLoadIdentity()
            glu.gluLookAt (0.0, 0.0, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0);
            
            GL.glTranslated(self.xPos, self.yPos, self.zoom )
            GL.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
            GL.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
            GL.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
            

            self.qglColor(self.trolltechGreen)
            mesh.render()
        #GL.glCallList(self.object)

    def resizeGL(self, width, height):
        side = min(width, height)
        if side == width:
            side2 = height
        else:
            side2 = width
        GL.glViewport((width - side) / 2, (height - side) / 2, side, side)
        #GL.glViewport(0, 0, width, height)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        #aspect1 = float(height)/float(width)
        #aspect2 = float(width)/float(height)
        #GL.glOrtho(-0.5, +0.5, +0.5, -0.5, -1500.0, 1500.0)
        GL.glFrustum(-1 , 1 , -1 , 1 , 4.0, 6000.0)
        GL.glMatrixMode(GL.GL_MODELVIEW)

    def mousePressEvent(self, event):
        self.lastPos = QtCore.QPoint(event.pos())

    def mouseMoveEvent(self, event):
        dx = float( event.x() - self.lastPos.x() )
        dy = float( event.y() - self.lastPos.y() )

        if event.buttons() & QtCore.Qt.LeftButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setYRotation(self.yRot + 8 * dx)
        elif event.buttons() & QtCore.Qt.RightButton:
            self.zoom += dx/10.0
            self.updateGL()
        elif event.buttons() & QtCore.Qt.MiddleButton:
            self.xPos += dx/100.0
            self.yPos -= dy/100.0
            self.updateGL()

        self.lastPos = QtCore.QPoint(event.pos())

    def makeObject(self):
        genList = GL.glGenLists(1)
        GL.glNewList(genList, GL.GL_COMPILE)

        GL.glBegin(GL.GL_QUADS)

        x1 = +0.06
        y1 = -0.14
        x2 = +0.14
        y2 = -0.06
        x3 = +0.08
        y3 = +0.00
        x4 = +0.30
        y4 = +0.22

        self.quad(x1, y1, x2, y2, y2, x2, y1, x1)
        self.quad(x3, y3, x4, y4, y4, x4, y3, x3)

        self.extrude(x1, y1, x2, y2)
        self.extrude(x2, y2, y2, x2)
        self.extrude(y2, x2, y1, x1)
        self.extrude(y1, x1, x1, y1)
        self.extrude(x3, y3, x4, y4)
        self.extrude(x4, y4, y4, x4)
        self.extrude(y4, x4, y3, x3)

        Pi = 3.14159265358979323846
        NumSectors = 200

        for i in range(NumSectors):
            angle1 = (i * 2 * Pi) / NumSectors
            x5 = 0.30 * math.sin(angle1)
            y5 = 0.30 * math.cos(angle1)
            x6 = 0.20 * math.sin(angle1)
            y6 = 0.20 * math.cos(angle1)

            angle2 = ((i + 1) * 2 * Pi) / NumSectors
            x7 = 0.20 * math.sin(angle2)
            y7 = 0.20 * math.cos(angle2)
            x8 = 0.30 * math.sin(angle2)
            y8 = 0.30 * math.cos(angle2)

            self.quad(x5, y5, x6, y6, x7, y7, x8, y8)

            self.extrude(x6, y6, x7, y7)
            self.extrude(x8, y8, x5, y5)

        GL.glEnd()
        GL.glEndList()

        return genList

    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4):
        self.qglColor(self.trolltechGreen)

        GL.glVertex3d(x1, y1, -0.05)
        GL.glVertex3d(x2, y2, -0.05)
        GL.glVertex3d(x3, y3, -0.05)
        GL.glVertex3d(x4, y4, -0.05)

        GL.glVertex3d(x4, y4, +0.05)
        GL.glVertex3d(x3, y3, +0.05)
        GL.glVertex3d(x2, y2, +0.05)
        GL.glVertex3d(x1, y1, +0.05)

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
    
    
    
