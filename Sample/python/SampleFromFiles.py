'''Sample constructed from a list of files.
Derived from SampleBase'''

# Standard imports
import ROOT
import os, subprocess

# Logging
import logging
logger = logging.getLogger(__name__)

# Base class
from  RootTools.Sample.SampleBase import SampleBase, EmptySampleError

# Helpers
import RootTools.tools.helpers as helpers

class SampleFromFiles( SampleBase ):

    def __init__(self, name, files, treeName = 'Events', maxN = None):

        super(SampleFromFiles, self).__init__(name=name, treeName = treeName)

        self.maxN = maxN if not (maxN and maxN<0) else None 

        # Adding and checking files
        for filename in files: 
            if not helpers.checkRootFile(filename, checkForObjects=[treeName] ):
                logger.warning( "Could not read file %s",  filename )
            else:
                self.files.append(filename)

        # Don't allow empty samples
        if len(self.files) == 0: 
            raise EmptySampleError("No valid file found for sample {0}.".format(self.name) )

        logger.info("Loaded SampleFromFiles %s. Total number of files : %i. Bad files: %i.", \
                     self.name, len(files), len(files)-len(self.files) ) 
