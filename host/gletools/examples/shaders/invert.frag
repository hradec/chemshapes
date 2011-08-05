uniform sampler2D texture;

void main(){
    gl_FragColor = 1.0 - texture2D(texture, gl_TexCoord[0].st);
}
