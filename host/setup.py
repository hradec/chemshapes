import os, sys, glob
sys.path.append(os.path.abspath("."))
sys.path.append(os.path.abspath("./gletools"))


data_files = [
    'glViewport/slicer.frag',
    'glViewport/slicer.vert',
    'glViewport/normal.frag',
    'glViewport/normal.vert',
    'meshes','meshes',
]

if sys.platform == 'darwin':
    from setuptools import setup
    setup(
        options = {'py2exe': {
            "packages": [
                "ctypes", 
                "logging", 
                "OpenGL", 
                "PySide",
            ], "excludes": [], "skip_archive":False, 'optimize': 2, "unbuffered": True, "bundle_files":2 }
        },
        app=["draft.py"],
        setup_requires=["py2app"],
        data_files=data_files,
    )    
    
else:
    from distutils.core import setup
    from glob import glob

    import py2exe

    # pack MSVC libs for python 2.7
    data_files.append("Microsoft.VC90.CRT", [os.path.abspath('./__debug_env_w32/Python27/msvcr90.dll')])
    data_files.append("Microsoft.VC90.CRT", [os.path.abspath('./__debug_env_w32/Python27/msvcp90.dll')])
    
    #data_files = [("Microsoft.VC90.CRT", glob(r'C:\Program Files\Microsoft Visual Studio 9.0\VC\redist\x86\Microsoft.VC90.CRT\*.*'))]
    # generate 
    #setup(console=['draft.py'], data_files=data_files)



    setup(
        options = {'py2exe': {
            "packages": [
                "ctypes", 
                "logging", 
                "OpenGL", 
                "PySide",
            ], "excludes": [], "skip_archive":False, 'optimize': 2, "unbuffered": True, "bundle_files":2 }
        },
        console = [{'script': "test.py"}],
        zipfile = "shared.lib",
        data_files=data_files,
        
    )



