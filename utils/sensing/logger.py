#!/usr/bin/env python

#@package utils

import os
import matplotlib.pyplot as plt

## Log class
# Used it to add information
class Logger(object):

	_enable = False
	_history = {}
	_objects = {}
	_ch_status = 0

	## Clear all data added
	@staticmethod
	def clear_all():
		Logger._history   = {}
		Logger._ch_status = {}


	## Register object to log
	# @param name Object name
	# @param item List of items (variables) to log
	# @param default_value Default value
	@staticmethod
	def register(name, items, default_value = 0):
		if not name in Logger._history:
			Logger._history[name] = {}

		for i in items:
			if default_value == 0:
				Logger._history[name][i] = []
			else:
				Logger._history[name][i] = [ default_value, ]


	## Get data from object
	# @param name Name of object
	# @param variable Name of object variable
	@staticmethod
	def get_data(name, variable):
		data = Logger._history[name][variable]

		# Is array
		# Copy array data to other array (deep copy)
		if isinstance(data, list):
			return data
			ret = []
			for tup in data:
				ret.append(tup[0])

			return ret
		# Not array
		else:
			return data


	## Add data
	# @param name Object name
	# @param variable Variable name
	# @param value Value
	# @param ch_status Append global channel status also
	@staticmethod
	def append(name, variable, value, ch_status = False):
		# Return if log is not enable
		if not Logger._enable:
			return

		if not ch_status:
			Logger._history[name][variable].append( value )
		else:
			Logger._history[name][variable].append( (value, Logger._ch_status) )


	## Change previosly added data value
	# @param name Object name
	# @param variable Variable name
	# @param value New balue
	@staticmethod
	def set(name, variable, value):
		if not Logger._enable:
			return

		Logger._history[name][variable] = value


	## Register a callback to be called by the logger class.
	# The callback MUST return a value that can be inserted in the _history.
	# @param name Object name
	# @param item A items (variable) to log
	# @param obj Callback function.
	@staticmethod
	def register_getter(name, item, callback):
		if not name in Logger._objects:
			Logger._objects[name] = {}

		Logger._objects[name][i] = obj
		Logger.register(name, [item, ])

	## Append a callback data to _history.
	# @param name Object name.
	# @param item Item name.
	# @param ch_status True to append channel status.
	@staticmethod
	def log_object(name, item, ch_status = False):
		Logger.append(name, item, Logger._object[name][item](), ch_status )

	
	## Plot a figure
	# @param direc
	# @param subdirec
	# @param plot_arr Array of tuple. for each tuple:
	#	- first element: obj_name
	#	- second element: array of parameters to plot
	# @param it
	@staticmethod
	def dump_plot(direc, subdirec, plot_arr, it):

		Logger.directory( direc, subdirec )

		# Sanity check
		if not plot_arr:
			return

		# Number of plots:
		t_plots = 0
		for plot in plot_arr:
			obj_name, obj_data = plot

			t_plots += len(obj_data)

		# create plot
		f, axarr = plt.subplots( t_plots, sharex = True )

		# Plots
		cur_idx = 0
		for plot in plot_arr:
			obj_name, obj_data = plot

			for idx, data_name in enumerate(obj_data):
				data = Logger.get_data(obj_name, data_name)

				axarr[ cur_idx ].plot( range( len(data) ), data )
				axarr[ cur_idx ].set_ylabel( data_name )

				axarr[ cur_idx ].set_ylim( min(data) - min(data)/100, max(data) + max(data)/100)

				cur_idx += 1

		plt.savefig( direc + subdirec + '/plot_' + str(it) + '.pdf' )


	## Save all objects
	# @param direc Directory
	# @param subdirec Subdirectory
	# @param it Iterations
	@staticmethod
	def dump(direc, subdirec, it = -1):
		Logger.directory( direc, subdirec )

		for name in Logger._history:
			Logger.dump_obj( name = name,
					data = Logger._history[ name ],
					directory = direc + subdirec,
					it = it )

	## Dump a single object data
	# @param name Object Name
	# @param data Dictionary of parameters. Parameters is a list of values
	# @param directory Directory to dump data
	# @param it Test Iteration (used do separate repetitions of tests)
	@staticmethod
	def dump_obj(name, data, directory, it = -1):
		for d in data:
			# Save list
			if isinstance(data[d], list):
				# File name
				fstr = '/' + name + '_' + d + ('_' + str( it ) if it != -1 else '') + '.txt'

				# Create file and dump all items
				fd = open( directory + fstr, 'w' ) 
				fd.write('\n'.join(map(lambda x: str(x), data[d])) + "\n")
			# Save global
			else:
				fstr = '/' + name + '_global'  + ('_' + str( it ) if it != -1 else '') + '.txt'

				# Create file and dump all items
				fd = open( directory + fstr, 'a' )
				fd.write(d + ':' + str(data[d]) + '\n')


	## Create d and subd directories if necessary
	# @param d Directory
	# @param subd Subdirectory
	@staticmethod
	def directory( d, subd ):
		if not os.path.exists( d ):
			os.makedirs( d )
		if not os.path.exists( d + subd ):
			os.makedirs( d + subd )
