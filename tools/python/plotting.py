''' Create and fill histograms
'''

# Logging
import logging
logger = logging.getLogger(__name__)

# RootTools
import RootTools.tools.Variable as Variable
import RootTools.tools.helpers as helpers

def fill(plots, usedVariables = []):
    '''Create and fill all plots
    '''

    selectionStrings = list(set(p.selectionString for p in plots))

    for selectionString in selectionStrings:
        logger.info( "Now working on selection string %s"% selectionString )
        allSamples = list(set(sum([p.stack.samples() for p in plots if p.selectionString == selectionString], [])))
        plots_for_sample={}
        for s in allSamples:
            plots_for_sample[s.hash()] = [p for p in plots if s in p.stack.samples() and p.selectionString == selectionString]

        for sample in allSamples:
            read_variables      = list(set([p.variable for p in plots_for_sample[sample.hash()] if p.variable.filler is None]))

            # Anything added with the 'uses' decorator?
            read_variables += helpers.fromString(usedVariables)

            filled_variables    = list(set([p.variable for p in plots_for_sample[sample.hash()] if p.variable.filler is not None]))
            r = sample.treeReader( variables = read_variables, filled_variables = filled_variables, selectionString = selectionString)
            r.start()
            while r.run():
                for plot in plots_for_sample[s.hash()]:
                    plot.

