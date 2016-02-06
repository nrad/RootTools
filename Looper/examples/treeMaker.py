# Standard imports
import sys
import logging
import ROOT

#RootTools
from RootTools.Sample.Sample import Sample
from RootTools.Looper.TreeReader import TreeReader
from RootTools.Looper.TreeMaker import TreeMaker

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

vectors_read   =    [ {'name':'Jet', 'nMax':100,'variables': ['pt/F'] } ]
scalars_read   =    [ 'met_pt/F' ]
vectors_write  =    [ {'name':'MyJet', 'nMax':100,'variables': ['pt/F'] } ]
scalars_write  =    [ 'myMet/F' ]

# Define a reader
reader = s2.treeReader( scalars = scalars_read,     vectors = vectors_read,  selectionString = None)

# Define a filler

#This filler just copies. Usually, some modifications would be made
def filler(struct):
    struct.nMyJet = reader.data.nJet
    for i in range(reader.data.nJet):
        struct.MyJet_pt[i] = reader.data.Jet_pt[i]
    struct.myMet = reader.data.met_pt
    return

maker  =    TreeMaker( filler = filler, scalars = scalars_write,  vectors = vectors_write )
reader.start()
maker.start()
while reader.run():
    maker.run()
