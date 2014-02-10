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

"""
@package device
"""

import time
from gnuradio import uhd #pylint: disable=F0401

# OpERA imports
from abstractDevice import AbstractDevice

class UHDBase(AbstractDevice):
    """
    Base class to UHDSource and UHDSink.
    """

    def __init__(self, uhd, name="UHDBase"):
        """
        CTOR
        @param uhd UHD Device: uhd.usrp_source or uhd.usrp_sink.
        """
        AbstractDevice.__init__(self, name=name)
        self.__uhd = uhd


    @property
    def uhd(self):
        """
        @return UHD Device
        """
        return self.__uhd

    def input_signature(self):
        return self.__uhd.input_signature()
    def output_signature(self):
        return self.__uhd.output_signature()


    def __getattr__(self, name):
        if hasattr(self.__uhd, name):
            return self.__uhd
        else:
            raise AttributeError


    def _get_center_freq(self):
        """
        Implementation of base class abstract method.
        """
        return self.__uhd.get_center_freq()


    def _set_center_freq(self, center_freq):
        """
        Implementation of base class abstract method.
        """
        self.__uhd.set_center_freq(center_freq)


    def _get_samp_rate(self):
        """
        Implementation of base class abstract method.
        """
        return self.__uhd.get_samp_rate()


    def _set_samp_rate(self, samp_rate):
        """
        Implementation of base class abstract method.
        """
        self.__uhd.set_samp_rate( samp_rate )


    def _get_gain(self):
        """
        Implementation of base class abstract method.
        """
        return self.__uhd.get_gain()

    def _set_gain(self, gain):
        """
        Implementation of base class abstract method.
        """
        self.__uhd.set_gain(gain)


    def _get_bandwidth(self):
        """
        Implementation of base class abstract method.
        """
        self.__uhd.get_samp_rate()

    def _set_bandwidth(self, bw):
        """
        Implementation of base class abstract method.
        """
        # In a USRP, bandwidth is given by the samp rate.
        self.__uhd.set_samp_rate(bw)


## Wrapper for uhd.usrp_source device.
# Always utilizes the 'RX2' antenna.
class UHDSource(UHDBase):

    ## CTOR.
    # @param device_addr USRP identification.
    # @param antenna Device antenna to use.
    # @param stream_args USRP stream arguments.
    def __init__(self, device_addr = '',
            antenna = 'RX2',
            stream_args = uhd.stream_args('fc32'),
            name="UHDSource"): #pylint: disable=E1101

        # Only creates the base class passing a uhd.usrp_source
        UHDBase.__init__(self,
                uhd = uhd.usrp_source(device_addr = device_addr, stream_args = stream_args),
                name = name)

        self.uhd.set_antenna(antenna, 0)


## Wrapper for uhd.usrp_sink device.
# Always utilize the TX/RX antenna.
class UHDSink(UHDBase):

    ## CTOR.
    # @param  device_addr USRP IP address.
    # @param stream_args USRP stream arguments.
    def __init__(self,
            device_addr = '',
            antenna = 'TX/RX',
            stream_args = uhd.stream_args('fc32'),
            name="UHDSink"): #pylint: disable=E1101


        # Only creates the base class passing a uhd.usrp_sink
        UHDBase.__init__(self,
                uhd = uhd.usrp_sink(device_addr = device_addr, stream_args = stream_args),
                name = name)

        self.uhd.set_antenna(antenna, 0)
