''' Sample class.
    Implements definition and handling of the TChain.
'''

# Standard imports
import ROOT
import uuid
import numbers
import os
from math import sqrt

# Logging
import logging
logger = logging.getLogger(__name__)
# RootTools imports
import RootTools.tools.helpers as helpers
import RootTools.tools.u_float as u_float

class EmptySampleError(Exception):
    '''Accessing a sample without ROOT files.
    '''
    pass

@helpers.static_vars(sampleCounter = 0)
def newName():
    result = "Sample_"+str(newName.sampleCounter)
    newName.sampleCounter += 1
    return result

class Sample ( object ): # 'object' argument will disappear in Python 3

    def __init__(self, name, treeName , files = [], sumOfWeights = None):
        ''' Base class constructor for all sample classes.
            name: Name of the sample, treeName: name of the TTree in the input files
        '''
        self.name = name
        self.treeName = treeName
        self.files = files
        self.sumOfWeights = None
        self._chain = None
        logger.debug("Created new sample %s with treeName %s.", name, treeName)

    @classmethod
    def fromFiles(cls, name, files, treeName=None, sumOfWeights = None):
        '''Load sample from files or list of files. If the name is "", enumerate the sample
        '''

        # Work with files and list of files
        files = [files] if type(files)==type("") else files

        # If no name, enumerate them.
        if not name: name = newName()
        if not treeName: 
            treeName = "Events"
            logger.debug("Argument 'treeName' not providedf for sample %s, using 'Events'."%name) 

        sample =  cls(name = name, treeName = treeName, files = files, sumOfWeights = sumOfWeights)

        logger.info("Loaded sample %s from %i files.", name, len(files))
        return sample

    @classmethod
    def fromDirectory(cls, name, directory, treeName = None, sumOfWeights = None):
        '''Load sample from directory or list of directories. If the name is "", enumerate the sample
        '''
        # Work with directories and list of directories
        directories = [directory] if type(directory)==type("") else directory 

        # If no name, enumerate them.
        if not name: name = newName()

        # find all files
        files = [] 
        for d in directories:
            files.extend(  os.path.join(d, f) for f in os.listdir(d) if f.endswith('.root') )
        if not treeName: 
            treeName = "Events"
            log.debug("Argument 'treeName' not provided, using 'Events'.") 

        sample =  cls(name = name, treeName = treeName, files = files, sumOfWeights = sumOfWeights)
        logger.info("Loaded sample %s from %i directory(ies): %s", name, len(files), ",".join(directories))
        return sample

    @classmethod
    def fromCMGOutput(cls, name, baseDirectory, treeFilename = 'tree.root', chunkString = None, treeName = 'tree', maxN = None):
    
        def readNormalization(filename):
            with open(filename, 'r') as fin:
                for line in fin:
                    if any( [x in line for x in ['All Events', 'Sum Weights'] ] ):
                        sumW = float(line.split()[2])
                        return sumW

        maxN = maxN if not (maxN and maxN<0) else None

        # Reading all subdirectories in base directory. If chunkString != None, require cmg output name formatting
        chunkDirectories = []
        for x in os.walk(baseDirectory):
            if not chunkString or (x[0].startswith(chunkString) and x[0].endswith('_Chunk')) or x[0]==chunkString:
                chunkDirectories.append(x[0])

        logger.debug( "Found %i chunk directories with chunkString %s in base directory %s", \
                           len(chunkDirectories), chunkString, baseDirectory )

        sumOfWeights = 0
        files = []
        failedChunks=[]
        goodChunks  =[]

        for i, chunkDirectory in enumerate( chunkDirectories ):
            success = False
            logger.debug("Reading chunk %s", chunkDirectory)

            for root, subFolders, filenames in os.walk( chunkDirectory ):
                sumW = None
                treeFile = None

                # Determine normalization constant
                if 'SkimReport.txt' in filenames:
                    skimReportFilename = os.path.join(root, 'SkimReport.txt')
                    sumW = readNormalization( skimReportFilename )
                    if not sumW:
                        logger.warning( "Read chunk %s and found report '%s' but could not read normalization.",
                                             chunkDirectory, skimReportFilename )

                # Load tree file 
                if treeFilename in filenames:
                    treeFile = os.path.join(root, treeFilename)
                    # Checking whether root file is OG and contains a tree
                    if not helpers.checkRootFile(treeFile, checkForObjects=[treeName] ):
                        logger.warning( "Read chunk %s and found tree file '%s' but file looks broken.",  chunkDirectory, treeFile )

                # If both, normalization and treefile are OK call it successful. 
                if sumW and treeFile:
                    files.append( treeFile )
                    sumOfWeights += sumW
                    logger.debug( "Successfully read chunk %s and incremented sumOfWeights by %7.2f",  chunkDirectory, sumW )
                    success = True
                    goodChunks.append( chunkDirectory )
                    break

            if not success:
                failedChunks.append( chunkDirectory  )

        # Don't allow empty samples
        if len(goodChunks) == 0:
            raise EmptySampleError("Could not find good CMGOutput chunks for sample {0}. Total number of chunks: {1}. baseDirectory: {2}"\
                  .format(name, len(chunkDirectories), baseDirectory))

        # Log statements
        eff = 100*len(failedChunks)/float( len(chunkDirectories) )
        logger.info("Loaded CMGOutput sample %s. Total number of chunks : %i. Normalization: %7.2f Bad: %i. Inefficiency: %3.3f", \
                          name, len(chunkDirectories), sumOfWeights, len(failedChunks), eff)

        for chunk in failedChunks:
            logger.debug( "Failed to load chunk %s", chunk)

        return cls( name = name, treeName = treeName, files = files, sumOfWeights = sumOfWeights)

    # Handle loading of chain -> load it when first used 
    @property
    def chain(self):
        if not self._chain: 
            logger.debug("First request of attribute 'chain' for sample %s. Calling __loadChain", self.name)
            self.__loadChain()
        return self._chain

    # "Private" method that loads the chain from self.files
    def __loadChain(self):
        ''' Load the TChain. Private.
        '''
        if len(self.files) == 0:
            raise EmptySampleError("Sample {name} has no input files! Can not load.".format(name = self.name) )
        else:
            self._chain = ROOT.TChain(self.treeName)
            counter = 0
            for f in self.files:
                logger.debug("Now adding file %s to sample '%s'", f, self.name)
                try:
                    if helpers.checkRootFile(f, checkForObjects=[self.treeName]):
                        self._chain.Add(f)
                        counter+=1
                except IOError:
                    pass
                    logger.warning( "Could not load file %s", f )
            logger.debug( "Loaded %i files for sample '%s'.", counter, self.name )

    def clear(self): #FIXME How to promote to destructor without making it segfault?
        ''' Really (in the ROOT namespace) delete the chain
        '''
        if self._chain:
            self._chain.IsA().Destructor( self._chain )
            self._chain = None
            logger.debug("Called TChain Destructor for sample '%s'.", self.name)

    def treeReader(self, **kwargs):
        ''' Return a Reader class for the sample
        '''
        from TreeReader import TreeReader
        logger.debug("Creating TreeReader object for sample '%s'.", self.name)
        return TreeReader( self, **kwargs )

    # Below some helper functions to get useful things from a sample

    def getEList(self, selectionString=None, name=None):
        ''' Get a TEventList from a selectionString
        '''

        tmp=str(uuid.uuid4())
        logger.debug( "Making eList for sample %s and selectionString %s", self.name, selectionString )
        self.chain.Draw('>>'+tmp, selectionString if selectionString else "(1)")
        elistTMP_t = ROOT.gDirectory.Get(tmp)

        if not name:
            return elistTMP_t
        else:
            elistTMP = elistTMP_t.Clone(name)
            del elistTMP_t
            return elistTMP

## The following should really not be used. Why making a framework for doing fast loops and implement a slow one.
#    def getYieldFromLoop(self, selectionString=None, cutFunc = None, weightVar = None, weightFunc = None):
#        ''' Get yield from self.chain according to a cut, a selectionString, a cutFunc, 
#            a weight variable (must be a TLeafElement) and a weight function.
#            This is deprecated and very slow.
#        '''
#        eList = self.getEList(selectionString)
#        res = 0.
#        resVar=0.
#
#        for i in range(eList.GetN()):
#            self.chain.GetEntry(eList.GetEntry(i))
#            if (not cutFunc) or cutFunc(self.chain):
#                w = getattr(self.chain, weightVar) if weightVar else 1
#                if not isinstance(w, numbers.Number):
#                    raise ValueError ("Problem with weightVar argument %s. Evaluates to %r"%(weightVar, w))
#                w *= weightFunc(self.chain) if weightFunc else 1
#                res += w
#                resVar += w**2
#        del eList
#        # Should remove this unecessary dependency
#        return u_float.u_float(res, sqrt(resVar) )

    def getYieldFromDraw(self, selectionString = None, weightString = None):
        ''' Get yield from self.chain according to a selectionString and a weightString
        ''' 
        tmp=str(uuid.uuid4())
        h = ROOT.TH1D(tmp, tmp, 1,0,2)
        h.Sumw2()
        weight = weightString if weightString else "1"
        cut = selectionString if selectionString else "1"
        self.chain.Draw("1>>"+tmp, "("+weight+")*("+cut+")", 'goff')
        res = h.GetBinContent(1)
        resErr = h.GetBinError(1)
        del h

        ## Should remove this unecessary dependency
        #return u_float.u_float( res, resErr )
        
        return {'val': res, 'sigma':resErr}        

    def getHistoFromDraw(self, variableString, binning, selectionString = None, weightString = None, binningIsExplicit = False, addOverFlowBin = None):
        ''' Get TH1D/TH2D from draw command using selectionString, weight. If binningIsExplicit is true, 
            the binning argument (a list) is translated into variable bin widths. 
            addOverFlowBin can be 'upper', 'lower', 'both' and will add 
            the corresponding overflow bin to the last bin of a 1D histogram'''
        is2D = len(binning)==6 
        tmp=str(uuid.uuid4())
        if binningIsExplicit:
            res = ROOT.TH1D(tmp, tmp, len(binning)-1, array('d', binning))
        else:
            if is2D:
                res = ROOT.TH2D(tmp, tmp, *binning)
            else:
                res = ROOT.TH1D(tmp, tmp, *binning)
        weight = weightString if weightString else "1"
        self.chain.Draw(variableString+">>"+tmp, weight+"*("+selectionString+")", 'goff')

        if not is2D:
            if addOverFlowBin.lower() == "upper" or addOverFlowBin.lower() == "both":
                nbins = res.GetNbinsX()
                res.SetBinContent(nbins , res.GetBinContent(nbins) + res.GetBinContent(nbins + 1))
                res.SetBinError(nbins , sqrt(res.GetBinError(nbins)**2 + res.GetBinError(nbins + 1)**2))
            if addOverFlowBin.lower() == "lower" or addOverFlowBin.lower() == "both":
                res.SetBinContent(1 , res.GetBinContent(0) + res.GetBinContent(1))
                res.SetBinError(1 , sqrt(res.GetBinError(0)**2 + res.GetBinError(1)**2))

        return res

