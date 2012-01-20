

from mesh import *

class obj(mesh):

    def clean(self):
        self.vertex = []
        self.faces = []
        self.normals = []
        mesh.clean(self)
        
    def load(self, file):
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
        
        self.calculateNormal( )
        mesh.load(self,file)

    def render(self):
        if not self.glList:
            self.glList = GL.glGenLists(1)
            GL.glNewList(self.glList, GL.GL_COMPILE)

            def draw():
                for each in self.faces:
                    l = None
                    for index in each:
#                        if len(index)>1:
                        normal = self.normals[ int(index[0])-1 ]
                        GL.glNormal3f( -float(normal[0]), -float(normal[1]), -float(normal[2]))
                        vertex = self.vertex[ int(index[0])-1 ]
                        GL.glVertex3f( float(vertex[0]), float(vertex[1]), float(vertex[2]))

            GL.glBegin(GL.GL_TRIANGLES)
            draw()
            GL.glEnd()
            
            GL.glEndList()
        mesh.render(self)



    def calculateNormal(self ):
        edges = {}
        for each in self.faces:
            oldVert = self.vertex[ int(each[-1][0])-1 ]
            oldId = int(each[-1][0])-1
            for index in each:
                id = int(index[0])-1
                vertex = self.vertex[ id ]
                if not edges.has_key(oldId):
                    edges[oldId] = []
                if not edges.has_key(id):
                    edges[id] = []
                e = []
                for v in range(3):
                    e.append( oldVert[v] - vertex[v] )
                edges[oldId].append( e )
                edges[id].append( e )
                oldVert = vertex
                oldId = id
                    
#            print edges
        if not self.normals:
            self.normals = {}
            for each in self.faces:
                for index in each:
                    id = int(index[0])-1
                    self.normals[id] = cross(edges[id][0], edges[id][1] )
                
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
            
    
# register this importer class!
registry()['.obj'] = obj



class obj_new(mesh):
    def load(self):
        vertex = []
        faces = []
        normal = []
        for line in open( self.file, 'r'):
            line = line.split()
            if line:
                id = line[0].lower() 
                
                # found vertex
                if id == 'v':
                    # OBJs are naturally smaller than STL for some weird reason, so we multiply then by 10!
                    vertex.append( map( lambda x: float(x)*10.0, [line[1],line[3],line[2]] ) ) 
                    # calculate bounding box
                    self.feedBBox(vertex[-1])
                    
                # found normal
#                elif id == 'vn':
#                    normal.append( map( lambda x: float(x), line[1:]) )
                    
                #found face
                elif id == 'f':
                    def face(l):
                        # faces are stored as a list divided by commas
                        # each face element can have 3 components, divide by a slash: VertexID/UV ID/Normal ID
                        ret = []
                        for each in line[1:]:
                            ret.append( int(each.split('/')[0]) ) # in our case, we only need the vertex Index
                        return ret
                    faces.append( face(line) )
                    
        # interact over faces and triangulate it, using the same mechanism of STL 
        # to store the mesh.
        for face in faces:
            lastVertexIndex = len(face)-1
            vertexIndex = 1
            while( vertexIndex < lastVertexIndex ):
                self.addTriangle(
                    vertex[face[vertexIndex+1]-1],
                    vertex[face[vertexIndex]-1],
                    vertex[face[0]-1],
                )
                vertexIndex += 1

        



            