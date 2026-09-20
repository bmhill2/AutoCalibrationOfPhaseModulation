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
#include "async_signal_mux_impl.h"

namespace gr {
  namespace predistort {

    async_signal_mux::sptr
    async_signal_mux::make(size_t itemsize, int num_inputs)
    {
      return gnuradio::get_initial_sptr
        (new async_signal_mux_impl(itemsize, num_inputs));
    }


    /*
     * The private constructor
     */
    async_signal_mux_impl::async_signal_mux_impl(size_t itemsize, int num_inputs)
      : gr::block("async_signal_mux",
              gr::io_signature::make(num_inputs, num_inputs, itemsize),
              gr::io_signature::make(1, 1, itemsize)),
        d_itemsize(itemsize),
        d_num_inputs(num_inputs),
        d_current_stream(0)
    {

        message_port_register_in(pmt::intern("ctrl_in"));

        set_msg_handler(pmt::mp("ctrl_in"),
                    [this](pmt::pmt_t msg) { this->handle_msg(msg); });
    }

    /*
     * Our virtual destructor.
     */
    async_signal_mux_impl::~async_signal_mux_impl()
    {
    }

    
    void async_signal_mux_impl::handle_msg(pmt::pmt_t msg)
    {
        // Lock mutex to prevent race conditions with general_work
        std::lock_guard<std::mutex> lock(d_mutex);

        // We expect a PMT pair like: (intern("stream") . 1)
        if (pmt::is_pair(msg)) {
            if (pmt::eq(pmt::car(msg), pmt::intern("stream"))) {
                int next_stream = pmt::to_long(pmt::cdr(msg));
                
                // Validate that the requested stream exists
                if (next_stream >= 0 && next_stream < d_num_inputs) {
                    d_current_stream = next_stream;
                }
            }
        } 
        // We also support PMT dictionaries like: {"stream": 1}
        else if (pmt::is_dict(msg)) {
            if (pmt::dict_has_key(msg, pmt::intern("stream"))) {
                int next_stream = pmt::to_long(pmt::dict_ref(msg, pmt::intern("stream"), pmt::from_long(0)));
                
                if (next_stream >= 0 && next_stream < d_num_inputs) {
                    d_current_stream = next_stream;
                }
            }
        }
    }

    void
    async_signal_mux_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        for(unsigned i = 0; i < ninput_items_required.size(); i++) {
            ninput_items_required[i] = noutput_items;
        }
    }

    int
    async_signal_mux_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
        std::lock_guard<std::mutex> lock(d_mutex);

        // Find the minimum available items across ALL input buffers
        int nitems = noutput_items;
        for(size_t i = 0; i < input_items.size(); i++) {
            if (ninput_items[i] < nitems) {
                nitems = ninput_items[i];
            }
        }

        if (nitems == 0) return 0;

        // Pointer arithmetic for copying memory
        const char *in = (const char *) input_items[d_current_stream];
        char *out = (char *) output_items[0];

        // Copy ONLY the selected stream to the output
        memcpy(out, in, nitems * d_itemsize);

        // Consume items from ALL inputs to keep data flowing and avoid stalling
        for(size_t i = 0; i < input_items.size(); i++) {
            consume(i, nitems);
        }

        return nitems;
    }

  } /* namespace predistort */
} /* namespace gr */

