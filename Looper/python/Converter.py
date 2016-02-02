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

        self.makeClass( "output" )

        # self.setAddressestosometree

    def execute(self):
        ''' Do what a converter does'''
        # point to the position in the chain (or the eList if there is one)
#        self.sample.chain.GetEntry ( self.eList.GetEntry( self.position ) ) if self.eList else self.sample.chain.GetEntry(self.position)
        return

