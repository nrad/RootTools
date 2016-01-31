''' Base class for a sample.
    Implements definition and handling of the TChain. 
'''

# Standard imports
import ROOT

# Logging
import logging

# RootTools imports
import RootTools.tools.helpers as helpers


class EmptySampleError(Exception):
    '''Accessing a sample without ROOT files.
    '''
    pass

class Sample:

    def __init__(self, name, treeName = "Events", files=[]):
        self.name = name
        self.treeName = treeName
        self.files = files
        self.logger = logging.getLogger("Logger."+__name__)
        self.logger.info("Created new sample %s with treeName %s.", name, treeName)

# Overloading getattr: Requesting sample.chain prompts the loading of the TChain.
    def __getattr__(self, name):
        if name=="chain":
            self.logger.debug("First request of attribute 'chain' for sample %s. Calling __loadChain", self.name)
            self.__loadChain() 
            return self.chain
        else:
            raise AttributeError

# "Private" method that loads the chain from self.files 
    def __loadChain(self):
        if len(self.files) == 0:
            raise EmptySampleError("Sample {name} has no input files! Can not load.".format(name = self.name) )
        else:
            self.chain = ROOT.TChain(self.treeName)
            counter = 0
            for f in self.files:
                self.logger.debug("Now adding file %s to sample '%s'", f, self.name)
                try:
                    if helpers.checkRootFile(f, checkForObjects=[self.treeName]):
                        self.chain.Add(f)
                        counter+=1
                except IOError:
                    pass
                    self.logger.warning( "Could not load file %s", f )
            self.logger.info( "Loaded %i files for sample '%s'.", counter, self.name )

## FIXME This should really be doable?
#    def __del__(self):
#        '''Calling the TChain Destructor.
#        '''
#        if self.chain:
#            try:
#                self.chain.IsA().Destructor(self.chain)
#            except:
#                pass

#    @abc.abstractmethod
#    def load(self) 
