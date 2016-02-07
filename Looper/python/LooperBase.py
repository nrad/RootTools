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
logger = logging.getLogger(__name__)

# RootTools
from RootTools.Looper.LooperHelpers import createClassString
from RootTools.Variable.Variable import Variable, ScalarType, VectorType

class LooperBase( object ):
    __metaclass__ = abc.ABCMeta

    def __init__(self, variables, addVectorCounters = True):

        if not type(variables) == type([]):
            raise ValueError( "Argument 'variables' must be list. Got '%r'"%variables )
        if not all (isinstance(v, Variable) for v in variables):
            raise ValueError( "Not all elements in variable list are instances of Variable. Got '%r'"%variables )

        self.variables = variables

        # directory where the class is compiled
        self.tmpDir = '/tmp/'

        # Internal state for running
        self.position = -1
        self.eList = None

        # FIXME Could use to identify the sample ... alternatively overload __hash__
        self.classUUID = None
        # Whether or not to add default counter variables 'nVector/I' for vectors
        self.addVectorCounters = addVectorCounters

    def _allBranchInfo( self, restrictType = None):
        ''' Get a list of the form [(var, type), (vectorComponent, type, counterName)...] for all branches which is
            neededfor handling the branches.
        '''
        res = []
        for s in self.variables:
            if isinstance(s, ScalarType):
                if not restrictType or restrictType == ScalarType:
                    res.append( (s.name, s.type, None) )
            elif isinstance(s, VectorType):
                tmp = s.counterVariable()
                for c in s.components:
                    if not restrictType or restrictType == VectorType:
                        res.append( ( '%s_%s'%( s.name, c.name ), c.type, tmp.name) )
                if self.addVectorCounters: 
                    if not restrictType or restrictType == ScalarType:
                        res.append( (tmp.name, tmp.type, None) )
            else: raise ValueError( "This should never happen. Found an element in self.variables that is not a ScalarType or VectorType instance: '%r'"%s )
        return res

    def makeClass(self, attr, useSTDVectors = False):

        if not os.path.exists(self.tmpDir):
            logger.info("Creating %s directory for temporary files for class compilation.", self.tmpDir)
            os.path.makedirs(self.tmpDir)

        # Recall the uuid of the compilation for the __hash__ method which we use to identify readers when plotting over multiple samples
        self.classUUID = str(uuid.uuid4()).replace('-','_')

        tmpFileName = os.path.join(self.tmpDir, self.classUUID+'.C')
        className = "Class_"+self.classUUID

        with file( tmpFileName, 'w' ) as f:
            logger.debug("Creating temporary file %s for class compilation.", tmpFileName)
            f.write(
                createClassString( variables = self.variables, useSTDVectors = useSTDVectors, addVectorCounters = self.addVectorCounters)
                .replace( "className", className )
            )

        # A less dirty solution possible?
        logger.debug("Compiling file %s", tmpFileName)
        ROOT.gROOT.ProcessLine('.L %s+'%tmpFileName )

        logger.debug("Importing class %s", className)
        exec( "from ROOT import %s" % className )

        logger.debug("Creating instance of class %s", className)
        setattr(self, attr, eval("%s()" % className) )

        return self

    def start(self):
        ''' Call before starting a loop.
        '''
        logger.debug("Starting to run.")
        self._initialize()

    def run(self):
        ''' Incrementing the loop.
            Load event into self.entry. Return 0, if last event has been reached
        '''

        assert self.position>=0, "Not initialized!"

        success = self._execute()

        self.position += 1

        return success


    @abc.abstractmethod
    def _initialize(self):
        return

    @abc.abstractmethod
    def _execute(self):
        return
