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
from RootTools.tools.LooperHelpers import createClassString
from RootTools.tools.Variable import Variable, ScalarType, VectorType

class LooperBase( object ):
    __metaclass__ = abc.ABCMeta

    def __init__(self, variables):

        if not type(variables) == type([]):
            raise ValueError( "Argument 'variables' must be list. Got %r"%variables )
        if not all (isinstance(v, Variable) for v in variables):
            raise ValueError( "Not all elements in variable list are instances of Variable. Got %r"%variables )

        self.variables = variables

        # directory where the class is compiled
        self.tmpDir = '/tmp/'

        # Internal state for running
        self.position = -1
        self.eList = None

        self.classUUIDs = []

    @staticmethod
    def _branchInfo( variables, addVectorCounters = False, restrictType = None):
        ''' Get a list of the form [(var, type), (vectorComponent, type, counterName)...] for all branches which is
            needed for handling the branches.
        '''
        res = []
        for s in variables:
            if isinstance(s, ScalarType):
                if not restrictType or restrictType == ScalarType:
                    res.append( {'name':s.name, 'type':s.type} )
            elif isinstance(s, VectorType):
                tmp = s.counterVariable()
                for c in s.components:
                    if restrictType is None or restrictType == VectorType:
                        res.append( { 'name':c.name, 'type':c.type, 'counterInt':tmp.name} )
                if addVectorCounters: 
                    if restrictType is None or restrictType == ScalarType:
                        res.append( {'name':tmp.name, 'type':tmp.type} )
            else: raise ValueError( "Found an element in that is not a ScalarType or VectorType instance: %r"%s )
        return res

    def makeClass(self, attr, variables, addVectorCounters, useSTDVectors = False):

        if not os.path.exists(self.tmpDir):
            logger.info("Creating %s directory for temporary files for class compilation.", self.tmpDir)
            os.path.makedirs(self.tmpDir)

        classUUID = str(uuid.uuid4()).replace('-','_')
        self.classUUIDs.append( classUUID )

        tmpFileName = os.path.join(self.tmpDir, classUUID+'.C')
        className = "Class_"+classUUID

        with file( tmpFileName, 'w' ) as f:
            logger.debug("Creating temporary file %s for class compilation.", tmpFileName)
            f.write(
                createClassString( variables = variables, useSTDVectors = useSTDVectors, addVectorCounters = addVectorCounters)
                .replace( "className", className )
            )

        # A less dirty solution possible?
        logger.debug("Compiling file %s", tmpFileName)
#        ROOT.gROOT.ProcessLine('.L %s+'%tmpFileName )
        #FIXME OSX ACliC compilation doesn't work
        ROOT.gROOT.ProcessLine('.L %s'%tmpFileName )

        logger.debug("Importing class %s", className)
        exec( "from ROOT import %s" % className )

        logger.debug("Creating instance of class %s", className)
        setattr(self, attr, eval("%s()" % className) )

        return self

    def cleanUpTempFiles(self):
        ''' Delete all temporary files.
        '''
        files = os.listdir(self.tmpDir)
        toBeDeleted = []
        for uuid in self.classUUIDs:
            for f in files:
                if uuid in f:
                    toBeDeleted.append(f)
        for f in toBeDeleted:
            filename = os.path.join(self.tmpDir, f)
            os.remove(filename)
            logger.debug( "Deleted temporary file %s"%filename )

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
