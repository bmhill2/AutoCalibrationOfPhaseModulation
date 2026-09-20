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

#ifndef INCLUDED_PREDISTORT_IQ_DELAY_BY_MSG_IMPL_H
#define INCLUDED_PREDISTORT_IQ_DELAY_BY_MSG_IMPL_H

#include <predistort/iq_delay_by_msg.h>
#include <atomic>
#include <vector>
#include <mutex>

namespace gr {
  namespace predistort {

    class iq_delay_by_msg_impl : public iq_delay_by_msg
    {
     private:
      const int d_max_delay;
      size_t d_buf_size;
      size_t d_mask;
      size_t d_write_idx;

      std::vector<float> d_buf_i;
      std::vector<float> d_buf_q;

      std::atomic<int> d_delay_i;
      std::atomic<int> d_delay_q;

      void handle_msg(pmt::pmt_t msg);

     public:
      iq_delay_by_msg_impl(int max_delay);
      ~iq_delay_by_msg_impl();

      // Where all the action really happens
      int work(
              int noutput_items,
              gr_vector_const_void_star &input_items,
              gr_vector_void_star &output_items
      );
    };

  } // namespace predistort
} // namespace gr

#endif /* INCLUDED_PREDISTORT_IQ_DELAY_BY_MSG_IMPL_H */

