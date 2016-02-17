''' A stack of samples (not plots).
Must be a list of lists.
'''
# Standard imports
import uuid

# RootTools
from RootTools.core.Sample import Sample
from RootTools.plot.Plot import Plot
from RootTools.plot.Immutable import Immutable

class Stack ( list ):
        
    def __init__(self, *stackList):

        # change [[...], X, [...] ...]  to [[...], [X], [...], ...]
        stackList = [ s if type(s)==type([]) else [s] for s in stackList]

        # Check the input. LBYL.
        for s in stackList:
            if not type(s)==type([]) or not all(isinstance(p, Sample) for p in s):
                raise ValueError("Stack should be a list of lists of Sample instances. Got %r."%( stackList ) )

        # Make Immutable
        stackList = map(lambda l: map(lambda s:Immutable(s), l), stackList)

        super(Stack, self).__init__( stackList )

    def samples(self):
        ''' Get all unique samples for this stack
        '''
        return list(set(sum(self,[])))

    def make_histos(self, plot):
        '''Make histograms for plot for this stack. Structure is list of lists of histos parallel to the stack object
        '''
        res = []
        for i, l in enumerate(self):
            histos = [] 
            for j, s in enumerate(l):
                histo = plot.histo_class(\
                    "_".join([plot.variable.name, s.name, str(uuid.uuid4()).replace('-','_')]), 
                    "_".join([plot.variable.name, s.name]), 
                     *plot.binning )
                histo.Reset()
                # Exectute style function on histo
                if hasattr(s, "style"):
                    s.style(histo)

                histos.append(histo)
            res.append(histos)
            
        return res 

    def getSampleIndicesInStack(self, sample):
        ''' Find the indices of a sample in the stack
        '''
        indices = []
        for i, l in enumerate(self):
            for j, s in enumerate(l):
                if s==sample: indices.append((i,j))
        return indices
