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

class LooperBase( object ):
    __metaclass__ = abc.ABCMeta

    def __init__(self, scalars, vectors):

        self.scalars = []
        self.vectors = []

        # directory where the class is compiled
        self.tmpDir = '/tmp/'

        if scalars: 
            for s in scalars:
                self.addScalar(s)

        if vectors: 
            for v in vectors:
                self.addVector(v)

        # Internal state for running
        self.position = -1
        self.nEvents = None
        self.eList = None

    def addScalar(self, scalarname):
        '''Add a scalar variable with syntax 'Var/Type'.
        '''

        if not type(scalarname)==type(""):   raise ValueError ("Got %r but was expecting string"%s)
        if not scalarname.count('/')==1:     raise Exception( "Cannot add scalar variable '%r'. Syntax is Name/Type."% s)
        scalarname, varType = scalarname.split('/')
        self.scalars.append({'name':scalarname, 'type':varType})

    def addVector(self, vector):
        '''Add vector variable as a dictionary e.g. {'name':Jet, 'nMax':100, 'variables':['pt/F']}
           N.B. This will be added as {'name':Jet, 'nMax':100, 'variables':[{'name':'pt', 'type':'F'}]}.
        '''
        vector_ = copy.deepcopy(vector)
        if vector_.has_key('name') and vector_.has_key('nMax') and vector_.has_key('variables'):

            # Add counting variable (CMG default for vector_ variable counters is 'nNAME')
            self.scalars.append( {'name':'n{0}'.format(vector_['name']), 'type':'I'} )

            # replace 'variables':['pt/F',...] with 'variables':[{'name':'pt', 'type':'F'}]
            variables_ = []
            for component in vector_['variables']:
                if not component.count('/')==1:     raise Exception( "Cannot add vector component '%r'. Syntax is Name/Type."% r)
                varName, varType = component.split('/')
                variables_.append({'name':varName, 'type':varType})

            vector_.update({'variables':variables_})
            self.vectors.append(vector_)

        else:
            raise Exception("Don't know what to do with vector %r"%vector)

    def makeClass(self, attr, useSTDVectors = False):

        if not os.path.exists(self.tmpDir):
            logger.info("Creating %s directory for temporary files for class compilation.", self.tmpDir)
            os.path.makedirs(self.tmpDir)

        uniqueString = str(uuid.uuid4()).replace('-','_')
        tmpFileName = os.path.join(self.tmpDir, uniqueString+'.C')
        className = "Class_"+uniqueString

        with file( tmpFileName, 'w' ) as f:
            logger.debug("Creating temporary file %s for class compilation.", tmpFileName)
            f.write( 
                createClassString( scalars = self.scalars, vectors=self.vectors, useSTDVectors = useSTDVectors)
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

    def run(self):
        ''' Load event into self.entry. Return 0, if last event has been reached
        '''
    
        assert self.position>=0, "Not initialized!"

        success = self.execute()

        self.position += 1

        return success


    def start(self):
        self.position = 0    
        self.initialize()
    
    @abc.abstractmethod
    def initialize(self):
        return

    @abc.abstractmethod
    def execute(self):
        return
