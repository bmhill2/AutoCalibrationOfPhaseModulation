/* -*- c++ -*- */

#define PREDISTORT_API

%include "gnuradio.i"           // the common stuff

//load generated python docstrings
%include "predistort_swig_doc.i"

%{
#include "predistort/async_signal_mux.h"
#include "predistort/add_by_msg.h"
#include "predistort/add_complex_by_msg.h"
#include "predistort/mult_by_msg.h"
#include "predistort/mult_complex_by_msg.h"
#include "predistort/iq_delay_by_msg.h"
#include "predistort/delay_msg.h"
#include "predistort/fractional_delay_msg.h"
%}

%include "predistort/async_signal_mux.h"
GR_SWIG_BLOCK_MAGIC2(predistort, async_signal_mux);



%include "predistort/add_by_msg.h"
GR_SWIG_BLOCK_MAGIC2(predistort, add_by_msg);
%include "predistort/add_complex_by_msg.h"
GR_SWIG_BLOCK_MAGIC2(predistort, add_complex_by_msg);
%include "predistort/mult_by_msg.h"
GR_SWIG_BLOCK_MAGIC2(predistort, mult_by_msg);
%include "predistort/mult_complex_by_msg.h"
GR_SWIG_BLOCK_MAGIC2(predistort, mult_complex_by_msg);

%include "predistort/iq_delay_by_msg.h"
GR_SWIG_BLOCK_MAGIC2(predistort, iq_delay_by_msg);
%include "predistort/delay_msg.h"
GR_SWIG_BLOCK_MAGIC2(predistort, delay_msg);
%include "predistort/fractional_delay_msg.h"
GR_SWIG_BLOCK_MAGIC2(predistort, fractional_delay_msg);
