void main()
{   
    float theta = 0.785;
    float cost = cos(theta);
    float sint = sin(theta);
    vec4 vertex = vec4(
        gl_Vertex.x * cost - gl_Vertex.y * sint,
        gl_Vertex.x * sint + gl_Vertex.y * cost,
        gl_Vertex.z,
        gl_Vertex.w / 30.0);
    gl_Position = gl_ModelViewProjectionMatrix * vertex;
}

