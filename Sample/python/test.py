import sys
import logging
import ROOT
import CMGOutput
import SampleFromFiles

# create logger
logger = logging.getLogger("Logger")
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
fh = logging.FileHandler('out.txt')
fh.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)
fh.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)
logger.addHandler(fh)

td = "/data/rschoefbeck/cmgTuples/MC25ns_v2_1l_151218/TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISpring15MiniAODv2-74X_mcRun2_asymptotic_v2_ext1-v1/"

s2 = CMGOutput.CMGOutput("TTJets", baseDirectory = td, treeName = "tree")
s2.chain

s3 = SampleFromFiles.SampleFromFiles("test2", files = ["/afs/hephy.at/data/rschoefbeck01/cmgTuples/postProcessed_mAODv2/dilep/TTZToQQ/TTZToQQ_0.root"])
s3.chain
