# Standard imports
import sys
import logging
import ROOT

#RootTools
from RootTools.Sample.Sample import Sample
from RootTools.Looper.TreeReader import TreeReader
from RootTools.Looper.TreeMaker import TreeMaker
from RootTools.Variable.Variable import Variable, ScalarType, VectorType

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

# from files
s2 = Sample.fromFiles("TTZToQQ", files = ["/afs/hephy.at/data/rschoefbeck01/RootTools/examples/TTZToQQ/TTZToQQ_0.root"], treeName = "Events")
s2.chain

variables =     [ Variable.fromString( 'Jet[pt/F]' ) ] \
              + [ Variable.fromString(x) for x in [ 'met_pt/F', 'nJet/I' ] ]

new_variables =     [ Variable.fromString('MyJet[pt/F]' ) ] \
                  + [ Variable.fromString(x) for x in [ 'myMet/F' ] ]

# Define a reader
reader = s2.treeReader( variables = variables,  selectionString = "met_pt>600")

# Define a filler

#This filler just copies. Usually, some modifications would be made
def filler(struct):
    struct.nMyJet = reader.data.nJet
    for i in range(reader.data.nJet):
        struct.MyJet_pt[i] = reader.data.Jet_pt[i]
    struct.myMet = reader.data.met_pt
    return

maker  =    TreeMaker( filler = filler, variables = new_variables )
reader.start()
maker.start()
while reader.run():
    maker.run()
