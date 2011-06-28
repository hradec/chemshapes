#!python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'PySide==1.0.2qt472','console_scripts','pyside-uic'
__requires__ = 'PySide==1.0.2qt472'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('PySide==1.0.2qt472', 'console_scripts', 'pyside-uic')()
    )
