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

import random as rd
import numpy as np
from array import *
from utils import Logger
from algorithm.abstractAlgorithm import AbstractAlgorithm


# This is my Enum. Shining!!!
class Actions:
    DECR = -1
    HOLD = 0
    INCR = 1


class SARSA(AbstractAlgorithm):
    """

    """
    def __init__(self, alpha=0.3, gamma=1.0, epsilon=0.1, verbose=False,
                 min_th=0.0, max_th=100.0, delta_th=1.0):
        """
        CTOR
        @param alpha
        @param gamma
        @param epsilon Probability of executing a random action
        @param verbose
        @param min_th The lowest threshold
        @param max_th The highest threshold
        @param delta_th
        """

        #  "The learning rate determines to what extent the newly
        #  acquired information will override the old information. A factor of 0
        #  will make the agent not learn anything, while a factor of 1 would make
        #  the agent consider only the most recent information."
        self.alpha = float(alpha)

        # According to Wikipedia: "The discount factor determines the importance
        # of future rewards. A factor of 0 will make the agent "opportunistic" by only
        # considering current rewards, while a factor approaching 1 will make it
        # strive for a long-term high reward."
        self.gamma = float(gamma)

        # Probabilidade de executar uma acao randomicamente.
        # Probability of executing a random action
        self.epsilon = float(epsilon)

        #
        self.verbose = verbose

        # min_th is the lowest threshold
        self.min_th = min_th

        # max_th is the highest threshold
        self.max_th = max_th

        # gap is the... gap between states, so, the number of states
        #  will be (max_th - min_th) / gap
        self.gap = delta_th

        # The feedback
        self._feedback = 0.0

        # Number of Increase Actions in sequence
        self.action_i = 0
        # Number of Decrease Actions in sequence
        self.action_d = 0

        # Set to '1' when a feedback is received
        self.feedback_received = True

        # Count how many feedbacks are received by the algorithm.
        # Used only for info gathering
        self.feedback_counter = 0

        #
        self.cycle_counter = 0
        self.cycle_counter_max = int(406383 / 8)

        # Execution Time of this class
        self.m_time = 0.0

        # Enum for actions
        self.action = Actions()

        # Load in self.actions the possible actions
        self.actions = self.get_action_list()
        # Load in self.states the possible actions
        self.states = self.get_state_list()

        # How many states?
        self.nstates = len(self.states)
        # Max jump
        self.max_jump = int(self.nstates / 50)

        # Map the threshold value to the index of this threshold in self.states
        self.state_map = {'0.0': 0}
        for i in range(self.nstates):
            self.state_map[self.states[i]] = i

        # How many actions I'm using?
        self.nactions = len(self.actions)

        # Build an empty q_table with size (nactions * nstates)
        self.q_table = self.build_q_table()

        # Guess what?
        self.s = self.get_initial_state()
        self.a = self.e_greedy_selection(self.s)

        # May be messy
        if self.verbose:
            self.print_q_table()

        Logger.register('bayes_learning', ['hypothesis', 'feedback', 'state', 'reward', 'action'])


    def print_q_table(self):
        """
        """
        for i in range(self.nstates):
            print "%.4f  %s" % (self.states[i], self.q_table[i])


    def finish(self):
        """
        Print the results.
        """
        print "SARSA Time: %.4f" % (self.m_time)
        print "States: %d [%.2f, %.2f, %.6f]" % (self.nstates, self.min_th, self.max_th, self.gap)
        print 'Received ' + str(self.feedback_counter) + ' feedbacks'
        print 'Alpha: ' + str(self.alpha)
        print 'Gamma: ' + str(self.gamma)
        print "Epsilon: %.4f" % (self.epsilon)


    @property
    def feedback(self):
        """
        Feedback property getter
        @ret _feedback
        """
        return self._feedback

    @feedback.setter
    def feedback(self, val):
        """
        Feedback property setter
        @param val New feedback value
        """
        self._feedback = val
        self.feedback_received = True
        self.feedback_counter += 1


    # Defined Actions:
    #	-1: Decrease threshold
    #	 0: Keep threshold
    #	 1: Increase threshold
    def get_action_list(self):
        """
        """
        return array('i', [self.action.DECR, self.action.HOLD, self.action.INCR])


    def get_state_list(self):
        """
        Generate State List
        """
        # Min to Max with the gap
        return np.arange(self.min_th, self.max_th, self.gap)


    def get_initial_state(self):
        """
        @return The first state.
        """
        # Last element. Believe it.
        #return self.states[ -1 ]
        # Starting from the middle.
        #return self.states[ int( self.nstates/2 ) ]
        # Lowest threshold, Bayes mode
        return self.states[0]


    def build_q_table(self):
        """
        """
        # Filled with zeros
        return [[0 for i in range(self.nactions)] for i in range(self.nstates)]


    def get_best_action(self, state):
        """
        @param state
        """
        # Get the line corresponding to the state
        state_row = self.q_table[self.state_map[state]]
        # Get action with more rewards ...
        max_val = max(state_row)
        # and get the index of this action
        max_val_idx = state_row.index(max_val)

        if self.verbose:
            print state_row
            print "max_val: %.4f  Idx: %d\n" % (max_val, max_val_idx)

        return max_val_idx


    def e_greedy_selection(self, state):
        """
        Chooses an action for the given state
        @param state
        """

        idx = 0

        # Higher probability. Get the action with more rewards.
        if rd.random() > self.epsilon:
            idx = self.get_best_action(state)
        else:
            # Randomly chosen action
            idx = rd.randint(0, self.nactions - 1)

        return self.actions[idx]


    def do_action(self, state, action):
        """

        @param state
        @param action
        """

        final_state_index = cur_idx = self.state_map[state]

        if action == self.action.HOLD:
            #self.action_i = 0
            #self.action_d = 0
            pass

        elif action == self.action.DECR:
            self.action_i = 0
            self.action_d += 1

            state_jump = min(self.action_d, self.max_jump)

            final_state_index = max(0, cur_idx - state_jump)

        elif action == self.action.INCR:
            self.action_i += 1
            self.action_d = 0

            state_jump = min(self.action_i, self.max_jump)

            final_state_index = min(self.nstates - 1, cur_idx + state_jump)

        return self.states[final_state_index]


    def get_reward(self, energy, state):
        """

        @param energy
        @param state
        """

        if self.feedback_received == False:
            return 0
        self.feedback_received = False

        rw = 0
        my_decision = 0

        if energy > state:
            # Occupied
            my_decision = 1
        else:
            # Busy
            my_decision = 0

        if self._feedback != my_decision:
            rw = -100
        else:
            rw = 10

        return rw


    def update_q_table(self, s, a, rw, sp, ap):
        """

        @param s
        @param a
        @param rw
        @param sp
        @param ap
        """

        # Index of current state
        state_idx = self.state_map[s]
        # Index of next state
        next_state_idx = self.state_map[sp]
        # Index of current action
        act_idx = self.actions.index(a)
        # Index of next action
        next_act_idx = self.actions.index(ap)
        # Current value in q_table
        cur_val = self.q_table[state_idx][act_idx]
        # q_table value corresponding to the next state and action
        next_val = self.q_table[next_state_idx][next_act_idx]
        # Update current value
        self.q_table[state_idx][act_idx] += self.alpha * (rw + self.gamma * next_val - cur_val)


    def decision(self, energy):
        """

        @param energy
        """
        energy = np.sum(energy) / energy.size

        self.cycle_counter += 1

        if self.cycle_counter_max == self.cycle_counter:
            self.cycle_counter = 0

        sp = self.do_action(self.s, self.a)
        rw = self.get_reward(energy, sp)
        ap = self.e_greedy_selection(sp)

        self.update_q_table(self.s, self.a, rw, sp, ap)

        self.s = sp
        self.a = ap

        #self.epsilon *= 0.999

        Logger.append('bayes_learning', 'hypothesis', 1.0 if energy > self.s else 0.0)
        Logger.append('bayes_learning', 'feedback', self._feedback)
        Logger.append('bayes_learning', 'state', self.s)
        Logger.append('bayes_learning', 'reward', rw)
        Logger.append('bayes_learning', 'action', self.a)

        return 1 if (energy > sp) else 0, energy
