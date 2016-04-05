''' What is a plot?
'''

# Standard imports
import ROOT
from math import sqrt

def addOverFlowBin1D( histo, addOverFlowBin = None):

    if not any( isinstance(histo, o) for o in [ROOT.TH1, ROOT.TProfile]):
        raise NotImplementedError( "Can add overflow bin only to 1D histos. Got %r" %histo )

    if addOverFlowBin is not None:
        if addOverFlowBin.lower() == "upper" or addOverFlowBin.lower() == "both":
            nbins = histo.GetNbinsX()
            histo.SetBinContent(nbins , histo.GetBinContent(nbins) + histo.GetBinContent(nbins + 1))
            histo.SetBinError(nbins , sqrt(histo.GetBinError(nbins)**2 + histo.GetBinError(nbins + 1)**2))
        if addOverFlowBin.lower() == "lower" or addOverFlowBin.lower() == "both":
            histo.SetBinContent(1 , histo.GetBinContent(0) + histo.GetBinContent(1))
            histo.SetBinError(1 , sqrt(histo.GetBinError(0)**2 + histo.GetBinError(1)**2))

class Plot( object ):

    def __init__(self, stack, variable,  binning, name = None, selectionString = None, weight = None, histo_class = ROOT.TH1F, 
                 texX = "", texY = "Number of Events", addOverFlowBin = None):
        ''' A plot needs a
        'stack' of Sample instances, e.g. [[mc1, mc2, ...], [data], [signal1, signal2,...]], a
        'variable' instance, either with a filler or with the name of a data member, a
        'selectionString' to be used on top of each samples selectionString, a
        'weight' function, a 
        'hist_class', e.g. ROOT.TH1F or ROOT.TProfile1D
        'texX', 'texY' labels for x and y axis and a
        ''' 
        self.name = name
        self.stack = stack
        self.variable = variable
        self.binning = binning
        self.selectionString = selectionString
        self.weight = weight
        self.histo_class = histo_class
        self.texX = texX
        self.texY = texY
        self.addOverFlowBin = addOverFlowBin

    @classmethod
    def fromHisto(cls, name, histos, texX= "", texY = "Number of Events"):
        res = cls(stack=None, name=name, variable=None, binning=None, selectionString = None, weight = None, histo_class = None,\
            texX = texX, texY = texY)
        res.histos = histos
        return res
