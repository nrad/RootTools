''' Class for a making a new tree based in a TChain in a Sample.
'''

# Standard imports
import ROOT
import copy

# Logging
import logging
logger = logging.getLogger(__name__)

# RootTools
from RootTools.tools.LooperBase import LooperBase
from RootTools.tools.Variable import ScalarType, VectorType, Variable
class TreeMaker( LooperBase ):

    def __init__(self, variables, filler = None, treeName = "Events"):
        
        if not type(variables)==type([]):
            variables = [variables]
        for v in variables:
            if not isinstance(v, Variable):
                raise ValueError( "Not a proper variable: '%r' '%s'"%(v,v) )
            if  hasattr(v, 'filler') and v.filler and not hasattr(v.filler, '__call__'):
                raise ValueError( "Something wrong with the filler '%r' for variable  '%r' '%s'"%(v.filler, v, v) )

        super(TreeMaker, self).__init__( variables = variables)

        self.makeClass( "data", variables = variables, useSTDVectors = False, addVectorCounters = True)

        # Create tree to store the information and store also the branches
        self.treeIsExternal = False
        self.tree = ROOT.TTree( treeName, treeName )
        self.branches = []
        self.makeBranches()

        # function to fill the data 
        self.filler = filler

    def cloneWithoutCompile(self, externalTree = None):
        ''' make a deep copy of self to e.g. avoid re-compilation of class in a loop. 
            Reset TTree as to not create a memory leak.
        '''
        # deep copy by default
        res = copy.deepcopy(self)
        res.branches = []

        # remake TTree
        treeName = self.tree.GetName()
        if res.tree: res.tree.IsA().Destructor( res.tree )
        if externalTree:
            res.treeIsExternal = True
            assert self.tree.GetName() == externalTree.GetName(),\
                "Treename inconsistency (instance: %s, externalTree: %s). Change one of the two"%(self.treeName, externalTree.GetName())
            res.tree = externalTree
        else:
            res.treeIsExternal = False
            res.tree = ROOT.TTree( treeName, treeName )

        res.makeBranches()

        return res

    def makeBranches(self):

        scalerCount = 0
        for s in LooperBase._branchInfo( self.variables, restrictType = ScalarType, addVectorCounters = True):
            name = s[0]
            type_ = s[1]
            self.branches.append( 
                self.tree.Branch(name, ROOT.AddressOf( self.data, name), '%s/%s'%(name, type_))
            )
            scalerCount+=1
        vectorCount = 0
        for name, type_, counterName in LooperBase._branchInfo( self.variables, restrictType = VectorType, addVectorCounters = True ):
            self.branches.append(
                self.tree.Branch(name, ROOT.AddressOf( self.data, name ), "%s[%s]/%s"%(name, counterName, type_) )
            )
            vectorCount+=1
        logger.debug( "TreeMaker created %i new scalars and %i new vectors.", scalerCount, vectorCount )

    def clear(self):
        if self.tree: self.tree.IsA().Destructor( self.tree )

    def _initialize(self):
        self.position = 0
        pass

    def _execute(self):
        ''' Use filler to fill struct and then fill struct to tree'''

        # Initialize struct
        self.data.init()

        if (self.position % 10000)==0:
            logger.info("TreeMaker is at position %6i", self.position)

        # Call external filler method: variables first
        # FIXME: Here, could do a better job by filling with return value for scalars and some
        # vector filler that handles the filling of the components and nVecname.
        for v in self.variables:
            if hasattr(v, 'filler') and v.filler:
                raise NotImplementedError( "Still need to decide whether this is a good idea." )
                self.filler( self.data )
        if self.filler:
            self.filler( self.data )

        # Write to TTree
        if self.treeIsExternal:
            for b in self.branches:
                b.Fill()
        else:
            self.tree.Fill()
        
        return 1 
