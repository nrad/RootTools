''' A simple example that demonstrates how to create Sample instances from data files.
'''
import sys
import logging
import ROOT
from Sample import Sample

# create logger
logger = logging.getLogger("RootTools")
logger.setLevel(logging.INFO)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


s0 = Sample.fromFiles("s0", files = ["example_data/file_0.root"], treeName = "Events")
s0.chain

## from files
#s1 = Sample.fromFiles("TTZToQQ", files = ["/afs/hephy.at/data/rschoefbeck01/RootTools/examples/TTZToQQ/TTZToQQ_0.root"], treeName = "Events")
#s1.chain

## from CMG output
#td = "/afs/hephy.at/data/rschoefbeck01/RootTools/examples/WJetsToLNu_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISpring15MiniAODv2-74X_mcRun2_asymptotic_v2-v1"
#s2 = Sample.fromCMGOutput("WJets_HT600", baseDirectory = td, treeName = "tree")
#s2.chain

## from a directory with root files
#s3=Sample.fromDirectory(name="TTJets", directory="/afs/hephy.at/data/rschoefbeck01/RootTools/examples/ttJetsCSA1450ns", treeName = "Events")
#s3.chain

