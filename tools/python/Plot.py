''' What is a plot?
'''

class Plot( object ):

    def __init__(self, var, binning, cutString, varFunc = None, cutFunc = None, weightVar = None, weightFunc = None):

        assert ( not (var and varFunc) ) and ( var or varFunc), "Specify exactly one: var (is '%r') or varFunc (is '%r')"%(var,varFunc)
        self.var            = var
        self.varFunc        = varFunc
        self.cutString      = cutString
        self.cutFunc        = cutFunc
        self.weightVar      = weightVar
        self.weightFunc     = weightFunc
        
