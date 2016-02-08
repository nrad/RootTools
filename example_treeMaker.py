''' Simple example of a TreeMaker. Creates a new TTree by looping a TreeReader over a sample and filling.
'''

# Standard imports
import sys
import logging
import ROOT

#RootTools
from Sample import Sample
from TreeReader import TreeReader
from TreeMaker import TreeMaker
from Variable import Variable, ScalarType, VectorType

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
s0 = Sample.fromFiles("s0", files = ["example_data/file_0.root"], treeName = "Events")

read_variables =  [ Variable.fromString( "nJet/I"), Variable.fromString('Jet[pt/F,eta/F,phi/F]' ) ] \
                + [ Variable.fromString(x) for x in [ 'met_pt/F', 'met_phi/F' ] ]

new_variables =     [ Variable.fromString('MyJet[pt2/F]' ) ] \
                  + [ Variable.fromString(x) for x in [ 'myMetOver2/F' ] ]

# Define a reader
reader = s0.treeReader( variables = read_variables,  selectionString = "met_pt>600")

# Define a filler

#A simple eample
def filler(struct):
    struct.nMyJet = reader.data.nJet
    for i in range(reader.data.nJet):
        struct.MyJet_pt2[i] = reader.data.Jet_pt[i]**2
    struct.myMetOver2 = reader.data.met_pt/2.
    return

maker  =    TreeMaker( filler = filler, variables = new_variables )
reader.start()
maker.start()
while reader.run():
    maker.run()
