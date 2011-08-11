#version 400

vertex:
    in vec4 position;
    out vec3 v_position;

    void main(void){
        v_position = position.xyz;
    }

control:
    layout(vertices = 3) out;

    in vec3 v_position[];
    out vec3 tc_position[];

    uniform float inner_level;
    uniform float outer_level;

    void main(){
        tc_position[gl_InvocationID] = v_position[gl_InvocationID];
        if (gl_InvocationID == 0){
            gl_TessLevelInner[0] = inner_level;
            gl_TessLevelOuter[0] = outer_level; // 1 and 2
            gl_TessLevelOuter[1] = outer_level; // 2 and 0
            gl_TessLevelOuter[2] = outer_level; // 0 and 1
        }
    }

eval:
    layout(triangles, equal_spacing, cw) in;

    in vec3 tc_position[];

    uniform mat4 projection;
    uniform mat4 modelview;

    void main(){
        vec3 p0 = gl_TessCoord.x * tc_position[0];
        vec3 p1 = gl_TessCoord.y * tc_position[1];
        vec3 p2 = gl_TessCoord.z * tc_position[2];
        gl_Position = projection * modelview * vec4(p0 + p1 + p2, 1);
    }

geometry: off
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
