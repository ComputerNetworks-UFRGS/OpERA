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

## @package device
# Module with all classes related to device specific

from abc import ABCMeta, abstractmethod
from OpERABase import OpERABase

from utils import Channel

class AbstractDevice(OpERABase):
    """
    Abstract device
    Interface for a specific hardware
    """
    __metaclass__ = ABCMeta

    def __init__(self, name="AbstractDevice"):
        """
        CTOR.
        @param name Instance name.
        """
        OpERABase.__init__(self, name=name)

        self._channel = None


    def set_channel(self, channel):
        """
        Set channel.
        @param channel Channel instance.
        @return True
        """
        self._channel = channel
        self.set_bandwidth(channel.get_bandwidth())
        self.set_center_freq(channel.get_freq())

        return True


    def get_channel(self):
        """
        Return the current channel
        @return Current channel.
        """
        return self._channel


    def get_center_freq(self):
        """
        Getter for center_freq property.
        @return Device center frequency.
        """
        return self._get_center_freq()


    @abstractmethod
    def _get_center_freq(self):
        """
        Device specific getter for center_freq.
        Must be implemented on derived classes.
        """
        pass


    def set_center_freq(self, the_channel):
        """
        Setter for center_freq property.
        @param the_channel Channel object.
        """
        if type(the_channel) == Channel:
            self._set_center_freq(the_channel.get_freq())
        else:
            self._set_center_freq(the_channel)

        return self.get_center_freq()


    @abstractmethod
    def _set_center_freq(self, freq):
        """
        Device specific setter for center_freq.
        Must be implemented on derived classes.
        """
        pass


    def get_samp_rate(self):
        """
        Getter for samp_rate property
        @return Device sample rate
        """
        return self._get_samp_rate()


    @abstractmethod
    def _get_samp_rate(self):
        """
        Device specific getter  for sample rate.
        Must be implemented on derived classes.
        @return Sample rate
        """
        pass


    def set_samp_rate(self, samp_rate):
        """
        Setter for samp_rate property.
        @param samp_rate The sample rate (integer).
        """
        self._set_samp_rate( samp_rate )
        return self.get_samp_rate()


    @abstractmethod
    def _set_samp_rate(self, sample_rate):
        """
        Device specific setter  for sample rate.
        Must be implemented on derived classes.
        @param samp_rate Sample rate.
        """
        pass


    def get_gain(self):
        """
        Getter for gain property.
        @return Device gain.
        """
        return self._get_gain()


    @abstractmethod
    def _get_gain(self):
        """
        Device specific getter for gain.
        Must be implemented on derived classes.
        @return Gain.
        """
        pass


    def set_gain(self, gain):
        """
        Setter for gain property.
        @param gain The gain (float).
        """
        self._set_gain( gain )
        return self.get_gain()


    @abstractmethod
    def _set_gain(self, gain):
        """
        Device specific gain for sample rate.
        Must be implemented on derived classes.
        @param gain The gain.
        """
        pass


    def get_bandwidth(self):
        """
        Get current device bandwidth
        @return Device bandwidth
        """
        return self._get_bandwidth()


    @abstractmethod
    def _get_bandwidth(self):
        """
        Derived class implementation.
        """
        pass


    def set_bandwidth(self, bw):
        """
        Set current device bandwidth
        @param bw Bandwidth
        """
        return self._set_bandwidth(bw)


    @abstractmethod
    def _set_bandwidth(self, value):
        """
        Derived class implementation.
        """
        pass
