varying vec3 normal;
varying vec4 P;
uniform float layer;
uniform vec4 bboxSize;
varying vec2 texCoord;

void main()
{
    float sliceSize = bboxSize[3];
    float sliceLevel = layer;
    float slice = smoothstep(sliceLevel-sliceSize,sliceLevel,P[1]) * (1.0-smoothstep(sliceLevel,sliceLevel+sliceSize,P[1]));

    
    
    float light = dot(normalize(vec3(1,1,0)),normalize(normal.rgb))*0.5+0.5;
    
    vec2 vv = floor(texCoord*10.0)/2.0;
    //vv.x+=1;
    vv.x = vv.x-floor(vv.x) > 0.0 ? 1.0 : 0.0;
    vv.y = vv.y-floor(vv.y) > 0.0 ? 1.0 : 0.0;
    vec4 color = vec4( vec3(vv.x+vv.y)*0.1, 0.1 );
    gl_FragColor = color;
}

