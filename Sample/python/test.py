import sys
import logging
import ROOT
import Sample

# create logger
logger = logging.getLogger("Logger")
logger.setLevel(logging.DEBUG)

logging.getLogger("Sample").setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
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

s = Sample.Sample("data", treeName = "tree")
s.files=['/data/rschoefbeck/cmgTuples/Run2015B/50ns_0l/JetHT_Run2015B-17Jul2015-v1/tree.root']
s.chain
