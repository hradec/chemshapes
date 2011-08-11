varying vec3 normal;
varying vec3 _V;
varying vec3 _N;
varying vec4 P;
varying vec4 eyenormal;
varying vec4 eye;
varying vec4 Peye;
uniform float layer;
uniform float front;
uniform vec4 bboxSize;

void main()
{
    float sliceSize = bboxSize[3];
    float sliceLevel = layer*bboxSize[2]*2.0;
    float slice = smoothstep(sliceLevel-sliceSize,sliceLevel,P[1]) * (1.0-smoothstep(sliceLevel,sliceLevel+sliceSize,P[1]));

    vec3 N = normalize(_N); 
	vec3 V = -vec3(_V);

//    vec3 I = normalize(eye.xyz);
    
    vec3 up = normalize(gl_NormalMatrix * vec3(1.0,-1.0,0.0));
    
    float light = dot(up,normalize(N))*0.5+0.5;
    //light = dot(normalize(I), normalize(normal.rgb));
    
    light = light<0.0 ? 0.0 : light;
    //light = 1.0-light;
//    light = step(0.95,abs(dot(normalize(I), normalize(normal.rgb))))*0.5+0.5;
    
    
    slice = step( sliceLevel, bboxSize[2]*2.0-P[1]);
    float fr = dot(-normalize(V),normalize(N));//slice > 0 ? 1 : 0;
    vec4 color = vec4( light*1.2, light*0.1, 0.0, 0.0 );
//    slice *= step(0,fr) ;
    color.rgb = N;
    color.rgb = vec3(0.0,0.0,0.0);
    if( front>0.0 ){
        if ( fr > 0.0 ) {
            discard;
        }
        color.rgb = vec3(abs(fr),0.0,0.0);//vec3(abs(fr),0,0);
//        gl_FragDepth = 0.0;
    }else{
        if ( fr <= 0.0 ){
            discard;
        }
        color.rgb = vec3(1.0);
    }
    float mask = step(0.0,fr);
    color.rgb = vec3(mask) + vec3(-fr*(1.0-mask),0.0,0.0);
    gl_FragColor = vec4(color.rgb,slice) ;
    if( slice<1.0 ) discard;
}
