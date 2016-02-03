''' Class for a TreeReader of an instance of Sample.
'''

# Standard imports
import ROOT

# Logging
import logging
logger = logging.getLogger(__name__)

# RootTools
from RootTools.Looper.LooperBase import LooperBase

class TreeReader( LooperBase ):

    def __init__(self, sample, scalars, vectors, selectionString = None):

        super(TreeReader, self).__init__( sample = sample, scalars = scalars, vectors = vectors , selectionString = selectionString )

        self.makeClass( "entry", useSTDVectors = False)

        self.setAddresses()

    def setAddresses(self):
        for s in self.scalars:
            self.sample.chain.SetBranchAddress(s['name'], ROOT.AddressOf(self.entry, s['name']))
        for v in self.vectors:
            for c in v['variables']:
                self.sample.chain.SetBranchAddress('%s_%s'%(v['name'], c['name']), \
                ROOT.AddressOf(self.entry, '%s_%s'%(v['name'], c['name'])))

    def execute(self):  
        ''' Do what a reader does'''
        # point to the position in the chain (or the eList if there is one)
        self.sample.chain.GetEntry ( self.eList.GetEntry( self.position ) ) if self.eList else self.sample.chain.GetEntry(self.position)
