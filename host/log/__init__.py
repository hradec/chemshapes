


from PySide.QtCore import QIODevice, QFile, SIGNAL, SLOT, QObject
from PySide.QtGui import QPlainTextEdit 
import PySide.QtUiTools as QtUiTools

import time, traceback

class log:
    def __init__(self, logfile='log.html', QPlainTextEdit_widget=None, error=False):
        self.attachLog( QPlainTextEdit_widget )
        self.logfile = logfile
#        self._write('='*80, cleanText=True)
#        self._write('new log started...', cleanText=True)
        self.error = error

    def remove(self):
        self._write('='*80, cleanText=True)

    def attachLog( self, QPlainTextEdit_widget ):
        self.QPlainTextEdit_widget = QPlainTextEdit_widget 
         
    def _write(self, msg, warning = False, error = False, cleanText=False):
        msg = msg.rstrip()
        if msg:
            if not cleanText:
                if self.error:
                    msg = '<FONT COLOR="#ff0000" ><strong>PYTHON EXCEPTION:</strong></FONT> \t<FONT COLOR="#cc6600">%s</FONT>' % msg
                elif warning:
                    msg = '<FONT COLOR="#eeee00"><strong>WARNING:</strong></FONT> <FONT COLOR="#aaaa00">%s</FONT>' % msg
                elif error:
                    msg = '<FONT COLOR="#ff0000"><strong>ERROR:</strong></FONT> <FONT COLOR="#aa3300">%s</FONT>' % msg
                else:
                    msg = '<FONT COLOR="#00aa00">%s</FONT>' % msg
                msg =  '%s >>  %s' % (time.ctime(),msg)
            if self.QPlainTextEdit_widget:
                self.QPlainTextEdit_widget.appendHtml ( msg )
            self.logFile = open(self.logfile,'a')
            self.logFile.write( '%s\n' % msg )
            self.logFile.flush()
            self.logFile.close()

    def flush(self):
        pass

    def write( self, str ):
        self._write( str, 
            error = ( 'exception' in str.lower() or 'error' in str.lower() ),
            warning = ( 'warning' in str.lower() or 'attention' in str.lower() )
         )
        
    def warning( self, str ):
        self._write( 'WARNING: %s' % str )
        
    def error( self, str ):
        self._write( 'ERROR: %s' % str )
    
    def handleException(self, Exception, err):
        self._write( 'EXCEPTION: %s' % traceback.format_exc() )

        
    
    