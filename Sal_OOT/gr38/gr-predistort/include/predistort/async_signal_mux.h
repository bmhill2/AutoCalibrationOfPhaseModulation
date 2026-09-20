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

#ifndef INCLUDED_PREDISTORT_ASYNC_SIGNAL_MUX_H
#define INCLUDED_PREDISTORT_ASYNC_SIGNAL_MUX_H

#include <predistort/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace predistort {

    /*!
     * \brief <+description of block+>
     * \ingroup predistort
     *
     */
    class PREDISTORT_API async_signal_mux : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<async_signal_mux> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of predistort::async_signal_mux.
       *
       * To avoid accidental use of raw pointers, predistort::async_signal_mux's
       * constructor is in a private implementation
       * class. predistort::async_signal_mux::make is the public interface for
       * creating new instances.
       */
      static sptr make(size_t itemsize, int num_inputs);
    };

  } // namespace predistort
} // namespace gr

#endif /* INCLUDED_PREDISTORT_ASYNC_SIGNAL_MUX_H */

