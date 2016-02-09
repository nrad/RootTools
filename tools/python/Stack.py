''' A stack of samples (not plots) 
'''

from RootTools.tools.Sample import Sample

class Stack ( list ):
        
    def __init__(self, *stackList):
        list.__init__(self, *stackList)

        if  not all( type(s)==type([]) for s in self ):
            raise ValueError("'stackList' must be a list of lists of Sample insstance. Got '%r'"%self )

