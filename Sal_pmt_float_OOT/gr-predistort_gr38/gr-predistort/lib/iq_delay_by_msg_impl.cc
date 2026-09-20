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
#include "iq_delay_by_msg_impl.h"

namespace gr {
  namespace predistort {

    iq_delay_by_msg::sptr
    iq_delay_by_msg::make(int max_delay)
    {
      return gnuradio::get_initial_sptr
        (new iq_delay_by_msg_impl(max_delay));
    }


    /*
     * The private constructor
     */
    iq_delay_by_msg_impl::iq_delay_by_msg_impl(int max_delay)
      : gr::sync_block("iq_delay_by_msg",
                     gr::io_signature::make(1, 1, sizeof(gr_complex)),
                     gr::io_signature::make(1, 1, sizeof(gr_complex))),
      d_max_delay(std::max(1, max_delay)),
      d_write_idx(0),
      d_delay_i(0),
      d_delay_q(0)
    {
      // Compute next power-of-two buffer size >= (max_delay + 1)
      d_buf_size = 1;
      while (d_buf_size <= static_cast<size_t>(d_max_delay)) {
          d_buf_size <<= 1;
      }
      d_mask = d_buf_size - 1;

      d_buf_i.assign(d_buf_size, 0.0f);
      d_buf_q.assign(d_buf_size, 0.0f);

      message_port_register_in(pmt::intern("ctrl_in"));

      set_msg_handler(pmt::mp("ctrl_in"),
                  [this](pmt::pmt_t msg) { this->handle_msg(msg); });

    }

    /*
     * Our virtual destructor.
     */
    iq_delay_by_msg_impl::~iq_delay_by_msg_impl()
    {
    }

    void iq_delay_by_msg_impl::handle_msg(pmt::pmt_t msg)
    {
        int new_delay_i = d_delay_i.load();
        int new_delay_q = d_delay_q.load();

        if (pmt::is_pair(msg)) 
        {
          if (pmt::eq(pmt::car(msg), pmt::intern("value"))) 
          {
            pmt::pmt_t msg_cdr = pmt::cdr(msg);
            if(pmt::is_s32vector(msg_cdr))
            {
              new_delay_i = (pmt::s32vector_ref(msg_cdr, 0));
              new_delay_q = (pmt::s32vector_ref(msg_cdr, 1));
            }
          }
        } 

        // Clamp values to [0, d_max_delay]
        new_delay_i = std::max(0, std::min(new_delay_i, d_max_delay));
        new_delay_q = std::max(0, std::min(new_delay_q, d_max_delay));

        d_delay_i.store(new_delay_i);
        d_delay_q.store(new_delay_q);
    }

    int
    iq_delay_by_msg_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      const gr_complex* in  = static_cast<const gr_complex*>(input_items[0]);
      gr_complex*       out = static_cast<gr_complex*>(output_items[0]);

      const size_t delay_i = static_cast<size_t>(d_delay_i.load());
      const size_t delay_q = static_cast<size_t>(d_delay_q.load());
      const size_t mask    = d_mask;

      for (int i = 0; i < noutput_items; i++) {
          // Store incoming components in ring buffers
          d_buf_i[d_write_idx] = in[i].real();
          d_buf_q[d_write_idx] = in[i].imag();

          // Calculate delayed read indices
          const size_t read_idx_i = (d_write_idx - delay_i) & mask;
          const size_t read_idx_q = (d_write_idx - delay_q) & mask;

          // Output reconstructed complex sample
          out[i] = gr_complex(d_buf_i[read_idx_i], d_buf_q[read_idx_q]);

          d_write_idx = (d_write_idx + 1) & mask;
      }

      return noutput_items;
    }

  } /* namespace predistort */
} /* namespace gr */

