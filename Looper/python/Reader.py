''' Class for a Reader of a Sample.
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
from RootTools.Sample.SampleBase import SampleBase
from RootTools.Looper.LooperHelpers import createClassString

class Reader():
    
    def __init__(self, sample, scalars, vectors):
        if not isinstance(sample, SampleBase):
            raise ValueError( "Need instance of SampleBase to initialize Reader" )

        self.sample  = sample
        self.scalars = []
        self.vectors = []

        # directory where the class is compiled
        self.tmpDir = '/tmp/'

        for s in scalars:
            self.addScalar(s)

        for v in vectors:
            self.addVector(v)

        self.makeClass()

    def addScalar(self, scalarname):
        '''Add a scalar variable with syntax 'Var/Type'.
        '''

        if not type(scalarname)==type(""):   raise ValueError ("Got %r but was expecting string"%s)
        if not scalarname.count('/')==1:     raise Exception( "Cannot add scalar variable '%r'. Syntax is Name/Type."% s)
        scalarname, varType = scalarname.split('/')
        self.scalars.append({'name':scalarname, 'type':varType})

    def addVector(self, vector):
        '''Add vector variable as a dictionary e.g. {'name':Jet, 'nMax':100, 'variables':['pt/F']}.
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

    def makeClass(self):
        if not os.path.exists(self.tmpDir): os.path.makedirs(self.tmpDir)
        uniqueString = str(uuid.uuid4()).replace('-','_')
        tmpFileName = os.path.join(self.tmpDir, uniqueString+'.C')
        className = "Class_"+uniqueString
        with file( tmpFileName, 'w' ) as f:
            f.write( createClassString( scalars = self.scalars, vectors=self.vectors).replace( "className", className ) )

        # A less dirty solution possible?
        ROOT.gROOT.ProcessLine('.L %s+'%tmpFileName )
        exec( "from ROOT import %s" % className )
        setattr(self, "entry", eval("%s()" % className) )
