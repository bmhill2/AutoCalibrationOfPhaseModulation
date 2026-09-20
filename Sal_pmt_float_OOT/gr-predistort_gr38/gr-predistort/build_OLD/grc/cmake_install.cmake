# Install script for directory: /home/sal/Documents/nanouhf/GR38/gr-predistort/grc

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/home/sal/prefix/gr38")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set default install directory permissions.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/objdump")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/gnuradio/grc/blocks" TYPE FILE FILES
    "/home/sal/Documents/nanouhf/GR38/gr-predistort/grc/predistort_async_signal_mux.block.yml"
    "/home/sal/Documents/nanouhf/GR38/gr-predistort/grc/predistort_add_by_msg.block.yml"
    "/home/sal/Documents/nanouhf/GR38/gr-predistort/grc/predistort_add_complex_by_msg.block.yml"
    "/home/sal/Documents/nanouhf/GR38/gr-predistort/grc/predistort_mult_by_msg.block.yml"
    "/home/sal/Documents/nanouhf/GR38/gr-predistort/grc/predistort_mult_complex_by_msg.block.yml"
    "/home/sal/Documents/nanouhf/GR38/gr-predistort/grc/predistort_iq_delay_by_msg.block.yml"
    "/home/sal/Documents/nanouhf/GR38/gr-predistort/grc/predistort_delay_msg.block.yml"
    "/home/sal/Documents/nanouhf/GR38/gr-predistort/grc/predistort_fractional_delay_msg.block.yml"
    )
endif()

