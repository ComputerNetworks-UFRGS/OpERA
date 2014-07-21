"""
Copyright 2013 OpERA

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
"""

import sys
import os
import time
path = os.path.abspath(os.path.join(os.path.dirname(__file__),"../"))
sys.path.insert(0, path)


from gnuradio import gr      #pylint: disable=F0401
from gnuradio import blocks  #pylint: disable=F0401
from gnuradio import filter  #pylint: disable=F0401
from gnuradio import fft     #pylint: disable=F0401

import numpy as np
import math

from device import UHDSSArch  #pylint: disable=F0401

#from OpERA  import cyclo_detector

#class specest_cyclo_fam_calcspectrum_impl():
#
#    def __init__(self, Np, P, L):
#        self.d_Np = Np
#        self.d_P  = P
#        self.d_L  = L
#        self.d_N  = P * L
#        self.d_result = np.zeros((2*self.d_N, 2*self.d_Np-1), dtype=np.float32)
#        self.d_complex_demodulates = np.zeros((P, Np), dtype=complex)  #pylint: disable=E1101
#
#        window = filter.firdes.window(filter.firdes.WIN_HAMMING, self.d_Np, 0)
#
#        h = 0
#        for i in window:
#            h += (i * i)
#        self.d_scale = h * self.d_P
#
#        self.d_fft_out = np.zeros(P, dtype = complex) #pylint: disable=E1101
#        self.d_fft_in  = np.zeros(P)                  #pylint: disable=E1101
#
#
#    def get_value(self, row, column):
#        print "---- d_result"
#        print "row: ", row
#        print "col: ", column
#        print self.d_result[row][column]
#        return self.d_result[row][column]
#
#
#    def calc(self, _in):
#        """
#        """
#        p = 0
#        i = 0
#
#
#        for m in range(self.d_P * self.d_Np):
#            _real =  _in[m].real * math.cos(2*math.pi*i*(p*self.d_L)/self.d_Np) + _in[m].imag * math.sin(2*math.pi*i*(p*self.d_L)/self.d_Np)
#            _imag =  _in[m].imag * math.cos(2*math.pi*i*(p*self.d_L)/self.d_Np) - _in[m].real * math.sin(2*math.pi*i*(p*self.d_L)/self.d_Np)
#
#            self.d_complex_demodulates[p][i] = _real + 1j * _imag
#
#            i += 1
#
#            if ((m+1)%self.d_Np) == 0:
#                p += 1
#                i = 0
#
#        half = self.d_Np/2
#
#
#        tmp = np.fft.fftshift(self.d_complex_demodulates) #pylint: disable=E1101
#        self.d_complex_demodulates = tmp
#
#
#        for f_k in range(1, self.d_Np):
#            for f_l in range(1, self.d_Np):
#                self.fft(f_k, f_l)
#
#    def fft(self, f_k, f_l):
#
#        for p in range(self.d_P):
#            self.d_fft_in[p] = self.d_complex_demodulates[p][f_k-1]*np.conjugate(self.d_complex_demodulates[p]*f_l-1)/self.d_scale #pylint: disable=E1101
#
#        d_fft_p = fftw3.Plan(
#                self.d_fft_in,
#                self.d_fft_out,
#                direction = 'forward',
#                flags = ['estimate'])
#
#        d_fft_p()
#
#        column = f_k+f_l-2
#        row    = math.floor((f_k-f_l*self.d_Np)*(self.d_N/self.d_Np))
#
#
#        for i in range(self.d_N/self.d_P):
#            self.d_result[row+i][column] = np.absolute(self.d_fft_out[i]) #pylint: disable=E1101
#
#        for i in range(1, self.d_N/self.d_Np):
#            self.d_result[row-i][column] = np.absolute(self.d_fft_out[self.d_P-i]) #pylint: disable=E1101
#
#
#
#class stream_to_vector_overlap(gr.decim_block):
#    """
#    """
#
#    def __init__(self, nitems_per_block, overlap):
#        """
#        CTOR.
#        @param nitems_per_block
#        @param overlap
#        """
#
#        gr.decim_block.__init__(self,
#                name = "stream_to_vector_overlap",
#                in_sig  = [np.complex64],
#                out_sig = [np.dtype((np.complex64, nitems_per_block))], #pylint: disable=E1101
#                decim   = nitems_per_block - overlap
#            )
#
#        self.d_bytes_overlap = gr.sizeof_gr_complex * overlap
#
#        self.set_history(overlap + 1) #pylint: disable=E1101
#
#
#    def work(self, input_items, output_items):
#        """
#        @param input_items
#        @param output_items
#        """
#
#        block_size = self.to_basic_block().output_signature().sizeof_stream_item(0) #pylint: disable=E1101
#
#        _in = input_items[0][0]
#        _out = output_items[0][0]
#
#        _tmp = _in[:block_size]
#        for i in range( len(_out) ):
#            _out[i*block_size:] = _tmp[:block_size]
#
#            _tmp = _in[i* (block_size-self.d_bytes_overlap):]
#
#        return len(input_items)
#
#
#class cyclo_fam_calspectrum(gr.interp_block):
#    """
#    """
#
#    def __init__(self, Np, P, L):
#        """
#        """
#
#        gr.interp_block.__init__(self, name = "cyclo_fam_calcspectrum",
#                in_sig  = [np.dtype((np.complex64, Np))],      #pylint: disable=E1101
#                out_sig = [np.dtype((np.float32, 2*Np))], #pylint: disable=E1101
#                interp = 2*L
#            )
#
#        self.d_Np = Np
#        self.d_P  = P
#        self.d_N  = P * L
#        self.d_L  = L
#        self.d_p_index = 0
#
#        self.set_history(P) #pylint: disable=E1101
#
#        self.d_calcspectrum = specest_cyclo_fam_calcspectrum_impl(Np, P, L)
#
#
#    def work(self, input_items, output_items):
#        """
#        """
#        print "XXXXXXXXXXXXXXXX"
#        _in  = input_items[0][0]
#        _out = output_items[0][0]
#
#        #d_K = self.interpolation() #pylint: disable=E1101
#        d_K = self.d_L * 2
#
#        ninput_items = len(_out)/d_K
#
#        for w in range(ninput_items):
#            for p in range(d_K):
#                for i_column in range(2*self.d_Np-1):
#                    _out[w*2*self.d_Np*d_K+p*2*self.d_Np+i_column] = self.d_calcspectrum.get_value(p+self.d_p_index*d_K, i_column) #pylint: disable=E1101
#                _out[w*2*self.d_Np*d_K+p*2*self.d_Np+2*self.d_Np-1] = self.d_calcspectrum.get_value(p+self.d_p_index, 0)       #pylint: disable=E1101
#
#
#            self.d_p_index +=1
#            if self.d_p_index == (2*self.d_N/d_K):
#                self.d_calcspectrum.calc(_in[w * self.d_Np]) #pylint: disable=E1101
#                self.d_p_index = 0
#
#        return len(input_items)
#
#
#class CyclostationaryDetector(gr.hier_block2):
#
#    def __init__(self, Np, P, L):
#        """
#        """
#        gr.hier_block2.__init__(self, name = "CyclostationaryDetector",
#                input_signature  = gr.io_signature(1, 1, gr.sizeof_gr_complex),
#                output_signature = gr.io_signature(1, 1, gr.sizeof_float * Np * 2)
#          )
#
#        d_stream_to_vector = stream_to_vector_overlap(gr.sizeof_gr_complex, Np, Np-L)
#        d_Np_fft           = fft.fft_vcc(Np, True, (fft.window.hamming(Np)) , True, 1)
#        d_calcspectrum     = cyclo_fam_calcspectrum_vcf(Np, P, L)
#
#        self.connect(self, d_stream_to_vector, d_Np_fft, d_calcspectrum, self) #pylint: disable=E1101

#::TODO:: descricao de classes, metodos e seus parametros
class CycloBuffer(gr.sync_block):
    """

    """

    def __init__(self, Np, P, L):
        """
        CTOR
        @param Np
        @param P
        @param L
        """

        gr.sync_block.__init__(self,
                               name="CycloDetector",
                               in_sig=[np.dtype((np.complex64, Np))],  #pylint: disable=E1101
                               out_sig=[np.dtype((np.complex64,  Np*P))]
                               )

	self._Np = Np
	self._P = P
	self._L = L

	self._dec = 0
	self._p = 0
        self._sum = 0
	self._to_algo = [np.array([np.complex64()] * Np) ] * P 


    def work(self, input_items, output_items):
        """
        @param input_items
        @param output_items
        """

	_out_idx = 0

        for idx in range(len(input_items[0])):
            self._to_algo[self._p][:] = input_items[0][idx]

	    self._p += 1
	    if (self._p == self._P): 
                self._p = 0

	    xxx = []
	    for x in self._to_algo:
	    	xxx.extend(x)
	    output_items[0][idx][:] = np.array(xxx)

        return len(output_items[0])

    def output(self):
        return (self._dec, self._sum)


class CycloDetector(gr.sync_block):
    """

    """

    def __init__(self, Np, P, L, algorithm):
        """
        CTOR
        @param Np
        @param P
        @param L
        """

        gr.sync_block.__init__(self,
                               name="CycloDetector",
                               in_sig=[np.dtype((np.complex64, Np * P))],  #pylint: disable=E1101
                               out_sig=None
                               )

        self._algorithm = algorithm

	self._Np = Np
	self._P = P
	self._p = 0
	self._L = L

	self._dec = 0
        self._sum = 0
	self._to_algo = []


    def work(self, input_items, output_items):
        """
        @param input_items
        @param output_items
        """

        for idx in range(len(input_items[0])):
		self._dec, self._sum = self._algorithm.decision(input_items[0][idx])
		
	return len(input_items[0])

    def output(self):
        return (self._dec, self._sum)


class CycloSSArch(UHDSSArch):
    """

    """
    def __init__(self, Np, P, L):
        """
        CTOR
        @param Np
        @param P
        @param L
        """

        self.Np = Np
        self.P  = P
        self.L  = L

        UHDSSArch.__init__(self,
                           name="CycloSSArch",
                           input_signature=gr.io_signature(1, 1, gr.sizeof_gr_complex),
                           output_signature=gr.io_signature(1, 1, gr.sizeof_gr_complex * Np * P)
                           )

    #::TODO:: nao usa os parametros input e output sig
    def _build(self, input_signature, output_signature):
        """
        @param input_signature The input signature.
        @param output_signature The output signature.
        """
        from gnuradio import fft

        self._stream = blocks.stream_to_vector(gr.sizeof_gr_complex, self.Np)
        self._fft = fft.fft_vcc(self.Np, True, [])
        self._buffer = CycloBuffer(self.Np, self.P, self.L)

	self._vs1 = blocks.vector_to_stream(gr.sizeof_gr_complex, self.Np)
	self._vs2 = blocks.stream_to_vector(gr.sizeof_gr_complex, self.Np * self.P)


        #self._add_connections([self, self._stream, self._fft, self._buffer, self])
        self._add_connections([self, self._stream, self._fft, self._vs1, self._vs2, self])

        return None


    def _get_sensing_data(self, channel, sensing_duration):
        """
        @param channel
        @param sensing_duration
        """
	raise NotImplemented
        pass


if __name__ == '__main__':

    Np = 1024
    P = 1
    L = 1024

    from grc_gnuradio import blks2 as grc_blks2
    from gr_blocks.utils import UHDSourceDummy
    from gnuradio import digital
    from channels import AWGNChannel
    from opera import cyclo_detector
    from utils import Logger

    Logger._ch_status = 1

    modulator = grc_blks2.packet_mod_b(digital.ofdm_mod(
			    options=grc_blks2.options(
				    modulation="bpsk",
				    fft_length=512,
				    occupied_tones=200,
				    cp_length=128,
				    pad_for_usrp=True,
				    log=None,
				    verbose=None,
				    ),
			    ),
        	payload_length=0,
        )

    src = UHDSourceDummy(modulator=modulator)

    the_source = AWGNChannel(component=src)

    from sensing import CycloSSArch
    from sensing import CycloDecision

    cyclo_fam = CycloSSArch(Np, P, L)
    algorithm = CycloDecision(1024, 2, 512, 1)
    cyclo_sink = CycloDetector(Np, P, L, algorithm)

    the_source._component.set_active_freqs([1, ])
    the_source._component.set_center_freq(0)

    tb = gr.top_block()
    src.pre_connect(tb)
    cyclo_fam.pre_connect(tb)
    the_source.pre_connect(tb)

    tb.connect(the_source, cyclo_fam, cyclo_sink)
    tb.start()

    _cyclo = {'noise': {}, 'signal': {}, 'noise_max': {}, 'signal_min': {}}
    import numpy as np

    the_source._component.set_center_freq(1)
    for ebn0 in range(4, 5):
        the_source.set_ebn0(ebn0)
        _arr = []
        for i in range(500):
            time.sleep(0.05)

            _sum = cyclo_sink._sum
            _arr.append(_sum)

        _arr.sort()
        _cyclo['noise']["%2.0f" % ebn0] = _arr[int(len(_arr) * 0.9)]
        _cyclo['noise_max']["%2.0f" % ebn0] = max(_arr)

    the_source._component.set_center_freq(1)
    for ebn0 in range(-10, 5):
        the_source.set_ebn0(ebn0)
        _arr = []
        for i in range(500):
            time.sleep(0.05)

            _sum = cyclo_sink._sum
            _arr.append(_sum)

        _arr.sort()
        _cyclo['signal']["%2.0f" % ebn0] = _arr[int(len(_arr) * 0.1)]
        _cyclo['signal_min']["%2.0f" % ebn0] = min(_arr)

    import yaml

    with open('cyclo.txt', 'w+') as fd:
        fd.write(yaml.dump(_cyclo))

    tb.stop()
