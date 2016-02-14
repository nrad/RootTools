''' Create and fill histograms
'''

# Logging
import logging
logger = logging.getLogger(__name__)

# Standard imports
import ROOT

# RootTools
import RootTools.tools.Variable as Variable
import RootTools.tools.helpers as helpers

def fill(plots, read_variables = []):
    '''Create and fill all plots
    '''

    # Unique list of selection strings
    selectionStrings    = list(set(p.selectionString for p in plots))
    # Convert extra arguments from text to Variable instance
    read_variables      = list(helpers.fromString(read_variables))

    for selectionString in selectionStrings:
        logger.info( "Now working on selection string %s"% selectionString )

        # find all plots with current selection
        plots_for_selection = [p for p in plots if p.selectionString == selectionString]

        # Find all samples we have to loop over
        samples = list(set(sum([p.stack.samples() for p in plots_for_selection], [])))
        logger.info( "Found %i different samples for this selection string"%len(samples) )

        # Give histos to plot
        for p in plots_for_selection:
            p.histos = p.stack.make_histos(p)

        for sample in samples:

            # find all plots whose stack contains the current sample
            plots_for_sample = [p for p in plots_for_selection if sample in p.stack.samples()]
            
            # find the positions (indices)  of the stack in each plot
            for plot in plots_for_sample:
                plot.sample_indices = plot.stack.getSampleIndicesInStack(sample)

            # Make reader
            chain_variables  = list(set([p.variable for p in plots_for_sample if p.variable.filler is None]))
            filled_variables = list(set([p.variable for p in plots_for_sample if p.variable.filler is not None]))

            # Create reader and run it over sample, fill the plots
            r = sample.treeReader( variables = read_variables + chain_variables, filled_variables = filled_variables, selectionString = selectionString)

            r.start()
            while r.run():
                for plot in plots_for_sample:
                    for index in plot.sample_indices:
                                                
                        weight = 1 if plot.weight is None else plot.weight(r.data)
                        val = plot.variable.filler(r.data) if plot.variable.filler else getattr(r.data, plot.variable.name)
                        plot.histos[index[0]][index[1]].Fill(val, weight)

            # Clean up
            for plot in plots_for_sample:
                del plot.sample_indices
            r.cleanUpTempFiles()
