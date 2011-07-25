#  SHIBOKEN_INCLUDE_DIR        - Directories to include to use SHIBOKEN
#  SHIBOKEN_LIBRARY            - Files to link against to use SHIBOKEN
#  SHIBOKEN_BINARY             - Executable name
#  SHIBOKEN_BUILD_TYPE         - Tells if Shiboken was compiled in Release or Debug mode.
#  SHIBOKEN_PYTHON_INTERPRETER - Python interpreter (regular or debug) to be used with the bindings.
#  SHIBOKEN_PYTHON_LIBRARIES   - Python libraries (regular or debug) Shiboken is linked against.

SET(SHIBOKEN_INCLUDE_DIR "/Volumes/ramdisk/install/usr/include/shiboken")
if(MSVC)
   SET(SHIBOKEN_LIBRARY "/Volumes/ramdisk/install/usr/lib/libshiboken-python2.7.lib")
elseif(WIN32)
    SET(SHIBOKEN_LIBRARY "/Volumes/ramdisk/install/usr/bin/libshiboken-python2.7.dylib")
else()
    SET(SHIBOKEN_LIBRARY "/Volumes/ramdisk/install/usr/lib/libshiboken-python2.7.dylib")
endif()
SET(SHIBOKEN_PYTHON_INCLUDE_DIR "/Library/Frameworks/Python.framework/Headers")
SET(SHIBOKEN_PYTHON_INCLUDE_DIR "/Library/Frameworks/Python.framework/Headers")
SET(SHIBOKEN_PYTHON_INTERPRETER "/Library/Frameworks/Python.framework/Versions/2.7/bin/python2.7")
SET(SHIBOKEN_PYTHON_LIBRARIES "-undefined dynamic_lookup")
SET(SHIBOKEN_PYTHON_BASENAME "python2.7")
message(STATUS "libshiboken built for Release")


set(SHIBOKEN_BINARY "/Volumes/ramdisk/install/usr/bin/shiboken")
