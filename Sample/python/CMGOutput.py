'''Handling cmg output chunks.'''

from  Roottools.Sample.Sample import Sample
import os, subprocess

class CMGOutput( Sample ):
    def __init__(name, baseDirectory, chunkString, treeName = 'tree', maxN = -1):
        super(CMGOutput, self).__init__(name=name, treeName = treeName)
        self.baseDirectory = baseDirectory
        self.chunkString = chunkString
        self.maxN = maxN 
        
        chunks = [{'name':x} for x in os.listdir(baseDirectory) \
                        if x.startswith(chunkString) and x.endswith('_Chunk') or x==sample.chunkString]

        chunks=chunks[:maxN] if maxN>0 else chunks
    sumWeights=0
    failedChunks=[]
    goodChunks  =[]
    const = 'All Events' if sample.isData else 'Sum Weights'
    for i, s in enumerate(chunks):
            logfile = "/".join([sample.path, s['name'], sample.skimAnalyzerDir,'SkimReport.txt'])
#      print logfile
            if os.path.isfile(logfile):
                line = [x for x in subprocess.check_output(["cat", logfile]).split('\n') if x.count(const)]
                assert len(line)==1,"Didn't find normalization constant '%s' in  number in file %s"%(const, logfile)
                n = int(float(line[0].split()[2]))
                sumW = float(line[0].split()[2])
                inputFilename = '/'.join([sample.path, s['name'], sample.rootFileLocation])
#        print sumW, inputFilename
                if os.path.isfile(inputFilename) and checkRootFile(inputFilename):
                    sumWeights+=sumW
                    s['file']=inputFilename
                    goodChunks.append(s)
                else:
                    failedChunks.append(chunks[i])
            else:
                print "log file not found:  ", logfile
                failedChunks.append(chunks[i])
#    except: print "Chunk",s,"could not be added"
    eff = round(100*len(failedChunks)/float(len(chunks)),3)
    print "Chunks: %i total, %i good (normalization constant %f), %i bad. Inefficiency: %f"%(len(chunks),len(goodChunks),sumWeights,len(failedChunks), eff)
    for s in failedChunks:
        print "Failed:",s
    return goodChunks, sumWeights
         
