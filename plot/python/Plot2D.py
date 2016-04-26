''' What is a 2D plot?
'''

# Standard imports
import ROOT

#RootTools
from RootTools.plot.PlotBase import PlotBase

class Plot2D( PlotBase ):

    defaultStack           = None
    defaultVariables       = None
    defaultBinning         = None
    defaultName            = None
    defaultSelectionString = None
    defaultWeight          = None
    defaultHistoClass      = ROOT.TH2F
    defaultTexX            = "variable x"
    defaultTexY            = "variable y"

    @staticmethod
    def setDefaults(stack = None, variables = None, binning = None, name = None, selectionString = None, weight = None, histo_class = ROOT.TH2F,
                 texX = "", texY = "Number of events"):
        Plot2D.defaultStack           = stack
        Plot2D.defaultVariables       = variables
        Plot2D.defaultBinning         = binning
        Plot2D.defaultName            = name
        Plot2D.defaultSelectionString = selectionString
        Plot2D.defaultWeight          = staticmethod(weight)
        Plot2D.defaultHistoClass      = histo_class
        Plot2D.defaultTexX            = texX
        Plot2D.defaultTexY            = texY

    def __init__(self, stack = None, variables = None, binning = None, name = None, selectionString = None, weight = None, histo_class = None,
                 texX = None, texY = None):
        ''' A 2D plot needs a
        'stack' of Sample instances, e.g. [[mc1, mc2, ...], [data], [signal1, signal2,...]], a
        'variables' list of instances of Variable (x,y), either with a filler or with the name of a data member, a
        'selectionString' to be used on top of each samples selectionString, a
        'weight' function, a 
        'hist_class', e.g. ROOT.TH2F or ROOT.TProfile2D
        'texX', 'texY' labels for x and y axis and a
        ''' 

        super(Plot2D, self).__init__( \
            stack           = stack            if stack           is not None else Plot2D.defaultStack,
            selectionString = selectionString  if selectionString is not None else Plot2D.defaultSelectionString,
            weight          = weight           if weight          is not None else Plot2D.defaultWeight,
            texX            = texX             if texX            is not None else Plot2D.defaultTexX,
            texY            = texY             if texY            is not None else Plot2D.defaultTexY,
            name            = name             if name            is not None else Plot2D.defaultName if Plot2D.defaultName is not None else "_vs_".join(variable.name for variable in variables)
        )

        self.variables       = variables        if variables       is not None else Plot2D.defaultVariables
        self.binning         = binning          if binning         is not None else Plot2D.defaultBinning
        self.histo_class     = histo_class      if histo_class     is not None else Plot2D.defaultHistoClass

    @classmethod
    def fromHisto(cls, name, histos, texX = defaultTexX, texY = defaultTexY):
        res = cls(stack=None, name=name, variables=None, binning=None, selectionString = None, weight = None, histo_class = None,\
            texX = texX, texY = texY)
        res.histos = histos
        return res
