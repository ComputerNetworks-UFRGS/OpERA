INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_OPERA opera)

FIND_PATH(
    OPERA_INCLUDE_DIRS
    NAMES opera/api.h
    HINTS $ENV{OPERA_DIR}/include
        ${PC_OPERA_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREEFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    OPERA_LIBRARIES
    NAMES gnuradio-opera
    HINTS $ENV{OPERA_DIR}/lib
        ${PC_OPERA_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(OPERA DEFAULT_MSG OPERA_LIBRARIES OPERA_INCLUDE_DIRS)
MARK_AS_ADVANCED(OPERA_LIBRARIES OPERA_INCLUDE_DIRS)

