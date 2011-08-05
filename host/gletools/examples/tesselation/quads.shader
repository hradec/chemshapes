#version 410

vertex:
    in vec4 position;
    
    void main(void){
        gl_Position = position;
    }

control:
    layout(vertices = 4) out;
    uniform float inner_level;
    uniform float outer_level;
    #define id gl_InvocationID

    void main(){
        gl_TessLevelInner[0] = inner_level;
        gl_TessLevelInner[1] = inner_level;
        gl_TessLevelOuter[0] = outer_level;
        gl_TessLevelOuter[1] = outer_level;
        gl_TessLevelOuter[2] = outer_level;
        gl_TessLevelOuter[3] = outer_level;

        gl_out[id].gl_Position = gl_in[id].gl_Position;
    }

eval:
    layout(quads, equal_spacing, ccw) in;

    uniform mat4 projection;
    uniform mat4 modelview;
    uniform bool simple;

    void main(){
        float u = gl_TessCoord.x;
        float v = gl_TessCoord.y;

        if(simple){
            vec4 a = mix(gl_in[1].gl_Position, gl_in[0].gl_Position, u);
            vec4 b = mix(gl_in[2].gl_Position, gl_in[3].gl_Position, u);
            gl_Position = projection * modelview * mix(a, b, v);
        }
        else{
            float omu = 1-u;
            float omv = 1-v;

            gl_Position = projection * modelview * (
                omu * omv * gl_in[0].gl_Position +
                  u * omv * gl_in[1].gl_Position +
                  u *   v * gl_in[2].gl_Position +
                omu *   v * gl_in[3].gl_Position);
        }
    }

geometry:
    layout(triangles) in;
    layout(triangle_strip, max_vertices = 3) out;

    void main(){
        gl_Position = gl_in[0].gl_Position; EmitVertex();
        gl_Position = gl_in[1].gl_Position; EmitVertex();
        gl_Position = gl_in[2].gl_Position; EmitVertex();
        EndPrimitive();
    }

fragment:
    out vec4 fragment;

    void main(){
        fragment = vec4(1.0);
    }
