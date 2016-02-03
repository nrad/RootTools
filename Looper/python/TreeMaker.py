''' Class for a making a new tree based in a TChain in a Sample.
'''

# Standard imports
import ROOT
import copy

# Logging
import logging
logger = logging.getLogger(__name__)

# RootTools
from RootTools.Looper.LooperBase import LooperBase

class TreeMaker( LooperBase ):

    def __init__(self, filler, scalars = None, vectors = None, treeName = "Events"):

        if vectors: raise NotImplementedError("Need to implmenet variable sized vectors with arrays")

        assert filler, "Makes no sense to have no filler."
        assert scalars or vectors, "Makes no sense to have no members."

        super(TreeMaker, self).__init__( scalars = scalars, vectors = vectors )

        self.makeClass( "output" , useSTDVectors = True)

        # Create tree to store the information and store also the branches
        self.tree = ROOT.TTree( treeName, treeName )
        self.branches = []
        self.makeBranches()

        # function to fill the output 
        self.filler = filler

    def makeBranches(self):
        for s in self.scalars:
            self.branches.append( 
                self.tree.Branch(s['name'], ROOT.AddressOf( self.output, s['name']), "%s/%s"%(s['name'],s['type']))
            )
        # vectors segfault
        for v in self.vectors:
            for c in v['variables']:
                vectorComponentName = "%s_%s"%(v['name'], c['name'])
                self.branches.append( 
                    self.tree.Branch(vectorComponentName, "vector< %s >"%c['type'], ROOT.AddressOf( self.output, vectorComponentName ) )
                )

    def initialize(self):
        pass

    def execute(self):
        ''' Use filler to fill struct and then fill struct to tree'''

        # Initialize struct
        self.output.init()

        if (self.position % 10000)==0:
            logger.info("TreeMaker is at position %6i", self.position)

        # Call external filler method
        self.filler( self.output )

        # Write to TTree
        self.tree.Fill()

        return 1 
