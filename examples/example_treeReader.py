''' TreeReader example: Loop over a sample and write some data to a histogram.
'''
import sys
import logging
import ROOT
from RootTools.tools.Sample import Sample
from RootTools.tools.Variable import Variable, ScalarType, VectorType
from RootTools.tools.TreeReader import TreeReader
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
logger = get_logger(args.logLevel, logFile = None)

# Samplefrom files
s0 = Sample.fromFiles("s0", files = ["example_data/file_0.root"], treeName = "Events", selectionString = 'Jet_pt[0]>100')
s0.chain
variables =  [ Variable.fromString('Jet[pt/F,eta/F,phi/F]' ) ] \
           + [ Variable.fromString(x) for x in [ 'met_pt/F', 'met_phi/F' ] ]

#s1.reader( scalars = scalars, vectors = vectors, selectionString = "met_pt>100")

h=ROOT.TH1F('met','met',100,0,0)
r = s0.treeReader( variables = variables, selectionString = "met_pt>100")
r.start()
while r.run():
    h.Fill( r.data.met_pt )
