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

#ifndef INCLUDED_PREDISTORT_ASYNC_SIGNAL_MUX_IMPL_H
#define INCLUDED_PREDISTORT_ASYNC_SIGNAL_MUX_IMPL_H

#include <predistort/async_signal_mux.h>
#include <mutex>

namespace gr {
  namespace predistort {

    class async_signal_mux_impl : public async_signal_mux
    {
     private:
      size_t d_itemsize;
      int d_num_inputs;
      int d_current_stream;
      
      std::mutex d_mutex;

      // Async message handler callback
      void handle_msg(pmt::pmt_t msg);
      
     public:
      async_signal_mux_impl(size_t itemsize, int num_inputs);
      ~async_signal_mux_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);

    };

  } // namespace predistort
} // namespace gr

#endif /* INCLUDED_PREDISTORT_ASYNC_SIGNAL_MUX_IMPL_H */

