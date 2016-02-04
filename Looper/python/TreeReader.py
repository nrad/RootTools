''' Class for a TreeReader of an instance of Sample.
'''

# Standard imports
import ROOT

# Logging
import logging
logger = logging.getLogger(__name__)

# RootTools
from RootTools.Looper.LooperBase import LooperBase
from RootTools.Sample.Sample import Sample

class TreeReader( LooperBase ):

    def __init__(self, sample, scalars = None, vectors = None, selectionString = None):

        if not isinstance(sample, Sample):
            raise ValueError( "Need instance of Sample to initialize any Looper instance" )

        self.selectionString = selectionString
        self.sample = sample

        super(TreeReader, self).__init__( scalars = scalars, vectors = vectors )

        self.makeClass( "data", useSTDVectors = False)

        self.setAddresses()

    def setAddresses(self):
        for s in self.scalars:
            self.sample.chain.SetBranchAddress(s['name'], ROOT.AddressOf(self.data, s['name']))
        for v in self.vectors:
            for c in v['variables']:
                self.sample.chain.SetBranchAddress('%s_%s'%(v['name'], c['name']), \
                ROOT.AddressOf(self.data, '%s_%s'%(v['name'], c['name'])))

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

    def _initialize(self):

        # Turn on everything for flexibility with the selectionString
        logger.debug("Initializing TreeReader for sample %s", self.sample.name)
        self.unmute()
        self.eList = self.sample.getEList(selectionString = self.selectionString) if self.selectionString else None
        self.mute()
        self.nEvents = self.eList.GetN() if  self.eList else self.sample.chain.GetEntries()
        logger.debug("Found %i events to in  %s", self.nEvents, self.sample.name)

        return

    def _execute(self):  
        ''' Execute the read statement and check for the end of the loop'''

        if self.position == self.nEvents: return 0

        if (self.position % 10000)==0:
            logger.info("TreeReader is at position %6i/%6i", self.position, self.nEvents)

        # init struct
        self.data.init()

        # point to the position in the chain (or the eList if there is one)
        self.sample.chain.GetEntry ( self.eList.GetEntry( self.position ) ) if self.eList else self.sample.chain.GetEntry( self.position )
        return 1
