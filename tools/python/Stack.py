''' A stack of samples (not plots) 
'''

from RootTools.tools.Sample import Sample

class Stack ( list ):
        
    def __init__(self, *stackList):

        # change [[...], X, [...] ...]  to [[...], [X], [...], ...]
        stackList = [ s if type(s)==type([]) else [s] for s in stackList]

        # Check the input. LBYL.
        for s in stackList:
            for p in s:
                if  not isinstance(p, Sample):
                    raise ValueError("Found smth else than a Sample insstance ( '%r' ) in Argument '%r'."%(p, stackList) )

        super(Stack, self).__init__( stackList ) 
