''' Class for a TreeReader of an instance of Sample.
'''

# Standard imports
import ROOT
import os

# Logging
import logging
logger = logging.getLogger(__name__)

# RootTools
from RootTools.tools.LooperBase import LooperBase
from RootTools.tools.Sample import Sample
from RootTools.tools.Variable import Variable, ScalarType, VectorType

class TreeReader( LooperBase ):

    def __init__(self, sample, variables, derived_variables = [], selectionString = None):

        # The following checks are 'look before you leap' but I rather have the user know if the input non-sensical
        if not isinstance(sample, Sample):
            raise ValueError( "Need instance of Sample to initialize any Looper instance. Got '%r'."%sample )
        if not type(variables) == type([]):
            raise ValueError( "Argument 'variables' must be list. Got '%r'."%variables )
        if not all (isinstance(v, Variable) for v in variables):
            raise ValueError( "Not all elements in 'variables' are instances of Variable. Got '%r'."%variables )
        if not type(derived_variables) == type([]):
            raise ValueError( "Argument 'derived_variables' must be list. Got '%r'."%derived_variables )
        if not all (isinstance(v, Variable) for v in derived_variables):
            raise ValueError( "Not all elements in 'derived_variables' are instances of Variable. Got '%r'."%derived_variables )

        self.selectionString = selectionString
        self.sample = sample
        
        super(TreeReader, self).__init__( variables = variables ) 
        self.derived_variables = derived_variables

        self.makeClass( "data", variables + derived_variables, useSTDVectors = False, addVectorCounters = False)

        self.setAddresses()
        
        # Turn on everything for flexibility with the selectionString
        logger.debug("Initializing TreeReader for sample %s", self.sample.name)
        self.activateAllBranches()
        self.eList = self.sample.getEList(selectionString = self.selectionString) if self.selectionString else None
        self.activateBranches()
        self.nEvents = self.eList.GetN() if  self.eList else self.sample.chain.GetEntries()
        logger.debug("Found %i events to in  %s", self.nEvents, self.sample.name)

        #  event range of the reader
        self.eventRange = (0, self.nEvents)

    def setAddresses(self):
        ''' Set all the branch addresses to the members in the class instance
        '''
        for s in LooperBase._branchInfo(self.variables, addVectorCounters = False):
            self.sample.chain.SetBranchAddress(s[0], ROOT.AddressOf(self.data, s[0]))

    def cloneTree(self, branchList = []):
        '''Clone tree after preselection and event range
        '''
        selectionString = self.selectionString if self.selectionString else "1"
        if self.eList:

            # If there is an eList, first restrict it to the event range, then clone
            list_to_copy = ROOT.TEventList("tmp","tmp")
            for i_ev in xrange(*self.eventRange):
                list_to_copy.Enter(self.eList.GetEntry(i_ev))

            # activate branches that we want to copy, disable the ones we only need for reading
            # FIXME I do not preserve the list of active branches here, maybe should improve in the future 
            self.activateBranches( readBranches = False, branchList = branchList )
            # Copy the selected events
            self.sample.chain.SetEventList( list_to_copy ) 
            res =  self.sample.chain.CopyTree( "(1)", "") 
            self.sample.chain.SetEventList( 0 ) 
            # activate what we read, don't activate the ones we just copied
            self.activateBranches( readBranches = True, branchList = [] )
            list_to_copy.Delete()

            return res 

        else:
            return self.sample.chain.CopyTree( selectionString, "", self.eventRange[1] - self.eventRange[0], self.eventRange[0] )

    def activateBranches(self, readBranches = True, branchList = []):
        ''' Set status of all needed branches in sample chain to '1' 
        '''
        self.sample.chain.SetBranchStatus("*", 0)
        if readBranches:
            for s in LooperBase._branchInfo( self.variables, addVectorCounters = False):
                self.sample.chain.SetBranchStatus(s[0], 1)
        for b in branchList:
            self.sample.chain.SetBranchStatus(b, 1)

    def activateAllBranches(self):
        '''Set status of all branches in the sample chain to 1
        '''
        self.sample.chain.SetBranchStatus("*", 1)

    def getEventRanges(self, maxFileSizeMB = 200):
        '''For convinience: Define splitting of sample according to total input file size
        '''
        
        nSplit = 1 + sum( os.path.getsize(f) for f in self.sample.files ) / ( 1024**2*maxFileSizeMB )
        chunks = [( i*( self.nEvents/nSplit), min(self.nEvents, (i+1)*( self.nEvents/nSplit) ) ) for i in range(nSplit) ]
        
        return chunks

    def setEventRange( self, evtRange ):
        ''' Specify an event range that the reader will run over. 
            Default is (0, nEvents).
        '''
        self.eventRange = ( max(0, evtRange[0]), min( self.nEvents, evtRange[1]) ) 

    def _initialize(self):
        ''' This method is called from the Base class start method.
            Initializes the reader, sets position to lower event range.
        '''
        # set to the first position, either 0 or the lower eventRange deliminator
        self.position = self.eventRange[0]

        return

    def _execute(self):  
        ''' Does what a reader should do: 'GetEntry' into the data struct.
            Returns 0 if upper eventRange is hit. 
        '''

        if self.position == self.eventRange[1]: return 0

        if (self.position % 10000)==0:
            logger.info("TreeReader is at position %6i/%6i", self.position, self.nEvents)

        # init struct
        self.data.init()

        # point to the position in the chain (or the eList if there is one)
        self.sample.chain.GetEntry ( self.eList.GetEntry( self.position ) ) if self.eList else self.sample.chain.GetEntry( self.position )
        return 1
