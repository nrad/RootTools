''' A stack of samples (not plots) 
'''

from RootTools.Sample.Sample import Sample

class Stack ( object ):
        
    def __init__( self, stackList ):

        if not type(stackList) == type([]) or not all( type(s)==type([]) for s in stackList ):
            raise ValueError("'stackList' must be a list of lists of Sample insstance. Got '%r'"%stackLists )

        self.stackList = stackList
