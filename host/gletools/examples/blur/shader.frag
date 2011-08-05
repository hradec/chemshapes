uniform float width, height;
uniform sampler2D texture;
int size = 32;

vec4 get(sampler2D texture, int x, int y){
    vec2 pos = vec2(gl_FragCoord.x, gl_FragCoord.y) + vec2(x, y); 
    return texture2D(texture, pos / vec2(width, height));
}

void main(){
    vec4 result = vec4(0.0, 0.0, 0.0, 0.0);
    for(int x=0; x<size; x++){
        for(int y=0; y<size; y++){
            vec4 color = get(texture, x-size/2, y-size/2);
            result += color;
        }
    }
    gl_FragColor = vec4(0.2) + result/(size*size) * 0.6;
    gl_FragColor.w = 1;
}
