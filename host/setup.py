import os, sys, glob
sys.path.append(os.path.abspath("."))
sys.path.append(os.path.abspath("./gletools"))


# add meshes and shaders to distribution
data_files = []
for types in ['stl','obj','scad']:
    for each in glob.glob('meshes/*.%s' % types):
        data_files.append( ( 'meshes',[each] ) )
for each in glob.glob('glViewport/*.frag'):
    data_files.append( ('shaders',[each]) )
for each in glob.glob('glViewport/*.vert'):
    data_files.append( ('shaders',[each]) )
    
# used packages
includes = []
packages = []
packages = [
    "ctypes", 
    "logging", 
    "OpenGL", 
    "PySide",
#    "tcl",
]

# exclude packages
excludes = []
#excludes = ['tcl']

# remove dist folder
os.system('rm -rf dist')


if sys.platform == 'darwin':
    from setuptools import setup
    setup(
        options = {'py2exe': {
            "packages": packages, 
            "includes": includes, 
            "excludes": excludes, 
            "skip_archive":False, 
            'optimize': 2, 
            "unbuffered": True, 
            "bundle_files":2,
        }},
        app=["draft.py"],
        setup_requires=["py2app"],
        data_files=data_files,
    )    
    
elif sys.platform == 'win32':
    from distutils.core import setup
    from glob import glob

    import py2exe

    # pack MSVC libs for python 2.7
#    data_files.append(os.path.abspath('./__debug_env_w32/Python27/msvcr90.dll'))
    data_files.append(os.path.abspath('./__debug_env_w32/Python27/msvcp90.dll'))
    
    #data_files = [("Microsoft.VC90.CRT", glob(r'C:\Program Files\Microsoft Visual Studio 9.0\VC\redist\x86\Microsoft.VC90.CRT\*.*'))]
    # generate 
    #setup(console=['draft.py'], data_files=data_files)

    setup(
        options = {'py2exe': {
            "packages": packages, 
            "includes": includes, 
            "excludes": excludes, 
            "skip_archive":False, 
            "optimize": 1, 
            "unbuffered": True, 
            "bundle_files":2,
            "skip_archive":False,
        }},
        windows = [{'script': "draft.py"}],
        zipfile = None, #"chemshapes.lib",
        data_files=data_files ,
    )



