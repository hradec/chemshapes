//varying vec3 normal;
varying vec3 _V;
varying vec3 _N;
varying vec4 P;
varying vec4 Pw;
//varying vec4 eyenormal;
//varying vec4 eye;
//varying vec4 Peye;
varying vec4 bbsize;
varying vec4 bbmin;
varying vec4 bbmax;
varying vec4 parea;

uniform float layer;
uniform float front;
uniform vec4 bboxSize;
uniform vec4 bboxMin;
uniform vec4 bboxMax;
uniform float invertNormals;
uniform vec4 clearColor;



void main()
{
    float Y = ((P.y)/abs(bbsize.z*2.0));
    float sliceSize = 0.001;//bbsize[3];
    float sliceLevel = layer;
    float slice = smoothstep(sliceLevel,sliceLevel+sliceSize,Y);


    vec3 N = normalize(_N); 
	vec3 V = -vec3(_V);
    
    if(invertNormals>0.0) N = -N;

//    vec3 I = normalize(eye.xyz);
    
    vec3 up = normalize(gl_NormalMatrix * vec3(1.0,-1.0,0.0));
    
    float light = dot(up,normalize(N))*0.5+0.5;
    //light = dot(normalize(I), normalize(normal.rgb));
    
    light = light<0.0 ? 0.0 : light;
    //light = 1.0-light;
//    light = step(0.95,abs(dot(normalize(I), normalize(normal.rgb))))*0.5+0.5;
    
    
    //slice = step( sliceLevel, bboxSize[2]*2.0-P[1]);
    float fr = dot(-normalize(V),normalize(N));//slice > 0 ? 1 : 0;
    vec4 color = vec4( light*1.2, light*0.1, 0.0, 0.0 );
//    slice *= step(0,fr) ;
    color.rgb = N;
    color.rgb = vec3(0.0,0.0,0.0);
    if( front>0.0 ){
        if ( fr > 0.0 ) {
            discard;
        }
    }else{
        if ( fr <= 0.0 ){
            discard;
        }
    }
    float mask = step(0.0,fr);
    color.rgb = vec3(mask*2.0);
    color.rgb += vec3(1.0,0.9,0.7) * max(0.0,-fr);
//    color.rgb = abs(P.x) > abs(parea.x)*0.05 ? clearColor.rgb : color.rgb ;
//    color.rgb = abs(P.y) > abs(parea.z)*0.2  ? clearColor.rgb : color.rgb ;
//    color.rgb = abs(P.z) > 10.0 ? clearColor.rgb : color.rgb ;
    if( P[1]<0.0 ){
        if ( mask>0.0 ){
            gl_FragDepth = 1.0;
        }else{
            color.rgb = clearColor.rgb;
        }
//        gl_FragDepth = 1.0;
    }
        

    gl_FragColor = vec4(color.rgb,1.0);// + vec4(0.0,1.0-min(0.0,(slice-0.5)*2.0),0.0,0.0);
    //gl_FragColor = vec4(Y,Y,Y<0 ? 0 : 1,1);
    if( slice>=1.0 ) discard;
}
