/* -*- c++ -*- */
/*
 * Copyright 2026 NIWC PAC.
 *
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "mult_complex_by_msg_impl.h"

namespace gr {
  namespace predistort {

    mult_complex_by_msg::sptr
    mult_complex_by_msg::make()
    {
      return gnuradio::get_initial_sptr
        (new mult_complex_by_msg_impl());
    }


    /*
     * The private constructor
     */
    mult_complex_by_msg_impl::mult_complex_by_msg_impl()
      : gr::sync_block("mult_complex_by_msg",
              gr::io_signature::make(1,1, sizeof(gr_complex)),
              gr::io_signature::make(1,1, sizeof(gr_complex))), d_val(0), d_scalar(true), d_val_real(0), d_val_imag(0)
    {
      message_port_register_in(pmt::intern("ctrl_in"));

      set_msg_handler(pmt::mp("ctrl_in"),
                  [this](pmt::pmt_t msg) { this->handle_msg(msg); });
    }

    /*
     * Our virtual destructor.
     */
    mult_complex_by_msg_impl::~mult_complex_by_msg_impl()
    {
    }

    void mult_complex_by_msg_impl::handle_msg(pmt::pmt_t msg)
    {
        // Lock mutex to prevent race conditions with general_work
        std::lock_guard<std::mutex> lock(d_mutex);

        // We expect a PMT pair like: (intern("stream") . 1)
        if (pmt::is_pair(msg)) 
        {
          if (pmt::eq(pmt::car(msg), pmt::intern("value"))) 
          {
            pmt::pmt_t msg_cdr = pmt::cdr(msg);
            if(pmt::is_f32vector(msg_cdr))
            {
              d_scalar = false;
              d_val_real = (pmt::f32vector_ref(msg_cdr, 0));
              d_val_imag = (pmt::f32vector_ref(msg_cdr, 1));
            }
            else
            {
              d_scalar = true;
              d_val = pmt::to_double(msg_cdr);
            }
          }
        } 
    }

    int
    mult_complex_by_msg_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      std::lock_guard<std::mutex> lock(d_mutex);

      // Pointer arithmetic for copying memory
      const gr_complex *in = (const gr_complex *) input_items[0];
      gr_complex *out = (gr_complex *) output_items[0];

      if(d_scalar)
      {
        for(int i=0; i<noutput_items; i++)
        {
          out[i] = in[i] * d_val;
        }
      }
      else
      {
        for(int i=0; i<noutput_items; i++)
        {
          out[i] = gr_complex(in[i].real() * d_val_real, in[i].imag() * d_val_imag);
        }
      }

      return noutput_items;   
    }

  } /* namespace predistort */
} /* namespace gr */

