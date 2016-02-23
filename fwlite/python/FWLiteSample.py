''' FWLite Sample class.
    Implements definition and handling of the TChain.
'''

# Standard imports
import ROOT
import os

#FWLite and CMSSW tools
from DataFormats.FWLite import Events, Handle
from PhysicsTools.PythonAnalysis import *

# Logging
import logging
logger = logging.getLogger(__name__)

# RootTools imports
import RootTools.core.helpers as helpers

@helpers.static_vars(sampleCounter = 0)
def newName():
    result = "FWLiteSample_"+str(newName.sampleCounter)
    newName.sampleCounter += 1
    return result

class FWLiteSample ( object ): 

    def __init__(self, name, files = [],  color = 0, texName = None):
        ''' Base class constructor for all sample classes.
            'name': Name of the sample, 
            'color': ROOT color to be used in plot scripts
            'texName': ROOT TeX string to be used in legends etc.
        '''

        self.name = name
        self.files = files
        if not len(self.files)>0:
          raise helpers.EmptySampleError( "No ROOT files for sample %s! Files: %s" % (sample.name, sample.files) )
 
        self.color = color
        self.texName = texName if not texName is None else name
             
        logger.debug("Created new sample %s with %i files.", name, len(self.files))

        # Loading files into events (FWLite.Events) member
        self.events = Events(files)

    @classmethod
    def fromFiles(cls, name, files,  color = 0, texName = None):
        '''Load sample from files or list of files. If the name is "", enumerate the sample
        '''

        # Work with files and list of files
        files = [files] if type(files)==type("") else files

        # If no name, enumerate them.
        if not name: name = newName()

        sample =  cls(name = name, files = files, color = color, texName = texName)
        return sample

    @classmethod
    def fromDirectory(cls, name, directory, color = 0, texName = None):
        '''Load sample from directory or list of directories. If the name is "", enumerate the sample
        '''
        # Work with directories and list of directories
        directories = [directory] if type(directory)==type("") else directory 

        # If no name, enumerate them.
        if not name: name = newName()

        # find all files
        files = [] 
        for d in directories:
            fileNames = [ os.path.join(d, f) for f in os.listdir(d) if f.endswith('.root') ]
            if len(fileNames) == 0:
                raise helpers.EmptySampleError( "No root files found in directory %s." %d )
            files.extend( fileNames )

        sample =  cls(name = name, files = files, color=color, texName = texName)
        return sample


    def fwliteReader(self, **kwargs):
        ''' Return a FWLiteReader class for the sample
        '''
        from FWLiteReader import FWLiteReader
        logger.debug("Creating FWLiteReader object for sample '%s'.", self.name)
        return FWLiteReader( self, **kwargs )
