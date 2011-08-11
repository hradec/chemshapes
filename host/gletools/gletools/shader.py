# -*- coding: utf-8 -*-

"""
    :copyright: 2009 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""

from __future__ import with_statement

from ctypes import c_char_p, pointer, cast, byref, c_char, create_string_buffer, c_float, c_int, POINTER

from gletools.gl import *
from pyglet.gl.glext_arb import *
from .util import Context

import re
import os

__all__ = 'VertexShader', 'FragmentShader', 'ShaderProgram', 'TessControlShader', 'TessEvalShader', 'GeometryShader'

class GLObject(object):
    _del = glDeleteObjectARB
    class Error(Exception): pass
    class Extension(Error): pass
    class Compile(Error): pass
    class Link(Error): pass
    class Validate(Error): pass

    def log(self):
        length = c_int(0)
        glGetObjectParameterivARB(self.id, GL_OBJECT_INFO_LOG_LENGTH_ARB, byref(length))
        log = create_string_buffer(length.value)
        glGetInfoLogARB(self.id, length.value, None, log)
        return log.value
    
    def __del__(self):
        self._del(self.id)

class Shader(GLObject):
    def __init__(self, source, filename='string'):
        self.filename = filename
        if not gl_info.have_extension(self.ext):
            raise self.Extension('file: %s, %s extension is not available' % (filename, self.ext))
        self.id = glCreateShaderObjectARB(self.type)
        self.source = source
        ptr = cast(c_char_p(source), POINTER(c_char))
        glShaderSourceARB(self.id, 1, byref(ptr), None)

        glCompileShader(self.id)
        
        status = c_int(0)
        glGetObjectParameterivARB(self.id, GL_OBJECT_COMPILE_STATUS_ARB, byref(status))
        if status.value == 0:
            error = self.log()
            raise self.Compile(error)
    
    @classmethod
    def open(cls, file):
        if isinstance(file, basestring):
            file = open(file)
        source = file.read()
        return cls(source, file.name)

class VertexShader(Shader):
    type = GL_VERTEX_SHADER_ARB
    ext = 'GL_ARB_vertex_program'

class FragmentShader(Shader):
    type = GL_FRAGMENT_SHADER_ARB
    ext = 'GL_ARB_fragment_program'

if gl_info.have_version(4, 0) or gl_info.have_extension('GL_ARB_tessellation_shader'):
    class TessControlShader(Shader):
        type = GL_TESS_CONTROL_SHADER
        ext = 'GL_ARB_tessellation_shader'

    class TessEvalShader(Shader):
        type = GL_TESS_EVALUATION_SHADER
        ext = 'GL_ARB_tessellation_shader'
else:
    class TessControlShader(object): pass
    class TessEvalShader(object): pass

if gl_info.have_version(4, 0):
    class GeometryShader(Shader):
        type = GL_GEOMETRY_SHADER
        ext = 'GL_ARB_geometry_shader4'
elif gl_info.have_extension('GL_ARB_geometry_shader4'):
    class GeometryShader(Shader):
        type = GL_GEOMETRY_SHADER_ARB
        ext = 'GL_ARB_geometry_shader4'
else:
    class GeometryShader(object): pass

class Variable(object):
    def set(self, program, name):
        with program:
            location = program.uniform_location(name)
            if location != -1:
                self.do_set(location)

class Sampler2D(Variable):
    def __init__(self, unit):
        self.value = unit - GL_TEXTURE0

    def do_set(self, location):
        glUniform1i(location, self.value)

class Mat4(Variable):
    def __init__(self, *values):
        self.values = (c_float*16)(*values)

    def do_set(self, location):
        glUniformMatrix4fv(location, 1, GL_FALSE, self.values)

class UniformArray(Variable):
    typemap = {
        int:{
            'ctype': c_int,
            'sizes':[
                glUniform1iv,
                glUniform2iv,
                glUniform3iv,
                glUniform4iv,
            ]
        },
        float:{
            'ctype': c_float,
            'sizes':[
                glUniform1fv,
                glUniform2fv,
                glUniform3fv,
                glUniform4fv,
            ]
        },
    }
    def __init__(self, type, size, values):
        spec = self.typemap[type]
        self.setter = spec['sizes'][size-1]
        self.count = len(values)
        ctype = spec['ctype']
        self.values = (ctype*(size*self.count))(*values)

    def do_set(self, location):
        self.setter(location, self.count, self.values)

typemap = {
    float:{
        1:glUniform1f,
        2:glUniform2f,
        3:glUniform3f,
    },
    int:{
        1:glUniform1i,
        2:glUniform2i,
        3:glUniform3i,
    },
    bool:{
        1:glUniform1i,
        2:glUniform2i,
        3:glUniform3i,
    }
}

class Vars(object):
    def __init__(self, program):
        self.__dict__['_program'] = program

    def __setattr__(self, name, value):
        self[name] = value

    def __setitem__(self, name, value):
        if isinstance(value, Variable):
            value.set(self._program, name)
        elif isinstance(value, (tuple, list)):
            setter = typemap[type(value[0])][len(value)]
            with self._program:
                location = self._program.uniform_location(name)
                if location != -1:
                    setter(location, *value)
        elif isinstance(value, (int, float)): 
            setter = typemap[type(value)][1]
            with self._program:
                location = self._program.uniform_location(name)
                if location != -1:
                    setter(location, value)

class SourceLine(object):
    stage_match = re.compile('(vertex|control|eval|geometry|fragment):')
    stage_parse = re.compile('(vertex|control|eval|geometry|fragment): *(on|off)?')
    
    import_match = re.compile('import: +(.+)')

    def __init__(self, filename, n, text):
        self.filename = filename
        self.n = n
        self.text = text

    def __repr__(self):
        return self.text

    def stage(self):
        if self.stage_match.match(self.text):
            typename, enabled = self.stage_parse.match(self.text).groups()
            enabled = not enabled == 'off'
            return typename, enabled
        else:
            return None, None

    def import_directive(self):
        match = self.import_match.search(self.text)
        if match:
            return match.group(1)

    def compile(self, module_number):
        return '#line %i %i\n%s\n' % (self.n+1, module_number, self.text)

class ShaderProgram(GLObject, Context):
    _get = GL_CURRENT_PROGRAM
    
    def bind(self, id):
        glUseProgram(id)

    def __init__(self, *shaders, **variables):
        Context.__init__(self)
        self.id = glCreateProgramObjectARB()
        self.shaders = list(shaders)
        for shader in shaders:
            glAttachObjectARB(self.id, shader.id)

        self.link()

        self.vars = Vars(self)
        for name, value in variables.items():
            setattr(self.vars, name, value)

    def attrib_location(self, name):
        return glGetAttribLocation(self.id, name)

    def link(self):
        glLinkProgramARB(self.id)
       
        status = c_int(0)
        glGetObjectParameterivARB(self.id, GL_OBJECT_LINK_STATUS_ARB, byref(status))
        if status.value == 0:
            error = self.log()
            raise self.Link(error)

        glValidateProgram(self.id)
        glGetObjectParameterivARB(self.id, GL_VALIDATE_STATUS, byref(status))
        if status.value == 0:
            error = self.log()
            raise self.Validate(error)
    
    def uniform_location(self, name):
        return glGetUniformLocation(self.id, name)

    @staticmethod
    def getlines(filename):
        return [
            SourceLine(filename, n, line)
            for n, line in
            enumerate(open(filename).read().split('\n'))
        ]

    @staticmethod
    def get_version(lines):
        for line in lines:
            if line.text.startswith('#version'):
                version = line.text
                lines.remove(line)
                return version

    @staticmethod
    def split_stages(lines):
        stage = []
        typename = None
        stages = {}

        for line in lines:
            new_type, enabled = line.stage()
            if new_type:
                if stage and typename:
                    stages[typename] = stage
                    stage = []
                typename = new_type
            else:
                stage.append(line)

        if stage and typename:
            stages[typename] = stage

        return stages

    @staticmethod
    def split_imports(lines):
        imports = []
        sourcelines = []
        for line in lines:
            name = line.import_directive()
            if name:
                dirname = os.path.dirname(line.filename)
                filename = os.path.abspath(os.path.join(dirname, '%s.shader' % name))
                imports.append(filename)
            else:
                sourcelines.append(line)

        return imports, sourcelines

    @classmethod
    def process_imports(cls, lines):
        todo = [lines]
        chunks = []
        processed = set()
        while todo:
            lines = todo.pop(0) 
            imports, sourcelines = cls.split_imports(lines)
            chunks.insert(0, sourcelines)
            for filename in imports:
                if filename not in processed:
                    lines = cls.getlines(filename)
                    todo.append(lines)
                    processed.add(filename)

        result = []
        for lines in chunks:
            result.extend(lines)
        return result
        
    @classmethod
    def open(cls, name, **variables):
        filename = os.path.abspath(name)
        lines = cls.getlines(filename)
        version = cls.get_version(lines)
        stages = cls.split_stages(lines)

        types = {
            'vertex'    : VertexShader,
            'control'   : TessControlShader,
            'eval'      : TessEvalShader,
            'geometry'  : GeometryShader,
            'fragment'  : FragmentShader,
        }

        modules = {}
        module_count = 0
        mapping = {}
        shaders = []
       
        try:
            for typename, stage in stages.items():
                if version:
                    source = '%s\n' % version
                else:
                    source = ''
                lines = cls.process_imports(stage)
                for line in lines:
                    module = modules.get(line.filename)
                    if not module:
                        module = modules[line.filename] = {}
                        mapping[line.filename] = module_count
                        module_count += 1

                    module_number = mapping[line.filename]
                    source += line.compile(module_number)
                    module[line.n] = line

                shader = types[typename]
                shaders.append(shader(source, filename))
            return cls(*shaders, **variables)
        except (cls.Compile, cls.Link, cls.Validate), error:
            matcher = re.compile('(\d+)\((\d+)\) : (.+)')
            errors = []
            mapping = dict((n, filename) for filename, n in mapping.items())
            for line in error.args[0].strip().split('\n'):
                match = matcher.search(line)
                if match:
                    module_number, line_number, message = match.groups()
                    module_number = int(module_number)
                    line_number = int(line_number)-1
                    filename = mapping[module_number]
                    module = modules[filename]
                    source_line = module[line_number]
                    line = 'File: %s Line: %s\n  %s\n  %s\n' % (filename, line_number, source_line.text.strip(), message)
                errors.append(line)

            message = '\n' + '\n'.join(errors)
            raise error.__class__(message)
