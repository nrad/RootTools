import ROOT
import os

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
    if not all( (type(s) == type("") or s is None) for s in selectionStringList):
        raise ValueError( "Don't know what to do with selectionStringList '%r'"%selectionStringList)

    list_ = [s for s in selectionStringList if not s is None ]
    if len(list_)==0:
        return "(1)"
    else:
        return stringOperator.join('('+s+')' for s in list_)

def lineStyle( color, width = None):
    def func( histo ):
        histo.SetLineColor( color )
        histo.SetMarkerSize( 0 )
        histo.SetMarkerStyle( 0 )
        histo.SetMarkerColor( color )
        histo.SetFillColor( 0 )
        if width: histo.SetLineWidth( width )
        return 
    return func

def uses(func, args):
    ''' Decorates a filler function with a list of strings of the used branch names
    '''
    if type(args)==type(""):
        args=[args]
    if not all(type(s)==type("") for s in args):
        raise ValueError( "Need string or list of strings as argument, got '%r'"%args)
    func.uses = args
    return func

