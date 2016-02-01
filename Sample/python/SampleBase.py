''' Base class for a sample.
    Implements definition and handling of the TChain.
'''

#Abstract Base Class
import abc

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

class SampleBase ( object ): # 'object' argument will disappear in Python 3
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, name, treeName ):
        ''' Base class constructor for all sample classes.
            name: Name of the sample, treeName: name of the TTree in the input files'''
        self.name = name
        self.treeName = treeName
        self.files = []
        self.__logger = logging.getLogger("Logger."+__name__)
        self.__logger.debug("Created new sample %s with treeName %s.", name, treeName)

# Overloading getattr: Requesting sample.chain prompts the loading of the TChain.
    def __getattr__(self, name):
        if name=="chain":
            self.__logger.debug("First request of attribute 'chain' for sample %s. Calling __loadChain", self.name)
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
                self.__logger.debug("Now adding file %s to sample '%s'", f, self.name)
                try:
                    if helpers.checkRootFile(f, checkForObjects=[self.treeName]):
                        self.chain.Add(f)
                        counter+=1
                except IOError:
                    pass
                    self.__logger.warning( "Could not load file %s", f )
            self.__logger.debug( "Loaded %i files for sample '%s'.", counter, self.name )

    def clear(self): #FIXME How to promote to destructor without making it segfault?
        if self.chain:
            self.chain.IsA().Destructor( self.chain )
            self.chain = None
            self.__logger.debug("Called TChain Destructor for sample '%s'.", self.name)


#    def __del__(self): #Will be executed when the refrence count is zero
#        '''Calling the TChain Destructor.
#        '''
#        self.clear()
