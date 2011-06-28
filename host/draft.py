

from ctypes import util
import sys, os, time
sys.path += [ '.' ]
#os.environ[ 'PATH' ] = '.%s%s' % ( os.path.pathsep, os.environ[ 'PATH' ] )


from PySide.QtCore import QIODevice, QFile, SIGNAL, SLOT, QObject, Qt
from PySide.QtGui import QApplication, QPushButton, QFileDialog, QWidget, QMessageBox, QTextOption, QWidget,QHBoxLayout, QCheckBox, QComboBox, QTextCursor, QGroupBox, QToolButton, QDoubleSpinBox, 	QStatusBar, QPlainTextEdit 
import PySide.QtUiTools as QtUiTools

from glViewport import GLWidget, mesh

import reprap
from log import log

defaultIcon = '\nborder: 0	px solid ;\nborder-radius: 7px;\nborder-color: rgb(150, 220,140);\nmargin-top: 0.0ex;background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.45, fx:0.386783, fy:0.358, '
comIcon = [
    defaultIcon +'stop:0 rgba(255, 169, 169, 255), stop:0.118227 rgba(214, 0, 0, 255), stop:0.82266 rgba(69, 0, 0, 255), stop:0.901478 rgba(0, 0, 0, 0), stop:1 rgba(0, 0, 0, 0));', 
    defaultIcon +'stop:0 rgba( 169, 255,169, 255), stop:0.118227 rgba(0, 214, 0, 255), stop:0.82266 rgba(0, 69, 0, 255), stop:0.901478 rgba(0, 0, 0, 0), stop:1 rgba(0, 0, 0, 0));', 
]

console = sys.stdout
stdoutLog = log()
stderrLog = log(error=True)


class win(QWidget):
    def __init__(self, app=None):
        QWidget.__init__(self, None)
        
        # load the draft.ui, a UI defination created on QT Creator.
        QUiLoader = QtUiTools.QUiLoader()
        self.currentCom = ""
        self.ui = QUiLoader.load('draft.ui')
        
        # main reprap object to comunicate with arduino
        self.reprap = reprap.device() #.cartesianClass()
        
        # fill combobox with available serial device names
        self.coms = self.ui.findChild(QComboBox, 'COMS') 
        for each in self.reprap.comList:
            self.coms.addItem ( each, userData=self.reprap.comList[each] )
        
        # connect buttons to methods on this class
        self.ui.connect(self.ui.findChild(QPushButton, 'loadGeo') , SIGNAL('clicked()'), lambda: self.loadGeo() )
        self.ui.connect(self.ui.findChild(QPushButton, 'sliceButton') , SIGNAL('clicked()'), lambda: self.sliceButton() )
        self.ui.connect(self.ui.findChild(QPushButton, 'printButton') , SIGNAL('clicked()'), lambda: self.printButton() )
        self.ui.connect(self.ui.findChild(QPushButton, 'connect') , SIGNAL('clicked()'), lambda: self.connectButton() )

        # store those as direct children for easy access and save in config file.
        self.startPrintAfterSlice   = self.ui.findChild(QCheckBox, 'startPrintAfterSlice') 
        self.expTime                = self.ui.findChild(QDoubleSpinBox, 'expTime') 
        self.sliceThickness         = self.ui.findChild(QDoubleSpinBox, 'sliceThickness') 
        self.axisSpeedSpinBox       = self.ui.findChild(QDoubleSpinBox, 'axisSpeed') 
        
        
        #self.ui.connect(self.axisSpeedSpinBox , SIGNAL('valueChanged()'), lambda: self.axisSpeed() )
        self.axisSpeedSpinBox.valueChanged[float].connect(lambda: self.axisSpeed())
        self.axisSpeed()

        self.ui.connect(self.ui.findChild(QToolButton, 'm10') , SIGNAL('clicked()'), lambda: self.moveZ(-10, True) )
        self.ui.connect(self.ui.findChild(QToolButton, 'm1')  , SIGNAL('clicked()'), lambda: self.moveZ(-1, True) )
        self.ui.connect(self.ui.findChild(QToolButton, 'm01') , SIGNAL('clicked()'), lambda: self.moveZ(-0.1, True) )
        
        self.ui.connect(self.ui.findChild(QToolButton, 'p10') , SIGNAL('clicked()'), lambda: self.moveZ(10, True) )
        self.ui.connect(self.ui.findChild(QToolButton, 'p1')  , SIGNAL('clicked()'), lambda: self.moveZ(1, True) )
        self.ui.connect(self.ui.findChild(QToolButton, 'p01') , SIGNAL('clicked()'), lambda: self.moveZ(0.1, True) )

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
        
        # load a default mesh into the opengl viewport
#        self.glFrame.addMesh( mesh('meshes/teapot.obj') )
       
        # add the glWidget to the framelayout of the main frame, so it resizes correctly.
        self.ui.findChild(QObject, 'frameLayout').addWidget( self.glFrame )
        
#        self.status = QStatusBar()
#        self.ui.findChild(QObject, 'statusBar').addWidget( self.status )
#        self.status.showMessage("Ready")

        self.logWin = self.ui.findChild(QPlainTextEdit, 'log')
        self.ui.connect(self.logWin , SIGNAL('textChanged()'), lambda: self.logAppended() )
        self.logWin.setWordWrapMode( QTextOption.NoWrap )
        
        self.fileName = "teapot.obj"
        self.configFile = 'draft.config'
        
        self.loadConfig()
        
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
        f.write( 'self.startPrintAfterSlice.setCheckState(%s)\n' % checkBoxStates[ self.startPrintAfterSlice.checkState() ] )
        
        f.flush()
        f.close()
        
    def loadConfig(self):
        for l in open( self.configFile ):
            exec( l )
                
        self.refreshMesh()

    
    def logAppended(self):
#        bar = self.logWin.verticalScrollBar()
#        x = bar.value()
#        bar.setValue(x-10)
#        bar.repaint()
#        self.logWin.moveCursor( QTextCursor.Start )
#        self.logWin.repaint()
        self.logWin.ensureCursorVisible()# ( QTextCursor.End )
        self.logWin.repaint()
        
        
    def axisSpeed( self ):
        print 'ssss' ; sys.stdout.flush()
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
        self.comLight.repaint()
        
    def show(self):
        self.ui.show()
        
        
    def disconnect(self):
        self.serialConnected = False
        self.setComIcon(self.serialConnected)
        self.reprap.close()
            
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
        
    def printButton(self):
        try:
            reprap.cartesian.homeReset()
        except: 
            self.arduinoException()
        

    def loadGeo(self, *args):
        dialog = QFileDialog(self)
        #dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setDirectory('meshes')
        dialog.setNameFilter("Images (*.obj *.stl)")
        
        self.fileName = ""
        if dialog.exec_():
            self.fileName = dialog.selectedFiles()[0]
        
        self.refreshMesh()
    
    def refreshMesh( self ):
        if not os.path.exists(self.fileName):
            self.fileName = os.path.abspath( './%s' % self.fileName)
            if not os.path.exists( self.fileName ):
                return
        self.glFrame.addMesh( mesh(self.fileName) )
        

stdoutLog = log()
stderrLog = log(error=True)
try:
    app = QApplication(sys.argv)
    w=win(app)
    stdoutLog.attachLog(w.logWin)
    stderrLog.attachLog(w.logWin)
    sys.stdout = stdoutLog 
    sys.stderr = stderrLog
    w.show()

    app.exec_()
except Exception, err:
    stderrLog.handleException(Exception, err)
