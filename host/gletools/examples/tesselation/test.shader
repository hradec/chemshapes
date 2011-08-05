#version 400

vertex:
    in vec4 position;
    //in vec3 normal;
    //out vec3 color;
    uniform mat4 mvp;
    
    void main(void){
        //color = normal;
        gl_Position = mvp * position;
    }

fragment:
    out vec4 fragment;
    //in vec3 color;
    void main(){
        fragment = vec4(1);
    }
