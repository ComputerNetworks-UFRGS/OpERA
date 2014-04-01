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
@package utils
"""

import time
import random
import threading

from math import *
from struct import *


class Channel(object):
    """
    Represents a channel with number, central frequency and bandwidth
    """

    def __init__(self, ch, freq, bw):
        """
        CTOR
        @param ch Channel number
        @param freq Channel central frequency
        @param bw Channel bandwidth
        """
        self._channel = ch
        self._freq = freq
        self._bw = bw


    def get_channel(self):
        """
        Return channel number.
        """
        return self._channel

    def get_freq(self):
        """
        Return channel frequency.
        """
        return self._freq

    def get_bandwidth(self):
        """
        Return channel bandwidth
        """
        return self._bw

    def __repr__(self):
        """
        Overridden method.
        """
        return repr("Channel %d (%f)" % (self.get_channel(), self.get_freq()))


class ChannelThread(threading.Thread):
    """
    Thread representing a channel whose status changes in time.
    Each channel thread must be associated to a Channel object.
    When the center_freq method on the ChannelModeler is called, the corresponding ChannelThread is activated.
    The ChannelThread controls an AbstractDevice object, by changing is central frequency following a random distribution.
    The distribution is a function callback.
    """

    _running = False

    def __init__(self, channel_modeler, device, the_channel, dist_callback):
        """
        CTOR.
        @param channel_modeler ChannelModeler instance.
        @param device AbstractDevice object instance.
        @param the_channel Channel object instance.
        @param dist_callback Distribution callback.
        """

        threading.Thread.__init__(self)

        self._channel_modeler = channel_modeler
        self._the_device = device
        self._the_channel = the_channel
        self._dist_callback = dist_callback

        self._active = False
        self._status = random.randrange(1, 3)


    def _set_center_freq(self):
        """
        Set frequency.
        Only the active ChannelThread can change the RadioDevice frequency.
        """

        # sanity check
        if not self._active:
            raise AttributeError

        if self._status:
            self._the_device.center_freq = self._the_channel.freq
        else:
            self._the_device.center_freq = 1e9


    def run(self):
        """
        Thread start function .
        """

        # Thread loop
        while ChannelThread._running:
            # if this thread is controlling the device
            if self._active:
                self._set_center_freq()

            time.sleep( self._dist_callback(self._the_channel, self._status) )
            self._status = (self._status+1) % 2


    def active(self, act):
        """
        Enable/disable thread 'active' status.
        @param act Active True/False.
        """
        self._active = act

        if self._active:
            self._set_center_freq()


class ChannelModeler(object):
    """
    Proxy for an AbstractDevice.
    This class is used to 'fake' channel changes by intercepting the 'center_freq' call.
    This class is used to proxy calls do AbstractDevice.center_freq 
    When AbstractDevice.center_freq is called, this class activates a thread that changes the central frequency.
    For the point of view of any external observer, the signal received is 'changing'
    """

    def __init__(self, device, channel_list, dist_callback):
        """
        CTOR.
        @param device AbstractDevice implementation.
        @param channel_list List of channels manage by the channel modeler
        @param dist_callback Distribution Callback
        """
        object.__init__(self)

        # Subject is the proxied object.
        object.__setattr__(self, '_device', device)
        object.__setattr__(self, '_curThread', None)

        # dictionary (channel, thread) to easily find the thread given a channel
        object.__setattr__(self, '_threads',
                           {channel: ChannelThread(self, device, channel, dist_callback) for channel in channel_list})

        # call start() on all threads
        ChannelThread._running = True
        map(lambda x: x.start(), self._threads.itervalues())


    ##::TODO:: esse @enable ta certo ou apenas esqueceram do @param antes??
    def _thread_activity(self, channel_thread, enable):
        """
        Change the channel_thread ChannelThread object activity.
        @param channel_thread Object to disable.
        @param enable True to enable.
        @enable True to enable.
        """
        if channel_thread:
            channel_thread.active(enable)


    def _center_freq(self, channel):
        """
        Intercept center_freq call for the AbstractDevice object.
        @param channel Channel object
        """
        self._thread_activity(self._curThread, False)   # disable current thread

        the_thread = self._threads[channel]
        self._thread_activity(the_thread, True)             # activate next thread
        object.__setattr__(self, '_curThread', the_thread)  # set new current thread based on channel value


    def __getattr__(self, attrname):
        """
        Overridden method.
        Forward unknown request to the proxied object.
        @param attrname Variable name
        """
        return getattr(self._device, attrname, None)

    def __setattr__(self, var, val):
        """
        Overridden method.
        Python way to proxy a object.
        Intercept any change to the center_freq property of the AbstractDevice object.
        @param var Name of the property changed.
        @param val The new value for this property.
        """

        # Check if is the 'center_freq' parameter
        if hasattr(self, var) and var == 'center_freq':
            self._center_freq(val)
        else:
            self._device.setattr(var, val)
