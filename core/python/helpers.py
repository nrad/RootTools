import ROOT
import os

class EmptySampleError(Exception):
    '''Accessing a sample without ROOT files.
    '''
    pass

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
defaultCTypeDict = {
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


# Decorator to have smth like a static variable
def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate

 
def checkRootFile(f, checkForObjects=[] ):
    ''' Checks whether a root file exists, was not recoverd or otherwise broken and
    contains the objects in 'checkForObjects'
    '''
    if not os.path.exists(f): raise IOError("File {0} not found".format(f))
    rf = ROOT.TFile.Open(f)
    if not rf: raise IOError("File {0} could not be opened. Not a root file?".format(f))
    good = (not rf.IsZombie()) and (not rf.TestBit(ROOT.TFile.kRecovered))

    if not good: 
        rf.Close()
        return False

    for o in checkForObjects:
        if not rf.GetListOfKeys().Contains(o):
            rf.Close()
            return False 

    rf.Close()
    return True

def combineSelectionStrings( selectionStringList = [], stringOperator = "&&"):
    '''Expects a list of string based cuts and combines them to a single string using stringOperator
    '''
    if selectionStringList is None: return "(1)"

    if not all( (type(s) == type("") or s is None) for s in selectionStringList):
        raise ValueError( "Don't know what to do with selectionStringList %r"%selectionStringList)

    list_ = [s for s in selectionStringList if not s is None ]
    if len(list_)==0:
        return "(1)"
    elif len(list_)==1:
        return list_[0]
    else:
        return stringOperator.join('('+s+')' for s in list_)

def fromString(*args):
    ''' Make a list of Variables from the input arguments
    '''
    from RootTools.core.Variable import Variable
    args = sum( [ [s] if type(s)==type("") else s for s in args if s is not None], [])
    if not all(type(s)==type("") or isinstance(s, Variable) for s in args):
        raise ValueError( "Need string or Variable instance or list of these as argument, got %r"%args)
    return tuple(map(lambda s:Variable.fromString(s) if type(s)==type("") else s, args))

def uses(func, args):
    ''' Decorates a filler function with a list of strings of the used branch names
    '''
    func.arguments = fromString( args )
    return func

def clone(root_object, new_name = None):
    ''' Cloning a ROOT class instance and preserving attributes
    '''
    new = root_object.Clone() if new_name is None else root_object.Clone(new_name)
    new.__dict__.update(root_object.__dict__)
    return new 
