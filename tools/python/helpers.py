import ROOT
import os
 
def checkRootFile(f, checkForObjects=[] ):

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
