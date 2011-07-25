#  GENERATORRUNNER_INCLUDE_DIR   - Directories to include to use GENERATORRUNNER
#  GENERATORRUNNER_LIBRARIES     - Files to link against to use GENERATORRUNNER
#  GENERATORRUNNER_PLUGIN_DIR    - Where to find/put plugins for generator runner
#  GENERATORRUNNER_BINARY        - Executable name

SET(GENERATORRUNNER_INCLUDE_DIR "/Volumes/ramdisk/install/usr/include/generatorrunner")
if(MSVC)
    SET(GENERATORRUNNER_LIBRARY "/Volumes/ramdisk/install/usr/lib/libgenrunner.lib")
elseif(WIN32)
    SET(GENERATORRUNNER_LIBRARY "/Volumes/ramdisk/install/usr/bin/libgenrunner.dylib")
else()
    SET(GENERATORRUNNER_LIBRARY "/Volumes/ramdisk/install/usr/lib/libgenrunner.dylib")
endif()
SET(GENERATORRUNNER_PLUGIN_DIR "/Volumes/ramdisk/install/usr/lib/generatorrunner")
SET(GENERATORRUNNER_BINARY "/Volumes/ramdisk/install/usr/bin/generatorrunner")
