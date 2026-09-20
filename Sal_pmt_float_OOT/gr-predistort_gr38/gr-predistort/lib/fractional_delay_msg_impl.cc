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
#include "fractional_delay_msg_impl.h"
#include <pmt/pmt.h>
#include <algorithm>
#include <cmath>

namespace gr {
  namespace predistort {

    fractional_delay_msg::sptr
    fractional_delay_msg::make(float max_delay)
    {
      return gnuradio::get_initial_sptr
        (new fractional_delay_msg_impl(max_delay));
    }

    /*
     * The private constructor
     */
    fractional_delay_msg_impl::fractional_delay_msg_impl(float max_delay)
      : gr::sync_block("fractional_delay_msg",
                     gr::io_signature::make(1, 1, sizeof(float)),
                     gr::io_signature::make(1, 1, sizeof(float))),
      d_max_delay(std::max(4.0f, max_delay)),
      d_write_idx(0),
      d_delay_val(0.0f)
    {
      d_buf_size = 1;
      while (d_buf_size <= static_cast<size_t>(d_max_delay + 8)) {
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
    fractional_delay_msg_impl::~fractional_delay_msg_impl()
    {
    }

    void fractional_delay_msg_impl::handle_msg(pmt::pmt_t msg)
    {
        float read_idx_val = d_delay_val.load();

        if (pmt::is_pair(msg)) 
        {
          if (pmt::eq(pmt::car(msg), pmt::intern("value"))) 
          {
            pmt::pmt_t msg_cdr = pmt::cdr(msg);
            read_idx_val = (pmt::to_double(msg_cdr));
          }
        } 

        read_idx_val = std::max(0.0f, std::min(read_idx_val, d_max_delay));
        d_delay_val.store(read_idx_val);
    }

    inline float fractional_delay_msg_impl::interpolate_lagrange4(
    const std::vector<float>& buf,
    size_t write_idx,
    float delay,
    size_t mask)
    {
        const int int_delay = static_cast<int>(std::floor(delay));
        const float mu = delay - static_cast<float>(int_delay);

        const size_t safe_idx = write_idx + (mask + 1)*2;

        // Retrieve 4 adjacent historical samples
        // y0 is at int_delay, y-1 is at int_delay - 1 (future relative to y0), y1, y2
        const float ym1 = buf[(safe_idx - int_delay + 1) & mask];
        const float y0  = buf[(safe_idx - int_delay)     & mask];
        const float y1  = buf[(safe_idx - int_delay - 1) & mask];
        const float y2  = buf[(safe_idx - int_delay - 2) & mask];

        // Compute Cubic Lagrange basis coefficients
        const float mu2 = mu * mu;
        const float cm1 = -0.16666667f * mu * (mu - 1.0f) * (mu - 2.0f);
        const float c0  =  0.5f * (mu2 - 1.0f) * (mu - 2.0f);
        const float c1  = -0.5f * mu * (mu + 1.0f) * (mu - 2.0f);
        const float c2  =  0.16666667f * mu * (mu2 - 1.0f);

        return (cm1 * ym1) + (c0 * y0) + (c1 * y1) + (c2 * y2);
    }

    int
    fractional_delay_msg_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      const float* in  = static_cast<const float*>(input_items[0]);
      float*       out = static_cast<float*>(output_items[0]);

      const float delay_val = d_delay_val.load();
      const size_t mask   = d_mask;

      for (int i = 0; i < noutput_items; i++) {
          d_buf_val[d_write_idx] = in[i];

          out[i] = interpolate_lagrange4(d_buf_val, d_write_idx, delay_val, mask);
          d_write_idx = (d_write_idx + 1) & mask;
      }

      return noutput_items;
    }

  } /* namespace predistort */
} /* namespace gr */

