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
