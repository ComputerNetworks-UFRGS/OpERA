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

from abc import ABCMeta
from abc import abstractmethod
from gnuradio import channels #pylint: disable=F0401

from device import UHDGenericArch #pylint: disable = F0401
from device import UHDBase   #pylint: disable = F0401


class AbstractChannel(UHDGenericArch):
    """
    """

    __metaclass__ = ABCMeta

    def __init__(self, name = "AbstractName", component = None):
        """
        """

        if isinstance(component, UHDBase):
            component = component.uhd
        input_signature  = component.input_signature()
        output_signature = component.output_signature()

        self._component = component

        UHDGenericArch.__init__(self, name = name,
                input_signature  = input_signature,
                output_signature = output_signature)


    #def __hasattr__(self, name):
    #    print "aqui"
    #    if hasattr(self._component, name):
    #        return getattr(self._component, name)

    #    raise AttributeError


    #def __getattr__(self, name):
    #    if hasattr(self._component, name):
    #        return getattr(self._component, name)

    #    raise AttributeError

    #def __setattr__(self, name, val):
    #    if hasattr(self._component, name):
    #        return setattr(self._component, name, val)

    #    object.__setattr__(self, name, val)
