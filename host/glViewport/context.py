
from __future__ import with_statement
import gletools
import prefs

class context:
    def __init__(self, parent, machinePrefs = prefs.cs1, filename=None, model=None, screen=None):
        # initialize printer preferences (default CS1)
        self.prefs = machinePrefs()
        
        # bind Model!
        if filename:
            self.m = mesh(filename)
        else:
            self.m = model

        # update width/height methods
        self.parent = parent
        self.width  = self.parent.width
        self.height = self.parent.height
        
        # setup frambuffer
        #self.config = pyglet.gl.Config( alpha_size=8 )
        self.ortho = gletools.Ortho( 0, self.width(), 0, self.height(), -100,100)
        self.projection = gletools.Projection(0, 0, self.width(), self.height())

        # set fbos to render in 
        self.initFBO()
        
        # refresh aspect ratio variables
        self.aspectRefresh()
        
        # load shaders
        self.loadShaders()

    def aspectRefresh(self):
        '''# setup aspect ratio correction'''
        self.winAspect = float(self.width())/float(self.height())
        self.printerAspect = self.prefs.printerAspect()

    def initFBO(self):
        ''' set Frame Buffer Objects (render to textures) fbo'''
        self.fbo = gletools.Framebuffer(
            gletools.Texture( self.width(), self.height(), data = [0,0,0,255]*(self.width()*self.height()) )
        )
        self.fbo.textures[0].unit = GL_TEXTURE0

        # fbo2
        self.fbo2 = gletools.Framebuffer(
            gletools.Texture( self.width(), self.height(), data = [0,0,0,255]*(self.width()*self.height()) )
        )
        self.fbo2.textures[0].unit = GL_TEXTURE1

    def loadShaders(self):
        # setup shader variables
        self.layer = 0.0
        self.shaderProgram.vars.buffer1 = gletools.Sampler2D(GL_TEXTURE0)
        self.rotation = 0.0
        
        self.timer = None

        
        self.shaderProgram = gletools.ShaderProgram(
            gletools.VertexShader('''
                varying vec3 normal;

                void main(void){
                    gl_TexCoord[0] = gl_MultiTexCoord0;
                    gl_FrontColor = gl_Color;
                    normal = gl_Normal;
                    gl_Position = ftransform();
                }
            '''),
            gletools.FragmentShader('''
                uniform vec3 color;
                uniform vec3 ambient;
                uniform vec3 direction;
                varying vec3 normal;
                
                uniform sampler2D buffer1;

                void main(){
                    vec3 surface_normal = normalize(normal);
                    vec3 incident_direction = normalize(direction);
                    float dot_surface_incident = dot(surface_normal, incident_direction);
                    vec3 diffuse = color * gl_Color.rgb * dot_surface_incident;
                    gl_FragColor.rgb = texture2D( buffer1, gl_TexCoord[0].st * vec2(1,-1) ).rgb; //diffuse + ambient;
                    gl_FragColor.w = gl_Color.w;
                }
            ''')
        )
        
        self.shaderDepth = gletools.ShaderProgram(
            gletools.VertexShader('''
                varying vec4 P;
                varying vec3 normal;
                varying vec3 eye;
                uniform vec4 bboxSize;
                
                void main()
                {   
                //    float theta = 0.785;
                //    float cost = cos(theta);
                //    float sint = sin(theta);
                //    vec4 vertex = vec4(
                //        gl_Vertex.x * cost - gl_Vertex.y * sint,
                //        gl_Vertex.x * sint + gl_Vertex.y * cost,
                //        gl_Vertex.z,
                //        gl_Vertex.w / 30.0);
                    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
                    P =  gl_ProjectionMatrixInverse*gl_Vertex;
                    normal = normalize(gl_NormalMatrix * gl_Normal);
                //    normal = (gl_ProjectionMatrixInverse *  gl_Vertex).xyz;
                //    normal = (gl_NormalMatrix *  gl_Vertex.xyz);
                    eye = (gl_ModelViewMatrixInverse * vec4(0.0,0.0,0.0,1.0)).xyz ;
                    
                    
                }
            '''),
            gletools.FragmentShader('''
                varying vec3 normal;
                varying vec4 P;
                varying vec3 eye;
                uniform float layer;
                uniform float layerThick;
                uniform vec3 bboxSize;

                void main()
                {
                    float sliceSize = layerThick;
                    float sliceLevel = layer ;
                    float slice = 100.0*smoothstep(sliceLevel-sliceSize*2.0,sliceLevel,P[1]) ; //* (1.0-smoothstep(sliceLevel,sliceLevel+sliceSize*2.0,P[1]));

                    vec3 I = eye-P.xyz;
                    
                    
                    
                    
                    float light = dot(normalize(vec3(1,1,0)),normalize(normal.rgb))*0.5+0.5;
                    //light = dot(normalize(I), normalize(normal.rgb));
                    
                    light = light<0.0 ? 0.0 : light;
                    //light = 1.0-light;
                //    light = step(0.95,abs(dot(normalize(I), normalize(normal.rgb))))*0.5+0.5;
                    
                    vec4 color = vec4( light*1.2, light*0.1, 0.0, 0.3 );
                    gl_FragColor = vec4(slice,slice,slice,slice);
                }
            '''),
           
        )
        path = os.path.dirname( __file__ )
        self.shaderBuffer1 = gletools.ShaderProgram(
            gletools.VertexShader( ''.join(open('%s/slicer.vert' % path).readlines()) ),
            gletools.FragmentShader('''
                //varying vec3 normal;
                varying vec4 P;
                //varying vec3 eye;
                uniform float layer;
                uniform float layerThick;
                uniform vec3 bboxSize;
                varying vec3 _V;
                varying vec3 _N;

                void main()
                {
                    float sliceSize = layerThick;
                    float sliceLevel = layer ;
                    float slice = 100.0*smoothstep(sliceLevel-sliceSize*2.0,sliceLevel,P[1]) * (1.0-smoothstep(sliceLevel,sliceLevel+sliceSize*2.0,P[1]));


                    vec3 I = -vec3(_V);
                    vec3 normal = _N;
                    
                    float light = dot(normalize(vec3(1,1,0)),normalize(normal.rgb))*0.5+0.5;
                    //light = dot(normalize(I), normalize(normal.rgb));
                    
                    light = light<0.0 ? 0.0 : light;
                    //light = 1.0-light;
                //    light = step(0.95,abs(dot(normalize(I), normalize(normal.rgb))))*0.5+0.5;
                    
                    vec4 color = vec4( light*1.2, light*0.1, 0.0, 0.3 );
                    //gl_FragColor = vec4(slice,slice,1,slice);
                    
                    slice = 1.0-step( sliceLevel, P[1]);
                    float fr = normal.g*slice > 0.0 ? 1.0 : 0.0;
                    gl_FragColor = vec4(fr,fr,fr,slice);
                    gl_FragColor = vec4(1.0,1.0,1.0,1.0);
                }
            '''),
           
        )

#        path = os.path.dirname(__file__) 
#        self.shaderBuffer1 = gletools.ShaderProgram(
#            gletools.VertexShader( ''.join(open('%s/slicer.vert' % path).readlines()) ),
#            gletools.FragmentShader( ''.join(open('%s/slicer.frag' % path).readlines()) ),
           
#        )


    def on_mouse_drag(self, x, y, rx, ry, button, modifier):
        pass
    
    def on_mouse_press(self, x, y, button, modifiers):
        if pyglet.window.mouse.LEFT == button:
            self.layer -= 1
        if pyglet.window.mouse.RIGHT == button:
            self.layer += 1
        
    def on_mouse_release(self, x, y, button, modifiers):
        pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pass
        
    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.RETURN:
            self.layer += 1
        if symbol == pyglet.window.key.ESCAPE:
#            pyglet.app.exit()
            self.close()

    
    def simulate(self, delta):
            print self.layer
            self.rotation  += 40.0 * delta


            self.layer -=1
    #        print m.bboxMin, m.bboxMax
            xrange = (self.m.bboxMax[0]-self.m.bboxMin[0])*0.5
            yrange = (self.m.bboxMax[1]-self.m.bboxMin[1])*0.5
            zrange = (self.m.bboxMax[2]-self.m.bboxMin[2])
            
            objAspect = xrange/yrange
            x = xrange*self.winAspect
            y = yrange*objAspect
            xmin = -x
            ymin = -y
            
            x = self.prefs.printArea_mm().x/10.0
            y = self.prefs.printArea_mm().z/10.0
             
            mm = 1.0
            micron = mm / 1000.0 
            _micron = micron /10.0
            _layer = _micron * 100.0
            
#            self.shaderBuffer1.vars.bboxSize = [
#                float(self.m.bboxMax[0])-float(self.m.bboxMin[0]),
#                float(self.m.bboxMax[1])-float(self.m.bboxMin[1]),
#                float(self.m.bboxMax[2])-float(self.m.bboxMin[2])
#                #float(1.0)
#            ]
            
            #print self.shaderBuffer1.vars.keys()
            
            
    #        ortho = Ortho( -x*aspect*0.5, x*aspect*0.5, -y*0.5*printAreaAspect, y*0.5*printAreaAspect, -10000,10000)
            ortho = gletools.Ortho( -x*0.5, x*0.5, -y*0.5, y*0.5, -100000,100000)
            
    #        glColor4f(0,0,1,1)
    #        with Group( fbo, ortho, Matrix ):
    #            glEnable(GL_BLEND)        
    #            glEnable(GL_MULTISAMPLE)
    #            glSampleCoverage(0.1, True)
    #            glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA )
    #            glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    #            glRotated( 90.0, 1.0, 0.0, 0.0 )
    ##            glScalef(1.1,  1.1, 1.1)
    #            m.render()

            glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA )
            glEnable(GL_BLEND)        
#            glEnable(GL_MULTISAMPLE)
#            glSampleCoverage(0.1, True)

#            print dir(self.fbo)
#            self.fbo.bind(self.fbo.id)
            
            with gletools.Group( self.fbo, ortho, self.shaderBuffer1, Matrix ):
                glColor4f(1,1,1,1)
                self.clear()
                self.shaderBuffer1.vars.layer = float(self.layer*_layer)
                #layer -= 1
                self.shaderBuffer1.vars.layerThick = float(_layer)

                #glRotated( 90.0, 1.0, 0.0, 0.0 )
    #            glScalef(0.8,  0.8, 0.8)
                self.m.render()


        
    def on_draw(self):
        self.clear()
        with gletools.Group(self.fbo.textures[0], self.projection, self.shaderProgram, Matrix):
            glTranslatef(0, 0, -1.92)
            gletools.quad(-self.winAspect,-1, self.winAspect,1)
    #        quad(0.0, window.width)

        if not self.timer:
            pyglet.clock.schedule_interval(self.simulate, 0.3)






        
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
        try:
            self.shader.uniformf( 'bboxSize', self.vec[0], self.vec[1], self.vec[2], thickness)
            self.shader.uniformf( 'bboxMin', self.mesh.bboxMin[0], self.mesh.bboxMin[1], self.mesh.bboxMin[2], 1.0)
            self.shader.uniformf( 'bboxMax', self.mesh.bboxMax[0], self.mesh.bboxMax[1], self.mesh.bboxMax[2], 1.0)
        except:
            pass
        
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
    

