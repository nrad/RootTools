''' What is a plot?
'''

# Standard imports
import ROOT

class Plot( object ):

    def __init__(self, stack, variable,  binning, name = None, selectionString = None, weight = None, histo_class = ROOT.TH1F, 
                 texX = "", texY = "Number of Events"):
        ''' A plot needs a
        'stack' of Sample instances, e.g. [[mc1, mc2, ...], [data], [signal1, signal2,...]], a
        'variable' instance, either with a filler or with the name of a data member, a
        'selectionStrong' to be used on top of each samples selectionString, a
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
