/* -*- c++ -*- */
/* 
 * Copyright 2014 <+YOU OR YOUR COMPANY+>.
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


#ifndef INCLUDED_OPERA_CYCLO_DETECTOR_H
#define INCLUDED_OPERA_CYCLO_DETECTOR_H

#include <opera/api.h>
#include <gnuradio/hier_block2.h>

namespace gr {
  namespace opera {

    /*!
     * \brief <+description of block+>
     * \ingroup opera
     *
     */
    class OPERA_API cyclo_detector : virtual public gr::hier_block2
    {


     public:
      typedef boost::shared_ptr<cyclo_detector> sptr;
      gr::opera::cyclo_fam_calcspectrum_vcf::sptr d_calcspectrum;

      /*!
       * \brief Return a shared_ptr to a new instance of opera::cyclo_detector.
       *
       * To avoid accidental use of raw pointers, opera::cyclo_detector's
       * constructor is in a private implementation
       * class. opera::cyclo_detector::make is the public interface for
       * creating new instances.
       */
      static sptr make(int Np, int P, int L);

	  const std::vector<std::vector<float> > &get_estimate() { return d_calcspectrum->get_estimate(); };
    };

  } // namespace opera
} // namespace gr

#endif /* INCLUDED_OPERA_CYCLO_DETECTOR_H */

