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

## The class verifies if the parameters are as expected.
class Verify(object):
    def __init__():
        pass

    # Receives a parameter and a tuple of values, representing the range on which the parameter should be
    # values compose a closed interval
    @staticmethod
    def _check_range_of_values(parameter, range_of_values):

        min_value = range_of_values[0]
        max_size = len(range_of_values) -1
        max_value = range_of_values[max_size]

        if min_value <= parameter and parameter <= max_value:
            return True
        else:
            return False

    # Check if the parameter is in a set of values.
    @staticmethod
    def _check_set_of_values(parameter, set_of_values):
        parameter_ok = True

        for value in set_of_values:
            if parameter == value:
                return parameter_ok

        return False        



    # Parameters and expected_values are lists.
    # Returns a bool (True if all parameters are ok, False otherwise) and a list with the index of the wrong parameters.
    @staticmethod
    def check_parameters(parameters, expected_values):
        possible_numbers = (int, long, float, complex)
        parameters_ok = True

        list_of_errors = []

        if len(parameters) == len(expected_values):
            for i in range(0, len(parameters)):

                # The parameter is a number, so we must verify if it is in a set or range of values.
                if isinstance(parameters[i], possible_numbers):

                    # If expected_values[i] is a tuple, then the parameter must be in a range of numbers.
                    if isinstance(expected_values[i], tuple):
                        range_ok = Verify._check_range_of_values(parameters[i], expected_values[i])
                        if range_ok is False:
                            parameters_ok = False
                            list_of_errors.append(i)

                    # If expected_values[i] os a list, then the parameter must be in a set of given numbers.
                    elif isinstance(expected_values[i], list):
                        set_ok = Verify._check_set_of_values(parameters[i], expected_values[i])
                        if set_ok is False:
                            parameters_ok = False
                            list_of_errors.append(i)

                    # If it is not either a tuple or a list, the type is wrong.
                    else:
                        parameters_ok = False

                # The parameter is an instance of some class.
                else:
                    if not isinstance(parameters[i], expected_values[i]):
                        parameters_ok = False
                        list_of_errors.append(i)

        # If the size of the two lists is not the same, something is wrong.
        else:
            parameters_ok = False
            print "ERROR: the two list do not have the same size!"

        return list_of_errors, parameters_ok


    @staticmethod
    def check_parameters_ok(parameters, expected_values):
        return Verify.check_parameters(parameters, expected_values)[1]
