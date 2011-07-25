varying vec3 normal;
varying vec4 P;
varying vec3 eye;
uniform float layer;
uniform vec4 bboxSize;

void main()
{
    float sliceSize = bboxSize[3];
    float sliceLevel = layer;
    float slice = smoothstep(sliceLevel-sliceSize,sliceLevel,P[1]) * (1.0-smoothstep(sliceLevel,sliceLevel+sliceSize,P[1]));

    vec3 I = eye-P.xyz;
    
    
    float light = dot(normalize(vec3(1,1,0)),normalize(normal.rgb))*0.5+0.5;
    //light = dot(normalize(I), normalize(normal.rgb));
    
    light = light<0.0 ? 0.0 : light;
    //light = 1.0-light;
//    light = step(0.95,abs(dot(normalize(I), normalize(normal.rgb))))*0.5+0.5;
    
    vec4 color = vec4( light*1.2, light*0.1, 0.0, 0.3 );
    gl_FragColor = vec4(slice,slice,slice,slice*0.5)  + color;
}
