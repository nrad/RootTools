''' What is a plot?
'''

# Abstract base class
import abc

# Standard imports
import ROOT
from math import sqrt

class PlotBase( object ):
    __metaclass__ = abc.ABCMeta

    def __init__(self, stack = None, name = None, variables = None, selectionString = None, weight = None,
                 texX = None, texY = None):
        ''' Base class for all plots
        '''
        self.stack           = stack
        self.selectionString = selectionString
        self.weight          = weight
        self.texX            = texX
        self.texY            = texY
        self.name            = name
        self.variables       = variables

    @property
    def histos_added(self):
        ''' Returns [[h1], [h2], ...] where h_i are the sums of all histograms in the i-th copmponent of the plot.
        '''

        if not hasattr(self, "histos"):
            raise AttributeError( "Plot %r has no attribute 'histos'. Did you forget to fill?"%self.name )
        res = [ [ h[0].Clone( h[0].GetName()+"_clone" ) ] for h in self.histos]
        for i, h in enumerate( self.histos ):
            for p in h[1:]:
                res[i][0].Add( p )
        return res
