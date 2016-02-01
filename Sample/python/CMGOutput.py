'''Handling cmg output chunks.'''

# Standard imports
import ROOT
import os, subprocess

# Logging
import logging
logger = logging.getLogger(__name__)

# Base class
from  RootTools.Sample.SampleBase import SampleBase, EmptySampleError

# Helpers
import RootTools.tools.helpers as helpers

def readNormalization(filename):
    with open(filename, 'r') as fin:
        for line in fin:
            if any( [x in line for x in ['All Events', 'Sum Weights'] ] ):
                sumW = float(line.split()[2])
                return sumW

class CMGOutput( SampleBase ):


    def __init__(self, name, baseDirectory, treeFilename = 'tree.root', chunkString = None, treeName = 'tree', maxN = None):

        super(CMGOutput, self).__init__(name=name, treeName = treeName)

        self.baseDirectory = baseDirectory
        self.chunkString = chunkString
        self.maxN = maxN if not (maxN and maxN<0) else None 

        # Reading all subdirectories in base directory. If chunkString != None, require cmg output name formatting
        chunkDirectories = []
        for x in os.walk(baseDirectory):
            if not chunkString or (x[0].startswith(chunkString) and x[0].endswith('_Chunk')) or x[0]==chunkString:
                chunkDirectories.append(x[0])

        logger.debug( "Found %i chunk directories with chunkString %s in base directory %s", \
                           len(chunkDirectories), chunkString, baseDirectory )

        self.sumWeights = 0
        self.failedChunks=[]
        self.goodChunks  =[]

        for i, chunkDirectory in enumerate( chunkDirectories ):
            success = False
            logger.debug("Reading chunk %s", chunkDirectory)

            for root, subFolders, filenames in os.walk( chunkDirectory ):
                sumW = None
                treeFile = None

                # Determine normalization constant
                if 'SkimReport.txt' in filenames:
                    skimReportFilename = os.path.join(root, 'SkimReport.txt')
                    sumW = readNormalization( skimReportFilename )
                    if not sumW:
                        logger.warning( "Read chunk %s and found report '%s' but could not read normalization.", 
                                             chunkDirectory, skimReportFilename )
 
                # Load tree file 
                if treeFilename in filenames:
                    treeFile = os.path.join(root, treeFilename)
                    # Checking whether root file is OG and contains a tree
                    if not helpers.checkRootFile(treeFile, checkForObjects=[treeName] ):
                        logger.warning( "Read chunk %s and found tree file '%s' but file looks broken.",  chunkDirectory, treeFile )
                
                # If both, normalization and treefile are OK call it successful. 
                if sumW and treeFile:
                    self.files.append( treeFile )
                    self.sumWeights += sumW
                    logger.debug( "Successfully read chunk %s and incremented sumWeights by %7.2f",  chunkDirectory, sumW )
                    success = True
                    self.goodChunks.append( chunkDirectory )
                    break

            if not success:
                self.failedChunks.append( chunkDirectory  )

        # Don't allow empty samples
        if len(self.goodChunks) == 0: 
            raise EmptySampleError("Could not find good CMGOutput chunks for sample {0}. Total number of chunks: {1}. baseDirectory: {2}"\
                  .format(self.name, len(chunkDirectories), baseDirectory))

        # Log statements
        eff = 100*len(self.failedChunks)/float( len(chunkDirectories) )
        logger.info("Loaded CMGOutput sample %s. Total number of chunks : %i. Normalization: %7.2f Bad: %i. Inefficiency: %3.3f", \
                          self.name, len(chunkDirectories), self.sumWeights, len(self.failedChunks), eff)

        for chunk in self.failedChunks:
            logger.debug( "Failed to load chunk %s", chunk)

