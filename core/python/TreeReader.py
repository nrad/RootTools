''' Class for a TreeReader of an instance of Sample.
'''

# Standard imports
import ROOT
import os
import array

# Logging
import logging
logger = logging.getLogger(__name__)

# RootTools
from RootTools.core.LooperBase import LooperBase
from RootTools.core.Sample import Sample
import RootTools.core.helpers as helpers
from RootTools.core.Variable import Variable, ScalarType, VectorType
from RootTools.core.helpers import shortTypeDict


class TreeReader( LooperBase ):

    def __init__(self, sample, variables, filled_variables = [], selectionString = None, allBranchesActive = True):

        # The following checks are 'look before you leap' but I rather have the user know if the input non-sensical
        if not isinstance(sample, Sample):
            raise ValueError( "Need instance of Sample to initialize any Looper instance. Got %r."%sample )
        if not type(variables) == type([]):
            raise ValueError( "Argument 'variables' must be list. Got %r."%variables )
        if not all (isinstance(v, Variable) for v in variables):
            raise ValueError( "Not all elements in 'variables' are instances of Variable. Got %r."%variables )
        if not type(filled_variables) == type([]):
            raise ValueError( "Argument 'filled_variables' must be list. Got %r."%filled_variables )
        if not all (isinstance(v, Variable) for v in filled_variables):
            raise ValueError( "Not all elements in 'filled_variables' are instances of Variable. Got %r."%filled_variables )
        for v in filled_variables:
            if not hasattr(v, "filler") or not v.filler or not hasattr(v.filler, "__call__"):
                raise ValueError( "Variable %s in 'filled_variables' does not have a proper filler function" )
        if selectionString is not None and not type(selectionString) == type(""):
            raise ValueError( "Don't know what to do with selectionString %r"%selectionString )

        # Selection string to be applied to the chain
        self.selectionString = selectionString

        self.sample = sample

        # Whether all branches are to be read or whether that information should come from the variables
        self.allBranchesActive = allBranchesActive

        # Read branch information from the chain
        self.readLeafInfo()

        # 'filled_variables' are calculated from variables from the chain, they are in the class but no branch 
        # has its address set to it.
        self.filled_variables = filled_variables

        # Get all the variables that should be read
        all_variables  = set()
        for v in self.filled_variables:
            if not v.filler or not hasattr(v.filler, "__call__"):
                raise ValueError( "A Variable to be filled has no proper filler function: %r"%v )
            if hasattr(v.filler, "arguments"):
                all_variables.update(v.filler.arguments)

        # Add 'variables' 
        if variables:  all_variables.update(variables)

        # 'variables' are read from the chain
        super(TreeReader, self).__init__( variables = list(all_variables) ) 

        for s in list(self.variables):
            logger.debug( "Making class with variable %s" %s)

        # make class
        self.makeClass( "data", list(self.variables), useSTDVectors = False, addVectorCounters = False)

        # set the addresses of the branches corresponding to 'variables'
        self.setAddresses()
        
        # make eList from cutString
        # Turn on everything for flexibility with the selectionString
        logger.debug("Initializing TreeReader for sample %s", self.sample.name)
        self.activateAllBranches()
        self.eList = self.sample.getEList(selectionString = self.selectionString) if self.selectionString is not None else None
        self.activateBranches()
        self.nEvents = self.eList.GetN() if  self.eList else self.sample.chain.GetEntries()
        logger.debug("Found %i events in  %s", self.nEvents, self.sample.name)

        #  default event range of the reader
        self.eventRange = (0, self.nEvents)

    def setAddresses(self):
        ''' Set all the branch addresses to the members in the class instance
        '''
        for s in LooperBase._branchInfo(self.variables, addVectorCounters = False):
            #logger.debug( "Setting address of %s to %s", s['name'], ROOT.AddressOf(self.data, s['name'] ) )
            self.sample.chain.SetBranchAddress(s['name'], ROOT.AddressOf(self.data, s['name'] ))

    def cloneTree(self, branchList = [], newTreename = None, rootfile = None):
        '''Clone tree after preselection and event range
        '''
        selectionString = self.selectionString if self.selectionString is not None else "1"
        if self.eList:

            # If there is an eList, first restrict it to the event range, then clone
            list_to_copy = ROOT.TEventList("tmp","tmp")
            for i_ev in xrange(*self.eventRange):
                list_to_copy.Enter(self.eList.GetEntry(i_ev))

            # activate branches that we want to copy, disable the ones we only need for reading
            self.activateBranches( turnOnReadBranches = False, branchList = branchList )
            # preserving current event list
            tmpEventList = self.sample.chain.GetEventList()
            tmpEventList = 0 if not self.sample.chain.GetEventList() else tmpEventList

            # Copy the selected events
            self.sample.chain.SetEventList( list_to_copy ) 

            # Create the new tree in a file (if there is one)
            tmp_directory = ROOT.gDirectory
            if rootfile is not None: 
                logger.debug( "cd to file %r", rootfile )
                rootfile.cd() 

            res =  self.sample.chain.CopyTree( "(1)", "" )
            # Same?
            # res =  self.sample.chain.CloneTree( 0 )
            # res.CopyEntries( self.sample.chain )

            # Change back to previous gDirectory
            tmp_directory.cd()

            # restoring event list
            self.sample.chain.SetEventList( tmpEventList ) 

            # activate what we read, don't activate the ones we just copied
            self.activateBranches( turnOnReadBranches = True, branchList = [] )

            list_to_copy.Delete()

            if newTreename is not None: res.SetName( newTreename )

            return res 

        else:

            tmp_directory = ROOT.gDirectory
            if rootfile is not None: 
                logger.debug( "cd to file %r", rootfile )
                rootfile.cd() 

            res = self.sample.chain.CopyTree( selectionString, "", self.eventRange[1] - self.eventRange[0], self.eventRange[0] )
            # Change back to previous gDirectory
            tmp_directory.cd()

            return res

    def activateBranches(self, turnOnReadBranches = True, branchList = []):
        ''' Set status of all needed branches in sample chain to '1' 
        '''
        self.sample.chain.SetBranchStatus("*", 0)
        if turnOnReadBranches:
            #Turn on all branches?
            if self.allBranchesActive:
                self.activateAllBranches()
                return
            # Turn on all branches from the variables to read
            # First, arguments used in any of the filler functions
            filler_variables = set()
            for v in self.filled_variables:
                if hasattr(v.filler, "arguments"): filler_variables.update( v.filler.arguments ) 
            # Turn on all branches
            for s in LooperBase._branchInfo( self.variables + list(filler_variables), addVectorCounters = False):
                self.sample.chain.SetBranchStatus(s['name'], 1)
        for b in branchList:
            self.sample.chain.SetBranchStatus(b, 1)

    def activateAllBranches(self):
        '''Set status of all branches in the sample chain to 1
        '''
        self.sample.chain.SetBranchStatus("*", 1)

    def readLeafInfo(self):
        ''' Read information on the leaves from the chain and store in dict
            FIXME: Pretty sure this doesn't yet work for fixed sized vectors
        '''
        leafInfo = []
        for s in self.sample.chain.GetListOfLeaves():
            leaf = {'type':shortTypeDict[s.GetTypeName()], 'name':s.GetName()}
            countval = array.array('i',[-9999])
            pointer = s.GetLeafCounter(countval)
            leaf['dim'] = 'scalar'
            if pointer:
                # Vector
                # GetLeafCounter returns countval==1 if a counter leaf was found and pointer points to that leaf
                # https://root.cern.ch/doc/master/classTLeaf.html#a062bd89a11fd1f922c096e66d2601ab6
                if countval[0]==1:
                    leaf['counterInt'] = pointer.GetName()
                leaf['dim'] = 'vector'
            else:
                # For fixed size arrays, the pointer is zero and the countval is the size of the array
                leaf['nMax'] = countval[0]
            leafInfo.append(leaf)
        return leafInfo

    def getEventRanges(self, maxFileSizeMB = None, maxNEvents = None, minJobs = None):
        '''For convinience: Define splitting of sample according to various criteria
        '''
        def chunks(l, n):
            """Yield successive n-sized chunks from l."""
            for i in xrange(0, len(l), n):
                yield (i, i+n)

        if maxFileSizeMB is not None:
            nSplit = sum( os.path.getsize(f) for f in self.sample.files ) / ( 1024**2*maxFileSizeMB )
        elif maxNEvents is not None:
            nSplit = self.nEvents / maxNEvents 
        else:
            nSplit = 0
        if minJobs is not None and nSplit < minJobs: 
            nSplit = minJobs
        if nSplit==0:
            logger.debug( "Returning full event range because no splitting is specified" )
            return [(0, self.nEvents)]
        thresholds = [i*self.nEvents/nSplit for i in range(nSplit)]+[self.nEvents]
        return [(thresholds[i], thresholds[i+1]) for i in range(len(thresholds)-1)] 

    def setEventRange( self, evtRange ):
        ''' Specify an event range that the reader will run over. 
            Bounded by (0, nEvents).
        '''
        old_eventRange = self.eventRange
        self.eventRange = ( max(0, evtRange[0]), min( self.nEvents, evtRange[1]) ) 
        logger.debug( "[setEventRange] Set eventRange %r (was: %r) for reader of sample %s", self.eventRange, old_eventRange, self.sample.name )

    def setEventList( self, evtList ):
        ''' Specify an event list that the reader will run over. 
        '''
        self.sample.chain.SetEventList( evtList ) 
        self.eList = evtList 
        self.nEvents = self.eList.GetN()
        self.eventRange = (0, self.nEvents)
        logger.debug( "[setEventList] Set eventRange %r for reader of sample %s", self.eventRange, self.sample.name )
    
    def reduceEventRange( self, reduction_factor ):
        ''' Reduce event range by a given factor. 
        '''
        old_eventRange = self.eventRange if hasattr(self, "eventRange") else None
        self.eventRange = ( self.eventRange[0], self.eventRange[0] + (self.eventRange[1] - self.eventRange[0])/reduction_factor ) 
        logger.debug( "[reduceEventRange] Set new eventRange %r (was: %r) for reader of sample %s", self.eventRange, old_eventRange, self.sample.name )

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
        if self.position==0:
            logger.info("TreeReader for sample %s starting at position %i and processing %i events.", 
                self.sample.name, self.position, self.nEvents)
        elif (self.position % 10000)==0:
            logger.info("TreeReader for sample %s is at position %6i/%6i", 
                self.sample.name, self.position, self.nEvents )

        # init struct
        self.data.init()

        # get entry 
        errorLevel = ROOT.gErrorIgnoreLevel
        ROOT.gErrorIgnoreLevel = 3000
        self.sample.chain.GetEntry ( self.eList.GetEntry( self.position ) ) if self.eList else self.sample.chain.GetEntry( self.position )
        ROOT.gErrorIgnoreLevel = errorLevel

        # point to the position in the chain (or the eList if there is one)
        for v in self.filled_variables:
            if isinstance(v, ScalarType):
                setattr(self.data, v.name, v.filler( self. data ) )
            else:
                raise NotImplementedError( "Haven't yet implemented vector type filled variables." )
        return 1

    def goToPosition(self, position):
        self.position = position
        self._execute()
