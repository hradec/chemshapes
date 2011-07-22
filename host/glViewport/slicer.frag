varying vec3 normal;
varying vec4 P;
uniform float layer;

void main()
{
    float sliceSize = 0.01;
    float sliceLevel = layer;
    float slice = smoothstep(sliceLevel-sliceSize,sliceLevel,P.g) * (1-smoothstep(sliceLevel,sliceLevel+sliceSize,P.g));

    
    
    float light = dot(normalize(vec3(1,1,0)),normalize(normal.rgb))+0.5;
    gl_FragColor = vec4(light.r,0,0,0.3);
    gl_FragColor = vec4(vec4(slice,slice,slice,slice)+gl_FragColor);
}

