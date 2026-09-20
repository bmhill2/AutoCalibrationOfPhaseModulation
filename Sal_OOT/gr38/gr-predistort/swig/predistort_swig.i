/* -*- c++ -*- */

#define PREDISTORT_API

%include "gnuradio.i"           // the common stuff

//load generated python docstrings
%include "predistort_swig_doc.i"

%{
#include "predistort/async_signal_mux.h"
%}

%include "predistort/async_signal_mux.h"
GR_SWIG_BLOCK_MAGIC2(predistort, async_signal_mux);
