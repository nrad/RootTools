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

    defaultStack           = None
    defaultVariable        = None
    defaultBinning         = None
    defaultName            = None
    defaultSelectionString = None
    defaultWeight          = None
    defaultHistoClass      = ROOT.TH1F
    defaultTexX            = ""
    defaultTexY            = "Number of Events"
    defaultAddOverFlowBin  = None

    @staticmethod
    def setDefaults(stack = None, variable = None, binning = None, name = None, selectionString = None, weight = None, histo_class = ROOT.TH1F,
                 texX = "", texY = "Number of events", addOverFlowBin = None):
        Plot.defaultStack           = stack
        Plot.defaultVariable        = variable
        Plot.defaultBinning         = binning
        Plot.defaultName            = name
        Plot.defaultSelectionString = selectionString
        Plot.defaultWeight          = staticmethod(weight)
        Plot.defaultHistoClass      = histo_class
        Plot.defaultTexX            = texX
        Plot.defaultTexY            = texY
        Plot.defaultAddOverFlowBin  = addOverFlowBin


    def __init__(self, stack = None, variable = None, binning = None, name = None, selectionString = None, weight = None, histo_class = None,
                 texX = None, texY = None, addOverFlowBin = None):
        ''' A plot needs a
        'stack' of Sample instances, e.g. [[mc1, mc2, ...], [data], [signal1, signal2,...]], a
        'variable' instance, either with a filler or with the name of a data member, a
        'selectionString' to be used on top of each samples selectionString, a
        'weight' function, a 
        'hist_class', e.g. ROOT.TH1F or ROOT.TProfile1D
        'texX', 'texY' labels for x and y axis and a
        ''' 
        self.stack           = stack            if stack           is not None else Plot.defaultStack
        self.variable        = variable         if variable        is not None else Plot.defaultVariable
        self.binning         = binning          if binning         is not None else Plot.defaultBinning
        self.selectionString = selectionString  if selectionString is not None else Plot.defaultSelectionString
        self.weight          = weight           if weight          is not None else Plot.defaultWeight
        self.histo_class     = histo_class      if histo_class     is not None else Plot.defaultHistoClass
        self.texX            = texX             if texX            is not None else Plot.defaultTexX
        self.texY            = texY             if texY            is not None else Plot.defaultTexY
        self.addOverFlowBin  = addOverFlowBin   if addOverFlowBin  is not None else Plot.defaultAddOverFlowBin
        self.name            = name             if name            is not None else Plot.defaultName if Plot.defaultName is not None else variable.name

    @classmethod
    def fromHisto(cls, name, histos, texX= "", texY = "Number of Events"):
        res = cls(stack=None, name=name, variable=None, binning=None, selectionString = None, weight = None, histo_class = None,\
            texX = texX, texY = texY)
        res.histos = histos
        return res

    @property
    def histos_added(self):
        ''' Returns [[h1], [h2], ...] where h_i are the sums of all histograms in the i-th copmponent of the plot.
        '''

        if not hasattr(self, "histos"):
            raise AttributeError( "Plot %r has no attribute 'histos'. Did you forget to fill?" )
        res = [ [ h[0].Clone( h[0].GetName()+"_clone" ) ] for h in self.histos]
        for i, h in enumerate( self.histos ):
            for p in h[1:]:
                res[i][0].Add( p )
        return res
         
            
