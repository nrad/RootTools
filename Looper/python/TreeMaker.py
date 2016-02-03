''' Class for a making a new tree based in a TChain in a Sample.
'''

# Standard imports
import ROOT

# Logging
import logging
logger = logging.getLogger(__name__)

# RootTools
from RootTools.Looper.LooperBase import LooperBase

class TreeMaker( LooperBase ):

    def __init__(self, sample, scalars, vectors = None, selectionString = None, treeName = "Events" ):

#        if vectors: raise NotImplementedError( "Haven't yet bothered adding vector output to TreeMaker. Call with vectors = None." )
        super(TreeMaker, self).__init__( sample = sample, scalars = scalars, vectors = vectors , selectionString = selectionString)

        self.makeClass( "output" , useSTDVectors = True)
        self.tree = ROOT.TTree( treeName, treeName )
        self.makeBranches()

    def makeBranches(self):
        for s in self.scalars:
            self.tree.Branch(s['name'], ROOT.AddressOf( self.output, s['name']), "%s/%s"%(s['name'],s['type']))
        
    def execute(self):
        ''' Do what a converter does'''
        # point to the position in the chain (or the eList if there is one)
#        self.sample.chain.GetEntry ( self.eList.GetEntry( self.position ) ) if self.eList else self.sample.chain.GetEntry(self.position)
        return
