
from mesh import *


class stl( mesh ):
    def load(self,filename):
        '''load stl file.
        detects if the file is a text file or binary file'''
        
        #read start of file to determine if its a binay stl file or a ascii stl file
        fp=open(filename,'rb')
        h=fp.read(80)
        type=h[0:5]
        fp.close()

        if type=='solid':
            print "reading text file"+str(filename)
            self.load_text_stl(filename)
        else:
            print "reading binary stl file "+str(filename,)
            self.load_binary_stl(filename)
        
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

        self.center = [0,0,0]
        for n in range(3):
            self.bboxMax[n] = self.bboxMax[n] / 10
            self.bboxMin[n] = self.bboxMin[n] / 10
            self.center[n] = self.bboxMin[n]+float(self.bboxMax[n]-self.bboxMin[n])/2.0
            
      
    #draw the models faces
    def render(self):
        if not self.glList:
#            GL.glDeleteLists(1,0)
            self.glList = GL.glGenLists(1)
            GL.glNewList(self.glList, GL.GL_COMPILE)
            GL.glBegin(GL.GL_TRIANGLES)

            for tri in self.model: #self.get_triangles():
                GL.glNormal3f(tri.normal.x,tri.normal.z,tri.normal.y)
                GL.glVertex3f(tri.points[0].x/10-self.center[0],tri.points[0].z/10-self.bboxMin[2],tri.points[0].y/10-self.center[1])
                GL.glVertex3f(tri.points[1].x/10-self.center[0],tri.points[1].z/10-self.bboxMin[2],tri.points[1].y/10-self.center[1])
                GL.glVertex3f(tri.points[2].x/10-self.center[0],tri.points[2].z/10-self.bboxMin[2],tri.points[2].y/10-self.center[1])
            GL.glEnd()
            GL.glEndList()
        mesh.render(self)
  

    #return the faces of the triangles
    def get_triangles(self):
        if self.model:
            for face in self.model:
                yield face

  
    #read text stl match keywords to grab the points to build the model
    def load_text_stl(self,filename):
        fp=open(filename,'r')

        self.model = []
        self.glList = None
        
        for line in fp.readlines():
            words=line.split()
            if len(words)>0:
                if words[0]=='solid':
                    self.name=words[1]

                if words[0]=='facet':
                    center=[0.0,0.0,0.0]
                    triangle=[]
                    try:
                        normal=(eval(words[2]),eval(words[3]),eval(words[4]))
                    except:
                        normal=(0,0,0) 
                  
                if words[0]=='vertex':
                    triangle.append((eval(words[1]),eval(words[2]),eval(words[3])))
                  
                  
                if words[0]=='endloop':
                    #make sure we got the correct number of values before storing
                    if len(triangle)==3:
                        self.model.append(createtriangle(triangle[0],triangle[1],triangle[2],normal))
        fp.close()

    #load binary stl file check wikipedia for the binary layout of the file
    #we use the struct library to read in and convert binary data into a format we can use
    def load_binary_stl(self,filename):
        fp=open(filename,'rb')
        h=fp.read(80)

        l=struct.unpack('I',fp.read(4))[0]
        count=0
        self.model = []
        self.glList = None
        while True:
            try:
                p=fp.read(12)
                if len(p)==12:
                    n=struct.unpack('f',p[0:4])[0],struct.unpack('f',p[4:8])[0],struct.unpack('f',p[8:12])[0]
                  
                p=fp.read(12)
                if len(p)==12:
                    p1=struct.unpack('f',p[0:4])[0],struct.unpack('f',p[4:8])[0],struct.unpack('f',p[8:12])[0]

                p=fp.read(12)
                if len(p)==12:
                    p2=struct.unpack('f',p[0:4])[0],struct.unpack('f',p[4:8])[0],struct.unpack('f',p[8:12])[0]

                p=fp.read(12)
                if len(p)==12:
                    p3=struct.unpack('f',p[0:4])[0],struct.unpack('f',p[4:8])[0],struct.unpack('f',p[8:12])[0]

                new_tri=(n,p1,p2,p3)

                if len(new_tri)==4:
                    tri=createtriangle(p1,p2,p3,n)
                    self.model.append(tri)
                count+=1
                fp.read(2)

                if len(p)==0:
                    break
            except EOFError:
                break
        fp.close()

# register this importer class!
registry()['.stl'] = stl

