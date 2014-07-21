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

from gnuradio import gr  #pylint: disable=F0401

from abstractDevice import AbstractDevice
from uhdDevice import *
from uhdArch import *

import time


#::TODO:: documentacao das funcoes das classes

class APath(object):
    """
    Class to handle a single path connection/disconnection
    """

    PENDING = 0
    CONNECTED = 1
    DISABLED = 2

    def __init__(self, source, arch, sink):
        """
        CTOR
        @param source 
        @param arch
        @param sink
        """

        if isinstance(source, UHDBase):
            source = source.uhd
        if isinstance(sink, UHDBase):
            sink = sink.uhd

        if source and not isinstance(source, tuple):
            source = (source, 0)
        if arch and not isinstance(arch, tuple):
            arch = (arch, 0)
        if sink and not isinstance(sink, tuple):
            sink = (sink, 0)


        self._source = source
        self._arch = arch
        self._sink = sink

        self._state = APath.PENDING

    def __hasattr__(self, name):
        """
        Function override.
        """
        if self._source and hasattr(self._source[0], name):
            return hasattr(self._source[0], name)
        elif self._arch and hasattr(self._arch[0], name):
            return hasattr(self._arch[0], name)
        elif self._sink and hasattr(self._sink[0], name):
            return hasattr(self._sink[0], name)

        raise AttributeError

    def __getattr__(self, name):
        """
        Function override.
        """
        if self._source and hasattr(self._source[0], name):
            return getattr(self._source[0], name)
        elif  self._arch and hasattr(self._arch[0], name):
            return getattr(self._arch[0], name)
        elif self._sink and hasattr(self._sink[0], name):
            return getattr(self._sink[0], name)

        raise AttributeError("%s not found in wrapper APath" % name)


    def connect(self, tb):
        """

        @param tb An OpERAFlow instance.
        """
        if self.is_connected():
            return

        if self._source:
            isinstance(self._source[0], UHDBaseArch) and self._source[0].pre_connect(tb)
        if self._sink:
            isinstance(self._sink[0], UHDBaseArch) and self._sink[0].pre_connect(tb)
        if self._arch:
            isinstance(self._arch[0], UHDBaseArch) and self._arch[0].pre_connect(tb)

        if self._arch:
            self._source and tb.connect(self._source, self._arch)
            self._sink   and tb.connect(self._arch, self._sink)
        else:
            self._source and self._sink and tb.connect(self._source, self._sink)

        self._state = APath.CONNECTED


    def disconnect(self, tb):
        """
        @param tb OpERAFlow instance.
        """

        if not self.is_connected():
            return

        if self._arch:
            self._source and tb.disconnect(self._source, self._arch)
            self._sink and tb.disconnect(self._arch, self._sink)
        else:
            self._source and self._sink and tb.disconnect(self._source, self._sink)

        self._state = APath.DISABLED


    def get_state(self):
        """
        """
        return self._state

    def is_connected(self):
        """
        """
        return self._state == APath.CONNECTED

    def is_disabled(self):
        """
        """
        return self._state == APath.DISABLED

    def is_pending(self):
        """
        """
        return self._state == APath.PENDING


class RadioDevice(AbstractDevice):
    """
    """

    def __init__(self, name="RadioDevice"):
        """
        CTOR
        @param name
        """
        AbstractDevice.__init__(self, name=name)

        # Dictionary of all UHD devices
        # Dictionary of AbstractArch of this radio device
        self._dict_of_uhds = {}
        self._dict_of_archs = {}

        self._tb = None
        # We need this flag because lock/unlock in OpERAFlow is not working
        # To avoid  performing the "RadioDevice::connect" 1+ times, we control it with this flag.
        self._pending_done = False


    def add_arch(self, source, sink, arch, name, uhd_device):
        """
        Add a reference to a arch in which this radio_device.is a source/sink.
        @param source Arch source.
        @param sink Architecture sink.
        @param arch AbstractArch device implementation.
        @param name Name Name of the architecture.
        @param uhd_device UHD device. Should be source or sink.
        """

        # The arch has a reference to the radio.
        if hasattr(arch, 'set_radio_device'):
            arch.set_radio_device(uhd_device)

        self._dict_of_archs[name] = APath(source=source, arch=arch, sink=sink)
        self._dict_of_uhds[name] = uhd_device

        # makes the name be accessible by doing radio.$name
        setattr(self, name, self._dict_of_archs[name])


    def disable_arch(self, name):
        """
        @param name
        """
        # Arch is not enabled
        if not name in self._dict_of_archs:
            raise AttributeError

        # ::TRICKY::
        # lock()/unlock() are not working  with python sync blocks.
        # So, we use stop/wait/start
        # For more info check the link:
        # http://gnuradio.org/redmine/issues/594
        self._tb.stop()
        self._tb.wait()

        self._dict_of_archs[name].disconnect(self._tb)

        self._tb.start()

    def enable_arch(self, name):
        """
        @param name
        """
        # Arch is not enabled
        if not name in self._dict_of_archs:
            raise AttributeError

        self._tb.stop()
        self._tb.wait()

        self._dict_of_archs[name].connect(self._tb)

        self._tb.start()


    def connect(self):
        """
        """
        if self._pending_done:
            return

        self._pending_done = True
        for x in self._dict_of_archs.itervalues():
            x.connect(self._tb)


    def set_top_block(self, tb):
        """
        @param tb Set the top block.
        """
        self._tb = tb


    def __getattr__(self, name):
        """
        Search for a parameter/function in all archs of this Radio.
        So, a programer that doed radio.function, activates this __getattr__
        function, which searches for 'function' in all architectures.

        @param name Name of parameter/function.
        """
        if name == "_dict_of_archs":
            return object.getattr(self, "_dict_of_archs")  #pylint: disable=E1101
        else:
            # search for method in the architectures
            for key in self._dict_of_archs:
                if hasattr(self._dict_of_archs[key], name):
                    return getattr(self._dict_of_archs[key], name)

        raise AttributeError("%r object has no attribute %s" % (self.__class__, name))


    ### Implementations required for the AbstractDevice

    def __getter(self, str_callback):
        """
        A gereric getter for this class.
        @param str_callback String with the name of the real getter function.
        """
        arr = []
        for uhd in self._dict_of_uhds.values():
            uhd and arr.append(getattr(uhd, str_callback)())
        return arr

    def _get_center_freq(self):
        """
        """
        return self.__getter('get_center_freq')


    def _set_center_freq(self, center_freq):
        """
        @param center_freq
        """
        for uhd in self._dict_of_uhds.values():
            uhd and uhd.set_center_freq(center_freq)

        return center_freq

    def _get_samp_rate(self):
        """
        Device sample rate getter.
        """
        return self.__getter('get_samp_rate')


    def _set_samp_rate(self, samp_rate):
        """
        @param samp_rate
        """
        for uhd in self._dict_of_uhds.values():
            uhd and uhd.set_samp_rate(samp_rate)

        return samp_rate


    def _get_gain(self):
        """
        Device gain getter.
        """
        return self.__getter('get_gain')


    def _set_gain(self, gain):
        """
        @param gain
        """
        for uhd in self._dict_of_uhds.values():
            uhd and uhd.set_gain(gain)

        return gain

    def _get_bandwidth(self):
        """
        Get the device's bandwidth.
        @return
        """
        return self.__getter('get_bandwidth')

    def _set_bandwidth(self, bw):
        """
        @param bw
        """
        for uhd in self._dict_of_uhds.values():
            uhd and uhd.set_bandwidth(bw)

        return bw
