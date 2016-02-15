''' Create and fill histograms
'''

# Logging
import logging
logger = logging.getLogger(__name__)

# Standard imports
import ROOT

# RootTools
import RootTools.core.Variable as Variable
import RootTools.core.helpers as helpers

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

            sample_scale = sample.scale(sample) if  hasattr(sample, "scale") else 1

            r.start()
            while r.run():
                for plot in plots_for_sample:
                    for index in plot.sample_indices:
                                                
                        weight = 1 if plot.weight is None else plot.weight(r.data)
                        val = plot.variable.filler(r.data) if plot.variable.filler else getattr(r.data, plot.variable.name)
                        plot.histos[index[0]][index[1]].Fill(val, weight*sample_scale)

            # Clean up
            for plot in plots_for_sample:
                del plot.sample_indices
            r.cleanUpTempFiles()

def draw(plot,logY = True, yRange = "default", extensions = ["pdf", "png", "root"]):

    # FIXME -> Introduces CMSSW dependence
    ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/RootTools/plot/scripts/tdrstyle.C")
    ROOT.setTDRStyle()

    # Make canvas 
    y_width = 500
    y_ratio = 200
    scaleFacRatioPad = y_width/float(y_ratio) 
    if hasattr(plot, "ratio") and plot.ratio:
        y_width += y_ratio
    c1 = ROOT.TCanvas("ROOT.c1","drawHistos",200,10,500, y_width)

    # Clone and add up histos in stack
    histos = map(lambda l:map(lambda h:h.Clone(), l), plot.histos)
    for l in histos:
        n = len(l)
        for i in range(n):
            for j in range(i+1,n):
                l[i].Add(l[j])

    # Range on y axis
    max_ = max( l[0].GetMaximum() for l in histos )
    min_ = min( l[0].GetMinimum() for l in histos )
    if yRange == "default":
        if logY:
            yMax_ = 10**0.5*max_
#            yMin_ = 10**-0.5*min_ if min_>0 else 10**-1
            yMin_ = 0.7 
        else:
            yMax_ = 1.2*max_
            yMin_ = 0 if min_>0 else 1.2*min_
        
    same = ""
    for i, l in enumerate(histos):
        for j, h in enumerate(l):
            drawOpt = h.drawOpt if hasattr(h, "drawOpt") else "hist"
            c1.SetLogy(logY)
            h.GetYaxis().SetRangeUser(yMin_, yMax_)
            h.GetXaxis().SetTitle(plot.texX)
            h.GetYaxis().SetTitle(plot.texY)

            h.GetXaxis().SetTitleSize(0.04)
            h.GetYaxis().SetTitleSize(0.04)
            h.GetYaxis().SetTitleOffset(1.3)
            h.GetXaxis().SetTitleOffset(1.1)
            
            h.Draw(drawOpt+same)
            same = "same"
    c1.RedrawAxis()
    for extension in extensions:
        c1.Print("/afs/hephy.at/user/r/rschoefbeck/www/etc/%s.%s"%(plot.variable.name, extension))
    del c1
