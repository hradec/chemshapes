# - try to find APIEXTRACTOR
#  APIEXTRACTOR_INCLUDE_DIR   - Directories to include to use APIEXTRACTOR
#  APIEXTRACTOR_LIBRARIES     - Files to link against to use APIEXTRACTOR

SET(APIEXTRACTOR_INCLUDE_DIR "/Volumes/ramdisk/install/usr/include/apiextractor")
if(MSVC)
    SET(APIEXTRACTOR_LIBRARY "/Volumes/ramdisk/install/usr/lib/libapiextractor.lib")
elseif(WIN32)
    SET(APIEXTRACTOR_LIBRARY "/Volumes/ramdisk/install/usr/bin/libapiextractor.dylib")
else()
    SET(APIEXTRACTOR_LIBRARY "/Volumes/ramdisk/install/usr/lib/libapiextractor.dylib")
endif()

SET(APIEXTRACTOR_DOCSTRINGS_DISABLED OFF)
