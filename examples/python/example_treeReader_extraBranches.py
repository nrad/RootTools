''' A TreeReader runs over a sample and evaluates extra variables.
Useful for using in a plot makro with complex derived observables.
'''
# Standard imports
import sys
from math import sqrt
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
s0 = Sample.fromFiles("s0", files = ["example_data/file_0.root"], treeName = "Events")

variables =  [ Variable.fromString('Jet[pt/F,eta/F,phi/F]' ) ] \
           + [ Variable.fromString(x) for x in [ 'met_pt/F', 'met_phi/F' ] ]

metPt2 = Variable.fromString('met_pt2/F') 
metPt2.filler = lambda data: data.met_pt**2
filled_variables = [ metPt2 ]

h=ROOT.TH1F('met','met',100,0,0)
r = s0.treeReader( variables = variables, filled_variables = filled_variables, selectionString = "met_pt>100")
r.start()
while r.run():
    h.Fill( sqrt(r.data.met_pt2) )
