''' Base class for a sample.
    Implements definition and handling of the TChain.
'''

#Abstract Base Class
import abc

# Standard imports
import ROOT
import uuid
import numbers
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

class SampleBase ( object ): # 'object' argument will disappear in Python 3
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, name, treeName ):
        ''' Base class constructor for all sample classes.
            name: Name of the sample, treeName: name of the TTree in the input files
        '''
        self.name = name
        self.treeName = treeName
        self.files = []
        logger.debug("Created new sample %s with treeName %s.", name, treeName)

# Overloading getattr: Requesting sample.chain prompts the loading of the TChain.
    def __getattr__(self, name):
        '''Overload getattr such that self.chain is automatically created when asked for.
        '''
        if name=="chain":
            logger.debug("First request of attribute 'chain' for sample %s. Calling __loadChain", self.name)
            self.__loadChain()
            return self.chain
        else:
            raise AttributeError

# "Private" method that loads the chain from self.files
    def __loadChain(self):
        ''' Load the TChain. Private.
        '''
        if len(self.files) == 0:
            raise EmptySampleError("Sample {name} has no input files! Can not load.".format(name = self.name) )
        else:
            self.chain = ROOT.TChain(self.treeName)
            counter = 0
            for f in self.files:
                logger.debug("Now adding file %s to sample '%s'", f, self.name)
                try:
                    if helpers.checkRootFile(f, checkForObjects=[self.treeName]):
                        self.chain.Add(f)
                        counter+=1
                except IOError:
                    pass
                    logger.warning( "Could not load file %s", f )
            logger.debug( "Loaded %i files for sample '%s'.", counter, self.name )

    def clear(self): #FIXME How to promote to destructor without making it segfault?
        ''' Really (in the ROOT namespace) delete the chain
        '''
        if self.chain:
            self.chain.IsA().Destructor( self.chain )
            self.chain = None
            logger.debug("Called TChain Destructor for sample '%s'.", self.name)

    def reader(self, **kwargs):
        ''' Return a reader of the sample
        '''
        from RootTools.Looper.Reader import Reader
        logger.debug("Creating Reader object for sample '%s'.", self.name)
        self.reader = Reader( self, **kwargs )
        return self.reader

#    def __del__(self): #Will be executed when the refrence count is zero
#        '''Calling the TChain Destructor.
#        '''
#        self.clear()

    def getEList(self, selectionString=None, name=None):
        ''' Get a TEventList from a selectionString
        '''

        tmp=str(uuid.uuid4())
        self.chain.Draw('>>'+tmp, selectionString if selectionString else "(1)")
        elistTMP_t = ROOT.gDirectory.Get(tmp)

        if not name:
            return elistTMP_t
        else:
            elistTMP = elistTMP_t.Clone(name)
            del elistTMP_t
            return elistTMP

    def getYieldFromLoop(self, selectionString=None, cutFunc = None, weightVar = None, weightFunc = None):
        ''' Get yield from self.chain according to a cut, a selectionString, a cutFunc, 
            a weight variable (must be a TLeafElement) and a weight function.
            This is deprecated and very slow.
        '''
        eList = self.getEList(selectionString)
        res = 0.
        resVar=0.

        for i in range(eList.GetN()):
            self.chain.GetEntry(eList.GetEntry(i))
            if (not cutFunc) or cutFunc(self.chain):
                w = getattr(self.chain, weightVar) if weightVar else 1
                if not isinstance(w, numbers.Number):
                    raise ValueError ("Problem with weightVar argument %s. Evaluates to %r"%(weightVar, w))
                w *= weightFunc(self.chain) if weightFunc else 1
                res += w
                resVar += w**2
        del eList
        return u_float.u_float(res, sqrt(resVar) )

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
        return u_float.u_float( res, resErr )

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

