


from PySide.QtCore import QIODevice, QFile, SIGNAL, SLOT, QObject
from PySide.QtGui import QPlainTextEdit 

import time, traceback, socket, sys

_stdout_bkp = sys.stdout
_stderr_bkp = sys.stderr


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    
    
class log:
    def __init__(self, logfile='log_%s.html' % socket.gethostname(), QPlainTextEdit_widget=None, error=False):
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
            cleanMsg = msg
            if not cleanText:
                if self.error:
                    print >> _stderr_bkp, bcolors.FAIL, msg
                    msg = '<FONT COLOR="#ff0000" ><strong>PYTHON EXCEPTION:</strong></FONT> \t<FONT COLOR="#FF1100">%s</FONT>' % msg
                elif warning:
                    print >> _stdout_bkp, bcolors.WARNING, msg
                    msg = '<FONT COLOR="#eeee00"><strong>WARNING:</strong></FONT> <FONT COLOR="#aaaa00">%s</FONT>' % msg
                elif error:
                    print >> _stderr_bkp, bcolors.FAIL, msg
                    msg = '<FONT COLOR="#ff0000"><strong>ERROR:</strong></FONT> <FONT COLOR="#aa3300">%s</FONT>' % msg
                else:
                    print >> _stdout_bkp, bcolors.OKGREEN, msg
                    msg = '<FONT COLOR="#00aa00">%s</FONT>' % msg
                msg =  '%s >>  %s' % (time.ctime(),msg)
                msg = '<pre>%s</pre><br>'  % msg #.replace('\n','<br>                 ')
            if self.QPlainTextEdit_widget:
                self.QPlainTextEdit_widget.appendHtml ( msg )
            self.logFile = open(self.logfile,'a')
            self.logFile.write( msg )
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

        
    
    