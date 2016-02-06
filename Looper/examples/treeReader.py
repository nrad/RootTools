import sys
import logging
import ROOT
from RootTools.Sample.Sample import Sample
from RootTools.Looper.TreeReader import TreeReader

# create logger
logger = logging.getLogger("RootTools")
logger.setLevel(logging.INFO)

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

vectors   =    [ {'name':'Jet', 'nMax':100, 'variables': ['pt/F', 'eta/F', 'phi/F', 'id/I','btagCSV/F'] } ]
scalars   =    [ 'met_pt/F', 'met_phi/F', 'run/I', 'lumi/I', 'evt/l', 'nVert/I' ]

#s1.reader( scalars = scalars, vectors = vectors, selectionString = "met_pt>100")

h=ROOT.TH1F('met','met',100,0,0)
r = s2.treeReader( scalars = scalars, vectors = vectors, selectionString = "met_pt>100")
r.start()
while r.run():
    h.Fill( r.data.met_pt )
