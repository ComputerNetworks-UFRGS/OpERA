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

from gnuradio import channels #pylint: disable=F0401

from device import UHDBaseArch #pylint: disable = F0401
from device import UHDBase   #pylint: disable = F0401

from abstractChannel import AbstractChannel

class FadingChannel(AbstractChannel):
    """
    Class that applies a fading over an input signal.

    Design pattern: DECORATOR
    """

    def __init__(self, name = "FadingModel", component = None):
        """
        CTOR

        @param name Block name.
        @param component The decorator component.
        """

        AbstractChannel.__init__(self, name = name, component = component)


    def _build(self, component):
        """
        Base classe abstract method.
        @param component The decorator component.
        """
        return channels.fading_model( 8, 0.1, False, 0.001, 0 )
