
import sys, os
import math
import struct
import time

try:
    from PySide import QtCore, QtGui, QtOpenGL
except:
    from PyQt4 import QtCore, QtGui, QtOpenGL

try:
    from OpenGL import GL
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "OpenGL hellogl",
                            "PyOpenGL must be installed to run this example.",
                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
                            QtGui.QMessageBox.NoButton)
    sys.exit(1)


def timePrint(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60);
    return "%d:%02d:%02d" % (h, m, s)

#class for a 3d point
class createpoint:
    def __init__(self,p,c=(1,0,0)):
        self.point_size=0.5
        self.color=c
        self.x=p[0]
        self.y=p[1]
        self.z=p[2]

    def glvertex(self):
        GL.glVertex3f(self.x,self.y,self.z)

#class for a 3d face on a model
class createtriangle:
    points=None
    normal=None

    def __init__(self,p1,p2,p3,n=None):
        #3 points of the triangle
        self.points=createpoint(p1),createpoint(p2),createpoint(p3)

        #triangles normal
        self.normal=createpoint(self.calculate_normal(self.points[0],self.points[1],self.points[2]))#(0,1,0)#

    #calculate vector / edge
    def calculate_vector(self,p1,p2):
        return p2.x-p1.x,p2.y-p1.y,p2.z-p1.z

    def calculate_normal(self,p1,p2,p3):
        a=self.calculate_vector(p3,p2)
        b=self.calculate_vector(p3,p1)
        #calculate the cross product returns a vector
        return self.cross_product(a,b)

    def cross_product(self,p1,p2):
        return (p1[1]*p2[2]-p2[1]*p1[2]) , (p1[2]*p2[0])-(p2[2]*p1[0]) , (p1[0]*p2[1])-(p2[0]*p1[1])


class stl:
#    model = []
    def __init__(self, file):
        self.bboxMin = [999999999,999999999,999999999]
        self.bboxMax = [-999999999,-999999999,-999999999]
        self.model=[]
        self.glList = None
        self.file = file
        self.__scale = 1.0/10.0
        self.__load()

    def getFixScale(self):
        return self.__scale

    def __vectorLen(self, v):
        return math.sqrt(
            (v[0]*v[0]) +
            (v[1]*v[1]) +
            (v[2]*v[2])
        )

    def feedBBox(self, v):
        for n in range(3):
            if v[n] < self.bboxMin[n]:
                self.bboxMin[n] = v[n]
            if v[n] > self.bboxMax[n]:
                self.bboxMax[n] = v[n]

    def bboxLen(self):
        return [self.bboxMax[0]-self.bboxMin[0],self.bboxMax[1]-self.bboxMin[1],self.bboxMax[2]-self.bboxMin[2]]

    def fixSmallModels(self):
        bboxLen = self.__vectorLen( self.bboxLen() )
        if( bboxLen < 20 ):
            self.__scale = 1.0
        #auto scale!!
        #self.__scale = 10.0/bboxLen


    def bbox(self):
        for tri in self.get_triangles():
            for n in range(3):
                if tri.points[n].x < self.bboxMin[0]:
                    self.bboxMin[0] = tri.points[n].x
                if tri.points[n].y < self.bboxMin[1]:
                    self.bboxMin[1] = tri.points[n].y
                if tri.points[n].z < self.bboxMin[2]:
                    self.bboxMin[2] = tri.points[n].z

                if tri.points[n].x > self.bboxMax[0]:
                    self.bboxMax[0] = tri.points[n].x
                if tri.points[n].y > self.bboxMax[1]:
                    self.bboxMax[1] = tri.points[n].y
                if tri.points[n].z > self.bboxMax[2]:
                    self.bboxMax[2] = tri.points[n].z
        self.bboxCenter()
        self.updateBBoxValues()

    def bboxCenter(self):
        self.bboxCenter = [0,0,0]
        for n in range(3):
            self.bboxMax[n] = self.bboxMax[n] #/ 10
            self.bboxMin[n] = self.bboxMin[n] #/ 10
            self.bboxCenter[n] = self.bboxMin[n]+float(self.bboxMax[n]-self.bboxMin[n])/2.0
        return self.bboxCenter



    #return the faces of the triangles
    def get_triangles(self):
        if self.model:
            for face in self.model:
                yield face

    #draw the models faces
    def render(self):
        if not self.glList:
#            GL.glDeleteLists(1,0)
            self.glList = GL.glGenLists(1)
            GL.glNewList(self.glList, GL.GL_COMPILE)
            GL.glBegin(GL.GL_TRIANGLES)

            for tri in self.model: #self.get_triangles():
                GL.glNormal3f(tri.normal.x,tri.normal.z,tri.normal.y)
                for fv in range(3):
                    GL.glVertex3f(
                        ( tri.points[fv].x - self.bboxCenter[0] ),
                        ( tri.points[fv].z - self.bboxMin[2]    ),
                        ( tri.points[fv].y - self.bboxCenter[1] ),
                    )
            GL.glEnd()
            GL.glEndList()
        GL.glCallList(self.glList)


    def __load(self):
        self.__scale = 1.0/10.0
        self.model = []
        if self.glList:
            GL.glDeleteLists( self.glList, 1)
            del self.glList
            self.glList = None
        self.loadStartTime = time.time()
        self.load()
#        self.bbox()
        self.bboxCenter()
        self.fixSmallModels()
        print "Read in %s seconds." % timePrint( time.time() - self.loadStartTime ); sys.stdout.flush()


    #load stl file detects if the file is a text file or binary file
    def load(self):
        #read start of file to determine if its a binay stl file or a ascii stl file
        fp=open(self.file,'rb')
        h=fp.read(80)
        type=h[0:5]
        fp.close()


        if type=='solid':
            print "Loading text stl: "+str(self.file); sys.stdout.flush()
            self.load_text_stl(self.file)
        else:
            print "Loading binary stl: "+str(self.file); sys.stdout.flush()
            self.load_binary_stl(self.file)

    def addTriangle(self, *triangle ):
#        self.feedBBox(triangle[0])
#        self.feedBBox(triangle[1])
#        self.feedBBox(triangle[2])
        self.model.append( createtriangle(triangle[0],triangle[1],triangle[2]) )

    #read text stl match keywords to grab the points to build the model
    def load_text_stl(self,filename):
        fp=open(filename,'r')


        for line in fp.readlines():
            words=line.split()
#            print words
            if len(words)>0:
                if words[0]=='solid':
                    self.name=words[1]

                if words[0]=='facet':
                    center=[0.0,0.0,0.0]
                    triangle=[]
                    try:
                        normal=(float(words[2]),float(words[3]),float(words[4]))
                    except:
                        normal=(0,0,0)

                if words[0]=='vertex':
                    v = (float(words[1]),float(words[2]),float(words[3]))
                    triangle.append(v)
                    self.feedBBox(triangle[-1])


                if words[0]=='endloop':
                    #make sure we got the correct number of values before storing
                    if len(triangle)==3:
                        self.addTriangle( *triangle )
        fp.close()

    #load binary stl file check wikipedia for the binary layout of the file
    #we use the struct library to read in and convert binary data into a format we can use
    def load_binary_stl(self,filename):
        fp=open(filename,'rb')
        h=fp.read(80)

        l=struct.unpack('I',fp.read(4))[0]
        self.model = []
        self.glList = None
        while True:
            try:
                PsAndN = []
                for each in range(4):
                    p=fp.read(12)
                    if len(p)==12:
                        PsAndN.append( ( struct.unpack('f',p[0:4])[0],struct.unpack('f',p[4:8])[0],struct.unpack('f',p[8:12])[0] ) )
                        self.feedBBox( PsAndN[-1] )

                if PsAndN:
                    self.addTriangle( PsAndN[1],PsAndN[2],PsAndN[3] )
                fp.read(2)

                if len(p)==0:
                    break
            except EOFError:
                break
        fp.close()

