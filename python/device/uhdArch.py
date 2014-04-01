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
from abc import ABCMeta
from abc import abstractmethod

from gnuradio import gr  #pylint: disable=F0401

# OpERA imports
from OpERABase import OpERABase  #pylint: disable=F0401
from abstractArch import AbstractSSArch
from abstractArch import AbstractTxPktArch
from abstractArch import AbstractRxPktArch


class UHDBaseArch(gr.hier_block2):
    """
    Abstract class for the UHD architectures.
    This is the base class for UHD architectures.
    """

    def __init__(self, name, input_signature, output_signature):
        """
        CTOR
        @param name Instance name.
        @param input_signature.
        @param output_signature.
        """
        object.__setattr__(self, "_radio_device", None)

        gr.hier_block2.__init__(self,
                                name=name,
                                input_signature=input_signature,
                                output_signature=output_signature,
                                )

        self.__initialized = False

        self._blocks = []


    #::TODO:: pq o paramtro top_block nao eh usado:???
    @abstractmethod
    def pre_connect(self, top_block):
        """
        Called before the connection is made.
        In this function, the hier_block2 internal blocks must be connected

        @param top_block TopBlock
        """
        if self.__initialized:
            return

        for blocks in self._blocks:
            if len(blocks) > 1:
                self.connect(*blocks) # pylint: disable=E1101

        self.__initialized = True


    def _add_connections(self, blocks):
        """
        @param blocks
        """
        self._blocks.append(blocks)


    def get_connections(self):
        """
        """
        return self._blocks


    def set_radio_device(self, radio_device):
        """
        Set the radio device used for this UHDBaseArch.
        @param radio_device
        """
        self._radio_device = radio_device


    @property
    def radio(self):
        """
        """
        if self._radio_device is not None:
            return self._radio_device

        raise AttributeError('Radio is None')


class UHDGenericArch(UHDBaseArch, OpERABase):
    """
    """

    __metaclass__ = ABCMeta

    def __init__(self, name, input_signature, output_signature):
        """
        CTOR
        @param name SS Arch instance name
        @param input_signature A gr.io_signature instance.
        @param output_signature A gr.io_signature instance.
        """
        OpERABase.__init__(self, name=name)
        UHDBaseArch.__init__(self,
                             name=name,
                             input_signature=input_signature,
                             output_signature=output_signature
                             )

        self._block = self._build(input_signature, output_signature)

        # Connect input/outputs if necessary
        """
        ::TODO::
        Pass this code to UHDBaseArch. Maybe in the pre_process function ?
        """
        blocks = []
        if input_signature.min_streams():
            blocks.append(self)

        blocks.append(self._block)

        if output_signature.min_streams():
            blocks.append(self)  #pylint: disable=E1101
        self._add_connections(blocks)


    #::TODO:: o parametro callback aparece na doc, mas nao esta dentree os parametros da funcao
    @abstractmethod
    def _build(self, input_signature, output_signature):
        """
        Build internal blocks  of the architecture.
        @param callback Callback function.
        @param input_signature  A gr.io_signature instance.
        @param output_signature A gr.io_signature instance.
        @return A GNURadio source block.
        """
        pass


class UHDSSArch(UHDBaseArch, AbstractSSArch):
    """
    Base architecture for spectrum sensing with UHD devices.
    """

    __metaclass__ = ABCMeta

    def __init__(self, name, input_signature, output_signature):
        """
        CTOR
        @param name SS Arch instance name
        @param input_signature A gr.io_signature instance.
        @param output_signature A gr.io_signature instance.
        """
        AbstractSSArch.__init__(self, name)
        UHDBaseArch.__init__(self,
                             name=name,
                             input_signature=input_signature,
                             output_signature=output_signature
                             )

        self._sensing = self._build(input_signature, output_signature)
        # Connect input/outputs if necessary
        if self._sensing:
            """
            ::TODO::
            Pass this code to UHDBaseArch. Maybe in the pre_process function ?
            """
            blocks = []
            if input_signature.min_streams():
                blocks.append(self)

            blocks.append(self._sensing)

            if output_signature.min_streams():
                blocks.append(self)  #pylint: disable=E1101
            self._add_connections(blocks)


    @abstractmethod
    def _build(self, input_signature, output_signature):
        """
        Build internal blocks  of the architecture.
        @param callback Callback function.
        @param input_signature  A gr.io_signature instance.
        @param output_signature A gr.io_signature instance.
        @return A GNURadio source block.
        """
        pass


    def sense_channel(self, channel, sensing_duration):
        """
        SS on a single channel.
        Implements AbstractSSArch abstract method.
        @param the_channel Channel to be sensed.
        @param sensing_time Sensing duration on channel.
        @return Tuple (decision, energy)
        """
        # save -> sense -> restore

        prev_channel = self.radio.get_channel()

        self.radio.set_channel(channel)
        res =  self._get_sensing_data( channel, sensing_duration )

        prev_channel and self.radio.set_channel(prev_channel)

        return res


    #::TODO:: parametro sensing_duration == sensing_time???
    @abstractmethod
    def _get_sensing_data(self, channel, sensing_duration):
        """
        Sense channel and return data.
        The channel frequency is already configured when this method is called.
        @param channel Channel object.
        @param sensing_time Sensing duration.
        @return Sensing data.
        """
        pass


class UHDTxPktArch(UHDBaseArch, AbstractTxPktArch):
    """
    Base architecture to send packets with UHD devices
    """

    __metaclass__ = ABCMeta

    def __init__(self, name, input_signature, output_signature):
        """
        CTOR
        @param name Instance name.
        @param input_signature A gr.io_signature instance.
        @param output_signature A gr.io_signature instance.
        """
        AbstractTxPktArch.__init__(self, name)
        UHDBaseArch.__init__(self, name=name,
                             input_signature=input_signature,
                             output_signature=output_signature
                             )

        # Derived class implementation
        self._modulator = self._build(input_signature, output_signature)

        # Connect input/outputs if necessary
        """
        ::TODO::
        Pass this code to UHDBaseArch. Maybe in the pre_process function ?
        """
        blocks = []
        if input_signature.min_streams():
            blocks.extend([self, self._modulator])
        if output_signature.min_streams():
            blocks.append(self)  #pylint: disable=E1101

        self._add_connections(blocks)


    @abstractmethod
    def _build(self, input_signature, output_signature):
        """
        Build internal blocks  of the architecture.
        @param input_signature
        @param output_signature
        @return A GNURadio sink block.
        """
        pass

    def _send_pkt(self, payload, eof=False):
        """
        Transmit the payload using a implementation specific modulator
        @param payload A struct type
        @param eof End of file. True/False
        """
        self._modulator.send_pkt(payload, eof)
        # We cannot send too much packets because GNURadio buffers then in memory
        time.sleep(0.01)


class UHDRxPktArch(UHDBaseArch, AbstractRxPktArch):
    """
    Receive data through USRP.
    This is the base class for the rx devices.
    """
    __metaclass__ = ABCMeta

    def __init__(self, name, callback, input_signature, output_signature):
        """
        CTOR
        @param name Instance name.
        @param callback Callback function with signature (self, payload).
        @param input_signature A gr.io_signature instance.
        @param output_signature A gr.io_signature instance.
        """
        AbstractRxPktArch.__init__(self, name)
        UHDBaseArch.__init__(self, name=name,
                             input_signature=input_signature,
                             output_signature=output_signature
                             )

        # keep callback
        self._callback = callback

        # Build demodulator
        self._demod = self._build(self._pkt_rx_callback, input_signature, output_signature)

        # Connect input/outputs if necessary
        """
        ::TODO::
        Pass this code to UHDBaseArch. Maybe in the pre_process function ?
        """
        blocks = []
        if input_signature.min_streams():
            blocks.extend([self, self._demod])  #pylint: disable=E1101
        if output_signature.min_streams():
            blocks.append(self)  #pylint: disable=E1101
        self._add_connections(blocks)


    @abstractmethod
    def _build(self, callback, input_signature, output_signature):
        """
        Build internal blocks of the architecture.
        @param callback Callback function.
        @param input_signature A gr.io_signature instance.
        @param output_signature A gr.io_signature instance.
        @return A GNURadio source block.
        """
        pass

    def _pkt_rx_callback(self, ok, payload):
        """
        Wraps the callback necessary in the GNU Radio reception.
        Firstly, we account the payload in the PktBitRate class, after
        we call the callback received in the CTOR or we queue the payload.
        @param ok
        @param payload
        """
        self._counter.count(payload)
        self._callback(ok, payload)
