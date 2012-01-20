

import sys, os
import math
import struct
import glViewport
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

# cross product 
def cross(a, b):
    c = [a[1]*b[2] - a[2]*b[1],
         a[2]*b[0] - a[0]*b[2],
         a[0]*b[1] - a[1]*b[0]]

    return c


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


class registry(dict):
    '''
    mesh classes registry
    
    this class globaly stores its date inside glViewport module, 
    so the data is visible and up-to-date every were in the 
    application.
    
    The class is essentially a dictionary!
    
    to register a new importer class, 
    just add a new extension to it, and assign
    the class obj ptr as value:

    ex: 
        class objImporter(mesh):
            ...python code...
            ...python code...
            ....
            
        registry()['.obj', objImporter]
    '''
    import glViewport
    def __init__(self):
        dict.__init__(self)
        self.refresh()
#        for each in dir(dict):
#            exec( 'def %s(*args):\n self.refresh()\n return dict.%s(*args)' % (each, each) )
    
    def refresh(self):
        if not hasattr(glViewport, '_mesh__registry'):
            glViewport._mesh__registry = {}
        self.update(glViewport._mesh__registry)
        glViewport._mesh__registry = self
    
    def keys(self):
        self.refresh()
        return dict.keys(self)

    def __fixItem__(self, item):
        item = str(item).lower()
        if item[0] != '.':
            item = ".%s" % item
        return item
    
    def __getitem__(self,item):
        self.refresh()
        return dict.__getitem__(self,self.__fixItem__(item))

    def __setitem__(self,item,value):
        self.refresh()
        return dict.__setitem__(self,self.__fixItem__(item),value)
        
    def __str__(self):
        self.refresh()
        return dict.__str__(self)
        
    def __repr__(self):
        self.refresh()
        return dict.__repr__(self)
               
    def has_key(self,item):
        self.refresh()
        return dict.has_key(self,self.__fixItem__(item))
        
        

class mesh:
    '''
    mesh class is the base class that all importers 
    must be derivated from.

    Every importer must return a mesh derivated class 
    so our GL context can render it properly.

    The mesh class also is a loader class, used by 
    the main application to load a mesh.

    It uses registry() to find the 
    available importers, so a importer MUST 
    register its class into registry() by just 
    adding the class pointer using the extension 
    for which that importer works as an index.
    ex: 
        class objImporter(mesh):
            ...python code...
            ...python code...
            ....
            
        registry()['.obj', objImporter]
    '''
    def __init__(self, file=None):
        # bounding box variables
        self.bboxMin = [999999999,999999999,999999999]
        self.bboxMax = [-999999999,-999999999,-999999999]
        self.center = [0,0,0]
        
        # reserved to be used by importers to store the 
        # imported mesh data.
        self.model=[]
        
        # self mesh is a flag variable that 
        # identifies this obj as having a 
        # mesh loaded into it. 
        # by setting it to None, we're flaging 
        # the GL Context that this obj
        # is empty!
        self.mesh = None

        # glList stores the display list of the 
        # loaded mesh geometry
        # if the importer is not drawing the mesh using 
        # a display list, glList should be kept as None
        # WARNING: Not using display lists has a huge
        # impact if drawing speed of high polycount 
        # meshes!! We strongly recomend an importer
        # to use displaylists.
        self.glList = None
        
        # try to read a mesh, if file is passed on.
        self.read(file)

        # calculate bound box
        self.bbox()

    '''
    Virtual Methods 
    They MUST be overriden by importers!
    Every override method must call the original virtual 
    one to avoid breaking functionality!
    ======================================================'''
    def bbox(self):
        ''' virtual method 
        must be implemented by derivated classes. 
        This method should calculate and set the bounding box 
        of the current loaded mesh.
        The implemented bbox method MUST call mesh.bbox(self)
        to run any other execution that is needed, like
        calculating the center of the mesh.'''
        for n in range(3):
            self.center[n] = self.bboxMin[n]+float(self.bboxMax[n]-self.bboxMin[n])/2.0
        
    
    def render(self):
        ''' virtual method
        must be implemented by derivated class to do the render of the mesh.
        as each importer can store data on its own way, this setup makes 
        the implementation more flexible, allowing for using GL coding
        mechanisms that would speed up the render of different file formats.'''    
        if self.glList:
            GL.glCallList(self.glList)
    
    def load(self,filename):
        ''' virtual method
        must be implemented by derivated class to load the mesh'''
        pass
    

    '''
    Non-Virtual Methods - they can be override, but
    it's not necessary. 
    IF ANY OF THOSE CLASSES IS OVERRIDED, OVERRIDE CLASS
    MUST CALL THIS ORIGINAL CLASS OTHERWISE WILL BREAK 
    FUNCTIONALITY!!!
    CODE IN NON-VIRTUAL METHODS CAN AND MOST PROBABLY WILL
    CHANGE IN THE FUTURE, SO IMPORTERS MUST AVOID 
    RE-IMPLEMENTING ITS FUNCTIONALITY!!!! 
    ======================================================'''
    def refreshDisplayList(self):
        '''this method is called by GL context to force
        a mesh to update its displaylist'''
        if self.glList:
            GL.glDeleteLists( self.glList, 1)
            del self.glList 
            self.glList = None
        
    def clean(self):
        '''cleans up any memory allocation or anything else 
        this method is called by GL context when a 
        mesh is deleted or replaced by a new mesh.'''
        if self.mesh:
            self.refreshDisplayList()
            self.mesh = None
            self.bboxMin = [999999999,999999999,999999999]
            self.bboxMax = [-999999999,-999999999,-999999999]
            self.center = [0,0,0]
            mesh.bbox(self)
            
    
    def read(self, file):
        ''' using meshClasses registry, this method 
        tries to read a give model by its filename'''
        
        # clean, just in case we are re-using the same obj
        self.clean()
        
        if file:
            try:
                ext = os.path.splitext( file )[1].lower()
            except: 
                print >>sys.stderr, "ERROR: File must have an extension to identify its format!"
            finally:
                if registry().has_key( ext ):
                    # loads the mesh using the proper importer
                    # calls the virtual load method!
                    self.mesh = registry()[ ext ]()
                    self.mesh.load(file)
                else:
                    print >>sys.stderr, "ERROR: No importer for extension '%s' exists." % ext
        
        if self.mesh:        
            # if we have loaded a mesh suscessfully, 
            # we update this class object with it.
            #self = mesh
            self.refreshDisplayList = self.mesh.refreshDisplayList
            self.bboxMin = self.mesh.bboxMin
            self.bboxMax = self.mesh.bboxMax
            self.center = self.mesh.center
            self.bbox = self.mesh.bbox
            self.clean = self.mesh.clean
            self.load = self.mesh.load
            self.render = self.mesh.render
            self.render = self.mesh.render

        # refresh bbox!
        self.bbox()
        print self.bboxMin
        print self.bboxMax
            
                
