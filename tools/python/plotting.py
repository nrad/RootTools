''' Create and fill histograms
'''

# Logging
import logging
logger = logging.getLogger(__name__)

def fill(*plots):
    '''Create and fill all plots
    '''

    # Get hashes from all used samples and the set of selectionStrings of the plots
    stack_hashes = {}
    selectionStrings = [] 
    for p in plots:
        selectionStrings.append(p.selectionString)
        for s in p.stack.samples():
            stack_hashes[s.hash()] = s

    for selectionString in list( set( selectionStrings ) ):
        for hash_, sample in stack_hashes.iteritems():
            variables = 
            r = sample.treeReader( variables = variables, selectionString = selectionString)
            r.start()
            while r.run():
                pass
#                h.Fill( r.data.met_pt )
