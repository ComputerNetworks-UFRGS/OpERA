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


#@package utils

import os
from threading import Semaphore 
#import matplotlib
#matplotlib.use("Agg")
#import matplotlib.pyplot as plt


class Logger(object):
    """
    Log class.
    Used it to add information.
    """

    _enable = True
    _history = {}
    _objects = {}
    _ch_status = None
    _print_list = {}

    __lock = Semaphore()


    @staticmethod
    def add_to_print_list(name, variable):
        """
        Associates a name and a variable in the print list (which is a dict).
        @param name The associated name.
        @param variable The associated variable.
        """
        # First, check if the name is already a key in the dict.
        if name in Logger._print_list:
            # The variable is associated with the name. Just return.
            if variable in Logger._print_list[name]:
                return
            
            else:
                Logger._print_list[name].append(variable)

        else:
            Logger._print_list[name] = []
            Logger._print_list[name].append(variable)


    @staticmethod    
    def remove_from_print_list(name, variable):
        """
        Removes the variable associated with the key 'name' in the print list.
        @param name The associated name.
        @param variable The associated variable.
        """
        # Check if the key is in the dict
        if name in Logger._print_list:
            if variable in Logger._print_list[name]:
                # Check if the variable is the only one in the list.
                if len(Logger._print_list[name]) == 1:
                    # Removes the key.
                    del Logger._print_list[name]

                # If the variable is not the only one, removes it of the print list, but do not remove the key.
                else:
                    for i in range(0, len(Logger._print_list[name])):
                        if Logger._print_list[name][i] is variable:
                            del_index = i

                    Logger._print_list[name].pop(del_index)


    @staticmethod
    def clear_all():
        """
        Clear all data added.
	The registered classes and parameters are maintained.
        """
	for name in Logger._history:
		for i in Logger._history[name]:
			Logger._history[name][i] = []

	print "--- Clearing ch_status" 
        Logger._ch_status = None


    @staticmethod
    def register(name, item, default_value=0):
        """
        Register object to log.
        @param name Object name.
        @param item List/String of items to log.
        @param default_value Default value.
        """
        if not name in Logger._history:
            Logger._history[name] = {}

        if isinstance(item, list):
            for i in item:
                if i not in Logger._history[name]:
                    Logger._history[name][i] = []
        else:
           if item not in Logger._history[name]:
               Logger._history[name][item] = []


    @staticmethod
    def get_data(name, variable):
        """
        Get data from object.
        @param name Name of object.
        @param variable Name of object variable.
        """
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


    @staticmethod
    def append(name, variable, value, ch_status=False):
        """
        Add data.
        @param name Object name.
        @param variable Variable name.
        @param value Value.
        @param ch_status Append global channel status also.
        """

        Logger.register(name, variable)

        # Check if the name and the variable are associated in the print list.
        # If so, print the value.
        if name in Logger._print_list:
            if variable in Logger._print_list[name]:
                print name + ":" + variable + " = " + str(value)

        # Return if log is not enable
        if not Logger._enable:
            return

        if ch_status is None:
            Logger._history[name][variable].append(value)
        else:
            Logger._history[name][variable].append( (value, Logger._ch_status) )


    @staticmethod
    def set(name, variable, value):
        """
        Change previously added data value.
        @param name Object name.
        @param variable Variable name.
        @param value New value.
        """
        if not Logger._enable:
            return

        Logger.register(name, variable)
        Logger._history[name][variable] = value


    @staticmethod
    def dump_plot(direc, subdirec, plot_arr, it):
        """
        Plot a figure.
        @param direc
        @param subdirec
        @param plot_arr Array of tuple. for each tuple:
          - first element: obj_name.
          - second element: array of parameters to plot.
        @param it
        """

        Logger.directory(direc, subdirec)

        # Sanity check
        if not plot_arr:
            return

        # Number of plots:
        t_plots = 0
        for plot in plot_arr:
            obj_name, obj_data = plot

            t_plots += len(obj_data)

        # create plot
        f, axarr = plt.subplots(t_plots, sharex=True)

        # Plots
        cur_idx = 0
        for plot in plot_arr:
            obj_name, obj_data = plot

            for idx, data_name in enumerate(obj_data):
                data = Logger.get_data(obj_name, data_name)

                axarr[cur_idx].plot(range(len(data)), data)
                axarr[cur_idx].set_ylabel(data_name)

                axarr[cur_idx].set_ylim( min(data) - min(data)/100, max(data) + max(data)/100)

                cur_idx += 1

        plt.savefig(direc + subdirec + '/plot_' + str(it) + '.pdf')


    @staticmethod
    def dump(direc, subdirec, it=-1):
        """
        Save all objects.
        @param direc Directory.
        @param subdirec Subdirectory.
        @param it Iterations.
        """
        Logger.directory(direc, subdirec)

        for name in Logger._history:
            print 'Saving object:',  name
            Logger.dump_obj(name=name,
                            data=Logger._history[name],
                            directory=direc + subdirec,
                            it=it)


    @staticmethod
    def dump_obj(name, data, directory, it=-1):
        """
         Dump a single object data.
        @param name Object Name.
        @param data Dictionary of parameters. Parameters is a list of values.
        @param directory Directory to dump data.
        @param it Test Iteration (used do separate repetitions of tests).
        """
        for d in data:
            # Save list
            if isinstance(data[d], list):
                print '\titem: ', d, '[', len(data[d]), ']'
                # File name
                fstr = '/' + name + '_' + d + ('_' + str(it) if it != -1 else '') + '.txt'

                # Create file and dump all items
                with open(directory + fstr, 'w') as fd:
                	fd.write('\n'.join(map(lambda x: str(x), data[d])) + "\n")
		
            # Save global
            else:
                print '\titem: ', d
                fstr = '/' + name + '_global' + ('_' + str(it) if it != -1 else '') + '.txt'

                # Create file and dump all items
                with open(directory + fstr, 'a') as fd:
                	fd.write(d + ':' + str(data[d]) + '\n')


    @staticmethod
    def directory(d, subd):
        """
        Create d and subd directories if necessary.
        @param d Directory.
        @param subd Subdirectory.
        """
        Logger.__lock.acquire(True)
        if not os.path.exists(d):
            os.makedirs(d)
        if not os.path.exists(d + subd):
            os.makedirs(d + subd)
        Logger.__lock.release()
