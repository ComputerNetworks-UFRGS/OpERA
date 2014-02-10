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

# Scheduler needds the logging module. REF: http://stackoverflow.com/questions/17528363/no-handlers-could-be-found-for-logger-apscheduler-scheduler
import logging
logging.basicConfig()

from apscheduler.scheduler import Scheduler

# ::TODO:: OpERABase como superclasse de todas as superclasses do OpERA.
# ::TODO:: fazer os inits das superclasses do jeito "moderno":  http://stackoverflow.com/questions/2399307/python-invoke-super-constructor (ver comentario do ignacio)

class OpERABase(object):
    """
    The OpERABase is the base class of all other class.
    """

    "Schedule events"
    _scheduler = Scheduler()
    _scheduler.start()

    def __init__(self, name="OpERABase"):

        #check if it is necessary.
        self._name = name


    def register_scheduling(self, func, delay_sec, *args, **kwargs):
        """
        Register a funtion for scheduling.
        @param func Function to be scheduled.
        @param delay_sec Interval between func calls.
        @param *args args forwarded to fun.
        @param **kwargs kwargs forwarded to fun
        """
        OpERABase._scheduler.add_interval_job(func, seconds = delay_sec, args = args, kwargs = kwargs)
