#version 400

vertex:
    in vec4 position;
    
    void main(void){
        gl_Position = position;
    }

control:
    layout(vertices = 4) out;
    uniform float pixels_per_division;
    uniform vec2 screen_size;
    uniform mat4 projection;
    uniform mat4 modelview;
    uniform bool projected;
    
    vec2 project(vec4 vertex){
        vec4 result = projection * modelview * vertex;
        result = clamp(result/result.w, -1.3, 1.3);
        return (result.xy+1)*(screen_size*0.5);
    }

    float divisions(vec2 v0, vec2 v1){
        return round(clamp(distance(v0, v1)/pixels_per_division, 1, 64));
    }

    void main(){
        if(gl_InvocationID == 0){
            float e0, e1, e2, e3;
            if(projected){
                vec2 v0 = project(gl_in[0].gl_Position);
                vec2 v1 = project(gl_in[1].gl_Position);
                vec2 v2 = project(gl_in[2].gl_Position);
                vec2 v3 = project(gl_in[3].gl_Position);

                e0 = divisions(v1, v2);
                e1 = divisions(v0, v1);
                e2 = divisions(v3, v0);
                e3 = divisions(v2, v3);
            }
            else{
                vec3 v0 = (modelview * gl_in[0].gl_Position).xyz;
                vec3 v1 = (modelview * gl_in[1].gl_Position).xyz;
                vec3 v2 = (modelview * gl_in[2].gl_Position).xyz;
                vec3 v3 = (modelview * gl_in[3].gl_Position).xyz;
               
                float x = 50; 
                e0 = round(clamp(x/length((v1+v2)/2), 1, 64));
                e1 = round(clamp(x/length((v0+v1)/2), 1, 64));
                e2 = round(clamp(x/length((v3+v0)/2), 1, 64));
                e3 = round(clamp(x/length((v2+v3)/2), 1, 64));
            }

            gl_TessLevelInner[0] = max(e1, e2);
            gl_TessLevelInner[1] = max(e0, e3);
            gl_TessLevelOuter[0] = e0;
            gl_TessLevelOuter[1] = e1;
            gl_TessLevelOuter[2] = e2;
            gl_TessLevelOuter[3] = e3;
        }
        gl_out[gl_InvocationID].gl_Position = gl_in[gl_InvocationID].gl_Position;
    }

eval:
    layout(quads, equal_spacing, ccw) in;
    //layout(quads, fractional_even_spacing, ccw) in;
    //layout(quads, fractional_odd_spacing, ccw) in;

    uniform mat4 projection;
    uniform mat4 modelview;
    uniform bool simple;

    void main(){
        float u = gl_TessCoord.x;
        float v = gl_TessCoord.y;

        vec4 a = mix(gl_in[1].gl_Position, gl_in[0].gl_Position, u);
        vec4 b = mix(gl_in[2].gl_Position, gl_in[3].gl_Position, u);
        gl_Position = projection * modelview * mix(a, b, v);
    }

fragment:
    out vec4 fragment;

    void main(){
        fragment = vec4(1.0);
    }
