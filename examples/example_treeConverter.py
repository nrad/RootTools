'''Combining a TreeReader and a TreeMaker, a simple converter is built 
that splits an input sample into chunks of given size and stores the result in new ROOT files.
'''

# Standard imports
import ROOT
import sys
import logging
import os

#RootTools
from RootTools.tools.Sample import Sample
from RootTools.tools.Immutable import Immutable
from RootTools.tools.TreeReader import TreeReader
from RootTools.tools.TreeMaker import TreeMaker
from RootTools.tools.Variable import Variable, ScalarType, VectorType
from RootTools.tools.logger import get_logger

# argParser
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel', 
      action='store',
      nargs='?',
      choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],
      default='INFO',
      help="Log level for logging"
)

args = argParser.parse_args()
logger = get_logger(args.logLevel, None)

# from files
s0 = Immutable(Sample.fromFiles("s0", files = ["example_data/file_0.root"], treeName = "Events"))

read_variables =  [ Variable.fromString( "nJet/I"), Variable.fromString('Jet[pt/F,eta/F,phi/F]' ) ] \
                + [ Variable.fromString(x) for x in [ 'met_pt/F', 'met_phi/F' ] ]

new_variables =     [ Variable.fromString('MyJet[pt2/F]' ) ] \
                  + [ Variable.fromString(x) for x in [ 'myMetOver2/F' ] ]

outputfile = "./converted.root"


branches_to_keep = [ "met_phi" ]

# Define a reader
reader = s0.treeReader( variables = read_variables, selectionString = "(met_pt>100)")

# A simple eample
def filler(struct):
    struct.nMyJet = reader.data.nJet
    for i in range(reader.data.nJet):
        struct.MyJet_pt2[i] = reader.data.Jet_pt[i]**2
    struct.myMetOver2 = reader.data.met_pt/2.
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
