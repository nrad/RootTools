''' FWLiteReader example: Loop over a sample and write some data to a histogram.
'''
# Standard imports
import os
import logging
import ROOT

#RootTools
from RootTools.core.Variable import Variable, ScalarType, VectorType
from RootTools.core.logger import get_logger
from RootTools.fwlite.FWLiteSample import FWLiteSample
from RootTools.fwlite.FWLiteReader import FWLiteReader
from RootTools.plot.Plot import Plot
import RootTools.plot.plotting as plotting

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


# 8X mAOD, assumes eos mount in home directory 
filename = "~/eos/cms/store/relval/CMSSW_8_0_0_pre6/JetHT/MINIAOD/80X_dataRun2_v4_RelVal_jetHT2015HLHT-v1/10000/02EF6290-71D6-E511-AF4F-0025905B858A.root"
dirname = "~/eos/cms/store/relval/CMSSW_8_0_0_pre6/JetHT/MINIAOD/80X_dataRun2_v4_RelVal_jetHT2015HLHT-v1/10000/"

s0 = FWLiteSample.fromFiles("test", files = os.path.expanduser(filename) )
#s1 = FWLiteSample.fromDirectory("jetHT", directory = os.path.expanduser(dirname) )

products = {
    'slimmedJets':{'type':'vector<pat::Jet>', 'label':("slimmedJets", "", "reRECO")} 
    }

r = s1.fwliteReader( products = products )

h=ROOT.TH1F('met','met',100,0,0)
r.start()

runs = set()
while r.run():
    runs.add(r.evt[0])
#    print r.evt, [j.pt() for j in r.products['slimmedJets']]

logger.info( "Found the following run(s): %s", ",".join(str(run) for run in runs) )

