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


## Try to import easygui.
try:
	import easygui
	easygui_import = True

except ImportError:
	easygui_import = False
	


import os
import sys

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, path)

from gnuradio  import gr
from gnuradio import blocks
from gnuradio.eng_option import eng_option
from optparse  import OptionParser
from struct    import * 
from threading import Thread
import time
import random

import numpy as np

#Project imports:

from OpERAFlow 		import OpERAFlow
from device             import *
from algorithm.decision import EnergyDecision
from gr_blocks          import *
from reception.sensing  import EnergySSArch, EnergyCalculator
from reception.packet   import PacketGMSKRx, PacketOFDMRx
from transmission       import PacketGMSKTx, PacketOFDMTx, SimpleTx
from utils 		import Channel, TopBlock, Logger, ChannelModeler


## constants

MIN_FREQ = 100e6
MAX_FREQ = 2.2e9

MIN_GAIN = 0
MAX_GAIN = 30

NEW_FREQ = "Set a new frequency" 
GAIN_MULTIPLIER = "Set a new gain multiplier"
QUIT = "Quit"

OPT_SET_FREQ = 1
OPT_SET_GAIN = 2
OPT_QUIT = 3


ENTER = "enter"
RAW_ENTER = ""


## functions:

# Check the os and use an apropriate function to clear the screen
def clear_screen():

	# Clear Windows command prompt.
	if (os.name in ('ce', 'nt', 'dos')):
    		os.system('cls')

	# Clear the Linux terminal.
	elif ('posix' in os.name):
		    os.system('clear')




###########################################################################################
# Add energy_calculator and energy to the Logger print list.
def add_print_list():
	print "\n******************************************************************\n"
	print "\nPrinting the energy\n"
	Logger.add_to_print_list("energy_calculator", "energy")
	print "\n******************************************************************\n"


###########################################################################################
# Prints the energy.
def printing_energy():
	clear_screen()
	key = None
	
	# Press enter to exit (stop the printing).
	while key is not ENTER:
		add_print_list()
		key = raw_input()
		# If "enter" key was pressed, exit the loop:
		if RAW_ENTER in key:
			key = ENTER

###########################################################################################
## Definition of the radio device, uhd device, etc
def device_definition():
	
	tb = OpERAFlow(name = 'US')

	uhd_source = UHDSource()
	uhd_source.samp_rate = 195512
	device_source = RadioDevice(the_source = uhd_source, the_sink = blocks.probe_signal_f())

	energy = EnergySSArch(device = device_source,
				fft_size  = 512,
				mavg_size = 5,
				algorithm = None)

	tb.add_path(abstract_arch = energy, radio_device = device_source, name_of_arch = 'ss')

	return tb, device_source

###########################################################################################
## Easygui 
# Frequency should be in range(100e6, 2.2e9)

# Set frequency method, when using easygui
def eg_set_frequency():
	mens = "Enter the frequency: "
	frequency = ""
	float_freq = False
	
	frequency_ok = False
	no_freq = False

	Logger.remove_from_print_list("energy_calculator", "energy")

	while frequency_ok is False and no_freq is False:

		frequency = easygui.enterbox(mens)
		##print frequency
		if frequency is not None:
			try:
				float_freq = float(frequency)
				if float_freq < MIN_FREQ or float_freq > MAX_FREQ:
					range_error = "Frequency should be in range(100e6, 2.2e9)."
					easygui.msgbox(range_error)
				else:
					frequency_ok = True

			except ValueError:
				type_error = "Frequency should be a float number."
				easygui.msgbox(type_error)

		elif frequency is None:
			choices = ["Yes", "No"]
			msg = "Quit the frequency setter?"	
			reply   = easygui.buttonbox(msg,choices=choices)
			if reply is "Yes":
				no_freq = True

	
	# print the energy
	#printing_energy()
	return float_freq, no_freq


## Gain multiplier for the radio device. It should be in range(0, 30).
def eg_gain_multiplier():
	mens = "Enter the gain multiplier: "
	gain = ""
	float_gain = 0
	
	gain_ok = False
	no_gain = False

	while gain_ok is False and no_gain is False:
		gain = easygui.enterbox(mens)
		if gain is not None:
			try:
				float_gain = float(gain)
				if float_gain < MIN_GAIN or float_gain > MAX_GAIN:
					range_error_msg = "Gain multiplier should be in range (0, 30)."
					easygui.msgbox(range_error_msg)

				else:
					gain_ok = True

			except ValueError:
				type_error_msg = "Gain multiplier should be a float number."
				easygui.msgbox(type_error_msg)

	#If the user press "cancel":
		elif gain is None:
			choices = ["Yes", "No"]
			msg = "Quit gain multiplier setter?"	
			reply   = easygui.buttonbox(msg,choices=choices)
			if reply is "Yes":
				no_gain = True

	#return both the gain multiplier and the bool which is True wheter the user press cancel.
	return float_gain, no_gain
			
		
## Main menu window, using easygui.
def eg_main_window():

	#remove from print list"
	Logger.remove_from_print_list("energy_calculator", "energy")

	choices = [NEW_FREQ, GAIN_MULTIPLIER, QUIT]
	msg = "Choose one option: "
	reply = easygui.buttonbox(msg, choices=choices)
	return reply
	
	
## Execution using easygui.
def with_easygui():
	
	tb, radio = device_definition()
	tb.start()
	continue_loop = True
	no_freq = False

	while continue_loop is True: 
		reply = eg_main_window()

		if reply is QUIT:
			choices = ["Yes", "No"]
			msg = "Are you sure?"	
			reply   = easygui.buttonbox(msg,choices=choices)
			if reply is "Yes":
				tb.stop()
				continue_loop = False
				os._exit(1)

		elif reply is NEW_FREQ:
			freq, no_freq = eg_set_frequency()
			if no_freq is False:	
				radio.center_freq = freq
				# print the energy
				printing_energy()

		elif reply is GAIN_MULTIPLIER:
			gain, no_gain = eg_gain_multiplier()
			if no_gain is False:
				radio._set_gain(gain)
				printing_energy()

############################################################################################
## Terminal
 
# Function to set the frequency, when using console.
def console_set_frequency():
	str_freq = ""
	float_freq = 0
	
	# Bool variable to control the loop.
	input_ok = False
	
	# Clear the screen
	clear_screen()
	
	#print "\nremove from print list"
	#Logger.remove_from_print_list("energy_calculator", "energy")

	# Make sure the input frequency fits the requirement.
	while input_ok is False:
		str_freq = raw_input("\nEnter a frequency value. Should be in range(1e8, 2.29e9): ")
		try:
			float_freq = float(str_freq)
			if float_freq < MIN_FREQ or float_freq > MAX_FREQ:
				print "\nInput should be in range (1e8, 2.29e9)."
			
			else:	
				input_ok = True

		except ValueError:
			print "\nInput should be a float number."


	# print the energy
	##printing_energy()

	return float_freq


## Set gain multiplier of a radio device.
def console_gain_multiplier():
	str_gain = ""
	float_gain = 0
	
	# Bool variable to control the loop.
	input_ok = False
	
	# Clear the screen
	clear_screen()
	
	# Make sure the input gain fits the requirement.
	while input_ok is False:
		str_gain = raw_input("\nEnter the gain multiplier. Should be in range(0, 30): ")
		try:
			float_gain = float(str_gain)
			if float_gain < MIN_GAIN or float_gain > MAX_GAIN:
				print "\nInput should be in range (0, 30)."
			
			else:	
				input_ok = True

		except ValueError:
			print "\nInput should be a float number."

	return float_gain


## Main menu when using the console.
def console_main_menu():
	# Clear the screen.

	#remove from print list"
	Logger.remove_from_print_list("energy_calculator", "energy")
	clear_screen()
	
	print "***************************************************************\n"
	print "\t1. Set a new frequency.\n"
	print "\t2. Set the gain multiplier.\n"
	print "\t3. Quit.\n"
	print "*****************************************************************\n\n"

	input_ok = False



	while input_ok is False:
		choice = raw_input("Choose one option: ")

		if choice.isdigit() is True:
			int_choice = int(choice)
			
			if int_choice is not OPT_SET_FREQ and int_choice is not OPT_SET_GAIN and int_choice is not OPT_QUIT:
				print "\n\nChosen operation is invalid.\n"
			
			else:
				input_ok = True
		
		else:
			print "\n\nEnter a number that corresponds to a valid operation.\n"
		
	return int_choice

## Execution using console.
def with_terminal():
	tb, radio = device_definition()
	tb.start()
	continue_loop = True

	while continue_loop is True:
		choice = console_main_menu()
		if choice is OPT_SET_FREQ:
			freq = console_set_frequency()
			radio.center_freq = freq
			# print the energy
			printing_energy()

		
		elif choice is OPT_SET_GAIN:
			gain = console_gain_multiplier()
			radio._set_gain(gain)
			# print the energy
			printing_energy()

			
			
		elif choice is OPT_QUIT:
			print "\nQuitting the program.\n"
			tb.stop()
			continue_loop = False
			os._exit(1)
			


###########################################################################################
## Main function
def main():
	#if easygui_import is True:
	#	with_easygui()

	#elif easygui_import is False:
	with_terminal()

if __name__ == "__main__":
	main()
