from ctypes import (
    byref, c_char, c_char_p, c_int, cast, create_string_buffer, pointer,
    POINTER
)
import sys
from OpenGL import GL as gl


class ShaderError(Exception): pass
class CompileError(ShaderError): pass
class LinkError(ShaderError): pass


shaderErrors = {
    gl.GL_INVALID_VALUE: 'GL_INVALID_VALUE (bad 1st arg)',
    gl.GL_INVALID_OPERATION: 'GL_INVALID_OPERATION '
        '(bad id or immediate mode drawing in progress)',
    gl.GL_INVALID_ENUM: 'GL_INVALID_ENUM (bad 2nd arg)',
}


class _Shader(object):

    type = None

    def __init__(self, sources):
        if isinstance(sources, basestring):
            self.sources = [sources]
        else:
            self.sources = sources
        self.id = None
        
        
    def _get(self, paramId):
        outvalue = c_int(0)
        value = gl.glGetShaderiv(self.id, paramId) #, byref(outvalue))
        #value = outvalue.value
        if value in shaderErrors.keys():
            msg = '%s from glGetShader(%s, %s, &value)'
            raise ValueError(msg % (shaderErrors[value], self.id, paramId))
        return value


    def getCompileStatus(self):
        return bool(self._get(gl.GL_COMPILE_STATUS))


    def getInfoLogLength(self):
        return self._get(gl.GL_INFO_LOG_LENGTH)


    def getInfoLog(self):
        return gl.glGetShaderInfoLog(self.id)

    def _srcToArray(self):
        num = len(self.sources)
        all_source = (c_char_p * num)(*self.sources)
        return num, cast(pointer(all_source), POINTER(POINTER(c_char)))
        

    def compile(self):
        self.id = gl.glCreateShader(self.type)

        num, src = self._srcToArray()
        gl.glShaderSource(self.id, self.sources)
        gl.glCompileShader(self.id)

        if not self.getCompileStatus():
            raise CompileError(self.getInfoLog())



class VertexShader(_Shader):
    type = gl.GL_VERTEX_SHADER


class FragmentShader(_Shader):
    type = gl.GL_FRAGMENT_SHADER



class ShaderProgram(object):

    def __init__(self, *shaders):
        self.shaders = list(shaders)
        self.id = None

    
    def _get(self, paramId):
        outvalue = c_int(0)
        gl.glGetProgramiv(self.id, paramId, byref(outvalue))
        value = outvalue.value
        if value in shaderErrors.keys():
            msg = '%s from glGetProgram(%s, %s, &value)'
            raise ValueError(msg % (shaderErrors[value], self.id, paramId))
        return value
        
        
    def getLinkStatus(self):
        return bool(self._get(gl.GL_LINK_STATUS))


    def getInfoLogLength(self):
        return self._get(gl.GL_INFO_LOG_LENGTH)


    def getInfoLog(self):
        return gl.glGetProgramInfoLog(self.id)
        

    def _getMessage(self):
        messages = []
        for shader in self.shaders:
            log = shader.getInfoLog()
            if log:
                messages.append(log)
        log = self.getInfoLog()
        if log:
            messages.append(log)
        return '\n'.join(messages)

        
    def use(self):
        self.id = gl.glCreateProgram()
        
        for shader in self.shaders:
            shader.compile()
            gl.glAttachShader(self.id, shader.id)

        gl.glLinkProgram(self.id)

        message = self._getMessage()
        if not self.getLinkStatus():
            raise LinkError(message)

        gl.glUseProgram(self.id)
        return message

    def bind(self):
        # bind the program
        gl.glUseProgram(self.id)

    def unbind(self):
        # unbind whatever program is currently bound - not necessarily this program,
        # so this should probably be a class method instead
        gl.glUseProgram(0)


    # upload a floating point uniform
    # this program must be currently bound
    def uniformf(self, name, *vals):
#        self.bind()
        # check there are 1-4 values
        if len(vals) in range(1, 5):
            # select the correct function
            { 1 : gl.glUniform1f,
                2 : gl.glUniform2f,
                3 : gl.glUniform3f,
                4 : gl.glUniform4f
                # retrieve the uniform location, and set
            }[len(vals)](gl.glGetUniformLocation(self.id, name), *vals)
#        self.unbind()

    # upload an integer uniform
    # this program must be currently bound
    def uniformi(self, name, *vals):
#        self.bind()
        # check there are 1-4 values
        if len(vals) in range(1, 5):
            # select the correct function
            { 1 : gl.glUniform1i,
                2 : gl.glUniform2i,
                3 : gl.glUniform3i,
                4 : gl.glUniform4i
                # retrieve the uniform location, and set
            }[len(vals)](gl.glGetUniformLocation(self.id, name), *vals)
#        self.unbind()

    # upload a uniform matrix
    # works with matrices stored as lists,
    # as well as euclid matrices
    def uniform_matrixf(self, name, mat):
#        self.bind()
        # obtian the uniform location
        loc = gl.glGetUniformLocation(self.id, name)
        # uplaod the 4x4 floating point matrix
        gl.glUniformMatrix4fv(loc, 1, False, (c_float * 16)(*mat))
#        self.unbind()


