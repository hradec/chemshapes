
http://code.google.com/p/pyglet-shaders/

Python wrapper to compile, link, use OpenGL GLSL shaders, using pyglet
bindings.


===Status===

Minimally complete and working. \o/

See 'known problems'


===Usage===

For an example usage, see functionaltests/ft001-big-green-diamond.py

{{{
cd functionaltests
python ft001-big-green-diamond.py
}}}

This won't work if your hardware doesn't support shaders.

Basically, In your Python program, go:

{{{
vs = VertexShader(['src1', 'src2'])
fs = FragmentShader(['src1', 'src2'])
shader = ShaderProgram(vs, fs)
shader.use()
}}}

In the `use()` call, this will create the shaders, compile them, create the shader program, attach the shaders to the program, link the program and then use it for future rendering.

One or many shaders can be passed to the `ShaderProgram()` constructor. They will all be compiled and linked into the resulting program.

Failures (eg. compile or link errors) raise exceptions from `.use()`, with the compile or link errors in the exception message.


===Known Problems===

  * Does not yet handle binding variables to the shaders.
  * Does not yet support stuff like unbinding a shader to use a different one. It just handles the simple case of setting up a single shader program and leaving it in place permanently.


===Tests===

{{{
python tests/shader_tests.py
}}}

Constructing these unit tests was instructive in how to test code
which makes OpenGL code. The tests patch out the pyglet.gl module,
enabling tests code to call the code-under-test willy-nilly, without
having to worry about what OpenGL might actually be doing.

