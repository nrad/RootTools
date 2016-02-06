''' Implementation of a Variable.
Used in the Loopers and for plotting.
'''

# standard imports
import re 

# Translation of short types to ROOT C types
cStringTypeDict = {
    'b': 'UChar_t',
    'S': 'Short_t',
    's': 'UShort_t',
    'I': 'Int_t',
    'i': 'UInt_t',
    'F': 'Float_t',
    'D': 'Double_t',
    'L': 'Long64_t',
    'l': 'ULong64_t',
    'O': 'Bool_t',
}
# reversed
shortTypeDict = {v: k for k, v in cStringTypeDict.items()}

# defaults
defaultTypeDict = {
    'b': '0',
    'S': '-1',
    's': '0',
    'I': '-1',
    'i': '0',
    'F': 'TMath::QuietNaN()',
    'D': 'TMath::QuietNaN()',
    'L': '-1',
    'l': '-1',
    'O': '0',
}

allTypes  = set(cStringTypeDict.keys())
allCTypes = set(cStringTypeDict.values())

class Variable( object ):

    def __init__( self, name, tp, dim = 'scalar', filler = None, default = None, nMax = None):
        ''' Initialize variable. 
            tp: shortcut for ROOT type (b/s/S/I/i/F/D/L/l/O) or the corresponding C ROOT types, 
            dim is 'scalar' or 'vector',
            filler is a function that fills the variable,
            default is the value the variable will be initialized with,
            nMax is the maximal length of the vector in memory (if not specified: 100)
        '''
        self.name = name

        assert tp in allTypes.union( allCTypes ), "Type %r not known"%tp
        # translate type to short form
        self.tp = tp if tp in allTypes else shortTypeDict[tp]

        self.filler = filler
        
        # Scalar or Vvctor?
        assert dim in ['scalar', 'vector'], "dim(ension) must be either scalar or vector. Got '%r'"%dim
        self.dim = dim

        assert not ( dim=='scalar' and nMax is not None ), "nMax argument only for vector" 
        self.nMax = nMax
        if dim=='vector':
            # Use 100 if not specified
            self.nMax = nMax if nMax is not None else 100 

        # store default
        self.default = default if default is not None else defaultTypeDict[self.tp]

    @classmethod
    def scalar(name, tp, filler = None, default = None): 
        return cls(dim = 'scalar', name = name, tp = tp, filler = None, default = None, nMax = None)

    def vector(name, tp, filler = None, default = None): 
        return cls(dim = 'vector', name = name, tp = tp, filler = None, default = None, nMax = None)

    @classmethod
    def fromString(cls, string):
        '''Create scalar variable from name/type
           or vector variable from name/type[], name/type[nMax]
        '''
        if not type(string)==type(""): raise ValueError( "Expected string got '%r'"%string )
        string = string.replace(' ', '')
        assert string.count('/')==1, "Could not parse string '%s'"%string

        nMax = None
        dim = 'scalar' if not "[]" in string else "vector"
        string = string.replace("[]", "")
            
        name, tp_ = string.split('/')
        try:
            if tp_.count('[') == tp_.count(']') == 1:
                dim = 'vector'
                lst_ =  re.findall(r"[\w']+", tp_)
                if len(lst_)==1:
                    tp  = lst_[0]
                elif len(lst_)==2:
                    tp, nMaxStr = lst_
                    nMax = int(nMaxStr)
                else:
                    raise ValueError()
            else:
                tp = tp_
        except:
            raise ValueError("Could not interpret string '%s')"%string)
        return cls( name = name, tp = tp, dim = dim, nMax = nMax)

    def __str__(self):
        return "%s (type: %s, dim: %s, nMax: %i" %(self. name, self.tp, self.dim, self.nMax)
