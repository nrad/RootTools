''' TreeReader example: Loop over a sample and write some data to a histogram.
'''
import sys
import logging
import ROOT
from Sample import Sample
from Variable import Variable, ScalarType, VectorType
from TreeReader import TreeReader

# create logger
logger = logging.getLogger(__name__)
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

# Samplefrom files
s0 = Sample.fromFiles("s0", files = ["example_data/file_0.root"], treeName = "Events")

variables =  [ Variable.fromString('Jet[pt/F,eta/F,phi/F]' ) ] \
           + [ Variable.fromString(x) for x in [ 'met_pt/F', 'met_phi/F' ] ]

#s1.reader( scalars = scalars, vectors = vectors, selectionString = "met_pt>100")

h=ROOT.TH1F('met','met',100,0,0)
r = s0.treeReader( variables = variables, selectionString = "met_pt>100")
r.start()
while r.run():
    h.Fill( r.data.met_pt )
