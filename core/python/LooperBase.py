''' Abstract Class for a looping over an instance of Sample.
'''
#Abstract Base Class
import abc

# Standard imports
import ROOT
import uuid
import copy
import os

# Logging
import logging
logger      = logging.getLogger(__name__)

# RootTools
from RootTools.core.LooperHelpers import createClassString
from RootTools.core.TreeVariable import TreeVariable, ScalarTreeVariable, VectorTreeVariable

class LooperBase( object ):
    __metaclass__ = abc.ABCMeta

    def __init__(self):

        # Internal state for running
        self.position = -1

    def start(self):
        ''' Call before starting a loop.
        '''
        logger.debug("Starting to run.")
        self._initialize()

    def run(self, **kwargs):
        ''' Incrementing the loop.
            Load event into self.entry. Return 0, if last event has been reached
        '''

        assert self.position>=0, "Not initialized!"
        success = self._execute( **kwargs )

        self.position += 1

        return success

    @abc.abstractmethod
    def _initialize(self):
        return

    @abc.abstractmethod
    def _execute(self):
        return
