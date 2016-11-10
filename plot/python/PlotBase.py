''' What is a plot?
'''

# Abstract base class
import abc

# Standard imports
import ROOT
from math import sqrt

# RootTools
from RootTools.core.TreeVariable import ScalarTreeVariable, TreeVariable

class PlotBase( object ):
    __metaclass__ = abc.ABCMeta

    def __init__(self, stack = None, name = None, attributes = None, selectionString = None, weight = None,
                 texX = None, texY = None, read_variables = []):
        ''' Base class for all plots
        '''
        self.stack           = stack
        self.selectionString = selectionString
        self.weight          = weight
        self.texX            = texX
        self.texY            = texY
        self.name            = name
        self.attributes      = attributes
        self.read_variables  = read_variables

    @property
    def tree_variables( self ):
        variables = [attribute for attribute in self.attributes if isinstance( attribute, ScalarTreeVariable) ]
        for var in self.read_variables:
            if isinstance(var, TreeVariable):
                variables.append( var )
            elif isinstance(var, str):
                variables.append( TreeVariable.fromString( var ) )
            else:
                raise ValueError( "Don't know what to do with %r." % var )            
        return variables
    
    @property 
    def fillers( self ):
        fillers = []
        for attribute in self.attributes:
            if type(attribute)==str:
                fillers.append( lambda event, sample: getattr( event, attribute ) )
            elif hasattr( attribute, '__call__'):
                fillers.append( attribute )
            elif isinstance( attribute, ScalarTreeVariable ):
                fillers.append( lambda event, sample: getattr( event, attribute.name ) )
            else:
                raise ValueError( "Don't know what to do with attribute %r" % attribute )
        return fillers
            

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
