INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_PREDISTORT predistort)

FIND_PATH(
    PREDISTORT_INCLUDE_DIRS
    NAMES predistort/api.h
    HINTS $ENV{PREDISTORT_DIR}/include
        ${PC_PREDISTORT_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    PREDISTORT_LIBRARIES
    NAMES gnuradio-predistort
    HINTS $ENV{PREDISTORT_DIR}/lib
        ${PC_PREDISTORT_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/predistortTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(PREDISTORT DEFAULT_MSG PREDISTORT_LIBRARIES PREDISTORT_INCLUDE_DIRS)
MARK_AS_ADVANCED(PREDISTORT_LIBRARIES PREDISTORT_INCLUDE_DIRS)
