varying vec4 P;
varying vec3 _V;
varying vec3 _N;
varying vec3 normal;
varying vec4 eyenormal;
varying vec4 eye;
varying vec4 Peye;
uniform vec4 bboxSize;

void main()
{   


    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    P = gl_ProjectionMatrix * gl_Vertex.xyzw;
    
    _N = normalize(gl_NormalMatrix*gl_Normal); 
	_V = -vec3(gl_ModelViewMatrix*gl_Vertex);
    
//    _N = gl_Normal; 
//	_V = gl_Vertex;
}

