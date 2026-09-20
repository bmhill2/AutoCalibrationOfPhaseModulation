# Install script for directory: /home/brendan/Documents/Sal_pmt_float_OOT/gr-predistort_gr38/gr-predistort/include/predistort

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/home/brendan/prefix-3.8")
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

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/predistort" TYPE FILE FILES
    "/home/brendan/Documents/Sal_pmt_float_OOT/gr-predistort_gr38/gr-predistort/include/predistort/api.h"
    "/home/brendan/Documents/Sal_pmt_float_OOT/gr-predistort_gr38/gr-predistort/include/predistort/async_signal_mux.h"
    "/home/brendan/Documents/Sal_pmt_float_OOT/gr-predistort_gr38/gr-predistort/include/predistort/add_by_msg.h"
    "/home/brendan/Documents/Sal_pmt_float_OOT/gr-predistort_gr38/gr-predistort/include/predistort/add_complex_by_msg.h"
    "/home/brendan/Documents/Sal_pmt_float_OOT/gr-predistort_gr38/gr-predistort/include/predistort/mult_by_msg.h"
    "/home/brendan/Documents/Sal_pmt_float_OOT/gr-predistort_gr38/gr-predistort/include/predistort/mult_complex_by_msg.h"
    "/home/brendan/Documents/Sal_pmt_float_OOT/gr-predistort_gr38/gr-predistort/include/predistort/iq_delay_by_msg.h"
    "/home/brendan/Documents/Sal_pmt_float_OOT/gr-predistort_gr38/gr-predistort/include/predistort/delay_msg.h"
    "/home/brendan/Documents/Sal_pmt_float_OOT/gr-predistort_gr38/gr-predistort/include/predistort/fractional_delay_msg.h"
    )
endif()

