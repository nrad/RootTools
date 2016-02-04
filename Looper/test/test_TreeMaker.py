# Standard imports
import sys
import logging
import ROOT

#RootTools
from RootTools.Sample.CMGOutput import CMGOutput
from RootTools.Sample.SampleFromFiles import SampleFromFiles
from RootTools.Looper.TreeReader import TreeReader
from RootTools.Looper.TreeMaker import TreeMaker

# create logger
logger = logging.getLogger("RootTools")
logger.setLevel(logging.INFO)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

td = "/data/rschoefbeck/cmgTuples/MC25ns_v2_1l_151218/TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISpring15MiniAODv2-74X_mcRun2_asymptotic_v2_ext1-v1/"
#s1 = CMGOutput("TTJetsDilep", baseDirectory = td, treeFilename = 'tree.root', treeName = 'tree')
s2 = SampleFromFiles("TTZ", files = ["/afs/hephy.at/data/rschoefbeck01/cmgTuples/postProcessed_mAODv2/dilep/TTZToQQ/TTZToQQ_0.root"])

vectors_read   =    [ {'name':'Jet', 'nMax':100,'variables': ['pt/F'] } ]
scalars_read   =    [ 'met_pt/F' ]
vectors_write  =    [ {'name':'MyJet', 'nMax':100,'variables': ['pt/F'] } ]
scalars_write  =    [ 'myMet/F' ]

# Define a reader
reader = s2.treeReader( scalars = scalars_read,     vectors = vectors_read,  selectionString = None)

# Define a filler

#This filler just copies. Usually, some modifications would be made
def filler(struct):
    struct.nMyJet = reader.data.nJet
    for i in range(reader.data.nJet):
        struct.MyJet_pt[i] = reader.data.Jet_pt[i]
    struct.myMet = reader.data.met_pt
    return

maker  =    TreeMaker( filler = filler, scalars = scalars_write,  vectors = vectors_write )
reader.start()
maker.start()
while reader.run():
    maker.run()
