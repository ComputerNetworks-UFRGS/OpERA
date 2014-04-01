__author__ = 'jtsreinaldo'

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

from abstractDecisionAlgorithm import AbstractDecisionAlgorithm


class Graph(AbstractDecisionAlgorithm):
    """
    Graph decision algorithm class.
    """

    def __init__(self):
        """
        CTOR
        """

        AbstractDecisionAlgorithm.__init__(self)
        self._int_matrix = None
        self.graph = None
        self.matching = []

    def calc_possible_shares(self, data):
        """
        @param data A dictionary with the parameters used by the algorithm.
        """

        possible_shares = []

        self._int_matrix = data[self.INTERFERENCE_MATRIX]
        self.graph = data[self.UTILITY_MATRIX]

        for i in range(len(self._int_matrix)):
            for j in range(len(self._int_matrix[i])):
                if (j != i) and (self._int_matrix[i][j] == 0):
                    possible_shares.append([i, j])

        stack = []

        for i in range(len(self._int_matrix)):
            stack.append(i)

            for j in possible_shares:
                if i == j[0]:
                    stack.append(j[1])

            elem_to_remove = []
            for k in stack:
                m = k + 1
                while m <= len(stack):
                    if (m in stack) and (self._int_matrix[k][m] == 1):
                        elem_to_remove.append(m)
                    m += 1

            for l in elem_to_remove:
                if l in stack:
                    stack.remove(l)
            if len(stack) > 2:
                possible_shares.append(stack)

            stack = []

        a = []
        for i in possible_shares:
            i.sort()
            if not (i in a):
                a.append(i)

        possible_shares = sorted(a)

        for i in range(6):
            possible_shares.append([i])

        return possible_shares

    def remove_allocated(self, possible_shares, index):
        """
        Remove the values passed as a parameter.
        @param possible_shares The values to remove.
        @param index
        """

        values_to_remove = possible_shares
        possible_shares.remove(values_to_remove)


    def evaluate(self, data):
        """
        Executes the decision algorithm.
        @param data A dictionary with the parameters used by the algorithm.
        """

        possible_freqs = data[self.POSSIBLE_FREQUENCIES]
        possible_links = data[self.POSSIBLE_LINKS]

        self._int_matrix = data[self.INTERFERENCE_MATRIX]
        self.graph = data[self.UTILITY_MATRIX]

        possible_shares = possible_links

        result = []

        dict_links_to_freq = {}

        while possible_freqs and possible_shares:

            utility_vector = []

            for link in possible_shares:

                util = -1
                f = -1

                for freq in possible_freqs:
                    sum_ = self.graph[link][freq]

                    if sum_ > util:
                        util = sum_
                        f = freq

                utility_vector.append([util, f])

            max_utility = max(utility_vector)

            index = utility_vector.index(max_utility)

            links = possible_shares[index]

            dict_links_to_freq[links] = max_utility[1]

            possible_shares.pop(index)
            possible_freqs.remove(max_utility[1])

        return dict_links_to_freq


def main():

    # Constants used in the 'data' dictionary:
    INTERFERENCE_MATRIX = 9
    UTILITY_MATRIX = 11
    POSSIBLE_LINKS = 12
    POSSIBLE_FREQUENCIES = 13

    utility_matrix = [[4, 3, 1, 10], [10, 5, 2, 6], [3, 6, 1, 4], [1, 6, 3, 1], [4, 5, 1, 3], [3, 0, 6, 11]]
    interference_matrix = [[1, 1, 1, 1, 1, 1] * 6]

    data = {}
    data[UTILITY_MATRIX] = utility_matrix
    data[INTERFERENCE_MATRIX] = interference_matrix
    data[POSSIBLE_FREQUENCIES] = [0, 1, 2, 3]
    data[POSSIBLE_LINKS] = [2]

    G = Graph()
    l = G.evaluate(data)

    print(l)

if __name__ == '__main__':
    main()