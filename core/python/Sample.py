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
import RootTools.core.helpers as helpers

@helpers.static_vars(sampleCounter = 0)
def newName():
    result = "Sample_"+str(newName.sampleCounter)
    newName.sampleCounter += 1
    return result

class Sample ( object ): # 'object' argument will disappear in Python 3

    def __init__(self, name, treeName , files = [], normalization = None, selectionString = None, isData = False, color = 0, texName = None):
        ''' Handling of sample. Uses a TChain to handle root files with flat trees.
            'name': Name of the sample, 
            'treeName': name of the TTree in the input files
            'normalization': can be set in order to later calculate weights, 
            e.g. to total number of events befor all cuts or the sum of NLO gen weights
            'selectionString': sample specific string based selection (can be list of strings)
            'isData': Whether the sample is real data or not (simulation)
            'color': ROOT color to be used in plot scripts
            'texName': ROOT TeX string to be used in legends etc.
        '''

        self.name = name
        self.treeName = treeName
        self.files = files
        if not len(self.files)>0:
          raise helpers.EmptySampleError( "No ROOT files for sample %s! Files: %s" % (sample.name, sample.files) )
        self.normalization = None
        self._chain = None
        
        self.setSelectionString( selectionString )

        self.isData = isData
        self.color = color
        self.texName = texName if not texName is None else name
             
        logger.debug("Created new sample %s with %i files, treeName %s and __selectionStrings %s.", 
            name, len(self.files), treeName, self.__selectionStrings)

    def setSelectionString(self, selectionString):
        if type(selectionString)==type(""):
            self.__selectionStrings = [ selectionString ] 
        elif type(selectionString)==type([]): 
            self.__selectionStrings =  selectionString 
        elif selectionString is None:
            self.__selectionStrings = None
        else:
            raise ValueError( "Don't know what to do with selectionString %r"%selectionString )

        self.clear()

    @property
    def selectionString(self):
        return self.__selectionStrings if type(self.__selectionStrings)==type("") else helpers.combineSelectionStrings(self.__selectionStrings) 

    @classmethod
    def fromFiles(cls, name, files, treeName=None, normalization = None, selectionString = None, isData = False, color = 0, texName = None, maxN = None):
        '''Load sample from files or list of files. If the name is "", enumerate the sample
        '''

        # Work with files and list of files
        files = [files] if type(files)==type("") else files

        # If no name, enumerate them.
        if not name: name = newName()
        if not treeName: 
            treeName = "Events"
            logger.debug("Argument 'treeName' not provided for sample %s, using 'Events'."%name) 

        # restrict files 
        maxN = maxN if maxN is not None and maxN>0 else None
        files = files[:maxN]

        sample =  cls(name = name, treeName = treeName, files = files, normalization = normalization, selectionString = selectionString,\
                        isData = isData, color=color, texName = texName)

        logger.debug("Loaded sample %s from %i files.", name, len(files))
        return sample

    @classmethod
    def fromDirectory(cls, name, directory, treeName = None, normalization = None, selectionString = None, \
                        isData = False, color = 0, texName = None, maxN = None):
        '''Load sample from directory or list of directories. If the name is "", enumerate the sample
        '''
        # Work with directories and list of directories
        directories = [directory] if type(directory)==type("") else directory 

        # If no name, enumerate them.
        if not name: name = newName()

        # find all files
        files = [] 
        for d in directories:
            fileNames = [ os.path.join(d, f) for f in os.listdir(d) if f.endswith('.root') ]
            if len(fileNames) == 0:
                raise helpers.EmptySampleError( "No root files found in directory %s." %d )
            files.extend( fileNames )
        if not treeName: 
            treeName = "Events"
            logger.debug("Argument 'treeName' not provided, using 'Events'.") 

        # restrict files 
        maxN = maxN if maxN is not None and maxN>0 else None
        files = files[:maxN]

        sample =  cls(name = name, treeName = treeName, files = files, normalization = normalization, selectionString = selectionString, \
                        isData = isData, color=color, texName = texName)
        logger.debug("Loaded sample %s from %i files.", name, len(files))
        return sample

    @classmethod
    def fromCMGOutput(cls, name, baseDirectory, treeFilename = 'tree.root', chunkString = None, treeName = 'tree', maxN = None, selectionString = None, \
                        isData = False, color = 0, texName = None):
    
        def readNormalization(filename):
            with open(filename, 'r') as fin:
                for line in fin:
                    if any( [x in line for x in ['All Events', 'Sum Weights'] ] ):
                        sumW = float(line.split()[2])
                        return sumW

        maxN = maxN if maxN is not None and maxN>0 else None

        # Reading all subdirectories in base directory. If chunkString != None, require cmg output name formatting
        chunkDirectories = []

        # FIXME: Better to loop only over subdirectories in base directory?
        for x in os.listdir(baseDirectory): 
            if os.path.isdir(os.path.join(baseDirectory, x)):
                if not chunkString or (x.startswith(chunkString) and x.endswith('_Chunk')) or x==chunkString:
                    chunkDirectories.append(os.path.join(baseDirectory, x))
                    if len(chunkDirectories)==maxN:break

        logger.debug( "Found %i chunk directories with chunkString %s in base directory %s", \
                           len(chunkDirectories), chunkString, baseDirectory )
        normalization = 0
        files = []
        failedChunks=[]
        goodChunks  =[]

        for i, chunkDirectory in enumerate( chunkDirectories ):
            success = False
            logger.debug("Reading chunk %s", chunkDirectory)

            # Find normalization
            sumW = None
            for root, subFolders, filenames in os.walk( chunkDirectory ):
                # Determine normalization constant
                if 'SkimReport.txt' in filenames:
                    skimReportFilename = os.path.join(root, 'SkimReport.txt')
                    sumW = readNormalization( skimReportFilename )
                    if not sumW:
                        logger.warning( "Read chunk %s and found report '%s' but could not read normalization.",
                                             chunkDirectory, skimReportFilename )
            # Find treefile
            treeFile = None
            for root, subFolders, filenames in os.walk( chunkDirectory ):
                # Load tree file 
                if treeFilename in filenames:
                    treeFile = os.path.join(root, treeFilename)
                    # Checking whether root file is OG and contains a tree
                    if not helpers.checkRootFile(treeFile, checkForObjects=[treeName] ):
                        logger.warning( "Read chunk %s and found tree file '%s' but file looks broken.",  chunkDirectory, treeFile )

            # If both, normalization and treefile are OK call it successful.
            if sumW and treeFile:
                files.append( treeFile )
                normalization += sumW
                logger.debug( "Successfully read chunk %s and incremented normalization by %7.2f",  chunkDirectory, sumW )
                success = True
                goodChunks.append( chunkDirectory )

            if not success:
                failedChunks.append( chunkDirectory )

        # Don't allow empty samples
        if len(goodChunks) == 0:
            raise helpers.EmptySampleError("Could not find good CMGOutput chunks for sample {0}. Total number of chunks: {1}. baseDirectory: {2}"\
                  .format(name, len(chunkDirectories), baseDirectory))

        # Log statements
        eff = 100*len(failedChunks)/float( len(chunkDirectories) )
        logger.debug("Loaded CMGOutput sample %s. Total number of chunks : %i. Normalization: %7.2f Bad: %i. Inefficiency: %3.3f", \
                          name, len(chunkDirectories), normalization, len(failedChunks), eff)

        for chunk in failedChunks:
            logger.debug( "Failed to load chunk %s", chunk)
        return cls( name = name, treeName = treeName, files = files, normalization = normalization, selectionString = selectionString, \
                    isData = isData, color = color, texName = texName )

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
            raise helpers.EmptySampleError("Sample {name} has no input files! Can not load.".format(name = self.name) )
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
        return

    def treeReader(self, **kwargs):
        ''' Return a Reader class for the sample
        '''
        from TreeReader import TreeReader
        logger.debug("Creating TreeReader object for sample '%s'.", self.name)
        return TreeReader( self, **kwargs )

    # Below some helper functions to get useful 

    def combineWithSampleSelection(self, selectionString):
        if selectionString is None: return self.selectionString
        if not type(selectionString)==type(""): raise ValueError( "Need 'None' or string for selectionString, got %s" % selectionString )
        if self.__selectionStrings:
            logger.debug("For Sample %s: Combining selectionString %s with sample selectionString %s", \
                self.name, selectionString, self.selectionString )
            return helpers.combineSelectionStrings( [selectionString]+self.__selectionStrings )
        else:
            logger.debug("For Sample %s: Return selectionString %s because sample has no selectionString", \
                self.name, selectionString )
            return selectionString

    def getEList(self, selectionString=None, name=None):
        ''' Get a TEventList from a selectionString (combined with self.selectionString, if exists).
        '''

        selectionString_ = self.combineWithSampleSelection( selectionString )

        tmp=str(uuid.uuid4())
        logger.debug( "Making eList for sample %s and selectionString %s", self.name, selectionString_ )
        self.chain.Draw('>>'+tmp, selectionString_ if selectionString else "(1)")
        elistTMP_t = ROOT.gDirectory.Get(tmp)

        if not name:
            return elistTMP_t
        else:
            elistTMP = elistTMP_t.Clone(name)
            del elistTMP_t
            return elistTMP

    def getYieldFromDraw(self, selectionString = None, weightString = None):
        ''' Get yield from self.chain according to a selectionString and a weightString
        ''' 

        selectionString_ = self.combineWithSampleSelection( selectionString )

        tmp=str(uuid.uuid4())
        h = ROOT.TH1D(tmp, tmp, 1,0,2)
        h.Sumw2()
        weight = weightString if weightString else "1"
        self.chain.Draw("1>>"+tmp, "("+weight+")*("+selectionString_+")", 'goff')
        res = h.GetBinContent(1)
        resErr = h.GetBinError(1)
        del h

        ## Should remove this unecessary dependency
        #return u_float.u_float( res, resErr )
        
        return {'val': res, 'sigma':resErr}        

    def get1DHistoFromDraw(self, variableString, binning, selectionString = None, weightString = None, binningIsExplicit = False, addOverFlowBin = None, isProfile = False):
        ''' Get TH1D/TProfile1D from draw command using selectionString, weight. If binningIsExplicit is true, 
            the binning argument (a list) is translated into variable bin widths. 
            addOverFlowBin can be 'upper', 'lower', 'both' and will add 
            the corresponding overflow bin to the last bin of a 1D histogram'''

        selectionString_ = self.combineWithSampleSelection( selectionString )

        tmp=str(uuid.uuid4())
        if binningIsExplicit:
            binningArgs = (len(binning)-1, array('d', binning))
        else:
            binningArgs = binning

        cls = ROOT.TProfile if isProfile else ROOT.TH1D

        res = cls(tmp, tmp, *binningArgs)

        weight = weightString if weightString else "1"

        self.chain.Draw(variableString+">>"+tmp, weight+"*("+selectionString_+")", 'goff')

        if addOverFlowBin is not None:
            if addOverFlowBin.lower() == "upper" or addOverFlowBin.lower() == "both":
                nbins = res.GetNbinsX()
                res.SetBinContent(nbins , res.GetBinContent(nbins) + res.GetBinContent(nbins + 1))
                res.SetBinError(nbins , sqrt(res.GetBinError(nbins)**2 + res.GetBinError(nbins + 1)**2))
            if addOverFlowBin.lower() == "lower" or addOverFlowBin.lower() == "both":
                res.SetBinContent(1 , res.GetBinContent(0) + res.GetBinContent(1))
                res.SetBinError(1 , sqrt(res.GetBinError(0)**2 + res.GetBinError(1)**2))

        return res

    def get2DHistoFromDraw(self, variableString, binning, selectionString = None, weightString = None, binningIsExplicit = False, addOverFlowBin = None, isProfile = False):
        ''' Get TH2D/TProfile2D from draw command using selectionString, weight. If binningIsExplicit is true, 
            the binning argument (a tuple of two lists) is translated into variable bin widths. 
        '''

        selectionString_ = self.combineWithSampleSelection( selectionString )

        tmp=str(uuid.uuid4())
        if binningIsExplicit:
            if not len(binning)==2 and type(binning)==type(()):
                raise ValueError( "Need a tuple with two lists corresponding to variable bin thresholds for x and y axis. Got % s"% binning )
            binningArgs = (len(binning[0])-1, array('d', binning[0]), len(binning[1])-1, array('d', binning[1]))
        else:
            if not len(binning)==6:
                raise ValueError( "Need binning in standard 2D form: [nBinsx,xLow,xHigh,nBinsy,yLow,yHigh]. Got %s" % binning )
            binningArgs = binning

        if isProfile:
            cls = ROOT.TProfile2D 
        else:
            cls = ROOT.TH2D

        res = cls(tmp, tmp, *binningArgs)

        weight = weightString if weightString else "1"

        self.chain.Draw(variableString+">>"+tmp, weight+"*("+selectionString_+")", 'goff')

        return res
