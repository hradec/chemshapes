# -*- coding: utf-8 -*-
from __future__ import with_statement

import sys, os
sys.path.append( '%s/gletools' % os.path.dirname( __file__ ) )
sys.path.append( os.path.dirname( __file__ ) )

import pyglet
from gletools import (
    Projection, Framebuffer, Texture, ShaderProgram, VertexShader, FragmentShader, Sampler2D,
    interval, quad, Group, Matrix, Screen, Ortho
)
from gletools.util import Matrix as Matrix
from gletools.gl import *

import OpenGL as gl

from glViewport import mesh

import sys

if '.stl' not in sys.argv[-1]:
    m = mesh('meshes/teapot.stl')
else:
    m = mesh(sys.argv[-1])
    
mm = 1.0
micron = mm / 1000.0 
printArea_mm = [
    225.0,
    160.0,
    300.0,
]

config = pyglet.gl.Config( alpha_size=8 )

window = pyglet.window.Window(fullscreen = False)
screen = Screen(0, 0, window.width, window.height)
ortho = Ortho( 0, window.width, 0, window.height, -100,100)
projection = Projection(0, 0, window.width, window.height)
fbo = Framebuffer(
    Texture(window.width, window.height,
        data = [0,0,0,255]*(window.width*window.height)
    )
)
fbo.textures[0].unit = GL_TEXTURE0

fbo2 = Framebuffer(
    Texture(window.width, window.height,
        data = [0,0,0,255]*(window.width*window.height)
    )
)
fbo2.textures[0].unit = GL_TEXTURE1

aspect = float(window.width)/float(window.height)
printAreaAspect = printArea_mm[0]/printArea_mm[1]

program = ShaderProgram(
    VertexShader('''
        varying vec3 normal;

        void main(void){
            gl_TexCoord[0] = gl_MultiTexCoord0;
            gl_FrontColor = gl_Color;
            normal = gl_Normal;
            gl_Position = ftransform();
        }
    '''),
    FragmentShader('''
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


depth = ShaderProgram(
    VertexShader('''
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
    FragmentShader('''
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

buffer1 = ShaderProgram(
    VertexShader('''
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
    FragmentShader('''
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
            
            slice = 1-step( sliceLevel, P[1]);
            float fr = normal.g*slice > 0 ? 1 : 0;
            gl_FragColor = vec4(fr,fr,fr,slice);
        }
    '''),
   
)
layer = 0.0
program.vars.buffer1 = Sampler2D(GL_TEXTURE0)


@window.event
def on_mouse_drag(x, y, rx, ry, button, modifier):
    global layer
    if pyglet.window.mouse.LEFT == button:
        layer -= 1
    if pyglet.window.mouse.RIGHT == button:
        layer += 1
        
@window.event
def on_key_press(symbol, modifiers):
    pass



rotation = 0.0
@interval(0.03)
def simulate(delta):
        global rotation
        rotation += 40.0 * delta

        global layer
        layer -=1
#        print m.bboxMin, m.bboxMax
        xrange = (m.bboxMax[0]-m.bboxMin[0])*0.5
        yrange = (m.bboxMax[1]-m.bboxMin[1])*0.5
        zrange = (m.bboxMax[2]-m.bboxMin[2])
        
        objAspect = xrange/yrange
        x = xrange*aspect
        y = yrange*objAspect
        xmin = -x
        ymin = -y
        
        x = printArea_mm[0]/10.0
        y = printArea_mm[1]/10.0
        
        _micron = micron /10.0
        _layer = _micron * 100.0
        
        buffer1.vars.bboxSize = [
            m.bboxMax[0]-m.bboxMin[0],
            m.bboxMax[1]-m.bboxMin[1],
            m.bboxMax[2]-m.bboxMin[2],
        ]
        buffer1.vars.layer = layer*_layer
        #layer -= 1
        buffer1.vars.layerThick = _layer*50
        
#        ortho = Ortho( -x*aspect*0.5, x*aspect*0.5, -y*0.5*printAreaAspect, y*0.5*printAreaAspect, -10000,10000)
        ortho = Ortho( -x*0.5, x*0.5, -y*0.5, y*0.5, -100000,100000)
        
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

        glColor4f(0,0,0,1)
        with Group( fbo, ortho, buffer1, Matrix ):
            glEnable(GL_BLEND)        
#            glEnable(GL_MULTISAMPLE)
#            glSampleCoverage(0.1, True)
            glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA )

            glRotated( 90.0, 1.0, 0.0, 0.0 )
#            glScalef(0.8,  0.8, 0.8)
            m.render()


    
@window.event
def on_draw():
    window.clear()
    with Group(fbo.textures[0], projection, program, Matrix):
        glTranslatef(0, 0, -1.92)
        quad(-aspect,-1, aspect,1)
#        quad(0.0, window.width)


if __name__ == '__main__':
    glEnable(GL_LINE_SMOOTH)
    pyglet.app.run()
