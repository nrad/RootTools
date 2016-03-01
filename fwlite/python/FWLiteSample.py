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
          raise helpers.EmptySampleError( "No ROOT files for self %s! Files: %s" % (self.name, self.files) )
 
        self.color = color
        self.texName = texName if not texName is None else name
             
        logger.debug("Created new sample %s with %i files.", name, len(self.files))

        # Loading files into events (FWLite.Events) member
        self.events = Events(files)

    @classmethod
    def fromFiles(cls, name, files,  color = 0, texName = None, maxN = None):
        '''Load sample from files or list of files. If the name is "", enumerate the sample
        '''

        # Work with files and list of files
        files = [files] if type(files)==type("") else files

        # restrict files 
        maxN = maxN if maxN is not None and maxN>0 else None
        files = files[:maxN]

        # If no name, enumerate them.
        if not name: name = newName()

        sample =  cls(name = name, files = files, color = color, texName = texName)
        return sample

    @classmethod
    def fromDirectory(cls, name, directory, color = 0, texName = None, maxN = None):
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

        # restrict files 
        maxN = maxN if maxN is not None and maxN>0 else None
        files = files[:maxN]

        sample =  cls(name = name, files = files, color=color, texName = texName)
        return sample

    @classmethod
    def fromDAS(cls, name, dataset, instance = 'global', prefix='root://xrootd.unl.edu/', maxN = None):
        ''' Make sample from DAS. 
        '''
        # https://github.com/CERN-PH-CMG/cmg-cmssw/blob/0f1d3bf62e7ec91c2e249af1555644b7f414ab50/CMGTools/Production/python/dataset.py#L437

        def _dasPopen(dbs):
            if 'LSB_JOBID' in os.environ:
                raise RuntimeError, "Trying to do a DAS query while in a LXBatch job (env variable LSB_JOBID defined)\nquery was: %s" % dbs
            if 'X509_USER_PROXY' in os.environ:
                dbs += " --key {0} --cert {0}".format(os.environ['X509_USER_PROXY'])
            logger.info('DAS query\t: %s',  dbs)
            return os.popen(dbs)

        sampleName = dataset.rstrip('/')
        query, qwhat = sampleName, "dataset"
        if "#" in sampleName: qwhat = "block"

        maxN = maxN if maxN is not None and maxN>0 else None
        limit = maxN if maxN else 0

        dbs='das_client.py --query="file %s=%s instance=prod/%s" --limit %i'%(qwhat,query, instance, limit)
        dbsOut = _dasPopen(dbs).readlines()
        
        files = []
        for line in dbsOut:
            if line.find('/store')==-1:
                continue
            line = line.rstrip()
            files.append(prefix+line)

        return cls(name, files=files)


    def fwliteReader(self, **kwargs):
        ''' Return a FWLiteReader class for the sample
        '''
        from FWLiteReader import FWLiteReader
        logger.debug("Creating FWLiteReader object for sample '%s'.", self.name)
        return FWLiteReader( self, **kwargs )
