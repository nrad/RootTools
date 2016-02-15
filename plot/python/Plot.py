''' What is a plot?
'''

# Standard imports
import ROOT

class Plot( object ):

    def __init__(self, stack, variable,  binning, selectionString = None, weight = None, histo_class = ROOT.TH1F, 
                 texX = "", texY = "Number of Events"):
        
        self.stack = stack
        self.variable = variable
        self.binning = binning
        self.selectionString = selectionString
        self.weight = weight
        self.histo_class = histo_class
        self.texX = texX
        self.texY = texY
