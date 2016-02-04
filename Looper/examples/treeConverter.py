'''Example of a converter that splits the input sample into chunks of given size
Has all (I hope) the post processor functionality.
'''

# Standard imports
import ROOT
import sys
import logging
import os

#RootTools
from RootTools.Sample.Sample import Sample
from RootTools.Looper.TreeReader import TreeReader
from RootTools.Looper.TreeMaker import TreeMaker

# create logger
logger = logging.getLogger("RootTools")
logger.setLevel(logging.INFO)
logging.getLogger("RootTools.Looper").setLevel(logging.CRITICAL)

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
#s1 = Sample.fromCMGOutput("TTJetsDilep", baseDirectory = td, treeFilename = 'tree.root', treeName = 'tree')
s2 = Sample.fromFiles("TTZ", files = ["/afs/hephy.at/data/rschoefbeck01/cmgTuples/postProcessed_mAODv2/dilep/TTZToQQ/TTZToQQ_0.root"], treeName = "Events")

outputfile = "./converted.root"

vectors_read   =    [ {'name':'Jet', 'nMax':100,'variables': ['pt/F'] } ]
scalars_read   =    [ 'met_pt/F' ]
vectors_write  =    [ {'name':'MyJet', 'nMax':100,'variables': ['pt/F'] } ]
scalars_write  =    [ 'myMet/F' ]

branches_to_keep = ["evt", "run", "lumi"]

# Define a reader
reader = s2.treeReader( scalars = scalars_read, vectors = vectors_read, selectionString = "(met_pt>200)")

# Define a filler

#This filler just copies. Usually, some modifications would be made
def filler(struct):
    struct.nMyJet = reader.data.nJet
    for i in range(reader.data.nJet):
        struct.MyJet_pt[i] = reader.data.Jet_pt[i]
    struct.myMet = reader.data.met_pt
    return

# Create a empty maker. Maker class will be compiled.
treeMaker_parent = TreeMaker( filler = filler, scalars = scalars_write,  vectors = vectors_write )

# Split input in ranges
eventRanges = reader.getEventRanges( maxFileSizeMB = 20)
logger.info( "Splitting into %i ranges of %i events on average.",  len(eventRanges), (eventRanges[-1][1] - eventRanges[0][0])/len(eventRanges) )

convertedEvents = 0
clonedEvents = 0
for ievtRange, eventRange in enumerate(eventRanges):
    logger.info( "Now at range %i which has %i events.",  ievtRange, eventRange[1]-eventRange[0] )
    

    # Set the reader to the event range
    reader.setEventRange( eventRange )
    clonedTree = reader.cloneTree( branches_to_keep )
    clonedEvents += clonedTree.GetEntries()

    # Clone the empty maker in order to avoid recompilation at every loop iteration
    maker = treeMaker_parent.cloneWithoutCompile(externalTree = clonedTree)
    maker.start()

    # Do the thing
    reader.start()
    while reader.run():
        maker.run()

    convertedEvents += maker.tree.GetEntries()

    # Writing to file
    filename, ext = os.path.splitext( outputfile )
    f = ROOT.TFile.Open(filename+'_'+str(ievtRange)+ext, 'recreate')
    maker.tree.Write()
    f.Close()

    # Destroy the TTree
    maker.clear()

logger.info( "Converted %i events of %i, cloned %i",  convertedEvents, reader.nEvents , clonedEvents)
