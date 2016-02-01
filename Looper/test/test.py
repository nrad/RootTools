import sys
import logging
import ROOT
from RootTools.Sample.CMGOutput import CMGOutput
from RootTools.Sample.SampleFromFiles import SampleFromFiles
from RootTools.Looper.Reader import Reader

# create logger
logger = logging.getLogger("RootTools")
logger.setLevel(logging.DEBUG)

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

s1 = SampleFromFiles("TTZ", files = ["/afs/hephy.at/data/rschoefbeck01/cmgTuples/postProcessed_mAODv2/dilep/TTZToQQ/TTZToQQ_0.root"])

vectors   =    [ {'name':'Jet', 'nMax':100, 'variables': ['pt/F', 'eta/F', 'phi/F', 'id/I','btagCSV/F'] } ]
scalars   =    [ 'met_pt/F', 'met_phi/F', 'run/I', 'lumi/I', 'evt/l', 'nVert/I' ]

r = s1.reader( scalars = scalars, vectors = vectors, selectionString = "met_pt>100")

h=ROOT.TH1F('met','met',100,0,0)
while r.run():
   h.Fill( r.entry.met_pt )
