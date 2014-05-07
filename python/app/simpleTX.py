#!/usr/bin/env python

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

import os
import sys

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, path)

from gnuradio import gr
from gnuradio import blocks
from gnuradio.eng_option import eng_option
from optparse import OptionParser
from struct import *
from threading import Thread
import time
import random

import numpy as np
from abc import ABCMeta, abstractmethod

#Project imports:
from OpERAFlow import OpERAFlow
from device import *
from sensing import EnergyDecision
from gr_blocks import *
from sensing import EnergySSArch, EnergyCalculator
from packet import PacketGMSKRx, PacketOFDMRx, SimpleTx
from utils import Channel, Logger, ChannelModeler


# Try to import easygui.
try:
    import easygui

    easygui_import = True

except ImportError:
    easygui_import = False

# Constants used in the program:

# ranges:
MIN_FREQ = 100e6
MAX_FREQ = 2.2e9

MIN_GAIN = 0
MAX_GAIN = 30

# options
STR_FREQ = "Frequency"
STR_GAIN = "Gain multiplier"

#questions
QUESTION_SET_TX_FREQ = "Enter a trasmission frequency value. Should be in range"
QUESTION_SET_GAIN = "Enter a gain multiplier. Should be in range"

# menu (operations)
NEW_TX_FREQ = "Set a new transmission frequency"
NEW_GAIN = "Set a new gain multiplier"
QUIT = "Quit"

# integers representing the operations
OPT_SET_TX_FREQ = 1
OPT_SET_GAIN = 2
OPT_QUIT = 3

# others
MIN_OPT = 1
MAX_OPT = 3

YES = 1
NO = 0

ENTER = "enter"
RAW_ENTER = ""


def clear_screen():
    """
    Check the os and use an appropriate function to clear the screen
    """
    # Clear Windows command prompt.
    if (os.name in ('ce', 'nt', 'dos')):
        os.system('cls')

    # Clear the Linux terminal.
    elif ('posix' in os.name):
        os.system('clear')


class OpERAUtils(object):
    """
    Class with useful methods from OpERA
    """

    def __init__(self):
        """
        CTOR
        """
        pass

    @staticmethod
    def device_definition():
        """
        Definition of the devices used in the program.
        """
        tb = OpERAFlow(name='US')

        uhd_sink = UHDSink()

        radio_source = blocks.vector_source_f(map(int, np.random.randint(0, 100, 1000)), True)

        device_source = RadioDevice(name="device_source")
        device_source.add_arch(source=radio_source, arch=uhd_sink, sink=uhd_sink, uhd_device=uhd_sink, name='tx')

        tx_arch = SimpleTx()

        return tb, device_source


class AbstractMenu(object):
    """
    Abstract class for the menus.
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        """
        CTOR
        """
        pass

    def get_value_in_range(self, min_value, max_value, question, option):
        """
        Reads a value (from the user) and check if it is in range (ie, min_value >= value <= max_value).
        @param min_value Mininum value of the range (float number)
        @param max_value Maximum value of the range (float number)
        @param question Question asked (string type)
        @param option (string type)
        @return float_value
        @return no_value Indicates if the value returned is valid (no_value = False) or if the user has
                        cancelled the operation (no_value = True).
        """


        # Check if the chosen option is "Set Frequency" or "Set Gain Multiplier", in order
        # to use the most appropriate string formatting.
        if option is STR_GAIN:
            mens = "%s (%.2f, %.2f)." % (question, min_value, max_value)

        elif option is STR_FREQ:
            mens = "%s (%.2e, %.2e)." % (question, min_value, max_value)

        value = ""
        float_value = False
        value_ok = False
        no_value = False

        while value_ok is False and no_value is False:
            value = self._get_value(mens)

            # If it is a valid input.
            if value is not None:
                try:
                    float_value = float(value)
                    # If the value is a float number but it's not in range, shows an error message
                    if float_value < min_value or float_value > max_value:
                        if option is STR_GAIN:
                            range_error = "%s should be in range (%.2f, %.2f)." % (option, min_value, max_value)

                        elif option is STR_FREQ:
                            range_error = "%s should be in range (%.2e, %.2e)." % (option, min_value, max_value)
                        self._show_error_msg(range_error)

                    # If the value if a float number and it's in range, so the input is valid. Exits the loop.
                    else:
                        value_ok = True

                # If the input is not a float number, shows an error message.
                except ValueError:
                    type_error = "%s should be a float number." % (option)
                    self._show_error_msg(type_error)

            # If the user has cancelled the operation.
            elif value is None:
                # Check if the user wants to quit.
                choices = ["Yes", "No"]
                msg = "Quit the %s setter? " % (option.lower())
                reply = self._choose_option(msg, choices)

                if reply is "Yes":
                    no_value = True
        # Returns the value (casted to float) and a boolean that indicates if the value
        #  returned is valid or not(in case of cancelled operation).
        return float_value, no_value


    @abstractmethod
    def _show_error_msg(self, msg):
        """
        Shows an error message with the appropriate GUI.
        @param msg Error message.
        """
        pass

    @abstractmethod
    def _choose_option(self, msg, choices):
        """
        Let the user choose an option and return the integer that represents it.
        @param msg Instruction message
        @param choices List of choices
        """
        pass

    @abstractmethod
    def _get_value(self, msg):
        """
        Returns the read value
        @param msg
        """
        pass


class Menu(AbstractMenu):
    """
    Class that manages the GUIs.
    """
    def __init__(self):
        AbstractMenu.__init__(self)

        # If the import was successful, uses Easygui as GUI.
        if easygui_import is True:
            self._menu = EasyguiMenu()

        # If it isn't, uses the Console.
        else:
            self._menu = ConsoleMenu()


    def get_value_in_range(self, min_value, max_value, question, option):
        """
        @param min_value Mininum value of the range (float number)
        @param max_value Maximum value of the range (float number)
        @param question Question asked (string type)
        @param option (string type --> or constant??)
        """
        return self._menu.get_value_in_range(min_value, max_value, question, option)


    def main_menu(self):
        """
        Shows the main menu
        """
        self._menu._main_menu()

    def _show_error_msg(self, msg):
        """
        Shows an error message with the appropriate interface.
        """
        self._menu._show_error_msg(msg)


    def _choose_option(self, msg, choices):
        """
        Let the user choose an option from a list of choices.
        """
        return self._menu._choose_option(msg, choices)

    def _get_value(self, msg):
        """
        Return the value entered by the user.
        """
        self._menu._get_value(msg)

    def _show_menu(self, str_list):
        """
        Shows a menu.
        """
        return self._menu._show_menu(str_list)


class EasyguiMenu(AbstractMenu):
    """
    Class for the menu (shown with easygui)
    """

    def __init__(self):
        """
        CTOR
        """
        AbstractMenu.__init__(self)

    def _show_error_msg(self, msg):
        """
        Easygui implementation for showing a message.
        """
        easygui.msgbox(msg)

    def _choose_option(self, msg, choices):
        """
        Easygui implementation of showing options and letting the user choose one of them.
        """
        reply = easygui.buttonbox(msg, choices=choices)
        if reply is "Yes":
            return YES
        elif reply is "No":
            return NO

    def _get_value(self, msg):
        """
        Easygui implementation of getting a value from the user.
        """
        value = easygui.enterbox(msg)
        return value

    def _show_menu(self, str_list):
        """
        Easygui implementation of showing a menu with many options and letting the user choose one of them.
        """
        choices = str_list
        msg = "Choose one option: "
        reply = easygui.buttonbox(msg, choices=choices)

        if reply is NEW_TX_FREQ:
            int_reply = 1
        elif reply is NEW_GAIN:
            int_reply = 2
        elif reply is QUIT:
            int_reply = 3
        return int_reply


class ConsoleMenu(AbstractMenu):
    """
    Class for the menu (shown in console)
    """
    def __init__(self):
        """
        CTOR
        """
        AbstractMenu.__init__(self)

    def _show_error_msg(self, msg):
        """
        Shows a string message.
        """
        print msg

    def _choose_option(self, msg, choices):
        """
        Shows the options that the user has to choose, and return the chosen one.
        """
        reply_ok = False

        while reply_ok is False:
            print msg
            for num, opt in enumerate(choices):
                print "%i: %s" % (num, opt)

            reply = raw_input("\nChoose one option: ")
            try:
                int_reply = int(reply)
                if int_reply is 0:
                    reply_ok = True
                    return int_reply

                elif int_reply is 1:
                    reply_ok = True
                    return int_reply

                else:
                    print "\nReply should be 0 (Yes) or 1 (No)."

            except ValueError:
                print "\nReply should be an integer."


    def _get_value(self, msg):
        """
        Get a value from the user.
        """
        str_value = raw_input("\n" + msg)
        return str_value

    def _show_menu(self, str_list):
        """
        Shows a menu, according to the strings in the string list (passed as a parameter).
        """

        print "*****************************************************************\n"
        for num, opt in enumerate(str_list):
            print "%i. %s" % (num, opt)
        print "*****************************************************************\n\n"

        input_ok = False

        while input_ok is False:
            choice = raw_input("Choose one option: ")

            if choice.isdigit() is True:
                int_choice = int(choice)

                if int_choice < MIN_OPT or int_choice > MAX_OPT:
                    print "\n\nChosen operation is invalid.\n"

                else:
                    input_ok = True

            else:
                print "\n\nEnter a number that corresponds to a valid operation.\n"

        return int_choice


def main(tb, radio):
    """
    Main function
    """
    # instance of Menu class
    menu = Menu()

    tb.start()
    radio.center_freq = 100e6
    continue_loop = True
    no_freq = False

    while continue_loop is True:
        reply = menu._show_menu([NEW_TX_FREQ, NEW_GAIN, QUIT])
        # Operation is quit.
        if reply is OPT_QUIT:
            choices = ["Yes", "No"]
            msg = "Are you sure?"
            reply_2 = menu._choose_option(msg, choices=choices)

            # If the answer is YES, quit the program. Else, continues in the loop.
            if reply_2 is YES:
                tb.stop()
                continue_loop = False
                print "\n******************************************"
                print "\tQuitting the program."
                print "******************************************\n"
                os._exit(1)

        # Operation is "set a new frequency".
        elif reply is OPT_SET_TX_FREQ:
            # gets the frequency
            freq, no_freq = menu.get_value_in_range(MIN_FREQ, MAX_FREQ, QUESTION_SET_TX_FREQ, STR_FREQ)
            if no_freq is False:
                radio.center_freq = freq


        # Operation is "set the gain multiplier".
        elif reply is OPT_SET_GAIN:
            # gets the gain
            gain, no_gain = menu.get_value_in_range(MIN_GAIN, MAX_GAIN, QUESTION_SET_GAIN, STR_GAIN)
            if no_gain is False:
                radio._set_gain(gain)


if __name__ == "__main__":
    tb, radio = OpERAUtils.device_definition()

    try:
        main(tb, radio)
    except KeyboardInterrupt:
        tb.stop()
        Logger.dump('./dump/', '', 0)
