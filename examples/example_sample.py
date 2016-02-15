''' A simple example that demonstrates how to create Sample instances from data files.
'''
# Standard imports
import sys
import os

#import logging
import ROOT

# RootTools
from RootTools.core.Sample import Sample
from RootTools.core.logger import get_logger

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

filename =  "example_data/file_0.root"

# simplest way
s0 = Sample.fromFiles("", filename )
s0.chain

# works as well with lists:
s0_2 = Sample.fromFiles("", [filename, filename], selectionString = ["met_pt>200", "Jet_pt[0]>100"])
s0_2.chain

afsRootToolsExamples = "/afs/hephy.at/data/rschoefbeck01/RootTools/examples"
if os.path.exists(afsRootToolsExamples):

    # from files
    s1 = Sample.fromFiles("TTZToQQ", files = [os.path.join( afsRootToolsExamples, "TTZToQQ/TTZToQQ_0.root" )], treeName = "Events")
    s1.chain

    # from CMG output
    td = os.path.join( afsRootToolsExamples, \
            "WJetsToLNu_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISpring15MiniAODv2-74X_mcRun2_asymptotic_v2-v1" )
    s2 = Sample.fromCMGOutput("WJets_HT600", baseDirectory = td, treeName = "tree")
    s2.chain

    # from a directory with root files
    s3=Sample.fromDirectory(name="TTJets", directory = os.path.join( afsRootToolsExamples, "ttJetsCSA1450ns" ), treeName = "Events")
    s3.chain
