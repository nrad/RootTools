'''Make a stacked plot
'''

#Standard imports
import ROOT

# Logging
import logging
logger = logging.getLogger(__name__)

# RootTools
from RootTools.Sample.Sample import Sample
from RootTools.Plot.Stack import Stack
from RootTools.Plot.Plot import Plot

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
s0 = Sample.fromFiles("TTZToQQ", files = ["/afs/hephy.at/data/rschoefbeck01/RootTools/examples/ttJetsCSA1450ns/ttJetsCSA1450ns_0.root"], treeName = "Events")
s0.chain
s1 = Sample.fromFiles("TTZToQQ", files = ["/afs/hephy.at/data/rschoefbeck01/RootTools/examples/ttJetsCSA1450ns/ttJetsCSA1450ns_1.root"], treeName = "Events")
s1.chain
s2 = Sample.fromFiles("TTZToQQ", files = ["/afs/hephy.at/data/rschoefbeck01/RootTools/examples/ttJetsCSA1450ns/ttJetsCSA1450ns_2.root"], treeName = "Events")
s2.chain

stack = Stack([ [s0, s1], [s2] ])

plot1 = Plot('met_pt', [100,0,1000] ,"(1)", weightVar = "weight")
plot2 = Plot('met_phi', [100,0,1000] ,"(1)", weightVar = "weight")
