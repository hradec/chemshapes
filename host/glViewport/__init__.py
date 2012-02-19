from __future__ import with_statement

import sys, os
import math
sys.path.append( '%s/gletools' % os.path.dirname( os.path.dirname( __file__ )) )


try:
    from PySide import QtCore, QtGui, QtOpenGL
except:
    from PyQt4 import QtCore, QtGui, QtOpenGL
    QtCore.Qt.MiddleButton = QtCore.Qt.MidButton

try:
    from OpenGL.platform import win32
except AttributeError:
    pass

try:
    from OpenGL import GL
    from OpenGL import GLU as glu
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "OpenGL hellogl",
                            "PyOpenGL must be installed to run this example.",
                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
                            QtGui.QMessageBox.NoButton)
    sys.exit(1)
    



from mesh import *
import stl, obj

import pyglet
import pyglet_shaders 
import gletools
import prefs

from context import context
from glwidget import *

