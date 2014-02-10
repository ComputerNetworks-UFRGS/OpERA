/* -*- c++ -*- */

#define OPERA_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "opera_swig_doc.i"

%{
#include "opera/stream_to_vector_overlap.h"
#include "opera/cyclo_fam_calcspectrum_vcf.h"
#include "opera/cyclo_detector.h"
%}


%include "opera/stream_to_vector_overlap.h"
GR_SWIG_BLOCK_MAGIC2(opera, stream_to_vector_overlap);
%include "opera/cyclo_fam_calcspectrum_vcf.h"
GR_SWIG_BLOCK_MAGIC2(opera, cyclo_fam_calcspectrum_vcf);
%include "opera/cyclo_detector.h"
GR_SWIG_BLOCK_MAGIC2(opera, cyclo_detector);
