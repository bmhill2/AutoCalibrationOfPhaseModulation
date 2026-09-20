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
#include "delay_msg_impl.h"

namespace gr {
  namespace predistort {

    delay_msg::sptr
    delay_msg::make(int max_delay)
    {
      return gnuradio::get_initial_sptr
        (new delay_msg_impl( max_delay));
    }


    /*
     * The private constructor
     */
    delay_msg_impl::delay_msg_impl(int max_delay)
      : gr::sync_block("delay_msg",
                     gr::io_signature::make(1, 1, sizeof(float)),
                     gr::io_signature::make(1, 1, sizeof(float))),
      d_max_delay(std::max(1, max_delay)),
      d_write_idx(0),
      d_delay_val(0)
    {
      // Compute next power-of-two buffer size >= (max_delay + 1)
      d_buf_size = 1;
      while (d_buf_size <= static_cast<size_t>(d_max_delay)) {
          d_buf_size <<= 1;
      }
      d_mask = d_buf_size - 1;

      d_buf_val.assign(d_buf_size, 0.0f);

      message_port_register_in(pmt::intern("ctrl_in"));

      set_msg_handler(pmt::mp("ctrl_in"),
                  [this](pmt::pmt_t msg) { this->handle_msg(msg); });
    }

    /*
     * Our virtual destructor.
     */
    delay_msg_impl::~delay_msg_impl()
    {
    }

    void delay_msg_impl::handle_msg(pmt::pmt_t msg)
    {
        int read_idx_val = d_delay_val.load();

        if (pmt::is_pair(msg)) 
        {
          if (pmt::eq(pmt::car(msg), pmt::intern("value"))) 
          {
            pmt::pmt_t msg_cdr = pmt::cdr(msg);
            read_idx_val = (pmt::to_long(msg_cdr));
            
          }
        } 

        read_idx_val = std::max(0, std::min(read_idx_val, d_max_delay));

        d_delay_val.store(read_idx_val);
    }

    int
    delay_msg_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      const float* in  = static_cast<const float*>(input_items[0]);
      float*       out = static_cast<float*>(output_items[0]);

      const size_t delay_val = static_cast<size_t>(d_delay_val.load());
      const size_t mask    = d_mask;

      for (int i = 0; i < noutput_items; i++) {
          d_buf_val[d_write_idx] = in[i];

          // Calculate delayed read indices
          const size_t read_idx_val = (d_write_idx - delay_val) & mask;

          // Output reconstructed complex sample
          out[i] = d_buf_val[read_idx_val];

          d_write_idx = (d_write_idx + 1) & mask;
      }

      return noutput_items;
    }

  } /* namespace predistort */
} /* namespace gr */

