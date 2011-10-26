

try:
    from PySide.QtCore import QIODevice, QFile, SIGNAL, SLOT, QObject
    from PySide.QtGui import QPlainTextEdit
except:
    from PyQt4.QtCore import QIODevice, QFile, SIGNAL, SLOT, QObject
    from PyQt4.QtGui import QPlainTextEdit

import time, traceback, socket, sys


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


class log:
    def __init__(self, QPlainTextEdit_widget=None, logfile='log_%s.html' % socket.gethostname(), error=False):
        sys.stdout = self.__log(QPlainTextEdit_widget=QPlainTextEdit_widget)
        sys.stderr = self.__log(QPlainTextEdit_widget=QPlainTextEdit_widget, error=True)

    class __log:
        def __init__(self, logfile='log_%s.html' % socket.gethostname(), QPlainTextEdit_widget=None, error=False):
            self.attachLog( QPlainTextEdit_widget )
            self.logfile = logfile
    #        self._write('='*80, cleanText=True)
    #        self._write('new log started...', cleanText=True)
            self.error = error
            self.sysStdOut = sys.stdout
            self.sysStdErr = sys.stderr

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
                        print >> self.sysStdErr, bcolors.FAIL, msg ; self.sysStdErr.flush()
                        msg = '<FONT COLOR="#ff0000" ><strong>PYTHON EXCEPTION:</strong></FONT> \t<FONT COLOR="#FF1100">%s</FONT>' % msg
                    elif warning:
                        print >> self.sysStdOut, bcolors.WARNING, msg ; self.sysStdOut.flush()
                        msg = '<FONT COLOR="#eeee00"><strong>WARNING:</strong></FONT> <FONT COLOR="#aaaa00">%s</FONT>' % msg
                    elif error:
                        print >> self.sysStdErr, bcolors.FAIL, msg ; self.sysStdErr.flush()
                        msg = '<FONT COLOR="#ff0000"><strong>ERROR:</strong></FONT> <FONT COLOR="#aa3300">%s</FONT>' % msg
                    else:
                        print >> self.sysStdOut, bcolors.OKGREEN, msg ; self.sysStdOut.flush()
                        msg = '<FONT COLOR="#00aa00">%s</FONT>' % msg
                    msg =  '%s >>  %s' % (time.ctime(),msg)
                    msg = '<pre>%s</pre><br>'  % msg #.replace('\n','<br>                 ')
                if self.QPlainTextEdit_widget:
                    self.QPlainTextEdit_widget.appendHtml ( msg.strip('<br>') )
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



