/* -*- c++ -*- */
/*
 * Copyright 2026 Salwan Damman.
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
#include "add_by_msg_impl.h"
#include <volk/volk.h>

namespace gr {
  namespace predistort {

    add_by_msg::sptr
    add_by_msg::make()
    {
      return gnuradio::get_initial_sptr
        (new add_by_msg_impl());
    }

    /*
     * The private constructor
     */
    add_by_msg_impl::add_by_msg_impl()
      : gr::sync_block("add_by_msg",
              gr::io_signature::make(1,1, sizeof(float)),
              gr::io_signature::make(1,1, sizeof(float))), d_val(0)
    {
      message_port_register_in(pmt::intern("msg_in"));

      set_msg_handler(pmt::mp("msg_in"),
                  [this](pmt::pmt_t msg) { this->handle_msg(msg); });
    }

    /*
     * Our virtual destructor.
     */
    add_by_msg_impl::~add_by_msg_impl()
    {
    }

    void add_by_msg_impl::handle_msg(pmt::pmt_t msg)
    {
        // Lock mutex to prevent race conditions with general_work
        std::lock_guard<std::mutex> lock(d_mutex);

        // We expect a PMT pair like: (intern("stream") . 1)
        if (pmt::is_pair(msg)) 
        {
          if (pmt::eq(pmt::car(msg), pmt::intern("value"))) 
          {
            d_val = pmt::to_long(pmt::cdr(msg));
          }
        } 
    }

    int
    add_by_msg_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      std::lock_guard<std::mutex> lock(d_mutex);

      // Pointer arithmetic for copying memory
      const float *in = (const float *) input_items[0];
      float *out = (float *) output_items[0];

      for(int i=0; i<noutput_items; i++)
      {
        out[i] = in[i] + d_val;
      }

      return noutput_items;
    }

  } /* namespace predistort */
} /* namespace gr */

