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

#ifndef INCLUDED_PREDISTORT_IQ_DELAY_BY_MSG_H
#define INCLUDED_PREDISTORT_IQ_DELAY_BY_MSG_H

#include <predistort/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
  namespace predistort {

    /*!
     * \brief <+description of block+>
     * \ingroup predistort
     *
     */
    class PREDISTORT_API iq_delay_by_msg : virtual public gr::sync_block
    {
     public:
      typedef boost::shared_ptr<iq_delay_by_msg> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of predistort::iq_delay_by_msg.
       *
       * To avoid accidental use of raw pointers, predistort::iq_delay_by_msg's
       * constructor is in a private implementation
       * class. predistort::iq_delay_by_msg::make is the public interface for
       * creating new instances.
       */
      static sptr make(int max_delay = 1024);
    };

  } // namespace predistort
} // namespace gr

#endif /* INCLUDED_PREDISTORT_IQ_DELAY_BY_MSG_H */

