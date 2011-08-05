uniform float seed;

float random(vec2 uv){
    return fract(sin(dot(uv ,vec2(12.9898,78.233))) * 43758.5453);
}

void main(){
    vec2 uv = gl_TexCoord[0].st;
    float intensity = random(uv+seed);
    gl_FragColor = vec4(intensity, intensity, intensity, 1.0);
}
