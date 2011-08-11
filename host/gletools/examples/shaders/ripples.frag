uniform vec2 offsets;
uniform sampler2D tex2;
uniform sampler2D tex3;

vec4 get(sampler2D texture, float xoff, float yoff){
    vec2 pos = gl_TexCoord[0].st + (vec2(xoff, yoff)*offsets); 
    return texture2D(texture, pos);
}

void main(void){
    vec4 sample = (
        get(tex3, -1.0, 0.0) +
        get(tex3,  0.0, -1.0) + 
        get(tex3,  1.0, 0.0) + 
        get(tex3,  0.0, 1.0)
    );
    vec4 value = (sample * 0.51 - get(tex2, 0.0, 0.0)) * 0.960;
    gl_FragColor = value;
}
