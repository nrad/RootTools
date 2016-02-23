''' A simple example that demonstrates how to create a FWLiteSample instance from data files.
'''
# Standard imports
import sys
import os

#import logging
import ROOT

# RootTools
from RootTools.fwlite.FWLiteSample import FWLiteSample
from RootTools.core.logger import get_logger

# argParser
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel', 
      action='store',
      nargs='?',
      choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],
      default='DEBUG',
      help="Log level for logging"
)

args = argParser.parse_args()
logger = get_logger(args.logLevel, None)

# 8X mAOD, assumes eos mount in home directory 
dirname = "~/eos/cms/store/relval/CMSSW_8_0_0_pre6/JetHT/MINIAOD/80X_dataRun2_v4_RelVal_jetHT2015HLHT-v1/10000/" 
filename = "~/eos/cms/store/relval/CMSSW_8_0_0_pre6/JetHT/MINIAOD/80X_dataRun2_v4_RelVal_jetHT2015HLHT-v1/10000/02EF6290-71D6-E511-AF4F-0025905B858A.root"

s0 = FWLiteSample.fromDirectory("jetHT", directory = os.path.expanduser(dirname) )
s1 = FWLiteSample.fromFiles("test", files = os.path.expanduser(filename) )
