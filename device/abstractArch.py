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

# GNU Radio imports
from abc import ABCMeta
from abc import abstractmethod

# OpERA imports
from OpERABase import OpERABase  #pylint: disable=F0401
from utils     import PktBitRate #pylint: disable=F0401

class AbstractSSArch(OpERABase):
    """
    Base class of all sensing architectures.
    """

    __metaclass__ = ABCMeta

    def __init__(self, name="AbstractSSArch"):
        """
        CTOR
        """
        OpERABase.__init__(self, name=name)

    @abstractmethod
    def sense_channel(self, channel, sensing_duration):
        """
        Must be implemented on derived classes.
        @param the_list List of Channel/frequencies(float) to sense.
        @return Sense result: 0/1.
        """
        pass


    def sense_channel_list(self, channel_list, sensing_duration):
        """
        Sense a list of channels.
        @param channel_list     List of channels to sense.
        @param sensing_duration Sensing duration in each channel.
        @return Sensing information of all channels.
        """
        data = []

        for channel in channel_list:
            res = self.sense_channel(channel, sensing_duration)
            data.append(res)

        return data



class AbstractPktArch(object):
    """
    Abstract Class for any packet architectures
    """
    __metaclass__ = ABCMeta

    def __init__(self, name):
        self._counter = PktBitRate(name + "_bit_rate")


    @property
    def counter(self):
        return self._counter


    @property
    @abstractmethod
    def bits_per_symbol(self):
        pass


    @property
    @abstractmethod
    def symbols(self):
        pass



class AbstractTxPktArch(OpERABase, AbstractPktArch):
    """
    Base class of all packet transmission architectures.
    """
    __metaclass__ = ABCMeta


    def __init__(self, name="AbstractTxPktArch"):
        """
        CTOR.
        @param name
        """
        AbstractPktArch.__init__(self, name)
        OpERABase.__init__(self, name)


    def send_pkt(self, payload, eof = False):
        """
        Send Packet.
        @param payload
        """
        self._counter.count(payload)
        self._send_pkt(payload, eof)


    @abstractmethod
    def _send_pkt(self, payload, eof = False):
        """
        Send payload.
        @param payload Pkt Payload.
        @param eof End Of File.
        """
        pass


class AbstractRxPktArch(OpERABase, AbstractPktArch):
    """
    Base class of all packet reception architectures.
    """
    __metaclass__ = ABCMeta

    def __init__(self, name = "AbstractRxPktArch"):
        """
        CTOR
        @param name
        """
        AbstractPktArch.__init__(self, name)
        OpERABase.__init__(self, name)
