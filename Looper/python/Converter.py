''' Class for a Converting of a Sample (Need better name)?
So far this is only a reader ... working on it.
'''

# Standard imports
import ROOT
import uuid
import copy
import os

# Logging
import logging
logger = logging.getLogger(__name__)

# RootTools
from RootTools.Looper.LooperBase import LooperBase

class Converter( LooperBase ):

    def __init__(self, sample, scalars, vectors, selectionString = None):

        super(Converter, self).__init__( sample = sample, scalars = scalars, vectors = vectors , selectionString = selectionString)

        # Internal state for running
        self.selectionString = selectionString
        self.eList = None
        self.position = -1
        self.nEvents = None

    def run(self):
        ''' Load event into self.entry. Return 0, if last event has been reached
        '''
        if self.position < 0:
            logger.debug("Starting Converter for sample %s", self.sample.name)
            self.__start()
            self.position = 0
        else:
            self.position += 1
        if self.position == self.nEvents: return 0

        if (self.position % 1000)==0:
            logger.info("Converter for sample %s is at position %6i/%6i", self.sample.name, self.position, self.nEvents)

        # point to the position in the chain (or the eList if there is one)
        self.sample.chain.GetEntry ( self.eList.GetEntry( self.position ) ) if self.eList else self.sample.chain.GetEntry(self.position)

        return 1
