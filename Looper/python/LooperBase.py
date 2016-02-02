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
from RootTools.Sample.SampleBase import SampleBase
from RootTools.Looper.LooperHelpers import createClassString

class LooperBase( object ):
    __metaclass__ = abc.ABCMeta

    def __init__(self, sample, scalars, vectors, selectionString):
        if not isinstance(sample, SampleBase):
            raise ValueError( "Need instance of Sample to initialize any Looper instance" )

        self.sample  = sample
        self.scalars = []
        self.vectors = []

        # directory where the class is compiled
        self.tmpDir = '/tmp/'

        for s in scalars:
            self.addScalar(s)

        for v in vectors:
            self.addVector(v)

        self.selectionString = selectionString

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
            raise Exception("Don't know what to do with vector %r"%s)

    def makeClass(self, attr):

        if not os.path.exists(self.tmpDir):
            logger.info("Creating %s directory for temporary files for class compilation.", self.tmpDir)
            os.path.makedirs(self.tmpDir)

        uniqueString = str(uuid.uuid4()).replace('-','_')
        tmpFileName = os.path.join(self.tmpDir, uniqueString+'.C')
        className = "Class_"+uniqueString

        with file( tmpFileName, 'w' ) as f:
            logger.debug("Creating temporary file %s for class compilation.", tmpFileName)
            f.write( createClassString( scalars = self.scalars, vectors=self.vectors).replace( "className", className ) )

        # A less dirty solution possible?
        logger.debug("Compiling file %s", tmpFileName)
        ROOT.gROOT.ProcessLine('.L %s+'%tmpFileName )

        logger.debug("Importing class %s", className)
        exec( "from ROOT import %s" % className )

        logger.debug("Creating instance of class %s", className)
        setattr(self, attr, eval("%s()" % className) )

        return self

    def mute(self):
        ''' Mute all branches that are not needed
        '''
        self.sample.chain.SetBranchStatus("*", 0)
        for s in self.scalars:
            self.sample.chain.SetBranchStatus(s['name'], 1)
        for v in self.vectors:
            for c in v['variables']:
                self.sample.chain.SetBranchStatus("%s_%s"%(v['name'],c['name']), 1)

    def unmute(self):
        self.sample.chain.SetBranchStatus("*", 1)

    def initialize(self):
        # Turn on everything for flexibility with the selectionString
        self.unmute()
        self.eList = self.sample.getEList(selectionString = self.selectionString) if self.selectionString else None
        self.mute()
        self.nEvents = self.eList.GetN() if  self.eList else self.sample.chain.GetEntries()

        return

    def loop(self):
        ''' Load event into self.entry. Return 0, if last event has been reached
        '''
        if self.position < 0:
            logger.debug("Starting Reader for sample %s", self.sample.name)
            self.initialize()
            self.position = 0
        else:
            self.position += 1
        if self.position == self.nEvents: return 0

        if (self.position % 1000)==0:
            logger.info("Reader for sample %s is at position %6i/%6i", self.sample.name, self.position, self.nEvents)

        self.execute()

        return 1

    @abc.abstractmethod
    def execute(self):
        return

