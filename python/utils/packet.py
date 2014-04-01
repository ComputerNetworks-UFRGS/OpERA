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

import time
import struct

from collections import deque

from OpERABase import OpERABase  #pylint: disable=F0401
from utils import Logger         #pylint: disable=F0401


class PktBitRate(OpERABase):
    """
    Class for counting the bit rate.
    """

    def __init__(self, name="PktBitRate"):
        """
        CTOR
        @param name Instance name.
        """
        OpERABase.__init__(self, name)

        self._pkts = {'cur': 0, 'total': 0, 'counting': 0, 'accumulated': 0}
        self._bps = {'cur': 0, 'total': 0, 'counting': 0}

        # OpERA base method
        self.register_scheduling(self._tick, delay_sec=1)  # pylint: disable=E1101

        Logger.register(name, ['bps', 'pkts', 'pkt_accumulated'])


    def get_bps(self):
        """
        Return the current bps.
        """
        return self._bps['cur']

    def get_pkts(self):
        """
        Return the current pkt.
        """
        return self._pkts['cur']

    def get_pkt_accumulated(self, clear=False):
        """
        @param clear
        """
        tmp = self._pkts['accumulated']

        Logger.append(self._name, 'pkt_accumulated', self._pkts['accumulated'])  # pylint: disable=E1101

        if clear:
            self._pkts['accumulated'] = 0

        return tmp


    def count(self, payload):
        """
        Count the payload as a packet.
        @param payload Data of a packet.
        """
        self._pkts['counting'] += 1
        self._pkts['accumulated'] += 1
        self._bps['counting'] += (len(payload) * 8)


    def _tick(self):
        """
        Called automatically each one second.
        """
        for _d in (self._bps, self._pkts):
            _d['cur'] = _d['counting']
            _d['counting'] = 0

        Logger.append(self._name, 'bps',  self._bps['cur'] ) #pylint: disable=E1101
        Logger.append(self._name, 'pkts', self._pkts['cur']) #pylint: disable=E1101


class PktQueue(OpERABase):
    """
    PktQueue should be used as a callback for any RxPktArch.
    For example:
        queue = PktQueue()
        receiver = PacketGMSKRx(callback = queue)
        payload = queue.get_pkt()
    """

    def __init__(self, max_queue_len=1000,  name="PktQueue"):
        """
        CTOR.
        @param max_queue_len Maximum queue length.
        @param name Name of this instance.
        """
        OpERABase.__init__(self, name=name)

        self.__max_queue_len = max_queue_len
        self.__pkt_queue = deque()


    def __call__(self, ok, payload):
        """
        Enables a instance to be treated as a function.
        For example:
                queue = PktQueue()
                queue([1 2 3])
        @param ok
        @param payload data
        """
        self.__pkt_queue.append(payload)

        # dequeue if
        if len(self) > self.__max_queue_len:
            self.pop()

    def pop(self):
        """
        Returns the leftmost element of the list (older).
        @return Pkt payload.
        """
        return self.__pkt_queue.popleft()


    def __len__(self):
        """
        Return the number of packets in the queue.
        @return Length of packet queue.
        """
        return len(self.__pkt_queue)


    def __iter__(self):
        """
        Iterate over our packet queue.
        ::WARNING:: The queue is cleared.
        """
        _iter = iter(self.__pkt_queue)
        self.__pkt_queue.clear()

        return _iter


class PktSender(object):
    """
    Class to send packets
    """

    @staticmethod
    def _flood(fin_callback, tx_pkt_arch, payload=None, pkt_len=None):
        """
        Send packets until the fin_callback returns True.
        @param fin_callback Fin callback, must return True or false.
        @param tx_pkt_arch An AbstractTxPktArch instance.
        @param payload Packet payload. If None, we built it.
        @param pkt_len Packet length. Used if payload is none.
        """

        # Build payload if necessary
        if not payload:
            payload = struct.pack('%sB' % pkt_len, *[1] * pkt_len)

        # Loop to send packet
        finished = False
        while not finished:
            # callback
            finished = fin_callback()
            tx_pkt_arch.send_pkt(payload)


    @staticmethod
    def flood_by_pkt(n_pkts, tx_pkt_arch, payload=None, pkt_len=None):
        """
        Transmit 'n_pkts' packets with 'payload' data.
        @param n_pkts Total number of packets to send.
        @param tx_pkt_arch An AbstractTxPktArch instance.
        @param payload  Packet payload. If None, we built it.
        @param pkt_len Packet Length. Used if payload is None.
        @return Seconds elapsed to transmit n_pkts 
        """

        # callback
        def fin_callback():
            fin_callback.n_pkts -= 1
            return True if fin_callback.n_pkts == 0 else False
        fin_callback.n_pkts = 0
        fin_callback.time = time.time()

        # flood. fin_callback is called after each packet sent.
        PktSender._flood(fin_callback=fin_callback,
                         tx_pkt_arch=tx_pkt_arch,
                         payload=payload,
                         pkt_len=pkt_len)

        return time.time() - fin_callback.time


    #::TODO:: na lista de parametros temos o parametro duration, mas na documentacao aparece o parametro seconds. eles sao equivalentes??
    @staticmethod
    def flood_by_time(duration, tx_pkt_arch, payload=None, pkt_len=None):
        """
        Transmit for 'duration' seconds with 'payload' data.
        @param seconds Total duration.
        @param duration
        @param tx_pkt_arch An AbstractTxPktArch instance.
        @param payload  Packet payload. If None, we built it.
        @param pkt_len Packet Length. Used if payload is None.
        @return Total of packets send
        """

        def fin_callback():
            """

            """
            fin_callback.t_pkt += 1
            return True if time.time() > fin_callback.t_fin else False

        fin_callback.t_fin = time.time() + duration
        fin_callback.t_pkt = 0

        # flood. fin_callback is called after each packet sent.
        PktSender._flood(fin_callback = fin_callback,
                tx_pkt_arch = tx_pkt_arch,
                payload = payload,
                pkt_len = pkt_len)

        return fin_callback.t_pkt
