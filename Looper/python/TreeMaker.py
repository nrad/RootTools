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

        assert filler, "No filler function provided.."
        assert scalars or vectors, "No data member specification provided."

        super(TreeMaker, self).__init__( scalars = scalars, vectors = vectors )

        self.makeClass( "data" , useSTDVectors = False)

        # Create tree to store the information and store also the branches
        self.tree = ROOT.TTree( treeName, treeName )
        self.branches = []
        self.makeBranches()

        # function to fill the data 
        self.filler = filler

    def makeBranches(self):
        for s in self.scalars:
            self.branches.append( 
                self.tree.Branch(s['name'], ROOT.AddressOf( self.data, s['name']), "%s/%s"%(s['name'],s['type']))
            )
        for v in self.vectors:
            for c in v['variables']:
                vectorComponentName = "%s_%s"%(v['name'], c['name'])
                self.branches.append( 
                    self.tree.Branch(vectorComponentName, ROOT.AddressOf( self.data, vectorComponentName ), \
                        "%s[n%s]/%s"%(vectorComponentName, v['name'], c['type']) )
                )
        logger.debug( "TreeMaker created %i new scalars and %i new vectors.", len(self.scalars), len(self.vectors) )

    def _initialize(self):
        pass

    def _execute(self):
        ''' Use filler to fill struct and then fill struct to tree'''

        # Initialize struct
        self.data.init()

        if (self.position % 10000)==0:
            logger.info("TreeMaker is at position %6i", self.position)

        # Call external filler method
        self.filler( self.data )

        # Write to TTree
        self.tree.Fill()

        return 1 
