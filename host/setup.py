import os, sys
from distutils.core import setup
from glob import glob
import py2exe

sys.argv.append('py2exe')


# pack MSVC libs for python 2.7
data_files = [
    ("", ['C:\\Program Files (x86)/Microsoft Xbox 360 SDK\\bin\\win32\\MSVCP90.dll'])
]

# generate 
#setup(console=['draft.py'], data_files=data_files)

setup(
    options = {'py2exe': {"includes": ["ctypes", "logging", "OpenGL", "PySide",], "excludes": []}}, # ,'optimize': 2
    windows = [{'script': "draft.py"}],
    zipfile = "shared.lib",
    data_files=data_files
)
