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

#ifndef INCLUDED_PREDISTORT_FRACTIONAL_DELAY_MSG_IMPL_H
#define INCLUDED_PREDISTORT_FRACTIONAL_DELAY_MSG_IMPL_H

#include <predistort/fractional_delay_msg.h>
#include <atomic>
#include <vector>
#include <mutex>

namespace gr {
  namespace predistort {

    class fractional_delay_msg_impl : public fractional_delay_msg
    {
     private:
      const float d_max_delay;
      size_t d_buf_size;
      size_t d_mask;
      size_t d_write_idx;

      std::vector<float> d_buf_val;
      std::atomic<float> d_delay_val;

      void handle_msg(pmt::pmt_t msg);
      float interpolate_lagrange4(const std::vector<float>& buf, size_t write_idx, float delay, size_t mask);

     public:
      fractional_delay_msg_impl(float max_delay);
      ~fractional_delay_msg_impl();

      // Where all the action really happens
      int work(
              int noutput_items,
              gr_vector_const_void_star &input_items,
              gr_vector_void_star &output_items
      );
    };

  } // namespace predistort
} // namespace gr

#endif /* INCLUDED_PREDISTORT_FRACTIONAL_DELAY_MSG_IMPL_H */

