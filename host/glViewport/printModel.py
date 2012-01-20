

from __future__ import with_statement
import sys, os, time

from ctypes import util
if 'win32' in sys.platform.lower() :
    try:
        from OpenGL.platform import win32
    except AttributeError:
        pass

import pyglet
import gletools
#from gletools import (
#    Projection, Framebuffer, Texture, ShaderProgram, VertexShader, FragmentShader, Sampler2D,
#    interval, quad, Group, Matrix, Screen, Ortho
#)
from gletools.util import Matrix as Matrix
from gletools.gl import *

import OpenGL as gl

from glViewport import mesh

import prefs




buffer1 = gletools.ShaderProgram(
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
        //    normal = (gl_ModelViewMatrixInverse *  gl_Vertex).xyz;
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
            float slice = 100.0*smoothstep(sliceLevel-sliceSize*2.0,sliceLevel,P[1]) * (1.0-smoothstep(sliceLevel,sliceLevel+sliceSize*2.0,P[1]));


            vec3 I = eye-P.xyz;
            
            
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
        }
    '''),
   
)

class printModel(pyglet.window.Window):
    def __init__(self, machinePrefs = prefs.cs1, fullscreen = True, filename=None, model=None, screen=None, width=600, height=600):
        # initialize pyglet base class
#        display = pyglet.window.get_platform().get_default_display()
#        screens = display.get_screens()
#        print screens 
#        sys.stdout.flush()
        if fullscreen:
            pyglet.window.Window.__init__(self,fullscreen = True, screen=screen)
            self.set_exclusive_mouse()
        else:
            pyglet.window.Window.__init__(self,fullscreen = False, screen=screen, width=width, height=height)
            self.set_exclusive_mouse()

        # initialize printer preferences (default CS1)
        self.prefs = machinePrefs()
        
        # bind Model!
        if not model:
            raise Exception( "No model loaded to print. Please load a model first, then try a print!" )
        self.m = model[0]
        
        self.m = mesh(filename)
        
        # setup frambuffer
        #self.config = pyglet.gl.Config( alpha_size=8 )
        self.win = self #pyglet.window.Window(fullscreen = fullscreen)
        self.ortho = gletools.Ortho( 0, self.width, 0, self.height, -100,100)
        self.projection = gletools.Projection(0, 0, self.width, self.height)
        
        # set Frame Buffer Objects (render to textures)
        self.fbo = gletools.Framebuffer(
            gletools.Texture( self.width, self.height, data = [0,0,0,255]*(self.width*self.height) )
        )
        self.fbo.textures[0].unit = GL_TEXTURE0

        self.fbo2 = gletools.Framebuffer(
            gletools.Texture( self.width, self.height, data = [0,0,0,255]*(self.width*self.height) )
        )
        self.fbo2.textures[0].unit = GL_TEXTURE1

        # setup aspect ratio correction
        self.winAspect = float(self.width)/float(self.height)
        self.printerAspect = self.prefs.printerAspect()
        
        # load shaders
        self.loadShaders()

        # setup shader variables
        self.layer = 0.0
        self.shaderProgram.vars.buffer1 = gletools.Sampler2D(GL_TEXTURE0)
        self.rotation = 0.0
        
        self.timer = None
                

    def createDrawableObjects(self):
        pass
    def adjustWindowSize(self):
        pass
    def moveObjects(self, t):
        pass


    def run(self):
        pyglet.app.run()
        
    def loadShaders(self):
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
        

