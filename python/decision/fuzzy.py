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


#PU and SU presence
LOW_PRESENCE = 0
MEDIUM_PRESENCE = 1
HIGH_PRESENCE = 2
VERY_HIGH_PRESENCE = 3
EXTREME_HIGH_PRESENCE = 4

#Channel classification
VERY_GOOD_CHANNEL = 0
GOOD_CHANNEL = 1
INTERMEDIATE_CHANNEL = 2
BAD_CHANNEL = 3
VERY_BAD_CHANNEL = 4

# Size of the evaluations
SIZE_PRESENCE = 100
SIZE_CHANNEL = 100  # SNR

from abstractDecisionAlgorithm import AbstractDecisionAlgorithm


class UserPresence(object):
    """
    Class for calculations on the user presence.
    """
    def __init__(self):
        """
        CTOR
        """
        pass

    @staticmethod
    def u_low_presence(presence):
        """
        Calculates the user's low presence.
        @param presence The user presence.
        """
        if presence <= 10:
            u = 1
        elif presence > 20:
            u = 0
        else:
            u = 1 - float((presence - 11)) / 10
        return u

    @staticmethod
    def u_medium_presence(presence):
        """
        Calculates the user's medium presence.
        @param presence The user presence.
        """
        if presence < 20:
            u = 0
        elif presence < 30:
            u = float((presence - 19)) / 10
        elif presence == 30:
            u = 1
        elif presence < 40:
            u = 1 - float((presence - 30)) / 10
        else:  # presence >= 40
            u = 0
        return u

    @staticmethod
    def u_high_presence(presence):
        """
        Calculates the user's high presence.
        @param presence The user presence.
        """
        if presence < 40:
            u = 0
        elif presence < 50:
            u = float((presence - 39)) / 10
        elif presence == 50:
            u = 1
        elif presence < 60:
            u = 1 - float((presence - 50)) / 10
        else:  # presence >= 60
            u = 0
        return u

    @staticmethod
    def u_very_high_presence(presence):
        """
        Calculates the user's very high presence.
        @param presence The user presence.
        """
        if presence < 60:
            u = 0
        elif presence < 70:
            u = float((presence - 59)) / 10
        elif presence == 70:
            u = 1
        elif presence < 80:
            u = 1 - float((presence - 70)) / 10
        else:  # presence >= 80
            u = 0
        return u

    @staticmethod
    def u_extreme_high_presence(presence):
        """
        Calculates the user's extreme high presence.
        @param presence The user presence.
        """
        if presence < 80:
            u = 0
        elif presence >= 90:
            u = 1
        else:
            u = 1 - float((presence - 80)) / 10
        return u


class ChannelClassification(object):
    """
    Class for channel classifications.
    """
    def __init__(self):
        """
        CTOR
        """
        pass


    # Channel classification pertinence functions.

    @staticmethod
    def u_very_good_channel(channel):
        """
        Classification as 'very good channel'.
        @param channel
        """
        if channel <= 10:
            u = 1
        elif channel > 20:
            u = 0
        else:
            u = 1 - float((channel - 11)) / 10
        return u

    @staticmethod
    def u_good_channel(channel):
        """
        Classification as 'good channel'.
        @param channel
        """

        if channel < 20:
            u = 0
        elif channel < 30:
            u = float((channel - 19)) / 10
        elif channel == 30:
            u = 1
        elif channel < 40:
            u = 1 - float((channel - 30)) / 10
        else:  # presence >= 40
            u = 0
        return u

    @staticmethod
    def u_intermediate_channel(channel):
        """
        Classification as 'intermediate channel'.
        @param channel
        """
        if channel < 40:
            u = 0
        elif channel < 50:
            u = float((channel - 39)) / 10
        elif channel == 50:
            u = 1
        elif channel < 60:
            u = 1 - float((channel - 50)) / 10
        else:  # presence >= 60
            u = 0

        return u

    @staticmethod
    def u_bad_channel(channel):
        """
        Classification as 'bad channel'.
        @param channel
        """
        if channel < 60:
            u = 0
        elif channel < 70:
            u = float((channel - 59)) / 10
        elif channel == 70:
            u = 1
        elif channel < 80:
            u = 1 - float((channel - 70)) / 10
        else:  # presence >= 80
            u = 0
        return u

    @staticmethod
    def u_very_bad_channel(channel):
        """
        Classification as 'very bad channel'.
        @param channel
        """

        if channel < 80:
            u = 0
        elif channel >= 90:
            u = 1
        else:
            u = 1 - float((channel - 80)) / 10
        return u


class Fuzzy(AbstractDecisionAlgorithm):
    """
    Fuzzy decision algorithm.
    """
    def __init__(self):
        """
        CTOR
        """
        AbstractDecisionAlgorithm.__init__(self)

    @staticmethod
    def fuzzify(presence, u_user_presence):
        """
        Fuzzifier.
        @param presence
        @param u_user_presence
        @return The user presence.
        """
        u_user_presence[LOW_PRESENCE] = UserPresence.u_low_presence(presence)
        u_user_presence[MEDIUM_PRESENCE] = UserPresence.u_medium_presence(presence)
        u_user_presence[HIGH_PRESENCE] = UserPresence.u_high_presence(presence)
        u_user_presence[VERY_HIGH_PRESENCE] = UserPresence.u_very_high_presence(presence)
        u_user_presence[EXTREME_HIGH_PRESENCE] = UserPresence.u_extreme_high_presence(presence)

        return u_user_presence


    @staticmethod
    def evaluate_rules(u_user_presence, u_channel_classification):
        """
        Evaluate rules.
        @param u_user_presence
        @param u_channel_classification
        @return
        """
        if u_user_presence[LOW_PRESENCE] >= 0:
            u_channel_classification[VERY_GOOD_CHANNEL] = u_user_presence[LOW_PRESENCE]
        else:
            u_channel_classification[VERY_GOOD_CHANNEL] = 0

        if u_user_presence[MEDIUM_PRESENCE] >= 0:
            u_channel_classification[GOOD_CHANNEL] = u_user_presence[MEDIUM_PRESENCE]
        else:
            u_channel_classification[GOOD_CHANNEL] = 0

        if u_user_presence[HIGH_PRESENCE] >= 0:
            u_channel_classification[INTERMEDIATE_CHANNEL] = u_user_presence[HIGH_PRESENCE]
        else:
            u_channel_classification[INTERMEDIATE_CHANNEL] = 0

        if u_user_presence[VERY_HIGH_PRESENCE] >= 0:
            u_channel_classification[BAD_CHANNEL] = u_user_presence[VERY_HIGH_PRESENCE]
        else:
            u_channel_classification[BAD_CHANNEL] = 0

        if u_user_presence[EXTREME_HIGH_PRESENCE] >= 0:
            u_channel_classification[VERY_BAD_CHANNEL] = u_user_presence[EXTREME_HIGH_PRESENCE]
        else:
            u_channel_classification[VERY_BAD_CHANNEL] = 0

        return u_channel_classification


    @staticmethod
    def defuzzify(u_channel_classification):
        """
        Defuzzifier.
        @param u_channel_classification
        @return The channel classification.
        """
        numerator = 0.0
        divisor = 0.0
        channel_classification = 0.0
        result_set = [0.0 for i in range(SIZE_CHANNEL)]

        if u_channel_classification[VERY_GOOD_CHANNEL] > 0:
            for i in range(SIZE_CHANNEL):
                u_aux = ChannelClassification.u_very_good_channel(i)
                if u_aux > u_channel_classification[VERY_GOOD_CHANNEL]:
                    u_aux = u_channel_classification[VERY_GOOD_CHANNEL]
                if u_aux > result_set[i]:
                    result_set[i] = u_aux

        if u_channel_classification[GOOD_CHANNEL] > 0:
            for i in range(SIZE_CHANNEL):
                u_aux = ChannelClassification.u_good_channel(i)
                if u_aux > u_channel_classification[GOOD_CHANNEL]:
                    u_aux = u_channel_classification[GOOD_CHANNEL]
                if u_aux > result_set[i]:
                    result_set[i] = u_aux

        if u_channel_classification[INTERMEDIATE_CHANNEL] > 0:
            for i in range(SIZE_CHANNEL):
                u_aux = ChannelClassification.u_intermediate_channel(i)
                if u_aux > u_channel_classification[INTERMEDIATE_CHANNEL]:
                    u_aux = u_channel_classification[INTERMEDIATE_CHANNEL]
                if u_aux > result_set[i]:
                    result_set[i] = u_aux

        if u_channel_classification[BAD_CHANNEL] > 0:
            for i in range(SIZE_CHANNEL):
                u_aux = ChannelClassification.u_bad_channel(i)
                if u_aux > u_channel_classification[BAD_CHANNEL]:
                    u_aux = u_channel_classification[BAD_CHANNEL]
                if u_aux > result_set[i]:
                    result_set[i] = u_aux

        if u_channel_classification[VERY_BAD_CHANNEL] > 0:
            for i in range(SIZE_CHANNEL):
                u_aux = ChannelClassification.u_very_bad_channel(i)
                if u_aux > u_channel_classification[VERY_BAD_CHANNEL]:
                    u_aux = u_channel_classification[VERY_BAD_CHANNEL]
                if u_aux > result_set[i]:
                    result_set[i] = u_aux

        # Centroid: center of mass calculation
        # From the uniom of the fuzzy sets to the channel classification
        for i in range(SIZE_CHANNEL):
            numerator = numerator + result_set[i] * i

        for i in range(SIZE_CHANNEL):
            divisor = divisor + result_set[i]

        channel_classification = float(numerator) / divisor
        return channel_classification


    def evaluate(self, data):
        """
        Evaluates the decision algorithm.
        @param data A dictionary with the parameters used by the algorithm.
        """
        pu_weight = 0.6
        pu_weight = 0.3
        pu_weight = 0.1

        evalf_pu = []
        evalf_su = []

        for pu_per in data[self.CHANNEL_PU_PRESENCE]:
            pu_list = [0] * 5
            classification = [0] * 5

            Fuzzy.fuzzify(pu_per, pu_list)
            Fuzzy.evaluate_rules(pu_list, classification)

            val = Fuzzy.defuzzify(classification)

            evalf_pu.append(val)

        for su_per in data[self.CHANNEL_SU_PRESENCE]:
            su_list = [0] * 5
            classification = [0] * 5

            Fuzzy.fuzzify(su_per, su_list)
            Fuzzy.evaluate_rules(su_list, classification)

            val = Fuzzy.defuzzify(classification)
            evalf_su.append(val)

        channel_eval = []
        for pu_val, su_val in zip(evalf_pu, evalf_su):
            final_val = pu_val * pu_weight + su_val * (1 - pu_weight)
            channel_eval.append(final_val)

        return channel_eval
