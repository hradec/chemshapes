#!/usr/bin/env python

import sys, os, time
sys.path += [ os.path.abspath('.') ]
#os.environ[ 'PATH' ] = '.%s%s' % ( os.path.pathsep, os.environ[ 'PATH' ] )

if not hasattr(sys, "frozen"):
    try:
        import draft_ui
        if ( not  os.path.exists('draft_ui.py') ) or os.stat( 'draft_ui.py' ).st_mtime < os.stat( 'draft.ui' ).st_mtime:
            raise
    except:
        def which(file):
            for path in os.environ["PATH"].split(os.path.pathsep):
                #if file in os.listdir(path):
                filePath = os.path.join(path, file)
                if os.path.exists( filePath ):
                    return filePath

        sys.stdout.write( "\nTranslating draft.ui to .py..." )
        sys.stdout.flush()

        f = open('draft_ui.py','w')

        uic = which( 'pyside-uic' )
        if not uic:
            import PyQt4
            os.environ['PATH'] = os.path.join( os.path.dirname(PyQt4.__file__), os.environ['PATH']  )
            uic = which( 'pyuic' )
            del PyQt4

        for line in os.popen( '%s draft.ui 2>&1 ' % uic).readlines():
            f.write(line)
        f.close()
        sys.stdout.write( "Done!\n" )
        sys.stdout.flush()
        import draft_ui


try:
    from PySide.QtCore import QIODevice, QFile, SIGNAL, SLOT, QObject, Qt
    from PySide.QtGui import QApplication, QFrame, QDial, QSlider, QPushButton, QFileDialog, QWidget, QMessageBox, QTextOption, QWidget,QHBoxLayout, QCheckBox, QComboBox, QTextCursor, QGroupBox, QToolButton, QDoubleSpinBox, 	QStatusBar, QPlainTextEdit
except:
    from PyQt4.QtCore import QIODevice, QFile, SIGNAL, SLOT, QObject, Qt
    from PyQt4.QtGui import QApplication, QFrame, QDial, QSlider, QPushButton, QFileDialog, QWidget, QMessageBox, QTextOption, QWidget,QHBoxLayout, QCheckBox, QComboBox, QTextCursor, QGroupBox, QToolButton, QDoubleSpinBox, 	QStatusBar, QPlainTextEdit


try:
    import psyco
    from psyco.classes import *
    psyco.log()
    psyco.profile(0.05)
    psyco.full()
    print 'Using psyco.'
except ImportError:
    print 'Not using psyco.'





from glViewport import GLWidget, mesh, printModel
import pyglet
import reprap
import log
import prefs
#import glSVG


defaultIcon = '\nborder: 0 solid ;\nborder-radius: 7;\nborder-color: rgb(150, 220,140);\nmargin-top: 0.0ex;background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.45, fx:0.386783, fy:0.358, '
comIcon = [
    defaultIcon +'stop:0 rgba(255, 169, 169, 255), stop:0.118227 rgba(214, 0, 0, 255), stop:0.82266 rgba(69, 0, 0, 255), stop:0.901478 rgba(0, 0, 0, 0), stop:1 rgba(0, 0, 0, 0));',
    defaultIcon +'stop:0 rgba( 169, 255,169, 255), stop:0.118227 rgba(0, 214, 0, 255), stop:0.82266 rgba(0, 69, 0, 255), stop:0.901478 rgba(0, 0, 0, 0), stop:1 rgba(0, 0, 0, 0));',
]

console = sys.stdout
stdoutLog = None
stderrLog = None


class struct():
    pass

class win(QFrame):
    def __init__(self, app=None):
        QFrame.__init__(self, None)

        self.svgGLViewer = None

        self.layerSliderValue = 0.5

        # load the draft.ui, a UI defination created on QT Creator.
        self.currentCom = ""

        USE_QTUITOOLS=False
        if USE_QTUITOOLS:
            import PySide.QtUiTools as QtUiTools
            QUiLoader = QtUiTools.QUiLoader()
            self.ui = QUiLoader.load('draft.ui')
        else:
            self.ui = draft_ui.Ui_Frame()
            self.ui.setupUi( self )
            def __findChild( *args):
                global _self
                _self = self
                ret =  eval("_self.ui.%s" % args[1])
                return ret
            self.ui.findChild = __findChild

        # main reprap object to comunicate with arduino
        self.reprap = reprap.device() #.cartesianClass()

        # fill combobox with available serial device names
        self.coms = self.ui.findChild(QComboBox, 'COMS')
        for each in self.reprap.comList:
            self.coms.addItem ( each, userData=self.reprap.comList[each] )

        # fill combobox with available displays to use for print ( the display connected to the projector)
        self.displays = self.ui.findChild(QComboBox, 'printDisplay')
        displayCount=1
        for each in pyglet.window.get_platform().get_default_display().get_screens():
            try: name = each.get_device_name().replace('\\\\.\\','')
            except:
                name = 'Display%d' % displayCount
                displayCount += 1
            menuOption = 'use %s-%dx%d' % (name, each.width, each.height)
            #print dir(each)
            print self.displays
            self.displays.addItem ( menuOption, each )

        # connect buttons to methods on this class
        self.connect(self.ui.findChild(QPushButton, 'loadGeo') , SIGNAL('clicked()'), lambda: self.loadGeo() )
#        self.connect(self.ui.findChild(QPushButton, 'sliceButton') , SIGNAL('clicked()'), lambda: self.sliceButton() )
        self.connect(self.ui.findChild(QPushButton, 'printButton') , SIGNAL('clicked()'), lambda: self.printButton() )
        self.connect(self.ui.findChild(QPushButton, 'connect') , SIGNAL('clicked()'), lambda: self.connectButton() )
        self.connect(self.ui.findChild(QToolButton, 'refil') , SIGNAL('clicked()'), lambda: self.refilButton() )

        self.connect(self.ui.findChild(QDial, 'sliceDial') , SIGNAL('sliderMoved(int)'), self.layerSlider )
#        self.connect(self.ui.findChild(QSlider, 'layer') , SIGNAL('sliderMoved(int)'), self.layerSlider )
#        self.connect(self.ui.findChild(QSlider, 'layer') , SIGNAL('valueChanged(int)'), self.layerSlider )


        # store those as direct children for easy access and save in config file.
        self.invertNormals          = self.ui.findChild(QCheckBox, 'invertNormals')
        self.expTime                = self.ui.findChild(QDoubleSpinBox, 'expTime')
        self.sliceThickness         = self.ui.findChild(QDoubleSpinBox, 'sliceThickness')
        self.axisSpeedSpinBox       = self.ui.findChild(QDoubleSpinBox, 'axisSpeed')

        self.connect(self.sliceThickness, SIGNAL('valueChanged(double)'), self.refreshGPU )
        self.connect(self.invertNormals, SIGNAL('clicked()'), self.refreshGPU )

        self.connect(self.axisSpeedSpinBox , SIGNAL('valueChanged(double)'), lambda: self.axisSpeed() )
        #self.axisSpeedSpinBox.valueChanged[float].connect(lambda: self.axisSpeed())
        self.axisSpeed()

        self.connect(self.ui.findChild(QToolButton, 'm10') , SIGNAL('clicked()'), lambda: self.moveZ(-10, True) )
        self.connect(self.ui.findChild(QToolButton, 'm1')  , SIGNAL('clicked()'), lambda: self.moveZ(-1, True) )
        self.connect(self.ui.findChild(QToolButton, 'm01') , SIGNAL('clicked()'), lambda: self.moveZ(-0.1, True) )

        self.connect(self.ui.findChild(QToolButton, 'p10') , SIGNAL('clicked()'), lambda: self.moveZ(10, True) )
        self.connect(self.ui.findChild(QToolButton, 'p1')  , SIGNAL('clicked()'), lambda: self.moveZ(1, True) )
        self.connect(self.ui.findChild(QToolButton, 'p01') , SIGNAL('clicked()'), lambda: self.moveZ(0.1, True) )

        #translate model
        self.modelTransform = struct()
        self.modelTransform.tx = self.ui.findChild(QDoubleSpinBox, 'modelMoveX')
        self.modelTransform.ty = self.ui.findChild(QDoubleSpinBox, 'modelMoveY')
        self.modelTransform.tz = self.ui.findChild(QDoubleSpinBox, 'modelMoveZ')
        self.modelTransform.rx = self.ui.findChild(QDoubleSpinBox, 'modelRotateX')
        self.modelTransform.ry = self.ui.findChild(QDoubleSpinBox, 'modelRotateY')
        self.modelTransform.rz = self.ui.findChild(QDoubleSpinBox, 'modelRotateZ')
        self.modelTransform.s = self.ui.findChild(QDoubleSpinBox, 'modelScale')

        def resetFunction( method, value, *sliders ):
            method( value,value,value, set=True)
            for each in sliders:
                each.setValue( value )

        moveFunction = lambda: self.moveModel(self.modelTransform.tx.value(), self.modelTransform.tz.value(), self.modelTransform.ty.value())
        self.connect(self.modelTransform.tx , SIGNAL('valueChanged(double)'), moveFunction )
        self.connect(self.modelTransform.ty , SIGNAL('valueChanged(double)'), moveFunction )
        self.connect(self.modelTransform.tz , SIGNAL('valueChanged(double)'), moveFunction )
        self.connect(self.ui.findChild(QPushButton, 'modelMoveReset') , SIGNAL('clicked()'), lambda: resetFunction( self.moveModel, 0.0, self.modelTransform.tx, self.modelTransform.ty, self.modelTransform.tz ) )

        rotateFunction = lambda: self.rotateModel(self.modelTransform.rx.value(), self.modelTransform.rz.value(), self.modelTransform.ry.value())
        self.connect(self.modelTransform.rx , SIGNAL('valueChanged(double)'), rotateFunction )
        self.connect(self.modelTransform.ry , SIGNAL('valueChanged(double)'), rotateFunction )
        self.connect(self.modelTransform.rz , SIGNAL('valueChanged(double)'), rotateFunction )
        self.connect(self.ui.findChild(QPushButton, 'modelRotateReset') , SIGNAL('clicked()'), lambda: resetFunction( self.rotateModel, 0.0, self.modelTransform.rx, self.modelTransform.ry, self.modelTransform.rz ) )

        scaleFunction = lambda: self.scaleModel(self.modelTransform.s.value(), self.modelTransform.s.value(), self.modelTransform.s.value())
        self.connect(self.modelTransform.s , SIGNAL('valueChanged(double)'), scaleFunction )
        self.connect(self.ui.findChild(QPushButton, 'modelScaleReset') , SIGNAL('clicked()'), lambda: resetFunction( self.scaleModel, 1.0, self.modelTransform.s ) )



        # VERY IMPORTANT!!! we MUST schedule glFrame to be deleted or else we get a thread fatal error in python!
        # this fix "Fatal Python error: PyEval_SaveThread: NULL tstate" error when using QtOpenGl Widgets!!
        def fix_PyEval_SaveThread_Fatal_Error_on_exit():
            self.glFrame.deleteLater()
            self.saveConfig()
        app.connect( app, SIGNAL('aboutToQuit()'), fix_PyEval_SaveThread_Fatal_Error_on_exit )

        # get light icon...
        self.comLight = self.ui.findChild(QGroupBox, 'ConnectLight')
        self.comLightState = 0
        self.setComIcon()

        # create a new GLWidget, parented to the ui main frame
        self.glFrame = GLWidget( self.ui.findChild(QWidget, 'frame') )
        self.glFrame.app = app

        # unit setup
        self.modelUnit = self.ui.findChild(QComboBox, 'modelUnit')
        unitz = prefs.units()
        unitzIndez = unitz.keys()
        unitzIndez.sort()
        for each in unitzIndez:
            self.modelUnit.addItem ( each, unitz[each] )
        self.modelUnit.setCurrentIndex( self.modelUnit.findText( 'mm' ) )
        def setCurrentUnit():
            self.glFrame.unit = unitz[str(self.modelUnit.currentText())]
            self.refreshGPU()
        self.connect( self.modelUnit , SIGNAL('currentIndexChanged(QString)'), setCurrentUnit )


        # load a default mesh into the opengl viewport
#        self.glFrame.addMesh( mesh('meshes/teapot.obj') )

        # add the glWidget to the framelayout of the main frame, so it resizes correctly.
        self.ui.findChild(QObject, 'frameLayout').addWidget( self.glFrame )

#        self.status = QStatusBar()
#        self.ui.findChild(QObject, 'statusBar').addWidget( self.status )
#        self.status.showMessage("Ready")

        self.logWin = self.ui.findChild(QPlainTextEdit, 'log')
        self.connect(self.logWin , SIGNAL('textChanged()'), lambda: self.logAppended() )
        self.logWin.setWordWrapMode( QTextOption.NoWrap )

        self.fileName = 'meshes/.'
        self.configFile = 'draft.config'

        self.loadConfig()

#        stdoutLog = log()
#        stderrLog = log(error=True)

        self.moveModel(0,0,0, set=True)
        self.rotateModel(0,0,0, set=True)
        self.scaleModel(1,1,1, set=True)

    def saveConfig(self):
        checkBoxStates = {
            Qt.Unchecked        : 'Qt.Unchecked',
            Qt.PartiallyChecked : 'Qt.PartiallyChecked',
            Qt.Checked          : 'Qt.Checked',
        }
        f = open( self.configFile, 'w' )
        f.write( 'self.currentCom = "%s"\n' % self.currentCom )
        f.write( 'self.fileName = "%s"\n' % self.fileName )
        f.write( 'self.axisSpeedSpinBox.setValue(%s)\n' % str(self.axisSpeedSpinBox.value()) )
        f.write( 'self.sliceThickness.setValue(%s)\n' % str(self.sliceThickness.value()) )
        f.write( 'self.expTime.setValue(%s)\n' % str(self.expTime.value()) )
#        f.write( 'self.startPrintAfterSlice.setCheckState(%s)\n' % checkBoxStates[ self.startPrintAfterSlice.checkState() ] )

        f.flush()
        f.close()

    def loadConfig(self):
        if os.path.exists( self.configFile ):
            for l in open( self.configFile ):
                try:
                    exec( l )
                except:
                    pass

            self.refreshMesh()

    def moveModel(self, x, y, z, set=True):
        if set:
            self.glFrame.moveOBJ = [x,y,z]
        else:
            self.glFrame.moveOBJ[0] += x
            self.glFrame.moveOBJ[1] += y
            self.glFrame.moveOBJ[2] += z
        self.refreshGPU()

    def rotateModel(self, x, y, z, set=True):
        if set:
            self.glFrame.rotateOBJ = [x,y,z]
        else:
            self.glFrame.rotateOBJ[0] += x
            self.glFrame.rotateOBJ[1] += y
            self.glFrame.rotateOBJ[2] += z
        self.refreshGPU()

    def scaleModel(self, x, y, z, set=True):
        if set:
            self.glFrame.scaleOBJ = [x,y,z]
        else:
            self.glFrame.scaleOBJ[0] += x
            self.glFrame.scaleOBJ[1] += y
            self.glFrame.scaleOBJ[2] += z
        self.refreshGPU()


    def logAppended(self):
#        bar = self.logWin.verticalScrollBar()
#        x = bar.value()
#        bar.setValue(x-10)
#        bar.repaint()
#        self.logWin.moveCursor( QTextCursor.Start )
#        self.logWin.repaint()
        self.logWin.ensureCursorVisible()# ( QTextCursor.End )
#        self.logWin.repaint()

    def layerSlider(self, value):
        self.layerSliderValue = float(value)/100.0
        self.refreshGPU()


    def refilButton(self):
        self.glFrame.install_shaders( )
        self.refreshGPU()

    def axisSpeed( self ):
        self.reprap.z.speed( float(self.axisSpeedSpinBox.value()) )

    def moveZ(self, mm, relative=False):
        self.reprap.z.move( mm, relative )

    def arduinoException(self):
        self.disconnect()
        print "arduinoException!!" ; sys.stdout.flush()

    def setComIcon(self, state=None):
        if state:
            self.comLightState = state
        self.comLight.setStyleSheet( comIcon[self.comLightState ] )
#        self.comLight.repaint()

#    def show(self):
#        self.show()


    def disconnect(self):
        self.serialConnected = False
        self.setComIcon(self.serialConnected)
        try:
            self.reprap.close()
        except:
            pass

    def connectButton(self):
        self.currentCom = self.coms.currentText()

        self.disconnect()

        # Initialise serial port, here the first port (0) is used.
        try:
            self.reprap.connect( self.currentCom , 57600 )
        except:
            self.arduinoException()
            return

        self.serialConnected = True
        self.setComIcon(self.serialConnected)

    def homeButton(self):
        try:
            reprap.cartesian.homeReset()
        except:
            self.arduinoException()

    def sliceButton(self):
        pass
#        if not self.svgGLViewer:
#            self.svgGLViewer = glSVG.PygletApp( )

#        self.svgGLViewer.load( self.fileName )
#        self.svgGLViewer.run()

    def printButton(self):
        try:
            reprap.cartesian.homeReset()
        except:
            self.arduinoException()

        #self.glFrame.fullScreen()
        render = printModel( prefs.cs1, False, self.fileName, self.glFrame.meshs, self.displays.itemData( self.displays.currentIndex() ) )
        render.run()



    def loadGeo(self, *args):
        dialog = QFileDialog(self)
        #dialog.setFileMode(QFileDialog.AnyFile)
        if not self.fileName:
            dialog.setDirectory('meshes')
        else:
            dialog.setDirectory(os.path.dirname(self.fileName))

        dialog.setNameFilter("Images (*.obj *.stl)")

        if dialog.exec_():
            self.fileName = str(dialog.selectedFiles()[0])

            self.refreshMesh()


    def refreshGPU(self):
        if hasattr( self.glFrame, "shader" ):
            print "refreshGPU", self.layerSliderValue
            thickness = float(self.sliceThickness.value())/10000.0
            try:
                self.glFrame.s['slicer'].bind()
                self.glFrame.shader.uniformf( 'layer', self.layerSliderValue )
                self.glFrame.shader.uniformf( 'invertNormals', float(self.invertNormals.checkState()) )
                self.glFrame.s['slicer'].unbind()
            except:
                pass

        self.glFrame.updateGL()


    def refreshMesh( self ):
        if not os.path.exists(self.fileName):
            self.fileName = os.path.abspath( './%s' % self.fileName)
            if not os.path.exists( self.fileName ):
                return
        if not os.path.isfile(self.fileName):
            return
        self.glFrame.addMesh( mesh(self.fileName) )
        self.modelUnit.setCurrentIndex( self.modelUnit.findText( 'mm' ) )
        self.refreshGPU()



#try:
app = QApplication(sys.argv)
w=win(app)
log.log( w.logWin )
w.show()

app.exec_()
#except Exception, err:
#    stderrLog.handleException(Exception, err)
