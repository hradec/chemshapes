#version 400

vertex:
    //uniform sampler2D terrain;
    uniform mat4 modelview;
    uniform mat4 projection;
    uniform vec2 screen_size;

    in vec4 position;
    in vec3 normal;
    out _{
        vec4 world;
        vec3 eye;
        float dist;
        vec3 eye_normal;
        vec4 device;
        vec2 screen;
        bool offscreen;
        vec3 normal;
    } o;
    
    void main(void){
        vec2 texcoord = position.xy;
        o.world = position;
        o.eye = (modelview * o.world).xyz;
        o.dist = length(o.eye);
        o.eye_normal = normalize(o.eye);
        o.device = projection * modelview * o.world;
        o.device = clamp(o.device/o.device.w, -1.6, 1.6);
        o.screen = (o.device.xy+1) * (screen_size*0.5);
        o.normal = normal;

        if(o.device.z < -0.5){
            o.offscreen = true;
        }
        else{
            o.offscreen = any(
                lessThan(o.device.xy, vec2(-1.59)) ||
                greaterThan(o.device.xy, vec2(1.59))
            );
        }
    }

control:
    layout(vertices = 3) out;
    float pih = 3.14159265358979323846264338327950288419716939937510*0.5;
    uniform mat4 modelview;
    mat3 normalmatrix = mat3(transpose(inverse(modelview)));

    in _{
        vec4 world;
        vec3 eye;
        float dist;
        vec3 eye_normal;
        vec4 device;
        vec2 screen;
        bool offscreen;
        vec3 normal;
    } i[];

    float edge_colin(int i0, int i1){
        int near, far;
        if(i[i0].dist < i[i1].dist){
            near = i0;
            far = i1;
        }
        else{
            near = i1;
            far = i0;
        }
        vec3 n0 = normalize(i[near].eye+i[far].eye);
        vec3 n1 = normalize(i[far].eye - i[near].eye);
        float cosine = dot(n0, n1);
        float rad = acos(cosine);
        float deg = degrees(rad);
        float factor = abs(deg-90)/90;
        return mix(1.0, 32.0, pow(factor, 2));
    }

    float normal_colin(int i0, int i1){
        vec3 n0 = normalmatrix * normalize(i[i0].normal + i[i1].normal);
        vec3 n1 = normalize((i[i0].eye+i[i1].eye)/2);

        float cosine = dot(n0, n1);
        float rad = acos(cosine);
        float deg = degrees(rad);
        float factor = abs(deg-90)/90;
        return mix(1.0, 0.3, pow(factor, 0.6));
    }

    float center_weight(int i0, int i1){
        vec2 middle = (i[i0].device.xy + i[i1].device.xy)/2;
        return mix(1.0, 0.3, length(middle)/1.414213562);
    }
    
    float screen(int i0, int i1){
        return distance(i[i0].screen, i[i1].screen)/4 + edge_colin(i0, i1);
    }
    
    float dist(int i0, int i1){
        float center_factor = center_weight(i0, i1);
        float normal_factor = normal_colin(i0, i1);
        
        vec3 middle = (modelview * (i[i0].world+i[i1].world)/2).xyz;
        float dist = length(middle);
        return 0.3/pow(dist, 2) * center_factor * normal_factor;

        //return dist_factor;
        //return (0.3*normal_colin(i0, i1)*center_weight(i0, i1))/pow(length(middle), 1.2);
    }
    
    float dist_length(int i0, int i1){
        vec3 eye0 = i[i0].eye;
        vec3 eye1 = i[i1].eye;

        vec3 middle = (eye0+eye1)/2;
        float factor = distance(eye0, eye1)/length(middle);
        return 185*factor;
    }

    float angular(int i0, int i1){
        float center_factor = center_weight(i0, i1);
        float normal_factor = normal_colin(i0, i1);
        float edge_factor = edge_colin(i0, i1);
        float angle = acos(dot(normalize(i[i0].eye), normalize(i[i1].eye)));
        vec3 middle = (modelview * (i[i0].world+i[i1].world)/2).xyz;
        float dist_factor = 0.005/pow(length(middle), 2);
        return (angle/radians(0.1))*center_factor*normal_factor*dist_factor+edge_factor;
    }

    void main(){
        if(gl_InvocationID == 0){
            if(i[0].offscreen && i[1].offscreen && i[2].offscreen){
                gl_TessLevelInner[0] = 0;
                gl_TessLevelOuter[0] = 0;
                gl_TessLevelOuter[1] = 0;
                gl_TessLevelOuter[2] = 0;
            }
            else{
                //float e0=screen(1, 2), e1=screen(2, 0), e2=screen(0, 1); // probably worst, a lot of lateral movement artefacts, though performs better in fills then distance
                //float e0=dist(1, 2), e1=dist(2, 0), e2=dist(0, 1); // better then screen, also introduces some non edge artefacts
                //float e0=dist_length(1, 2), e1=dist_length(2, 0), e2=dist_length(0, 1); // better then dist
                float e0=angular(1, 2), e1=angular(2, 0), e2=angular(0, 1); // less lateral movement artefacts, about similar to screen

                //gl_TessLevelInner[0] = clamp((e0+e1+e2)/3, 1, 64);
                gl_TessLevelInner[0] = clamp(min(min(e0, e1),e2), 1, 64);
                //gl_TessLevelInner[0] = clamp(max(max(e0, e1),e2), 1, 64);
                gl_TessLevelOuter[0] = clamp(e0, 1, 64);
                gl_TessLevelOuter[1] = clamp(e1, 1, 64);
                gl_TessLevelOuter[2] = clamp(e2, 1, 64);
            }
        }
        gl_out[gl_InvocationID].gl_Position = i[gl_InvocationID].world;
    }

eval:
    layout(triangles, fractional_even_spacing, cw) in;
    //layout(triangles, equal_spacing, cw) in;

    uniform sampler2D terrain;
    uniform mat4 mvp;
    out vec2 texcoord;
    out float depth;

    void main(){
        float u = gl_TessCoord.x;
        float v = gl_TessCoord.y;

        vec4 p0 = gl_TessCoord.x * gl_in[0].gl_Position;
        vec4 p1 = gl_TessCoord.y * gl_in[1].gl_Position;
        vec4 p2 = gl_TessCoord.z * gl_in[2].gl_Position;
        vec4 position = p0 + p1 + p2;

        position.z = texture(terrain, position.xy).a;
        gl_Position = mvp * position;
        texcoord = position.xy;
        depth = gl_Position.z;
    }

fragment:
    uniform sampler2D diffuse;
    uniform sampler2D terrain;

    in vec2 texcoord;
    in float depth;
    out vec4 fragment;

    vec3 incident = normalize(vec3(1.0, 0.2, 0.5));
    vec4 light = vec4(1.0, 0.95, 0.9, 1.0) * 1.1;

    void main(){
        vec3 normal = normalize(texture(terrain, texcoord).xyz);
        vec4 color = texture(diffuse, texcoord);

        float dot_surface_incident = max(0, dot(normal, incident));

        color = color * light * (max(0.1, dot_surface_incident)+0.05)*1.5;
        fragment = mix(color, color*0.5+vec4(0.5, 0.5, 0.5, 1.0), depth*2.0);
    }
