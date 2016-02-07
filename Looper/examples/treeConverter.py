'''Example of a converter that splits the input sample into chunks of given size
Has all (I hope) post processor functionality.
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
from RootTools.Variable.Variable import Variable, ScalarType, VectorType

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

# from files
s2 = Sample.fromFiles("TTZToQQ", files = ["/afs/hephy.at/data/rschoefbeck01/RootTools/examples/TTZToQQ/TTZToQQ_0.root"], treeName = "Events")
s2.chain

outputfile = "./converted.root"

vectors_read   =    [ {'name':'Jet', 'nMax':100,'variables': ['pt/F', 'eta/F', 'phi/F'] } ]
scalars_read   =    [ 'met_pt/F', 'met_phi/F' ]
vectors_write  =    [ {'name':'MyJet', 'nMax':100,'variables': ['pt/F'] } ]
scalars_write  =    [ 'myMet/F' ]

variables =     [ Variable.fromString( 'Jet[pt/F,eta/F,phi/F]' ) ] \
              + [ Variable.fromString(x) for x in [ 'met_pt/F', 'met_phi/F', 'nJet/I' ] ]

new_variables =     [ Variable.fromString('MyJet[pt/F]') ] \
                  + [ Variable.fromString(x) for x in [ 'myMet/F' ] ]

branches_to_keep = ["evt", "run", "lumi", "met_pt", "met_phi", "Jet_pt", "Jet_eta", "Jet_phi", 'nJet']

# Define a reader
reader = s2.treeReader( variables = variables, selectionString = "(met_pt>100)")

# Define a filler

#This filler just copies. Usually, some modifications would be made
def filler( target):
    target.myMet = reader.data.met_pt
    target.nMyJet = reader.data.nJet
    for i in range(reader.data.nJet):
        target.MyJet_pt[i] = reader.data.Jet_pt[i]
    return

# Create a maker. Maker class will be compiled. This instance will be used as a parent in the loop
treeMaker_parent = TreeMaker( filler = filler, variables = new_variables )

# Split input in ranges
eventRanges = reader.getEventRanges( maxFileSizeMB = 30)
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
    maker = treeMaker_parent.cloneWithoutCompile( externalTree = clonedTree )
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
